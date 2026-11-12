"""Consulta profissional com projecoes fechadas e exportacao minimizada."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from stroop.domain.auth import AppUser
from stroop.domain.web_export import export_filename, serialize_assessment_csv
from stroop.persistence import web_assessments as persistence
from stroop.persistence.auth import PersistenceError
from stroop.persistence.web_sessions import MissingError

SchemaError = persistence.SchemaError
SnapshotConflict = persistence.SnapshotConflict
FacetLimitError = persistence.FacetLimitError


def _base(item: dict) -> dict:
    return {
        **{key: item[key] for key in (
            'assessment_id', 'participant_id', 'visit', 'evaluator_id', 'platform',
            'test_code', 'test_version', 'protocol_id', 'app_version', 'summary')},
        'valid_for_result': item.get('valid_for_result', True),
        'invalidation_reason': item.get('invalidation_reason'),
        'created_at': persistence.iso_utc(item['created_at']),
        'started_at': persistence.iso_utc(item['started_at']),
    }


def assessments(database_url: str, project_id: UUID, actor: AppUser,
                *, participant_id: str | None, visit: str | None,
                limit: int, offset: int) -> list[dict]:
    allowed, items = persistence.list_assessments(
        database_url, project_id, actor.issuer, actor.subject,
        participant_id=participant_id, visit=visit, limit=limit, offset=offset,
    )
    if not allowed:
        raise MissingError
    return [_base(item) for item in items]


def assessments_page(database_url, project_id, actor, *, filters, limit, offset, snapshot=None):
    allowed, items, fingerprint = persistence.list_assessments(
        database_url, project_id, actor.issuer, actor.subject, filters=filters,
        limit=limit, offset=offset, snapshot=snapshot, include_snapshot=True)
    if not allowed:
        raise MissingError
    return [_base(item) for item in items], fingerprint


def options(database_url, project_id, actor, *, filters):
    allowed, result = persistence.assessment_options(database_url, project_id, actor.issuer, actor.subject, filters=filters)
    if not allowed:
        raise MissingError
    return result


def _record(database_url: str, project_id: UUID, assessment_id: str, actor: AppUser) -> dict:
    item = persistence.get_assessment(database_url, project_id, assessment_id,
                                      actor.issuer, actor.subject)
    if item is None:
        raise MissingError
    return item


def assessment(database_url: str, project_id: UUID, assessment_id: str, actor: AppUser) -> dict:
    item = _record(database_url, project_id, assessment_id, actor)
    if not item.get('valid_for_result', True):
        return {**_base(item), 'project_id': str(project_id),
                'session_id': str(item['session_id']), 'valid_for_result': False,
                'invalidation_reason': item['invalidation_reason'],
                'summary': None, 'metrics': [], 'trials': []}
    trials = []
    for source in item['trials']:
        trial = {key: source[key] for key in (
            'trial_number', 'condition_id', 'word', 'ink_color', 'condition',
            'correct_response', 'key_pressed', 'correct', 'error_type',
            'trial_start_ms', 'stimulus_onset_ms', 'stimulus_offset_ms', 'trial_end_ms',
            'key_at_ms', 'reaction_time_ms', 'reaction_time_seconds',
        )}
        trials.append(trial)
    return {
        **_base(item), 'project_id': str(project_id),
        'valid_for_result': item.get('valid_for_result', True),
        'invalidation_reason': item.get('invalidation_reason'),
        'session_id': str(item['session_id']) if item['session_id'] is not None else None,
        'completed_at': persistence.iso_utc(item['completed_at']),
        'metrics': item['metrics'], 'frame_period_ms': item['frame_period_ms'],
        'trials': trials,
    }


def export_aggregate(database_url, projects, actor, *, filters, view):
    from stroop.domain.web_aggregate_export import aggregate_filename, serialize_aggregate_csv
    try:
        filename = aggregate_filename(view['test_code'])
    except ValueError:
        raise UnsupportedExportError from None
    allowed, rows = persistence.aggregate_assessments(database_url, projects, actor.issuer, actor.subject,
                                                       filters=filters, view=view)
    if not allowed:
        raise MissingError
    projected = [{**_base(row), 'project_id': str(row['project_id']),
                  'project_code': row['project_code']} for row in rows]
    try:
        content = serialize_aggregate_csv(projected, test_code=view['test_code'])
    except (ValueError, TypeError, KeyError):
        raise PersistenceError from None
    return filename, content


def export_assessment(database_url: str, project_id: UUID, assessment_id: str,
                      actor: AppUser) -> tuple[str, str]:
    # Reconsulta e reautoriza a cada download, mesmo apos visualizar o detalhe.
    item = _record(database_url, project_id, assessment_id, actor)
    if not item.get('valid_for_result', True):
        raise MissingError
    if item['test_code'] != 'stroop_go_nogo_ptbr':
        raise UnsupportedExportError
    metadata = {
        'project': item['project_code'], 'participant_id': item['participant_id'],
        'visit': item['visit'], 'evaluator': item['evaluator_id'] or 'LEGADO_NAO_MAPEADO',
        'assessment_id': item['assessment_id'], 'assessment_date': item['assessment_date'],
        'started_at': persistence.iso_utc(item['started_at']), 'test_code': item['test_code'],
        'test_version': item['test_version'],
    }
    try:
        content = serialize_assessment_csv(metadata, item['trials'])
        filename = export_filename(metadata['started_at'], allow_naive=item['platform'] == 'psychopy')
    except (ValueError, TypeError, KeyError):
        raise PersistenceError from None
    return filename, content


class UnsupportedExportError(ValueError):
    """Instrumento sem contrato de CSV oficial Stroop."""


def session_status(database_url, project_id, session_id, actor):
    item = persistence.session_status(database_url,project_id,session_id,actor.issuer,actor.subject)
    if item is None:
        raise MissingError
    return item


def analysis_query(database_url, actor, *, query, filters, sort, offset, size, snapshot=None):
    """Projeção de A/T sem combinar métricas oficiais entre instrumentos."""
    from stroop.domain.stroop import expected_outcome
    allowed, rows, trials, content, sources = persistence.analysis_selection(
        database_url, [UUID(project) for project in query['projects']], actor.issuer, actor.subject,
        filters=filters, assessment_ids=query.get('assessment_ids'))
    if not allowed:
        raise MissingError
    if snapshot is not None and snapshot != content:
        raise SnapshotConflict
    # Métricas oficiais de TODA a avaliação já hidratadas pelo domínio, sem
    # calcular precisão/RT sobre o recorte de tentativas ou ler nomes.
    criteria = query['filters']
    def eligible(row):
        summary = row['summary']
        for lower, upper, field, factor in (
                ('accuracy_min', 'accuracy_max', 'accuracy', 1),
                ('rt_median_min_ms', 'rt_median_max_ms', 'response_time_seconds', 1000)):
            if lower not in criteria and upper not in criteria:
                continue
            value = summary.get(field)
            if value is None:
                if field == 'response_time_seconds' and criteria.get('include_null_rt', True):
                    continue
                return False
            if lower in criteria and value * factor < criteria[lower]:
                return False
            if upper in criteria and value * factor >= criteria[upper]:
                return False
        return criteria.get('include_null_rt', True) or summary.get('response_time_seconds') is not None
    rows = [row for row in rows if eligible(row)]
    selected_ids = {row['assessment_id'] for row in rows}
    if query.get('assessment_ids') is not None and not set(query['assessment_ids']) <= selected_ids:
        raise SnapshotConflict
    selected_trials = []
    for trial in trials:
        if trial['assessment_id'] not in selected_ids:
            continue
        if filters.get('condition') and trial['condition'] not in filters['condition']:
            continue
        if filters.get('response_type'):
            outcome = expected_outcome({'condition': trial['condition'], 'key_pressed': trial['key_pressed'] or ''})
            if outcome is None or outcome[2] not in filters['response_type']:
                continue
        selected_trials.append(trial)
    counts = {
        'participants': len({(str(row['project_id']), row['participant_id']) for row in rows}),
        'visits': len({(str(row['project_id']), row['participant_id'], row['visit']) for row in rows}),
        'assessments': len(rows), 'trials': len(selected_trials),
    }
    # Desempate estável; nenhuma identidade é unida por nome/código.
    rows.sort(key=lambda row: (str(row['project_id']), row['assessment_id']))
    def date_key(row):
        value = datetime.fromisoformat(persistence.iso_utc(row['started_at']).replace('Z', '+00:00'))
        # iso_utc normaliza valores com fuso e preserva legado sem fuso.
        return (value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond)
    key = {'participant_code_asc': lambda row: row['participant_id'],
           'participant_code_desc': lambda row: row['participant_id'],
           'visit_asc': lambda row: row['visit']}.get(sort, date_key)
    if sort.startswith(('accuracy_', 'response_time_')):
        field = 'accuracy' if sort.startswith('accuracy_') else 'response_time_seconds'
        # Ausentes sempre ao fim, em ambas as direções; preserva desempate.
        present = [row for row in rows if row['summary'].get(field) is not None]
        absent = [row for row in rows if row['summary'].get(field) is None]
        present.sort(key=lambda row: row['summary'][field], reverse=sort.endswith('_desc'))
        rows = present + absent
    else:
        rows.sort(key=key, reverse=sort.endswith('_desc'))
    aggregates = []
    for project in query['projects']:
        scoped = [row for row in rows if str(row['project_id']) == project]
        ids = {row['assessment_id'] for row in scoped}
        aggregates.append({'project_id': project, 'assessments': len(scoped),
                           'trials': sum(trial['assessment_id'] in ids for trial in selected_trials)})
    return {'content_fingerprint': content, 'legacy_snapshots': sources, 'counts': counts, 'aggregates': aggregates,
            'items': [{**_base(row), 'project_id': str(row['project_id'])} for row in rows[offset:offset + size]]}
