"""Hardening de producao com artefatos e dados exclusivamente sinteticos."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import io
import os
from pathlib import Path
import tempfile
import unittest

import psycopg

from dashboard.auth import AuthDatabaseError, record_import_result
from scripts.aplicar_retencao import RetentionError, apply_retention
from scripts.backup_postgres import (
    BackupError,
    decrypt_stream,
    encrypt_stream,
    ensure_separate,
    generate_key,
    load_key,
    rotate_backups,
)
from scripts.migrations import apply_migrations


ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get("TEST_DATABASE_URL", "")


class ProductionConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compose = (ROOT / "compose.production.yaml").read_text(encoding="utf-8")
        cls.restore = (ROOT / "compose.restore-test.yaml").read_text(encoding="utf-8")
        cls.nginx = (ROOT / "nginx/nginx.conf").read_text(encoding="utf-8")
        cls.dockerfile = (ROOT / "Dockerfile.dashboard").read_text(encoding="utf-8")
        cls.proxy_dockerfile = (ROOT / "Dockerfile.proxy").read_text(encoding="utf-8")
        cls.proxy_entrypoint = (ROOT / "nginx/proxy-entrypoint.sh").read_text(encoding="utf-8")
        cls.streamlit = (ROOT / ".streamlit/config.toml").read_text(encoding="utf-8")

    def test_somente_proxy_publica_http_e_https(self) -> None:
        self.assertEqual(self.compose.count("    ports:\n"), 1)
        self.assertIn('      - "80:8080"', self.compose)
        self.assertIn('      - "443:8443"', self.compose)
        self.assertIn("backend:\n    internal: true", self.compose)

    def test_tls_externo_e_obrigatorio_sem_certificado_versionado(self) -> None:
        self.assertIn("TLS_CERTIFICATE_FILE:?", self.compose)
        self.assertIn("TLS_PRIVATE_KEY_FILE:?", self.compose)
        self.assertIn("ssl_certificate /run/secrets/tls_certificate", self.nginx)
        certificate_sources = [
            path
            for directory in (ROOT / "nginx", ROOT / "dashboard", ROOT / "scripts")
            for pattern in ("*.crt", "*.pem", "*.key")
            for path in directory.rglob(pattern)
        ]
        self.assertEqual(certificate_sources, [])

    def test_dashboard_usa_url_de_leitura_separada(self) -> None:
        self.assertIn(
            "DASHBOARD_DATABASE_URL: ${DASHBOARD_DATABASE_URL:?",
            self.compose,
        )
        example = (ROOT / ".env.production.example").read_text(encoding="utf-8")
        self.assertIn("DASHBOARD_DATABASE_URL=postgresql://stroop_dashboard_ro:", example)
        dashboard_docs = (ROOT / "docs" / "DASHBOARD_POSTGRESQL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("GRANT SELECT ON TABLE", dashboard_docs)

    def test_imagens_fixadas_e_manifestos_arm64_documentados(self) -> None:
        self.assertIn("nginx:1.28.0-alpine3.21@sha256:30f1c0d", self.proxy_dockerfile)
        self.assertIn("postgres:17.6-bookworm@sha256:f3bd19c", self.compose)
        self.assertIn("python:3.12.11-slim-bookworm@sha256:519591d", self.dockerfile)

    def test_conteineres_com_privilegios_reduzidos(self) -> None:
        self.assertGreaterEqual(self.compose.count("cap_drop:"), 3)
        self.assertGreaterEqual(self.compose.count("no-new-privileges:true"), 3)
        self.assertGreaterEqual(self.compose.count("read_only: true"), 3)
        self.assertIn("USER 10001:10001", self.dockerfile)

    def test_certificado_sintetico_e_recusado_em_producao(self) -> None:
        self.assertIn('APP_ENV: production', self.compose)
        self.assertIn('synthetic[.]invalid', self.proxy_entrypoint)
        self.assertIn('APP_ENV:-', self.proxy_entrypoint)
        self.assertIn('ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS:-', self.proxy_entrypoint)

    def test_perfil_ampere_preserva_cpu_para_o_host(self) -> None:
        self.assertIn("${POSTGRES_CPUS:-0.75}", self.compose)
        self.assertIn("${DASHBOARD_CPUS:-0.65}", self.compose)
        self.assertIn("${PROXY_CPUS:-0.15}", self.compose)
        self.assertLess(0.75 + 0.65 + 0.15, 2.0)

    def test_headers_limites_e_log_sem_uri_ou_conteudo(self) -> None:
        for header in (
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Content-Security-Policy",
        ):
            self.assertIn(header, self.nginx)
        self.assertIn("limit_req_zone", self.nginx)
        self.assertIn("limit_conn", self.nginx)
        log_definition = self.nginx.split("log_format operational", 1)[1].split(";", 1)[0]
        for forbidden in ("$request_uri", "$uri", "$args", "$http_cookie", "$request_body"):
            self.assertNotIn(forbidden, log_definition)

    def test_upload_limitado_em_duas_camadas(self) -> None:
        self.assertIn("client_max_body_size 6m", self.nginx)
        self.assertIn("maxUploadSize = 5", self.streamlit)
        self.assertIn("maxMessageSize = 6", self.streamlit)

    def test_erros_e_telemetria_reduzidos(self) -> None:
        self.assertIn('showErrorDetails = "none"', self.streamlit)
        self.assertIn('level = "warning"', self.streamlit)
        self.assertIn("gatherUsageStats = false", self.streamlit)

    def test_restauracao_e_isolada_sem_portas_ou_volume_persistente(self) -> None:
        self.assertIn("restore_isolated:\n    internal: true", self.restore)
        self.assertNotIn("ports:", self.restore)
        self.assertNotIn("volumes:", self.restore)
        self.assertIn("/var/lib/postgresql/data:rw", self.restore)

    def test_dependencias_diretas_tem_versao_exata(self) -> None:
        requirements = (ROOT / "dashboard/requirements.txt").read_text(encoding="utf-8")
        for line in requirements.splitlines():
            self.assertIn("==", line)
            self.assertNotIn(">=", line)
        lock = (ROOT / "dashboard/requirements.lock").read_text(encoding="utf-8")
        for line in lock.splitlines():
            if line and not line.startswith("#"):
                self.assertIn("==", line)
        self.assertIn("requirements.lock", self.dockerfile)


class BackupEncryptionTests(unittest.TestCase):
    def test_criptografia_autenticada_round_trip(self) -> None:
        key = os.urandom(32)
        source = b"SYNTHETIC pg_dump bytes" * 10_000
        encrypted = io.BytesIO()
        encrypt_stream(io.BytesIO(source), encrypted, key)
        self.assertNotIn(source[:64], encrypted.getvalue())
        restored = io.BytesIO()
        decrypt_stream(encrypted, restored, key)
        self.assertEqual(restored.getvalue(), source)

    def test_chave_incorreta_ou_backup_adulterado_sao_recusados(self) -> None:
        encrypted = io.BytesIO()
        encrypt_stream(io.BytesIO(b"SYNTHETIC"), encrypted, os.urandom(32))
        with self.assertRaises(BackupError):
            decrypt_stream(encrypted, io.BytesIO(), os.urandom(32))

    def test_chave_tem_256_bits_e_permissao_restrita(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            key_file = Path(directory) / "backup.key"
            generate_key(key_file)
            self.assertEqual(len(load_key(key_file)), 32)
            self.assertEqual(key_file.stat().st_mode & 0o777, 0o600)

    def test_chave_nao_pode_ficar_no_diretorio_de_backups(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(BackupError):
                ensure_separate(root / "backups/key", root / "backups")

    def test_rotacao_mantem_trinta_geracoes_e_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(32):
                backup = root / f"stroop-202601{index:02d}T000000Z.dump.enc"
                backup.write_bytes(base64.b64encode(str(index).encode()))
                backup.with_suffix(backup.suffix + ".sha256").write_text("synthetic")
            rotate_backups(root, 30)
            self.assertEqual(len(list(root.glob("*.dump.enc"))), 30)
            self.assertEqual(len(list(root.glob("*.sha256"))), 30)


@unittest.skipUnless(URL, "TEST_DATABASE_URL nao configurada")
class HardeningDatabaseIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        database = psycopg.conninfo.conninfo_to_dict(URL).get("dbname", "")
        if not database.startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco descartavel obrigatorio")

    def setUp(self) -> None:
        with psycopg.connect(URL, autocommit=True) as connection:
            connection.execute("DROP SCHEMA public CASCADE")
            connection.execute("CREATE SCHEMA public")
        apply_migrations(URL)

    def test_auditoria_de_rejeicao_guarda_somente_campos_minimos(self) -> None:
        record_import_result(
            URL,
            "00000000000000000000000000000001",
            "a" * 64,
            "rejeitado",
            "invalid_envelope",
        )
        with psycopg.connect(URL) as connection:
            columns = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'import_audit_events'
                    """
                )
            }
            row = connection.execute(
                "SELECT content_sha256, status, error_code FROM import_audit_events"
            ).fetchone()
        self.assertEqual(
            columns,
            {"event_id", "occurred_at", "request_id", "content_sha256", "status", "error_code"},
        )
        self.assertEqual(row, ("a" * 64, "rejeitado", "invalid_envelope"))

    def test_vocabulario_livre_de_erro_e_recusado(self) -> None:
        with self.assertRaises(AuthDatabaseError):
            record_import_result(
                URL,
                "00000000000000000000000000000002",
                "b" * 64,
                "rejeitado",
                "SYNTHETIC_PRIVATE_CONTENT",
            )

    def test_retencao_remove_apenas_auditorias_vencidas(self) -> None:
        with psycopg.connect(URL) as connection:
            connection.execute(
                """
                INSERT INTO import_audit_events
                    (occurred_at, request_id, content_sha256, status, error_code)
                VALUES (%s, %s, %s, 'rejeitado', 'invalid_envelope')
                """,
                (
                    datetime.now(timezone.utc) - timedelta(days=31),
                    "00000000-0000-0000-0000-000000000003",
                    "c" * 64,
                ),
            )
            connection.execute(
                """
                INSERT INTO assessments
                    (assessment_id, test_code, test_version, project, participant_id,
                     participant_name, visit, evaluator, assessment_date, started_at,
                     source_file, imported_at, import_status)
                VALUES ('synthetic-retention', 'stroop_go_nogo_ptbr', '0.2.2',
                        'SYNTHETIC', 'synthetic-id', 'SYNTHETIC', 'V1', 'EV1',
                        '2026-01-01', 'synthetic', 'synthetic', 'synthetic', 'valid')
                """
            )
        self.assertEqual(
            apply_retention(URL, operational_days=30, auth_days=180, apply=False)["operational"],
            1,
        )
        result = apply_retention(URL, operational_days=30, auth_days=180, apply=True)
        self.assertEqual(result["operational"], 1)
        with psycopg.connect(URL) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 1)

    def test_retencao_invalida_e_recusada(self) -> None:
        with self.assertRaises(RetentionError):
            apply_retention(URL, operational_days=0)


if __name__ == "__main__":
    unittest.main()
