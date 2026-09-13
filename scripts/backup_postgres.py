#!/usr/bin/env python3
"""Backup PostgreSQL criptografado e restauracao em ambiente isolado."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import hmac
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import BinaryIO

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


ROOT = Path(__file__).resolve().parents[1]
RESTORE_COMPOSE = ROOT / "compose.restore-test.yaml"
MAGIC = b"STROOP-PG-BACKUP\x01"
NONCE_BYTES = 12
TAG_BYTES = 16
CHUNK_BYTES = 64 * 1024
DEFAULT_GENERATIONS = 30
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")
PROJECT_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")


class BackupError(Exception):
    """Erro de backup sanitizado, sem comandos, paths ou dados internos."""


def generate_key(path: Path) -> None:
    path = path.expanduser()
    if path.exists():
        raise BackupError("Arquivo de chave ja existe; nenhuma alteracao realizada.")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as destination:
            destination.write(base64.urlsafe_b64encode(os.urandom(32)) + b"\n")
    except OSError as exc:
        raise BackupError("Nao foi possivel criar a chave de backup.") from exc


def load_key(path: Path) -> bytes:
    try:
        stat = path.stat()
        if stat.st_mode & 0o077:
            raise BackupError("A chave deve permitir acesso somente ao proprietario.")
        encoded = path.read_bytes().strip()
        key = base64.b64decode(encoded, altchars=b"-_", validate=True)
    except BackupError:
        raise
    except (OSError, ValueError) as exc:
        raise BackupError("Chave de backup ausente ou invalida.") from exc
    if len(key) != 32:
        raise BackupError("Chave de backup ausente ou invalida.")
    return key


def ensure_separate(key_path: Path, output_directory: Path) -> None:
    key = key_path.expanduser().resolve()
    output = output_directory.expanduser().resolve()
    if key == output or output in key.parents:
        raise BackupError("A chave deve permanecer fora do diretorio de backups.")


def encrypt_stream(source: BinaryIO, destination: BinaryIO, key: bytes) -> None:
    nonce = os.urandom(NONCE_BYTES)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    destination.write(MAGIC)
    destination.write(nonce)
    while chunk := source.read(CHUNK_BYTES):
        destination.write(encryptor.update(chunk))
    destination.write(encryptor.finalize())
    destination.write(encryptor.tag)


def decrypt_stream(source: BinaryIO, destination: BinaryIO, key: bytes) -> None:
    try:
        source.seek(0, os.SEEK_END)
        total_size = source.tell()
        minimum = len(MAGIC) + NONCE_BYTES + TAG_BYTES
        if total_size < minimum:
            raise BackupError("Backup criptografado invalido.")
        source.seek(0)
        if source.read(len(MAGIC)) != MAGIC:
            raise BackupError("Backup criptografado invalido.")
        nonce = source.read(NONCE_BYTES)
        source.seek(total_size - TAG_BYTES)
        tag = source.read(TAG_BYTES)
        source.seek(len(MAGIC) + NONCE_BYTES)
        remaining = total_size - minimum
        decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
        while remaining:
            chunk = source.read(min(CHUNK_BYTES, remaining))
            if not chunk:
                raise BackupError("Backup criptografado truncado.")
            remaining -= len(chunk)
            destination.write(decryptor.update(chunk))
        destination.write(decryptor.finalize())
    except BackupError:
        raise
    except (OSError, ValueError, InvalidTag) as exc:
        raise BackupError("Falha de integridade ou chave incorreta.") from exc


def _positive_generations(value: str | int) -> int:
    try:
        generations = int(value)
    except (TypeError, ValueError):
        raise BackupError("Numero de geracoes invalido.") from None
    if not 1 <= generations <= 3650:
        raise BackupError("Numero de geracoes invalido.")
    return generations


def _identifier(value: str, label: str) -> str:
    if IDENTIFIER.fullmatch(value) is None:
        raise BackupError(f"{label} invalido.")
    return value


def _compose_base(
    compose_file: Path,
    project_name: str | None = None,
    env_file: Path | None = None,
) -> list[str]:
    if not compose_file.is_file():
        raise BackupError("Arquivo Compose nao encontrado.")
    command = ["docker", "compose"]
    if env_file is not None:
        if not env_file.is_file():
            raise BackupError("Arquivo de ambiente nao encontrado.")
        command.extend(["--env-file", str(env_file)])
    if project_name:
        if PROJECT_NAME.fullmatch(project_name) is None:
            raise BackupError("Projeto Compose invalido.")
        command.extend(["--project-name", project_name])
    command.extend(["-f", str(compose_file)])
    return command


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def rotate_backups(directory: Path, generations: int) -> None:
    backups = sorted(directory.glob("stroop-*.dump.enc"), reverse=True)
    for expired in backups[_positive_generations(generations) :]:
        expired.unlink(missing_ok=True)
        expired.with_suffix(expired.suffix + ".sha256").unlink(missing_ok=True)


def create_backup(
    *,
    compose_file: Path,
    key_file: Path,
    output_directory: Path,
    database: str,
    user: str,
    generations: int = DEFAULT_GENERATIONS,
    service: str = "postgres",
    project_name: str | None = None,
    env_file: Path | None = None,
    now: datetime | None = None,
) -> Path:
    ensure_separate(key_file, output_directory)
    key = load_key(key_file)
    database = _identifier(database, "Banco")
    user = _identifier(user, "Usuario")
    service = _identifier(service, "Servico")
    generations = _positive_generations(generations)
    try:
        output_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        output_directory.chmod(0o700)
    except OSError as exc:
        raise BackupError("Diretorio de backup indisponivel.") from exc
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    target = output_directory / f"stroop-{timestamp}.dump.enc"
    partial = target.with_suffix(target.suffix + ".partial")
    command = _compose_base(compose_file, project_name, env_file) + [
        "exec",
        "-T",
        service,
        "pg_dump",
        "--format=custom",
        "--compress=gzip:6",
        "--no-owner",
        "--no-privileges",
        "--username",
        user,
        "--dbname",
        database,
    ]
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if process.stdout is None:
            raise BackupError("Falha ao iniciar backup PostgreSQL.")
        with partial.open("xb") as destination:
            os.chmod(partial, 0o600)
            encrypt_stream(process.stdout, destination, key)
        if process.wait() != 0:
            raise BackupError("Backup PostgreSQL nao confirmado.")
        partial.replace(target)
        checksum = _digest_file(target)
        checksum_path = target.with_suffix(target.suffix + ".sha256")
        checksum_path.write_text(f"{checksum}  {target.name}\n", encoding="ascii")
        checksum_path.chmod(0o600)
        rotate_backups(output_directory, generations)
        return target
    except BackupError:
        raise
    except (OSError, subprocess.SubprocessError) as exc:
        raise BackupError("Backup PostgreSQL nao confirmado.") from exc
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        partial.unlink(missing_ok=True)


def verify_checksum(backup: Path) -> None:
    checksum_path = backup.with_suffix(backup.suffix + ".sha256")
    try:
        expected, filename = checksum_path.read_text(encoding="ascii").split()
    except (OSError, ValueError) as exc:
        raise BackupError("Checksum do backup ausente ou invalido.") from exc
    if filename != backup.name or not hmac.compare_digest(
        expected, _digest_file(backup)
    ):
        raise BackupError("Checksum do backup nao confere.")


def restore_isolated(backup: Path, key_file: Path) -> tuple[int, int]:
    """Restaura em PostgreSQL tmpfs sem portas e sempre remove o ambiente."""
    verify_checksum(backup)
    key = load_key(key_file)
    compose = _compose_base(RESTORE_COMPOSE, "stroop-restore-validation")
    try:
        subprocess.run(
            compose + ["up", "-d", "--wait", "restore-postgres"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process = subprocess.Popen(
            compose
            + [
                "exec",
                "-T",
                "restore-postgres",
                "pg_restore",
                "--exit-on-error",
                "--single-transaction",
                "--no-owner",
                "--no-privileges",
                "--username",
                "stroop_restore",
                "--dbname",
                "stroop_restore_test",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if process.stdin is None:
            raise BackupError("Falha ao iniciar restauracao isolada.")
        try:
            with backup.open("rb") as source:
                decrypt_stream(source, process.stdin, key)
            process.stdin.close()
        except Exception:
            process.kill()
            process.wait()
            raise
        if process.wait() != 0:
            raise BackupError("Restauracao isolada nao confirmada.")
        result = subprocess.run(
            compose
            + [
                "exec",
                "-T",
                "restore-postgres",
                "psql",
                "--username",
                "stroop_restore",
                "--dbname",
                "stroop_restore_test",
                "--tuples-only",
                "--no-align",
                "--command",
                "SELECT COUNT(*) FROM schema_migrations; SELECT COUNT(*) FROM assessments;",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        counts = [int(line) for line in result.stdout.splitlines() if line.strip()]
        if len(counts) != 2 or counts[0] < 1 or counts[1] < 0:
            raise BackupError("Restauracao isolada sem verificacao estrutural.")
        return counts[0], counts[1]
    except BackupError:
        raise
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise BackupError("Restauracao isolada nao confirmada.") from exc
    finally:
        subprocess.run(
            compose + ["down", "--volumes", "--remove-orphans"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cria backup criptografado ou valida restauracao isolada."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    key = subparsers.add_parser("generate-key")
    key.add_argument("--key-file", required=True, type=Path)

    backup = subparsers.add_parser("backup")
    backup.add_argument("--compose-file", type=Path, default=ROOT / "compose.production.yaml")
    backup.add_argument("--env-file", type=Path)
    backup.add_argument("--project-name")
    backup.add_argument("--service", default="postgres")
    backup.add_argument("--key-file", required=True, type=Path)
    backup.add_argument("--output-dir", required=True, type=Path)
    backup.add_argument("--database", required=True)
    backup.add_argument("--user", required=True)
    backup.add_argument(
        "--generations",
        default=os.environ.get("BACKUP_GENERATIONS", str(DEFAULT_GENERATIONS)),
    )

    restore = subparsers.add_parser("restore-test")
    restore.add_argument("--key-file", required=True, type=Path)
    restore.add_argument("--backup", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.command == "generate-key":
            generate_key(args.key_file)
            print("Chave de backup criada fora do repositorio de backups.")
        elif args.command == "backup":
            create_backup(
                compose_file=args.compose_file,
                project_name=args.project_name,
                env_file=args.env_file,
                service=args.service,
                key_file=args.key_file,
                output_directory=args.output_dir,
                database=args.database,
                user=args.user,
                generations=args.generations,
            )
            print("Backup PostgreSQL criptografado concluido.")
        else:
            migrations, assessments = restore_isolated(args.backup, args.key_file)
            print(
                "Restauracao isolada comprovada; "
                f"migrations={migrations}; avaliacoes={assessments}."
            )
        return 0
    except BackupError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
