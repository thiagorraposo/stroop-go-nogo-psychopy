"""Gestao WEB com validacao compartilhada e capacidade SQL dedicada."""
from __future__ import annotations

from stroop.application.auth import _validate_user_fields
from stroop.domain.auth import (AppUser, AuthDatabaseError, ForbiddenOperationError,
                               InvalidIdentityError, LastAdminProtectionError)
from stroop.persistence import web_administration as persistence
from stroop.persistence.auth import DuplicateUserError, PersistenceError


def _manage(database_url: str, operation: str, issuer: str, subject: str, *,
            role: str, active: bool, email: str | None, actor: AppUser) -> None:
    identity = _validate_user_fields(issuer, subject, role, email)
    from stroop.domain.local_auth import LOCAL_ISSUER
    if issuer == LOCAL_ISSUER:
        if operation == 'create':
            raise ForbiddenOperationError('Provisionamento exclusivo do operador.')
    try:
        status = persistence.manage_user(database_url, operation, identity, role=role,
                                         active=active, email=email, actor=actor)
    except DuplicateUserError:
        raise InvalidIdentityError('Usuario ja cadastrado.') from None
    except PersistenceError:
        raise AuthDatabaseError('Falha ao gerir usuario.') from None
    if status == 'forbidden':
        raise ForbiddenOperationError('Operacao nao autorizada.')
    if status == 'last_admin':
        raise LastAdminProtectionError('A ultima conta administrativa ativa deve ser preservada.')
    if status == 'missing':
        raise InvalidIdentityError('Usuario nao cadastrado.')
    if status != ('created' if operation == 'create' else 'updated'):
        raise AuthDatabaseError('Falha ao gerir usuario.')


def create_user(database_url: str, issuer: str, subject: str, role: str,
                email: str | None, actor: AppUser) -> None:
    _manage(database_url, 'create', issuer, subject, role=role, active=True,
            email=email, actor=actor)


def update_user(database_url: str, issuer: str, subject: str, *, role: str,
                active: bool, email: str | None, actor: AppUser) -> None:
    _manage(database_url, 'update', issuer, subject, role=role, active=active,
            email=email, actor=actor)
