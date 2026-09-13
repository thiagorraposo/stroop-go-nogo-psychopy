#!/usr/bin/env python3
"""Recepcao local de CSV sintetico; nao e um servidor de producao."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import secrets
from socketserver import ThreadingMixIn
import tempfile
import threading
from urllib.parse import unquote
import uuid

if __package__:
    from .importar_csv_postgres import import_csv, PostgresImportError, DuplicateAssessmentError
else:
    from importar_csv_postgres import import_csv, PostgresImportError, DuplicateAssessmentError

MAX_BYTES = 5 * 1024 * 1024
MAX_CONCURRENT = 4

PAGE = r'''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Importar CSV Stroop</title>
<style>body{font:18px system-ui;max-width:680px;margin:60px auto;padding:24px;background:#f5f7fa;color:#172636}button,input{font:inherit;margin:12px 0}button{padding:12px}pre{white-space:pre-wrap}</style>
<h1>Importar CSV Stroop</h1>
<p>Uso local com dados sintéticos. Selecione um CSV UTF-8 de até 5 MiB.
Avaliações já importadas serão rejeitadas. O arquivo enviado será descartado após o processamento.</p>
<form id="form"><label for="file">Arquivo CSV</label><br>
<input id="file" type="file" accept=".csv" required><br>
<button id="send">Enviar e importar</button></form>
<pre id="status" role="status" aria-live="polite"></pre>
<script>
const form=document.getElementById('form'), file=document.getElementById('file'),
status=document.getElementById('status'), send=document.getElementById('send');
form.onsubmit=async(e)=>{e.preventDefault();const f=file.files[0];
if(!f || file.files.length!==1 || !f.name.toLowerCase().endsWith('.csv') || f.size>5242880 || !f.size){status.textContent='Rejeitado: selecione um CSV de até 5 MiB.';return;}
send.disabled=true;status.textContent='Enviando…';
try{const response=await fetch('/upload',{method:'POST',headers:{'Content-Type':'text/csv','X-Upload-Token':'TOKEN_VALUE','X-Upload-Name':encodeURIComponent(f.name)},body:f});
const result=await response.json();status.textContent=(result.statuses||['rejeitado']).join(' → ')+'\n'+result.message;
}catch(e){status.textContent='Resposta não confirmada. Confira o serviço local antes de tentar novamente.';}
finally{send.disabled=false;file.value='';}};
</script></html>'''


def process_upload(content: bytes, filename: str, database_url: str, *, temp_root=None, audit=None):
    """Valida o envelope, isola os bytes e importa sem sobrescrever duplicatas."""
    upload_id = uuid.uuid4().hex
    statuses = []

    def event(status):
        statuses.append(status)
        record = {"id": upload_id, "origin": "upload local",
                  "at": datetime.now(timezone.utc).isoformat(), "status": status}
        if audit:
            audit(record)

    event("recebido")
    try:
        if not isinstance(filename, str) or not filename.lower().endswith('.csv'):
            raise ValueError
        if not 0 < len(content) <= MAX_BYTES:
            raise ValueError
        text = content.decode('utf-8-sig', errors='strict')
        if '\x00' in text:
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
        event('rejeitado')
        message = 'Avaliacao ja importada; nenhuma substituicao realizada.'
    except (ValueError, UnicodeError, OSError, PostgresImportError):
        event('rejeitado')
        message = 'Arquivo rejeitado ou importacao nao confirmada. Verifique o CSV e o servico local.'
    return {"id": upload_id, "statuses": statuses, "message": message}


class UploadServer(ThreadingMixIn, HTTPServer):
    daemon_threads = False
    block_on_close = True

    def __init__(self, port, database_url, *, temp_root=None, audit=None):
        self.database_url = database_url
        self.temp_root = temp_root
        self.audit = audit
        self.token = secrets.token_urlsafe(32)
        self.slots = threading.BoundedSemaphore(MAX_CONCURRENT)
        super().__init__(('127.0.0.1', port), UploadHandler)
        self.origin = f'http://127.0.0.1:{self.server_port}'

    def process_request(self, request, client_address):
        # Limita threads e memoria antes da leitura de qualquer corpo.
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        # Nao imprime traceback com caminhos, headers ou dados enviados.
        pass


class UploadHandler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(15)
        super().setup()

    def log_message(self, format, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self.reply(code, {"statuses": ['rejeitado'], "message": 'Requisicao rejeitada.'})

    def reply(self, code, payload, *, html=False):
        data = payload.encode('utf-8') if html else json.dumps(payload).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8' if html else 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; form-action 'self'")
        self.send_header('Connection', 'close')
        self.end_headers()
        self.close_connection = True
        self.wfile.write(data)

    def valid_host(self):
        return self.headers.get_all('Host') == [f'127.0.0.1:{self.server.server_port}']

    def do_GET(self):
        if not self.valid_host() or self.path != '/':
            self.send_error(403)
            return
        self.reply(200, PAGE.replace('TOKEN_VALUE', self.server.token), html=True)

    def do_POST(self):
        if (not self.valid_host() or self.path != '/upload'
                or self.headers.get_all('Origin') != [self.server.origin]
                or self.headers.get_all('X-Upload-Token') != [self.server.token]):
            self.send_error(403)
            return
        lengths = self.headers.get_all('Content-Length', [])
        names = self.headers.get_all('X-Upload-Name', [])
        if (len(lengths) != 1 or not lengths[0].isdigit()
                or not 0 < int(lengths[0]) <= MAX_BYTES
                or self.headers.get('Transfer-Encoding') is not None
                or self.headers.get_all('Content-Type') != ['text/csv']
                or len(names) != 1):
            self.send_error(400)
            return
        size = int(lengths[0])
        try:
            content = self.rfile.read(size)
            if len(content) != size:
                self.send_error(400)
                return
            result = process_upload(content, unquote(names[0]), self.server.database_url,
                                    temp_root=self.server.temp_root, audit=self.server.audit)
            self.reply(200 if result['statuses'][-1] == 'importado' else 422, result)
        except (TimeoutError, ConnectionError, OSError):
            self.close_connection = True


def main(argv=None):
    parser = argparse.ArgumentParser(description='Upload local de CSV sintetico.')
    parser.add_argument('--local', action='store_true', help='Habilita explicitamente o uso local.')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args(argv)
    if (not args.local or os.environ.get('APP_ENV', 'local') not in {'local', 'development', 'test'}
            or not os.environ.get('DATABASE_URL') or not 1 <= args.port <= 65535):
        print('Inicializacao recusada. Use --local, ambiente local e DATABASE_URL configurada.')
        return 1
    audit_lock = threading.Lock()

    def audit(record):
        with audit_lock:
            print(json.dumps(record), flush=True)

    try:
        with UploadServer(args.port, os.environ['DATABASE_URL'], audit=audit) as server:
            print(f'Upload local: {server.origin}', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    except OSError:
        print('Nao foi possivel iniciar o upload local.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
