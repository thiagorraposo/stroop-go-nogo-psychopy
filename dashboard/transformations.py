"""Transformacoes puras dos dados exibidos pelo dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from statistics import mean, median
from typing import Any


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


def metric_map(metrics: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    mapped: dict[str, dict[str, float]] = {}
    for row in metrics:
        assessment_id = str(row["assessment_id"])
        metric_code = str(row["metric_code"])
        mapped.setdefault(assessment_id, {})[metric_code] = float(row["metric_value"])
    return mapped


def build_assessment_table(
    data: dict[str, list[dict[str, Any]]], metric_codes: list[str] | tuple[str, ...] | None = None
) -> list[dict[str, Any]]:
    """Monta tabela agregada de uma linha por avaliacao."""
    metrics_by_assessment = metric_map(data["assessment_metrics"])
    if metric_codes is None:
        discovered = [str(row["metric_code"]) for row in data["assessment_metrics"]]
        metric_codes = tuple(dict.fromkeys([*METRIC_CODES, *discovered]))
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
        for metric_code in (metric_codes or METRIC_CODES):
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


def visible_assessment_rows(
    rows: list[dict[str, Any]], metric_codes: list[str] | tuple[str, ...] | None = None
) -> list[dict[str, Any]]:
    columns = AGGREGATED_COLUMNS
    if metric_codes is not None:
        columns = [
            "assessment_date", "test_code", "project", "participant_id",
            "participant_name", "visit", "evaluator", *metric_codes,
        ]
    return [{column: row.get(column) for column in columns} for row in rows]


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


def filtered_csv_bytes(
    rows: list[dict[str, Any]], metric_codes: list[str] | tuple[str, ...] | None = None
) -> bytes:
    dataframe = to_dataframe(visible_assessment_rows(rows, metric_codes))
    return dataframe.to_csv(index=False).encode("utf-8")
