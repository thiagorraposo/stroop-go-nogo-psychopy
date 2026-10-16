"""Persistencia transacional de avaliacoes normalizadas no PostgreSQL."""

from __future__ import annotations

from pathlib import Path

import psycopg

from stroop.application.errors import DuplicateAssessmentError, PostgresImportError
from stroop.domain.assessment import NormalizedAssessment


def store_assessment(
    normalized: NormalizedAssessment,
    csv_path: Path,
    database_url: str,
    *,
    force: bool = False,
    timestamp: str,
) -> bool:
    """Grava uma avaliacao e informa se substituiu uma importacao existente."""
    metadata = normalized.metadata
    assessment_id = metadata["assessment_id"]
    metrics = normalized.metrics
    trials = normalized.trial_values
    try:
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            # Serializa importadores, inclusive contra a migracao legada, antes
            # de verificar duplicidade. A PK continua protegendo outros escritores.
            connection.execute("LOCK TABLE assessments IN SHARE ROW EXCLUSIVE MODE")
            exists = connection.execute(
                "SELECT 1 FROM assessments WHERE assessment_id = %s", (assessment_id,)
            ).fetchone() is not None
            if exists and not force:
                raise DuplicateAssessmentError("Avaliacao ja importada. Use --force para reimportar.")
            if exists:
                connection.execute("DELETE FROM assessments WHERE assessment_id = %s", (assessment_id,))
            connection.execute(
                """INSERT INTO assessments (
                    assessment_id, test_code, test_version, project, participant_id,
                    participant_name, initials, visit, evaluator, assessment_date,
                    started_at, source_file, imported_at, import_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (assessment_id, metadata["test_code"], metadata["test_version"], metadata["project"],
                 metadata["participant_id"], metadata["participant_name"], metadata["initials"] or None,
                 metadata["visit"], metadata["evaluator"], metadata["assessment_date"], metadata["started_at"],
                 str(csv_path), timestamp, "valid"),
            )
            with connection.cursor() as cursor:
                if trials:
                    cursor.executemany(
                        """INSERT INTO trial_results (
                            assessment_id, block, trial_number, word, ink_color, condition,
                            correct_response, key_pressed, reaction_time, correct, error_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", trials,
                    )
                cursor.executemany(
                    """INSERT INTO assessment_metrics (
                        assessment_id, metric_code, metric_label, metric_value, unit, calculated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)""",
                    [(assessment_id, m["metric_code"], m["metric_label"], m["metric_value"],
                      m["unit"], timestamp) for m in metrics],
                )
    except DuplicateAssessmentError:
        raise
    except (psycopg.Error, ValueError, OverflowError):
        raise PostgresImportError(
            "Falha no PostgreSQL; importacao nao confirmada. Verifique conexao e migrations."
        ) from None
    return exists
