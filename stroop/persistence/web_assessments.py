"""Consultas somente leitura de avaliacoes WEB e legadas autorizadas."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
import math
import hashlib
import json
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from stroop.persistence.auth import PersistenceError
from stroop.domain.stroop import ALLOWED_CONDITIONS, ALLOWED_KEYS, calculate_metrics, expected_outcome


REQUIRED_COLUMNS = {
    "assessments": {
        "assessment_id", "test_code", "test_version", "project", "participant_id",
        "visit", "evaluator", "assessment_date",
        "started_at", "imported_at", "import_status",
    },
    "assessment_metrics": {
        "assessment_id", "metric_code", "metric_label", "metric_value", "unit",
    },
    "trial_results": {
        "assessment_id", "block", "trial_number", "word", "ink_color", "condition",
        "correct_response", "key_pressed", "reaction_time", "correct", "error_type",
    },
    "web_projects": {"project_id", "code", "active"},
    "web_legacy_project_links": {"legacy_project", "project_id", "active"},
    "web_csv_imports": {"operation_id", "project_id", "status", "assessment_id"},
    "web_project_members": {"project_id", "issuer", "subject", "active"},
    "app_users": {"issuer", "subject", "role", "active"},
    "web_assessments": {
        "assessment_id", "session_id", "project_id", "platform", "protocol_id",
        "app_version", "frame_period_ms", "completed_at",
    },
    "web_session_invalidations": {"session_id", "reason", "recorded_at", "source", "event_at_ms"},
    "web_session_checkpoints": {"session_id", "confirmed_through", "prefix_hash", "received_at"},
    "web_participant_sessions": {"session_id", "state", "expires_at", "abort_reason", "revoked_at"},
    "web_invitations": {"session_id", "project_id", "revoked_at"},
    "web_trial_observations": {
        "assessment_id", "trial_number", "condition_id", "trial_start_ms",
        "stimulus_onset_ms", "stimulus_offset_ms", "trial_end_ms", "key_at_ms",
        "reaction_time_ms",
    },
}


class SchemaError(Exception):
    """Schema indisponivel ou incompativel com a consulta WEB."""


def _connect(database_url: str):
    if not database_url:
        raise PersistenceError("Credencial somente leitura nao configurada.")
    connection = None
    try:
        connection = psycopg.connect(database_url, connect_timeout=5, row_factory=dict_row)
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        return connection
    except psycopg.Error as exc:
        if connection is not None:
            connection.close()
        raise PersistenceError from exc


def _validate_schema(connection) -> None:
    try:
        missing_tables: list[str] = []
        missing_columns: list[str] = []
        for table, expected in REQUIRED_COLUMNS.items():
            actual = {
                row["column_name"] for row in connection.execute(
                    """SELECT column_name FROM information_schema.columns
                       WHERE table_schema='public' AND table_name=%s""", (table,)
                ).fetchall()
            }
            if not actual:
                missing_tables.append(table)
            elif expected - actual:
                missing_columns.append(f"{table}: {', '.join(sorted(expected - actual))}")
        if missing_tables or missing_columns:
            raise SchemaError
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _authorized_project(connection, project_id: UUID, issuer: str, subject: str) -> bool:
    row = connection.execute(
        """SELECT 1 FROM web_projects p
           JOIN web_project_members m ON m.project_id=p.project_id
           JOIN app_users u ON (u.issuer,u.subject)=(m.issuer,m.subject)
           WHERE p.project_id=%s AND p.active AND m.active AND u.active
             AND m.issuer=%s AND m.subject=%s
             AND u.role IN ('consulta','importacao','administracao')""",
        (project_id, issuer, subject),
    ).fetchone()
    return row is not None


def _base_query(where_clause: str, *, history=False) -> str:
    # where_clause is selected only from the fixed call sites below.
    valid_clause = "" if history else "AND NOT EXISTS (SELECT 1 FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id)"
    return f"""SELECT a.assessment_id, a.participant_id, a.visit, p.code AS project_code,
                      CASE WHEN wa.assessment_id IS NULL THEN NULL ELSE a.evaluator END AS evaluator_id,
                      COALESCE(wa.completed_at, a.imported_at::timestamptz) AS created_at,
                      a.started_at, COALESCE(wa.platform, 'psychopy') AS platform,
                      a.test_code, a.test_version, wa.protocol_id, wa.app_version,
                      wa.session_id, wa.completed_at, wa.frame_period_ms,
                      a.assessment_date, a.import_status,
                      NOT EXISTS (SELECT 1 FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id) AS valid_for_result,
                      (SELECT inv.reason FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id) AS invalidation_reason
               FROM assessments a
               LEFT JOIN web_assessments wa ON wa.assessment_id=a.assessment_id
               LEFT JOIN web_csv_imports wi ON wi.assessment_id=a.assessment_id AND wi.status='importado'
               JOIN web_projects p ON p.project_id=%s
                 AND ((wa.assessment_id IS NOT NULL AND wa.project_id=p.project_id)
                   OR (wi.assessment_id IS NOT NULL AND wi.project_id=p.project_id)
                   OR (wa.assessment_id IS NULL AND wi.assessment_id IS NULL AND EXISTS (
                     SELECT 1 FROM web_legacy_project_links lp
                     WHERE lp.project_id=p.project_id AND lp.legacy_project=a.project AND lp.active
                   )))
               JOIN web_project_members m ON m.project_id=p.project_id
                 AND m.issuer=%s AND m.subject=%s AND m.active
               JOIN app_users u ON (u.issuer,u.subject)=(m.issuer,m.subject)
                 AND u.active AND u.role IN ('consulta','importacao','administracao')
               WHERE p.active AND a.import_status='valid' {valid_clause} {where_clause}"""


class SnapshotConflict(Exception):
    """Conjunto mudou entre paginas."""


class FacetLimitError(Exception):
    """Opcoes excederam limite explicito."""


def _filters(filters):
    clauses, values = [], []
    columns = {'participant_id': 'a.participant_id', 'visit': 'a.visit', 'test_version': 'a.test_version',
               'platform': "COALESCE(wa.platform,'psychopy')",
               'evaluator_id': "COALESCE(CASE WHEN wa.assessment_id IS NULL THEN NULL ELSE a.evaluator END,'LEGADO_NAO_MAPEADO')"}
    for key, column in columns.items():
        if filters.get(key):
            clauses.append(f'AND {column}=ANY(%s)')
            values.append(list(filters[key]))
    for key, operator in [('start_date', '>='), ('end_date', '<=')]:
        if filters.get(key):
            clauses.append(f'AND a.assessment_date {operator} %s')
            values.append(filters[key])
    if filters.get('test_code'):
        clauses.append('AND a.test_code=ANY(%s)')
        instruments = filters['test_code']
        values.append([instruments] if isinstance(instruments, str) else list(instruments))
    if filters.get('condition') or filters.get('response_type'):
        # Resolve outcome categories through the official domain. One EXISTS
        # requires condition AND response on the SAME main trial; metrics below
        # continue to hydrate the full assessment.
        conditions = filters.get('condition') or ALLOWED_CONDITIONS
        responses = filters.get('response_type')
        pairs = []
        for condition in sorted(ALLOWED_CONDITIONS):
            for key in sorted(ALLOWED_KEYS):
                outcome = expected_outcome({'condition': condition, 'key_pressed': key})
                if outcome and condition in conditions and (not responses or outcome[2] in responses):
                    pairs.append((condition, key))
        if not pairs:
            clauses.append('AND FALSE')
        else:
            alternatives = " OR ".join("(tr.condition=%s AND COALESCE(tr.key_pressed,'')=%s)" for _ in pairs)
            clauses.append("AND EXISTS (SELECT 1 FROM trial_results tr WHERE tr.assessment_id=a.assessment_id "
                           "AND tr.block='main' AND (" + alternatives + '))')
            values.extend(value for pair in pairs for value in pair)
    return ' '.join(clauses), values


def assessment_options(database_url, project_id, issuer, subject, *, filters):
    try:
        with _connect(database_url) as connection:
            _validate_schema(connection)
            if not _authorized_project(connection, project_id, issuer, subject):
                return False, {}
            where, values = _filters(filters)
            base = _base_query(where)
            result = {}
            for key in ('participant_id', 'visit', 'evaluator_id', 'test_version', 'platform', 'test_code'):
                expression = "COALESCE(evaluator_id,'LEGADO_NAO_MAPEADO')" if key == 'evaluator_id' else key
                rows = connection.execute(f'SELECT DISTINCT {expression} AS value FROM ({base}) scoped ORDER BY value LIMIT 201',
                                          (project_id, issuer, subject, *values)).fetchall()
                if len(rows) > 200:
                    raise FacetLimitError
                result[key] = [row['value'] for row in rows]
            return True, result
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _scoped_query(project_id, issuer, subject, filters, participant_id=None, visit=None):
    clauses, params = [], [project_id, issuer, subject]
    for column, value in (('participant_id', participant_id), ('visit', visit)):
        if value is not None:
            clauses.append(f'AND a.{column}=%s')
            params.append(value)
    where, values = _filters(filters)
    return _base_query(' '.join(clauses) + ' ' + where), [*params, *values]


def _snapshot(connection, base, params):
    entries = connection.execute('SELECT * FROM (' + base + ') scoped ORDER BY assessment_id LIMIT 5001', params).fetchall()
    if len(entries) > 5000:
        raise FacetLimitError
    digest = hashlib.sha256()
    def update(value):
        digest.update(json.dumps(value, sort_keys=True, default=str, separators=(',', ':')).encode())
        digest.update(b'\n')
    update(entries)
    # Hash exactly the source values used by professional summaries, never names.
    stroop = [row['assessment_id'] for row in entries if row['test_code'] == 'stroop_go_nogo_ptbr']
    generic = [row['assessment_id'] for row in entries if row['test_code'] != 'stroop_go_nogo_ptbr']
    if stroop:
        cursor = connection.execute("""SELECT assessment_id,trial_number,condition,key_pressed,reaction_time
            FROM trial_results WHERE assessment_id=ANY(%s) AND block='main'
            ORDER BY assessment_id,trial_number""", (stroop,))
        for row in cursor:
            update(row)
    update('generic-metrics')
    if generic:
        cursor = connection.execute("""SELECT assessment_id,metric_code,metric_value FROM assessment_metrics
            WHERE assessment_id=ANY(%s) ORDER BY assessment_id,metric_code""", (generic,))
        for row in cursor:
            update(row)
    return entries, digest.hexdigest()


def _hydrate(connection, rows, project_id):
    if not rows:
        return []
    ids = [row["assessment_id"] for row in rows]
    metrics = connection.execute(
        """SELECT assessment_id, metric_code, metric_value
           FROM assessment_metrics WHERE assessment_id = ANY(%s)
           ORDER BY assessment_id, metric_code""", (ids,),
    ).fetchall()
    metrics_by_id: dict[str, dict[str, float]] = {}
    for metric in metrics:
        metrics_by_id.setdefault(metric["assessment_id"], {})[
            metric["metric_code"]
        ] = float(metric["metric_value"])
    stroop_ids = [row["assessment_id"] for row in rows if row["test_code"] == "stroop_go_nogo_ptbr"]
    trials_by_id: dict[str, list[dict]] = {}
    if stroop_ids:
        source_trials = connection.execute(
            """SELECT assessment_id,condition,key_pressed,reaction_time FROM trial_results
               WHERE assessment_id=ANY(%s) AND block='main' ORDER BY assessment_id,trial_number""",
            (stroop_ids,),
        ).fetchall()
        for trial in source_trials:
            trials_by_id.setdefault(trial["assessment_id"], []).append(trial)
    result = []
    for row in rows:
        item = dict(row)
        item["project_id"] = project_id
        values = metrics_by_id.get(item["assessment_id"], {})
        if item["test_code"] == "stroop_go_nogo_ptbr":
            values = {metric["metric_code"]: metric["metric_value"]
                      for metric in _recalculate(trials_by_id.get(item["assessment_id"], []))}
        item["summary"] = _summary(item["test_code"], values)
        item.pop("import_status", None)
        result.append(item)
    return result


def list_assessments(database_url: str, project_id: UUID, issuer: str, subject: str,
                     *, participant_id: str | None = None, visit: str | None = None,
                     limit: int, offset: int, filters=None, snapshot=None, include_snapshot=False):
    try:
        with _connect(database_url) as connection:
            _validate_schema(connection)
            if not _authorized_project(connection, project_id, issuer, subject):
                return (False, [], None) if include_snapshot else (False, [])
            base, params = _scoped_query(project_id, issuer, subject, filters or {}, participant_id, visit)
            fingerprint = None
            if include_snapshot:
                _, fingerprint = _snapshot(connection, base, params)
                if snapshot is not None and snapshot != fingerprint:
                    raise SnapshotConflict
            rows = connection.execute(base + """
                ORDER BY COALESCE(wa.completed_at, a.imported_at::timestamptz), a.assessment_id
                LIMIT %s OFFSET %s""", (*params, limit, offset)).fetchall()
            result = _hydrate(connection, rows, project_id)
            return (True, result, fingerprint) if include_snapshot else (True, result)
    except psycopg.Error as exc:
        raise PersistenceError from exc


def aggregate_assessments(database_url, projects, issuer, subject, *, filters, view):
    """Reautoriza todos e compara os conjuntos originais em uma unica transacao RO."""
    if not 1 <= len(projects) <= 20:
        raise FacetLimitError
    try:
        with _connect(database_url) as connection:
            _validate_schema(connection)
            selected = []
            count = 0
            for project_id, expected in projects:
                if not _authorized_project(connection, project_id, issuer, subject):
                    return False, []
                base, params = _scoped_query(project_id, issuer, subject, filters)
                rows, fingerprint = _snapshot(connection, base, params)
                if fingerprint != expected:
                    raise SnapshotConflict
                count += len(rows)
                if count > 5000:
                    raise FacetLimitError
                selected.append((project_id, rows))
            result = []
            for project_id, rows in selected:
                visible = [row for row in rows if row['test_code'] == view['test_code']
                           and (not view.get('platform') or row['platform'] == view['platform'])]
                result.extend(_hydrate(connection, visible, project_id))
            return True, result
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _canonical_trial(source: dict) -> dict:
    row = {"block": "main", "condition": source["condition"],
           "key_pressed": source["key_pressed"] or ""}
    outcome = expected_outcome(row)
    if outcome is None:
        raise PersistenceError
    row["correct_response"], row["correct"], row["error_type"] = outcome
    value = source["reaction_time"]
    if row["key_pressed"]:
        if value is None or not math.isfinite(float(value)) or float(value) <= 0:
            raise PersistenceError
        row["reaction_time"] = str(float(value))
    else:
        if value is not None:
            raise PersistenceError
        row["reaction_time"] = ""
    return row


def _recalculate(trials: list[dict]) -> list[dict]:
    if not trials:
        raise PersistenceError
    return calculate_metrics([_canonical_trial(row) for row in trials])


def _summary(test_code: str, metrics: dict[str, float]) -> dict[str, Any]:
    if test_code != "stroop_go_nogo_ptbr":
        return {"metrics": metrics}
    hits = int(metrics.get("hits", 0))
    return {
        "accuracy": metrics.get("accuracy"),
        "accuracy_go_trials": metrics.get("accuracy_go_trials") if metrics.get("total_go_trials", 0) else None,
        "accuracy_no_go_trials": metrics.get("accuracy_no_go_trials") if metrics.get("total_no_go_trials", 0) else None,
        "total_go_trials": int(metrics.get("total_go_trials", 0)),
        "total_no_go_trials": int(metrics.get("total_no_go_trials", 0)),
        "response_time_seconds": metrics.get("response_time") if hits else None,
        "total_trials": int(metrics.get("total_trials", 0)),
        "hits": hits,
        "omission_errors": int(metrics.get("omission_errors", 0)),
        "commission_errors": int(metrics.get("commission_errors", 0)),
        "correct_rejections": int(metrics.get("correct_rejections", 0)),
    }


def get_assessment(database_url: str, project_id: UUID, assessment_id: str,
                   issuer: str, subject: str) -> dict[str, Any] | None:
    try:
        with _connect(database_url) as connection:
            _validate_schema(connection)
            if not _authorized_project(connection, project_id, issuer, subject):
                return None
            rows = connection.execute(
                _base_query("AND a.assessment_id=%s", history=True),
                (project_id, issuer, subject, assessment_id),
            ).fetchone()
            if rows is None:
                return None
            item = dict(rows)
            item["project_id"] = project_id
            metric_rows = connection.execute(
                """SELECT metric_code, metric_label, metric_value, unit
                   FROM assessment_metrics WHERE assessment_id=%s ORDER BY metric_code""",
                (assessment_id,),
            ).fetchall()
            metric_values = {row["metric_code"]: float(row["metric_value"]) for row in metric_rows}
            hits = int(metric_values.get("hits", 0))
            item["metrics"] = [
                {**row, "metric_value": (None if item["test_code"] == "stroop_go_nogo_ptbr"
                                         and row["metric_code"] == "response_time" and hits == 0
                                         else float(row["metric_value"]))}
                for row in metric_rows
            ]
            item["summary"] = _summary(item["test_code"], metric_values)
            trial_rows = connection.execute(
                """SELECT tr.block, tr.trial_number, wto.condition_id, tr.word, tr.ink_color,
                          tr.condition, tr.correct_response, tr.key_pressed, tr.reaction_time,
                          tr.correct, tr.error_type, wto.trial_start_ms, wto.stimulus_onset_ms,
                          wto.stimulus_offset_ms, wto.trial_end_ms, wto.key_at_ms,
                          wto.reaction_time_ms
                   FROM trial_results tr
                   LEFT JOIN web_trial_observations wto
                     ON wto.assessment_id=tr.assessment_id AND wto.trial_number=tr.trial_number
                   WHERE tr.assessment_id=%s AND tr.block='main'
                   ORDER BY tr.trial_number""", (assessment_id,),
            ).fetchall()
            if item["test_code"] == "stroop_go_nogo_ptbr":
                recalculated = _recalculate(trial_rows)
                metric_values = {metric["metric_code"]: metric["metric_value"] for metric in recalculated}
                hits = int(metric_values["hits"])
                item["metrics"] = [
                    {**metric, "metric_value": (None if (
                        metric["metric_code"] == "response_time" and not hits
                        or metric["metric_code"] in ("accuracy_go_trials", "omission_errors_percentage") and not metric_values["total_go_trials"]
                        or metric["metric_code"] == "accuracy_no_go_trials" and not metric_values["total_no_go_trials"]
                    ) else metric["metric_value"])} for metric in recalculated
                ]
                item["summary"] = _summary(item["test_code"], metric_values)
                for trial in trial_rows:
                    canonical = _canonical_trial(trial)
                    trial.update(correct=canonical["correct"] == "1", error_type=canonical["error_type"],
                                 correct_response=canonical["correct_response"] or None)
            item["trials"] = [
                {**row, "trial_number": int(row["trial_number"]),
                 "condition_id": (None if row["condition_id"] is None else int(row["condition_id"])),
                 "correct": bool(row["correct"]),
                 "reaction_time_seconds": (None if row["reaction_time"] is None
                                           else float(row["reaction_time"]))}
                for row in trial_rows
            ]
            return item
    except (SchemaError, PersistenceError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def iso_utc(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise PersistenceError from exc
    if not isinstance(value, datetime):
        raise PersistenceError
    if value.tzinfo is None:
        return value.isoformat()  # Legado sem fuso permanece sem fuso; nao inventar UTC.
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


__all__ = ["PersistenceError", "SchemaError", "SnapshotConflict", "FacetLimitError",
           "list_assessments", "assessment_options", "aggregate_assessments", "get_assessment", "iso_utc"]


def session_status(database_url, project_id, session_id, issuer, subject):
    """Estado de recepcao separado das consultas oficiais; sem observacoes brutas."""
    try:
        with _connect(database_url) as connection:
            _validate_schema(connection)
            if not _authorized_project(connection,project_id,issuer,subject):
                return None
            row = connection.execute(
                """SELECT s.session_id,s.state,s.expires_at,s.abort_reason,s.revoked_at,
                          i.revoked_at AS invitation_revoked_at,c.confirmed_through,c.prefix_hash,c.received_at,
                          inv.reason AS invalidation_reason,inv.source AS invalidation_source,
                          inv.recorded_at AS invalidated_at,inv.event_at_ms,
                          (s.expires_at <= clock_timestamp()) AS deadline_passed
                   FROM web_participant_sessions s JOIN web_invitations i USING(session_id)
                   LEFT JOIN web_session_checkpoints c USING(session_id)
                   LEFT JOIN web_session_invalidations inv USING(session_id)
                   WHERE i.project_id=%s AND s.session_id=%s""", (project_id,session_id),
            ).fetchone()
            if row is None:
                return None
            expired = row['deadline_passed'] and row['state'] in {'preparing','running'}
            return {
                'session_id':str(row['session_id']), 'state':'expired' if expired else row['state'],
                'expires_at':iso_utc(row['expires_at']),
                'complete':row['state']=='completed',
                'valid_for_result':row['state']=='completed' and row['invalidation_reason'] is None,
                'abort_reason':row['abort_reason'],
                'revoked':row['revoked_at'] is not None or row['invitation_revoked_at'] is not None,
                'invalidation':None if row['invalidation_reason'] is None else {
                    'reason':row['invalidation_reason'],'source':row['invalidation_source'],
                    'event_at_ms':row['event_at_ms'],'recorded_at':iso_utc(row['invalidated_at']),
                },
                'checkpoint':{'confirmed_through':row['confirmed_through'] or 0,
                              'prefix_hash':row['prefix_hash'],'received_at':iso_utc(row['received_at'])},
            }
    except psycopg.Error as exc:
        raise PersistenceError from exc


def analysis_selection(database_url, projects, issuer, subject, *, filters, assessment_ids=None):
    """Universo autorizado em uma transação RO; nunca publicar prefixo de 5.001."""
    if not 1 <= len(projects) <= 20:
        raise FacetLimitError
    try:
        with _connect(database_url) as connection:
            _validate_schema(connection)
            # Reautorizar TODOS antes de ler/popular qualquer resultado.
            if not all(_authorized_project(connection, project, issuer, subject) for project in projects):
                return False, [], [], None
            selected, sources = [], []
            for project in projects:
                base, params = _scoped_query(project, issuer, subject, filters)
                if assessment_ids is not None:
                    base += ' AND a.assessment_id=ANY(%s)'
                    params.append(assessment_ids)
                rows, fingerprint = _snapshot(connection, base, params)
                selected.extend((project, row) for row in rows)
                sources.append((str(project), fingerprint))
                if len(selected) > 5000:
                    raise FacetLimitError
            if len({row['assessment_id'] for _, row in selected}) != len(selected):
                # Vínculos legados ambíguos não podem duplicar o universo A/T.
                raise SnapshotConflict
            eligible = {row['assessment_id'] for _, row in selected}
            if assessment_ids is not None:
                if not set(assessment_ids) <= eligible:
                    raise SnapshotConflict
                selected = [(project, row) for project, row in selected if row['assessment_id'] in assessment_ids]
            result = []
            for project in projects:
                result.extend(_hydrate(connection, [row for scope, row in selected if scope == project], project))
            # Apenas colunas pseudonimizadas disponíveis ao papel SELECT.
            ids = sorted({row['assessment_id'] for row in result})
            trials = connection.execute('''SELECT assessment_id,trial_number,condition,word,ink_color,
                correct_response,key_pressed,reaction_time,correct,error_type FROM trial_results
                WHERE assessment_id=ANY(%s) AND block='main' ORDER BY assessment_id,trial_number''', (ids,)).fetchall() if ids else []
            content = hashlib.sha256(json.dumps([sources, result, trials], sort_keys=True, default=str,
                                               separators=(',', ':')).encode()).hexdigest()
            return True, result, trials, content
    except psycopg.Error as exc:
        raise PersistenceError from exc
