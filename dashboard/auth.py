"""Autorizacao OIDC Google e perfis persistidos no PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Mapping
from uuid import uuid4

import psycopg


GOOGLE_ISSUERS = frozenset(
    {"https://accounts.google.com", "accounts.google.com"}
)
ROLES = ("consulta", "importacao", "administracao")
PERMISSIONS = {
    "view_dashboard": frozenset(ROLES),
    "export_dashboard": frozenset(ROLES),
    "import_csv": frozenset({"importacao", "administracao"}),
    "manage_users": frozenset({"administracao"}),
}
DENIAL_LIMIT = 5
DENIAL_WINDOW_MINUTES = 15
IMPORT_STATUSES = frozenset({"importado", "rejeitado"})
IMPORT_ERROR_CODES = frozenset(
    {
        "invalid_envelope",
        "duplicate_assessment",
        "validation_or_service_failure",
    }
)
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


class AuthError(Exception):
    """Erro seguro de autenticacao, autorizacao ou configuracao."""


class InvalidIdentityError(AuthError):
    """Claims obrigatorias ausentes ou invalidas."""


class ExpiredIdentityError(AuthError):
    """Token OIDC expirado."""


class UnregisteredUserError(AuthError):
    """Identidade valida, mas nao cadastrada localmente."""


class BlockedUserError(AuthError):
    """Conta local bloqueada."""


class ForbiddenOperationError(AuthError):
    """Perfil sem permissao para a operacao."""


class RateLimitedError(AuthError):
    """Muitas recusas locais recentes para a identidade."""


class AuthDatabaseError(AuthError):
    """Falha segura ao consultar ou alterar a autorizacao."""


@dataclass(frozen=True)
class Identity:
    issuer: str
    subject: str
    expires_at: int
    email: str | None = None


@dataclass(frozen=True)
class AppUser:
    issuer: str
    subject: str
    email: str | None
    role: str
    active: bool


def parse_identity(claims: Mapping[str, Any]) -> Identity:
    """Extrai somente claims necessarias e auxiliares do ID token validado."""
    issuer = claims.get("iss")
    subject = claims.get("sub")
    expiration = claims.get("exp")
    if issuer not in GOOGLE_ISSUERS:
        raise InvalidIdentityError("Identidade OIDC invalida.")
    if (
        not isinstance(subject, str)
        or not 1 <= len(subject) <= 255
        or not subject.isascii()
        or subject.strip() != subject
        or any(character.isspace() for character in subject)
    ):
        raise InvalidIdentityError("Identidade OIDC invalida.")
    if isinstance(expiration, bool) or not isinstance(expiration, int):
        raise InvalidIdentityError("Identidade OIDC invalida.")
    expires_at = expiration
    email = claims.get("email")
    if not isinstance(email, str) or not 3 <= len(email) <= 320:
        email = None
    return Identity(issuer, subject, expires_at, email)


def ensure_not_expired(identity: Identity, now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    if identity.expires_at <= int(current.timestamp()):
        raise ExpiredIdentityError("Sessao expirada.")


def _audit(
    connection: psycopg.Connection,
    action: str,
    outcome: str,
    identity: Identity | AppUser | None,
) -> None:
    connection.execute(
        """
        INSERT INTO auth_audit_events
            (issuer, subject, action, outcome, request_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            identity.issuer if identity else None,
            identity.subject if identity else None,
            action,
            outcome,
            uuid4(),
        ),
    )


