"""Configuracao explicita do processo HTTP, sem carregar arquivos locais."""

from __future__ import annotations

from dataclasses import dataclass, field
import ipaddress
import os
import stat
import re
from typing import Mapping
from urllib.parse import urlsplit

from psycopg.conninfo import conninfo_to_dict


class ConfigurationError(RuntimeError):
    """Configuracao ausente ou invalida, sem refletir valores do ambiente."""


def _invalid() -> None:
    raise ConfigurationError("Configuracao da API ausente ou invalida.") from None


def secret_value(values: Mapping[str, str], key: str, default: str = "") -> str:
    """Le somente arquivo explicitamente indicado; nao descobre .env/secrets."""
    file_key = f"{key}_FILE"
    if file_key not in values:
        return values.get(key, default)
    if key in values:
        _invalid()
    path = values[file_key]
    if not isinstance(path, str) or not path or "\x00" in path:
        _invalid()
    descriptor = None
    try:
        # NONBLOCK permite recusar FIFO/dispositivo sem esperar por um produtor.
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            _invalid()
        content = os.read(descriptor, 16385)
        if len(content) > 16384:
            _invalid()
        value = content.decode("utf-8")
        if value.endswith("\n"):
            value = value[:-1]
            if value.endswith("\r"):
                value = value[:-1]
        if not value:
            _invalid()
        return value
    except ConfigurationError:
        raise
    except (OSError, UnicodeError, ValueError):
        _invalid()
    finally:
        if descriptor is not None:
            os.close(descriptor)


def postgres_database_url(value: str) -> str:
    """Valida DSN URI para runtime e migrador, sem refletir credenciais."""
    try:
        if (not isinstance(value, str) or not value.startswith(("postgresql://", "postgres://"))
                or any(character.isspace() for character in value)):
            _invalid()
        database = conninfo_to_dict(value)
        if not database.get("dbname") or not (database.get("host") or database.get("hostaddr")):
            _invalid()
    except ConfigurationError:
        raise
    except Exception:
        _invalid()
    return value


@dataclass(frozen=True, slots=True, repr=False)
class APIConfig:
    database_url: str = field(repr=False)
    public_origin: str
    app_env: str
    session_secret: str = field(repr=False)
    oidc_client_id: str = field(default="", repr=False)
    oidc_client_secret: str = field(default="", repr=False)
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
    read_database_url: str = field(default="", repr=False)
    oidc_callback_path: str = "/api/v1/auth/callback"
    auth_mode: str = "local"

    def __post_init__(self) -> None:
        if self.auth_mode not in {"local", "oidc"} or (self.auth_mode == "oidc" and self.app_env != "test"):
            _invalid()
        for value, upper_bound in (
            (self.participant_read_rate_limit, 10000),
            (self.participant_write_rate_limit, 10000),
            (self.participant_rate_window_seconds, 86400),
        ):
            if type(value) is not int or not 1 <= value <= upper_bound:
                _invalid()
        if self.oidc_callback_path not in ("/api/v1/auth/callback", "/oauth2callback"):
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
        secrets_to_validate = [(self.session_secret, 32, 512)]
        if self.auth_mode == "oidc":
            secrets_to_validate.extend([(self.oidc_client_id, 8, 256), (self.oidc_client_secret, 16, 512)])
        for value, minimum, maximum in secrets_to_validate:
            if (
                not isinstance(value, str) or not minimum <= len(value) <= maximum
                or any(character.isspace() or ord(character) < 32 for character in value)
            ):
                _invalid()
        try:
            if not isinstance(self.read_database_url, str):
                _invalid()
            database_urls = [self.database_url]
            if self.read_database_url:
                database_urls.append(self.read_database_url)
            for database_url in database_urls:
                postgres_database_url(database_url)
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
            auth_mode=values.get("API_AUTH_MODE", "local"),
            database_url=secret_value(values, "API_DATABASE_URL"),
            read_database_url=secret_value(values, "API_READ_DATABASE_URL"),
            oidc_callback_path=values.get("OIDC_CALLBACK_PATH", "/api/v1/auth/callback"),
            public_origin=values.get("API_PUBLIC_ORIGIN", ""),
            app_env=values.get("APP_ENV", ""),
            oidc_client_id=secret_value(values, "OIDC_CLIENT_ID") if values.get("API_AUTH_MODE", "local") == "oidc" else "",
            oidc_client_secret=secret_value(values, "OIDC_CLIENT_SECRET") if values.get("API_AUTH_MODE", "local") == "oidc" else "",
            session_secret=secret_value(values, "API_SESSION_SECRET"),
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
