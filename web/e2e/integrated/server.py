"""API real + proxy HTTPS local para build real, em banco descartavel explicito."""
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import urlsplit

from common import API_PORT, ISSUER, ORIGIN, ROOT, SUBJECT, database_url, environment, read_url, write_url
import psycopg
from scripts.migrations import apply_migrations
from scripts.provision_web_database import provision
from stroop.application import auth


def main():
    database = database_url()  # Guard antes de qualquer reset de schema.
    for port in (4373, API_PORT):
        with socket.socket() as check:
            check.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            check.bind(('127.0.0.1', port))
    with psycopg.connect(database, autocommit=True) as connection:
        connection.execute('DROP SCHEMA public CASCADE')
        connection.execute('CREATE SCHEMA public')
    apply_migrations(database)
    auth.bootstrap_admin(database, ISSUER, SUBJECT)
    provision({'API_MIGRATION_DATABASE_URL': database,
               'API_DATABASE_URL': write_url(), 'API_READ_DATABASE_URL': read_url()})
    with psycopg.connect(write_url()) as connection:
        if connection.execute("""SELECT rolsuper,rolcreatedb,rolcreaterole,
            has_schema_privilege(current_user,'public','CREATE'),
            has_column_privilege(current_user,'public.app_users','issuer','INSERT'),
            has_column_privilege(current_user,'public.app_users','role','UPDATE')
            FROM pg_roles WHERE rolname=current_user""").fetchone() != (False,) * 6:
            raise RuntimeError('Writer sintetico deve permanecer restrito.')
    children = []
    with tempfile.TemporaryDirectory(prefix='stroop-synthetic-https-') as directory:
        private = Path(directory) / 'key.pem'
        certificate = Path(directory) / 'cert.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                        '-subj', '/CN=127.0.0.1', '-addext', 'subjectAltName=IP:127.0.0.1',
                        '-keyout', str(private), '-out', str(certificate)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with (Path(directory) / 'server.log').open('w') as log:
            try:
                api = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'api.main:create_app', '--factory',
                                        '--host', '127.0.0.1', '--port', str(API_PORT), '--no-access-log'],
                                       cwd=ROOT, env=environment(), stdout=log, stderr=log)
                children.append(api)
                for _ in range(100):
                    if api.poll() is not None:
                        raise RuntimeError('API sintetica nao iniciou.')
                    try:
                        request = urllib.request.Request(f'http://127.0.0.1:{API_PORT}/health/live', headers={'Host': urlsplit(ORIGIN).netloc})
                        with urllib.request.urlopen(request, timeout=.2):
                            break
                    except OSError:
                        time.sleep(.1)
                else:
                    raise RuntimeError('API sintetica nao ficou pronta.')
                proxy = subprocess.Popen(['node', str(Path(__file__).with_name('proxy.mjs'))], cwd=ROOT,
                    env={**os.environ, 'STROOP_TEST_TLS_KEY': str(private), 'STROOP_TEST_TLS_CERT': str(certificate)},
                    stdout=log, stderr=log)
                children.append(proxy)
                print(f'Integracao sintetica HTTPS local: {ORIGIN}', flush=True)
                while all(child.poll() is None for child in children):
                    time.sleep(.2)
                raise RuntimeError('Servidor sintetico encerrou antes dos testes.')
            finally:
                for child in reversed(children):
                    if child.poll() is None:
                        child.terminate()
                for child in reversed(children):
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill(); child.wait()


def stop(_signal, _frame):
    raise KeyboardInterrupt


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, stop)
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        print('Falha no ambiente sintetico HTTPS; confira banco descartavel, portas e dependencias.', file=sys.stderr)
        raise SystemExit(1) from None
