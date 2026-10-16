"""Configuracao exclusivamente sintetica; nunca carrega .env ou dados locais."""
from pathlib import Path
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
READER = 'synthetic_integration_reader'
READER_PASSWORD = 'synthetic-read-only-never-use'


def database_url():
    value = os.environ.get('TEST_DATABASE_URL', '')
    if not value.startswith(('postgresql://', 'postgres://')):
        raise RuntimeError('TEST_DATABASE_URL sintetica obrigatoria.')
    name = psycopg.conninfo.conninfo_to_dict(value).get('dbname', '')
    if not name.startswith('stroop_etapa4_test'):
        raise RuntimeError('Banco descartavel sintetico obrigatorio.')
    return value


def read_url():
    uri = urlsplit(database_url())
    host = uri.netloc.rsplit('@', 1)[-1]
    return urlunsplit((uri.scheme, f'{READER}:{READER_PASSWORD}@{host}', uri.path, uri.query, ''))


def environment():
    return {**os.environ, 'APP_ENV': 'test', 'API_DATABASE_URL': database_url(),
            'API_READ_DATABASE_URL': read_url(), 'API_PUBLIC_ORIGIN': ORIGIN,
            'OIDC_CLIENT_ID': 'synthetic-integrated-client',
            'OIDC_CLIENT_SECRET': 'synthetic-integrated-secret-never-use',
            'API_SESSION_SECRET': SESSION_SECRET, 'API_REDEEM_RATE_LIMIT': '100'}
