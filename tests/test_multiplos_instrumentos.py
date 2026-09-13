import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import importar_csv_sqlite as sqlite_importer
from scripts import importar_csv_postgres as postgres_importer
from scripts.instrumentos import InstrumentValidationError, load_instrument_csv
from dashboard.transformations import DashboardFilters, build_assessment_table, filter_assessment_table


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "csv"


class MultiplosInstrumentosTests(unittest.TestCase):
    def test_registro_normaliza_stroop_e_demo_sem_mistura(self):
        stroop = load_instrument_csv(FIXTURES / "valido_minimo.csv")
        demo = load_instrument_csv(FIXTURES / "instrumento_sintetico_demo.csv")
        self.assertEqual(stroop.adapter_code, "stroop_go_nogo_ptbr")
        self.assertEqual(len(stroop.trial_values), 4)
        self.assertEqual(len(stroop.metrics), 12)
        self.assertEqual(demo.adapter_code, "instrumento_sintetico_demo")
        self.assertEqual(demo.trial_values, [])
        self.assertEqual({m["metric_code"] for m in demo.metrics}, {"demo_total", "demo_mean"})

    def test_demo_rejeita_metrica_de_outro_instrumento(self):
        source = (FIXTURES / "instrumento_sintetico_demo.csv").read_text(encoding="utf-8")
        source = source.replace("demo_mean,Media demonstrativa", "accuracy,Precisao total")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demo.csv"
            path.write_text(source, encoding="utf-8")
            with self.assertRaises(InstrumentValidationError):
                load_instrument_csv(path)

    def test_demo_pode_ser_validado_pela_cli_postgres_sem_conexao(self):
        result = postgres_importer.import_csv(
            FIXTURES / "instrumento_sintetico_demo.csv", validate_only=True
        )
        self.assertEqual(result, {"status": "validated", "trials": 0, "metrics": 2})

    def test_stroop_e_demo_coexistem_no_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "synthetic.sqlite3"
            sqlite_importer.import_csv(FIXTURES / "valido_minimo.csv", db)
            sqlite_importer.import_csv(FIXTURES / "instrumento_sintetico_demo.csv", db)
            with sqlite3.connect(db) as connection:
                self.assertEqual(
                    connection.execute("SELECT test_code, COUNT(*) FROM assessments GROUP BY test_code ORDER BY test_code").fetchall(),
                    [("instrumento_sintetico_demo", 1), ("stroop_go_nogo_ptbr", 1)],
                )
                self.assertEqual(
                    connection.execute("SELECT test_code, COUNT(*) FROM assessments a LEFT JOIN assessment_metrics m USING (assessment_id) GROUP BY test_code ORDER BY test_code").fetchall(),
                    [("instrumento_sintetico_demo", 2), ("stroop_go_nogo_ptbr", 12)],
                )

    def test_dashboard_filtra_um_instrumento_sem_comparacao_cruzada(self):
        data = {
            "assessments": [
                {"assessment_id": "A_ST", "assessment_date": "2026-09-13", "project": "P",
                 "participant_id": "S1", "participant_name": "SINTETICO", "visit": "V1",
                 "evaluator": "E", "test_code": "stroop_go_nogo_ptbr", "test_version": "0.2.2",
                 "started_at": "2026-09-13T10:00:00-03:00", "source_file": "x", "imported_at": "x", "import_status": "valid"},
                {"assessment_id": "A_DE", "assessment_date": "2026-09-13", "project": "P",
                 "participant_id": "S1", "participant_name": "SINTETICO", "visit": "V1",
                 "evaluator": "E", "test_code": "instrumento_sintetico_demo", "test_version": "1.0",
                 "started_at": "2026-09-13T10:00:00-03:00", "source_file": "y", "imported_at": "x", "import_status": "valid"},
            ],
            "assessment_metrics": [
                {"assessment_id": "A_ST", "metric_code": "accuracy", "metric_value": 100},
                {"assessment_id": "A_DE", "metric_code": "demo_mean", "metric_value": 2.5},
            ],
            "trial_results": [],
        }
        rows = build_assessment_table(data)
        selected = filter_assessment_table(rows, DashboardFilters(test_code=("instrumento_sintetico_demo",)))
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["demo_mean"], 2.5)


if __name__ == "__main__":
    unittest.main()
