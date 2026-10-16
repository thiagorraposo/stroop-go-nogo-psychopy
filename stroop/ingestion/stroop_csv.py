"""Leitura do CSV oficial e normalizacao das tentativas existentes."""

from __future__ import annotations

import csv
from pathlib import Path

from stroop.domain.errors import ImportValidationError
from stroop.domain.stroop import (
    CANONICAL_COLUMNS,
    parse_optional_reaction_time,
    validate_rows,
)


def read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise ImportValidationError(f"Arquivo nao encontrado: {csv_path}")
    if not csv_path.is_file():
        raise ImportValidationError(f"Caminho nao e arquivo: {csv_path}")

    errors: list[str] = []
    rows: list[dict[str, str]] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as file_obj:
        reader = csv.reader(file_obj)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ImportValidationError("Arquivo CSV vazio.") from exc

        if header != CANONICAL_COLUMNS:
            raise ImportValidationError(
                "Cabecalho invalido. Esperado: " + ", ".join(CANONICAL_COLUMNS)
            )

        for line_number, values in enumerate(reader, start=2):
            if len(values) != len(CANONICAL_COLUMNS):
                errors.append(
                    f"Linha {line_number}: numero de campos {len(values)}; "
                    f"esperado {len(CANONICAL_COLUMNS)}."
                )
                continue
            rows.append(dict(zip(CANONICAL_COLUMNS, values)))

    if errors:
        raise ImportValidationError("\n".join(errors))
    if not rows:
        raise ImportValidationError("CSV sem tentativas.")
    return rows


def load_and_validate_csv(csv_path: Path) -> list[dict[str, str]]:
    rows = read_csv_rows(csv_path)
    validate_rows(rows)
    return rows


def row_to_trial_values(row: dict[str, str]) -> tuple[object, ...]:
    return (
        row["assessment_id"],
        row["block"],
        int(row["trial_number"]),
        row["word"],
        row["ink_color"],
        row["condition"],
        row["correct_response"] or None,
        row["key_pressed"] or None,
        parse_optional_reaction_time(row["reaction_time"]),
        int(row["correct"]),
        row["error_type"],
    )
