"""Validacao e casos de uso do fluxo WEB de convites e sessoes."""

from __future__ import annotations

import re
import hashlib
import secrets
from uuid import UUID

from stroop.domain.auth import AppUser
from stroop.persistence import web_sessions as persistence
from stroop.persistence.auth import PersistenceError


LABEL = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
PROJECT_CODE = LABEL
APP_VERSION = re.compile(r"^[A-Za-z0-9_.+-]{1,64}$")
ABORT_REASONS = frozenset({
    "focus_lost", "visibility_hidden", "escape", "reload", "page_closed",
    "timing_invalid", "user_cancelled",
})


class InvalidDataError(ValueError):
    """Entrada que viola o contrato da sessao WEB."""


def _label(value: str) -> str:
    normalized = value.strip() if isinstance(value, str) else ""
    if LABEL.fullmatch(normalized) is None:
        raise InvalidDataError
    return normalized


def projects(database_url: str, actor: AppUser, limit: int = 25, offset: int = 0):
    return persistence.list_projects(
        database_url, actor.issuer, actor.subject,
        all_projects=actor.role == "administracao",
        limit=limit, offset=offset,
    )


def create_project(database_url: str, project_id: UUID, code: str, name: str,
                   actor: AppUser):
    code = _label(code)
    name = name.strip() if isinstance(name, str) else ""
    if not 1 <= len(name) <= 120 or any(ord(char) < 32 for char in name):
        raise InvalidDataError
    return persistence.create_project(database_url, project_id, code, name,
                                      actor.issuer, actor.subject)


def members(database_url: str, project_id: UUID, limit: int = 25, offset: int = 0):
    return persistence.list_members(database_url, project_id, limit, offset)


def project_invitation_access(database_url: str, project_id: UUID, actor: AppUser):
    return persistence.project_invitation_access(database_url, project_id,
                                                 actor.issuer, actor.subject)


def set_member(database_url: str, project_id: UUID, issuer: str, subject: str,
               active: bool, actor: AppUser) -> bool:
    if not isinstance(active, bool):
        raise InvalidDataError
    return persistence.set_member(database_url, project_id, issuer, subject, active,
                                  actor.issuer, actor.subject)


def create_invitation(database_url: str, invitation_id: UUID, session_id: UUID,
                      project_id: UUID, code_hash: str, participant_id: str,
                      visit: str, actor: AppUser):
    return persistence.create_invitation(
        database_url, invitation_id, session_id, project_id, code_hash,
        _label(participant_id), _label(visit), actor.issuer, actor.subject,
    )


def revoke_invitation(database_url: str, project_id: UUID, invitation_id: UUID,
                      actor: AppUser) -> bool:
    return persistence.revoke_invitation(
        database_url, project_id, invitation_id, actor.issuer, actor.subject
    )


def _ordered_conditions() -> tuple[int, ...]:
    import secrets
    values = list(range(1, 17))
    secrets.SystemRandom().shuffle(values)
    return tuple(values)


def redeem(database_url: str, code_hash: str, token_hash: str):
    return persistence.redeem(database_url, code_hash, token_hash,
                               _ordered_conditions())


def participant_session(database_url: str, token_hash: str):
    return persistence.get_participant_session(database_url, token_hash)


def start(database_url: str, token_hash: str, app_version: str):
    normalized = app_version.strip() if isinstance(app_version, str) else ""
    if APP_VERSION.fullmatch(normalized) is None:
        raise InvalidDataError
    return persistence.start_participant_session(database_url, token_hash, normalized)


def abort(database_url: str, token_hash: str, reason: str):
    if reason not in ABORT_REASONS:
        raise InvalidDataError
    return persistence.abort_participant_session(database_url, token_hash, reason)


def redeem_limit(database_url: str, remote_hash: str, limit: int, window_seconds: int):
    return persistence.redeem_limit(database_url, remote_hash, limit, window_seconds)


__all__ = ["InvalidDataError", "ConflictError", "ExpiredError", "MissingError",
           "PersistenceError", "projects", "create_project", "members", "set_member",
           "create_invitation", "revoke_invitation", "redeem", "participant_session",
           "start", "abort", "redeem_limit", "logout"]


ConflictError = persistence.ConflictError
ExpiredError = persistence.ExpiredError
MissingError = persistence.MissingError
UnknownCredentialError = persistence.UnknownCredentialError


def logout(database_url: str, token_hash: str) -> None:
    replacement_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    persistence.logout_participant_session(database_url, token_hash, replacement_hash)
