"""Integracao da Etapa 4 com PostgreSQL descartavel e dados sinteticos."""

from __future__ import annotations

import os
import sqlite3
import shutil
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
        self.assertEqual(
            apply_migrations(TEST_DATABASE_URL),
            [
                "0001_initial.sql",
                "0002_authentication.sql",
                "0003_import_audit.sql",
                "0004_web_professional_auth.sql",
                "0005_web_participant_sessions.sql",
                "0006_web_completed_results.sql",
                "0007_web_legacy_project_links.sql",
                "0008_web_user_lock.sql",
                "0009_web_csv_imports.sql",
                "0010_web_user_management.sql",
                "0011_web_incremental_sessions.sql",
                "0012_local_authentication.sql",
                "0013_local_user_management.sql",
            ],
        )
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
            }
            self.assertTrue(
                {
                    "schema_migrations",
                    "assessments",
                    "assessment_metrics",
                    "trial_results",
                    "app_users",
                    "auth_audit_events",
                    "import_audit_events",
                    "web_oidc_transactions",
                    "web_professional_sessions",
                    "web_login_rate_limits",
                    "web_projects",
                    "web_project_members",
                    "web_invitations",
                    "web_participant_sessions",
                    "web_session_main_order",
                    "web_participant_redeem_limits",
                    "web_professional_request_limits",
                    "web_assessments",
                    "web_trial_observations",
                    "web_participant_request_limits",
                    "web_csv_imports",
                }
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
            self.assertIn("idx_web_csv_imports_project_updated", indices)
            foreign_keys = connection.execute(
                """
                SELECT COUNT(*) FROM information_schema.table_constraints
                WHERE constraint_schema = 'public' AND constraint_type = 'FOREIGN KEY'
                """
            ).fetchone()[0]
            self.assertEqual(foreign_keys, 30)
            self.assertIn("web_legacy_project_links", tables)
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM web_legacy_project_links").fetchone()[0], 0)

    def test_migrations_sao_idempotentes(self) -> None:
        apply_migrations(TEST_DATABASE_URL)
        self.assertEqual(apply_migrations(TEST_DATABASE_URL), [])

    def test_migration_web_e_aditiva_sobre_schema_legado_com_dados(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            older_migrations = Path(directory)
            for path in sorted(MIGRATIONS_DIR.glob("000[1-4]_*.sql")):
                shutil.copyfile(path, older_migrations / path.name)
            self.assertEqual(len(apply_migrations(TEST_DATABASE_URL, older_migrations)), 4)
        source = self.create_sqlite_fixture()
        self.assertEqual(
            migrate_sqlite_to_postgres(source, TEST_DATABASE_URL),
            {"assessments": 1, "assessment_metrics": 2, "trial_results": 2},
        )
        self.assertEqual(apply_migrations(TEST_DATABASE_URL), [
            "0005_web_participant_sessions.sql", "0006_web_completed_results.sql",
            "0007_web_legacy_project_links.sql",
            "0008_web_user_lock.sql",
            "0009_web_csv_imports.sql",
            "0010_web_user_management.sql",
                "0011_web_incremental_sessions.sql",
                "0012_local_authentication.sql",
                "0013_local_user_management.sql",
        ])
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessment_metrics").fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM trial_results").fetchone()[0], 2)

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

    def test_migration_resultados_preserva_sessao_web_em_execucao(self) -> None:
        from uuid import uuid4
        from stroop.application import web_sessions

        with tempfile.TemporaryDirectory() as directory:
            older = Path(directory)
            for path in sorted(MIGRATIONS_DIR.glob('000[1-5]_*.sql')):
                shutil.copyfile(path, older / path.name)
            self.assertEqual(len(apply_migrations(TEST_DATABASE_URL, older)), 5)
        # Fixture SQL do schema antigo: o adaptador atual exige a funcao 0008 e
        # nao deve ser executado antes de aplicar suas dependencias de schema.
        issuer, subject = 'https://accounts.google.com', 'synthetic-upgrade-user'
        project_id, invitation_id, session_id = uuid4(), uuid4(), uuid4()
        session_query = 'SELECT * FROM web_participant_sessions WHERE session_id=%s'
        order_query = 'SELECT trial_number,condition_id FROM web_session_main_order WHERE session_id=%s ORDER BY trial_number'
        invitation_query = '''SELECT invitation_id,session_id,project_id,code_sha256,participant_id,visit,
            evaluator_issuer,evaluator_subject,protocol_id,state,created_at,expires_at,redeemed_at,revoked_at
            FROM web_invitations WHERE session_id=%s'''
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            connection.execute("INSERT INTO app_users(issuer,subject,role) VALUES(%s,%s,'administracao')", (issuer, subject))
            connection.execute("""INSERT INTO web_projects(project_id,code,name,created_by_issuer,created_by_subject)
                VALUES(%s,'SYNTHETIC_UPGRADE','Projeto sintetico',%s,%s)""", (project_id, issuer, subject))
            connection.execute('INSERT INTO web_project_members(project_id,issuer,subject) VALUES(%s,%s,%s)', (project_id, issuer, subject))
            connection.execute("""INSERT INTO web_invitations(invitation_id,session_id,project_id,code_sha256,
                participant_id,visit,evaluator_issuer,evaluator_subject,state,expires_at,redeemed_at)
                VALUES(%s,%s,%s,%s,'P_SINTETICO','V1',%s,%s,'redeemed',
                CURRENT_TIMESTAMP+interval '24 hours',CURRENT_TIMESTAMP)""",
                (invitation_id, session_id, project_id, 'a' * 64, issuer, subject))
            connection.execute("""INSERT INTO web_participant_sessions(session_id,participant_token_sha256,state,
                activated_at,expires_at,started_at,app_version) VALUES(%s,%s,'running',CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP+interval '30 minutes',CURRENT_TIMESTAMP,'synthetic-web-0.1.0')""", (session_id, 'b' * 64))
            connection.cursor().executemany('INSERT INTO web_session_main_order(session_id,trial_number,condition_id) VALUES(%s,%s,%s)',
                [(session_id, index, index) for index in range(1, 17)])
            before = (connection.execute(session_query, (session_id,)).fetchall(),
                      connection.execute(order_query, (session_id,)).fetchall(),
                      connection.execute(invitation_query, (session_id,)).fetchall())
        self.assertEqual(apply_migrations(TEST_DATABASE_URL), [
            '0006_web_completed_results.sql', '0007_web_legacy_project_links.sql', '0008_web_user_lock.sql',
            '0009_web_csv_imports.sql', '0010_web_user_management.sql', '0011_web_incremental_sessions.sql', '0012_local_authentication.sql', '0013_local_user_management.sql'])
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            after = (connection.execute(session_query, (session_id,)).fetchall(),
                     connection.execute(order_query, (session_id,)).fetchall(),
                     connection.execute(invitation_query, (session_id,)).fetchall())
        self.assertEqual(after, before)
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            self.assertEqual(connection.execute("""SELECT p.pseudonym,v.label FROM web_invitations i
                JOIN web_project_participants p USING(participant_uuid)
                JOIN web_participant_visits v USING(visit_uuid)
                WHERE i.session_id=%s""",(session_id,)).fetchone(),('P_SINTETICO','V1'))
            self.assertEqual(connection.execute('SELECT count(*) FROM web_session_observations').fetchone()[0],0)
            self.assertEqual(connection.execute('SELECT count(*) FROM web_session_checkpoints').fetchone()[0],0)
        session = web_sessions.participant_session(TEST_DATABASE_URL, 'b' * 64)
        self.assertEqual(session.state, 'running')
        self.assertEqual(session.session_id, session_id)

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
            sorted(path.name for path in MIGRATIONS_DIR.glob("*.sql")),
            [
                "0001_initial.sql",
                "0002_authentication.sql",
                "0003_import_audit.sql",
                "0004_web_professional_auth.sql",
                "0005_web_participant_sessions.sql",
                "0006_web_completed_results.sql",
                "0007_web_legacy_project_links.sql",
                "0008_web_user_lock.sql",
                "0009_web_csv_imports.sql",
                "0010_web_user_management.sql",
                "0011_web_incremental_sessions.sql",
                "0012_local_authentication.sql",
                "0013_local_user_management.sql",
            ],
        )

    def test_dashboard_operacional_usa_postgres_com_fallback_sqlite(self) -> None:
        launcher = (ROOT / "scripts" / "run_dashboard.py").read_text(encoding="utf-8")
        dashboard = (ROOT / "dashboard" / "data_access.py").read_text(encoding="utf-8")
        self.assertIn("importar_csv_sqlite.py", launcher)
        self.assertIn("load_postgres_data", dashboard)
        self.assertIn("DASHBOARD_DATABASE_URL", dashboard)
        self.assertIn("load_sqlite_data", dashboard)
        self.assertNotIn("migrar_sqlite_postgres", launcher)


if __name__ == "__main__":
    unittest.main()
