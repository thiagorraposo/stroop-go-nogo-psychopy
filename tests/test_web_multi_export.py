"""Testes unitários e de domínio para exportações multi-granularidade (REQ-CSV-005)."""
import copy
import csv
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

from stroop.domain.stroop import CANONICAL_COLUMNS, calculate_metrics
from stroop.domain.web_export import serialize_assessment_csv
from stroop.domain.web_multi_export import (
    GRANULARITY_COLUMNS,
    validate_granularity_and_columns,
    format_csv_cell,
    serialize_multi_csv,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analisar_stroop  # noqa: E402
from stroop.application.import_sqlite import import_csv  # noqa: E402


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

    def test_roundtrip_export_canonico_com_analisar_stroop_e_sqlite(self):
        """WEB-026: Comprova roundtrip do CSV 21 colunas com analisador e SQLite."""
        fixture_path = ROOT / "tests/fixtures/web_results_summary.json"
        shared = json.loads(fixture_path.read_text())
        case = shared["cases"][0]

        # Usa o CSV canônico da fixture sintética oficial da plataforma
        csv_text = case["expected_csv"]
        self.assertIn("congruent", csv_text)

        # 1. Valida roundtrip com scripts/analisar_stroop.py
        rows, errors = analisar_stroop.parse_rows_from_text(csv_text)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 16)
        validation_errors = analisar_stroop.validate_rows(rows)
        self.assertEqual(validation_errors, [])

        # 2. Valida cálculo de métricas oficiais
        metrics = {m["metric_code"]: m["metric_value"] for m in calculate_metrics(rows)}
        self.assertEqual(len(metrics), 12)
        self.assertIn("accuracy", metrics)
        self.assertIn("response_time", metrics)

        # 3. Valida roundtrip com importador SQLite oficial
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "stroop_exportado.csv"
            csv_file.write_text(csv_text, encoding="utf-8")
            db_file = Path(tmpdir) / "teste.sqlite3"
            summary = import_csv(csv_file, db_file)
            self.assertEqual(summary["trials_imported"], 16)

            with sqlite3.connect(db_file) as conn:
                assessments_count = conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
                self.assertEqual(assessments_count, 1)
                metrics_count = conn.execute("SELECT COUNT(*) FROM assessment_metrics").fetchone()[0]
                self.assertEqual(metrics_count, 12)
                trials_count = conn.execute("SELECT COUNT(*) FROM trial_results").fetchone()[0]
                self.assertEqual(trials_count, 16)

    def test_roundtrip_granularidades_avancadas_com_sqlite(self):
        """WEB-026: Comprova compatibilidade das granularidades com carregamento tabular SQLite."""
        sample_data = {
            "pacientes": [
                {
                    "patient_id": "00000000-0000-0000-0000-000000000001",
                    "participant_code": "PAT-20261108-000001",
                    "participant_name": "Paciente Sintetico A",
                    "initials": "PSA",
                    "active": True,
                    "created_at": "2026-11-08T12:00:00Z",
                }
            ],
            "avaliacoes": [
                {
                    "assessment_id": "00000000-0000-0000-0000-000000000002",
                    "project_id": "00000000-0000-0000-0000-000000000003",
                    "project_code": "PROJ_TEST",
                    "participant_code": "PAT-20261108-000001",
                    "participant_name": "Paciente Sintetico A",
                    "evaluator_code": "EVA-000001",
                    "evaluator_name": "Avaliador Sintetico",
                    "visit": "V1",
                    "started_at": "2026-11-08T12:30:00Z",
                    "completed_at": "2026-11-08T12:35:00Z",
                    "platform": "web",
                    "test_code": "stroop_go_nogo_ptbr",
                    "test_version": "0.1.0",
                }
            ],
            "tentativas": [
                {
                    "assessment_id": "00000000-0000-0000-0000-000000000002",
                    "project_code": "PROJ_TEST",
                    "participant_code": "PAT-20261108-000001",
                    "participant_name": "Paciente Sintetico A",
                    "visit": "V1",
                    "trial_number": 1,
                    "block": "main",
                    "word": "VERMELHO",
                    "ink_color": "red",
                    "condition": "congruent",
                    "correct_response": "space",
                    "key_pressed": "space",
                    "correct": True,
                    "error_type": "hit",
                    "reaction_time_seconds": 0.450,
                }
            ],
            "metricas": [
                {
                    "assessment_id": "00000000-0000-0000-0000-000000000002",
                    "project_code": "PROJ_TEST",
                    "participant_code": "PAT-20261108-000001",
                    "participant_name": "Paciente Sintetico A",
                    "visit": "V1",
                    "metric_code": "hits",
                    "metric_label": "Acertos",
                    "metric_value": 1,
                    "unit": "count",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "granularidades.sqlite3"
            with sqlite3.connect(db_path) as conn:
                for granularity, rows in sample_data.items():
                    csv_text = serialize_multi_csv(
                        rows,
                        granularity=granularity,
                        columns=list(GRANULARITY_COLUMNS[granularity]),
                        identification_mode="deidentified",
                    )
                    # Verifica que o CSV parseia com delimitadores padrão
                    reader = list(csv.DictReader(io.StringIO(csv_text)))
                    self.assertEqual(len(reader), len(rows))
                    cols = list(reader[0].keys())

                    # Cria tabela e insere no SQLite para comprovar roundtrip tabular
                    conn.execute(f"CREATE TABLE {granularity} ({', '.join(f'{c} TEXT' for c in cols)})")
                    placeholders = ", ".join(["?"] * len(cols))
                    for r in reader:
                        conn.execute(
                            f"INSERT INTO {granularity} VALUES ({placeholders})",
                            [r[c] for c in cols],
                        )
                    count = conn.execute(f"SELECT COUNT(*) FROM {granularity}").fetchone()[0]
                    self.assertEqual(count, len(rows))


if __name__ == "__main__":
    unittest.main()
