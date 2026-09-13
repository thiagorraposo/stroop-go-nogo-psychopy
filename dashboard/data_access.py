"""Acesso somente leitura ao SQLite legado e ao PostgreSQL operacional."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql


DEFAULT_DB_PATH = Path("database/stroop_results.sqlite3")
DEFAULT_PAGE_SIZE = 1000

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


def _page_size(value: int | str | None = None) -> int:
    raw = value if value is not None else os.environ.get(
        "DASHBOARD_PAGE_SIZE", str(DEFAULT_PAGE_SIZE)
    )
    try:
        parsed = int(raw)
    except (TypeError, ValueError):
        raise DashboardDataError("DASHBOARD_PAGE_SIZE invalido.") from None
    if not 1 <= parsed <= 10_000:
        raise DashboardDataError("DASHBOARD_PAGE_SIZE fora do intervalo permitido.")
    return parsed


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


POSTGRES_TABLE_ORDER = {
    "assessments": "assessment_id",
    "assessment_metrics": "metric_id",
    "trial_results": "trial_result_id",
}
POSTGRES_TABLES = tuple(POSTGRES_TABLE_ORDER)


def connect_postgres_readonly(database_url: str) -> psycopg.Connection:
    """Abre uma conexao PostgreSQL com transacoes somente leitura."""
    if not database_url:
        raise DashboardDataError("DASHBOARD_DATABASE_URL nao configurada.")
    try:
        connection = psycopg.connect(database_url, connect_timeout=5)
        connection.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        connection.commit()
        return connection
    except psycopg.Error as exc:
        raise DashboardDataError(
            "Nao foi possivel conectar ao PostgreSQL do dashboard."
        ) from exc


def postgres_table_columns(
    connection: psycopg.Connection, table_name: str
) -> set[str]:
    rows = connection.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (table_name,),
    ).fetchall()
    return {row[0] for row in rows}


def validate_postgres_schema(connection: psycopg.Connection) -> None:
    missing_tables: list[str] = []
    missing_columns: list[str] = []
    for table_name, expected_columns in REQUIRED_COLUMNS.items():
        actual = postgres_table_columns(connection, table_name)
        if not actual:
            missing_tables.append(table_name)
            continue
        missing = sorted(expected_columns - actual)
        if missing:
            missing_columns.append(f"{table_name}: {', '.join(missing)}")
    if missing_tables:
        raise DashboardDataError(
            "Schema PostgreSQL invalido. Tabelas ausentes: "
            + ", ".join(sorted(missing_tables))
        )
    if missing_columns:
        raise DashboardDataError(
            "Schema PostgreSQL invalido. Colunas ausentes: "
            + " | ".join(missing_columns)
        )


def fetch_postgres_rows(
    connection: psycopg.Connection,
    table_name: str,
    *,
    page_size: int | str | None = None,
) -> list[dict[str, Any]]:
    """Busca uma tabela em lotes para nao materializar o cursor de uma vez."""
    if table_name not in POSTGRES_TABLE_ORDER:
        raise DashboardDataError("Tabela PostgreSQL desconhecida.")
    rows: list[dict[str, Any]] = []
    batch_size = _page_size(page_size)
    order_column = POSTGRES_TABLE_ORDER[table_name]
    with connection.cursor(name=f"dashboard_{table_name}") as cursor:
        cursor.execute(
            sql.SQL("SELECT * FROM {} ORDER BY {};").format(
                sql.Identifier(table_name), sql.Identifier(order_column)
            )
        )
        columns = [description.name for description in cursor.description]
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            rows.extend(dict(zip(columns, row)) for row in batch)
    return rows


def load_postgres_data(
    database_url: str,
    *,
    page_size: int | str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Le as tabelas oficiais usando a credencial somente leitura do dashboard."""
    try:
        with connect_postgres_readonly(database_url) as connection:
            validate_postgres_schema(connection)
            data = {
                table_name: fetch_postgres_rows(
                    connection, table_name, page_size=page_size
                )
                for table_name in POSTGRES_TABLES
            }
    except DashboardDataError:
        raise
    except psycopg.Error as exc:
        raise DashboardDataError(
            "Falha ao ler o PostgreSQL do dashboard."
        ) from exc

    if not data["assessments"]:
        raise DashboardDataError(
            "Banco PostgreSQL vazio. Importe pelo menos uma avaliacao antes de abrir o dashboard."
        )
    return data


def load_dashboard_data(
    db_path: Path = DEFAULT_DB_PATH,
    *,
    database_url: str | None = None,
    page_size: int | str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Usa PostgreSQL configurado; sem URL, preserva o fluxo SQLite local."""
    configured_url = database_url
    if configured_url is None:
        configured_url = os.environ.get("DASHBOARD_DATABASE_URL") or os.environ.get(
            "DATABASE_URL", ""
        )
    if configured_url:
        return load_postgres_data(configured_url, page_size=page_size)
    return load_sqlite_data(db_path)
