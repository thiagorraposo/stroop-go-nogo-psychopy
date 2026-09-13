"""Contrato e integracao do importador com fontes exclusivamente sinteticas."""
from contextlib import redirect_stdout, redirect_stderr
from concurrent.futures import ThreadPoolExecutor
import io
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import psycopg
from scripts import importar_csv_postgres as pg
from scripts import importar_csv_sqlite as legacy
from scripts.migrations import apply_migrations

FIXTURES = Path(__file__).parent / "fixtures" / "csv"
URL = os.environ.get("TEST_DATABASE_URL", "")


class PostgresCsvValidationTests(unittest.TestCase):
    def test_validate_only_nao_conecta(self):
        with patch.object(pg.psycopg, "connect") as connect:
            result = pg.import_csv(FIXTURES / "valido_minimo.csv", validate_only=True)
        connect.assert_not_called()
        self.assertEqual(result, {"status": "validated", "trials": 4, "metrics": 12})

    def test_fixtures_invalidas_nao_conectam(self):
        with patch.object(pg.psycopg, "connect") as connect:
            for name in ("invalido_coluna_ausente.csv", "invalido_tipo.csv", "invalido_dominio.csv"):
                with self.subTest(name=name), self.assertRaises(pg.PostgresImportError):
                    pg.import_csv(FIXTURES / name, "synthetic")
        connect.assert_not_called()

    def test_url_ausente(self):
        with self.assertRaisesRegex(pg.PostgresImportError, "DATABASE_URL nao configurada"):
            pg.import_csv(FIXTURES / "valido_minimo.csv")

    def test_erros_nao_expoem_conteudo_caminho_ou_credenciais(self):
        marker = "SYNTHETIC_SECRET_SENTINEL"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / (marker + ".csv")
            path.write_text((FIXTURES / "valido_minimo.csv").read_text().replace("congruent", marker))
            for source in (path, Path(directory) / "missing.csv"):
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(output):
                    self.assertEqual(pg.main([str(source)]), 1)
                self.assertNotIn(marker, output.getvalue())
                self.assertNotIn(directory, output.getvalue())
        with patch.object(pg.psycopg, "connect", side_effect=psycopg.OperationalError(marker)):
            with self.assertRaises(pg.PostgresImportError) as caught:
                pg.import_csv(FIXTURES / "valido_minimo.csv", marker)
        self.assertNotIn(marker, str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)

    def test_cli_argumento_invalido_sanitizado(self):
        output = io.StringIO()
        with redirect_stderr(output), self.assertRaises(SystemExit) as caught:
            pg.main(["--SYNTHETIC_SECRET"])
        self.assertEqual(caught.exception.code, 2)
        self.assertNotIn("SYNTHETIC_SECRET", output.getvalue())


