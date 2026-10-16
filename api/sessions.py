"""Rotas de projetos, convites e ciclo operacional de sessao participante."""

from __future__ import annotations

import base64
import binascii
import csv
import hashlib
import hmac
import secrets
from datetime import timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from api.auth import (
    TOKEN_PATTERN, _cookie, _origin_is_valid, _professional_context,
    csrf_is_valid, opaque_user_id, parse_opaque_user_id, require_professional,
    _professional_rate_limit,
)
from api.config import APIConfig
from api.errors import APIError
from api.models import RequestModel
from stroop.application import web_sessions as application
from stroop.persistence.auth import PersistenceError
from stroop.persistence import web_sessions as persistence


router = APIRouter(prefix="/api/v1", tags=["sessions"])
PARTICIPANT_COOKIE = "__Host-stroop_participant"
PARTICIPANT_TOKEN_PATTERN = TOKEN_PATTERN
CONDITIONS_DIR = Path(__file__).resolve().parents[1] / "condicoes"
DISPLAY_COLORS = {
    "green": "#40FF00", "yellow": "#FFF200", "pink": "#FF5CCB",
    "black": "#000000", "red": "#FF0000", "orange": "#FF9000",
    "brown": "#965000", "purple": "#9A24FF", "blue": "#0062FF",
    "gray": "#808080",
}
PROTOCOL_SNAPSHOT = {
    "countdown_segment_ms": 550,
    "practice": {
        "trials": 4, "fixation_ms": 300, "stimulus_window_ms": 2000,
        "blank_interval_ms": 500, "feedback_ms": 500,
        "feedback_after_each_trial": True,
    },
    "main": {
        "trials": 16, "fixation_ms": 300, "stimulus_window_ms": 2500,
        "blank_interval_ms": 950, "trial_ms": 3750, "duration_ms": 60000,
        "feedback_after_each_trial": False,
    },
    "response": {
        "key": "space", "window_start_ms": 300, "end_exclusive": True,
        "first_press_only": True, "ignore_keyboard_repeat": True,
        "require_release_before_next_press": True,
    },
    "interruption": {
        "abort_on_focus_loss": True, "abort_on_hidden": True,
        "abort_on_reload": True, "abort_on_escape": True,
        "resume_running_session": False,
    },
    "practice_repeat_allowed": True,
    "hud": {"live_accuracy": True, "main_timer": True, "progress": True},
    "colors": DISPLAY_COLORS,
}


class CreateProject(RequestModel):
    code: str
    name: str


class SetMember(RequestModel):
    active: bool


class CreateInvitation(RequestModel):
    participant_id: str
    visit: str


class Redeem(RequestModel):
    code: str


class Start(RequestModel):
    app_version: str


class Abort(RequestModel):
    reason: str


class EmptyRequest(RequestModel):
    pass


def _reject_query(request: Request) -> None:
    if request.query_params:
        raise APIError("invalid_request")


def _page(request: Request, scope: str, config: APIConfig) -> tuple[int, int]:
    pairs = request.query_params.multi_items()
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)) or set(keys) - {"limit", "cursor"}:
        raise APIError("invalid_request")
    values = dict(pairs)
    raw_limit = values.get("limit", "25")
    if not raw_limit.isascii() or not raw_limit.isdigit() or len(raw_limit) > 3:
        raise APIError("invalid_request")
    limit = int(raw_limit)
    if not 1 <= limit <= 100:
        raise APIError("invalid_request")
    cursor = values.get("cursor")
    if cursor is None:
        return limit, 0
    if not 1 <= len(cursor) <= 512 or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for c in cursor):
        raise APIError("invalid_request")
    try:
        decoded = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)).decode("ascii")
        raw_offset, signature = decoded.split(".", 1)
        if not raw_offset.isdigit() or len(raw_offset) > 8:
            raise ValueError
        offset = int(raw_offset)
        expected = hmac.new(config.session_secret.encode("utf-8"),
                            b"stroop-page-v1\0" + scope.encode("utf-8") + b"\0" + raw_offset.encode("ascii"),
                            hashlib.sha256).hexdigest()[:32]
        if offset > 10_000_000 or not hmac.compare_digest(signature, expected):
            raise ValueError
        return limit, offset
    except (ValueError, UnicodeError, binascii.Error):
        raise APIError("invalid_request") from None


