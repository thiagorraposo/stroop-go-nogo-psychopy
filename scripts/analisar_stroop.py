#!/usr/bin/env python3
"""Valida e resume um CSV unificado do Stroop Go/No-Go."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path
from statistics import median


CANONICAL_COLUMNS = [
    "project",
    "participant_id",
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

REQUIRED_NON_EMPTY = {
    "project",
    "participant_id",
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


def is_loop_csv_path(path: str | Path) -> bool:
    name = Path(path).name
    return name.endswith("_pratica_loop.csv") or name.endswith("_principal_loop.csv")


def write_canonical_csv(rows: list[dict[str, str]], output: io.TextIOBase) -> None:
    writer = csv.DictWriter(
        output,
        fieldnames=CANONICAL_COLUMNS,
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in CANONICAL_COLUMNS})


def _read_csv_stream(stream: io.TextIOBase) -> tuple[list[dict[str, str]], list[str]]:
    reader = csv.reader(stream)
    errors: list[str] = []

    try:
        header = next(reader)
    except StopIteration:
        return [], ["Arquivo CSV vazio."]

    if header != CANONICAL_COLUMNS:
        errors.append(
            "Cabecalho invalido. Esperado: "
            + ", ".join(CANONICAL_COLUMNS)
        )

    rows: list[dict[str, str]] = []
    for line_number, values in enumerate(reader, start=2):
        if len(values) != len(CANONICAL_COLUMNS):
            errors.append(
                f"Linha {line_number}: numero de campos {len(values)}; "
                f"esperado {len(CANONICAL_COLUMNS)}."
            )
            continue
        rows.append(dict(zip(CANONICAL_COLUMNS, values)))

    return rows, errors


def read_canonical_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if is_loop_csv_path(path):
        return [], [
            "Arquivo parece ser CSV automatico de loop. Use o CSV canonico nomeado pelo assessment_id."
        ]
    if not path.exists():
        return [], [f"Arquivo nao encontrado: {path}"]
    if not path.is_file():
        return [], [f"Caminho nao e arquivo: {path}"]

    with path.open("r", newline="", encoding="utf-8-sig") as file_obj:
        return _read_csv_stream(file_obj)


def parse_rows_from_text(text: str) -> tuple[list[dict[str, str]], list[str]]:
    return _read_csv_stream(io.StringIO(text))


def _parse_positive_int(value: str) -> bool:
    try:
        return int(str(value).strip()) > 0
    except ValueError:
        return False


def _parse_reaction_time(value: str) -> float | None:
    if value == "":
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return parsed


def expected_outcome(row: dict[str, str]) -> tuple[str, str, str]:
    condition = row.get("condition", "")
    key_pressed = row.get("key_pressed", "")

    if condition == "congruent":
        if key_pressed == "space":
            return "space", "1", "hit"
        return "space", "0", "omission"

    if condition == "incongruent":
        if key_pressed == "space":
            return "", "0", "commission"
        return "", "1", "correct_rejection"

    return "", "", ""


def validate_record(row: dict[str, str], row_number: int) -> list[str]:
    errors: list[str] = []

    missing = [column for column in CANONICAL_COLUMNS if column not in row]
    extra = [column for column in row if column not in CANONICAL_COLUMNS]
    if missing:
        errors.append(f"Linha {row_number}: colunas ausentes: {', '.join(missing)}.")
    if extra:
        errors.append(f"Linha {row_number}: colunas extras: {', '.join(extra)}.")

    for column in REQUIRED_NON_EMPTY:
        if row.get(column, "") == "":
            errors.append(f"Linha {row_number}: campo obrigatorio vazio: {column}.")

    if row.get("block") not in ALLOWED_BLOCKS:
        errors.append(f"Linha {row_number}: block invalido: {row.get('block')!r}.")
    if row.get("condition") not in ALLOWED_CONDITIONS:
        errors.append(
            f"Linha {row_number}: condition invalida: {row.get('condition')!r}."
        )
    if row.get("error_type") not in ALLOWED_ERROR_TYPES:
        errors.append(
            f"Linha {row_number}: error_type invalido: {row.get('error_type')!r}."
        )
    if row.get("key_pressed") not in {"", "space"}:
        errors.append(
            f"Linha {row_number}: key_pressed invalido: {row.get('key_pressed')!r}."
        )
    if row.get("correct") not in {"0", "1"}:
        errors.append(f"Linha {row_number}: correct deve ser 0 ou 1.")
    if not _parse_positive_int(row.get("trial_number", "")):
        errors.append(f"Linha {row_number}: trial_number deve ser inteiro positivo.")

    expected_response, expected_correct, expected_error = expected_outcome(row)
    if expected_error:
        if row.get("correct_response", "") != expected_response:
            errors.append(
                f"Linha {row_number}: correct_response incompativel com condition."
            )
        if row.get("correct", "") != expected_correct:
            errors.append(f"Linha {row_number}: correct incompativel com resposta.")
        if row.get("error_type", "") != expected_error:
            errors.append(f"Linha {row_number}: error_type incompativel.")

    rt_value = row.get("reaction_time", "")
    if row.get("key_pressed") == "space":
        if _parse_reaction_time(rt_value) is None:
            errors.append(
                f"Linha {row_number}: reaction_time deve ser numerico e maior que zero."
            )
    elif rt_value != "":
        errors.append(
            f"Linha {row_number}: reaction_time deve ficar vazio sem resposta."
        )

    return errors


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        errors.extend(validate_record(row, row_number))
    return errors


def calculate_main_metrics(rows: list[dict[str, str]]) -> dict[str, float | int | None]:
    main_rows = [row for row in rows if row["block"] == "main"]
    total_valid_trials = len(main_rows)
    go_trials = [row for row in main_rows if row["condition"] == "congruent"]
    no_go_trials = [row for row in main_rows if row["condition"] == "incongruent"]
    hits = [row for row in main_rows if row["error_type"] == "hit"]
    omissions = [row for row in main_rows if row["error_type"] == "omission"]
    correct_rejections = [
        row for row in main_rows if row["error_type"] == "correct_rejection"
    ]
    commissions = [row for row in main_rows if row["error_type"] == "commission"]
    hit_rts = [float(row["reaction_time"]) for row in hits if row["reaction_time"]]

    def percent(numerator: int, denominator: int) -> float:
        return (numerator / denominator) * 100 if denominator else 0.0

    return {
        "total_valid_trials": total_valid_trials,
        "total_go_trials": len(go_trials),
        "total_no_go_trials": len(no_go_trials),
        "hits": len(hits),
        "omission_errors": len(omissions),
        "correct_rejections": len(correct_rejections),
        "commission_errors": len(commissions),
        "accuracy": percent(len(hits) + len(correct_rejections), total_valid_trials),
        "accuracy_go_trials": percent(len(hits), len(go_trials)),
        "accuracy_no_go_trials": percent(len(correct_rejections), len(no_go_trials)),
        "omission_errors_percentage": percent(len(omissions), len(go_trials)),
        "response_time": median(hit_rts) if hit_rts else None,
    }


def print_summary(path: Path, rows: list[dict[str, str]]) -> None:
    first = rows[0] if rows else {}
    metrics = calculate_main_metrics(rows)
    practice_total = sum(1 for row in rows if row["block"] == "practice")
    main_total = sum(1 for row in rows if row["block"] == "main")

    print(f"Arquivo: {path}")
    print(f"assessment_id: {first.get('assessment_id', '')}")
    print(f"project: {first.get('project', '')}")
    print(f"participant_id: {first.get('participant_id', '')}")
    print(f"visit: {first.get('visit', '')}")
    print(f"test_code: {first.get('test_code', '')}")
    print(f"test_version: {first.get('test_version', '')}")
    print("")
    print(f"Total de tentativas: {len(rows)}")
    print(f"Total de pratica: {practice_total}")
    print(f"Total de bloco principal: {main_total}")
    print(f"Hits: {metrics['hits']}")
    print(f"Omissoes: {metrics['omission_errors']}")
    print(f"Rejeicoes corretas: {metrics['correct_rejections']}")
    print(f"Comissoes: {metrics['commission_errors']}")
    print("")
    print(f"accuracy: {metrics['accuracy']:.2f}%")
    print(f"accuracy_go_trials: {metrics['accuracy_go_trials']:.2f}%")
    print(f"accuracy_no_go_trials: {metrics['accuracy_no_go_trials']:.2f}%")
    print(f"omission_errors: {metrics['omission_errors']}")
    print(
        "omission_errors_percentage: "
        f"{metrics['omission_errors_percentage']:.2f}%"
    )
    print(f"commission_errors: {metrics['commission_errors']}")
    response_time = metrics["response_time"]
    if response_time is None:
        print("response_time: indisponivel")
    else:
        print(f"response_time: {response_time:.6f} s")
    print("")
    print("Validacao: OK")
    print("Resultados descritivos; sem interpretacao clinica ou normativa.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida e resume um CSV unificado do Stroop Go/No-Go."
    )
    parser.add_argument("csv_path", type=Path, help="Caminho do CSV canonico nomeado pelo assessment_id")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    rows, read_errors = read_canonical_csv(args.csv_path)
    validation_errors = [] if read_errors else validate_rows(rows)
    errors = read_errors + validation_errors
    if errors:
        print("Validacao: ERRO", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not rows:
        print("Validacao: ERRO", file=sys.stderr)
        print("- CSV sem tentativas.", file=sys.stderr)
        return 1
    print_summary(args.csv_path, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
