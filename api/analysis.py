"""Entrada normalizada de consulta; capacidades parciais explícitas de CHG-007."""
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Literal
from uuid import UUID, uuid4
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from pydantic import Field

from api.assessments import _filters, _signed, _verified
from api.errors import APIError
from api.models import RequestModel
from api.sessions import _professional_write, _reject_query
from stroop.application import web_assessments as application

router = APIRouter(prefix='/api/v1/analysis', tags=['analysis'])


class QueryFilters(RequestModel):
    date_from: str | None = None
    date_to: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    participant_code: list[str] = Field(default_factory=list, max_length=100)
    participant_id: list[str] = Field(default_factory=list, max_length=100)
    visit: list[str] = Field(default_factory=list, max_length=100)
    evaluator_id: list[str] = Field(default_factory=list, max_length=100)
    test_code: list[str] = Field(default_factory=list, max_length=100)
    test_version: list[str] = Field(default_factory=list, max_length=100)
    platform: list[Literal['web', 'psychopy', 'psychopy_local']] = Field(default_factory=list, max_length=100)
    condition: list[Literal['congruent', 'incongruent']] = Field(default_factory=list, max_length=100)
    response_type: list[Literal['hit', 'omission', 'commission', 'correct_rejection']] = Field(default_factory=list, max_length=100)
    status: Literal['valid'] = 'valid'


class QuerySelection(RequestModel):
    projects: list[str] = Field(min_length=1, max_length=20)
    filters: QueryFilters
    assessment_ids: list[str] | None = Field(default=None, max_length=5000)


class Grouping(RequestModel):
    # Demais agrupamentos/métricas serão habilitados com o seletor WEB-051/052.
    level: Literal['assessment']
    dimension: Literal['project']


class QueryPage(RequestModel):
    size: int = Field(default=50, ge=1, le=100)
    cursor: str | None = Field(default=None, pattern=r'^[A-Za-z0-9_-]{1,1024}$')
    sort: Literal['started_at_desc', 'started_at_asc', 'participant_code_asc', 'visit_asc'] = 'started_at_desc'


class AnalysisRequest(RequestModel):
    query: QuerySelection
    grouping: Grouping
    page: QueryPage


def normalize(selection: QuerySelection):
    """Normaliza aliases na borda e reutiliza a validação das dimensões existentes."""
    try:
        projects = sorted(str(UUID(value)) for value in selection.projects)
    except ValueError:
        raise APIError('invalid_request') from None
    if len(set(projects)) != len(projects):
        raise APIError('invalid_request')
    raw = selection.filters.model_dump(exclude_none=True)
    raw.pop('status')
    if any(raw.get(key) == '' for key in ('date_from', 'date_to', 'start_date', 'end_date')):
        raise APIError('invalid_request')
    for alias, canonical in [('start_date', 'date_from'), ('end_date', 'date_to'), ('participant_id', 'participant_code')]:
        first, second = raw.pop(alias, None), raw.get(canonical)
        if first and second and (sorted(set(first)) if isinstance(first, list) else first) != (sorted(set(second)) if isinstance(second, list) else second):
            raise APIError('invalid_request')
        if first and not second:
            raw[canonical] = first
    normalized = {'status': 'valid'}
    legacy = {}
    aliases = {'date_from': 'start_date', 'date_to': 'end_date', 'participant_code': 'participant_id'}
    for key, value in raw.items():
        if not value:
            continue
        if isinstance(value, list):
            value = sorted(set('psychopy_local' if key == 'platform' and item == 'psychopy' else item for item in value))
        normalized[key] = value
        legacy[aliases.get(key, key)] = ['psychopy' if item == 'psychopy_local' else item for item in value] if key == 'platform' else value
    # Não reproduzir regex/allowlists das rotas existentes.
    validation_request = Request({'type': 'http', 'query_string': urlencode(legacy, doseq=True).encode()})
    filters = _filters(validation_request)
    query = {'projects': projects, 'filters': normalized}
    if selection.assessment_ids is not None:
        if any(not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', value) for value in selection.assessment_ids):
            raise APIError('invalid_request')
        query['assessment_ids'] = sorted(set(selection.assessment_ids))
    return query, filters


def _fingerprint(config, value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hmac.new(config.session_secret.encode(), b'analysis-query-v1\0' + data, hashlib.sha256).hexdigest()


@router.post('/query')
async def analysis_query(request: Request, body: AnalysisRequest):
    _reject_query(request)
    actor = _professional_write(request, 'view_dashboard')
    query, filters = normalize(body.query)
    config = request.app.state.config
    fingerprint = _fingerprint(config, query)
    scope = json.dumps(['analysis-page-v1', actor.issuer, actor.subject, fingerprint, body.page.sort], separators=(',', ':'))
    now = int(datetime.now(timezone.utc).timestamp())
    query_id, offset, expected, expires = str(uuid4()), 0, None, now + 900
    if body.page.cursor:
        claims = _verified(config, scope, body.page.cursor)
        if (not isinstance(claims, list) or len(claims) != 4
                or not isinstance(claims[0], str) or not re.fullmatch(r'[a-f0-9-]{36}', claims[0])
                or type(claims[1]) is not int or not 0 <= claims[1] <= 5000
                or not isinstance(claims[2], str) or not re.fullmatch(r'[a-f0-9]{64}', claims[2])
                or type(claims[3]) is not int):
            raise APIError('invalid_request')
        query_id, offset, expected, expires = claims
        if expires <= now:
            raise APIError('state_conflict')
    try:
        result = application.analysis_query(config.read_database_url, actor, query=query, filters=filters,
                                            sort=body.page.sort, offset=offset, size=body.page.size, snapshot=expected)
    except application.MissingError:
        raise APIError('not_found') from None
    except application.SnapshotConflict:
        raise APIError('state_conflict') from None
    except application.FacetLimitError:
        raise APIError('invalid_request') from None
    except (application.SchemaError, application.PersistenceError):
        raise APIError('service_unavailable') from None
    content = result.pop('content_fingerprint')
    more = offset + body.page.size < result['counts']['assessments']
    return {
        'query_id': query_id, 'normalized_query': query, 'query_fingerprint': fingerprint,
        'content_fingerprint': content, 'expires_at': datetime.fromtimestamp(expires, timezone.utc).isoformat().replace('+00:00', 'Z'),
        'completeness': 'complete', **result,
        'next_cursor': _signed(config, scope, [query_id, offset + body.page.size, content, expires]) if more else None,
        'indicator_definitions': {'counts': {'kind': 'operational_count', 'population': 'official_assessments_and_main_trials', 'timezone': 'UTC',
                                            'participant_identity': ['project_id', 'participant_code'],
                                            'visit_identity': ['project_id', 'participant_code', 'visit']},
                                  'summary': {'source': 'stroop.domain.stroop.calculate_metrics', 'population': 'complete_assessment', 'rt_unit': 'seconds'}},
        'capabilities': {'filters': ['date_from', 'date_to', 'participant_code', 'visit', 'evaluator_id', 'test_code', 'test_version', 'platform', 'status'],
                         'status': ['valid'], 'trial_filters': {'stroop_go_nogo_ptbr': ['condition', 'response_type']},
                         'grouping': [{'level': 'assessment', 'dimension': 'project'}],
                         'sort': ['started_at_desc', 'started_at_asc', 'participant_code_asc', 'visit_asc'],
                         'platform': ['web', 'psychopy_local'], 'max_assessments': 5000, 'max_projects': 20,
                         'exports': False, 'nominal_search': False},
    }
