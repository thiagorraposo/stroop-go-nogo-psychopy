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

    def __post_init__(self) -> None:
        if self.app_env not in {"development", "test", "production"}:
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
        return cls(
            database_url=values.get("API_DATABASE_URL", ""),
            public_origin=values.get("API_PUBLIC_ORIGIN", ""),
            app_env=values.get("APP_ENV", ""),
        )
