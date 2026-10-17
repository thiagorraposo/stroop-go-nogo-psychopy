"""Consulta e exportacao profissional sob escopo de projeto."""
import re
import base64
import hashlib
import hmac
import json
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import Response

from api.errors import APIError
from api.sessions import (
    _professional_read, _reject_empty_body, _reject_query,
)
from stroop.application import web_assessments as application

router = APIRouter(prefix='/api/v1/projects/{project_id}/assessments', tags=['assessments'])
MULTI = frozenset({'participant_id', 'visit', 'evaluator_id', 'test_version', 'platform'})
SINGLE = frozenset({'start_date', 'end_date', 'test_code'})
FILTERS = MULTI | SINGLE
LABEL = re.compile(r'^[A-Za-z0-9_.-]{1,64}$')


def _filters(request, *, options=False):
    allowed = SINGLE if options else FILTERS | {'limit', 'cursor'}
    if set(request.query_params) - allowed:
        raise APIError('invalid_request')
    result = {}
    for key in request.query_params:
        values = request.query_params.getlist(key)
        if key not in MULTI and len(values) != 1:
            raise APIError('invalid_request')
        if key in {'cursor', 'limit'}:
            continue
        if key in MULTI:
            if len(values) > 100 or any(not value for value in values):
                raise APIError('invalid_request')
            pattern = (r'^[A-Za-z0-9_-]{1,512}$' if key == 'evaluator_id' else
                       r'^[A-Za-z0-9_.+-]{1,64}$' if key == 'test_version' else LABEL.pattern)
            if key in ('participant_id', 'visit'):
                valid = all(1 <= len(value) <= 512 and value.strip() and not re.search(r'[\x00-\x1f\x7f]', value) for value in values)
            elif key == 'platform':
                valid = all(value in ('web', 'psychopy') for value in values)
            else:
                valid = all(re.fullmatch(pattern, value) for value in values)
            if not valid:
                raise APIError('invalid_request')
            result[key] = sorted(set(values))
        elif key in ('start_date', 'end_date'):
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', values[0]):
                    raise ValueError
                date.fromisoformat(values[0])
            except ValueError:
                raise APIError('invalid_request') from None
            result[key] = values[0]
        elif not LABEL.fullmatch(values[0]):
            raise APIError('invalid_request')
        else:
            result[key] = values[0]
    if result.get('start_date', '') > result.get('end_date', '9999-12-31'):
        raise APIError('invalid_request')
    return result


def _cursor(config, scope, offset, snapshot):
    data = json.dumps([offset, snapshot], separators=(',', ':')).encode()
    signature = hmac.new(config.session_secret.encode(), scope.encode() + b'\0' + data, hashlib.sha256).hexdigest().encode()
    return base64.urlsafe_b64encode(data + b'.' + signature).rstrip(b'=').decode()


def _pagination(request, config, scope):
    raw = request.query_params.get('limit', '25')
    if not raw.isascii() or not raw.isdigit() or len(raw) > 3 or not 1 <= int(raw) <= 100:
        raise APIError('invalid_request')
    cursor = request.query_params.get('cursor')
    if cursor is None:
        return int(raw), 0, None
    try:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,512}', cursor):
            raise ValueError
        data, signature = base64.urlsafe_b64decode(cursor + '=' * (-len(cursor) % 4)).rsplit(b'.', 1)
        expected = hmac.new(config.session_secret.encode(), scope.encode() + b'\0' + data, hashlib.sha256).hexdigest().encode()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        offset, snapshot = json.loads(data)
        if type(offset) is not int or not 0 <= offset <= 5000 or not re.fullmatch(r'[a-f0-9]{64}', snapshot):
            raise ValueError
        return int(raw), offset, snapshot
    except (ValueError, TypeError, UnicodeError):
        raise APIError('invalid_request') from None


def _identifier(value: str) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', value):
        raise APIError('invalid_request')


@router.get('')
async def list_assessments(request: Request, project_id: UUID):
    await _reject_empty_body(request)
    actor = _professional_read(request)
    config = request.app.state.config
    filters = _filters(request)
    scope = json.dumps(['assessments-v2', str(project_id), actor.issuer, actor.subject, filters], sort_keys=True)
    limit, offset, snapshot = _pagination(request, config, scope)
    try:
        items, fingerprint = application.assessments_page(config.read_database_url, project_id, actor,
            filters=filters, limit=limit + 1, offset=offset, snapshot=snapshot)
    except application.MissingError:
        raise APIError('not_found') from None
    except application.SnapshotConflict:
        raise APIError('state_conflict') from None
    except application.FacetLimitError:
        raise APIError('invalid_request') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None
    return {'items': items[:limit], 'next_cursor': _cursor(config, scope, offset + limit, fingerprint) if len(items) > limit else None}


@router.get('/options')
async def assessment_options(request: Request, project_id: UUID):
    await _reject_empty_body(request)
    actor = _professional_read(request)
    filters = _filters(request, options=True)
    try:
        return application.options(request.app.state.config.read_database_url, project_id, actor, filters=filters)
    except application.MissingError:
        raise APIError('not_found') from None
    except application.FacetLimitError:
        raise APIError('invalid_request') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None


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