def _next_cursor(config: APIConfig, scope: str, offset: int) -> str:
    raw_offset = str(offset).encode("ascii")
    signature = hmac.new(config.session_secret.encode("utf-8"),
                         b"stroop-page-v1\0" + scope.encode("utf-8") + b"\0" + raw_offset,
                         hashlib.sha256).hexdigest()[:32].encode("ascii")
    return base64.urlsafe_b64encode(raw_offset + b"." + signature).rstrip(b"=").decode("ascii")


async def _reject_empty_body(request: Request) -> None:
    if await request.body():
        raise APIError("invalid_request")


def _professional_write(request: Request, action: str):
    user, _, token = _professional_context(request, action)
    config: APIConfig = request.app.state.config
    if not _origin_is_valid(request, config) or not csrf_is_valid(request, config, token):
        raise APIError("csrf_failed")
    _professional_rate_limit(request, token, "write")
    return user


def _professional_read(request: Request, action: str = "view_dashboard"):
    user, _, token = _professional_context(request, action)
    _professional_rate_limit(request, token, "read")
    return user


def _participant(request: Request, *, count_read: bool = True) -> tuple[str, str]:
    token = _cookie(request, PARTICIPANT_COOKIE)
    if token is None or PARTICIPANT_TOKEN_PATTERN.fullmatch(token) is None:
        raise APIError("authentication_required")
    if count_read:
        _participant_rate_limit(request, token, 'read')
    return token, hashlib.sha256(token.encode("ascii")).hexdigest()


def _participant_rate_limit(request: Request, token: str, operation: str) -> None:
    config: APIConfig = request.app.state.config
    digest = hmac.new(config.session_secret.encode('utf-8'),
                      b'stroop-participant-rate-v1\0' + token.encode('ascii'),
                      hashlib.sha256).hexdigest()
    limit = config.participant_read_rate_limit if operation == 'read' else config.participant_write_rate_limit
    try:
        allowed, retry_after = persistence.participant_request_limit(
            config.database_url, digest, operation, limit, config.participant_rate_window_seconds,
        )
    except PersistenceError:
        raise _persistence_error() from None
    if not allowed:
        raise APIError('rate_limited', headers={'Retry-After': str(retry_after)})


