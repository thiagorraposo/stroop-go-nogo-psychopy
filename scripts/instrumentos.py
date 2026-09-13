"""Contratos e adaptadores de importacao para instrumentos suportados.

O contrato comum normaliza metadados da avaliacao e metricas calculadas. Cada
adaptador continua responsavel por validar seu proprio formato e suas formulas.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class InstrumentValidationError(Exception):
    """Entrada ausente, malformada ou incompatível com um instrumento."""


@dataclass(frozen=True)
class NormalizedAssessment:
    """Resultado comum consumido pelos importadores SQLite e PostgreSQL."""

    adapter_code: str
    metadata: dict[str, str]
    metrics: list[dict[str, Any]]
    trial_values: list[tuple[Any, ...]]


class InstrumentAdapter:
    def __init__(self, code: str, columns: tuple[str, ...], loader: Callable[..., NormalizedAssessment]):
        self.code = code
        self.columns = columns
        self.loader = loader

    def load(self, path: Path) -> NormalizedAssessment:
        return self.loader(path)


def _read_rows(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.exists() or not path.is_file():
        raise InstrumentValidationError("CSV invalido ou indisponivel.")
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            if tuple(header) != columns:
                raise InstrumentValidationError("Formato de CSV nao reconhecido.")
            rows = []
            for values in reader:
                if len(values) != len(columns):
                    raise InstrumentValidationError("CSV com numero de campos invalido.")
                rows.append(dict(zip(columns, values)))
    except (OSError, UnicodeError, csv.Error, StopIteration) as exc:
        raise InstrumentValidationError("CSV invalido ou indisponivel.") from exc
    if not rows:
        raise InstrumentValidationError("CSV sem dados.")
    return rows


def _load_stroop(path: Path) -> NormalizedAssessment:
    try:
        from . import importar_csv_sqlite as legacy
    except ImportError:
        import importar_csv_sqlite as legacy

    rows = legacy.load_and_validate_csv(path)
    first = rows[0]
    return NormalizedAssessment(
        adapter_code=first["test_code"],
        metadata={key: first[key] for key in legacy.ASSESSMENT_METADATA_COLUMNS},
        metrics=legacy.calculate_metrics(rows),
        trial_values=[legacy.row_to_trial_values(row) for row in rows],
    )


SYNTHETIC_COLUMNS = (
    "project", "participant_id", "participant_name", "initials", "visit",
    "evaluator", "assessment_id", "assessment_date", "started_at", "test_code",
    "test_version", "metric_code", "metric_label", "metric_value", "unit",
)
SYNTHETIC_CODE = "instrumento_sintetico_demo"
SYNTHETIC_METRICS = {
    "demo_total": ("Total demonstrativo", "count"),
    "demo_mean": ("Media demonstrativa", "unit"),
}


def _load_synthetic(path: Path) -> NormalizedAssessment:
    rows = _read_rows(path, SYNTHETIC_COLUMNS)
    first = rows[0]
    if first["test_code"] != SYNTHETIC_CODE:
        raise InstrumentValidationError("test_code nao suportado pelo adaptador demonstrativo.")
    metadata_keys = SYNTHETIC_COLUMNS[:11]
    metrics: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if any(row[key] != first[key] for key in metadata_keys):
            raise InstrumentValidationError("Metadados inconsistentes no CSV.")
        code = row["metric_code"]
        if code not in SYNTHETIC_METRICS or code in seen:
            raise InstrumentValidationError("Metrica nao suportada ou repetida.")
        if not row["metric_label"] or row["metric_label"] != SYNTHETIC_METRICS[code][0]:
            raise InstrumentValidationError("Rotulo de metrica invalido.")
        if row["unit"] != SYNTHETIC_METRICS[code][1]:
            raise InstrumentValidationError("Unidade de metrica invalida.")
        try:
            value = float(row["metric_value"])
        except ValueError as exc:
            raise InstrumentValidationError("Valor de metrica invalido.") from exc
        if not math.isfinite(value) or value < 0:
            raise InstrumentValidationError("Valor de metrica invalido.")
        metrics.append({"metric_code": code, "metric_label": row["metric_label"],
                        "metric_value": value, "unit": row["unit"]})
        seen.add(code)
    if seen != set(SYNTHETIC_METRICS):
        raise InstrumentValidationError("CSV demonstrativo deve conter as metricas registradas.")
    return NormalizedAssessment(
        adapter_code=SYNTHETIC_CODE,
        metadata={key: first[key] for key in metadata_keys},
        metrics=metrics,
        trial_values=[],
    )


def _build_adapters() -> tuple[InstrumentAdapter, ...]:
    try:
        from . import importar_csv_sqlite as legacy
    except ImportError:
        import importar_csv_sqlite as legacy

    return (
        InstrumentAdapter("stroop_go_nogo_ptbr", tuple(legacy.CANONICAL_COLUMNS), _load_stroop),
        InstrumentAdapter(SYNTHETIC_CODE, SYNTHETIC_COLUMNS, _load_synthetic),
    )


def supported_instruments() -> dict[str, InstrumentAdapter]:
    return {adapter.code: adapter for adapter in _build_adapters()}


def load_instrument_csv(path: Path) -> NormalizedAssessment:
    """Seleciona adaptador pela cabecalho e valida a avaliacao inteira."""
    path = Path(path)
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            header = tuple(csv.reader(handle).__next__())
    except (OSError, UnicodeError, csv.Error, StopIteration) as exc:
        raise InstrumentValidationError("CSV invalido ou indisponivel.") from exc
    for adapter in _build_adapters():
        if header == adapter.columns:
            return adapter.load(path)
    raise InstrumentValidationError("Cabecalho invalido. Formato de CSV nao reconhecido.")
