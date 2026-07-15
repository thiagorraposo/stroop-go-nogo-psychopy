#!/usr/bin/env python3
"""Dashboard local Streamlit para resultados do Stroop Go/No-Go."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import mean, median
from typing import Any


DEFAULT_DB_PATH = Path("database/stroop_results.sqlite3")
DISCLAIMER_TEXT = (
    "Resultados descritivos. Este dashboard não representa avaliação clínica ou diagnóstico."
)

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

METRIC_CODES = [
    "accuracy",
    "accuracy_go_trials",
    "accuracy_no_go_trials",
    "omission_errors",
    "omission_errors_percentage",
    "commission_errors",
    "response_time",
    "total_trials",
    "total_go_trials",
    "total_no_go_trials",
    "hits",
    "correct_rejections",
]

AGGREGATED_COLUMNS = [
    "assessment_date",
    "project",
    "participant_id",
    "participant_name",
    "visit",
    "evaluator",
    "test_version",
    "accuracy",
    "accuracy_go_trials",
    "accuracy_no_go_trials",
    "omission_errors",
    "commission_errors",
    "response_time",
]


class DashboardDataError(Exception):
    """Erro amigavel para dados ausentes, vazios ou invalidos."""


@dataclass(frozen=True)
class DashboardFilters:
    start_date: date | None = None
    end_date: date | None = None
    project: tuple[str, ...] = ()
    participant_id: tuple[str, ...] = ()
    participant_name: tuple[str, ...] = ()
    visit: tuple[str, ...] = ()
    evaluator: tuple[str, ...] = ()
    test_code: tuple[str, ...] = ()
    test_version: tuple[str, ...] = ()


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


def load_sqlite_data(db_path: Path = DEFAULT_DB_PATH) -> dict[str, list[dict[str, Any]]]:
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


def metric_map(metrics: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    mapped: dict[str, dict[str, float]] = {}
    for row in metrics:
        assessment_id = str(row["assessment_id"])
        metric_code = str(row["metric_code"])
        mapped.setdefault(assessment_id, {})[metric_code] = float(row["metric_value"])
    return mapped


def build_assessment_table(data: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Monta tabela agregada de uma linha por avaliacao."""
    metrics_by_assessment = metric_map(data["assessment_metrics"])
    rows: list[dict[str, Any]] = []

    for assessment in data["assessments"]:
        assessment_id = str(assessment["assessment_id"])
        row = {
            "assessment_id": assessment_id,
            "assessment_date": assessment["assessment_date"],
            "project": assessment["project"],
            "participant_id": assessment["participant_id"],
            "participant_name": assessment["participant_name"],
            "visit": assessment["visit"],
            "evaluator": assessment["evaluator"],
            "test_code": assessment["test_code"],
            "test_version": assessment["test_version"],
            "started_at": assessment["started_at"],
            "source_file": assessment["source_file"],
            "imported_at": assessment["imported_at"],
            "import_status": assessment["import_status"],
        }
        for metric_code in METRIC_CODES:
            row[metric_code] = metrics_by_assessment.get(assessment_id, {}).get(
                metric_code, 0.0
            )
        rows.append(row)

    return sorted(rows, key=lambda row: (row["assessment_date"], row["started_at"]))


def parse_iso_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def option_values(rows: list[dict[str, Any]], column: str) -> list[str]:
    return sorted({str(row[column]) for row in rows if row.get(column) not in (None, "")})


def matches_selection(value: Any, selected: tuple[str, ...]) -> bool:
    return not selected or str(value) in selected


def filter_assessment_table(
    rows: list[dict[str, Any]], filters: DashboardFilters
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for row in rows:
        assessment_date = parse_iso_date(row.get("assessment_date"))
        if filters.start_date and (
            assessment_date is None or assessment_date < filters.start_date
        ):
            continue
        if filters.end_date and (
            assessment_date is None or assessment_date > filters.end_date
        ):
            continue
        if not matches_selection(row.get("project"), filters.project):
            continue
        if not matches_selection(row.get("participant_id"), filters.participant_id):
            continue
        if not matches_selection(row.get("participant_name"), filters.participant_name):
            continue
        if not matches_selection(row.get("visit"), filters.visit):
            continue
        if not matches_selection(row.get("evaluator"), filters.evaluator):
            continue
        if not matches_selection(row.get("test_code"), filters.test_code):
            continue
        if not matches_selection(row.get("test_version"), filters.test_version):
            continue
        filtered.append(row)
    return filtered


def numeric_values(rows: list[dict[str, Any]], column: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(column)
        if value is None:
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    return values


def calculate_cards(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    accuracies = numeric_values(rows, "accuracy")
    response_times = numeric_values(rows, "response_time")
    return {
        "total_assessments": len(rows),
        "unique_participants": len(
            {row["participant_id"] for row in rows if row.get("participant_id")}
        ),
        "mean_accuracy": mean(accuracies) if accuracies else 0.0,
        "median_accuracy": median(accuracies) if accuracies else 0.0,
        "median_response_time": median(response_times) if response_times else 0.0,
        "total_omissions": int(sum(numeric_values(rows, "omission_errors"))),
        "total_commissions": int(sum(numeric_values(rows, "commission_errors"))),
    }


def count_by_date(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("assessment_date") or "")
        if key:
            counts[key] = counts.get(key, 0) + 1
    return [
        {"assessment_date": key, "assessments": value}
        for key, value in sorted(counts.items())
    ]


def accuracy_by_visit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("visit") or ""), []).extend(
            numeric_values([row], "accuracy")
        )
    return [
        {"visit": visit, "accuracy": mean(values) if values else 0.0}
        for visit, values in sorted(grouped.items())
        if visit
    ]


def errors_by_project(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, float]] = {}
    for row in rows:
        project = str(row.get("project") or "")
        if not project:
            continue
        grouped.setdefault(project, {"omission_errors": 0.0, "commission_errors": 0.0})
        grouped[project]["omission_errors"] += float(row.get("omission_errors") or 0.0)
        grouped[project]["commission_errors"] += float(row.get("commission_errors") or 0.0)
    return [
        {
            "project": project,
            "omission_errors": values["omission_errors"],
            "commission_errors": values["commission_errors"],
        }
        for project, values in sorted(grouped.items())
    ]