@unittest.skipUnless(URL, "TEST_DATABASE_URL nao configurada")
class PostgresCsvIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not psycopg.conninfo.conninfo_to_dict(URL).get("dbname", "").startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco de teste descartavel obrigatorio")

    def setUp(self):
        with psycopg.connect(URL, autocommit=True) as c:
            c.execute("DROP SCHEMA public CASCADE")
            c.execute("CREATE SCHEMA public")
        apply_migrations(URL)
        self.source = FIXTURES / "valido_minimo.csv"

    def counts(self):
        with psycopg.connect(URL) as c:
            return tuple(c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                         for t in ("assessments", "trial_results", "assessment_metrics"))

    def test_paridade_integral_sqlite_e_csv_imutavel(self):
        original = self.source.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "synthetic.sqlite3"
            with patch.object(legacy, "utc_now_iso", return_value="2026-09-13T00:00:00+00:00"):
                legacy.import_csv(self.source, target)
                result = pg.import_csv(self.source, URL)
            self.assertEqual(result["status"], "imported")
            with sqlite3.connect(target) as sqlite, psycopg.connect(URL) as postgres:
                for table in ("assessments", "trial_results", "assessment_metrics"):
                    query = f"SELECT * FROM {table} ORDER BY 1"
                    self.assertEqual(sqlite.execute(query).fetchall(), postgres.execute(query).fetchall())
        self.assertEqual(original, self.source.read_bytes())
        self.assertEqual(self.counts(), (1, 4, 12))

    def test_repeticao_recusada_e_force_sem_duplicar(self):
        pg.import_csv(self.source, URL)
        with self.assertRaises(pg.DuplicateAssessmentError):
            pg.import_csv(self.source, URL)
        self.assertEqual(self.counts(), (1, 4, 12))
        self.assertEqual(pg.import_csv(self.source, URL, force=True)["status"], "reimported")
        self.assertEqual(self.counts(), (1, 4, 12))

    def test_importacoes_simultaneas_nao_duplicam(self):
        def run():
            try:
                return pg.import_csv(self.source, URL)["status"]
            except pg.DuplicateAssessmentError:
                return "duplicate"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: run(), range(2)))
        self.assertCountEqual(results, ["imported", "duplicate"])
        self.assertEqual(self.counts(), (1, 4, 12))

    def test_rollback_apos_tentativas_e_preserva_reimportacao(self):
        with psycopg.connect(URL) as c:
            c.execute("ALTER TABLE assessment_metrics ADD CONSTRAINT synthetic_failure CHECK (metric_value < 0)")
        with self.assertRaises(pg.PostgresImportError):
            pg.import_csv(self.source, URL)
        self.assertEqual(self.counts(), (0, 0, 0))
        with psycopg.connect(URL) as c:
            c.execute("ALTER TABLE assessment_metrics DROP CONSTRAINT synthetic_failure")
        pg.import_csv(self.source, URL)
        with psycopg.connect(URL) as c:
            c.execute("ALTER TABLE assessment_metrics ADD CONSTRAINT synthetic_failure CHECK (metric_value < 0) NOT VALID")
            before = c.execute("SELECT * FROM assessments").fetchall()
        with self.assertRaises(pg.PostgresImportError):
            pg.import_csv(self.source, URL, force=True)
        self.assertEqual(self.counts(), (1, 4, 12))
        with psycopg.connect(URL) as c:
            self.assertEqual(before, c.execute("SELECT * FROM assessments").fetchall())

    def test_invalido_preserva_destino(self):
        pg.import_csv(self.source, URL)
        for name in ("invalido_coluna_ausente.csv", "invalido_tipo.csv", "invalido_dominio.csv"):
            with self.subTest(name=name), self.assertRaises(pg.PostgresImportError):
                pg.import_csv(FIXTURES / name, URL, force=True)
        self.assertEqual(self.counts(), (1, 4, 12))

    def test_cli_codigos_e_saida_segura(self):
        with patch.dict(os.environ, {"DATABASE_URL": URL}):
            for options, expected in (([], 0), ([], 3), (["--force"], 0), (["--validate-only"], 0)):
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(output):
                    self.assertEqual(pg.main([str(self.source)] + options), expected)
                self.assertNotIn(str(self.source), output.getvalue())
                self.assertNotIn("assessment_id", output.getvalue())

    def test_postgresql_indisponivel(self):
        # Porta 1 local nao hospeda o banco descartavel; sem acesso remoto.
        with self.assertRaises(pg.PostgresImportError):
            pg.import_csv(self.source, "postgresql://synthetic:synthetic@127.0.0.1:1/stroop_etapa4_test")
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_instrumento_sintetico_coexiste_sem_tentativas_stroop(self):
        source = FIXTURES / "instrumento_sintetico_demo.csv"
        result = pg.import_csv(source, URL)
        self.assertEqual(result, {"status": "imported", "trials": 0, "metrics": 2})
        self.assertEqual(self.counts(), (1, 0, 2))
        with psycopg.connect(URL) as connection:
            self.assertEqual(
                connection.execute("SELECT test_code FROM assessments").fetchone()[0],
                "instrumento_sintetico_demo",
            )
