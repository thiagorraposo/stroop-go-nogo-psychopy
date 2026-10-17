"""CSV agregado de avaliações autorizadas, distinto das 21 colunas de tentativas.

Retorna texto Unicode para codificação UTF-8 sem BOM pelo adaptador HTTP. Usa
vírgula, aspas CSV padrão e CRLF. Não consulta dados nem concede autorização;
o chamador fornece a projeção profissional completa do conjunto filtrado.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import csv
import io
import math

from stroop.domain.web_export import _safe_cell

METADATA_COLUMNS = (
    "assessment_id", "project_id", "project_code", "participant_id", "visit",
    "evaluator_id", "started_at", "platform", "test_code", "test_version",
    "protocol_id", "app_version",
)
STROOP_METRICS = (
    ("accuracy", "accuracy_percent"),
    ("accuracy_go_trials", "accuracy_go_trials_percent"),
    ("accuracy_no_go_trials", "accuracy_no_go_trials_percent"),
    ("response_time_seconds", "response_time_seconds"),
    ("total_trials", "total_trials_count"),
    ("total_go_trials", "total_go_trials_count"),
    ("total_no_go_trials", "total_no_go_trials_count"),
    ("hits", "hits_count"),
    ("omission_errors", "omission_errors_count"),
    ("commission_errors", "commission_errors_count"),
    ("correct_rejections", "correct_rejections_count"),
)
DEMO_METRICS = (("demo_total", "demo_total_count"), ("demo_mean", "demo_mean_unit"))
_REGISTERED = {"stroop_go_nogo_ptbr": STROOP_METRICS, "instrumento_sintetico_demo": DEMO_METRICS}


def _metrics(test_code: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(test_code, str) or test_code not in _REGISTERED:
        raise ValueError("Instrumento não registrado para exportação agregada.")
    return _REGISTERED[test_code]


def aggregate_filename(test_code: str) -> str:
    """Nome fixo permitido, sem identificadores, filtros ou metadados da pesquisa."""
    _metrics(test_code)
    return f"{test_code}_avaliacoes.csv"


def _text(value: object) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("Metadado inválido para exportação agregada.")
    return _safe_cell(value)


def _number(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Métrica inválida para exportação agregada.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Métrica não finita para exportação agregada.")
    # Números não recebem escape de texto: negativos são valores, não fórmulas.
    return str(value)


def serialize_aggregate_csv(rows: Iterable[Mapping[str, object]], *, test_code: str) -> str:
    """Uma linha por avaliação, com unidades explícitas e somente campos permitidos.

    Não recalcula nem arredonda métricas. Ausências são células vazias. Campos
    extras da projeção nunca são serializados; instrumentos misturados e valores
    inválidos são recusados antes de retornar qualquer CSV ao consumidor.
    """
    metrics = _metrics(test_code)
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow((*METADATA_COLUMNS, *(column for _, column in metrics)))
    for row in rows:
        if not isinstance(row, Mapping) or row.get("test_code") != test_code:
            raise ValueError("Avaliação incompatível com o instrumento selecionado.")
        summary = row.get("summary")
        if not isinstance(summary, Mapping):
            raise ValueError("Resumo inválido para exportação agregada.")
        if test_code == "instrumento_sintetico_demo":
            summary = summary.get("metrics")
            if not isinstance(summary, Mapping):
                raise ValueError("Métricas demonstrativas inválidas.")
        writer.writerow((
            *(_text(row.get(column)) for column in METADATA_COLUMNS),
            *(_number(summary.get(code)) for code, _ in metrics),
        ))
    return output.getvalue()
