"""Transacoes de credencial local, independentes das sessoes OIDC historicas."""
from __future__ import annotations

from uuid import uuid4
import re
import psycopg
from stroop.domain.local_auth import LOCAL_ISSUER
from stroop.persistence.auth import PersistenceError

BOOTSTRAP_LOCK = 849403021
LIMIT_ADMISSION_LOCK = 849403022
# Limite tecnico de memoria persistente, nao prazo de retencao de eventos.
MAX_LIMIT_BUCKETS = 10000
MAX_LIMIT_WINDOW_SECONDS = 86400
BUCKET_PATTERN = re.compile(r'^[0-9a-f]{64}$')


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


def _prepare_attempt(database_url, bucket, origin_bucket, origin_limit, origin_window_seconds):
    """Admissao curta separada do Argon2; cap atomico inclusive entre processos.

    Buckets sao HMAC calculados pelo adaptador com dominios separados para
    origem e identificador. Somente janelas vencidas ha pelo menos 24h sao
    removidas; nenhuma janela configuravel pode ultrapassar esse teto.
    """
    if (not BUCKET_PATTERN.fullmatch(bucket)
            or (origin_bucket is not None and (not BUCKET_PATTERN.fullmatch(origin_bucket)
                                               or origin_bucket == bucket))
            or type(origin_limit) is not int or not 1 <= origin_limit <= 1000
            or type(origin_window_seconds) is not int
            or not 1 <= origin_window_seconds <= MAX_LIMIT_WINDOW_SECONDS):
        raise ValueError('Configuracao de limite invalida.')
    try:
        with _connect(database_url) as connection:
            connection.execute('SELECT pg_advisory_xact_lock(%s)', (LIMIT_ADMISSION_LOCK,))
            # Nenhuma verificacao/hash executa enquanto esta trava e mantida.
            connection.execute("""DELETE FROM web_local_auth_limits
                WHERE window_started_at <= clock_timestamp() - INTERVAL '24 hours'""")

            def reserve(key):
                if connection.execute('SELECT 1 FROM web_local_auth_limits WHERE bucket_sha256=%s', (key,)).fetchone():
                    return True
                if connection.execute('SELECT count(*) FROM web_local_auth_limits').fetchone()[0] >= MAX_LIMIT_BUCKETS:
                    return False
                connection.execute('INSERT INTO web_local_auth_limits VALUES (%s,clock_timestamp(),0)', (key,))
                return True
            if origin_bucket is not None:
                if not reserve(origin_bucket):
                    return 60
                row = connection.execute("""SELECT failure_count,
                    window_started_at + make_interval(secs => %s)>clock_timestamp(),
                    GREATEST(1,ceil(extract(epoch FROM
                        (window_started_at + make_interval(secs => %s)-clock_timestamp()))))::integer
                    FROM web_local_auth_limits WHERE bucket_sha256=%s FOR UPDATE""",
                    (origin_window_seconds, origin_window_seconds, origin_bucket)).fetchone()
                count, current, retry = row
                if current and count >= origin_limit:
                    return retry
                connection.execute("""UPDATE web_local_auth_limits SET
                    window_started_at=CASE WHEN %s THEN window_started_at ELSE clock_timestamp() END,
                    failure_count=CASE WHEN %s THEN failure_count+1 ELSE 1 END
                    WHERE bucket_sha256=%s""", (current, current, origin_bucket))
            if not reserve(bucket):
                return 60
        return None
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _failure_window(connection, bucket):
    row = connection.execute("""SELECT failure_count,
        window_started_at + INTERVAL '15 minutes' > clock_timestamp(),
        GREATEST(1,ceil(extract(epoch FROM (window_started_at + INTERVAL '15 minutes' - clock_timestamp()))))::integer
        FROM web_local_auth_limits WHERE bucket_sha256=%s FOR UPDATE""", (bucket,)).fetchone()
    # Uma limpeza concorrente de bucket muito antigo so pode negar, nunca burlar.
    if not row:
        return 60
    failures, current, retry = row
    if current and failures >= 5:
        _event(connection, 'rate_limited')
        return retry
    if not current:
        connection.execute('UPDATE web_local_auth_limits SET window_started_at=clock_timestamp(),failure_count=0 WHERE bucket_sha256=%s', (bucket,))
    return None


