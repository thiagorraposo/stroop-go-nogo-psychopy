import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dashboard import app  # noqa: E402


SCHEMA_PATH = ROOT / "scripts" / "db_schema.sql"


def metric_rows(assessment_id, accuracy, go, no_go, omissions, commissions, rt):
    values = {
        "accuracy": accuracy,
        "accuracy_go_trials": go,
        "accuracy_no_go_trials": no_go,
        "omission_errors": omissions,
        "omission_errors_percentage": omissions * 10,
        "commission_errors": commissions,
        "response_time": rt,
        "total_trials": 4,
        "total_go_trials": 2,
        "total_no_go_trials": 2,
        "hits": 2 - omissions,
        "correct_rejections": 2 - commissions,
    }
    return [
        (assessment_id, code, code, float(value), "unit", "2026-07-15T12:00:00+00:00")
        for code, value in values.items()
    ]


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "stroop_results.sqlite3"
        self.create_database()

    def tearDown(self):
        self.tmp.cleanup()

    def create_database(self):
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            assessments = [
                (
                    "A1",
                    "stroop_go_nogo_ptbr",
                    "0.2.2",
                    "PROJETO_A",
                    "P001",
                    "PARTICIPANTE_UM",
                    None,
                    "V1",
                    "AV01",
                    "2026-07-01",
                    "2026-07-01T09:00:00-03:00",
                    "data/P001.csv",
                    "2026-07-15T12:00:00+00:00",
                    "valid",
                ),
                (
                    "A2",
                    "stroop_go_nogo_ptbr",
                    "0.2.2",
                    "PROJETO_A",
                    "P001",
                    "PARTICIPANTE_UM",
                    None,
                    "V2",
                    "AV01",
                    "2026-07-10",
                    "2026-07-10T09:00:00-03:00",
                    "data/P001_v2.csv",
                    "2026-07-15T12:00:00+00:00",
                    "valid",
                ),
                (
                    "A3",
                    "stroop_go_nogo_ptbr",
                    "0.2.3",
                    "PROJETO_B",
                    "P002",
                    "PARTICIPANTE_DOIS",
                    None,
                    "V1",
                    "AV02",
                    "2026-07-12",
                    "2026-07-12T09:00:00-03:00",
                    "data/P002.csv",
                    "2026-07-15T12:00:00+00:00",
                    "valid",
                ),
            ]
            connection.executemany(
                """
                INSERT INTO assessments (
                    assessment_id, test_code, test_version, project,
                    participant_id, participant_name, initials, visit,
                    evaluator, assessment_date, started_at, source_file,
                    imported_at, import_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                assessments,
            )
            metrics = []
            metrics.extend(metric_rows("A1", 75, 50, 100, 1, 0, 0.5))
            metrics.extend(metric_rows("A2", 100, 100, 100, 0, 0, 0.4))
            metrics.extend(metric_rows("A3", 50, 100, 0, 0, 2, 0.8))
            connection.executemany(
                """
                INSERT INTO assessment_metrics (
                    assessment_id, metric_code, metric_label, metric_value,
                    unit, calculated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                metrics,
            )
            trial_rows = [
                ("A1", "main", 1, "VERDE", "green", "congruent", "space", "space", 0.5, 1, "hit"),
                ("A1", "main", 2, "AZUL", "blue", "congruent", "space", None, None, 0, "omission"),
                ("A1", "main", 3, "ROSA", "yellow", "incongruent", None, None, None, 1, "correct_rejection"),
                ("A2", "main", 1, "VERDE", "green", "congruent", "space", "space", 0.4, 1, "hit"),
                ("A3", "main", 1, "ROXO", "blue", "incongruent", None, "space", 0.8, 0, "commission"),
            ]
            connection.executemany(
                """
                INSERT INTO trial_results (
                    assessment_id, block, trial_number, word, ink_color,
                    condition, correct_response, key_pressed, reaction_time,
                    correct, error_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                trial_rows,
            )

    def test_conexao_sqlite_somente_leitura(self):
        with app.connect_readonly(self.db_path) as connection:
            count = connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
            self.assertEqual(count, 3)
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("CREATE TABLE escrita_bloqueada (id INTEGER)")

    def test_erro_amigavel_quando_banco_nao_existe(self):
        missing = Path(self.tmp.name) / "missing.sqlite3"
        with self.assertRaises(app.DashboardDataError) as ctx:
            app.load_sqlite_data(missing)
        self.assertIn("Banco SQLite nao encontrado", str(ctx.exception))

    def test_leitura_das_tabelas_oficiais(self):
        data = app.load_sqlite_data(self.db_path)
        self.assertEqual(len(data["assessments"]), 3)
        self.assertEqual(len(data["assessment_metrics"]), 36)
        self.assertEqual(len(data["trial_results"]), 5)

    def test_schema_invalido_tem_erro_claro(self):
        invalid_path = Path(self.tmp.name) / "invalid.sqlite3"
        with sqlite3.connect(invalid_path) as connection:
            connection.execute("CREATE TABLE assessments (assessment_id TEXT)")

        with self.assertRaises(app.DashboardDataError) as ctx:
            app.load_sqlite_data(invalid_path)
        self.assertIn("Schema SQLite invalido", str(ctx.exception))

    def test_banco_vazio_tem_erro_claro(self):
        empty_path = Path(self.tmp.name) / "empty.sqlite3"
        with sqlite3.connect(empty_path) as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        with self.assertRaises(app.DashboardDataError) as ctx:
            app.load_sqlite_data(empty_path)
        self.assertIn("Banco SQLite vazio", str(ctx.exception))

    def test_montagem_da_tabela_agregada(self):
        data = app.load_sqlite_data(self.db_path)
        rows = app.build_assessment_table(data)

        self.assertEqual(len(rows), 3)
        first = rows[0]
        self.assertEqual(first["assessment_id"], "A1")
        self.assertEqual(first["project"], "PROJETO_A")
        self.assertEqual(first["participant_id"], "P001")
        self.assertEqual(first["accuracy"], 75.0)
        self.assertEqual(first["accuracy_go_trials"], 50.0)
        self.assertEqual(first["commission_errors"], 0.0)

    def test_filtros_por_campos_e_periodo(self):
        rows = app.build_assessment_table(app.load_sqlite_data(self.db_path))
        filters = app.DashboardFilters(
            start_date=date(2026, 7, 2),
            end_date=date(2026, 7, 12),
            project=("PROJETO_A",),
            participant_id=("P001",),
            visit=("V2",),
            evaluator=("AV01",),
        )

        filtered = app.filter_assessment_table(rows, filters)

        self.assertEqual([row["assessment_id"] for row in filtered], ["A2"])

    def test_calculo_dos_cards_principais(self):
        rows = app.build_assessment_table(app.load_sqlite_data(self.db_path))
        cards = app.calculate_cards(rows)

        self.assertEqual(cards["total_assessments"], 3)
        self.assertEqual(cards["unique_participants"], 2)
        self.assertAlmostEqual(cards["mean_accuracy"], 75.0)
        self.assertAlmostEqual(cards["median_accuracy"], 75.0)
        self.assertAlmostEqual(cards["median_response_time"], 0.5)
        self.assertEqual(cards["total_omissions"], 1)
        self.assertEqual(cards["total_commissions"], 2)

    def test_detalhe_de_avaliacao_e_contagem_de_tentativas(self):
        data = app.load_sqlite_data(self.db_path)
        trials = app.trials_for_assessment(data, "A1")
        counts = app.error_type_counts(trials)

        self.assertEqual(len(trials), 3)
        self.assertEqual(counts["hit"], 1)
        self.assertEqual(counts["omission"], 1)
        self.assertEqual(counts["correct_rejection"], 1)
        self.assertEqual(counts["commission"], 0)

    def test_ausencia_de_linguagem_clinica_proibida(self):
        source = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8").lower()
        forbidden_terms = [
            "percentil",
            "abaixo da média",
            "abaixo da media",
            "normativo",
            "normativa",
            "normalidade",
        ]
        for term in forbidden_terms:
            self.assertNotIn(term, source)

    def test_dashboard_nao_escreve_no_banco(self):
        before_mtime = os.stat(self.db_path).st_mtime_ns
        before_size = os.stat(self.db_path).st_size

        data = app.load_sqlite_data(self.db_path)
        rows = app.build_assessment_table(data)
        app.filter_assessment_table(rows, app.DashboardFilters(project=("PROJETO_A",)))
        app.calculate_cards(rows)

        self.assertEqual(os.stat(self.db_path).st_mtime_ns, before_mtime)
        self.assertEqual(os.stat(self.db_path).st_size, before_size)


if __name__ == "__main__":
    unittest.main()
