"""Consulta e exportacao profissional sob escopo de projeto."""
import re
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import Response

from api.errors import APIError
from api.sessions import (
    _next_cursor, _page, _professional_read, _reject_empty_body, _reject_query,
)
from stroop.application import web_assessments as application

router = APIRouter(prefix='/api/v1/projects/{project_id}/assessments', tags=['assessments'])
FILTERS = frozenset({'participant_id', 'visit'})
LABEL = re.compile(r'^[A-Za-z0-9_.-]{1,64}$')


def _filters(request: Request) -> dict[str, str | None]:
    values = {key: request.query_params.get(key) for key in FILTERS}
    if any(value is not None and LABEL.fullmatch(value) is None for value in values.values()):
        raise APIError('invalid_request')
    return values


def _identifier(value: str) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', value):
        raise APIError('invalid_request')


@router.get('')
async def list_assessments(request: Request, project_id: UUID):
    await _reject_empty_body(request)
    actor = _professional_read(request)
    config = request.app.state.config
    filters = _filters(request)
    scope = (f'assessments:{project_id}:{actor.issuer}:{actor.subject}:'
             f'{filters["participant_id"] or ""}:{filters["visit"] or ""}')
    limit, offset = _page(request, scope, config, FILTERS)
    try:
        items = application.assessments(config.read_database_url, project_id, actor,
                                       **filters, limit=limit + 1, offset=offset)
    except application.MissingError:
        raise APIError('not_found') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None
    return {'items': items[:limit],
            'next_cursor': _next_cursor(config, scope, offset + limit) if len(items) > limit else None}


@router.get('/{assessment_id}')
async def get_assessment(request: Request, project_id: UUID, assessment_id: str):
    await _reject_empty_body(request)
    _reject_query(request)
    actor = _professional_read(request)
    _identifier(assessment_id)
    try:
        return application.assessment(request.app.state.config.read_database_url,
                                      project_id, assessment_id, actor)
    except application.MissingError:
        raise APIError('not_found') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None


@router.get('/{assessment_id}/export')
async def export_assessment(request: Request, project_id: UUID, assessment_id: str):
    await _reject_empty_body(request)
    _reject_query(request)
    actor = _professional_read(request, 'export_dashboard')
    _identifier(assessment_id)
    try:
        filename, content = application.export_assessment(request.app.state.config.read_database_url,
                                                         project_id, assessment_id, actor)
    except application.MissingError:
        raise APIError('not_found') from None
    except application.UnsupportedExportError:
        raise APIError('invalid_request') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None
    return Response(content, media_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'})
