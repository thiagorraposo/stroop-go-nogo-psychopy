"""Casos de uso de importacao SQLite sem dependencia das CLIs."""

from __future__ import annotations

from pathlib import Path

from stroop.application import clock
from stroop.domain.assessment import NormalizedAssessment
from stroop.domain.errors import ImportValidationError, InstrumentValidationError
from stroop.domain.stroop import calculate_metrics
from stroop.ingestion.instruments import load_instrument_csv
from stroop.ingestion.stroop_csv import load_and_validate_csv
from stroop.persistence import sqlite


def import_rows(
    rows: list[dict[str, str]], csv_path: Path, db_path: Path, force: bool = False,
) -> dict[str, object]:
    metrics = calculate_metrics(rows)
    return sqlite.store_rows(
        rows, csv_path, db_path, force=force,
        metrics=metrics, timestamp=clock.utc_now_iso(),
    )


def import_normalized(
    normalized: NormalizedAssessment, csv_path: Path, db_path: Path, force: bool = False,
) -> dict[str, object]:
    return sqlite.store_normalized(
        normalized, csv_path, db_path, force=force, timestamp=clock.utc_now_iso(),
    )


def import_csv(csv_path: Path, db_path: Path, force: bool = False) -> dict[str, object]:
    # O caminho legado do Stroop permanece byte a byte equivalente. Adaptadores
    # adicionais podem gravar apenas metadados e metricas, sem criar tentativas
    # incompatíveis com o schema canonico.
    try:
        normalized = load_instrument_csv(csv_path)
    except InstrumentValidationError as exc:
        # Mantem a excecao publica historica da CLI SQLite.
        raise ImportValidationError(str(exc)) from exc
    if normalized.adapter_code == "stroop_go_nogo_ptbr":
        rows = load_and_validate_csv(csv_path)
        return import_rows(rows, csv_path, db_path, force=force)
    return import_normalized(normalized, csv_path, db_path, force=force)
