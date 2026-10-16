"""Persistencia SQLite existente, com SQL e schema preservados."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from stroop.domain.assessment import NormalizedAssessment
from stroop.domain.errors import ImportValidationError
from stroop.ingestion.stroop_csv import row_to_trial_values


# O recurso mantem seu caminho publico, inclusive na imagem do dashboard.
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "scripts" / "db_schema.sql"


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


def store_rows(
    rows: list[dict[str, str]],
    csv_path: Path,
    db_path: Path,
    force: bool = False,
    *,
    metrics: list[dict[str, object]],
    timestamp: str,
) -> dict[str, object]:
    first = rows[0]
    assessment_id = first["assessment_id"]
    imported_at = timestamp
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


def store_normalized(
    normalized: NormalizedAssessment, csv_path: Path, db_path: Path, force: bool = False,
    *, timestamp: str,
) -> dict[str, object]:
    """Persiste uma avaliação normalizada de um adaptador registrado."""
    assessment = normalized
    metadata = assessment.metadata
    imported_at = timestamp
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
