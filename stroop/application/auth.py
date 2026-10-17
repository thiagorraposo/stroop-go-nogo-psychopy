"""Casos de uso e erros publicos de autenticacao/autorizacao."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from stroop.domain.auth import (
    AppUser,
    AuthDatabaseError,
    AuthError,
    BlockedUserError,
    DENIAL_LIMIT,
    ExpiredIdentityError,
    ForbiddenOperationError,
    IMPORT_ERROR_CODES,
    IMPORT_STATUSES,
    Identity,
    InvalidIdentityError,
    LastAdminProtectionError,
    PERMISSIONS,
    RateLimitedError,
    ROLES,
    SHA256_HEX,
    UnregisteredUserError,
    ensure_not_expired,
    parse_identity,
)
from stroop.persistence import auth as auth_persistence
from stroop.persistence.auth import DuplicateUserError, PersistenceError


def _require_database(database_url: str) -> None:
    if not database_url:
        raise AuthDatabaseError("AUTH_DATABASE_URL nao configurada.")


def authorize(
    database_url: str,
    claims: Mapping[str, Any],
    action: str,
    *,
    now: datetime | None = None,
) -> AppUser:
    """Revalida expiracao, cadastro, bloqueio e perfil para uma operacao."""
    if action not in PERMISSIONS:
        raise ValueError("Operacao protegida desconhecida.")
    _require_database(database_url)
    identity = parse_identity(claims)
    try:
        ensure_not_expired(identity, now)
    except ExpiredIdentityError:
        try:
            auth_persistence.record_expired_denial(database_url, identity, action)
        except PersistenceError:
            pass
        raise

    try:
        result, user = auth_persistence.authorize_identity(
            database_url, identity, action, PERMISSIONS[action], DENIAL_LIMIT
        )
    except PersistenceError:
        raise AuthDatabaseError("Falha ao verificar autorizacao.") from None

    if result == "rate_limited":
        raise RateLimitedError("Acesso temporariamente limitado.")
    if result == "unregistered":
        raise UnregisteredUserError("Usuario nao cadastrado.")
    if result == "blocked":
        raise BlockedUserError("Usuario bloqueado.")
    if result == "forbidden":
        raise ForbiddenOperationError("Operacao nao autorizada.")
    if result == "found" and user is not None:
        return user
    raise AuthDatabaseError("Falha ao verificar autorizacao.")


def record_operation(
    database_url: str, user: AppUser, action: str, outcome: str
) -> None:
    try:
        auth_persistence.record_operation(database_url, user, action, outcome)
    except PersistenceError:
        raise AuthDatabaseError("Falha ao registrar auditoria.") from None


def record_import_result(
    database_url: str,
    request_id: str,
    content_sha256: str,
    status: str,
    error_code: str | None,
) -> None:
    """Persiste somente hash, resultado e erro de vocabulario controlado."""
    if (
        status not in IMPORT_STATUSES
        or SHA256_HEX.fullmatch(content_sha256) is None
        or (status == "importado" and error_code is not None)
        or (status == "rejeitado" and error_code not in IMPORT_ERROR_CODES)
    ):
        raise AuthDatabaseError("Resultado de importacao invalido.")
    try:
        auth_persistence.record_import_result(
            database_url, request_id, content_sha256, status, error_code
        )
    except PersistenceError:
        raise AuthDatabaseError("Falha ao registrar resultado de importacao.") from None


def list_users(database_url: str) -> list[AppUser]:
    try:
        return auth_persistence.list_users(database_url)
    except PersistenceError:
        raise AuthDatabaseError("Falha ao consultar usuarios.") from None


def list_users_page(database_url: str, limit: int, offset: int) -> list[AppUser]:
    try:
        return auth_persistence.list_users_page(database_url, limit, offset)
    except PersistenceError:
        raise AuthDatabaseError("Falha ao consultar usuarios.") from None


def _management_identity(issuer: str, subject: str) -> Identity:
    return parse_identity({"iss": issuer, "sub": subject, "exp": 2**62})


def _validate_user_fields(
    issuer: str, subject: str, role: str, email: str | None
) -> Identity:
    identity = _management_identity(issuer, subject)
    if role not in ROLES:
        raise InvalidIdentityError("Perfil invalido.")
    if email is not None and not 3 <= len(email) <= 320:
        raise InvalidIdentityError("E-mail auxiliar invalido.")
    return identity


def create_user(
    database_url: str,
    issuer: str,
    subject: str,
    role: str,
    email: str | None,
    actor: AppUser,
) -> None:
    identity = _validate_user_fields(issuer, subject, role, email)
    try:
        auth_persistence.create_user(database_url, identity, role, email, actor)
    except DuplicateUserError:
        raise InvalidIdentityError("Usuario ja cadastrado.") from None
    except PersistenceError:
        raise AuthDatabaseError("Falha ao cadastrar usuario.") from None


def update_user(
    database_url: str,
    issuer: str,
    subject: str,
    *,
    role: str,
    active: bool,
    email: str | None,
    actor: AppUser,
) -> None:
    identity = _validate_user_fields(issuer, subject, role, email)
    try:
        result = auth_persistence.update_user(
            database_url,
            identity,
            role=role,
            active=active,
            email=email,
            actor=actor,
        )
    except PersistenceError:
        raise AuthDatabaseError("Falha ao atualizar usuario.") from None
    if result == "last_admin":
        raise LastAdminProtectionError(
            "A ultima conta administrativa ativa deve ser preservada."
        )
    if result == "missing":
        raise InvalidIdentityError("Usuario nao cadastrado.")


def bootstrap_admin(
    database_url: str,
    issuer: str,
    subject: str,
    email: str | None = None,
) -> None:
    identity = _management_identity(issuer, subject)
    if email is not None and not 3 <= len(email) <= 320:
        raise InvalidIdentityError("E-mail auxiliar invalido.")
    try:
        created = auth_persistence.bootstrap_admin(database_url, identity, email)
    except PersistenceError:
        raise AuthDatabaseError("Falha no bootstrap administrativo.") from None
    if not created:
        raise InvalidIdentityError("Bootstrap permitido somente sem usuarios.")


def recover_admin(database_url: str, issuer: str, subject: str) -> None:
    identity = _management_identity(issuer, subject)
    try:
        recovered = auth_persistence.recover_admin(database_url, identity)
    except PersistenceError:
        raise AuthDatabaseError("Falha na recuperacao administrativa.") from None
    if not recovered:
        raise InvalidIdentityError("Usuario nao cadastrado.")


__all__ = [
    "AppUser",
    "AuthDatabaseError",
    "AuthError",
    "BlockedUserError",
    "ExpiredIdentityError",
    "ForbiddenOperationError",
    "Identity",
    "InvalidIdentityError",
    "RateLimitedError",
    "UnregisteredUserError",
    "authorize",
    "bootstrap_admin",
    "create_user",
    "ensure_not_expired",
    "list_users",
    "list_users_page",
    "LastAdminProtectionError",
    "parse_identity",
    "record_import_result",
    "record_operation",
    "recover_admin",
    "update_user",
    "ROLES",
    "PERMISSIONS",
    "DENIAL_LIMIT",
]
