"""Adaptador da credencial local; nenhuma senha ou token em respostas/logs."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from api.auth import (PROFESSIONAL_COOKIE, TOKEN_PATTERN, _cookie, _csrf_token,
                      _origin_is_valid, _professional_context, csrf_is_valid)
from api.errors import APIError
from api.models import RequestModel
from stroop.application import local_auth as application
from stroop.domain.auth import opaque_user_id
from stroop.domain.local_auth import LOCAL_ISSUER, InvalidCredential
from stroop.persistence.auth import PersistenceError
from stroop.security.passwords import PasswordServiceUnavailable

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


class LoginRequest(RequestModel):
    username: str
    password: str


class PasswordRequest(RequestModel):
    current_password: str
    new_password: str


def _local(request):
    if request.app.state.config.auth_mode != 'local':
        raise APIError('not_found')
    if request.query_params:
        raise APIError('invalid_request')
    if not _origin_is_valid(request, request.app.state.config):
        raise APIError('csrf_failed')


def _bucket(config, namespace, value):
    return hmac.new(config.session_secret.encode('utf-8'),
                    b'stroop-local-rate-v1\0' + namespace.encode('ascii') + b'\0' + value.encode('utf-8'),
                    hashlib.sha256).hexdigest()


def _origin_bucket(request):
    # ASGI peer somente; o servidor/proxy deve sobrescrever headers encaminhados.
    peer = request.client.host if request.client else 'unknown'
    return _bucket(request.app.state.config, 'origin', peer)


def _invalid_login(request):
    return JSONResponse({'error': {'code': 'authentication_required',
        'message': 'Usuário ou senha inválidos.'}, 'request_id': request.state.request_id},
        status_code=401, headers={'Cache-Control': 'no-store'})


def _clear_cookie(response):
    response.delete_cookie(PROFESSIONAL_COOKIE, path='/', secure=True, httponly=True, samesite='lax')


@router.post('/login')
def login(request: Request, body: LoginRequest):
    _local(request)
    config = request.app.state.config
    token = secrets.token_urlsafe(32)
    previous = _cookie(request, PROFESSIONAL_COOKIE)
    previous_hash = (hashlib.sha256(previous.encode('ascii')).hexdigest()
                     if previous and TOKEN_PATTERN.fullmatch(previous) else None)
    try:
        # Normalizacao feita pelo dominio antes de calcular o identificador HMAC.
        from stroop.domain.local_auth import normalize_username
        status, details = application.authenticate(config.database_url, body.username, body.password,
            _bucket(config, 'identifier', normalize_username(body.username)),
            hashlib.sha256(token.encode('ascii')).hexdigest(), previous_hash,
            origin_bucket=_origin_bucket(request), origin_limit=config.login_rate_limit,
            origin_window_seconds=config.login_rate_window_seconds)
    except InvalidCredential:
        raise APIError('invalid_request') from None
    except (PersistenceError, PasswordServiceUnavailable):
        raise APIError('service_unavailable') from None
    if status == 'limited':
        raise APIError('rate_limited', headers={'Retry-After': str(details)})
    if status != 'success':
        return _invalid_login(request)
    principal, role, expires = details
    response = JSONResponse({'user_id': opaque_user_id(LOCAL_ISSUER, str(principal)), 'role': role,
        'expires_at': expires.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'csrf_token': _csrf_token(config, token)})
    response.set_cookie(PROFESSIONAL_COOKIE, token,
        max_age=max(0, int((expires-datetime.now(timezone.utc)).total_seconds())),
        expires=expires.astimezone(timezone.utc), secure=True, httponly=True, samesite='lax', path='/')
    return response


@router.post('/password', status_code=204)
def password(request: Request, body: PasswordRequest):
    _local(request)
    config = request.app.state.config
    _, _, token = _professional_context(request, 'view_dashboard')
    if not csrf_is_valid(request, config, token):
        raise APIError('csrf_failed')
    try:
        status, retry = application.change_password_limited(config.database_url,
            hashlib.sha256(token.encode('ascii')).hexdigest(), body.current_password, body.new_password,
            bucket_for_username=lambda username: _bucket(config, 'identifier', username),
            origin_bucket=_origin_bucket(request), origin_limit=config.login_rate_limit,
            origin_window_seconds=config.login_rate_window_seconds)
    except InvalidCredential:
        raise APIError('invalid_request') from None
    except (PersistenceError, PasswordServiceUnavailable):
        raise APIError('service_unavailable') from None
    if status == 'limited':
        raise APIError('rate_limited', headers={'Retry-After': str(retry)})
    if status != 'success':
        return _invalid_login(request)
    response = Response(status_code=204)
    _clear_cookie(response)
    return response
