"""Rotas de autenticacao profissional; tokens nunca sao enviados ao navegador."""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timezone
from dataclasses import dataclass
from uuid import UUID
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, ConfigDict
from starlette.responses import Response as StarletteResponse

from api.config import APIConfig
from api.errors import APIError, error_response
from api.google_oidc import (
    InvalidOIDCResponse,
    OIDCProviderUnavailable,
    authorization_url,
    exchange_code,
)
from stroop.application import auth as auth_application
from stroop.application import local_auth as local_application
from stroop.domain.local_auth import LOCAL_ISSUER
from stroop.domain.auth import AppUser
from stroop.domain.auth import (
    opaque_user_id,
    AuthDatabaseError,
    AuthError,
    BlockedUserError,
    ExpiredIdentityError,
    ForbiddenOperationError,
    RateLimitedError,
    UnregisteredUserError,
)
from stroop.persistence.auth import PersistenceError
from stroop.persistence import web_auth, web_sessions as web_session_persistence


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
PROFESSIONAL_COOKIE = "__Host-stroop_professional"
OIDC_STATE_COOKIE = "__Host-stroop_oidc_state"
STATE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{40,64}$")
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{40,128}$")


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def _reject_query(request: Request) -> None:
    if request.query_params:
        raise APIError("invalid_request")


async def _reject_body(request: Request) -> None:
    if await request.body():
        raise APIError("invalid_request")


def _cookie(request: Request, name: str) -> str | None:
    """Le cookie de credencial precisa ser unico e ter valor ASCII fechado."""
    found: list[str] = []
    for key, value in request.scope.get("headers", []):
        if key.lower() != b"cookie":
            continue
        try:
            header = value.decode("ascii")
        except UnicodeError:
            raise APIError("authentication_required") from None
        for part in header.split(";"):
            item = part.strip()
            cookie_name, separator, cookie_value = item.partition("=")
            if cookie_name.strip() == name:
                if not separator:
                    raise APIError("authentication_required")
                found.append(cookie_value.strip())
    if len(found) > 1:
        raise APIError("authentication_required")
    return found[0] if found else None


def _origin_is_valid(request: Request, config: APIConfig) -> bool:
    values = [
        value for key, value in request.scope.get("headers", [])
        if key.lower() == b"origin"
    ]
    if len(values) != 1:
        return False
    try:
        return hmac.compare_digest(values[0].decode("ascii"), config.public_origin)
    except UnicodeError:
        return False


