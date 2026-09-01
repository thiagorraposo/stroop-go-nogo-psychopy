"""Acesso somente leitura ao SQLite do dashboard."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path("database/stroop_results.sqlite3")

REQUIRED_TABLES = {"assessments", "assessment_metrics", "trial_results"}
REQUIRED_COLUMNS = {
    "assessments": {
        "assessment_id",
        "test_code",
        "test_version",
        "project",
        "participant_id",
        "participant_name",
        "visit",
        "evaluator",
        "assessment_date",
        "started_at",
        "source_file",
        "imported_at",
        "import_status",
    },
    "assessment_metrics": {
        "assessment_id",
        "metric_code",
        "metric_label",
        "metric_value",
        "unit",
        "calculated_at",
    },
    "trial_results": {
        "assessment_id",
        "block",
        "trial_number",
        "word",
        "ink_color",
        "condition",
        "correct_response",
        "key_pressed",
        "reaction_time",
        "correct",
        "error_type",
    },
}


class DashboardDataError(Exception):
    """Erro amigavel para dados ausentes, vazios ou invalidos."""


def connect_readonly(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Abre o SQLite em modo somente leitura."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise DashboardDataError(
            f"Banco SQLite nao encontrado: {db_path}. Importe um CSV antes de abrir o dashboard."
        )
    if not db_path.is_file():
        raise DashboardDataError(f"Caminho do banco nao e arquivo: {db_path}")

    uri = f"file:{db_path.resolve()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def validate_schema(connection: sqlite3.Connection) -> None:
    existing_tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    missing_tables = sorted(REQUIRED_TABLES - existing_tables)
    if missing_tables:
        raise DashboardDataError(
            "Schema SQLite invalido. Tabelas ausentes: " + ", ".join(missing_tables)
        )

    missing_columns: list[str] = []
    for table_name, expected_columns in REQUIRED_COLUMNS.items():
        missing = sorted(expected_columns - table_columns(connection, table_name))
        if missing:
            missing_columns.append(f"{table_name}: {', '.join(missing)}")

    if missing_columns:
        raise DashboardDataError(
            "Schema SQLite invalido. Colunas ausentes: " + " | ".join(missing_columns)
        )


def fetch_all_rows(
    connection: sqlite3.Connection, table_name: str
) -> list[dict[str, Any]]:
    cursor = connection.execute(f"SELECT * FROM {table_name}")
    return [dict(row) for row in cursor.fetchall()]


def load_sqlite_data(
    db_path: Path = DEFAULT_DB_PATH,
) -> dict[str, list[dict[str, Any]]]:
    """Le as tres tabelas oficiais do SQLite sem modificar o banco."""
    with connect_readonly(db_path) as connection:
        validate_schema(connection)
        data = {
            "assessments": fetch_all_rows(connection, "assessments"),
            "assessment_metrics": fetch_all_rows(connection, "assessment_metrics"),
            "trial_results": fetch_all_rows(connection, "trial_results"),
        }

    if not data["assessments"]:
        raise DashboardDataError(
            "Banco SQLite vazio. Importe pelo menos uma avaliacao antes de abrir o dashboard."
        )
    return data
