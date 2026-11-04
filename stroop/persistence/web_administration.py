"""Capacidade SQL restrita para administracao de contas pela WEB."""
from __future__ import annotations

import psycopg

from stroop.domain.auth import AppUser, Identity
from stroop.persistence.auth import DuplicateUserError, PersistenceError


def manage_user(database_url: str, operation: str, identity: Identity, *, role: str,
                active: bool, email: str | None, actor: AppUser) -> str:
    try:
        with psycopg.connect(database_url) as connection:
            return connection.execute(
                'SELECT public.web_manage_user(%s,%s,%s,%s,%s,%s,%s,%s)',
                (operation, actor.issuer, actor.subject, identity.issuer,
                 identity.subject, role, email, active),
            ).fetchone()[0]
    except psycopg.errors.UniqueViolation as exc:
        raise DuplicateUserError from exc
    except psycopg.Error as exc:
        raise PersistenceError from exc
