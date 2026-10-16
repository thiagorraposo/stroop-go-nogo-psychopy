#!/usr/bin/env python3
"""Importa CSV unificado do Stroop Go/No-Go para SQLite local."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


DEFAULT_DB_PATH = Path("database/stroop_results.sqlite3")

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


from stroop.application.clock import utc_now_iso
from stroop.application.import_sqlite import import_csv, import_normalized, import_rows
from stroop.persistence.sqlite import SCHEMA_PATH, assessment_exists, connect_database


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
