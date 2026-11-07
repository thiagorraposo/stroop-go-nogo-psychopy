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
ISSUER = 'urn:stroop:local'
USERNAME = 'synthetic-integrated-admin'
PASSWORD = 'Frase sintética integração local 2026 🌱'
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
            'API_AUTH_MODE': 'local',
            'API_SESSION_SECRET': SESSION_SECRET, 'API_REDEEM_RATE_LIMIT': '100'}


def fixture_user(role):
    """Operador de teste: perfis extras para regressao; nao e cadastro do produto."""
    from uuid import uuid4
    from stroop.security.passwords import hash_password
    if role not in {'consulta', 'importacao', 'administracao'}:
        raise ValueError('Perfil sintetico invalido.')
    principal = uuid4()
    encoded = hash_password(PASSWORD)
    with psycopg.connect(database_url()) as connection:
        connection.execute('INSERT INTO app_users(issuer,subject,role) VALUES(%s,%s,%s)',
                           (ISSUER, str(principal), role))
        connection.execute('INSERT INTO web_local_credentials(principal_id,username,password_hash) VALUES(%s,%s,%s)',
                           (principal, f'synthetic-{principal.hex}', encoded))
    return str(principal)


def primary_subject():
    with psycopg.connect(database_url()) as connection:
        return str(connection.execute('SELECT principal_id FROM web_local_credentials WHERE username=%s', (USERNAME,)).fetchone()[0])


def fixture_session(subject=None):
    """Sessao local real injetada para ensaios de papeis/projetos.

    Login por senha/React e comprovado separadamente em e2e/local-auth.
    """
    import secrets
    from uuid import UUID
    from stroop.domain.auth import opaque_user_id
    token = secrets.token_urlsafe(32)
    principal = UUID(subject or primary_subject())
    with psycopg.connect(database_url()) as connection:
        row = connection.execute('''INSERT INTO web_local_sessions(token_sha256,principal_id,credential_version)
            SELECT %s,principal_id,credential_version FROM web_local_credentials WHERE principal_id=%s
            RETURNING principal_id''', (sha256(token.encode('ascii')).hexdigest(), principal)).fetchone()
        if row is None:
            raise RuntimeError('Credencial sintetica ausente.')
    return token, opaque_user_id(ISSUER, str(principal))
