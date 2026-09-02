"""Integracao da Etapa 4 com PostgreSQL descartavel e dados sinteticos."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import psycopg

from scripts.migrations import MIGRATIONS_DIR, MigrationError, apply_migrations
from scripts.migrar_sqlite_postgres import (
    LegacyMigrationError,
    migrate_sqlite_to_postgres,
)


ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")


@unittest.skipUnless(TEST_DATABASE_URL, "TEST_DATABASE_URL nao configurada")
class PostgresMigrationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        database_name = psycopg.conninfo.conninfo_to_dict(TEST_DATABASE_URL).get("dbname", "")
        if not database_name.startswith("stroop_etapa4_test"):
            raise RuntimeError("TEST_DATABASE_URL deve apontar para banco descartavel da Etapa 4")

    def setUp(self) -> None:
        with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as connection:
            connection.execute("DROP SCHEMA public CASCADE")
            connection.execute("CREATE SCHEMA public")

    def create_sqlite_fixture(self, invalid_reaction_time: bool = False) -> Path:
        temporary = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        temporary.close()
        path = Path(temporary.name)
        connection = sqlite3.connect(path)
        connection.executescript((ROOT / "scripts" / "db_schema.sql").read_text(encoding="utf-8"))
        connection.execute(
            """
            INSERT INTO assessments VALUES
            ('synthetic-assessment', 'stroop_go_nogo_ptbr', '0.2.2', 'SYNTHETIC',
             'synthetic-id', 'SYNTHETIC', NULL, 'V1', 'EV1', '2026-01-01',
             '2026-01-01T10:00:00', 'synthetic.csv', '2026-01-01T11:00:00+00:00', 'valid')
            """
        )
        connection.executemany(
            """
            INSERT INTO assessment_metrics
            (metric_id, assessment_id, metric_code, metric_label, metric_value, unit, calculated_at)
            VALUES (?, 'synthetic-assessment', ?, ?, ?, ?, '2026-01-01T11:00:00+00:00')
            """,
            [
                (7, "accuracy", "Precisao total", 100.0, "percent"),
                (9, "total_trials", "Total de tentativas", 2.0, "count"),
            ],
        )
        reaction_time = -0.5 if invalid_reaction_time else 0.5
        connection.executemany(
            """
            INSERT INTO trial_results
            (trial_result_id, assessment_id, block, trial_number, word, ink_color,
             condition, correct_response, key_pressed, reaction_time, correct, error_type)
            VALUES (?, 'synthetic-assessment', 'main', ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            [
                (11, 1, "VERDE", "green", "congruent", "space", "space", reaction_time, "hit"),
                (15, 2, "AZUL", "red", "incongruent", None, None, None, "correct_rejection"),
            ],
        )
        connection.commit()
        connection.close()
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_migration_em_banco_vazio_cria_schema_indices_e_fks(self) -> None:
        self.assertEqual(apply_migrations(TEST_DATABASE_URL), ["0001_initial.sql"])
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            }
            self.assertTrue(
                {"schema_migrations", "assessments", "assessment_metrics", "trial_results"}
                .issubset(tables)
            )
            indices = {
                row[0]
                for row in connection.execute(
                    "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
                )
            }
            self.assertIn("idx_assessment_metrics_assessment_metric", indices)
            self.assertIn("idx_trial_results_assessment_block", indices)
            foreign_keys = connection.execute(
                """
                SELECT COUNT(*) FROM information_schema.table_constraints
                WHERE constraint_schema = 'public' AND constraint_type = 'FOREIGN KEY'
                """
            ).fetchone()[0]
            self.assertEqual(foreign_keys, 2)

    def test_migrations_sao_idempotentes(self) -> None:
        apply_migrations(TEST_DATABASE_URL)
        self.assertEqual(apply_migrations(TEST_DATABASE_URL), [])

    def test_falha_de_migration_reverte_lote_inteiro(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            migration_dir = Path(directory)
            (migration_dir / "0001_valid.sql").write_text(
                "CREATE TABLE should_rollback (id INTEGER PRIMARY KEY);", encoding="utf-8"
            )
            (migration_dir / "0002_invalid.sql").write_text(
                "CREATE TABLE broken (", encoding="utf-8"
            )
            with self.assertRaises(MigrationError):
                apply_migrations(TEST_DATABASE_URL, migration_dir)
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            exists = connection.execute("SELECT to_regclass('public.should_rollback')").fetchone()[0]
            self.assertIsNone(exists)

    def test_migracao_sqlite_preserva_dados_relacionamentos_e_sequences(self) -> None:
        apply_migrations(TEST_DATABASE_URL)
        counts = migrate_sqlite_to_postgres(self.create_sqlite_fixture(), TEST_DATABASE_URL)
        self.assertEqual(counts, {"assessments": 1, "assessment_metrics": 2, "trial_results": 2})
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM assessment_metrics WHERE assessment_id = %s",
                    ("synthetic-assessment",),
                ).fetchone()[0],
                2,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT metric_value FROM assessment_metrics WHERE metric_code = 'accuracy'"
                ).fetchone()[0],
                100.0,
            )
            next_metric_id = connection.execute(
                """
                INSERT INTO assessment_metrics
                (assessment_id, metric_code, metric_label, metric_value, unit, calculated_at)
                VALUES ('synthetic-assessment', 'sequence_check', 'Sequence', 1, 'count', 'synthetic')
                RETURNING metric_id
                """
            ).fetchone()[0]
            self.assertGreater(next_metric_id, 9)

    def test_erro_no_destino_reverte_toda_migracao(self) -> None:
        apply_migrations(TEST_DATABASE_URL)
        with self.assertRaises(LegacyMigrationError):
            migrate_sqlite_to_postgres(
                self.create_sqlite_fixture(invalid_reaction_time=True), TEST_DATABASE_URL
            )
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            for table in ("assessments", "assessment_metrics", "trial_results"):
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)

    def test_destino_preenchido_e_recusado_sem_alteracao(self) -> None:
        apply_migrations(TEST_DATABASE_URL)
        source = self.create_sqlite_fixture()
        migrate_sqlite_to_postgres(source, TEST_DATABASE_URL)
        with self.assertRaises(LegacyMigrationError):
            migrate_sqlite_to_postgres(source, TEST_DATABASE_URL)
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 1)

    def test_schema_sqlite_invalido_e_recusado(self) -> None:
        apply_migrations(TEST_DATABASE_URL)
        temporary = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        temporary.close()
        path = Path(temporary.name)
        self.addCleanup(path.unlink, missing_ok=True)
        sqlite3.connect(path).close()
        with self.assertRaises(LegacyMigrationError):
            migrate_sqlite_to_postgres(path, TEST_DATABASE_URL)


class PostgresMigrationStaticTests(unittest.TestCase):
    def test_migration_versionada_existe(self) -> None:
        self.assertEqual(
            [path.name for path in MIGRATIONS_DIR.glob("*.sql")],
            ["0001_initial.sql"],
        )

    def test_fluxo_publico_permanece_sqlite(self) -> None:
        launcher = (ROOT / "scripts" / "run_dashboard.py").read_text(encoding="utf-8")
        dashboard = (ROOT / "dashboard" / "data_access.py").read_text(encoding="utf-8")
        self.assertIn("importar_csv_sqlite.py", launcher)
        self.assertIn("load_sqlite_data", dashboard)
        self.assertNotIn("migrar_sqlite_postgres", launcher)


if __name__ == "__main__":
    unittest.main()
