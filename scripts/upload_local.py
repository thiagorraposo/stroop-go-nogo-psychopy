#!/usr/bin/env python3
"""Recepcao local de CSV sintetico; nao e um servidor de producao."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

if __package__:
    from .importar_csv_postgres import import_csv, PostgresImportError, DuplicateAssessmentError
else:
    from importar_csv_postgres import import_csv, PostgresImportError, DuplicateAssessmentError

MAX_BYTES = 5 * 1024 * 1024


def process_upload(
    content: bytes,
    filename: str,
    database_url: str,
    *,
    temp_root=None,
    audit=None,
    origin="upload local",
):
    """Valida o envelope, isola os bytes e importa sem sobrescrever duplicatas."""
    upload_id = uuid.uuid4().hex
    statuses = []
    content_sha256 = hashlib.sha256(
        content if isinstance(content, bytes) else b""
    ).hexdigest()
    error_code = None

    def event(status):
        statuses.append(status)
        record = {"id": upload_id, "origin": origin,
                  "at": datetime.now(timezone.utc).isoformat(), "status": status}
        if audit:
            audit(record)

    event("recebido")
    try:
        if not isinstance(content, bytes):
            error_code = "invalid_envelope"
            raise ValueError
        if not isinstance(filename, str) or not filename.lower().endswith('.csv'):
            error_code = "invalid_envelope"
            raise ValueError
        if not 0 < len(content) <= MAX_BYTES:
            error_code = "invalid_envelope"
            raise ValueError
        text = content.decode('utf-8-sig', errors='strict')
        if '\x00' in text:
            error_code = "invalid_envelope"
            raise ValueError
        # Nunca usa o nome fornecido como caminho e nunca executa o conteudo.
        with tempfile.TemporaryDirectory(prefix='stroop-upload-', dir=temp_root) as directory:
            path = Path(directory) / (upload_id + '.csv')
            path.write_bytes(content)
            path.chmod(0o600)
            import_csv(path, validate_only=True)
            event('validado')
            import_csv(path, database_url)
        event('importado')
        message = 'Importacao concluida.'
    except DuplicateAssessmentError:
        error_code = "duplicate_assessment"
        event('rejeitado')
        message = 'Avaliacao ja importada; nenhuma substituicao realizada.'
    except (ValueError, UnicodeError, OSError, PostgresImportError):
        error_code = error_code or "validation_or_service_failure"
        event('rejeitado')
        message = 'Arquivo rejeitado ou importacao nao confirmada. Verifique o CSV e o servico.'
    return {
        "id": upload_id,
        "statuses": statuses,
        "status": statuses[-1],
        "content_sha256": content_sha256,
        "error_code": error_code,
        "message": message,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Abre a area autenticada de importacao.')
    parser.add_argument('--local', action='store_true', help='Habilita explicitamente o uso local.')
    parser.add_argument('--port', type=int, default=8501)
    args = parser.parse_args(argv)
    if (not args.local or os.environ.get('APP_ENV', 'local') not in {'local', 'development', 'test'}
            or not os.environ.get('DATABASE_URL')
            or not os.environ.get('AUTH_DATABASE_URL')
            or not 1 <= args.port <= 65535):
        print('Inicializacao recusada. Configure o ambiente local autenticado.')
        return 1
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment['STROOP_INITIAL_SECTION'] = 'Importacao'
    command = [
        sys.executable,
        '-m',
        'streamlit',
        'run',
        str(root / 'dashboard' / 'app.py'),
        '--server.address=127.0.0.1',
        f'--server.port={args.port}',
    ]
    try:
        return subprocess.run(command, cwd=root, env=environment, check=False).returncode
    except (OSError, KeyboardInterrupt):
        print('Nao foi possivel iniciar a area autenticada.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
