"""Persistencia para exportacao multi-granularidade (REQ-CSV-005).

Consulta PostgreSQL sob papel com permissoes estritas, filtra sessoes invalidas
e projeta as 5 granularidades.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID
import psycopg
from psycopg.rows import dict_row

from stroop.domain.web_multi_export import (
    GRANULARITY_COLUMNS,
    validate_granularity_and_columns,
    serialize_multi_csv,
)


def _connect(database_url: str):
    return psycopg.connect(database_url, row_factory=dict_row)


def query_multi_export_rows(
    database_url: str,
    *,
    project_id: UUID,
    granularity: str,
    identification_mode: str = "deidentified",
) -> list[dict[str, Any]]:
    with _connect(database_url) as conn:
        if granularity == "pacientes":
            rows = conn.execute(
                """SELECT p.id AS patient_id, p.participant_code,
                          p.full_name AS participant_name, p.initials,
                          p.active,
                          to_char(p.created_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS created_at
                   FROM web_patients p
                   ORDER BY p.participant_code ASC"""
            ).fetchall()
            return [dict(r) for r in rows]

        if granularity == "avaliacoes":
            rows = conn.execute(
                """SELECT a.assessment_id, p.project_id, p.code AS project_code,
                          COALESCE(wp.participant_code, a.participant_id) AS participant_code,
                          wp.full_name AS participant_name,
                          COALESCE(we.evaluator_code, a.evaluator) AS evaluator_code,
                          we.full_name AS evaluator_name,
                          a.visit, a.started_at,
                          COALESCE(to_char(wa.completed_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), a.started_at) AS completed_at,
                          COALESCE(wa.platform, 'psychopy') AS platform,
                          a.test_code, a.test_version
                   FROM assessments a
                   JOIN web_projects p ON p.project_id=%s
                   LEFT JOIN web_assessments wa ON wa.assessment_id=a.assessment_id
                   LEFT JOIN web_patients wp ON wp.id=wa.patient_id
                   LEFT JOIN web_evaluators we ON we.id=wa.evaluator_uuid
                   WHERE ((wa.assessment_id IS NOT NULL AND wa.project_id=p.project_id)
                       OR (wa.assessment_id IS NULL AND a.project_id=p.project_id))
                     AND NOT EXISTS (SELECT 1 FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id)
                   ORDER BY a.started_at DESC, a.assessment_id DESC""",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

        if granularity == "tentativas":
            rows = conn.execute(
                """SELECT tr.assessment_id, p.code AS project_code,
                          COALESCE(wp.participant_code, a.participant_id) AS participant_code,
                          wp.full_name AS participant_name,
                          a.visit, tr.trial_number, tr.block, tr.word, tr.ink_color, tr.condition,
                          tr.correct_response, tr.key_pressed, tr.correct, tr.error_type,
                          tr.reaction_time AS reaction_time_seconds
                   FROM trial_results tr
                   JOIN assessments a ON a.assessment_id=tr.assessment_id
                   JOIN web_projects p ON p.project_id=%s
                   LEFT JOIN web_assessments wa ON wa.assessment_id=a.assessment_id
                   LEFT JOIN web_patients wp ON wp.id=wa.patient_id
                   WHERE ((wa.assessment_id IS NOT NULL AND wa.project_id=p.project_id)
                       OR (wa.assessment_id IS NULL AND a.project_id=p.project_id))
                     AND NOT EXISTS (SELECT 1 FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id)
                     AND tr.block='main'
                   ORDER BY a.started_at DESC, tr.trial_number ASC""",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

        if granularity == "metricas":
            rows = conn.execute(
                """SELECT am.assessment_id, p.code AS project_code,
                          COALESCE(wp.participant_code, a.participant_id) AS participant_code,
                          wp.full_name AS participant_name,
                          a.visit, am.metric_code, am.metric_label, am.metric_value, am.unit
                   FROM assessment_metrics am
                   JOIN assessments a ON a.assessment_id=am.assessment_id
                   JOIN web_projects p ON p.project_id=%s
                   LEFT JOIN web_assessments wa ON wa.assessment_id=a.assessment_id
                   LEFT JOIN web_patients wp ON wp.id=wa.patient_id
                   WHERE ((wa.assessment_id IS NOT NULL AND wa.project_id=p.project_id)
                       OR (wa.assessment_id IS NULL AND a.project_id=p.project_id))
                     AND NOT EXISTS (SELECT 1 FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id)
                   ORDER BY a.started_at DESC, am.metric_code ASC""",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

        if granularity == "stroop_21_colunas":
            rows = conn.execute(
                """SELECT a.assessment_id, a.participant_id, wp.full_name AS participant_name,
                          COALESCE(wa.session_id::text, a.assessment_id) AS session,
                          a.assessment_date AS date,
                          'stroop_go_nogo_ptbr' AS expName,
                          COALESCE(wa.app_version, 'psychopy-imported') AS psychopyVersion,
                          COALESCE(wa.frame_period_ms, 16.666667) AS frameRate,
                          'web' AS OS,
                          tr.trial_number, tr.word, tr.ink_color, tr.condition,
                          tr.correct_response, tr.key_pressed,
                          wto.key_at_ms AS key_at,
                          tr.reaction_time AS reaction_time,
                          tr.correct, tr.error_type,
                          wto.trial_start_ms AS trial_start,
                          wto.stimulus_onset_ms AS stimulus_onset,
                          wto.stimulus_offset_ms AS stimulus_offset
                   FROM trial_results tr
                   JOIN assessments a ON a.assessment_id=tr.assessment_id
                   JOIN web_projects p ON p.project_id=%s
                   LEFT JOIN web_assessments wa ON wa.assessment_id=a.assessment_id
                   LEFT JOIN web_trial_observations wto
                     ON wto.assessment_id=tr.assessment_id AND wto.trial_number=tr.trial_number
                   LEFT JOIN web_patients wp ON wp.id=wa.patient_id
                   WHERE ((wa.assessment_id IS NOT NULL AND wa.project_id=p.project_id)
                       OR (wa.assessment_id IS NULL AND a.project_id=p.project_id))
                     AND NOT EXISTS (SELECT 1 FROM web_session_invalidations inv WHERE inv.session_id=wa.session_id)
                     AND tr.block='main'
                   ORDER BY a.started_at DESC, tr.trial_number ASC""",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

        raise ValueError(f"Granularidade não reconhecida: {granularity}")
