import csv
import io
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import analisar_stroop  # noqa: E402


def make_row(**overrides):
    row = {
        "project": "PILOTO_STROOP",
        "participant_id": "P_TEST",
        "initials": "",
        "visit": "V1",
        "evaluator": "AV01",
        "assessment_id": "00000000-0000-0000-0000-000000000000",
        "assessment_date": "2026-07-06",
        "started_at": "2026-07-06T10:00:00-03:00",
        "test_code": "stroop_go_nogo_ptbr",
        "test_version": "0.2.0",
        "block": "main",
        "trial_number": "1",
        "word": "VERMELHO",
        "ink_color": "red",
        "condition": "congruent",
        "correct_response": "space",
        "key_pressed": "space",
        "reaction_time": "0.512",
        "correct": "1",
        "error_type": "hit",
    }
    row.update(overrides)
    return row


class CsvUnificadoTests(unittest.TestCase):
    def assert_valid(self, row):
        self.assertEqual(analisar_stroop.validate_rows([row]), [])

    def test_hit_valido(self):
        self.assert_valid(make_row())

    def test_omission_valida(self):
        self.assert_valid(
            make_row(
                key_pressed="",
                reaction_time="",
                correct="0",
                error_type="omission",
            )
        )

    def test_correct_rejection_valida(self):
        self.assert_valid(
            make_row(
                condition="incongruent",
                correct_response="",
                key_pressed="",
                reaction_time="",
                correct="1",
                error_type="correct_rejection",
            )
        )

    def test_commission_valida(self):
        self.assert_valid(
            make_row(
                condition="incongruent",
                correct_response="",
                key_pressed="space",
                reaction_time="0.641",
                correct="0",
                error_type="commission",
            )
        )

    def test_campo_obrigatorio_ausente(self):
        row = make_row()
        row.pop("assessment_id")
        errors = analisar_stroop.validate_rows([row])
        self.assertTrue(any("colunas ausentes" in error for error in errors))

    def test_condition_incompativel_com_correct_response(self):
        row = make_row(condition="incongruent", correct_response="space")
        errors = analisar_stroop.validate_rows([row])
        self.assertTrue(any("correct_response incompativel" in error for error in errors))

    def test_reaction_time_zero_sem_resposta(self):
        row = make_row(key_pressed="", reaction_time="0", correct="0", error_type="omission")
        errors = analisar_stroop.validate_rows([row])
        self.assertTrue(any("reaction_time deve ficar vazio" in error for error in errors))

    def test_numero_incorreto_de_colunas(self):
        header = ",".join(analisar_stroop.CANONICAL_COLUMNS)
        linha_incompleta = ",".join(["x"] * 19)
        _, errors = analisar_stroop.parse_rows_from_text(
            f"{header}\n{linha_incompleta}\n"
        )
        self.assertTrue(any("numero de campos" in error for error in errors))

    def test_rejeita_csv_automatico_de_loop(self):
        self.assertTrue(
            analisar_stroop.is_loop_csv_path("data/abc_pratica_loop.csv")
        )
        self.assertTrue(
            analisar_stroop.is_loop_csv_path("data/abc_principal_loop.csv")
        )
        self.assertFalse(analisar_stroop.is_loop_csv_path("data/abc_trials.csv"))
        self.assertFalse(
            analisar_stroop.is_loop_csv_path(
                "data/00000000-0000-0000-0000-000000000000.csv"
            )
        )
        self.assertFalse(analisar_stroop.is_loop_csv_path("data/P_TEST.csv"))

    def test_exportador_canonico_ordem_e_20_colunas(self):
        output = io.StringIO()
        analisar_stroop.write_canonical_csv([make_row()], output)
        output.seek(0)
        reader = csv.reader(output)
        header = next(reader)
        row = next(reader)
        self.assertEqual(header, analisar_stroop.CANONICAL_COLUMNS)
        self.assertEqual(len(header), 20)
        self.assertEqual(len(row), 20)


if __name__ == "__main__":
    unittest.main()
