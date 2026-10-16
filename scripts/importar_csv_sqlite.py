#!/usr/bin/env python3
"""Importa CSV unificado do Stroop Go/No-Go para SQLite local."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DB_PATH = Path("database/stroop_results.sqlite3")
SCHEMA_PATH = Path(__file__).with_name("db_schema.sql")

# Execucao direta por caminho continua funcionando sem instalar o pacote local.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stroop.domain.errors import ImportValidationError, InstrumentValidationError
from stroop.domain.stroop import (
    ALLOWED_BLOCKS,
    ALLOWED_CONDITIONS,
    ALLOWED_ERROR_TYPES,
    ALLOWED_KEYS,
    ASSESSMENT_METADATA_COLUMNS,
    CANONICAL_COLUMNS,
    METRIC_DEFINITIONS,
    REQUIRED_NON_EMPTY,
    calculate_metrics,
    expected_outcome,
    parse_optional_reaction_time,
    parse_positive_int,
    percent,
    validate_row,
    validate_rows,
)
from stroop.ingestion.stroop_csv import (
    load_and_validate_csv,
    read_csv_rows,
    row_to_trial_values,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())
    return connection


def assessment_exists(connection: sqlite3.Connection, assessment_id: str) -> bool:
    cursor = connection.execute(
        "SELECT 1 FROM assessments WHERE assessment_id = ?",
        (assessment_id,),
    )
    return cursor.fetchone() is not None


def import_rows(
    rows: list[dict[str, str]],
    csv_path: Path,
    db_path: Path,
    force: bool = False,
) -> dict[str, object]:
    first = rows[0]
    assessment_id = first["assessment_id"]
    metrics = calculate_metrics(rows)
    imported_at = utc_now_iso()
    calculated_at = imported_at

    connection = connect_database(db_path)
    try:
        if assessment_exists(connection, assessment_id) and not force:
            raise ImportValidationError(
                f"assessment_id ja importado: {assessment_id}. Use --force para reimportar."
            )

        with connection:
            if force:
                connection.execute(
                    "DELETE FROM assessment_metrics WHERE assessment_id = ?",
                    (assessment_id,),
                )
                connection.execute(
                    "DELETE FROM trial_results WHERE assessment_id = ?",
                    (assessment_id,),
                )
                connection.execute(
                    "DELETE FROM assessments WHERE assessment_id = ?",
                    (assessment_id,),
                )

            connection.execute(
                """
                INSERT INTO assessments (
                    assessment_id, test_code, test_version, project,
                    participant_id, participant_name, initials, visit,
                    evaluator, assessment_date, started_at, source_file,
                    imported_at, import_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment_id,
                    first["test_code"],
                    first["test_version"],
                    first["project"],
                    first["participant_id"],
                    first["participant_name"],
                    first["initials"] or None,
                    first["visit"],
                    first["evaluator"],
                    first["assessment_date"],
                    first["started_at"],
                    str(csv_path),
                    imported_at,
                    "valid",
                ),
            )

            connection.executemany(
                """
                INSERT INTO trial_results (
                    assessment_id, block, trial_number, word, ink_color,
                    condition, correct_response, key_pressed, reaction_time,
                    correct, error_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [row_to_trial_values(row) for row in rows],
            )

            connection.executemany(
                """
                INSERT INTO assessment_metrics (
                    assessment_id, metric_code, metric_label, metric_value,
                    unit, calculated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        assessment_id,
                        metric["metric_code"],
                        metric["metric_label"],
                        metric["metric_value"],
                        metric["unit"],
                        calculated_at,
                    )
                    for metric in metrics
                ],
            )
    finally:
        connection.close()

    return {
        "assessment_id": assessment_id,
        "trials_imported": len(rows),
        "metrics_imported": len(metrics),
        "db_path": db_path,
    }


def import_csv(csv_path: Path, db_path: Path, force: bool = False) -> dict[str, object]:
    # O caminho legado do Stroop permanece byte a byte equivalente. Adaptadores
    # adicionais podem gravar apenas metadados e metricas, sem criar tentativas
    # incompatíveis com o schema canonico.
    try:
        from .instrumentos import load_instrument_csv
    except ImportError:
        from instrumentos import load_instrument_csv

    try:
        normalized = load_instrument_csv(csv_path)
    except InstrumentValidationError as exc:
        # Mantem a excecao publica historica da CLI SQLite.
        raise ImportValidationError(str(exc)) from exc
    if normalized.adapter_code == "stroop_go_nogo_ptbr":
        rows = load_and_validate_csv(csv_path)
        return import_rows(rows, csv_path, db_path, force=force)
    return import_normalized(normalized, csv_path, db_path, force=force)


def import_normalized(
    normalized: object, csv_path: Path, db_path: Path, force: bool = False
) -> dict[str, object]:
    """Persiste uma avaliação normalizada de um adaptador registrado."""
    assessment = normalized  # dataclass definida em stroop.domain.assessment
    metadata = assessment.metadata
    imported_at = utc_now_iso()
    connection = connect_database(db_path)
    try:
        if assessment_exists(connection, metadata["assessment_id"]) and not force:
            raise ImportValidationError(
                f"assessment_id ja importado: {metadata['assessment_id']}. Use --force para reimportar."
            )
        with connection:
            if force:
                connection.execute("DELETE FROM assessments WHERE assessment_id = ?", (metadata["assessment_id"],))
            connection.execute(
                """
                INSERT INTO assessments (
                    assessment_id, test_code, test_version, project,
                    participant_id, participant_name, initials, visit,
                    evaluator, assessment_date, started_at, source_file,
                    imported_at, import_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata["assessment_id"], metadata["test_code"], metadata["test_version"],
                    metadata["project"], metadata["participant_id"], metadata["participant_name"],
                    metadata["initials"] or None, metadata["visit"], metadata["evaluator"],
                    metadata["assessment_date"], metadata["started_at"], str(csv_path),
                    imported_at, "valid",
                ),
            )
            connection.executemany(
                """
                INSERT INTO assessment_metrics (
                    assessment_id, metric_code, metric_label, metric_value, unit, calculated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (metadata["assessment_id"], metric["metric_code"], metric["metric_label"],
                     metric["metric_value"], metric["unit"], imported_at)
                    for metric in assessment.metrics
                ],
            )
            if assessment.trial_values:
                connection.executemany(
                    """
                    INSERT INTO trial_results (
                        assessment_id, block, trial_number, word, ink_color,
                        condition, correct_response, key_pressed, reaction_time,
                        correct, error_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    assessment.trial_values,
                )
    finally:
        connection.close()
    return {
        "assessment_id": metadata["assessment_id"],
        "trials_imported": len(assessment.trial_values),
        "metrics_imported": len(assessment.metrics),
        "db_path": db_path,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa CSV unificado do Stroop Go/No-Go para SQLite local."
    )
    parser.add_argument("csv_path", type=Path, help="Caminho do CSV unificado.")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Caminho do SQLite local. Padrao: {DEFAULT_DB_PATH}",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reimporta assessment_id existente, substituindo linhas anteriores.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        summary = import_csv(args.csv_path, args.db, force=args.force)
    except (ImportValidationError, InstrumentValidationError, sqlite3.Error) as exc:
        print("Importacao: ERRO", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return 1

    print("Importacao: OK")
    print(f"assessment_id: {summary['assessment_id']}")
    print(f"trials importadas: {summary['trials_imported']}")
    print(f"metricas calculadas: {summary['metrics_imported']}")
    print(f"banco usado: {summary['db_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