def participant_evolution(
    rows: list[dict[str, Any]], participant_id: str | None
) -> list[dict[str, Any]]:
    if not participant_id:
        return []
    selected = [row for row in rows if row.get("participant_id") == participant_id]
    return [
        {
            "assessment_date": row["assessment_date"],
            "visit": row["visit"],
            "accuracy": row["accuracy"],
            "response_time": row["response_time"],
        }
        for row in sorted(selected, key=lambda item: (item["assessment_date"], item["visit"]))
    ]


def visible_assessment_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{column: row.get(column) for column in AGGREGATED_COLUMNS} for row in rows]


def metrics_for_assessment(
    data: dict[str, list[dict[str, Any]]], assessment_id: str
) -> list[dict[str, Any]]:
    return [
        row
        for row in data["assessment_metrics"]
        if str(row["assessment_id"]) == assessment_id
    ]


def trials_for_assessment(
    data: dict[str, list[dict[str, Any]]], assessment_id: str
) -> list[dict[str, Any]]:
    rows = [
        row for row in data["trial_results"] if str(row["assessment_id"]) == assessment_id
    ]
    return sorted(rows, key=lambda row: int(row["trial_number"]))


def error_type_counts(trials: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "hit": 0,
        "omission": 0,
        "correct_rejection": 0,
        "commission": 0,
    }
    for trial in trials:
        error_type = str(trial.get("error_type") or "")
        if error_type in counts:
            counts[error_type] += 1
    return counts


def to_dataframe(rows: list[dict[str, Any]]):
    import pandas as pd

    return pd.DataFrame(rows)


def filtered_csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    dataframe = to_dataframe(visible_assessment_rows(rows))
    return dataframe.to_csv(index=False).encode("utf-8")


def render_metric_card(streamlit_module: Any, label: str, value: str) -> None:
    streamlit_module.metric(label, value)


def format_percent(value: float | int) -> str:
    return f"{float(value):.1f}%"


def format_seconds(value: float | int) -> str:
    return f"{float(value):.3f} s"


