#!/usr/bin/env python3
import csv
from pathlib import Path
from statistics import median


DATA_DIR = Path("data")
EXPECTED_COLUMNS = {
    "participant",
    "session",
    "trial_number",
    "word",
    "ink_color",
    "condition",
    "correct_response",
    "key_pressed",
    "reaction_time",
    "correct",
    "error_type",
}
OPTIONAL_COLUMNS = {"block"}


def parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "sim", "yes"}


def parse_float(value):
    value = str(value).strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_trials():
    trials = []
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        with csv_path.open(newline="", encoding="utf-8-sig") as file_obj:
            reader = csv.DictReader(file_obj)
            if not reader.fieldnames:
                continue
            if not EXPECTED_COLUMNS.issubset(set(reader.fieldnames)):
                continue
            for row in reader:
                row["source_file"] = csv_path.name
                row["block"] = row.get("block") or "unknown"
                row["correct_bool"] = parse_bool(row.get("correct", ""))
                row["rt_float"] = parse_float(row.get("reaction_time", ""))
                trials.append(row)
    return trials


def print_accuracy(trials):
    total = len(trials)
    correct = sum(1 for trial in trials if trial["correct_bool"])
    accuracy = correct / total if total else 0
    print(f"Acuracia geral: {accuracy:.2%} ({correct}/{total})")

    for condition in sorted({trial["condition"] for trial in trials}):
        condition_trials = [trial for trial in trials if trial["condition"] == condition]
        condition_correct = sum(1 for trial in condition_trials if trial["correct_bool"])
        condition_accuracy = condition_correct / len(condition_trials)
        print(
            f"Acuracia {condition}: "
            f"{condition_accuracy:.2%} ({condition_correct}/{len(condition_trials)})"
        )

    for block in sorted({trial["block"] for trial in trials}):
        block_trials = [trial for trial in trials if trial["block"] == block]
        block_correct = sum(1 for trial in block_trials if trial["correct_bool"])
        block_accuracy = block_correct / len(block_trials)
        print(f"Acuracia bloco {block}: {block_accuracy:.2%} ({block_correct}/{len(block_trials)})")


def print_rt_comparison(trials):
    rts_by_condition = {}
    for trial in trials:
        if not trial["correct_bool"] or trial["rt_float"] is None:
            continue
        rts_by_condition.setdefault(trial["condition"], []).append(trial["rt_float"])

    print("\nTempo de reacao mediano em respostas corretas:")
    for condition in sorted(rts_by_condition):
        values = rts_by_condition[condition]
        print(f"{condition}: {median(values):.4f} s (n={len(values)})")

    congruent = rts_by_condition.get("congruente", [])
    incongruent = rts_by_condition.get("incongruente", [])
    if congruent and incongruent:
        diff = median(incongruent) - median(congruent)
        print(f"Diferenca incongruente - congruente: {diff:.4f} s")
    else:
        print("Comparacao de RT indisponivel: faltam respostas corretas em uma condicao.")


def main():
    if not DATA_DIR.exists():
        raise SystemExit("Pasta data/ nao encontrada.")

    trials = load_trials()
    if not trials:
        raise SystemExit(
            "Nenhum CSV compativel encontrado em data/. "
            "Execute o experimento antes da analise."
        )

    print(f"Arquivos analisados em {DATA_DIR}/")
    print_accuracy(trials)
    print_rt_comparison(trials)


if __name__ == "__main__":
    main()
