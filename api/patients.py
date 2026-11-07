"""Rotas HTTP para o cadastro central de pacientes (/api/v1/patients)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request

from api.errors import APIError
from api.models import RequestModel
from api.sessions import (
    _professional_read,
    _professional_write,
    _reject_empty_body,
    _reject_query,
)
from stroop.application import web_registry as application


router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

ALLOWED_LIST_PARAMS = frozenset(
    {"search", "project_id", "active", "page", "page_size", "sort"}
)
ALLOWED_DUPLICATE_PARAMS = frozenset({"full_name", "initials"})


class CreatePatientRequest(RequestModel):
    full_name: str
    initials: str | None = None
    disambiguation_note: str | None = None
    confirm_homonym: bool = False


class UpdatePatientRequest(RequestModel):
    full_name: str | None = None
    initials: str | None = None
    disambiguation_note: str | None = None
    active: bool | None = None
    reason_code: str


def _parse_positive_int(raw: str, *, default: int, max_value: int) -> int:
    if not raw.isascii() or not raw.isdigit() or len(raw) > 6:
        raise APIError("invalid_request")
    value = int(raw)
    if not 1 <= value <= max_value:
        raise APIError("invalid_request")
    return value


def _single_query_params(
    request: Request,
    allowed: frozenset[str],
) -> dict[str, str]:
    pairs = request.query_params.multi_items()
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)) or set(keys) - allowed:
        raise APIError("invalid_request")
    return dict(pairs)


def _map_registry_error(exc: Exception) -> APIError:
    if isinstance(exc, application.DuplicateCandidateError):
        return APIError(
            "duplicate_candidate_found",
            extra={"candidates": exc.candidates},
        )
    if isinstance(exc, application.InvalidRegistryDataError):
        return APIError("invalid_request")
    if isinstance(exc, application.ForbiddenRegistryError):
        return APIError("permission_denied")
    if isinstance(exc, application.MissingRegistryError):
        return APIError("not_found")
    return APIError("service_unavailable")


@router.get("")
async def list_patients(request: Request):
    await _reject_empty_body(request)
    actor = _professional_read(request, "view_dashboard")
    params = _single_query_params(request, ALLOWED_LIST_PARAMS)
    project_id: UUID | None = None
    if "project_id" in params:
        try:
            project_id = UUID(params["project_id"])
        except ValueError:
            raise APIError("invalid_request") from None
    page = _parse_positive_int(
        params.get("page", "1"), default=1, max_value=100_000
    )
    page_size = _parse_positive_int(
        params.get("page_size", "25"), default=25, max_value=100
    )
    try:
        return application.list_patients(
            request.app.state.config.database_url,
            actor,
            search=params.get("search"),
            project_id=project_id,
            active=params.get("active", "all"),
            page=page,
            page_size=page_size,
            sort=params.get("sort", "name_asc"),
        )
    except (
        application.InvalidRegistryDataError,
        application.ForbiddenRegistryError,
        application.MissingRegistryError,
        application.PersistenceError,
    ) as exc:
        raise _map_registry_error(exc) from None


@router.get("/duplicates")
async def find_patient_duplicates(request: Request):
    await _reject_empty_body(request)
    actor = _professional_read(request, "manage_patients")
    params = _single_query_params(request, ALLOWED_DUPLICATE_PARAMS)
    if "full_name" not in params:
        raise APIError("invalid_request")
    try:
        candidates = application.find_duplicate_patients(
            request.app.state.config.database_url,
            actor,
            full_name=params["full_name"],
            initials=params.get("initials"),
        )
    except (
        application.InvalidRegistryDataError,
        application.ForbiddenRegistryError,
        application.MissingRegistryError,
        application.PersistenceError,
    ) as exc:
        raise _map_registry_error(exc) from None
    return {"candidates": candidates}


@router.post("", status_code=201)
async def create_patient(request: Request, body: CreatePatientRequest):
    _reject_query(request)
    actor = _professional_write(request, "manage_patients")
    try:
        return application.create_patient(
            request.app.state.config.database_url,
            actor,
            full_name=body.full_name,
            initials=body.initials,
            disambiguation_note=body.disambiguation_note,
            confirm_homonym=body.confirm_homonym,
        )
    except (
        application.DuplicateCandidateError,
        application.InvalidRegistryDataError,
        application.ForbiddenRegistryError,
        application.MissingRegistryError,
        application.PersistenceError,
    ) as exc:
        raise _map_registry_error(exc) from None


@router.get("/{patient_id}")
async def get_patient(patient_id: UUID, request: Request):
    await _reject_empty_body(request)
    _reject_query(request)
    actor = _professional_read(request, "view_dashboard")
    try:
        return application.get_patient(
            request.app.state.config.database_url,
            actor,
            patient_id,
        )
    except (
        application.InvalidRegistryDataError,
        application.ForbiddenRegistryError,
        application.MissingRegistryError,
        application.PersistenceError,
    ) as exc:
        raise _map_registry_error(exc) from None


@router.patch("/{patient_id}")
async def update_patient(
    patient_id: UUID,
    request: Request,
    body: UpdatePatientRequest,
):
    _reject_query(request)
    actor = _professional_write(request, "manage_patients")
    try:
        return application.update_patient(
            request.app.state.config.database_url,
            actor,
            patient_id,
            full_name=body.full_name,
            initials=body.initials,
            disambiguation_note=body.disambiguation_note,
            active=body.active,
            reason_code=body.reason_code,
        )
    except (
        application.InvalidRegistryDataError,
        application.ForbiddenRegistryError,
        application.MissingRegistryError,
        application.PersistenceError,
    ) as exc:
        raise _map_registry_error(exc) from None


__all__ = ["router"]
