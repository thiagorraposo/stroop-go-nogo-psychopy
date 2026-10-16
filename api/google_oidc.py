"""Cliente minimo do OpenID Connect Google, sem devolver tokens ao navegador."""

from __future__ import annotations

import json
import hmac
import time
from typing import Any
from urllib.parse import urlencode, urlsplit

import httpx
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.id_token import verify_oauth2_token
import requests

from api.config import APIConfig


DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_ISSUER = "https://accounts.google.com"
GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
MAX_PROVIDER_BYTES = 32768


class OIDCProviderUnavailable(RuntimeError):
    """Falha de rede ou resposta invalida do provedor, sem conteudo externo."""


class InvalidOIDCResponse(ValueError):
    """Resposta ou identidade OIDC invalida."""


class _BoundedGoogleRequest(GoogleRequest):
    """Limita a cinco segundos tambem a busca de certificados do ID token."""

    def __call__(
        self, url, method="GET", body=None, headers=None, timeout=5.0, **kwargs
    ):
        return super().__call__(
            url,
            method=method,
            body=body,
            headers=headers,
            timeout=5.0 if timeout is None else min(timeout, 5.0),
            **kwargs,
        )


def _fetch_json(url: str, *, data: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=5.0, follow_redirects=False, trust_env=False) as client:
            with client.stream("GET" if data is None else "POST", url, data=data) as response:
                if not response.is_success:
                    raise OIDCProviderUnavailable("Provedor OIDC indisponivel.")
                body = bytearray()
                for chunk in response.iter_bytes():
                    if len(body) + len(chunk) > MAX_PROVIDER_BYTES:
                        raise OIDCProviderUnavailable("Resposta OIDC excede o limite.")
                    body.extend(chunk)
        result = json.loads(bytes(body).decode("utf-8"))
        if not isinstance(result, dict):
            raise OIDCProviderUnavailable("Resposta OIDC invalida.")
        return result
    except OIDCProviderUnavailable:
        raise
    except (httpx.HTTPError, UnicodeError, ValueError):
        raise OIDCProviderUnavailable("Provedor OIDC indisponivel.") from None


def _endpoint(metadata: dict[str, Any], key: str, hostname: str, path: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str):
        raise OIDCProviderUnavailable("Metadados OIDC invalidos.")
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https" or parsed.hostname != hostname
            or parsed.port is not None or parsed.username is not None
            or parsed.password is not None
            or parsed.path != path or parsed.query or parsed.fragment
        ):
            raise ValueError
    except ValueError:
        raise OIDCProviderUnavailable("Metadados OIDC invalidos.") from None
    return value


def authorization_url(
    config: APIConfig, *, state: str, nonce: str, code_challenge: str
) -> str:
    metadata = _fetch_json(DISCOVERY_URL)
    if (
        metadata.get("issuer") != GOOGLE_ISSUER
        or "code" not in metadata.get("response_types_supported", [])
        or "S256" not in metadata.get("code_challenge_methods_supported", [])
        or "client_secret_post" not in metadata.get(
            "token_endpoint_auth_methods_supported", []
        )
        or "RS256" not in metadata.get("id_token_signing_alg_values_supported", [])
    ):
        raise OIDCProviderUnavailable("Metadados OIDC invalidos.")
    endpoint = _endpoint(
        metadata, "authorization_endpoint", "accounts.google.com", "/o/oauth2/v2/auth"
    )
    _endpoint(metadata, "token_endpoint", "oauth2.googleapis.com", "/token")
    _endpoint(metadata, "jwks_uri", "www.googleapis.com", "/oauth2/v3/certs")
    parameters = urlencode({
        "client_id": config.oidc_client_id,
        "redirect_uri": f"{config.public_origin}/api/v1/auth/callback",
        "response_type": "code",
        "scope": "openid email",
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "prompt": "select_account",
    })
    return f"{endpoint}?{parameters}"


def exchange_code(
    config: APIConfig, *, code: str, code_verifier: str, expected_nonce: str
) -> dict[str, Any]:
    metadata = _fetch_json(DISCOVERY_URL)
    if (
        metadata.get("issuer") != GOOGLE_ISSUER
        or "client_secret_post" not in metadata.get(
            "token_endpoint_auth_methods_supported", []
        )
        or "RS256" not in metadata.get("id_token_signing_alg_values_supported", [])
    ):
        raise OIDCProviderUnavailable("Metadados OIDC invalidos.")
    token_endpoint = _endpoint(
        metadata, "token_endpoint", "oauth2.googleapis.com", "/token"
    )
    _endpoint(metadata, "authorization_endpoint", "accounts.google.com", "/o/oauth2/v2/auth")
    _endpoint(metadata, "jwks_uri", "www.googleapis.com", "/oauth2/v3/certs")
    token_data = _fetch_json(token_endpoint, data={
        "code": code,
        "client_id": config.oidc_client_id,
        "client_secret": config.oidc_client_secret,
        "redirect_uri": f"{config.public_origin}/api/v1/auth/callback",
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
    })
    encoded_id_token = token_data.get("id_token")
    if not isinstance(encoded_id_token, str) or not 1 <= len(encoded_id_token) <= 16384:
        raise InvalidOIDCResponse("Token OIDC invalido.")

    session = requests.Session()
    session.trust_env = False
    try:
        claims = verify_oauth2_token(
            encoded_id_token,
            _BoundedGoogleRequest(session=session),
            audience=config.oidc_client_id,
        )
    except (GoogleAuthError, requests.RequestException, ValueError):
        raise InvalidOIDCResponse("Token OIDC invalido.") from None
    finally:
        session.close()

    nonce = claims.get("nonce")
    if not isinstance(nonce, str) or not hmac.compare_digest(nonce, expected_nonce):
        raise InvalidOIDCResponse("Token OIDC invalido.")
    authorized_party = claims.get("azp")
    if authorized_party is not None and authorized_party != config.oidc_client_id:
        raise InvalidOIDCResponse("Token OIDC invalido.")
    if claims.get("iss") not in {"https://accounts.google.com", "accounts.google.com"}:
        raise InvalidOIDCResponse("Token OIDC invalido.")
    expiration = claims.get("exp")
    if (
        isinstance(expiration, bool) or not isinstance(expiration, int)
        or expiration <= int(time.time())
    ):
        raise InvalidOIDCResponse("Token OIDC invalido.")
    audience = claims.get("aud")
    if isinstance(audience, list) and len(audience) > 1 and authorized_party is None:
        raise InvalidOIDCResponse("Token OIDC invalido.")
    issued_at = claims.get("iat")
    if isinstance(issued_at, bool) or not isinstance(issued_at, int):
        raise InvalidOIDCResponse("Token OIDC invalido.")
    return dict(claims)
