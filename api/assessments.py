"""Consulta e exportacao profissional sob escopo de projeto."""
import re
import base64
import hashlib
import hmac
import json
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from api.errors import APIError
from api.models import RequestModel
from api.sessions import (
    _professional_read, _professional_write, _reject_empty_body, _reject_query,
)
from stroop.application import web_assessments as application

router = APIRouter(prefix='/api/v1/projects/{project_id}/assessments', tags=['assessments'])
export_router = APIRouter(prefix='/api/v1/assessments', tags=['assessments'])
MULTI = frozenset({'participant_id', 'visit', 'evaluator_id', 'test_version', 'platform', 'test_code', 'condition', 'response_type'})
TRIAL_VALUES = {
    'condition': frozenset({'congruent', 'incongruent'}),
    'response_type': frozenset({'hit', 'omission', 'commission', 'correct_rejection'}),
}
SINGLE = frozenset({'start_date', 'end_date'})
FILTERS = MULTI | SINGLE
LABEL = re.compile(r'^[A-Za-z0-9_.-]{1,64}$')


def _filters(request, *, options=False):
    allowed = SINGLE | {'test_code'} if options else FILTERS | {'limit', 'cursor'}
    if set(request.query_params) - allowed:
        raise APIError('invalid_request')
    result = {}
    for key in request.query_params:
        values = request.query_params.getlist(key)
        if (key not in MULTI or options) and len(values) != 1:
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
            elif key in TRIAL_VALUES:
                valid = all(value in TRIAL_VALUES[key] for value in values)
            elif key == 'platform':
                valid = all(value in ('web', 'psychopy') for value in values)
            else:
                valid = all(re.fullmatch(pattern, value) for value in values)
            if not valid:
                raise APIError('invalid_request')
            normalized = sorted(set(values))
            # Preserve the canonical scope of existing single-instrument snapshots.
            result[key] = normalized[0] if key == 'test_code' and len(normalized) == 1 else normalized
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
    if any(result.get(key) for key in TRIAL_VALUES):
        # Explicit instrument capability: never silently ignore trial filters.
        if result.get('test_code') != 'stroop_go_nogo_ptbr':
            raise APIError('invalid_request')
    return result


def _signed(config, scope, payload):
    data = json.dumps(payload, separators=(',', ':')).encode()
    signature = hmac.new(config.session_secret.encode(), scope.encode() + b'\0' + data, hashlib.sha256).hexdigest().encode()
    return base64.urlsafe_b64encode(data + b'.' + signature).rstrip(b'=').decode()


def _verified(config, scope, token):
    try:
        data, signature = base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).rsplit(b'.', 1)
        expected = hmac.new(config.session_secret.encode(), scope.encode() + b'\0' + data, hashlib.sha256).hexdigest().encode()
        if not hmac.compare_digest(signature, expected): raise ValueError
        return json.loads(data)
    except (ValueError, TypeError, UnicodeError):
        raise APIError('invalid_request') from None


def _cursor(config, scope, offset, snapshot, expires):
    return _signed(config, scope, [offset, snapshot, expires])


def _pagination(request, config, scope):
    raw = request.query_params.get('limit', '25')
    if not raw.isascii() or not raw.isdigit() or len(raw) > 3 or not 1 <= int(raw) <= 100:
        raise APIError('invalid_request')
    cursor = request.query_params.get('cursor')
    if cursor is None:
        return int(raw), 0, None, None
    try:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,512}', cursor):
            raise ValueError
        data, signature = base64.urlsafe_b64decode(cursor + '=' * (-len(cursor) % 4)).rsplit(b'.', 1)
        expected = hmac.new(config.session_secret.encode(), scope.encode() + b'\0' + data, hashlib.sha256).hexdigest().encode()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        offset, snapshot, expires = json.loads(data)
        if type(offset) is not int or not 0 <= offset <= 5000 or not re.fullmatch(r'[a-f0-9]{64}', snapshot) or type(expires) is not int:
            raise ValueError
        if expires < int(datetime.now(timezone.utc).timestamp()): raise APIError('state_conflict')
        return int(raw), offset, snapshot, expires
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
    limit, offset, snapshot, expires = _pagination(request, config, scope)
    if expires is None: expires = int(datetime.now(timezone.utc).timestamp()) + 900
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
    token_scope = json.dumps(['assessment-snapshot-v1', str(project_id), actor.issuer, actor.subject, filters], sort_keys=True)
    token = _signed(config, token_scope, [fingerprint, expires])
    return JSONResponse({'items': items[:limit], 'next_cursor': _cursor(config, scope, offset + limit, fingerprint, expires) if len(items) > limit else None},
                        headers={'X-Assessment-Snapshot': token, 'Cache-Control': 'no-store'})


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


