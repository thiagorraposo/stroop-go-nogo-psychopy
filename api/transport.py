"""Limites ASGI e contencao de falhas antes do handler padrao do servidor."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import re
from urllib.parse import urlsplit
from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from api.config import APIConfig
from api.errors import APIError, error_response


MAX_BODY_BYTES = 65536
MAX_CSV_UPLOAD_BYTES = 5 * 1024 * 1024
CSV_UPLOAD_PATH = re.compile(
    r"^/api/v1/projects/[0-9a-fA-F-]{36}/imports/[0-9a-fA-F-]{36}$"
)
# Defesa do proprio adaptador, inclusive quando o proxy nao participou do teste.
# Sao respostas de dados/redirecionamento, nunca paginas executaveis.
RESPONSE_HEADERS = {
    b"cache-control": b"no-store",
    b"x-content-type-options": b"nosniff",
    b"content-security-policy": (
        b"default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    ),
    b"x-frame-options": b"DENY",
    b"referrer-policy": b"no-referrer",
    b"cross-origin-resource-policy": b"same-origin",
}
logger = logging.getLogger("stroop.api")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError
    return number


def _invalid_constant(value: str) -> None:
    raise ValueError


def _json_media_type(value: str) -> bool:
    parts = [part.strip().lower() for part in value.split(";")]
    return parts[0] == "application/json" and (
        len(parts) == 1 or parts[1:] in (["charset=utf-8"], ['charset="utf-8"'])
    )


class RequestBoundary:
    """Conta bytes recebidos, valida JSON e nao propaga excecoes sensiveis."""

    def __init__(self, app: ASGIApp, config: APIConfig) -> None:
        self.app = app
        self.origin = urlsplit(config.public_origin)

    def _valid_host(self, headers: dict[bytes, list[bytes]]) -> bool:
        values = headers.get(b"host", [])
        if len(values) != 1:
            return False
        try:
            value = values[0].decode("ascii")
            if any(character.isspace() for character in value):
                return False
            parsed = urlsplit("//" + value)
            return (
                parsed.hostname == self.origin.hostname
                and (parsed.port if parsed.port is not None else 443)
                == (self.origin.port if self.origin.port is not None else 443)
                and parsed.username is None and parsed.password is None
                and not parsed.path and not parsed.query and not parsed.fragment
            )
        except (ValueError, UnicodeError):
            return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        started = False
        path = scope.get("path", "")
        is_csv_upload = scope["method"] == "POST" and CSV_UPLOAD_PATH.fullmatch(path) is not None
        upload_semaphore = getattr(getattr(self.app, "state", None), "csv_import_semaphore", None)
        upload_acquired = False

        async def safe_send(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
                headers = [
                    (key, value) for key, value in message.get("headers", [])
                    if key.lower() != b"x-request-id" and key.lower() not in RESPONSE_HEADERS
                ]
                message = dict(message, headers=headers + [
                    (b"x-request-id", request_id.encode("ascii")),
                    *RESPONSE_HEADERS.items(),
                ])
            await send(message)

        try:
            if is_csv_upload and upload_semaphore is not None:
                try:
                    await asyncio.wait_for(upload_semaphore.acquire(), timeout=5)
                    upload_acquired = True
                except TimeoutError:
                    raise APIError("rate_limited", headers={"Retry-After": "5"}) from None
            headers: dict[bytes, list[bytes]] = {}
            for key, value in scope.get("headers", []):
                headers.setdefault(key.lower(), []).append(value)
            if not self._valid_host(headers):
                raise APIError("invalid_request")
            declared_lengths = headers.get(b"content-length", [])
            # Framing ambiguo deve ser recusado tambem se chegar de um adaptador
            # ASGI/proxy permissivo; o proxy publico deve rejeita-lo antes.
            transfers = headers.get(b"transfer-encoding", [])
            if transfers and (declared_lengths or len(transfers) != 1
                              or transfers[0].strip().lower() != b"chunked"):
                raise APIError("invalid_json")
            body_limit = MAX_CSV_UPLOAD_BYTES if is_csv_upload else MAX_BODY_BYTES
            if declared_lengths:
                if len(declared_lengths) != 1 or not declared_lengths[0].isdigit():
                    raise APIError("invalid_json")
                size = declared_lengths[0].lstrip(b"0") or b"0"
                if len(size) > len(str(body_limit)) or int(size) > body_limit:
                    raise APIError("body_too_large")
            encodings = headers.get(b"content-encoding", [])
            if encodings and (len(encodings) != 1 or encodings[0].strip().lower() != b"identity"):
                raise APIError("unsupported_media_type")

            chunks = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                if len(chunks) + len(chunk) > body_limit:
                    raise APIError("body_too_large")
                chunks.extend(chunk)
                if not message.get("more_body", False):
                    break
            body = bytes(chunks)
            if declared_lengths and len(body) != int(size):
                raise APIError("invalid_json")
            requires_json = (scope["method"] in {"POST", "PUT", "PATCH", "DELETE"} or bool(body)) and not is_csv_upload
            if is_csv_upload:
                media_types = headers.get(b"content-type", [])
                media = media_types[0].decode("latin-1") if len(media_types) == 1 else ""
                parts = [part.strip().lower() for part in media.split(";")]
                if parts[0] != "text/csv" or (len(parts) > 1 and parts[1:] not in (["charset=utf-8"], ['charset="utf-8"'])):
                    raise APIError("unsupported_media_type")
            if requires_json:
                media_types = headers.get(b"content-type", [])
                if len(media_types) != 1 or not _json_media_type(media_types[0].decode("latin-1")):
                    raise APIError("unsupported_media_type")
                try:
                    json.loads(
                        body.decode("utf-8"), object_pairs_hook=_unique_object,
                        parse_float=_finite_float, parse_constant=_invalid_constant,
                    )
                except (ValueError, UnicodeError, RecursionError):
                    raise APIError("invalid_json") from None

            delivered = False

            async def replay_receive() -> Message:
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return await receive()

            await self.app(scope, replay_receive, safe_send)
        except APIError as exc:
            if not started:
                await error_response(exc.code, request_id)(scope, receive, safe_send)
        except Exception:
            # Sem exc_info, texto da excecao, path, query, corpo ou headers.
            logger.warning("request_failed request_id=%s", request_id)
            if not started:
                await error_response("internal_error", request_id)(scope, receive, safe_send)
        finally:
            if upload_acquired:
                upload_semaphore.release()
