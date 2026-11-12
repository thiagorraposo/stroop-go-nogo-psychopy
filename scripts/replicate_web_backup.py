#!/usr/bin/env python3
"""Replica somente backups criptografados por SSH restrito, sem ler a chave AES."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import threading

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.backup_postgres import CHUNK_BYTES, DEFAULT_GENERATIONS, MAGIC, NONCE_BYTES, TAG_BYTES


NAME = re.compile(r'stroop-([0-9]{8}T[0-9]{6}Z)\.dump\.enc')
MAX_BYTES = 512 * 1024 * 1024
MAX_AGE_SECONDS = 24 * 60 * 60
FIELDS = {'host', 'port', 'user', 'key_file', 'known_hosts_file', 'destination'}


class ReplicationError(Exception):
    """Falha fechada; nao inclui comando, path, dados ou configuracao privada."""


def configuration(values: dict) -> dict:
    if not isinstance(values, dict) or set(values) != FIELDS:
        raise ReplicationError
    if (not isinstance(values['host'], str) or
            not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{0,252}', values['host']) or
            not isinstance(values['user'], str) or
            not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', values['user']) or
            type(values['port']) is not int or not 1 <= values['port'] <= 65535):
        raise ReplicationError
    result = dict(values)
    for key in ('key_file', 'known_hosts_file', 'destination'):
        value = values[key]
        if not isinstance(value, str) or any(char in value for char in '\x00\r\n'):
            raise ReplicationError
        path = Path(value)
        if not path.is_absolute() or path.is_symlink():
            raise ReplicationError
        result[key] = path
    key = result['key_file']
    if (not key.is_file() or key.stat().st_mode & 0o077 or
            not result['known_hosts_file'].is_file()):
        raise ReplicationError
    destination = result['destination'].resolve()
    if key.resolve() == destination or destination in key.resolve().parents:
        raise ReplicationError
    return result


def load_configuration(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ReplicationError
    values = json.loads(path.read_text(encoding='utf8'))
    configuration(values)
    return values


def _fetch(config: dict, command: str, destination, limit: int) -> None:
    arguments = ['/usr/bin/ssh', '-F', '/dev/null', '-o', 'BatchMode=yes',
                 '-o', 'IdentitiesOnly=yes', '-o', 'IdentityAgent=none',
                 '-o', 'StrictHostKeyChecking=yes',
                 '-o', 'UserKnownHostsFile=' + str(config['known_hosts_file']),
                 '-o', 'GlobalKnownHostsFile=/dev/null', '-o', 'PasswordAuthentication=no',
                 '-o', 'KbdInteractiveAuthentication=no', '-o', 'ConnectTimeout=10',
                 '-o', 'ServerAliveInterval=10', '-o', 'ServerAliveCountMax=2',
                 '-i', str(config['key_file']), '-p', str(config['port']),
                 config['user'] + '@' + config['host'], command]
    process = subprocess.Popen(arguments, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    def timeout():
        try:
            process.kill()
        except ProcessLookupError:
            pass
    timer = threading.Timer(180, timeout)
    timer.daemon = True
    timer.start()
    try:
        total = 0
        while chunk := process.stdout.read(CHUNK_BYTES):
            total += len(chunk)
            if total > limit:
                raise ReplicationError
            destination.write(chunk)
        if process.wait(timeout=5):
            raise ReplicationError
    finally:
        timer.cancel()
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        process.stdout.close()


def _manifest(value: dict, now: datetime) -> tuple[dict, float]:
    if not isinstance(value, dict) or set(value) != {'schema', 'name', 'size', 'sha256', 'created_at'}:
        raise ReplicationError
    name = value['name']
    match = NAME.fullmatch(name) if isinstance(name, str) else None
    if (value['schema'] != 'stroop-encrypted-backup-v1' or not match or
            type(value['size']) is not int or
            not len(MAGIC) + NONCE_BYTES + TAG_BYTES <= value['size'] <= MAX_BYTES or
            not isinstance(value['sha256'], str) or
            not re.fullmatch('[0-9a-f]{64}', value['sha256'])):
        raise ReplicationError
    try:
        created = datetime.strptime(match[1], '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    except ValueError:
        raise ReplicationError from None
    if value['created_at'] != created.isoformat():
        raise ReplicationError
    age = (now - created).total_seconds()
    if age < -300:
        raise ReplicationError
    return value, max(0, age)


def _digest(path: Path) -> tuple[int, str]:
    if path.is_symlink() or not path.is_file():
        raise ReplicationError
    digest = hashlib.sha256()
    with path.open('rb') as source:
        if source.read(len(MAGIC)) != MAGIC:
            raise ReplicationError
        source.seek(0)
        size = 0
        while chunk := source.read(CHUNK_BYTES):
            size += len(chunk)
            if size > MAX_BYTES:
                raise ReplicationError
            digest.update(chunk)
    if size < len(MAGIC) + NONCE_BYTES + TAG_BYTES:
        raise ReplicationError
    return size, digest.hexdigest()


def _checksum(path: Path, expected: str) -> None:
    sidecar = path.with_suffix(path.suffix + '.sha256')
    contents = f'{expected}  {path.name}\n'.encode('ascii')
    try:
        descriptor = os.open(sidecar, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        if sidecar.is_symlink() or sidecar.read_bytes() != contents:
            raise ReplicationError from None
    else:
        with os.fdopen(descriptor, 'wb') as output:
            output.write(contents)
            output.flush()
            os.fsync(output.fileno())


def _rotate(destination: Path) -> int:
    verified = []
    for path in destination.glob('stroop-*.dump.enc'):
        match = NAME.fullmatch(path.name)
        if not match:
            continue
        try:
            datetime.strptime(match[1], '%Y%m%dT%H%M%SZ')
        except ValueError:
            continue
        sidecar = path.with_suffix(path.suffix + '.sha256')
        try:
            size, digest = _digest(path)
            if sidecar.is_symlink() or sidecar.read_text('ascii') != f'{digest}  {path.name}\n':
                continue
        except (OSError, UnicodeError, ReplicationError):
            continue
        verified.append(path)
    ordered = sorted(verified, reverse=True)
    for path in ordered[DEFAULT_GENERATIONS:]:
        path.unlink()
        path.with_suffix(path.suffix + '.sha256').unlink()
    return min(len(ordered), DEFAULT_GENERATIONS)


def run_once(values: dict, *, now: datetime | None = None) -> dict:
    config = configuration(values)
    destination = config['destination']
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    if destination.is_symlink() or not destination.is_dir():
        raise ReplicationError
    destination.chmod(0o700)
    lock = os.open(destination / '.replication.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    temporary = None
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        incoming = io.BytesIO()
        _fetch(config, 'manifest', incoming, 65536)
        manifest, age = _manifest(json.loads(incoming.getvalue()), now or datetime.now(timezone.utc))
        target = destination / manifest['name']
        copied = False
        if target.exists() or target.is_symlink():
            if _digest(target) != (manifest['size'], manifest['sha256']):
                raise ReplicationError
        else:
            descriptor, temporary_name = tempfile.mkstemp(prefix='.encrypted-backup-', dir=destination)
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, 'wb') as output:
                _fetch(config, 'download ' + manifest['name'], output, manifest['size'])
                output.flush()
                os.fsync(output.fileno())
            if _digest(temporary) != (manifest['size'], manifest['sha256']):
                raise ReplicationError
            os.link(temporary, target, follow_symlinks=False)
            temporary.unlink()
            temporary = None
            copied = True
        _checksum(target, manifest['sha256'])
        retained = _rotate(destination)
        directory = os.open(destination, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        stale = age > MAX_AGE_SECONDS
        return {'status': 'stale' if stale else ('copied' if copied else 'already_current'),
                'alert': stale, 'copied': copied, 'bytes': manifest['size'],
                'backup_age_seconds': round(age, 3), 'retained_generations': retained}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        os.close(lock)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--status-file', type=Path,
                        help='Ultimo resultado sanitizado, em diretorio privado existente')
    options = parser.parse_args(argv)
    try:
        values = load_configuration(options.config)
        report = run_once(values)
    except Exception:
        report = {'status': 'unavailable', 'alert': True, 'error': 'replication_failed'}
    if options.status_file is not None:
        try:
            save_status(options.status_file, report)
        except Exception:
            report = {'status': 'unavailable', 'alert': True, 'error': 'status_write_failed'}
    print(json.dumps(report))
    return int(report['alert'])


def save_status(path: Path, report: dict) -> None:
    """Publica ultimo resultado sem dados/credenciais; nao acumula logs."""
    if (not path.is_absolute() or path.is_symlink() or path.parent.is_symlink()
            or not path.parent.is_dir() or path.parent.stat().st_mode & 0o077):
        raise ReplicationError
    descriptor, name = tempfile.mkstemp(prefix='.replication-status-', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'w') as output:
            json.dump({**report, 'checked_at': datetime.now(timezone.utc).isoformat()}, output)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    raise SystemExit(main())