def _recent_denials(connection: psycopg.Connection, identity: Identity) -> int:
    return int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM auth_audit_events
            WHERE issuer = %s
              AND subject = %s
              AND outcome IN (
                  'denied_unregistered', 'denied_blocked', 'denied_forbidden',
                  'rate_limited'
              )
              AND occurred_at >= CURRENT_TIMESTAMP - (%s * INTERVAL '1 minute')
            """,
            (identity.issuer, identity.subject, DENIAL_WINDOW_MINUTES),
        ).fetchone()[0]
    )


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
    if not database_url:
        raise AuthDatabaseError("AUTH_DATABASE_URL nao configurada.")
    identity = parse_identity(claims)
    try:
        ensure_not_expired(identity, now)
    except ExpiredIdentityError:
        try:
            with psycopg.connect(database_url) as connection:
                _audit(connection, action, "denied_expired", identity)
        except psycopg.Error:
            pass
        raise

    try:
        with psycopg.connect(database_url) as connection:
            denial: AuthError | None = None
            if _recent_denials(connection, identity) >= DENIAL_LIMIT:
                _audit(connection, action, "rate_limited", identity)
                denial = RateLimitedError("Acesso temporariamente limitado.")
                user = None
            else:
                row = connection.execute(
                    """
                    SELECT issuer, subject, email, role, active
                    FROM app_users
                    WHERE issuer = %s AND subject = %s
                    """,
                    (identity.issuer, identity.subject),
                ).fetchone()
                if row is None:
                    _audit(connection, action, "denied_unregistered", identity)
                    denial = UnregisteredUserError("Usuario nao cadastrado.")
                    user = None
                else:
                    user = AppUser(*row)
                    if not user.active:
                        _audit(connection, action, "denied_blocked", identity)
                        denial = BlockedUserError("Usuario bloqueado.")
                    elif user.role not in PERMISSIONS[action]:
                        _audit(connection, action, "denied_forbidden", identity)
                        denial = ForbiddenOperationError("Operacao nao autorizada.")
                    else:
                        _audit(connection, action, "allowed", identity)
        if denial is not None:
            raise denial
        if user is None:
            raise AuthDatabaseError("Falha ao verificar autorizacao.")
        return user
    except (UnregisteredUserError, BlockedUserError, ForbiddenOperationError, RateLimitedError):
        raise
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha ao verificar autorizacao.") from exc


def record_operation(
    database_url: str,
    user: AppUser,
    action: str,
    outcome: str,
) -> None:
    """Registra somente identidade, acao fixa, resultado e horario."""
    try:
        with psycopg.connect(database_url) as connection:
            _audit(connection, action, outcome, user)
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha ao registrar auditoria.") from exc


def record_import_result(
    database_url: str,
    request_id: str,
    content_sha256: str,
    status: str,
    error_code: str | None,
) -> None:
    """Persiste apenas hash, resultado e erro de vocabulario controlado."""
    if (
        status not in IMPORT_STATUSES
        or SHA256_HEX.fullmatch(content_sha256) is None
        or (status == "importado" and error_code is not None)
        or (status == "rejeitado" and error_code not in IMPORT_ERROR_CODES)
    ):
        raise AuthDatabaseError("Resultado de importacao invalido.")
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute(
                """
                INSERT INTO import_audit_events
                    (request_id, content_sha256, status, error_code)
                VALUES (%s, %s, %s, %s)
                """,
                (request_id, content_sha256, status, error_code),
            )
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha ao registrar resultado de importacao.") from exc


def list_users(database_url: str) -> list[AppUser]:
    try:
        with psycopg.connect(database_url) as connection:
            rows = connection.execute(
                """
                SELECT issuer, subject, email, role, active
                FROM app_users
                ORDER BY role, subject
                """
            ).fetchall()
        return [AppUser(*row) for row in rows]
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha ao consultar usuarios.") from exc


def create_user(
    database_url: str,
    issuer: str,
    subject: str,
    role: str,
    email: str | None,
    actor: AppUser,
) -> None:
    identity = parse_identity({"iss": issuer, "sub": subject, "exp": 2**62})
    if role not in ROLES:
        raise InvalidIdentityError("Perfil invalido.")
    if email is not None and not 3 <= len(email) <= 320:
        raise InvalidIdentityError("E-mail auxiliar invalido.")
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute(
                """
                INSERT INTO app_users
                    (issuer, subject, email, role, created_by_issuer, created_by_subject)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    identity.issuer,
                    identity.subject,
                    email,
                    role,
                    actor.issuer,
                    actor.subject,
                ),
            )
            _audit(connection, "manage_users", "success", actor)
    except psycopg.errors.UniqueViolation as exc:
        raise InvalidIdentityError("Usuario ja cadastrado.") from exc
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha ao cadastrar usuario.") from exc


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
    identity = parse_identity({"iss": issuer, "sub": subject, "exp": 2**62})
    if role not in ROLES:
        raise InvalidIdentityError("Perfil invalido.")
    if email is not None and not 3 <= len(email) <= 320:
        raise InvalidIdentityError("E-mail auxiliar invalido.")
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute("LOCK TABLE app_users IN SHARE ROW EXCLUSIVE MODE")
            if role != "administracao" or not active:
                active_admins = connection.execute(
                    """
                    SELECT COUNT(*) FROM app_users
                    WHERE role = 'administracao' AND active
                      AND NOT (issuer = %s AND subject = %s)
                    """,
                    (issuer, subject),
                ).fetchone()[0]
                if active_admins == 0:
                    raise InvalidIdentityError(
                        "A ultima conta administrativa ativa deve ser preservada."
                    )
            cursor = connection.execute(
                """
                UPDATE app_users
                SET email = %s, role = %s, active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE issuer = %s AND subject = %s
                """,
                (email, role, active, issuer, subject),
            )
            if cursor.rowcount != 1:
                raise InvalidIdentityError("Usuario nao cadastrado.")
            _audit(connection, "manage_users", "success", actor)
    except InvalidIdentityError:
        raise
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha ao atualizar usuario.") from exc


def bootstrap_admin(
    database_url: str,
    issuer: str,
    subject: str,
    email: str | None = None,
) -> None:
    identity = parse_identity({"iss": issuer, "sub": subject, "exp": 2**62})
    if email is not None and not 3 <= len(email) <= 320:
        raise InvalidIdentityError("E-mail auxiliar invalido.")
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute("LOCK TABLE app_users IN EXCLUSIVE MODE")
            if connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0] != 0:
                raise InvalidIdentityError("Bootstrap permitido somente sem usuarios.")
            connection.execute(
                """
                INSERT INTO app_users (issuer, subject, email, role)
                VALUES (%s, %s, %s, 'administracao')
                """,
                (identity.issuer, identity.subject, email),
            )
            _audit(connection, "bootstrap_admin", "success", identity)
    except InvalidIdentityError:
        raise
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha no bootstrap administrativo.") from exc


def recover_admin(database_url: str, issuer: str, subject: str) -> None:
    identity = parse_identity({"iss": issuer, "sub": subject, "exp": 2**62})
    try:
        with psycopg.connect(database_url) as connection:
            cursor = connection.execute(
                """
                UPDATE app_users
                SET role = 'administracao', active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE issuer = %s AND subject = %s
                """,
                (identity.issuer, identity.subject),
            )
            if cursor.rowcount != 1:
                raise InvalidIdentityError("Usuario nao cadastrado.")
            _audit(connection, "recover_admin", "success", identity)
    except InvalidIdentityError:
        raise
    except psycopg.Error as exc:
        raise AuthDatabaseError("Falha na recuperacao administrativa.") from exc
