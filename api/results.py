"""Conclusao de uma execucao WEB completa e recuperacao idempotente do recibo."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import StrictFloat, StrictInt, ValidationError

from api.errors import APIError
from api.models import RequestModel
from api.sessions import _load_conditions, _participant_write, _reject_query
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
