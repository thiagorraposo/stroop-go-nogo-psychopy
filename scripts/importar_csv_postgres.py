#!/usr/bin/env python3
"""Importacao transacional do CSV Stroop para PostgreSQL, sem alterar o legado."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import psycopg

if __package__:
    from . import importar_csv_sqlite as legacy
    from .instrumentos import InstrumentValidationError, load_instrument_csv
else:
    import importar_csv_sqlite as legacy
    from instrumentos import InstrumentValidationError, load_instrument_csv


class PostgresImportError(Exception):
    """Falha publica sem dados de entrada ou detalhes de conexao."""


class DuplicateAssessmentError(PostgresImportError):
    """Avaliacao existente; substituicao exige --force."""


def import_csv(csv_path: Path, database_url: str = "", *, force: bool = False,
               validate_only: bool = False) -> dict[str, int | str]:
    try:
        normalized = load_instrument_csv(csv_path)
        metrics = normalized.metrics
        trials = normalized.trial_values
    except (InstrumentValidationError, legacy.ImportValidationError, OSError, UnicodeError, ValueError, OverflowError):
        raise PostgresImportError("CSV invalido ou indisponivel; nenhuma importacao realizada.") from None

    summary = {"status": "validated", "trials": len(trials), "metrics": len(metrics)}
    if validate_only:
        return summary
    if not database_url:
        raise PostgresImportError("DATABASE_URL nao configurada.")

    metadata = normalized.metadata
    assessment_id = metadata["assessment_id"]
    timestamp = legacy.utc_now_iso()
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
    summary["status"] = "reimported" if exists else "imported"
    return summary


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, "Argumentos invalidos. Consulte --help.\n")


def main(argv: list[str] | None = None) -> int:
    parser = SafeArgumentParser(description="Importa CSV Stroop via DATABASE_URL.")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--force", action="store_true", help="Substitui avaliacao existente em transacao.")
    parser.add_argument("--validate-only", action="store_true", help="Valida CSV sem conectar ou persistir.")
    args = parser.parse_args(argv)
    try:
        result = import_csv(args.csv_path, os.environ.get("DATABASE_URL", ""),
                            force=args.force, validate_only=args.validate_only)
    except DuplicateAssessmentError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except PostgresImportError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Importacao: {result['status']}; tentativas={result['trials']}; metricas={result['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
