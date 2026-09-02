#!/usr/bin/env python3
"""Migra explicitamente um SQLite legado validado para PostgreSQL."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import psycopg


EXPECTED_COLUMNS = {
    "assessments": {
        "assessment_id", "test_code", "test_version", "project",
        "participant_id", "participant_name", "initials", "visit", "evaluator",
        "assessment_date", "started_at", "source_file", "imported_at", "import_status",
    },
    "assessment_metrics": {
        "metric_id", "assessment_id", "metric_code", "metric_label",
        "metric_value", "unit", "calculated_at",
    },
    "trial_results": {
        "trial_result_id", "assessment_id", "block", "trial_number", "word",
        "ink_color", "condition", "correct_response", "key_pressed",
        "reaction_time", "correct", "error_type",
    },
}

TABLE_COLUMNS = {
    table: tuple(columns)
    for table, columns in {
        "assessments": (
            "assessment_id", "test_code", "test_version", "project", "participant_id",
            "participant_name", "initials", "visit", "evaluator", "assessment_date",
            "started_at", "source_file", "imported_at", "import_status",
        ),
        "assessment_metrics": (
            "metric_id", "assessment_id", "metric_code", "metric_label",
            "metric_value", "unit", "calculated_at",
        ),
        "trial_results": (
            "trial_result_id", "assessment_id", "block", "trial_number", "word",
            "ink_color", "condition", "correct_response", "key_pressed",
            "reaction_time", "correct", "error_type",
        ),
    }.items()
}


class LegacyMigrationError(Exception):
    """Erro de validacao ou migracao sem conteudo identificavel."""


def connect_sqlite_readonly(sqlite_path: Path) -> sqlite3.Connection:
    if not sqlite_path.is_file():
        raise LegacyMigrationError("SQLite de origem nao encontrado.")
    connection = sqlite3.connect(f"file:{sqlite_path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def validate_sqlite_schema(connection: sqlite3.Connection) -> None:
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise LegacyMigrationError("SQLite de origem falhou na verificacao de integridade.")
    if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise LegacyMigrationError("SQLite de origem possui relacionamentos invalidos.")
    existing = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    missing = sorted(EXPECTED_COLUMNS.keys() - existing)
    if missing:
        raise LegacyMigrationError("Schema SQLite invalido; tabelas ausentes.")
    for table, expected in EXPECTED_COLUMNS.items():
        actual = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        if actual != expected:
            raise LegacyMigrationError(f"Schema SQLite invalido na tabela {table}.")


def read_source(connection: sqlite3.Connection) -> dict[str, list[tuple[Any, ...]]]:
    return {
        table: [tuple(row) for row in connection.execute(
            f"SELECT {', '.join(columns)} FROM {table} ORDER BY {columns[0]}"
        ).fetchall()]
        for table, columns in TABLE_COLUMNS.items()
    }


def _insert_rows(connection: psycopg.Connection[Any], table: str, rows: list[tuple[Any, ...]]) -> None:
    if not rows:
        return
    columns = TABLE_COLUMNS[table]
    placeholders = ", ".join(["%s"] * len(columns))
    with connection.cursor() as cursor:
        cursor.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            rows,
        )


def migrate_sqlite_to_postgres(sqlite_path: Path, database_url: str) -> dict[str, int]:
    if not database_url:
        raise LegacyMigrationError("DATABASE_URL nao configurada.")
    with connect_sqlite_readonly(sqlite_path) as source_connection:
        validate_sqlite_schema(source_connection)
        source = read_source(source_connection)

    try:
        with psycopg.connect(database_url) as target:
            with target.transaction():
                for table in TABLE_COLUMNS:
                    target.execute(f"LOCK TABLE {table} IN EXCLUSIVE MODE")
                    if target.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone():
                        raise LegacyMigrationError(
                            "PostgreSQL de destino ja contem dados de dominio."
                        )
                _insert_rows(target, "assessments", source["assessments"])
                _insert_rows(target, "assessment_metrics", source["assessment_metrics"])
                _insert_rows(target, "trial_results", source["trial_results"])
                for table, identity in (
                    ("assessment_metrics", "metric_id"),
                    ("trial_results", "trial_result_id"),
                ):
                    target.execute(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', '{identity}'),
                            COALESCE(MAX({identity}), 1),
                            MAX({identity}) IS NOT NULL
                        ) FROM {table}
                        """
                    )
    except LegacyMigrationError:
        raise
    except psycopg.Error as exc:
        raise LegacyMigrationError("Falha na migracao para PostgreSQL; rollback executado.") from exc

    return {table: len(rows) for table, rows in source.items()}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migra SQLite legado para PostgreSQL.")
    parser.add_argument("sqlite", type=Path)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL", ""))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        counts = migrate_sqlite_to_postgres(args.sqlite, args.database_url)
    except LegacyMigrationError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print("Migracao concluida: " + ", ".join(
        f"{table}={count}" for table, count in counts.items()
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
