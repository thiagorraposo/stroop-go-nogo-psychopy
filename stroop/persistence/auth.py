"""Operacoes SQL de autorizacao PostgreSQL."""

from __future__ import annotations

from uuid import uuid4

import psycopg

from stroop.domain.auth import AppUser, DENIAL_WINDOW_MINUTES, Identity


class PersistenceError(Exception):
    """Falha de persistencia sem detalhes do driver."""


class DuplicateUserError(PersistenceError):
    """Chave de identidade ja cadastrada."""


def _audit(connection, action: str, outcome: str, identity: Identity | AppUser | None) -> None:
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


def record_expired_denial(
    database_url: str, identity: Identity, action: str
) -> None:
    try:
        with psycopg.connect(database_url) as connection:
            _audit(connection, action, "denied_expired", identity)
    except psycopg.Error as exc:
        raise PersistenceError from exc


def authorize_identity(
    database_url: str,
    identity: Identity,
    action: str,
    allowed_roles: frozenset[str],
    denial_limit: int,
) -> tuple[str, AppUser | None]:
    """Audita a decisao e retorna seu codigo interno e usuario, quando elegivel."""
    try:
        with psycopg.connect(database_url) as connection:
            recent_denials = int(
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
            if recent_denials >= denial_limit:
                _audit(connection, action, "rate_limited", identity)
                return "rate_limited", None

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
                return "unregistered", None

            user = AppUser(*row)
            if not user.active:
                _audit(connection, action, "denied_blocked", identity)
                return "blocked", user
            if user.role not in allowed_roles:
                _audit(connection, action, "denied_forbidden", identity)
                return "forbidden", user
            _audit(connection, action, "allowed", identity)
            return "found", user
    except psycopg.Error as exc:
        raise PersistenceError from exc


def record_operation(
    database_url: str, user: AppUser, action: str, outcome: str
) -> None:
    try:
        with psycopg.connect(database_url) as connection:
            _audit(connection, action, outcome, user)
    except psycopg.Error as exc:
        raise PersistenceError from exc


def record_import_result(
    database_url: str,
    request_id: str,
    content_sha256: str,
    status: str,
    error_code: str | None,
) -> None:
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
        raise PersistenceError from exc


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
        raise PersistenceError from exc


def list_users_page(database_url: str, limit: int, offset: int) -> list[AppUser]:
    try:
        with psycopg.connect(database_url) as connection:
            rows = connection.execute(
                """SELECT issuer, subject, email, role, active FROM app_users
                   ORDER BY role, subject, issuer LIMIT %s OFFSET %s""",
                (limit, offset),
            ).fetchall()
        return [AppUser(*row) for row in rows]
    except psycopg.Error as exc:
        raise PersistenceError from exc


def create_user(
    database_url: str,
    identity: Identity,
    role: str,
    email: str | None,
    actor: AppUser,
) -> None:
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
        raise DuplicateUserError from exc
    except psycopg.Error as exc:
        raise PersistenceError from exc


def update_user(
    database_url: str,
    identity: Identity,
    *,
    role: str,
    active: bool,
    email: str | None,
    actor: AppUser,
) -> str:
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
                    (identity.issuer, identity.subject),
                ).fetchone()[0]
                if active_admins == 0:
                    return "last_admin"
            cursor = connection.execute(
                """
                UPDATE app_users
                SET email = %s, role = %s, active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE issuer = %s AND subject = %s
                """,
                (email, role, active, identity.issuer, identity.subject),
            )
            if cursor.rowcount != 1:
                return "missing"
            _audit(connection, "manage_users", "success", actor)
        return "updated"
    except psycopg.Error as exc:
        raise PersistenceError from exc


def bootstrap_admin(
    database_url: str, identity: Identity, email: str | None
) -> bool:
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute("LOCK TABLE app_users IN EXCLUSIVE MODE")
            if connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0] != 0:
                return False
            connection.execute(
                """
                INSERT INTO app_users (issuer, subject, email, role)
                VALUES (%s, %s, %s, 'administracao')
                """,
                (identity.issuer, identity.subject, email),
            )
            _audit(connection, "bootstrap_admin", "success", identity)
        return True
    except psycopg.Error as exc:
        raise PersistenceError from exc


def recover_admin(database_url: str, identity: Identity) -> bool:
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
                return False
            _audit(connection, "recover_admin", "success", identity)
        return True
    except psycopg.Error as exc:
        raise PersistenceError from exc
