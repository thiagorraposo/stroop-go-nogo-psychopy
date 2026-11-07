"""Recepcao incremental, conclusao atomica e invalidacao auditavel WEB."""

import math
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import StrictFloat, StrictInt, ValidationError

from api.errors import APIError
from api.models import RequestModel
from api.sessions import _load_conditions, _participant_write, _reject_query, _professional_write
from stroop.application import web_results as application


router = APIRouter(prefix='/api/v1', tags=['results'])
Numeric = StrictFloat | StrictInt


class TrialResult(RequestModel):
    trial_number: StrictInt
    condition_id: StrictInt
    key_pressed: str | None
    reaction_time_ms: Numeric | None
    trial_start_ms: Numeric
    stimulus_onset_ms: Numeric
    stimulus_offset_ms: Numeric
    trial_end_ms: Numeric
    key_at_ms: Numeric | None


class Complete(RequestModel):
    protocol_id: str
    test_version: str
    platform: str
    app_version: str
    frame_period_ms: Numeric
    trials: list[TrialResult]


@router.post('/participant/complete')
async def complete(request: Request):
    _reject_query(request)
    _, token_hash = _participant_write(request)
    payload = await request.json()
    try:
        receipt, created = application.complete(
            request.app.state.config.database_url, token_hash,
            payload, _load_conditions('main'), validate_schema=Complete.model_validate,
        )
    except ValidationError:
        raise APIError('invalid_request') from None
    except application.InvalidResultError:
        raise APIError('invalid_result') from None
    except application.ResultConflictError:
        raise APIError('result_conflict') from None
    except application.ConflictError:
        raise APIError('state_conflict') from None
    except application.ExpiredError:
        raise APIError('session_expired') from None
    except application.UnknownCredentialError:
        raise APIError('authentication_required') from None
    except application.MissingError:
        raise APIError('not_found') from None
    except application.PersistenceError:
        raise APIError('service_unavailable') from None
    return JSONResponse(receipt, status_code=201 if created else 200)


class Invalidate(RequestModel):
    reason: Literal['focus_lost','visibility_hidden','escape','reload','page_closed',
                    'timing_invalid','user_cancelled']
    event_at_ms: Numeric | None


def _incremental_operation(operation):
    try:
        return operation()
    except ValidationError:
        raise APIError('invalid_request') from None
    except application.InvalidResultError:
        raise APIError('invalid_result') from None
    except application.ResultConflictError:
        raise APIError('result_conflict') from None
    except application.ConflictError:
        raise APIError('state_conflict') from None
    except application.ExpiredError:
        raise APIError('session_expired') from None
    except application.UnknownCredentialError:
        raise APIError('authentication_required') from None
    except application.MissingError:
        raise APIError('not_found') from None
    except application.PersistenceError:
        raise APIError('service_unavailable') from None


@router.post('/participant/session/checkpoints')
async def checkpoint(request: Request):
    _reject_query(request)
    _, token_hash = _participant_write(request)
    payload = await request.json()
    return _incremental_operation(lambda: application.checkpoint(
        request.app.state.config.database_url, token_hash, payload, _load_conditions('main'),
        validate_schema=Complete.model_validate,
    ))


def _event(body):
    try:
        valid = body.event_at_ms is None or (math.isfinite(body.event_at_ms) and body.event_at_ms >= 0)
    except OverflowError:
        valid = False
    if not valid:
        raise APIError('invalid_request')


@router.post('/participant/session/invalidate')
async def invalidate(request: Request, body: Invalidate):
    _reject_query(request)
    _, token_hash = _participant_write(request)
    _event(body)
    return _incremental_operation(lambda: application.invalidate(
        request.app.state.config.database_url, token_hash, body.reason, body.event_at_ms,
    ))


@router.post('/projects/{project_id}/sessions/{session_id}/invalidate')
async def invalidate_professional(project_id: UUID, session_id: UUID, request: Request, body: Invalidate):
    _reject_query(request)
    actor = _professional_write(request, 'view_dashboard')
    _event(body)
    return _incremental_operation(lambda: application.invalidate_professional(
        request.app.state.config.database_url, project_id, session_id, actor,
        body.reason, body.event_at_ms,
    ))


@router.get('/projects/{project_id}/sessions/{session_id}')
async def session_status(project_id: UUID, session_id: UUID, request: Request):
    from api.sessions import _professional_read, _reject_empty_body
    from stroop.application import web_assessments
    _reject_query(request)
    await _reject_empty_body(request)
    actor = _professional_read(request)
    try:
        return web_assessments.session_status(request.app.state.config.read_database_url,
                                              project_id,session_id,actor)
    except application.MissingError:
        raise APIError('not_found') from None
    except (web_assessments.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None
