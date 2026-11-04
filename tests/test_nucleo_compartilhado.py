"""Regressoes da extracao do nucleo, usando apenas fixtures sinteticas."""

from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from scripts import importar_csv_sqlite, instrumentos
from stroop.domain.assessment import NormalizedAssessment
from stroop.domain.errors import ImportValidationError, InstrumentValidationError
from stroop.domain.stroop import calculate_metrics
from stroop.ingestion.instruments import load_instrument_csv


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "csv" / "valido_minimo.csv"


class NucleoCompartilhadoTests(unittest.TestCase):
    def test_imports_anteriores_preservam_contratos_e_excecoes(self):
        self.assertIs(importar_csv_sqlite.ImportValidationError, ImportValidationError)
        self.assertIs(instrumentos.InstrumentValidationError, InstrumentValidationError)
        self.assertIs(instrumentos.NormalizedAssessment, NormalizedAssessment)
        self.assertIs(importar_csv_sqlite.calculate_metrics, calculate_metrics)
        self.assertIs(instrumentos.load_instrument_csv, load_instrument_csv)

    def test_normalizacao_independe_de_site_packages_interface_banco_e_clis(self):
        # -S desabilita site-packages: o nucleo precisa apenas da biblioteca padrao.
        code = """
from pathlib import Path
import sys
from stroop.ingestion.instruments import load_instrument_csv
assessment = load_instrument_csv(Path(sys.argv[1]))
metrics = {item['metric_code']: item['metric_value'] for item in assessment.metrics}
assert len(assessment.trial_values) == 4
assert len(metrics) == 12
assert metrics['accuracy'] == 50.0
assert metrics['hits'] == metrics['correct_rejections'] == 1.0
assert metrics['omission_errors'] == metrics['commission_errors'] == 1.0
for module in sys.modules:
    assert module.split('.')[0] not in {
        'scripts', 'dashboard', 'streamlit', 'psycopg', 'sqlite3', 'fastapi'
    }, module
"""
        result = subprocess.run(
            [sys.executable, "-S", "-c", code, str(FIXTURE)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_sqlite_preserva_importacao_duplicidade_e_force_fora_da_raiz(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "synthetic.sqlite3"
            command = [
                sys.executable, str(ROOT / "scripts" / "importar_csv_sqlite.py"),
                str(FIXTURE), "--db", str(database),
            ]
            for options, expected in (([], 0), ([], 1), (["--force"], 0)):
                with self.subTest(options=options, expected=expected):
                    result = subprocess.run(
                        command + options, cwd=directory,
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, expected, result.stderr)
            with sqlite3.connect(database) as connection:
                counts = [
                    connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in ("assessments", "assessment_metrics", "trial_results")
                ]
            self.assertEqual(counts, [1, 12, 4])

    def test_cli_postgres_valida_sem_banco_por_caminho_e_por_modulo(self):
        with tempfile.TemporaryDirectory() as directory:
            commands = (
                ([sys.executable, str(ROOT / "scripts" / "importar_csv_postgres.py")], directory),
                ([sys.executable, "-m", "scripts.importar_csv_postgres"], ROOT),
            )
            for command, cwd in commands:
                with self.subTest(command=command):
                    result = subprocess.run(
                        command + [str(FIXTURE), "--validate-only"], cwd=cwd,
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("validated; tentativas=4; metricas=12", result.stdout)


if __name__ == "__main__":
    unittest.main()
