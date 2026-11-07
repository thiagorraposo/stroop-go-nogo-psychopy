"""Administracao profissional de contas e operacoes de projeto existentes."""
from __future__ import annotations

from fastapi import APIRouter, Request

from api.auth import opaque_user_id, parse_opaque_user_id
from api.errors import APIError
from api.models import RequestModel
from api.sessions import _next_cursor, _page, _professional_read, _professional_write, _reject_empty_body, _reject_query
from stroop.application import auth as application
from stroop.application import web_administration as management
from stroop.domain.auth import AuthError, ForbiddenOperationError, InvalidIdentityError, LastAdminProtectionError


router = APIRouter(prefix="/api/v1/admin", tags=["administration"])


class CreateUser(RequestModel):
    issuer: str
    subject: str
    role: str
    email: str | None = None


class UpdateUser(RequestModel):
    role: str
    active: bool
    email: str | None


def _database_error(error: AuthError) -> APIError:
    if isinstance(error, application.AuthDatabaseError):
        return APIError("service_unavailable")
    if isinstance(error, LastAdminProtectionError):
        return APIError("state_conflict")
    if isinstance(error, ForbiddenOperationError):
        return APIError("forbidden")
    if isinstance(error, InvalidIdentityError):
        return APIError("invalid_request")
    return APIError("service_unavailable")


def _user_row(user):
    return {"user_id": opaque_user_id(user.issuer, user.subject), "issuer": user.issuer,
            "subject": user.subject, "email": user.email, "role": user.role, "active": user.active}


@router.get("/users")
async def list_users(request: Request):
    await _reject_empty_body(request)
    actor = _professional_read(request, "manage_users")
    config = request.app.state.config
    scope = f"admin-users:{actor.issuer}:{actor.subject}"
    limit, offset = _page(request, scope, config)
    try:
        users = application.list_users_page(config.database_url, limit + 1, offset)
    except AuthError as exc:
        raise _database_error(exc) from None
    more = len(users) > limit
    def row(user):
        if config.auth_mode == "local":
            return {key: value for key, value in _user_row(user).items() if key in {"user_id", "role", "active"}}
        return _user_row(user)
    return {"items": [row(user) for user in users[:limit]],
            "next_cursor": _next_cursor(config, scope, offset + limit) if more else None}


@router.post("/users", status_code=201)
async def create_user(request: Request, body: CreateUser):
    _reject_query(request)
    actor = _professional_write(request, "manage_users")
    if request.app.state.config.auth_mode == "local":
        raise APIError("permission_denied")
    try:
        management.create_user(request.app.state.config.database_url, body.issuer, body.subject,
                                body.role, body.email, actor)
    except AuthError as exc:
        try:
            application.record_operation(request.app.state.config.database_url, actor, "manage_users", "failure")
        except AuthError:
            raise APIError("service_unavailable") from None
        raise _database_error(exc) from None
    user = application.AppUser(body.issuer, body.subject, body.email, body.role, True)
    return _user_row(user)


@router.put("/users/{user_id}")
async def update_user(user_id: str, request: Request, body: UpdateUser):
    _reject_query(request)
    actor = _professional_write(request, "manage_users")
    if request.app.state.config.auth_mode == "local":
        raise APIError("not_found")
    identity = parse_opaque_user_id(user_id)
    if identity is None:
        raise APIError("invalid_request")
    try:
        management.update_user(request.app.state.config.database_url, identity[0], identity[1],
                                role=body.role, active=body.active, email=body.email, actor=actor)
    except AuthError as exc:
        try:
            application.record_operation(request.app.state.config.database_url, actor, "manage_users", "failure")
        except AuthError:
            raise APIError("service_unavailable") from None
        raise _database_error(exc) from None
    return {"user_id": user_id, "role": body.role, "active": body.active, "email": body.email}


__all__ = ["router"]


class LocalUserUpdate(RequestModel):
    role: str
    active: bool


class RevokeSessionsRequest(RequestModel):
    pass


@router.patch('/users/{user_id}')
async def update_local_user(user_id: str, request: Request, body: LocalUserUpdate):
    _reject_query(request)
    actor = _professional_write(request, 'manage_users')
    config = request.app.state.config
    from stroop.domain.local_auth import LOCAL_ISSUER
    identity = parse_opaque_user_id(user_id)
    if config.auth_mode != 'local' or identity is None:
        raise APIError('not_found')
    # Recursos historicos continuam no catalogo; nenhuma reescrita de identidade/email.
    from stroop.persistence.local_management import user_email
    from stroop.persistence.auth import PersistenceError
    try:
        email = user_email(config.database_url, *identity)
    except PersistenceError:
        raise APIError('service_unavailable') from None
    if email is None:
        raise APIError('not_found')
    try:
        management.update_user(config.database_url, *identity, role=body.role,
                               active=body.active, email=email[0], actor=actor)
    except AuthError as exc:
        raise _database_error(exc) from None
    return {'user_id': user_id, 'role': body.role, 'active': body.active}


@router.post('/users/{user_id}/sessions/revoke', status_code=204)
async def revoke_local_sessions(user_id: str, request: Request, body: RevokeSessionsRequest):
    _reject_query(request)
    actor = _professional_write(request, 'manage_users')
    config = request.app.state.config
    from stroop.domain.local_auth import LOCAL_ISSUER
    from stroop.persistence.local_management import revoke_sessions
    from stroop.persistence.auth import PersistenceError
    from fastapi.responses import Response
    from api.auth import PROFESSIONAL_COOKIE
    identity = parse_opaque_user_id(user_id)
    if config.auth_mode != 'local' or identity is None or identity[0] != LOCAL_ISSUER:
        raise APIError('not_found')
    try:
        status = revoke_sessions(config.database_url, actor, identity[1])
    except PersistenceError:
        raise APIError('service_unavailable') from None
    if status != 'success':
        raise APIError('permission_denied' if status == 'forbidden' else 'not_found')
    response = Response(status_code=204)
    if identity == (actor.issuer, actor.subject):
        # Revogacao propria nao pode renovar atividade nem cookie.
        request.state.local_session_token_hash = None
        response.delete_cookie(PROFESSIONAL_COOKIE, path='/', secure=True, httponly=True, samesite='lax')
    return response
