"""Caso de uso de importacao CSV para PostgreSQL, independente da CLI."""

from __future__ import annotations

from pathlib import Path

from stroop.application import clock
from stroop.application.errors import PostgresImportError
from stroop.domain.errors import ImportValidationError, InstrumentValidationError
from stroop.ingestion.instruments import load_instrument_csv
from stroop.persistence import postgres


def import_csv(csv_path: Path, database_url: str = "", *, force: bool = False,
               validate_only: bool = False) -> dict[str, int | str]:
    try:
        normalized = load_instrument_csv(csv_path)
        metrics = normalized.metrics
        trials = normalized.trial_values
    except (InstrumentValidationError, ImportValidationError, OSError, UnicodeError, ValueError, OverflowError):
        raise PostgresImportError("CSV invalido ou indisponivel; nenhuma importacao realizada.") from None

    summary = {"status": "validated", "trials": len(trials), "metrics": len(metrics)}
    if validate_only:
        return summary
    if not database_url:
        raise PostgresImportError("DATABASE_URL nao configurada.")

    exists = postgres.store_assessment(
        normalized, csv_path, database_url, force=force, timestamp=clock.utc_now_iso(),
    )
    summary["status"] = "reimported" if exists else "imported"
    return summary
