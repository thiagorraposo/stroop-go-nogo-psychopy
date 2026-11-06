"""Transacoes de credencial local, independentes das sessoes OIDC historicas."""
from __future__ import annotations

from uuid import uuid4
import psycopg
from stroop.domain.local_auth import LOCAL_ISSUER
from stroop.persistence.auth import PersistenceError

BOOTSTRAP_LOCK = 849403021


def _connect(database_url):
    return psycopg.connect(database_url, connect_timeout=5,
                           options='-c lock_timeout=5000 -c statement_timeout=10000')


def _event(connection, action, principal=None):
    connection.execute('INSERT INTO web_local_auth_events(principal_id,action) VALUES (%s,%s)',
                       (principal, action))


def provision(database_url: str, username: str, encoded: str, *, recover: bool = False) -> bool:
    """Operador exclusivo: bootstrap sem vinculos, ou recuperacao atomica."""
    try:
        with _connect(database_url) as connection:
            connection.execute('SELECT pg_advisory_xact_lock(%s)', (BOOTSTRAP_LOCK,))
            connection.execute('LOCK TABLE web_local_credentials IN EXCLUSIVE MODE')
            if not recover:
                if connection.execute('SELECT EXISTS(SELECT 1 FROM web_local_credentials)').fetchone()[0]:
                    return False
                principal = uuid4()
                connection.execute("INSERT INTO app_users(issuer,subject,role) VALUES (%s,%s,'administracao')",
                                   (LOCAL_ISSUER, str(principal)))
                connection.execute('INSERT INTO web_local_credentials(principal_id,username,password_hash) VALUES (%s,%s,%s)',
                                   (principal, username, encoded))
                _event(connection, 'bootstrap', principal)
            else:
                row = connection.execute('SELECT principal_id FROM web_local_credentials WHERE username=%s FOR UPDATE',
                                         (username,)).fetchone()
                if row is None:
                    return False
                principal = row[0]
                connection.execute("UPDATE app_users SET active=TRUE,role='administracao',updated_at=CURRENT_TIMESTAMP WHERE issuer=%s AND subject=%s",
                                   (LOCAL_ISSUER, str(principal)))
                _rotate(connection, principal, encoded)
                _event(connection, 'recovery', principal)
        return True
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _rotate(connection, principal, encoded):
    connection.execute('''UPDATE web_local_credentials SET password_hash=%s,
        credential_version=credential_version+1,updated_at=clock_timestamp() WHERE principal_id=%s''',
                       (encoded, principal))
    connection.execute('UPDATE web_local_sessions SET revoked_at=clock_timestamp() WHERE principal_id=%s AND revoked_at IS NULL',
                       (principal,))


def authenticate(database_url, username, password, bucket, token_hash, previous_hash,
                 verify, hash_password, needs_rehash):
    """Verifica e emite sob a trava da credencial: rotacao nao deixa sessao antiga.

    Callbacks criptograficos sao injetados pelo caso de uso; nenhum framework
    ou credencial em log. Janela por identificador e persistente e serializada.
    """
    try:
        with _connect(database_url) as connection:
            connection.execute('''INSERT INTO web_local_auth_limits VALUES (%s,clock_timestamp(),0)
                ON CONFLICT DO NOTHING''', (bucket,))
            row = connection.execute('''SELECT failure_count,
                window_started_at + INTERVAL '15 minutes' > clock_timestamp(),
                GREATEST(1,ceil(extract(epoch FROM (window_started_at + INTERVAL '15 minutes' - clock_timestamp()))))::integer
                FROM web_local_auth_limits WHERE bucket_sha256=%s FOR UPDATE''', (bucket,)).fetchone()
            failures, current, retry = row
            if current and failures >= 5:
                _event(connection, 'rate_limited')
                return 'limited', retry
            if not current:
                connection.execute('UPDATE web_local_auth_limits SET window_started_at=clock_timestamp(),failure_count=0 WHERE bucket_sha256=%s', (bucket,))
            # Ordem igual a recovery/rotacao: credencial, depois usuario.
            credential = connection.execute('''SELECT c.principal_id,c.password_hash,c.credential_version
                FROM web_local_credentials c WHERE username=%s FOR UPDATE''', (username,)).fetchone()
            valid = verify(credential[1] if credential else None, password)
            user = None
            if credential:
                user = connection.execute('SELECT role,active FROM public.web_lock_emitter(%s,%s)',
                                          (LOCAL_ISSUER, str(credential[0]))).fetchone()
            if not valid or not user or not user[1]:
                connection.execute('UPDATE web_local_auth_limits SET failure_count=LEAST(failure_count+1,5) WHERE bucket_sha256=%s', (bucket,))
                _event(connection, 'login_failure')
                return 'invalid', None
            principal, encoded, version = credential
            if needs_rehash(encoded):
                connection.execute('UPDATE web_local_credentials SET password_hash=%s,updated_at=clock_timestamp() WHERE principal_id=%s',
                                   (hash_password(password), principal))
            if previous_hash:
                connection.execute('UPDATE web_local_sessions SET revoked_at=clock_timestamp() WHERE token_sha256=%s AND revoked_at IS NULL', (previous_hash,))
            expires = connection.execute('''INSERT INTO web_local_sessions(token_sha256,principal_id,credential_version)
                VALUES (%s,%s,%s) RETURNING LEAST(absolute_expires_at,last_activity_at+INTERVAL '30 minutes')''',
                                         (token_hash, principal, version)).fetchone()[0]
            _event(connection, 'login_success', principal)
            return 'success', (principal, user[0], expires)
    except psycopg.Error as exc:
        raise PersistenceError from exc