def _csrf_token(config: APIConfig, session_token: str) -> str:
    digest = hmac.new(
        config.session_secret.encode("utf-8"),
        b"stroop-professional-csrf-v1\0" + session_token.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def csrf_is_valid(request: Request, config: APIConfig, session_token: str) -> bool:
    values = [
        value for key, value in request.scope.get("headers", [])
        if key.lower() == b"x-csrf-token"
    ]
    if len(values) != 1:
        return False
    try:
        supplied = values[0].decode("ascii")
    except UnicodeError:
        return False
    return hmac.compare_digest(supplied, _csrf_token(config, session_token))


def _auth_error(exc: AuthError) -> APIError:
    if isinstance(exc, (AuthDatabaseError,)):
        return APIError("service_unavailable")
    if isinstance(exc, BlockedUserError):
        return APIError("account_blocked")
    if isinstance(exc, ForbiddenOperationError):
        return APIError("permission_denied")
    if isinstance(exc, RateLimitedError):
        return APIError("rate_limited")
    if isinstance(exc, (ExpiredIdentityError, UnregisteredUserError)):
        return APIError("authentication_required")
    return APIError("authentication_required")


def _database_error(exc: PersistenceError) -> APIError:
    return APIError("service_unavailable")


def _professional_context(request: Request, action: str):
    config: APIConfig = request.app.state.config
    token = _cookie(request, PROFESSIONAL_COOKIE)
    if token is None or TOKEN_PATTERN.fullmatch(token) is None:
        raise APIError("authentication_required")
    if config.auth_mode == "local":
        try:
            status, details = local_application.session_context(
                config.database_url, hashlib.sha256(token.encode("ascii")).hexdigest(), action)
        except PersistenceError:
            raise APIError("service_unavailable") from None
        if status != "success":
            raise APIError("permission_denied" if status == "forbidden" else "authentication_required")
        principal, role, expires = details
        request.state.local_session_token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
        request.state.local_session_token = token
        return AppUser(LOCAL_ISSUER, str(principal), None, role, True), LocalSessionView(expires), token
    try:
        session = web_auth.find_professional_session(
            config.database_url, hashlib.sha256(token.encode("ascii")).hexdigest()
        )
    except PersistenceError as exc:
        raise _database_error(exc) from None
    if session is None:
        raise APIError("authentication_required")
    claims = {
        "iss": session.issuer,
        "sub": session.subject,
        "exp": int(session.oidc_expires_at.timestamp()),
    }
    try:
        user = auth_application.authorize(
            config.database_url, claims, action
        )
    except AuthError as exc:
        raise _auth_error(exc) from None
    return user, session, token


@dataclass(frozen=True)
class LocalSessionView:
    expires_at: datetime


def parse_opaque_user_id(value: str) -> tuple[str, str] | None:
    if not 1 <= len(value) <= 512 or re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
        return None
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        issuer, subject = raw.decode("ascii").split("\0", 1)
    except (ValueError, UnicodeError):
        return None
    if issuer == LOCAL_ISSUER:
        try:
            if str(UUID(subject)) != subject:
                return None
        except ValueError:
            return None
        return issuer, subject
    if issuer not in {"https://accounts.google.com", "accounts.google.com"}:
        return None
    if not 1 <= len(subject) <= 255 or any(c.isspace() for c in subject):
        return None
    return issuer, subject


def _professional_rate_limit(request: Request, token: str, operation: str) -> None:
    config: APIConfig = request.app.state.config
    digest = hmac.new(
        config.session_secret.encode("utf-8"),
        b"stroop-professional-rate-v1\0" + token.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    limit = config.professional_read_rate_limit if operation == "read" else config.professional_write_rate_limit
    try:
        allowed, retry_after = web_session_persistence.professional_request_limit(
            config.database_url, digest, operation, limit,
            config.professional_rate_window_seconds,
        )
    except PersistenceError:
        raise APIError("service_unavailable") from None
    if not allowed:
        raise APIError("rate_limited", headers={"Retry-After": str(retry_after)})


def require_professional(request: Request, action: str = "view_dashboard"):
    """Revalida sessao, cadastro, bloqueio e permissao em cada operacao."""
    user, _, _ = _professional_context(request, action)
    return user


def _clear_state(response: StarletteResponse) -> None:
    response.delete_cookie(
        OIDC_STATE_COOKIE, path="/", secure=True, httponly=True, samesite="lax"
    )


def _oidc_error(request: Request, code: str = "invalid_oidc_state") -> JSONResponse:
    response = error_response(code, request.state.request_id)
    _clear_state(response)
    return response


@router.get("/login")
async def login(request: Request):
    if request.app.state.config.auth_mode == "local":
        raise APIError("not_found")
    _reject_query(request)
    await _reject_body(request)
    config: APIConfig = request.app.state.config
    peer = request.client.host if request.client is not None else "unknown"
    remote_hash = hmac.new(
        config.session_secret.encode("utf-8"),
        b"stroop-login-rate-v1\0" + peer.encode("utf-8", errors="replace"),
        hashlib.sha256,
    ).hexdigest()
    try:
        allowed, retry_after = web_auth.count_login_attempt(
            config.database_url,
            remote_hash,
            config.login_rate_limit,
            config.login_rate_window_seconds,
        )
    except PersistenceError:
        return error_response("service_unavailable", request.state.request_id)
    if not allowed:
        limited = error_response("rate_limited", request.state.request_id)
        limited.headers["Retry-After"] = str(retry_after)
        return limited
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    try:
        url = authorization_url(
            config, state=state, nonce=nonce, code_challenge=challenge
        )
    except OIDCProviderUnavailable:
        return error_response("service_unavailable", request.state.request_id)
    try:
        web_auth.create_oidc_transaction(
            config.database_url,
            hashlib.sha256(state.encode("ascii")).hexdigest(),
            nonce,
            verifier,
        )
    except PersistenceError:
        return error_response("service_unavailable", request.state.request_id)
    response = RedirectResponse(url, status_code=303)
    response.set_cookie(
        OIDC_STATE_COOKIE,
        state,
        max_age=600,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/callback")
async def callback(request: Request):
    if request.app.state.config.auth_mode == "local":
        raise APIError("not_found")
    await _reject_body(request)
    config: APIConfig = request.app.state.config
    parameters = request.query_params.multi_items()
    keys = [key for key, _ in parameters]
    # Google also returns authorization metadata. These fields never authorize
    # a user: only the verified ID token supplies identity and permissions.
    metadata = {"scope", "authuser", "prompt", "hd", "iss"}
    if len(keys) != len(set(keys)) or set(keys) - metadata not in (
        {"state", "code"}, {"state", "error"}, {"state", "error", "error_description"}
    ):
        return _oidc_error(request)
    values = dict(parameters)
    if "iss" in values and values["iss"] != "https://accounts.google.com":
        return _oidc_error(request)
    state = values.get("state", "")
    state_cookie = _cookie(request, OIDC_STATE_COOKIE)
    if (
        STATE_PATTERN.fullmatch(state) is None
        or state_cookie is None
        or not hmac.compare_digest(state, state_cookie)
    ):
        return _oidc_error(request)
    try:
        transaction = web_auth.consume_oidc_transaction(
            config.database_url, hashlib.sha256(state.encode("ascii")).hexdigest()
        )
    except PersistenceError:
        response = error_response("service_unavailable", request.state.request_id)
        _clear_state(response)
        return response
    if transaction is None:
        return _oidc_error(request)
    nonce, verifier = transaction
    if "error" in values:
        return _oidc_error(request)
    code = values.get("code", "")
    if not 1 <= len(code) <= 2048 or any(ord(char) < 33 or ord(char) > 126 for char in code):
        return _oidc_error(request)
    try:
        claims = exchange_code(
            config, code=code, code_verifier=verifier, expected_nonce=nonce
        )
    except InvalidOIDCResponse:
        return _oidc_error(request, "authentication_required")
    except OIDCProviderUnavailable:
        response = error_response("service_unavailable", request.state.request_id)
        _clear_state(response)
        return response
    try:
        user = auth_application.authorize(
            config.database_url, claims, "view_dashboard"
        )
    except AuthError as exc:
        if isinstance(exc, UnregisteredUserError):
            response = JSONResponse({
                "error": {"code": "authentication_required", "message": "Solicite cadastro ao responsavel pela pesquisa."},
                "registration_request": {"issuer": claims["iss"], "subject": claims["sub"]},
                "request_id": request.state.request_id,
            }, status_code=401, headers={"Cache-Control": "no-store"})
            _clear_state(response)
            return response
        response = error_response(_auth_error(exc).code, request.state.request_id)
        _clear_state(response)
        return response
    try:
        session_token = secrets.token_urlsafe(32)
        expires_at = web_auth.create_professional_session(
            config.database_url,
            hashlib.sha256(session_token.encode("ascii")).hexdigest(),
            user.issuer,
            user.subject,
            int(claims["exp"]),
        )
    except (PersistenceError, KeyError, TypeError, ValueError):
        response = error_response("service_unavailable", request.state.request_id)
        _clear_state(response)
        return response
    response = RedirectResponse("/", status_code=303)
    _clear_state(response)
    max_age = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    cookie_expiry = expires_at.astimezone(timezone.utc)
    response.set_cookie(
        PROFESSIONAL_COOKIE,
        session_token,
        max_age=max_age,
        expires=cookie_expiry,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/me")
async def me(request: Request):
    _reject_query(request)
    await _reject_body(request)
    config: APIConfig = request.app.state.config
    user, session, token = _professional_context(request, "view_dashboard")
    _professional_rate_limit(request, token, "read")
    return {
        "user_id": opaque_user_id(user.issuer, user.subject),
        "role": user.role,
        "expires_at": session.expires_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "csrf_token": _csrf_token(config, token),
    }


@router.post("/logout", status_code=204)
async def logout(request: Request, body: LogoutRequest):
    del body
    _reject_query(request)
    config: APIConfig = request.app.state.config
    if not _origin_is_valid(request, config):
        raise APIError("csrf_failed")
    token = _cookie(request, PROFESSIONAL_COOKIE)
    if token is None:
        response = Response(status_code=204)
        response.delete_cookie(
            PROFESSIONAL_COOKIE, path="/", secure=True, httponly=True,
            samesite="lax",
        )
        return response
    if TOKEN_PATTERN.fullmatch(token) is None or not csrf_is_valid(request, config, token):
        raise APIError("csrf_failed")
    _professional_rate_limit(request, token, "write")
    try:
        if config.auth_mode == "local":
            from stroop.persistence.local_auth import revoke
            revoke(config.database_url, hashlib.sha256(token.encode("ascii")).hexdigest())
        else:
            web_auth.revoke_professional_session(
                config.database_url, hashlib.sha256(token.encode("ascii")).hexdigest()
            )
    except PersistenceError:
        return error_response("service_unavailable", request.state.request_id)
    response = Response(status_code=204)
    response.delete_cookie(
        PROFESSIONAL_COOKIE, path="/", secure=True, httponly=True,
        samesite="lax",
    )
    return response


__all__ = ["router", "require_professional", "csrf_is_valid"]
