"""Dominio e serializacao CSV multi-granularidade (REQ-CSV-005 / ADR-007).

Suporta 5 granularidades: pacientes, avaliacoes, tentativas, metricas e stroop_21_colunas.
Implementa protecao contra CSV formula injection, modo deidentified vs. nominal e
tratamento explicito de valores ausentes sem arredondamento destrutivo.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import csv
import io
import math

from stroop.domain.web_export import _safe_cell

GRANULARITY_COLUMNS: dict[str, tuple[str, ...]] = {
    "pacientes": (
        "patient_id",
        "participant_code",
        "participant_name",
        "initials",
        "active",
        "created_at",
    ),
    "avaliacoes": (
        "assessment_id",
        "project_id",
        "project_code",
        "participant_code",
        "participant_name",
        "evaluator_code",
        "evaluator_name",
        "visit",
        "started_at",
        "completed_at",
        "platform",
        "test_code",
        "test_version",
    ),
    "tentativas": (
        "assessment_id",
        "project_code",
        "participant_code",
        "participant_name",
        "visit",
        "trial_number",
        "block",
        "word",
        "ink_color",
        "condition",
        "correct_response",
        "key_pressed",
        "correct",
        "error_type",
        "reaction_time_seconds",
    ),
    "metricas": (
        "assessment_id",
        "project_code",
        "participant_code",
        "participant_name",
        "visit",
        "metric_code",
        "metric_label",
        "metric_value",
        "unit",
    ),
    "stroop_21_colunas": (
        "participant_id",
        "participant_name",
        "session",
        "date",
        "expName",
        "psychopyVersion",
        "frameRate",
        "OS",
        "trial_number",
        "word",
        "ink_color",
        "condition",
        "correct_response",
        "key_pressed",
        "key_at",
        "reaction_time",
        "correct",
        "error_type",
        "trial_start",
        "stimulus_onset",
        "stimulus_offset",
    ),
}

NOMINAL_COLUMNS: frozenset[str] = frozenset({
    "participant_name",
    "evaluator_name",
    "initials",
})


def validate_granularity_and_columns(
    granularity: str,
    requested_columns: Sequence[str] | None = None,
) -> tuple[str, list[str]]:
    if granularity not in GRANULARITY_COLUMNS:
        raise ValueError(f"Granularidade não suportada: {granularity}")
    allowed = GRANULARITY_COLUMNS[granularity]
    if not requested_columns:
        return granularity, list(allowed)
    for col in requested_columns:
        if col not in allowed:
            raise ValueError(f"Coluna não permitida para {granularity}: {col}")
    # Preserva a ordem canônica das colunas permitidas
    return granularity, [col for col in allowed if col in requested_columns]


def format_csv_cell(value: object, *, column: str, identification_mode: str) -> str:
    if value is None:
        return ""
    if identification_mode != "nominal" and column in NOMINAL_COLUMNS:
        return "NAO_COLETADO" if column == "participant_name" else ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return ""
        return str(value)
    text = str(value)
    return _safe_cell(text)


def serialize_multi_csv(
    rows: Iterable[Mapping[str, object]],
    *,
    granularity: str,
    columns: Sequence[str],
    identification_mode: str = "deidentified",
) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(columns)
    for row in rows:
        formatted = [
            format_csv_cell(row.get(col), column=col, identification_mode=identification_mode)
            for col in columns
        ]
        writer.writerow(formatted)
    return output.getvalue()
