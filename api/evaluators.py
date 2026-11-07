"""Rotas HTTP para o cadastro central de avaliadores (/api/v1/evaluators)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request

from api.errors import APIError
from api.models import RequestModel
from api.patients import (
    _map_registry_error,
    _parse_positive_int,
    _single_query_params,
)
from api.sessions import (
    _professional_read,
    _professional_write,
    _reject_empty_body,
    _reject_query,
)
from stroop.application import web_registry as application


router = APIRouter(prefix="/api/v1/evaluators", tags=["evaluators"])

ALLOWED_LIST_PARAMS = frozenset({"search", "active", "page", "page_size", "sort"})


class CreateEvaluatorRequest(RequestModel):
    full_name: str
    initials: str | None = None
    confirm_homonym: bool = False


class UpdateEvaluatorRequest(RequestModel):
    full_name: str | None = None
    initials: str | None = None
    active: bool | None = None
    reason_code: str


@router.get("")
async def list_evaluators(request: Request):
    await _reject_empty_body(request)
    actor = _professional_read(request, "view_dashboard")
    params = _single_query_params(request, ALLOWED_LIST_PARAMS)
    page = _parse_positive_int(
        params.get("page", "1"), default=1, max_value=100_000
    )
    page_size = _parse_positive_int(
        params.get("page_size", "25"), default=25, max_value=100
    )
    try:
        return application.list_evaluators(
            request.app.state.config.database_url,
            actor,
            search=params.get("search"),
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


@router.post("", status_code=201)
async def create_evaluator(request: Request, body: CreateEvaluatorRequest):
    _reject_query(request)
    actor = _professional_write(request, "manage_evaluators")
    try:
        return application.create_evaluator(
            request.app.state.config.database_url,
            actor,
            full_name=body.full_name,
            initials=body.initials,
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


@router.get("/{evaluator_id}")
async def get_evaluator(evaluator_id: UUID, request: Request):
    await _reject_empty_body(request)
    _reject_query(request)
    actor = _professional_read(request, "view_dashboard")
    try:
        return application.get_evaluator(
            request.app.state.config.database_url,
            actor,
            evaluator_id,
        )
    except (
        application.InvalidRegistryDataError,
        application.ForbiddenRegistryError,
        application.MissingRegistryError,
        application.PersistenceError,
    ) as exc:
        raise _map_registry_error(exc) from None


@router.patch("/{evaluator_id}")
async def update_evaluator(
    evaluator_id: UUID,
    request: Request,
    body: UpdateEvaluatorRequest,
):
    _reject_query(request)
    actor = _professional_write(request, "manage_evaluators")
    try:
        return application.update_evaluator(
            request.app.state.config.database_url,
            actor,
            evaluator_id,
            full_name=body.full_name,
            initials=body.initials,
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
