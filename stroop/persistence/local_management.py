"""Revogacao administrativa local com revalidacao transacional do ator."""
from stroop.domain.local_auth import LOCAL_ISSUER
from stroop.persistence.local_auth import _connect, _event
from stroop.persistence.auth import PersistenceError
import psycopg


def revoke_sessions(database_url, actor, principal):
    try:
        with _connect(database_url) as connection:
            # Mesmo lock do gestor de usuarios: serializa bloqueio/downgrade do ator.
            user = connection.execute('SELECT role,active FROM public.web_lock_emitter(%s,%s)',
                                      (actor.issuer, actor.subject)).fetchone()
            if not user or user != ('administracao', True):
                return 'forbidden'
            target = connection.execute('SELECT 1 FROM web_local_credentials WHERE principal_id=%s',
                                        (principal,)).fetchone()
            if not target:
                return 'missing'
            connection.execute('UPDATE web_local_sessions SET revoked_at=clock_timestamp() WHERE principal_id=%s AND revoked_at IS NULL',
                               (principal,))
            _event(connection, 'sessions_revoke', principal)
        return 'success'
    except psycopg.Error as exc:
        raise PersistenceError from exc


def user_email(database_url, issuer, subject):
    try:
        with _connect(database_url) as connection:
            row = connection.execute('SELECT email FROM app_users WHERE issuer=%s AND subject=%s',
                                     (issuer, subject)).fetchone()
            return row
    except psycopg.Error as exc:
        raise PersistenceError from exc
