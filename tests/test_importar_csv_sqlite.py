import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import importar_csv_sqlite  # noqa: E402


def make_row(**overrides):
    row = {
        "project": "PILOTO_STROOP",
        "participant_id": "P_TEST",
        "participant_name": "NOME_REDIGIDO",
        "initials": "",
        "visit": "V1",
        "evaluator": "AV01",
        "assessment_id": "00000000-0000-0000-0000-000000000001",
        "assessment_date": "2026-07-09",
        "started_at": "2026-07-09T10:00:00-03:00",
        "test_code": "stroop_go_nogo_ptbr",
        "test_version": "0.2.2",
        "block": "main",
        "trial_number": "1",
        "word": "VERMELHO",
        "ink_color": "red",
        "condition": "congruent",
        "correct_response": "space",
        "key_pressed": "space",
        "reaction_time": "0.500",
        "correct": "1",
        "error_type": "hit",
    }
    row.update(overrides)
    return row


def valid_rows():
    return [
        make_row(trial_number="1", reaction_time="0.400"),
        make_row(
            trial_number="2",
            word="AZUL",
            ink_color="blue",
            key_pressed="",
            reaction_time="",
            correct="0",
            error_type="omission",
        ),
        make_row(
            trial_number="3",
            word="VERDE",
            ink_color="yellow",
            condition="incongruent",
            correct_response="",
            key_pressed="",
            reaction_time="",
            correct="1",
            error_type="correct_rejection",
        ),
        make_row(
            trial_number="4",
            word="AMARELO",
            ink_color="blue",
            condition="incongruent",
            correct_response="",
            key_pressed="space",
            reaction_time="0.800",
            correct="0",
            error_type="commission",
        ),
        make_row(trial_number="5", word="ROSA", ink_color="pink", reaction_time="0.600"),
    ]


class ImportarCsvSqliteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv_path = self.root / "entrada.csv"
        self.db_path = self.root / "database" / "stroop_results.sqlite3"

    def tearDown(self):
        self.tmp.cleanup()

    def write_csv(self, rows, header=None):
        header = header or importar_csv_sqlite.CANONICAL_COLUMNS
        with self.csv_path.open("w", newline="", encoding="utf-8") as file_obj:
            writer = csv.DictWriter(file_obj, fieldnames=header, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({column: row.get(column, "") for column in header})

    def connect(self):
        return sqlite3.connect(self.db_path)

    def test_importacao_valida_cria_banco_e_linhas(self):
        self.write_csv(valid_rows())

        summary = importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        self.assertTrue(self.db_path.exists())
        self.assertEqual(summary["trials_imported"], 5)
        self.assertEqual(summary["metrics_imported"], 12)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM trial_results").fetchone()[0], 5)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM assessment_metrics").fetchone()[0], 12)

    def test_bloqueia_cabecalho_invalido(self):
        header = importar_csv_sqlite.CANONICAL_COLUMNS[:-1]
        self.write_csv(valid_rows(), header=header)

        with self.assertRaises(importar_csv_sqlite.ImportValidationError) as ctx:
            importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        self.assertIn("Cabecalho invalido", str(ctx.exception))
        self.assertFalse(self.db_path.exists())

    def test_bloqueia_duplicidade_sem_force(self):
        self.write_csv(valid_rows())
        importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        with self.assertRaises(importar_csv_sqlite.ImportValidationError) as ctx:
            importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        self.assertIn("assessment_id ja importado", str(ctx.exception))

    def test_reimporta_com_force(self):
        self.write_csv(valid_rows())
        importar_csv_sqlite.import_csv(self.csv_path, self.db_path)
        updated = valid_rows()
        updated[0]["reaction_time"] = "0.700"
        self.write_csv(updated)

        importar_csv_sqlite.import_csv(self.csv_path, self.db_path, force=True)

        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM trial_results").fetchone()[0], 5)
            response_time = conn.execute(
                "SELECT metric_value FROM assessment_metrics WHERE metric_code = 'response_time'"
            ).fetchone()[0]
            self.assertAlmostEqual(response_time, 0.65)

    def test_calculo_correto_das_metricas(self):
        self.write_csv(valid_rows())
        importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        with self.connect() as conn:
            rows = conn.execute(
                "SELECT metric_code, metric_value FROM assessment_metrics"
            ).fetchall()
        metrics = {code: value for code, value in rows}

        self.assertEqual(metrics["total_trials"], 5.0)
        self.assertEqual(metrics["total_go_trials"], 3.0)
        self.assertEqual(metrics["total_no_go_trials"], 2.0)
        self.assertEqual(metrics["hits"], 2.0)
        self.assertEqual(metrics["correct_rejections"], 1.0)
        self.assertEqual(metrics["omission_errors"], 1.0)
        self.assertEqual(metrics["commission_errors"], 1.0)
        self.assertAlmostEqual(metrics["accuracy"], 60.0)
        self.assertAlmostEqual(metrics["accuracy_go_trials"], 66.66666666666666)
        self.assertAlmostEqual(metrics["accuracy_no_go_trials"], 50.0)
        self.assertAlmostEqual(metrics["omission_errors_percentage"], 33.33333333333333)
        self.assertEqual(metrics["response_time"], 0.5)

    def test_rollback_em_erro_de_insercao(self):
        self.write_csv(valid_rows())
        original_calculate_metrics = importar_csv_sqlite.calculate_metrics

        def broken_metrics(rows):
            metrics = original_calculate_metrics(rows)
            metrics[0]["metric_value"] = None
            return metrics

        importar_csv_sqlite.calculate_metrics = broken_metrics
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                importar_csv_sqlite.import_csv(self.csv_path, self.db_path)
        finally:
            importar_csv_sqlite.calculate_metrics = original_calculate_metrics

        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM trial_results").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM assessment_metrics").fetchone()[0], 0)

    def test_reaction_time_ausente_em_sem_resposta_e_valido(self):
        rows = [
            make_row(
                key_pressed="",
                reaction_time="",
                correct="0",
                error_type="omission",
            )
        ]
        self.write_csv(rows)

        summary = importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        self.assertEqual(summary["trials_imported"], 1)

    def test_bloqueia_reaction_time_zero(self):
        self.write_csv([make_row(reaction_time="0")])

        with self.assertRaises(importar_csv_sqlite.ImportValidationError) as ctx:
            importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        self.assertIn("reaction_time deve ser numerico e maior que zero", str(ctx.exception))

    def test_bloqueia_incoerencia_condition_correct_response_error_type(self):
        self.write_csv(
            [
                make_row(
                    condition="incongruent",
                    correct_response="space",
                    correct="1",
                    error_type="hit",
                )
            ]
        )

        with self.assertRaises(importar_csv_sqlite.ImportValidationError) as ctx:
            importar_csv_sqlite.import_csv(self.csv_path, self.db_path)

        message = str(ctx.exception)
        self.assertIn("correct_response incompativel", message)
        self.assertIn("error_type incompativel", message)


if __name__ == "__main__":
    unittest.main()
