"""Componentes visuais reutilizaveis do dashboard Streamlit."""

from __future__ import annotations

from typing import Any

from dashboard.transformations import (
    accuracy_by_visit,
    calculate_cards,
    count_by_date,
    error_type_counts,
    errors_by_project,
    filtered_csv_bytes,
    metrics_for_assessment,
    numeric_values,
    option_values,
    participant_evolution,
    to_dataframe,
    trials_for_assessment,
    visible_assessment_rows,
)


def render_metric_card(streamlit_module: Any, label: str, value: str) -> None:
    streamlit_module.metric(label, value)


def format_percent(value: float | int) -> str:
    return f"{float(value):.1f}%"


def format_seconds(value: float | int) -> str:
    return f"{float(value):.3f} s"


def render_summary_cards(streamlit_module: Any, rows: list[dict[str, Any]]) -> None:
    cards = calculate_cards(rows)
    card_columns = streamlit_module.columns(7)
    with card_columns[0]:
        render_metric_card(streamlit_module, "Avaliacoes", str(cards["total_assessments"]))
    with card_columns[1]:
        render_metric_card(streamlit_module, "Participantes", str(cards["unique_participants"]))
    with card_columns[2]:
        render_metric_card(
            streamlit_module, "Precisao media", format_percent(cards["mean_accuracy"])
        )
    with card_columns[3]:
        render_metric_card(
            streamlit_module,
            "Precisao mediana",
            format_percent(cards["median_accuracy"]),
        )
    with card_columns[4]:
        render_metric_card(
            streamlit_module,
            "RT mediano",
            format_seconds(cards["median_response_time"]),
        )
    with card_columns[5]:
        render_metric_card(streamlit_module, "Omissoes", str(cards["total_omissions"]))
    with card_columns[6]:
        render_metric_card(streamlit_module, "Comissoes", str(cards["total_commissions"]))


def render_charts(streamlit_module: Any, rows: list[dict[str, Any]]) -> None:
    streamlit_module.subheader("Graficos")
    chart_left, chart_right = streamlit_module.columns(2)
    with chart_left:
        streamlit_module.caption("Avaliacoes por data")
        streamlit_module.bar_chart(
            to_dataframe(count_by_date(rows)), x="assessment_date", y="assessments"
        )
        streamlit_module.caption("Distribuicao do tempo de reacao")
        streamlit_module.bar_chart(
            to_dataframe(
                [
                    {"response_time": value}
                    for value in numeric_values(rows, "response_time")
                ]
            ),
            y="response_time",
        )
    with chart_right:
        streamlit_module.caption("Precisao por visita")
        streamlit_module.bar_chart(
            to_dataframe(accuracy_by_visit(rows)), x="visit", y="accuracy"
        )
        streamlit_module.caption("Omissoes e comissoes por projeto")
        streamlit_module.bar_chart(
            to_dataframe(errors_by_project(rows)),
            x="project",
            y=["omission_errors", "commission_errors"],
        )

    participant_options = option_values(rows, "participant_id")
    selected_participant = streamlit_module.selectbox(
        "Evolucao de participante",
        participant_options,
        index=0 if participant_options else None,
    )
    evolution = participant_evolution(rows, selected_participant)
    if evolution:
        streamlit_module.line_chart(
            to_dataframe(evolution), x="visit", y=["accuracy", "response_time"]
        )


def render_assessment_table(
    streamlit_module: Any, rows: list[dict[str, Any]]
) -> None:
    streamlit_module.subheader("Avaliacoes filtradas")
    visible_rows = visible_assessment_rows(rows)
    streamlit_module.dataframe(
        to_dataframe(visible_rows), use_container_width=True, hide_index=True
    )
    streamlit_module.download_button(
        "Baixar visao filtrada em CSV",
        data=filtered_csv_bytes(rows),
        file_name="stroop_dashboard_visao_filtrada.csv",
        mime="text/csv",
    )


def render_assessment_detail(
    streamlit_module: Any,
    data: dict[str, list[dict[str, Any]]],
    rows: list[dict[str, Any]],
) -> None:
    streamlit_module.subheader("Detalhe da avaliacao")
    assessment_labels = [
        f"{row['assessment_date']} | {row['participant_id']} | {row['visit']} | {row['assessment_id']}"
        for row in rows
    ]
    selected_label = streamlit_module.selectbox("Selecionar avaliacao", assessment_labels)
    selected_assessment_id = selected_label.rsplit(" | ", 1)[-1]
    selected_assessment = next(
        row for row in rows if row["assessment_id"] == selected_assessment_id
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
    streamlit_module.write("Metadados da sessao")
    streamlit_module.dataframe(
        to_dataframe(
            [
                {"campo": column, "valor": selected_assessment.get(column)}
                for column in metadata_columns
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    detail_metrics = metrics_for_assessment(data, selected_assessment_id)
    streamlit_module.write("Metricas completas")
    streamlit_module.dataframe(
        to_dataframe(detail_metrics), use_container_width=True, hide_index=True
    )

    detail_trials = trials_for_assessment(data, selected_assessment_id)
    streamlit_module.write("Contagem por tipo de resposta")
    streamlit_module.dataframe(
        to_dataframe(
            [
                {"error_type": error_type, "count": count}
                for error_type, count in error_type_counts(detail_trials).items()
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    streamlit_module.write("Tentativas")
    streamlit_module.dataframe(
        to_dataframe(detail_trials), use_container_width=True, hide_index=True
    )
