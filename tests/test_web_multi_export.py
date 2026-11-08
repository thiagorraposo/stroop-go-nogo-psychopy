"""Testes unitários e de domínio para exportações multi-granularidade (REQ-CSV-005)."""
import unittest

from stroop.domain.web_multi_export import (
    GRANULARITY_COLUMNS,
    validate_granularity_and_columns,
    format_csv_cell,
    serialize_multi_csv,
)


class WebMultiExportDomainTests(unittest.TestCase):
    def test_granularity_catalogs_exist(self):
        for g in ("pacientes", "avaliacoes", "tentativas", "metricas", "stroop_21_colunas"):
            self.assertIn(g, GRANULARITY_COLUMNS)
            granularity, columns = validate_granularity_and_columns(g)
            self.assertEqual(granularity, g)
            self.assertEqual(columns, list(GRANULARITY_COLUMNS[g]))

    def test_column_subset_filtering(self):
        _, cols = validate_granularity_and_columns("pacientes", ["participant_code", "active"])
        self.assertEqual(cols, ["participant_code", "active"])

    def test_invalid_granularity_or_column_rejected(self):
        with self.assertRaises(ValueError):
            validate_granularity_and_columns("invalida")
        with self.assertRaises(ValueError):
            validate_granularity_and_columns("pacientes", ["coluna_fantasma"])

    def test_formula_injection_protection(self):
        for malicious in ("=1+1", "+cmd", "-calc", "@SUM(A1)", "\t=evil", "\r-malicious"):
            with self.subTest(val=malicious):
                formatted = format_csv_cell(malicious, column="word", identification_mode="deidentified")
                self.assertTrue(formatted.startswith("'"), f"Failed to escape {malicious}: {formatted}")

    def test_nominal_vs_deidentified_masking(self):
        raw_name = "Paciente Silva"
        deidentified = format_csv_cell(raw_name, column="participant_name", identification_mode="deidentified")
        self.assertEqual(deidentified, "NAO_COLETADO")

        nominal = format_csv_cell(raw_name, column="participant_name", identification_mode="nominal")
        self.assertEqual(nominal, raw_name)

    def test_null_and_absence_handling(self):
        self.assertEqual(format_csv_cell(None, column="reaction_time_seconds", identification_mode="deidentified"), "")
        self.assertEqual(format_csv_cell(float("nan"), column="metric_value", identification_mode="deidentified"), "")

    def test_serialize_csv_end_to_end(self):
        rows = [
            {
                "assessment_id": "ASS-001",
                "project_code": "PROJ1",
                "participant_code": "PAT-001",
                "participant_name": "Fulano de Tal",
                "visit": "V1",
                "trial_number": 1,
                "block": "main",
                "word": "AZUL",
                "ink_color": "azul",
                "condition": "congruent",
                "correct_response": "space",
                "key_pressed": "space",
                "correct": True,
                "error_type": "hit",
                "reaction_time_seconds": 0.512345,
            }
        ]
        columns = ["assessment_id", "participant_code", "participant_name", "reaction_time_seconds", "correct"]

        # Deidentified
        csv_deid = serialize_multi_csv(rows, granularity="tentativas", columns=columns, identification_mode="deidentified")
        self.assertIn("ASS-001", csv_deid)
        self.assertIn("PAT-001", csv_deid)
        self.assertIn("NAO_COLETADO", csv_deid)
        self.assertNotIn("Fulano de Tal", csv_deid)
        self.assertIn("0.512345", csv_deid)
        self.assertIn("1", csv_deid)

        # Nominal
        csv_nom = serialize_multi_csv(rows, granularity="tentativas", columns=columns, identification_mode="nominal")
        self.assertIn("Fulano de Tal", csv_nom)


if __name__ == "__main__":
    unittest.main()
