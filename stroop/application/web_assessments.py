"""Consulta profissional com projecoes fechadas e exportacao minimizada."""
from __future__ import annotations

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
