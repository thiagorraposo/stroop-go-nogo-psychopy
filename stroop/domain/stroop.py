"""Contrato, validacao e metricas Stroop extraidos sem mudanca de regras."""

from __future__ import annotations

from statistics import median

from stroop.domain.errors import ImportValidationError


CANONICAL_COLUMNS = [
    "project",
    "participant_id",
    "participant_name",
    "initials",
    "visit",
    "evaluator",
    "assessment_id",
    "assessment_date",
    "started_at",
    "test_code",
    "test_version",
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
]

ASSESSMENT_METADATA_COLUMNS = [
    "project",
    "participant_id",
    "participant_name",
    "initials",
    "visit",
    "evaluator",
    "assessment_id",
    "assessment_date",
    "started_at",
    "test_code",
    "test_version",
]

REQUIRED_NON_EMPTY = {
    "project",
    "participant_id",
    "participant_name",
    "visit",
    "evaluator",
    "assessment_id",
    "assessment_date",
    "started_at",
    "test_code",
    "test_version",
    "block",
    "trial_number",
    "word",
    "ink_color",
    "condition",
    "correct",
    "error_type",
}

ALLOWED_BLOCKS = {"practice", "main"}

ALLOWED_CONDITIONS = {"congruent", "incongruent"}

ALLOWED_ERROR_TYPES = {"hit", "omission", "correct_rejection", "commission"}

ALLOWED_KEYS = {"", "space"}

METRIC_DEFINITIONS = {
    "accuracy": ("Precisao total", "percent"),
    "accuracy_go_trials": ("Precisao em Go", "percent"),
    "accuracy_no_go_trials": ("Precisao em No-Go", "percent"),
    "omission_errors": ("Erros de omissao", "count"),
    "omission_errors_percentage": ("Percentual de omissoes", "percent"),
    "commission_errors": ("Erros de comissao", "count"),
    "response_time": ("Tempo de resposta", "seconds"),
    "total_trials": ("Total de tentativas", "count"),
    "total_go_trials": ("Total de tentativas Go", "count"),
    "total_no_go_trials": ("Total de tentativas No-Go", "count"),
    "hits": ("Hits", "count"),
    "correct_rejections": ("Rejeicoes corretas", "count"),
}


def parse_positive_int(value: str) -> int | None:
    try:
        parsed = int(str(value).strip())
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def parse_optional_reaction_time(value: str) -> float | None:
    if value == "":
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return parsed


def expected_outcome(row: dict[str, str]) -> tuple[str, str, str] | None:
    condition = row.get("condition", "")
    key_pressed = row.get("key_pressed", "")

    if condition == "congruent" and key_pressed == "space":
        return "space", "1", "hit"
    if condition == "congruent" and key_pressed == "":
        return "space", "0", "omission"
    if condition == "incongruent" and key_pressed == "":
        return "", "1", "correct_rejection"
    if condition == "incongruent" and key_pressed == "space":
        return "", "0", "commission"
    return None