def render_dashboard(db_path: Path = DEFAULT_DB_PATH) -> None:
    import streamlit as st

    st.set_page_config(
        page_title="Dashboard Stroop Go/No-Go",
        page_icon="ST",
        layout="wide",
    )
    st.title("Dashboard Stroop Go/No-Go")
    st.warning(DISCLAIMER_TEXT)

    try:
        data = load_sqlite_data(db_path)
        assessment_rows = build_assessment_table(data)
    except DashboardDataError as exc:
        st.error(str(exc))
        return
    except sqlite3.Error as exc:
        st.error(f"Erro ao ler SQLite: {exc}")
        return

    dates = [parse_iso_date(row["assessment_date"]) for row in assessment_rows]
    valid_dates = [value for value in dates if value is not None]
    min_date = min(valid_dates) if valid_dates else None
    max_date = max(valid_dates) if valid_dates else None

    st.sidebar.header("Filtros")
    start_date = st.sidebar.date_input("Inicio", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Fim", value=max_date, min_value=min_date, max_value=max_date)

    filters = DashboardFilters(
        start_date=start_date if isinstance(start_date, date) else None,
        end_date=end_date if isinstance(end_date, date) else None,
        project=tuple(
            st.sidebar.multiselect("Projeto", option_values(assessment_rows, "project"))
        ),
        participant_id=tuple(
            st.sidebar.multiselect(
                "Participant ID", option_values(assessment_rows, "participant_id")
            )
        ),
        participant_name=tuple(
            st.sidebar.multiselect(
                "Participant name", option_values(assessment_rows, "participant_name")
            )
        ),
        visit=tuple(st.sidebar.multiselect("Visita", option_values(assessment_rows, "visit"))),
        evaluator=tuple(
            st.sidebar.multiselect("Avaliador", option_values(assessment_rows, "evaluator"))
        ),
        test_code=tuple(
            st.sidebar.multiselect("Teste", option_values(assessment_rows, "test_code"))
        ),
        test_version=tuple(
            st.sidebar.multiselect("Versao", option_values(assessment_rows, "test_version"))
        ),
    )

    filtered_rows = filter_assessment_table(assessment_rows, filters)
    if not filtered_rows:
        st.info("Nenhuma avaliacao encontrada para os filtros selecionados.")
        return

    cards = calculate_cards(filtered_rows)
    card_columns = st.columns(7)
    with card_columns[0]:
        render_metric_card(st, "Avaliacoes", str(cards["total_assessments"]))
    with card_columns[1]:
        render_metric_card(st, "Participantes", str(cards["unique_participants"]))
    with card_columns[2]:
        render_metric_card(st, "Precisao media", format_percent(cards["mean_accuracy"]))
    with card_columns[3]:
        render_metric_card(
            st, "Precisao mediana", format_percent(cards["median_accuracy"])
        )
    with card_columns[4]:
        render_metric_card(
            st, "RT mediano", format_seconds(cards["median_response_time"])
        )
    with card_columns[5]:
        render_metric_card(st, "Omissoes", str(cards["total_omissions"]))
    with card_columns[6]:
        render_metric_card(st, "Comissoes", str(cards["total_commissions"]))

    st.subheader("Graficos")
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.caption("Avaliacoes por data")
        st.bar_chart(to_dataframe(count_by_date(filtered_rows)), x="assessment_date", y="assessments")
        st.caption("Distribuicao do tempo de reacao")
        st.bar_chart(
            to_dataframe(
                [{"response_time": value} for value in numeric_values(filtered_rows, "response_time")]
            ),
            y="response_time",
        )
    with chart_right:
        st.caption("Precisao por visita")
        st.bar_chart(to_dataframe(accuracy_by_visit(filtered_rows)), x="visit", y="accuracy")
        st.caption("Omissoes e comissoes por projeto")
        st.bar_chart(
            to_dataframe(errors_by_project(filtered_rows)),
            x="project",
            y=["omission_errors", "commission_errors"],
        )

    participant_options = option_values(filtered_rows, "participant_id")
    selected_participant = st.selectbox(
        "Evolucao de participante", participant_options, index=0 if participant_options else None
    )
    evolution = participant_evolution(filtered_rows, selected_participant)
    if evolution:
        st.line_chart(to_dataframe(evolution), x="visit", y=["accuracy", "response_time"])

    st.subheader("Avaliacoes filtradas")
    visible_rows = visible_assessment_rows(filtered_rows)
    st.dataframe(to_dataframe(visible_rows), use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar visao filtrada em CSV",
        data=filtered_csv_bytes(filtered_rows),
        file_name="stroop_dashboard_visao_filtrada.csv",
        mime="text/csv",
    )

    st.subheader("Detalhe da avaliacao")
    assessment_labels = [
        f"{row['assessment_date']} | {row['participant_id']} | {row['visit']} | {row['assessment_id']}"
        for row in filtered_rows
    ]
    selected_label = st.selectbox("Selecionar avaliacao", assessment_labels)
    selected_assessment_id = selected_label.rsplit(" | ", 1)[-1]
    selected_assessment = next(
        row for row in filtered_rows if row["assessment_id"] == selected_assessment_id
    )

    metadata_columns = [
        "assessment_id",
        "assessment_date",
        "started_at",
        "project",
        "participant_id",
        "participant_name",
        "visit",
        "evaluator",
        "test_code",
        "test_version",
        "source_file",
        "imported_at",
        "import_status",
    ]
    st.write("Metadados da sessao")
    st.dataframe(
        to_dataframe(
            [{"campo": column, "valor": selected_assessment.get(column)} for column in metadata_columns]
        ),
        use_container_width=True,
        hide_index=True,
    )

    detail_metrics = metrics_for_assessment(data, selected_assessment_id)
    st.write("Metricas completas")
    st.dataframe(to_dataframe(detail_metrics), use_container_width=True, hide_index=True)

    detail_trials = trials_for_assessment(data, selected_assessment_id)
    st.write("Contagem por tipo de resposta")
    st.dataframe(
        to_dataframe(
            [
                {"error_type": error_type, "count": count}
                for error_type, count in error_type_counts(detail_trials).items()
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.write("Tentativas")
    st.dataframe(to_dataframe(detail_trials), use_container_width=True, hide_index=True)


def main() -> None:
    render_dashboard(DEFAULT_DB_PATH)


if __name__ == "__main__":
    main()