def _record_failure(connection, bucket):
    if bucket is not None:
        connection.execute('UPDATE web_local_auth_limits SET failure_count=LEAST(failure_count+1,5) WHERE bucket_sha256=%s', (bucket,))
    _event(connection, 'login_failure')


def authenticate(database_url, username, password, bucket, token_hash, previous_hash,
                 verify, hash_password, needs_rehash, *, origin_bucket=None,
                 origin_limit=20, origin_window_seconds=60):
    """Verifica e emite sob a trava da credencial: rotacao nao deixa sessao antiga.

    Callbacks criptograficos sao injetados pelo caso de uso; nenhum framework
    ou credencial em log. Janela por identificador e persistente e serializada.
    """
    retry = _prepare_attempt(database_url, bucket, origin_bucket, origin_limit, origin_window_seconds)
    if retry is not None:
        return 'limited', retry
    try:
        with _connect(database_url) as connection:
            retry = _failure_window(connection, bucket)
            if retry is not None:
                return 'limited', retry
            # Ordem igual a recovery/rotacao: credencial, depois usuario.
            credential = connection.execute('''SELECT c.principal_id,c.password_hash,c.credential_version
                FROM web_local_credentials c WHERE username=%s FOR UPDATE''', (username,)).fetchone()
            valid = verify(credential[1] if credential else None, password)
            user = None
            if credential:
                user = connection.execute('SELECT role,active FROM public.web_lock_emitter(%s,%s)',
                                          (LOCAL_ISSUER, str(credential[0]))).fetchone()
            if not valid or not user or not user[1]:
                _record_failure(connection, bucket)
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


def change_password(database_url, token_hash, current, new_password, verify, hash_password, *,
                    bucket_for_username=None, origin_bucket=None, origin_limit=20,
                    origin_window_seconds=60):
    try:
        bucket = None
        if bucket_for_username is not None:
            # Esta leitura descobre somente o bucket; nao autoriza a operacao.
            with _connect(database_url) as connection:
                row = connection.execute("""SELECT c.username FROM web_local_credentials c
                    JOIN web_local_sessions s USING(principal_id) WHERE s.token_sha256=%s""",
                    (token_hash,)).fetchone()
            if not row:
                return 'invalid', None
            bucket = bucket_for_username(row[0])
            retry = _prepare_attempt(database_url, bucket, origin_bucket, origin_limit, origin_window_seconds)
            if retry is not None:
                return 'limited', retry
        with _connect(database_url) as connection:
            # Ordem igual a login: bucket, credencial, usuario, sessao.
            if bucket is not None:
                retry = _failure_window(connection, bucket)
                if retry is not None:
                    return 'limited', retry
            row = connection.execute('SELECT principal_id FROM web_local_sessions WHERE token_sha256=%s', (token_hash,)).fetchone()
            if not row:
                return 'invalid', None
            principal = row[0]
            credential = connection.execute('SELECT password_hash,credential_version FROM web_local_credentials WHERE principal_id=%s FOR UPDATE', (principal,)).fetchone()
            if not credential:
                return 'invalid', None
            user = connection.execute('SELECT active FROM public.web_lock_emitter(%s,%s)', (LOCAL_ISSUER, str(principal))).fetchone()
            session = connection.execute("""SELECT 1 FROM web_local_sessions s
                WHERE s.token_sha256=%s AND s.revoked_at IS NULL AND s.credential_version=%s
                AND s.absolute_expires_at>clock_timestamp() AND s.last_activity_at+INTERVAL '30 minutes'>clock_timestamp()
                """, (token_hash, credential[1])).fetchone()
            if not session or not user or not user[0]:
                return 'invalid', None
            if not verify(credential[0], current):
                _record_failure(connection, bucket)
                return 'invalid', None
            # Custo de hash novo somente depois de limite e verificacao atuais.
            _rotate(connection, principal, hash_password(new_password))
            _event(connection, 'password_change', principal)
        return 'success', None
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
