"""Administracao profissional de contas e operacoes de projeto existentes."""
from __future__ import annotations

from fastapi import APIRouter, Request

from api.auth import opaque_user_id, parse_opaque_user_id
from api.errors import APIError
from api.models import RequestModel
from api.sessions import _next_cursor, _page, _professional_read, _professional_write, _reject_empty_body, _reject_query
from stroop.application import auth as application
from stroop.domain.auth import AuthError, InvalidIdentityError, LastAdminProtectionError


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
    return {"items": [_user_row(user) for user in users[:limit]],
            "next_cursor": _next_cursor(config, scope, offset + limit) if more else None}


@router.post("/users", status_code=201)
async def create_user(request: Request, body: CreateUser):
    _reject_query(request)
    actor = _professional_write(request, "manage_users")
    try:
        application.create_user(request.app.state.config.database_url, body.issuer, body.subject,
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
    identity = parse_opaque_user_id(user_id)
    if identity is None:
        raise APIError("invalid_request")
    try:
        application.update_user(request.app.state.config.database_url, identity[0], identity[1],
                                role=body.role, active=body.active, email=body.email, actor=actor)
    except AuthError as exc:
        try:
            application.record_operation(request.app.state.config.database_url, actor, "manage_users", "failure")
        except AuthError:
            raise APIError("service_unavailable") from None
        raise _database_error(exc) from None
    return {"user_id": user_id, "role": body.role, "active": body.active, "email": body.email}


__all__ = ["router"]