def _participant_csrf(config: APIConfig, token: str) -> str:
    digest = hmac.new(
        config.session_secret.encode("utf-8"),
        b"stroop-participant-csrf-v1\0" + token.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _participant_write(request: Request) -> tuple[str, str]:
    token, token_hash = _participant(request, count_read=False)
    config: APIConfig = request.app.state.config
    supplied = request.headers.getlist("x-csrf-token")
    try:
        valid_csrf = len(supplied) == 1 and hmac.compare_digest(
            supplied[0].encode('ascii'), _participant_csrf(config, token).encode('ascii')
        )
    except UnicodeError:
        valid_csrf = False
    if not _origin_is_valid(request, config) or not valid_csrf:
        raise APIError("csrf_failed")
    _participant_rate_limit(request, token, 'write')
    return token, token_hash


def _persistence_error() -> APIError:
    return APIError("service_unavailable")


def _serialize_time(value) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_conditions(kind: str) -> list[dict]:
    filename = "pratica_stroop_go_nogo_ptbr.csv" if kind == "practice" else "bloco_principal_stroop_go_nogo_ptbr.csv"
    with (CONDITIONS_DIR / filename).open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    return [
        {
            "condition_id": int(row["trial_number"]),
            "word": row["word"],
            "ink_color": row["ink_color"],
            "ink_color_display": DISPLAY_COLORS[row["ink_color"]],
            "condition": row["condition"],
            "correct_response": row["correct_response"] or None,
        }
        for row in rows
    ]


@router.get("/projects")
async def list_projects(request: Request):
    await _reject_empty_body(request)
    user = _professional_read(request)
    config: APIConfig = request.app.state.config
    scope = f"projects:{user.issuer}:{user.subject}:{user.role}"
    limit, offset = _page(request, scope, config)
    try:
        projects = application.projects(config.database_url, user, limit + 1, offset)
    except PersistenceError:
        raise _persistence_error() from None
    has_more = len(projects) > limit
    return {"items": projects[:limit],
            "next_cursor": _next_cursor(config, scope, offset + limit) if has_more else None}


@router.post("/projects", status_code=201)
async def create_project(request: Request, body: CreateProject):
    _reject_query(request)
    actor = _professional_write(request, "manage_projects")
    project_id = uuid4()
    try:
        created_at = application.create_project(request.app.state.config.database_url,
                                                 project_id, body.code, body.name, actor)
    except application.InvalidDataError:
        raise APIError("invalid_request") from None
    except persistence.ConflictError:
        raise APIError("duplicate_project") from None
    except PersistenceError:
        raise _persistence_error() from None
    return {"id": project_id, "code": body.code.strip(), "name": body.name.strip(),
            "active": True, "created_at": _serialize_time(created_at)}


@router.get("/projects/{project_id}/members")
async def list_members(project_id: UUID, request: Request):
    await _reject_empty_body(request)
    actor = _professional_read(request, "manage_project_members")
    config: APIConfig = request.app.state.config
    scope = f"members:{project_id}:{actor.issuer}:{actor.subject}"
    limit, offset = _page(request, scope, config)
    try:
        rows = application.members(config.database_url, project_id, limit + 1, offset)
    except PersistenceError:
        raise _persistence_error() from None
    if rows is None:
        raise APIError("not_found")
    has_more = len(rows) > limit
    return {"items": [{"user_id": opaque_user_id(row["issuer"], row["subject"]), "active": row["active"]} for row in rows[:limit]],
            "next_cursor": _next_cursor(config, scope, offset + limit) if has_more else None}


@router.put("/projects/{project_id}/members/{user_id}")
async def set_member(project_id: UUID, user_id: str, request: Request, body: SetMember):
    _reject_query(request)
    actor = _professional_write(request, "manage_project_members")
    identity = parse_opaque_user_id(user_id)
    if identity is None:
        raise APIError("invalid_request")
    try:
        result = application.set_member(request.app.state.config.database_url,
                                        project_id, identity[0], identity[1], body.active, actor)
    except PersistenceError:
        raise _persistence_error() from None
    if not result:
        raise APIError("not_found")
    return {"user_id": user_id, "active": body.active}


@router.post("/projects/{project_id}/invitations", status_code=201)
async def create_invitation(project_id: UUID, request: Request, body: CreateInvitation):
    _reject_query(request)
    actor = _professional_write(request, "view_dashboard")
    try:
        access = application.project_invitation_access(
            request.app.state.config.database_url, project_id, actor
        )
    except PersistenceError:
        raise _persistence_error() from None
    if access == "not_found":
        raise APIError("not_found")
    if access == "forbidden":
        raise APIError("permission_denied")
    code = secrets.token_urlsafe(32)
    invitation_id, session_id = uuid4(), uuid4()
    try:
        created = application.create_invitation(
            request.app.state.config.database_url, invitation_id, session_id,
            project_id, hashlib.sha256(code.encode("ascii")).hexdigest(),
            body.participant_id, body.visit, actor,
        )
    except application.InvalidDataError:
        raise APIError("invalid_request") from None
    except PersistenceError:
        raise _persistence_error() from None
    if not created:
        raise APIError("not_found")
    return {"invitation_id": invitation_id, "session_id": session_id,
            "code": code, "expires_at": _serialize_time(created), "state": "issued"}


@router.post("/projects/{project_id}/invitations/{invitation_id}/revoke", status_code=204)
async def revoke_invitation(project_id: UUID, invitation_id: UUID, request: Request,
                            body: EmptyRequest):
    _reject_query(request)
    actor = _professional_write(request, "view_dashboard")
    try:
        access = application.project_invitation_access(
            request.app.state.config.database_url, project_id, actor
        )
    except PersistenceError:
        raise _persistence_error() from None
    if access == "not_found":
        raise APIError("not_found")
    if access == "forbidden":
        raise APIError("permission_denied")
    try:
        revoked = application.revoke_invitation(request.app.state.config.database_url,
                                                project_id, invitation_id, actor)
    except PersistenceError:
        raise _persistence_error() from None
    if not revoked:
        raise APIError("not_found")
    return Response(status_code=204)


@router.post("/participant/redeem", status_code=201)
async def redeem(request: Request, body: Redeem):
    _reject_query(request)
    config: APIConfig = request.app.state.config
    if not _origin_is_valid(request, config):
        raise APIError("csrf_failed")
    peer = request.client.host if request.client is not None else "unknown"
    remote_hash = hmac.new(config.session_secret.encode("utf-8"),
                           b"stroop-redeem-rate-v1\0" + peer.encode("utf-8"),
                           hashlib.sha256).hexdigest()
    try:
        allowed, retry_after = application.redeem_limit(
            config.database_url, remote_hash, config.redeem_rate_limit,
            config.redeem_rate_window_seconds,
        )
    except PersistenceError:
        raise _persistence_error() from None
    if not allowed:
        raise APIError("rate_limited", headers={"Retry-After": str(retry_after)})
    if not body.code.isascii() or not 32 <= len(body.code) <= 128:
        raise APIError("not_found")
    token = secrets.token_urlsafe(32)
    try:
        result = application.redeem(config.database_url,
                                    hashlib.sha256(body.code.encode("ascii")).hexdigest(),
                                    hashlib.sha256(token.encode("ascii")).hexdigest())
    except application.ExpiredError:
        raise APIError("invitation_expired") from None
    except application.ConflictError:
        raise APIError("invitation_used") from None
    except application.MissingError:
        raise APIError("not_found") from None
    except PersistenceError:
        raise _persistence_error() from None
    response = JSONResponse({
        "session_id": str(result["session_id"]), "state": result["state"],
        "activated_at": _serialize_time(result["activated_at"]),
        "expires_at": _serialize_time(result["expires_at"]),
        "csrf_token": _participant_csrf(config, token),
    }, status_code=201)
    response.set_cookie(PARTICIPANT_COOKIE, token, max_age=1800, secure=True,
                         httponly=True, samesite="lax", path="/")
    return response


@router.get("/participant/session")
async def participant_session(request: Request):
    _reject_query(request)
    await _reject_empty_body(request)
    _, token_hash = _participant(request)
    try:
        session = application.participant_session(request.app.state.config.database_url,
                                                  token_hash)
    except application.ExpiredError:
        raise APIError("session_expired") from None
    except application.UnknownCredentialError:
        raise APIError("authentication_required") from None
    except application.MissingError:
        raise APIError("not_found") from None
    except PersistenceError:
        raise _persistence_error() from None
    result = {"session_id": session.session_id, "state": session.state,
              "activated_at": _serialize_time(session.activated_at),
              "expires_at": _serialize_time(session.expires_at), "can_resume": False}
    if session.state == 'completed':
        return session.receipt
    if session.state == "preparing":
        conditions = {row["condition_id"]: row for row in _load_conditions("main")}
        result.update({
            "csrf_token": _participant_csrf(request.app.state.config,
                                             _cookie(request, PARTICIPANT_COOKIE)),
            "protocol_id": "stroop_go_nogo_ptbr/0.2.2-web.1",
            "test_code": "stroop_go_nogo_ptbr", "test_version": "0.2.2-web.1",
            "platform": "web",
            "protocol": PROTOCOL_SNAPSHOT,
            "practice_conditions": _load_conditions("practice"),
            "main_conditions": [
                {"trial_number": index, **conditions[condition_id]}
                for index, condition_id in enumerate(session.order, 1)
            ],
        })
    elif session.state == "running":
        result["csrf_token"] = _participant_csrf(request.app.state.config,
                                                  _cookie(request, PARTICIPANT_COOKIE))
    elif session.state == "aborted":
        raise APIError("state_conflict")
    return result


@router.post("/participant/start")
async def start(request: Request, body: Start):
    _reject_query(request)
    _, token_hash = _participant_write(request)
    try:
        result = application.start(request.app.state.config.database_url,
                                   token_hash, body.app_version)
    except application.InvalidDataError:
        raise APIError("invalid_request") from None
    except application.ExpiredError:
        raise APIError("session_expired") from None
    except application.ConflictError:
        raise APIError("state_conflict") from None
    except application.UnknownCredentialError:
        raise APIError("authentication_required") from None
    except application.MissingError:
        raise APIError("not_found") from None
    except PersistenceError:
        raise _persistence_error() from None
    return {**result, "started_at": _serialize_time(result["started_at"]),
            "expires_at": _serialize_time(result["expires_at"])}


@router.post("/participant/abort")
async def abort(request: Request, body: Abort):
    _reject_query(request)
    _, token_hash = _participant_write(request)
    try:
        result = application.abort(request.app.state.config.database_url,
                                   token_hash, body.reason)
    except application.InvalidDataError:
        raise APIError("invalid_request") from None
    except application.ExpiredError:
        raise APIError("session_expired") from None
    except application.ConflictError:
        raise APIError("state_conflict") from None
    except application.UnknownCredentialError:
        raise APIError("authentication_required") from None
    except application.MissingError:
        raise APIError("not_found") from None
    except PersistenceError:
        raise _persistence_error() from None
    return result
