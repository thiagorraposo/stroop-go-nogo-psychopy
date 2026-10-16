"""Contratos puros de identidade e autorizacao do nucleo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import re
from typing import Any, Mapping


GOOGLE_ISSUERS = frozenset(
    {"https://accounts.google.com", "accounts.google.com"}
)
ROLES = ("consulta", "importacao", "administracao")
PERMISSIONS = {
    "view_dashboard": frozenset(ROLES),
    "export_dashboard": frozenset(ROLES),
    "import_csv": frozenset({"importacao", "administracao"}),
    "manage_users": frozenset({"administracao"}),
    "manage_projects": frozenset({"administracao"}),
    "manage_project_members": frozenset({"administracao"}),
    "create_invitation": frozenset({"importacao", "administracao"}),
    "revoke_invitation": frozenset({"importacao", "administracao"}),
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


def opaque_user_id(issuer: str, subject: str) -> str:
    """Identificador tecnico estavel; a identidade continua sendo issuer + subject."""
    raw = issuer.encode("ascii") + b"\0" + subject.encode("ascii")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


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
    email = claims.get("email")
    if not isinstance(email, str) or not 3 <= len(email) <= 320:
        email = None
    return Identity(issuer, subject, expiration, email)


def ensure_not_expired(identity: Identity, now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    if identity.expires_at <= int(current.timestamp()):
        raise ExpiredIdentityError("Sessao expirada.")
