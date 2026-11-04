"""Persistencia de transacoes OIDC e sessoes opacas da API WEB."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import psycopg
from stroop.persistence.auth import PersistenceError


@dataclass(frozen=True, slots=True)
class ProfessionalSession:
    issuer: str
    subject: str
    oidc_expires_at: datetime
    expires_at: datetime


def create_oidc_transaction(
    database_url: str, state_sha256: str, nonce: str, code_verifier: str
) -> None:
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute(
                "DELETE FROM web_oidc_transactions WHERE expires_at <= CURRENT_TIMESTAMP"
            )
            connection.execute(
                """
                INSERT INTO web_oidc_transactions
                    (state_sha256, nonce, code_verifier, expires_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '10 minutes')
                """,
                (state_sha256, nonce, code_verifier),
            )
    except psycopg.Error as exc:
        raise PersistenceError from exc


def consume_oidc_transaction(
    database_url: str, state_sha256: str
) -> tuple[str, str] | None:
    try:
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                """
                DELETE FROM web_oidc_transactions
                WHERE state_sha256 = %s AND expires_at > CURRENT_TIMESTAMP
                RETURNING nonce, code_verifier
                """,
                (state_sha256,),
            ).fetchone()
    except psycopg.Error as exc:
        raise PersistenceError from exc
    return None if row is None else (row[0], row[1])


def create_professional_session(
    database_url: str,
    token_sha256: str,
    issuer: str,
    subject: str,
    oidc_expires_at: int,
) -> datetime:
    try:
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                """
                INSERT INTO web_professional_sessions
                    (token_sha256, issuer, subject, oidc_expires_at, expires_at)
                VALUES (
                    %s, %s, %s, to_timestamp(%s),
                    LEAST(to_timestamp(%s), CURRENT_TIMESTAMP + INTERVAL '8 hours')
                )
                RETURNING expires_at
                """,
                (token_sha256, issuer, subject, oidc_expires_at, oidc_expires_at),
            ).fetchone()
    except psycopg.Error as exc:
        raise PersistenceError from exc
    return row[0]


def find_professional_session(
    database_url: str, token_sha256: str
) -> ProfessionalSession | None:
    try:
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                """
                SELECT issuer, subject, oidc_expires_at, expires_at
                FROM web_professional_sessions
                WHERE token_sha256 = %s
                  AND expires_at > CURRENT_TIMESTAMP
                  AND oidc_expires_at > CURRENT_TIMESTAMP
                """,
                (token_sha256,),
            ).fetchone()
    except psycopg.Error as exc:
        raise PersistenceError from exc
    return None if row is None else ProfessionalSession(*row)


def revoke_professional_session(database_url: str, token_sha256: str) -> None:
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute(
                "DELETE FROM web_professional_sessions WHERE token_sha256 = %s",
                (token_sha256,),
            )
    except psycopg.Error as exc:
        raise PersistenceError from exc


def count_login_attempt(
    database_url: str, remote_sha256: str, limit: int, window_seconds: int
) -> tuple[bool, int]:
    """Incrementa uma janela atomica sem armazenar o endereco remoto."""
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute(
                """
                DELETE FROM web_login_rate_limits
                WHERE window_started_at <= clock_timestamp()
                    - make_interval(secs => %s * 2)
                """,
                (window_seconds,),
            )
            row = connection.execute(
                """
                INSERT INTO web_login_rate_limits
                    (remote_sha256, window_started_at, request_count)
                VALUES (%s, clock_timestamp(), 1)
                ON CONFLICT (remote_sha256) DO UPDATE SET
                    window_started_at = CASE
                        WHEN web_login_rate_limits.window_started_at
                            <= clock_timestamp() - make_interval(secs => %s)
                        THEN clock_timestamp()
                        ELSE web_login_rate_limits.window_started_at
                    END,
                    request_count = CASE
                        WHEN web_login_rate_limits.window_started_at
                            <= clock_timestamp() - make_interval(secs => %s)
                        THEN 1
                        ELSE LEAST(web_login_rate_limits.request_count + 1, %s + 1)
                    END
                RETURNING request_count,
                    GREATEST(
                        1,
                        ceil(extract(epoch FROM (
                            window_started_at + make_interval(secs => %s)
                            - clock_timestamp()
                        )))::integer
                    )
                """,
                (remote_sha256, window_seconds, window_seconds, limit, window_seconds),
            ).fetchone()
        return row[0] <= limit, row[1]
    except psycopg.Error as exc:
        raise PersistenceError from exc
