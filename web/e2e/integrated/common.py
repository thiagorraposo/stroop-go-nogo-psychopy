"""Configuracao exclusivamente sintetica; nunca carrega .env ou dados locais."""
from pathlib import Path
from hashlib import sha256
import os
import sys
from urllib.parse import urlsplit, urlunsplit

import psycopg

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
ORIGIN = 'https://127.0.0.1:4373'
API_PORT = 4381
ISSUER = 'https://accounts.google.com'
SUBJECT = 'synthetic-integrated-admin'
SESSION_SECRET = 'synthetic-integrated-session-secret-never-use-0000000'
READER_PASSWORD = 'synthetic-read-only-never-use'
WRITER_PASSWORD = 'synthetic-write-only-never-use'


def database_url():
    value = os.environ.get('TEST_DATABASE_URL', '')
    if not value.startswith(('postgresql://', 'postgres://')):
        raise RuntimeError('TEST_DATABASE_URL sintetica obrigatoria.')
    name = psycopg.conninfo.conninfo_to_dict(value).get('dbname', '')
    if not name.startswith('stroop_etapa4_test'):
        raise RuntimeError('Banco descartavel sintetico obrigatorio.')
    return value


def role_url(kind, password):
    uri = urlsplit(database_url())
    host = uri.netloc.rsplit('@', 1)[-1]
    # Um namespace por banco/endpoint sintetico, sem assumir papeis globais alheios.
    # O provisionador ainda exige seu marcador canonico antes de reutilizar um papel.
    namespace = sha256(f'{host}{uri.path}'.encode('utf8')).hexdigest()[:16]
    role = f'synthetic_i_{namespace}_{kind}'
    return urlunsplit((uri.scheme, f'{role}:{password}@{host}', uri.path, uri.query, ''))


def read_url():
    return role_url('reader', READER_PASSWORD)


def write_url():
    return role_url('writer', WRITER_PASSWORD)


def environment():
    # O processo da API nao recebe DSN de proprietario ou configuracao operacional
    # herdada. Os helpers de fixtures continuam usando database_url() separadamente.
    inherited = {key: value for key, value in os.environ.items()
                 if not key.startswith(('API_', 'OIDC_')) and key not in
                 {'APP_ENV', 'TEST_DATABASE_URL', 'DATABASE_URL', 'AUTH_DATABASE_URL'}}
    return {**inherited, 'APP_ENV': 'test', 'API_DATABASE_URL': write_url(),
            'API_READ_DATABASE_URL': read_url(), 'API_PUBLIC_ORIGIN': ORIGIN,
            'OIDC_CLIENT_ID': 'synthetic-integrated-client',
            'OIDC_CLIENT_SECRET': 'synthetic-integrated-secret-never-use',
            'API_SESSION_SECRET': SESSION_SECRET, 'API_REDEEM_RATE_LIMIT': '100'}
