"""Configuracao explicita do processo HTTP, sem carregar arquivos locais."""

from __future__ import annotations

from dataclasses import dataclass, field
import ipaddress
import os
import re
from typing import Mapping
from urllib.parse import urlsplit

from psycopg.conninfo import conninfo_to_dict


class ConfigurationError(RuntimeError):
    """Configuracao ausente ou invalida, sem refletir valores do ambiente."""


def _invalid() -> None:
    raise ConfigurationError("Configuracao da API ausente ou invalida.") from None


@dataclass(frozen=True, slots=True, repr=False)
class APIConfig:
    database_url: str = field(repr=False)
    public_origin: str
    app_env: str
    oidc_client_id: str = field(repr=False)
    oidc_client_secret: str = field(repr=False)
    session_secret: str = field(repr=False)
    login_rate_limit: int = 20
    login_rate_window_seconds: int = 60
    redeem_rate_limit: int = 10
    redeem_rate_window_seconds: int = 60
    professional_read_rate_limit: int = 120
    professional_write_rate_limit: int = 60
    professional_rate_window_seconds: int = 60
    participant_read_rate_limit: int = 120
    participant_write_rate_limit: int = 60
    participant_rate_window_seconds: int = 60

    def __post_init__(self) -> None:
        for value, upper_bound in (
            (self.participant_read_rate_limit, 10000),
            (self.participant_write_rate_limit, 10000),
            (self.participant_rate_window_seconds, 86400),
        ):
            if type(value) is not int or not 1 <= value <= upper_bound:
                _invalid()
        if self.app_env not in {"development", "test", "production"}:
            _invalid()
        if (
            isinstance(self.login_rate_limit, bool)
            or not isinstance(self.login_rate_limit, int)
            or not 1 <= self.login_rate_limit <= 1000
            or isinstance(self.login_rate_window_seconds, bool)
            or not isinstance(self.login_rate_window_seconds, int)
            or not 1 <= self.login_rate_window_seconds <= 86400
            or isinstance(self.redeem_rate_limit, bool)
            or not isinstance(self.redeem_rate_limit, int)
            or not 1 <= self.redeem_rate_limit <= 1000
            or isinstance(self.redeem_rate_window_seconds, bool)
            or not isinstance(self.redeem_rate_window_seconds, int)
            or not 1 <= self.redeem_rate_window_seconds <= 86400
            or isinstance(self.professional_read_rate_limit, bool)
            or not isinstance(self.professional_read_rate_limit, int)
            or not 1 <= self.professional_read_rate_limit <= 10000
            or isinstance(self.professional_write_rate_limit, bool)
            or not isinstance(self.professional_write_rate_limit, int)
            or not 1 <= self.professional_write_rate_limit <= 10000
            or isinstance(self.professional_rate_window_seconds, bool)
            or not isinstance(self.professional_rate_window_seconds, int)
            or not 1 <= self.professional_rate_window_seconds <= 86400
        ):
            _invalid()
        for value, minimum, maximum in (
            (self.oidc_client_id, 8, 256),
            (self.oidc_client_secret, 16, 512),
            (self.session_secret, 32, 512),
        ):
            if (
                not isinstance(value, str) or not minimum <= len(value) <= maximum
                or any(character.isspace() or ord(character) < 32 for character in value)
            ):
                _invalid()
        try:
            if not isinstance(self.database_url, str) or not self.database_url.startswith(
                ("postgresql://", "postgres://")
            ):
                _invalid()
            if any(character.isspace() for character in self.database_url):
                _invalid()
            database = conninfo_to_dict(self.database_url)
            if not database.get("dbname") or not (database.get("host") or database.get("hostaddr")):
                _invalid()
            if not isinstance(self.public_origin, str) or any(
                character.isspace() or ord(character) < 32 for character in self.public_origin
            ):
                _invalid()
            origin = urlsplit(self.public_origin)
            if (
                origin.scheme != "https" or not origin.hostname
                or origin.username is not None or origin.password is not None
                or origin.path not in {"", "/"} or origin.query or origin.fragment
            ):
                _invalid()
            hostname = origin.hostname
            try:
                ipaddress.ip_address(hostname)
            except ValueError:
                if len(hostname) > 253 or any(
                    not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
                    for label in hostname.split(".")
                ):
                    _invalid()
            if origin.port is not None and not 1 <= origin.port <= 65535:
                _invalid()
        except ConfigurationError:
            raise
        except Exception:
            _invalid()
        canonical_host = f"[{hostname}]" if ":" in hostname else hostname.lower()
        port = f":{origin.port}" if origin.port not in {None, 443} else ""
        object.__setattr__(self, "public_origin", f"https://{canonical_host}{port}")

    @classmethod
    def from_env(cls, environment: Mapping[str, str] | None = None) -> APIConfig:
        values = os.environ if environment is None else environment
        try:
            login_rate_limit = int(values.get("API_LOGIN_RATE_LIMIT", "20"))
            login_rate_window_seconds = int(
                values.get("API_LOGIN_RATE_WINDOW_SECONDS", "60")
            )
            redeem_rate_limit = int(values.get("API_REDEEM_RATE_LIMIT", "10"))
            redeem_rate_window_seconds = int(
                values.get("API_REDEEM_RATE_WINDOW_SECONDS", "60")
            )
            professional_read_rate_limit = int(values.get("API_PROFESSIONAL_READ_RATE_LIMIT", "120"))
            professional_write_rate_limit = int(values.get("API_PROFESSIONAL_WRITE_RATE_LIMIT", "60"))
            professional_rate_window_seconds = int(values.get("API_PROFESSIONAL_RATE_WINDOW_SECONDS", "60"))
            participant_read_rate_limit = int(values.get("API_PARTICIPANT_READ_RATE_LIMIT", "120"))
            participant_write_rate_limit = int(values.get("API_PARTICIPANT_WRITE_RATE_LIMIT", "60"))
            participant_rate_window_seconds = int(values.get("API_PARTICIPANT_RATE_WINDOW_SECONDS", "60"))
        except (TypeError, ValueError):
            _invalid()
        return cls(
            database_url=values.get("API_DATABASE_URL", ""),
            public_origin=values.get("API_PUBLIC_ORIGIN", ""),
            app_env=values.get("APP_ENV", ""),
            oidc_client_id=values.get("OIDC_CLIENT_ID", ""),
            oidc_client_secret=values.get("OIDC_CLIENT_SECRET", ""),
            session_secret=values.get("API_SESSION_SECRET", ""),
            login_rate_limit=login_rate_limit,
            login_rate_window_seconds=login_rate_window_seconds,
            redeem_rate_limit=redeem_rate_limit,
            redeem_rate_window_seconds=redeem_rate_window_seconds,
            professional_read_rate_limit=professional_read_rate_limit,
            professional_write_rate_limit=professional_write_rate_limit,
            professional_rate_window_seconds=professional_rate_window_seconds,
            participant_read_rate_limit=participant_read_rate_limit,
            participant_write_rate_limit=participant_write_rate_limit,
            participant_rate_window_seconds=participant_rate_window_seconds,
        )
