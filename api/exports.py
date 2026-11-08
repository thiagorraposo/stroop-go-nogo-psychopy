"""Endpoints de exportação CSV multi-granularidade (REQ-CSV-005 / ADR-007).

Rotas:
- POST /api/v1/exports/preview
- POST /api/v1/exports/download
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from api.errors import APIError
from api.models import RequestModel
from api.sessions import _professional_write, _reject_query
from stroop.domain.web_multi_export import (
    GRANULARITY_COLUMNS,
    validate_granularity_and_columns,
    serialize_multi_csv,
)
from stroop.persistence.web_multi_export import query_multi_export_rows

router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


def _sign_token(config: Any, scope: str, payload: Any) -> str:
    data = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(
        config.session_secret.encode(),
        scope.encode() + b"\0" + data,
        hashlib.sha256,
    ).hexdigest().encode()
    return base64.urlsafe_b64encode(data + b"." + signature).rstrip(b"=").decode()


def _verify_token(config: Any, scope: str, token: str) -> Any:
    try:
        data, signature = base64.urlsafe_b64decode(
            token + "=" * (-len(token) % 4)
        ).rsplit(b".", 1)
        expected = hmac.new(
            config.session_secret.encode(),
            scope.encode() + b"\0" + data,
            hashlib.sha256,
        ).hexdigest().encode()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        return json.loads(data)
    except (ValueError, TypeError, UnicodeError):
        raise APIError("invalid_request") from None


class ExportPreviewRequest(RequestModel):
    project_id: str
    granularity: str
    columns: list[str] | None = None
    identification_mode: str = "deidentified"
    filters: dict[str, Any] | None = None


class ExportDownloadRequest(RequestModel):
    project_id: str
    granularity: str
    columns: list[str] | None = None
    identification_mode: str = "deidentified"
    export_token: str
    filters: dict[str, Any] | None = None


@router.post("/preview")
async def preview_export(request: Request, body: ExportPreviewRequest):
    _reject_query(request)
    actor = _professional_write(request, "export_dashboard")

    try:
        project_uuid = UUID(body.project_id)
    except ValueError:
        raise APIError("invalid_request") from None

    if body.identification_mode not in ("deidentified", "nominal"):
        raise APIError("invalid_request")

    if body.identification_mode == "nominal" and actor.role != "administracao":
        raise APIError("permission_denied")

    try:
        granularity, columns = validate_granularity_and_columns(
            body.granularity, body.columns
        )
    except ValueError:
        raise APIError("invalid_request") from None

    rows = query_multi_export_rows(
        request.app.state.config.read_database_url or request.app.state.config.database_url,
        project_id=project_uuid,
        granularity=granularity,
        identification_mode=body.identification_mode,
    )

    # 15 minutos de validade do token
    now_ts = int(datetime.now(timezone.utc).timestamp())
    expires_at = now_ts + 900
    token_scope = f"export-token-v1:{actor.issuer}:{actor.subject}"
    token_payload = [granularity, body.identification_mode, str(project_uuid), expires_at]
    token = _sign_token(request.app.state.config, token_scope, token_payload)

    sample = rows[:5]
    return {
        "total_rows": len(rows),
        "columns": columns,
        "applied_criteria": {
            "project_id": str(project_uuid),
            "granularity": granularity,
            "identification_mode": body.identification_mode,
        },
        "sample_rows": sample,
        "export_token": token,
    }


@router.post("/download")
async def download_export(request: Request, body: ExportDownloadRequest):
    _reject_query(request)
    actor = _professional_write(request, "export_dashboard")

    try:
        project_uuid = UUID(body.project_id)
    except ValueError:
        raise APIError("invalid_request") from None

    if body.identification_mode not in ("deidentified", "nominal"):
        raise APIError("invalid_request")

    if body.identification_mode == "nominal" and actor.role != "administracao":
        raise APIError("permission_denied")

    token_scope = f"export-token-v1:{actor.issuer}:{actor.subject}"
    claims = _verify_token(request.app.state.config, token_scope, body.export_token)

    now_ts = int(datetime.now(timezone.utc).timestamp())
    if not isinstance(claims, list) or len(claims) != 4:
        raise APIError("invalid_request")

    tok_granularity, tok_mode, tok_project, tok_expires = claims
    if tok_granularity != body.granularity or tok_mode != body.identification_mode or tok_project != str(project_uuid):
        raise APIError("invalid_request")
    if tok_expires < now_ts:
        raise APIError("state_conflict")

    try:
        granularity, columns = validate_granularity_and_columns(
            body.granularity, body.columns
        )
    except ValueError:
        raise APIError("invalid_request") from None

    rows = query_multi_export_rows(
        request.app.state.config.read_database_url or request.app.state.config.database_url,
        project_id=project_uuid,
        granularity=granularity,
        identification_mode=body.identification_mode,
    )

    csv_content = serialize_multi_csv(
        rows,
        granularity=granularity,
        columns=columns,
        identification_mode=body.identification_mode,
    )

    filename = f"{granularity}_{str(project_uuid)[:8]}.csv"
    return Response(
        content=csv_content.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