def validate_row(row: dict[str, str], line_number: int) -> list[str]:
    errors: list[str] = []

    for column in REQUIRED_NON_EMPTY:
        if row.get(column, "") == "":
            errors.append(f"Linha {line_number}: campo obrigatorio vazio: {column}.")

    if row.get("block") not in ALLOWED_BLOCKS:
        errors.append(f"Linha {line_number}: block invalido: {row.get('block')!r}.")
    if row.get("condition") not in ALLOWED_CONDITIONS:
        errors.append(
            f"Linha {line_number}: condition invalida: {row.get('condition')!r}."
        )
    if row.get("error_type") not in ALLOWED_ERROR_TYPES:
        errors.append(
            f"Linha {line_number}: error_type invalido: {row.get('error_type')!r}."
        )
    if row.get("key_pressed") not in ALLOWED_KEYS:
        errors.append(
            f"Linha {line_number}: key_pressed invalido: {row.get('key_pressed')!r}."
        )
    if row.get("correct_response") not in ALLOWED_KEYS:
        errors.append(
            f"Linha {line_number}: correct_response invalido: "
            f"{row.get('correct_response')!r}."
        )
    if row.get("correct") not in {"0", "1"}:
        errors.append(f"Linha {line_number}: correct deve ser 0 ou 1.")
    if parse_positive_int(row.get("trial_number", "")) is None:
        errors.append(f"Linha {line_number}: trial_number deve ser inteiro positivo.")

    outcome = expected_outcome(row)
    if outcome is None:
        errors.append(f"Linha {line_number}: linha nao representa tentativa valida.")
    else:
        expected_response, expected_correct, expected_error = outcome
        if row.get("correct_response", "") != expected_response:
            errors.append(
                f"Linha {line_number}: correct_response incompativel com condition."
            )
        if row.get("correct", "") != expected_correct:
            errors.append(f"Linha {line_number}: correct incompativel.")
        if row.get("error_type", "") != expected_error:
            errors.append(f"Linha {line_number}: error_type incompativel.")

    reaction_time = row.get("reaction_time", "")
    if row.get("key_pressed") == "space":
        if parse_optional_reaction_time(reaction_time) is None:
            errors.append(
                f"Linha {line_number}: reaction_time deve ser numerico e maior que zero."
            )
    elif reaction_time != "":
        errors.append(
            f"Linha {line_number}: reaction_time deve ficar vazio quando nao ha resposta."
        )

    return errors


def validate_rows(rows: list[dict[str, str]]) -> None:
    errors: list[str] = []
    first = rows[0]

    for line_number, row in enumerate(rows, start=2):
        errors.extend(validate_row(row, line_number))
        for column in ASSESSMENT_METADATA_COLUMNS:
            if row.get(column, "") != first.get(column, ""):
                errors.append(
                    f"Linha {line_number}: metadado inconsistente: {column}."
                )

    if errors:
        raise ImportValidationError("\n".join(errors))


def percent(numerator: int, denominator: int) -> float:
    return (numerator / denominator) * 100 if denominator else 0.0


def calculate_metrics(rows: list[dict[str, str]]) -> list[dict[str, float | str]]:
    main_rows = [row for row in rows if row["block"] == "main"]
    total_trials = len(main_rows)
    go_trials = [row for row in main_rows if row["condition"] == "congruent"]
    no_go_trials = [row for row in main_rows if row["condition"] == "incongruent"]
    hits = [row for row in main_rows if row["error_type"] == "hit"]
    omissions = [row for row in main_rows if row["error_type"] == "omission"]
    correct_rejections = [
        row for row in main_rows if row["error_type"] == "correct_rejection"
    ]
    commissions = [row for row in main_rows if row["error_type"] == "commission"]
    hit_reaction_times = [
        float(row["reaction_time"]) for row in hits if row["reaction_time"]
    ]
    response_time = median(hit_reaction_times) if hit_reaction_times else 0.0

    values: dict[str, float] = {
        "accuracy": percent(len(hits) + len(correct_rejections), total_trials),
        "accuracy_go_trials": percent(len(hits), len(go_trials)),
        "accuracy_no_go_trials": percent(len(correct_rejections), len(no_go_trials)),
        "omission_errors": float(len(omissions)),
        "omission_errors_percentage": percent(len(omissions), len(go_trials)),
        "commission_errors": float(len(commissions)),
        "response_time": float(response_time),
        "total_trials": float(total_trials),
        "total_go_trials": float(len(go_trials)),
        "total_no_go_trials": float(len(no_go_trials)),
        "hits": float(len(hits)),
        "correct_rejections": float(len(correct_rejections)),
    }

    return [
        {
            "metric_code": metric_code,
            "metric_label": METRIC_DEFINITIONS[metric_code][0],
            "metric_value": values[metric_code],
            "unit": METRIC_DEFINITIONS[metric_code][1],
        }
        for metric_code in METRIC_DEFINITIONS
    ]