class RelinkAssessmentRequest(RequestModel):
    patient_id: str | None = None
    evaluator_id: str | None = None
    reason_code: str


@router.post('/{assessment_id}/relink')
async def relink_assessment(
    request: Request,
    project_id: UUID,
    assessment_id: str,
    body: RelinkAssessmentRequest,
):
    _reject_query(request)
    actor = _professional_write(request, 'manage_patients')
    _identifier(assessment_id)
    patient_uuid: UUID | None = None
    evaluator_uuid: UUID | None = None
    try:
        if body.patient_id is not None:
            patient_uuid = UUID(body.patient_id)
        if body.evaluator_id is not None:
            evaluator_uuid = UUID(body.evaluator_id)
    except ValueError:
        raise APIError('invalid_request') from None
    from stroop.application import web_registry
    try:
        return web_registry.relink_assessment(
            request.app.state.config.database_url,
            actor,
            project_id=project_id,
            assessment_id=assessment_id,
            patient_id=patient_uuid,
            evaluator_id=evaluator_uuid,
            reason_code=body.reason_code,
        )
    except web_registry.InvalidRegistryDataError:
        raise APIError('invalid_request') from None
    except web_registry.ForbiddenRegistryError:
        raise APIError('permission_denied') from None
    except web_registry.MissingRegistryError:
        raise APIError('not_found') from None
    except web_registry.PersistenceError:
        raise APIError('service_unavailable') from None


@export_router.post('/export')
async def export_assessment_view(request: Request):
    actor = _professional_write(request, 'export_dashboard')
    try:
        body = await request.json()
    except Exception:
        raise APIError('invalid_request') from None
    if not isinstance(body, dict) or set(body) != {'projects', 'filters', 'view'}:
        raise APIError('invalid_request')
    projects_raw, filters_raw, view = body['projects'], body['filters'], body['view']
    if not isinstance(projects_raw, list) or not 1 <= len(projects_raw) <= 20 or not isinstance(filters_raw, dict):
        raise APIError('invalid_request')
    if set(filters_raw) & TRIAL_VALUES.keys():
        # Legacy aggregate export has no trial-subset contract.
        raise APIError('invalid_request')
    try:
        filters = {}
        for key, value in filters_raw.items():
            if key in MULTI:
                if not isinstance(value, list) and not (key == 'test_code' and isinstance(value, str)): raise ValueError
                filters[key] = value
            elif key in SINGLE:
                filters[key] = value
            else: raise ValueError
        encoded = []
        for key, value in filters.items():
            for item in value if isinstance(value, list) else [value]:
                from urllib.parse import quote
                encoded.append(f'{quote(key)}={quote(item)}')
        scope_request = Request({**request.scope, 'query_string': '&'.join(encoded).encode()})
        filters = _filters(scope_request)
        if not isinstance(view, dict) or set(view) - {'test_code', 'platform'} or 'test_code' not in view:
            raise ValueError
        if not isinstance(view['test_code'], str) or view['test_code'] not in ('stroop_go_nogo_ptbr', 'instrumento_sintetico_demo'):
            raise ValueError
        if 'platform' in view and view['platform'] not in ('web', 'psychopy'): raise ValueError
        projects = []
        expiry_now = int(datetime.now(timezone.utc).timestamp())
        for entry in projects_raw:
            if not isinstance(entry, dict) or set(entry) != {'project_id', 'snapshot'}: raise ValueError
            project_id = UUID(entry['project_id'])
            token = entry['snapshot']
            if not isinstance(token, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,1024}', token): raise ValueError
            token_scope = json.dumps(['assessment-snapshot-v1', str(project_id), actor.issuer, actor.subject, filters], sort_keys=True)
            claims = _verified(request.app.state.config, token_scope, token)
            if not isinstance(claims, list) or len(claims) != 2 or not re.fullmatch(r'[a-f0-9]{64}', claims[0]) or type(claims[1]) is not int:
                raise ValueError
            if claims[1] < expiry_now: raise APIError('state_conflict')
            projects.append((project_id, claims[0]))
        if len({project_id for project_id, _ in projects}) != len(projects): raise ValueError
    except APIError:
        raise
    except (ValueError, TypeError, AttributeError):
        raise APIError('invalid_request') from None
    try:
        filename, content = application.export_aggregate(request.app.state.config.read_database_url,
            projects, actor, filters=filters, view=view)
    except application.MissingError:
        raise APIError('not_found') from None
    except application.SnapshotConflict:
        raise APIError('state_conflict') from None
    except application.FacetLimitError:
        raise APIError('invalid_request') from None
    except application.UnsupportedExportError:
        raise APIError('invalid_request') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None
    return Response(content, media_type='text/csv; charset=utf-8', headers={
        'Content-Disposition': f'attachment; filename="{filename}"', 'Cache-Control': 'no-store',
    })