def change_password(database_url, token_hash, current, encoded, verify):
    try:
        with _connect(database_url) as connection:
            # Buscar id nao autoriza; revalidacao e locks abaixo.
            row = connection.execute('SELECT principal_id FROM web_local_sessions WHERE token_sha256=%s', (token_hash,)).fetchone()
            if not row:
                return False
            principal = row[0]
            credential = connection.execute('SELECT password_hash,credential_version FROM web_local_credentials WHERE principal_id=%s FOR UPDATE', (principal,)).fetchone()
            user = connection.execute('SELECT active FROM public.web_lock_emitter(%s,%s)', (LOCAL_ISSUER, str(principal))).fetchone()
            if not user or not user[0]:
                return False
            session = connection.execute('''SELECT 1 FROM web_local_sessions s
                WHERE s.token_sha256=%s AND s.revoked_at IS NULL AND s.credential_version=%s
                AND s.absolute_expires_at>clock_timestamp() AND s.last_activity_at+INTERVAL '30 minutes'>clock_timestamp()
                ''', (token_hash, credential[1])).fetchone()
            if not session or not verify(credential[0], current):
                return False
            _rotate(connection, principal, encoded)
            _event(connection, 'password_change', principal)
        return True
    except psycopg.Error as exc:
        raise PersistenceError from exc


def revoke(database_url, token_hash):
    try:
        with _connect(database_url) as connection:
            row = connection.execute('''UPDATE web_local_sessions SET revoked_at=clock_timestamp()
                WHERE token_sha256=%s AND revoked_at IS NULL RETURNING principal_id''', (token_hash,)).fetchone()
            if row:
                _event(connection, 'logout', row[0])
    except psycopg.Error as exc:
        raise PersistenceError from exc


def session_context(database_url, token_hash, allowed_roles):
    """Revalida versao, usuario e prazos sob locks; nao renova atividade.

    O adaptador HTTP futuro deve registrar atividade somente depois de uma
    operacao efetivamente autorizada, nunca por /me ou por negacao de projeto.
    """
    try:
        with _connect(database_url) as connection:
            credential = connection.execute('''SELECT c.principal_id,c.credential_version
                FROM web_local_credentials c JOIN web_local_sessions s USING(principal_id)
                WHERE s.token_sha256=%s FOR SHARE OF c''', (token_hash,)).fetchone()
            if not credential:
                return 'invalid', None
            principal, version = credential
            user = connection.execute('SELECT role,active FROM public.web_lock_emitter(%s,%s)',
                                      (LOCAL_ISSUER, str(principal))).fetchone()
            row = connection.execute('''SELECT LEAST(absolute_expires_at,last_activity_at+INTERVAL '30 minutes')
                FROM web_local_sessions WHERE token_sha256=%s AND credential_version=%s
                AND revoked_at IS NULL AND absolute_expires_at>clock_timestamp()
                AND last_activity_at+INTERVAL '30 minutes'>clock_timestamp() FOR SHARE''',
                                     (token_hash, version)).fetchone()
            if not row or not user or not user[1]:
                return 'invalid', None
            if user[0] not in allowed_roles:
                return 'forbidden', None
            return 'success', (principal, user[0], row[0])
    except psycopg.Error as exc:
        raise PersistenceError from exc


def record_activity(database_url, token_hash):
    """Somente operacao autorizada; prazo absoluto e versao nunca prorrogados."""
    try:
        with _connect(database_url) as connection:
            # Mesma ordem de locks de login/rotacao; conta nao e criada aqui.
            credential = connection.execute('''SELECT c.principal_id,c.credential_version
                FROM web_local_credentials c JOIN web_local_sessions s USING(principal_id)
                WHERE s.token_sha256=%s FOR SHARE OF c''', (token_hash,)).fetchone()
            if not credential:
                return False
            user = connection.execute('SELECT active FROM public.web_lock_emitter(%s,%s)',
                                      (LOCAL_ISSUER, str(credential[0]))).fetchone()
            if not user or not user[0]:
                return False
            return connection.execute('''UPDATE web_local_sessions SET last_activity_at=clock_timestamp()
                WHERE token_sha256=%s AND credential_version=%s AND revoked_at IS NULL
                AND absolute_expires_at>clock_timestamp()
                AND last_activity_at+INTERVAL '30 minutes'>clock_timestamp()''',
                                      (token_hash, credential[1])).rowcount == 1
    except psycopg.Error as exc:
        raise PersistenceError from exc
