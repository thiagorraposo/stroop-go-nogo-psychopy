"""Renovacao de atividade apos sucesso; executada fora do event loop ASGI."""
from datetime import datetime, timezone
from starlette.responses import Response

from stroop.application.local_auth import session_context
from stroop.persistence.local_auth import record_activity
from stroop.persistence.auth import PersistenceError


def activity_cookie(config, token_hash, token):
    cookie = Response()
    def expired_cookie():
        cookie.delete_cookie('__Host-stroop_professional', path='/', secure=True, httponly=True, samesite='lax')
        return [(key, value) for key, value in cookie.raw_headers if key == b'set-cookie']
    try:
        if not record_activity(config.database_url, token_hash):
            return expired_cookie()
        status, details = session_context(config.database_url, token_hash, 'view_dashboard')
        if status != 'success':
            return expired_cookie()
    except PersistenceError:
        # A operacao ja terminou: nao converter commit em rejeicao aparente.
        # Falha de renovacao encerra o cookie; proxima operacao exige sessao valida.
        return expired_cookie()
    expires = details[2].astimezone(timezone.utc)
    cookie.set_cookie('__Host-stroop_professional', token,
        max_age=max(0, int((expires-datetime.now(timezone.utc)).total_seconds())),
        expires=expires, path='/', secure=True, httponly=True, samesite='lax')
    return [(key, value) for key, value in cookie.raw_headers if key == b'set-cookie']
