"""Dashboard PostgreSQL da Etapa 10 com banco descartavel e dados sinteticos."""

from __future__ import annotations

import os
import unittest

import psycopg

from dashboard.data_access import (
    DashboardDataError,
    connect_postgres_readonly,
    load_dashboard_data,
    load_postgres_data,
)
from scripts.migrations import apply_migrations


URL = os.environ.get("TEST_DATABASE_URL", "")


@unittest.skipUnless(URL, "TEST_DATABASE_URL nao configurada")
class DashboardPostgresIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        database_name = psycopg.conninfo.conninfo_to_dict(URL).get("dbname", "")
        if not database_name.startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco descartavel obrigatorio")

    def setUp(self) -> None:
        with psycopg.connect(URL, autocommit=True) as connection:
            connection.execute("DROP SCHEMA public CASCADE")
            connection.execute("CREATE SCHEMA public")
        apply_migrations(URL)
        with psycopg.connect(URL) as connection:
            connection.execute(
                """
                INSERT INTO assessments (
                    assessment_id, test_code, test_version, project,
                    participant_id, participant_name, initials, visit, evaluator,
                    assessment_date, started_at, source_file, imported_at, import_status
                ) VALUES (
                    'synthetic-dashboard-a', 'stroop_go_nogo_ptbr', '0.2.2',
                    'SYNTHETIC_PROJECT', 'SYNTHETIC_P001', 'SYNTHETIC_PARTICIPANT',
                    NULL, 'V1', 'SYNTHETIC_EVALUATOR', '2026-01-01',
                    '2026-01-01T10:00:00+00:00', 'synthetic.csv',
                    '2026-01-01T11:00:00+00:00', 'valid'
                )
                """
            )
            connection.execute(
                """
                INSERT INTO assessment_metrics (
                    assessment_id, metric_code, metric_label, metric_value, unit, calculated_at
                ) VALUES
                    ('synthetic-dashboard-a', 'accuracy', 'Precisao', 75.0, 'percent', 'synthetic'),
                    ('synthetic-dashboard-a', 'response_time', 'RT', 0.5, 'seconds', 'synthetic')
                """
            )
            connection.execute(
                """
                INSERT INTO trial_results (
                    assessment_id, block, trial_number, word, ink_color, condition,
                    correct_response, key_pressed, reaction_time, correct, error_type
                ) VALUES (
                    'synthetic-dashboard-a', 'main', 1, 'VERDE', 'green', 'congruent',
                    'space', 'space', 0.5, 1, 'hit'
                )
                """
            )

    def test_leitura_paginada_preserva_formato_do_dashboard(self) -> None:
        data = load_postgres_data(URL, page_size=1)
        self.assertEqual(len(data["assessments"]), 1)
        self.assertEqual(len(data["assessment_metrics"]), 2)
        self.assertEqual(len(data["trial_results"]), 1)
        self.assertEqual(data["assessments"][0]["assessment_id"], "synthetic-dashboard-a")
        self.assertEqual(data["assessment_metrics"][0]["metric_value"], 75.0)

    def test_url_configurada_e_preferida_sem_sqlite(self) -> None:
        data = load_dashboard_data(database_url=URL, page_size=1)
        self.assertEqual(data["assessments"][0]["project"], "SYNTHETIC_PROJECT")

    def test_conexao_forca_somente_leitura(self) -> None:
        with connect_postgres_readonly(URL) as connection:
            self.assertEqual(
                connection.execute("SHOW transaction_read_only").fetchone()[0], "on"
            )
            with self.assertRaises(psycopg.errors.ReadOnlySqlTransaction):
                connection.execute("CREATE TABLE blocked_dashboard_write (id integer)")

    def test_banco_postgres_vazio_tem_erro_claro(self) -> None:
        with psycopg.connect(URL, autocommit=True) as connection:
            connection.execute("TRUNCATE assessments CASCADE")
        with self.assertRaisesRegex(DashboardDataError, "Banco PostgreSQL vazio"):
            load_postgres_data(URL)

    def test_schema_postgres_invalido_tem_erro_claro(self) -> None:
        with psycopg.connect(URL, autocommit=True) as connection:
            connection.execute("DROP TABLE trial_results")
        with self.assertRaisesRegex(DashboardDataError, "Schema PostgreSQL invalido"):
            load_postgres_data(URL)


if __name__ == "__main__":
    unittest.main()
