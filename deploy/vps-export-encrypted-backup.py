#!/usr/bin/env python3
"""Comando SSH forcado: exporta somente backups PostgreSQL criptografados."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.backup_postgres import CHUNK_BYTES, MAGIC, NONCE_BYTES, TAG_BYTES, verify_checksum


BASE = Path('/home/raposo/.local/share/stroop-web/backups/web')
NAME = re.compile(r'stroop-([0-9]{8}T[0-9]{6}Z)\.dump\.enc')
MAX_BYTES = 512 * 1024 * 1024


class ExportError(Exception):
    pass


def backup_path(base: Path, name: str) -> Path:
    match = NAME.fullmatch(name)
    if not match:
        raise ExportError
    try:
        datetime.strptime(match[1], '%Y%m%dT%H%M%SZ')
    except ValueError:
        raise ExportError from None
    path = base / name
    if path.is_symlink() or path.resolve().parent != base.resolve():
        raise ExportError
    return path


def describe(base: Path, name: str) -> dict:
    path = backup_path(base, name)
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or not len(MAGIC) + NONCE_BYTES + TAG_BYTES <= info.st_size <= MAX_BYTES:
            raise ExportError
        digest = hashlib.sha256()
        with os.fdopen(descriptor, 'rb', closefd=False) as source:
            if source.read(len(MAGIC)) != MAGIC:
                raise ExportError
            source.seek(0)
            while chunk := source.read(CHUNK_BYTES):
                digest.update(chunk)
        if path.with_suffix(path.suffix + '.sha256').is_symlink():
            raise ExportError
        verify_checksum(path)
        created = datetime.strptime(NAME.fullmatch(name)[1], '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
        return {'schema': 'stroop-encrypted-backup-v1', 'name': name,
                'size': info.st_size, 'sha256': digest.hexdigest(),
                'created_at': created.isoformat()}
    finally:
        os.close(descriptor)


def export(command: str, *, base: Path = BASE, output=None) -> None:
    """Nao aceita caminhos, chaves, stdin ou argumentos livres do cliente SSH."""
    output = sys.stdout.buffer if output is None else output
    if command == 'manifest':
        names = sorted(path.name for path in base.glob('stroop-*.dump.enc')
                       if NAME.fullmatch(path.name))
        if not names:
            raise ExportError
        result = describe(base, names[-1])
        output.write(json.dumps(result, separators=(',', ':')).encode('ascii') + b'\n')
    elif command.startswith('download ') and command.count(' ') == 1:
        name = command[9:]
        result = describe(base, name)
        path = backup_path(base, name)
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            digest = hashlib.sha256()
            written = 0
            with os.fdopen(descriptor, 'rb', closefd=False) as source:
                while chunk := source.read(CHUNK_BYTES):
                    written += len(chunk)
                    if written > result['size']:
                        raise ExportError
                    digest.update(chunk)
                    output.write(chunk)
            if written != result['size'] or digest.hexdigest() != result['sha256']:
                raise ExportError
        finally:
            os.close(descriptor)
    else:
        raise ExportError


def main() -> int:
    try:
        if len(sys.argv) != 1:
            raise ExportError
        export(os.environ.get('SSH_ORIGINAL_COMMAND', ''))
        return 0
    except Exception:
        print('Exportacao de backup recusada.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
