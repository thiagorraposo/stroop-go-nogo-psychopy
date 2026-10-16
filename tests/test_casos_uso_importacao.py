"""Casos de uso reutilizaveis sem carregar interfaces, com dados sinteticos."""

from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from scripts import importar_csv_postgres, importar_csv_sqlite
from stroop.application import import_postgres, import_sqlite
from stroop.application.errors import DuplicateAssessmentError, PostgresImportError


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "csv" / "valido_minimo.csv"


class CasosUsoImportacaoTests(unittest.TestCase):
    def test_clis_reexportam_casos_de_uso_e_mesmas_excecoes(self):
        self.assertIs(importar_csv_sqlite.import_csv, import_sqlite.import_csv)
        self.assertIs(importar_csv_sqlite.import_rows, import_sqlite.import_rows)
        self.assertIs(importar_csv_sqlite.import_normalized, import_sqlite.import_normalized)
        self.assertIs(importar_csv_postgres.import_csv, import_postgres.import_csv)
        self.assertIs(importar_csv_postgres.PostgresImportError, PostgresImportError)
        self.assertIs(importar_csv_postgres.DuplicateAssessmentError, DuplicateAssessmentError)

    def test_casos_de_uso_nao_carregam_clis_ou_interfaces(self):
        code = """
import sys
from pathlib import Path
from stroop.application.import_postgres import import_csv
from stroop.application import import_sqlite
result = import_csv(Path(sys.argv[1]), validate_only=True)
assert result == {'status': 'validated', 'trials': 4, 'metrics': 12}
for name in sys.modules:
    assert name.split('.')[0] not in {'scripts', 'dashboard', 'streamlit', 'fastapi'}, name
"""
        result = subprocess.run(
            [sys.executable, "-c", code, str(FIXTURE)], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sqlite_reutilizavel_sem_site_packages_e_sem_postgres(self):
        code = """
import sys
from pathlib import Path
from stroop.application.import_sqlite import import_csv
result = import_csv(Path(sys.argv[1]), Path(sys.argv[2]))
assert result['trials_imported'] == 4
assert result['metrics_imported'] == 12
for name in sys.modules:
    assert name.split('.')[0] not in {'scripts', 'dashboard', 'psycopg', 'streamlit'}, name
"""
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "synthetic.sqlite3"
            result = subprocess.run(
                [sys.executable, "-S", "-c", code, str(FIXTURE), str(database)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute(
                    "SELECT metric_value FROM assessment_metrics WHERE metric_code = 'accuracy'"
                ).fetchone(), (50.0,))

    def test_cli_sqlite_por_modulo_preserva_duplicidade_e_force(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "synthetic.sqlite3"
            command = [sys.executable, "-m", "scripts.importar_csv_sqlite",
                       str(FIXTURE), "--db", str(database)]
            for extra, expected in (([], 0), ([], 1), (["--force"], 0)):
                with self.subTest(extra=extra):
                    result = subprocess.run(
                        command + extra, cwd=ROOT,
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, expected, result.stderr)
            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessments").fetchone(), (1,))
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM trial_results").fetchone(), (4,))


if __name__ == "__main__":
    unittest.main()
