#!/usr/bin/env python3
"""Ponto de entrada e composicao do dashboard Stroop Go/No-Go."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from dashboard.components import (
    format_percent,
    format_seconds,
    render_assessment_detail,
    render_assessment_table,
    render_charts,
    render_metric_card,
    render_summary_cards,
)
from dashboard.data_access import (
    DEFAULT_DB_PATH,
    REQUIRED_COLUMNS,
    REQUIRED_TABLES,
    DashboardDataError,
    connect_readonly,
    fetch_all_rows,
    load_sqlite_data,
    table_columns,
    validate_schema,
)
from dashboard.transformations import (
    AGGREGATED_COLUMNS,
    METRIC_CODES,
    DashboardFilters,
    accuracy_by_visit,
    build_assessment_table,
    calculate_cards,
    count_by_date,
    error_type_counts,
    errors_by_project,
    filter_assessment_table,
    filtered_csv_bytes,
    matches_selection,
    metric_map,
    metrics_for_assessment,
    numeric_values,
    option_values,
    parse_iso_date,
    participant_evolution,
    to_dataframe,
    trials_for_assessment,
    visible_assessment_rows,
)


DISCLAIMER_TEXT = (
    "Resultados descritivos. Este dashboard não representa avaliação clínica ou diagnóstico."
)


def render_dashboard(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Compoe a interface Streamlit com dados e componentes modulares."""
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
    start_date = st.sidebar.date_input(
        "Inicio", value=min_date, min_value=min_date, max_value=max_date
    )
    end_date = st.sidebar.date_input(
        "Fim", value=max_date, min_value=min_date, max_value=max_date
    )

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
        visit=tuple(
            st.sidebar.multiselect("Visita", option_values(assessment_rows, "visit"))
        ),
        evaluator=tuple(
            st.sidebar.multiselect(
                "Avaliador", option_values(assessment_rows, "evaluator")
            )
        ),
        test_code=tuple(
            st.sidebar.multiselect("Teste", option_values(assessment_rows, "test_code"))
        ),
        test_version=tuple(
            st.sidebar.multiselect(
                "Versao", option_values(assessment_rows, "test_version")
            )
        ),
    )

    filtered_rows = filter_assessment_table(assessment_rows, filters)
    if not filtered_rows:
        st.info("Nenhuma avaliacao encontrada para os filtros selecionados.")
        return

    render_summary_cards(st, filtered_rows)
    render_charts(st, filtered_rows)
    render_assessment_table(st, filtered_rows)
    render_assessment_detail(st, data, filtered_rows)


def main() -> None:
    render_dashboard(DEFAULT_DB_PATH)


if __name__ == "__main__":
    main()
