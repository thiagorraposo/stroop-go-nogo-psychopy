"""Contrato de transporte HTTP com entradas e bancos exclusivamente sinteticos."""

import asyncio
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi import HTTPException
from fastapi.testclient import TestClient
import psycopg

from api.config import APIConfig, ConfigurationError
from api.main import create_app
from api.models import RequestModel


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://synthetic.example.test"
DATABASE = "postgresql://synthetic:SYNTHETIC_SECRET@127.0.0.1:1/stroop_etapa4_test_api"
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")


class SyntheticRequest(RequestModel):
    count: int
    text: str


def synthetic_config(**changes):
    return APIConfig(**{
        "database_url": DATABASE, "public_origin": ORIGIN, "app_env": "test",
        "oidc_client_id": "synthetic-client-id",
        "oidc_client_secret": "synthetic-client-secret-never-use",
        "session_secret": "synthetic-session-secret-never-use-0000000000",
        **changes,
    })


class APIConfigurationTests(unittest.TestCase):
    def test_factory_sem_configuracao_recusa_inicializacao_sem_reflexao(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ConfigurationError) as caught:
            create_app()
        self.assertEqual(str(caught.exception), "Configuracao da API ausente ou invalida.")

    def test_ambiente_obrigatorio_e_invalido_nao_reflete_valores(self):
        valid = {
            "API_DATABASE_URL": DATABASE, "API_PUBLIC_ORIGIN": ORIGIN, "APP_ENV": "test",
            "OIDC_CLIENT_ID": "synthetic-client-id",
            "OIDC_CLIENT_SECRET": "synthetic-client-secret-never-use",
            "API_SESSION_SECRET": "synthetic-session-secret-never-use-0000000000",
        }
        for missing in valid:
            environment = {key: value for key, value in valid.items() if key != missing}
            with self.subTest(missing=missing), self.assertRaises(ConfigurationError):
                APIConfig.from_env(environment)
        for field, values in {
            "API_DATABASE_URL": ["SYNTHETIC_SECRET", "sqlite:///SYNTHETIC_SECRET", "postgresql://", "postgresql://localhost/"],
            "API_PUBLIC_ORIGIN": ["http://SYNTHETIC_SECRET", "https://user:SYNTHETIC_SECRET@host", "https://host/SYNTHETIC_SECRET", "https://host?secret=SYNTHETIC_SECRET", "https://host:bad", "https://bad host"],
            "APP_ENV": ["SYNTHETIC_SECRET", ""],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value), self.assertRaises(ConfigurationError) as caught:
                    APIConfig.from_env({**valid, field: value})
                self.assertNotIn("SYNTHETIC_SECRET", str(caught.exception))
                self.assertTrue(caught.exception.__suppress_context__)

    def test_configuracao_valida_normaliza_origem_sem_expor_dsn_no_repr(self):
        config = synthetic_config(public_origin="https://SYNTHETIC.example.test:443/")
        self.assertEqual(config.public_origin, ORIGIN)
        self.assertNotIn("SYNTHETIC_SECRET", repr(config))
        with patch.dict(os.environ, {
            "API_DATABASE_URL": DATABASE, "API_PUBLIC_ORIGIN": ORIGIN, "APP_ENV": "test",
            "OIDC_CLIENT_ID": "synthetic-client-id",
            "OIDC_CLIENT_SECRET": "synthetic-client-secret-never-use",
            "API_SESSION_SECRET": "synthetic-session-secret-never-use-0000000000",
        }, clear=True):
            self.assertEqual(create_app().state.config.public_origin, ORIGIN)

    def test_rate_limit_login_tem_defaults_e_limites_configuraveis_validos(self):
        environment = {
            "API_DATABASE_URL": DATABASE,
            "API_PUBLIC_ORIGIN": ORIGIN,
            "APP_ENV": "test",
            "OIDC_CLIENT_ID": "synthetic-client-id",
            "OIDC_CLIENT_SECRET": "synthetic-client-secret-never-use",
            "API_SESSION_SECRET": "synthetic-session-secret-never-use-0000000000",
        }
        default = APIConfig.from_env(environment)
        self.assertEqual((default.login_rate_limit, default.login_rate_window_seconds), (20, 60))
        configured = APIConfig.from_env({
            **environment,
            "API_LOGIN_RATE_LIMIT": "7",
            "API_LOGIN_RATE_WINDOW_SECONDS": "120",
        })
        self.assertEqual((configured.login_rate_limit, configured.login_rate_window_seconds), (7, 120))
        for key, value in (
            ("API_LOGIN_RATE_LIMIT", "0"),
            ("API_LOGIN_RATE_LIMIT", "1001"),
            ("API_LOGIN_RATE_LIMIT", "invalid"),
            ("API_LOGIN_RATE_WINDOW_SECONDS", "0"),
            ("API_LOGIN_RATE_WINDOW_SECONDS", "86401"),
            ("API_LOGIN_RATE_WINDOW_SECONDS", "invalid"),
        ):
            with self.subTest(key=key, value=value), self.assertRaises(ConfigurationError):
                APIConfig.from_env({**environment, key: value})

    def test_importar_factory_nao_carrega_streamlit_dashboard_ou_clis(self):
        code = """
import sys
from api.main import create_app
assert callable(create_app)
assert not {'streamlit', 'dashboard', 'scripts'}.intersection(name.split('.')[0] for name in sys.modules)
"""
        result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class APIBaseTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(synthetic_config())

        @self.app.post("/api/v1/synthetic")
        def synthetic(body: SyntheticRequest):
            return {"accepted": True}

        @self.app.get("/api/v1/synthetic-http-error")
        def http_error():
            raise HTTPException(403, "SYNTHETIC_SECRET", headers={"X-Secret": "SYNTHETIC_SECRET"})

        @self.app.get("/api/v1/synthetic-unexpected-error")
        def unexpected_error():
            raise RuntimeError("SYNTHETIC_SECRET " + DATABASE)

        self.client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(self.client.close)

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status)
        body = response.json()
        self.assertEqual(set(body), {"error", "request_id"})
        self.assertEqual(set(body["error"]), {"code", "message"})
        self.assertEqual(body["error"]["code"], code)
        self.assertEqual(str(UUID(body["request_id"])), response.headers["X-Request-ID"])
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertNotIn("SYNTHETIC_SECRET", response.text)
        self.assertNotIn(DATABASE, response.text)

    def test_liveness_independe_do_banco_e_gera_request_id_novo(self):
        with patch("api.health.psycopg.connect") as connect:
            responses = [self.client.get("/health/live", headers={"X-Request-ID": "SYNTHETIC_SECRET"}) for _ in range(2)]
        connect.assert_not_called()
        for response in responses:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})
            self.assertEqual(UUID(response.headers["X-Request-ID"]).version, 4)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertNotEqual(responses[0].headers["X-Request-ID"], responses[1].headers["X-Request-ID"])

    def test_readiness_exige_banco_e_todas_as_migrations_sem_escrever(self):
        required = sorted(path.name for path in (ROOT / "scripts" / "migrations").glob("*.sql"))
        for applied, status in ((required, 200), (required[:-1], 503), (required + ["9999_unknown.sql"], 503)):
            connection = MagicMock()
            connection.execute.return_value.fetchall.return_value = [(name,) for name in applied]
            with self.subTest(applied=applied), patch("api.health.psycopg.connect") as connect:
                connect.return_value.__enter__.return_value = connection
                response = self.client.get("/health/ready")
            if status == 200:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"status": "ready"})
            else:
                self.assert_error(response, 503, "service_unavailable")
            self.assertEqual(connection.execute.call_count, 1)
            self.assertTrue(connection.execute.call_args.args[0].startswith("SELECT "))
            self.assertIn("default_transaction_read_only=on", connect.call_args.kwargs["options"])

    def test_readiness_indisponivel_ou_schema_ausente_e_erro_seguro(self):
        for error in (psycopg.OperationalError(DATABASE), psycopg.errors.UndefinedTable("SYNTHETIC_SECRET")):
            with self.subTest(error=type(error)), patch("api.health.psycopg.connect", side_effect=error):
                response = self.client.get("/health/ready")
            self.assert_error(response, 503, "service_unavailable")
        with tempfile.TemporaryDirectory() as directory, patch("api.health.MIGRATIONS_DIR", Path(directory)), patch("api.health.psycopg.connect") as connect:
            self.assert_error(self.client.get("/health/ready"), 503, "service_unavailable")
        connect.assert_not_called()

    def test_host_query_rota_metodo_e_detalhe_http_nao_refletem_entrada(self):
        cases = (
            (self.client.get("/health/live", headers={"Host": "SYNTHETIC_SECRET.example.test"}), 422, "invalid_request"),
            (self.client.get("/health/live", headers={"Host": "synthetic.example.test:0"}), 422, "invalid_request"),
            (self.client.get("/health/live?SYNTHETIC_SECRET=value"), 422, "invalid_request"),
            (self.client.get("/SYNTHETIC_SECRET"), 404, "not_found"),
            (self.client.post("/health/live", json={}), 405, "method_not_allowed"),
            (self.client.get("/api/v1/synthetic-http-error"), 403, "permission_denied"),
        )
        for response, status, code in cases:
            with self.subTest(status=status, code=code):
                self.assert_error(response, status, code)
                self.assertNotIn("x-secret", response.headers)

    def test_falha_inesperada_nao_propaga_excecao_ou_log_sensivel(self):
        with self.assertLogs("stroop.api", logging.WARNING) as logs:
            response = self.client.get("/api/v1/synthetic-unexpected-error")
        self.assert_error(response, 500, "internal_error")
        self.assertNotIn("SYNTHETIC_SECRET", " ".join(logs.output))
        self.assertIn(response.headers["X-Request-ID"], " ".join(logs.output))
        self.assertTrue(all(record.exc_info is None for record in logs.records))

    def test_schema_estrito_rejeita_coercao_booleano_extras_ausencias_e_null(self):
        cases = (
            {"count": "1", "text": "SYNTHETIC_SECRET"}, {"count": True, "text": "SYNTHETIC_SECRET"},
            {"count": 1.0, "text": "SYNTHETIC_SECRET"}, {"count": 1, "text": None},
            {"count": 1, "text": "ok", "SYNTHETIC_SECRET": 1}, {"text": "SYNTHETIC_SECRET"},
        )
        for body in cases:
            with self.subTest(body=body):
                self.assert_error(self.client.post("/api/v1/synthetic", json=body), 422, "invalid_request")
        self.assertEqual(self.client.post("/api/v1/synthetic", json={"count": 1, "text": "ok"}).json(), {"accepted": True})

    def test_json_malformado_chave_duplicada_nan_infinito_e_utf8_invalidos(self):
        bodies = (
            b'{"SYNTHETIC_SECRET":', b'{"count":1,"count":2,"text":"ok"}',
            b'{"count":NaN,"text":"ok"}', b'{"count":Infinity,"text":"ok"}',
            b'{"count":-Infinity,"text":"ok"}', b'{"count":1e999,"text":"ok"}',
            b'{"nested":{"x":1,"x":2}}', b'{"count":1,"text":"\xff"}', b'',
        )
        for body in bodies:
            with self.subTest(body=body):
                self.assert_error(self.client.post("/api/v1/synthetic", content=body, headers={"Content-Type": "application/json"}), 400, "invalid_json")

    def test_media_type_e_encoding_rejeitados_antes_do_schema(self):
        for headers in (
            {}, {"Content-Type": "text/plain"}, {"Content-Type": "application/json; charset=latin-1"},
            {"Content-Type": "application/json", "Content-Encoding": "gzip"},
        ):
            with self.subTest(headers=headers):
                self.assert_error(self.client.post("/api/v1/synthetic", content=b'{}', headers=headers), 415, "unsupported_media_type")

    def test_limite_conta_bytes_utf8_e_aceita_exatamente_64kib(self):
        prefix = b'{"count":1,"text":"'
        suffix = b'"}'
        body = prefix + b'x' * (65536 - len(prefix) - len(suffix)) + suffix
        self.assertEqual(len(body), 65536)
        headers = {"Content-Type": "application/json"}
        self.assertEqual(self.client.post("/api/v1/synthetic", content=body, headers=headers).status_code, 200)
        self.assert_error(self.client.post("/api/v1/synthetic", content=body + b' ', headers=headers), 413, "body_too_large")
        unicode_body = json.dumps({"count": 1, "text": "é" * 32768}, ensure_ascii=False).encode()
        self.assertGreater(len(unicode_body), 65536)
        self.assert_error(self.client.post("/api/v1/synthetic", content=unicode_body, headers=headers), 413, "body_too_large")

    def test_content_length_adulterado_nao_causa_erro_interno(self):
        for value, status, code in (("-1", 400, "invalid_json"), ("SYNTHETIC_SECRET", 400, "invalid_json"), ("9" * 5000, 413, "body_too_large")):
            with self.subTest(status=status, value=value[:16]):
                response = self.client.post("/api/v1/synthetic", content=b'{}', headers={"Content-Type": "application/json", "Content-Length": value})
                self.assert_error(response, status, code)

    def test_limite_real_sem_content_length_e_com_length_falso_em_chunks_asgi(self):
        async def send_request(declared_length):
            chunks = iter([b'{' + b' ' * 32767, b' ' * 32768, b'}'])
            reads = 0
            messages = []

            async def receive():
                nonlocal reads
                reads += 1
                chunk = next(chunks)
                return {"type": "http.request", "body": chunk, "more_body": reads < 3}

            async def send(message):
                messages.append(message)

            headers = [(b"host", b"synthetic.example.test"), (b"content-type", b"application/json")]
            if declared_length is not None:
                headers.append((b"content-length", declared_length))
            await self.app({
                "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                "method": "POST", "scheme": "https", "path": "/api/v1/synthetic",
                "raw_path": b"/api/v1/synthetic", "query_string": b"", "root_path": "",
                "headers": headers, "client": ("127.0.0.1", 1234), "server": ("synthetic.example.test", 443),
            }, receive, send)
            return messages, reads

        for length in (None, b"2"):
            with self.subTest(length=length):
                messages, reads = asyncio.run(send_request(length))
                start = next(message for message in messages if message["type"] == "http.response.start")
                body = b''.join(message.get("body", b'') for message in messages if message["type"] == "http.response.body")
                self.assertEqual(start["status"], 413)
                self.assertEqual(json.loads(body)["error"]["code"], "body_too_large")
                self.assertEqual(reads, 3)


@unittest.skipUnless(TEST_DATABASE_URL, "TEST_DATABASE_URL nao configurada")
class APIReadinessIntegrationTests(unittest.TestCase):
    def test_readiness_postgres_real_preserva_migrations_e_dados(self):
        if not psycopg.conninfo.conninfo_to_dict(TEST_DATABASE_URL).get("dbname", "").startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco descartavel de testes obrigatorio")
        # Preparacao explicita da fixture, fora do endpoint sob teste.
        from scripts.migrations import apply_migrations
        apply_migrations(TEST_DATABASE_URL)
        query = "SELECT version FROM schema_migrations ORDER BY version"
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            before = connection.execute(query).fetchall()
            counts = [connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone() for table in ("assessments", "trial_results", "assessment_metrics")]
        with TestClient(create_app(synthetic_config(database_url=TEST_DATABASE_URL)), base_url=ORIGIN) as client:
            response = client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready"})
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            self.assertEqual(connection.execute(query).fetchall(), before)
            self.assertEqual([connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone() for table in ("assessments", "trial_results", "assessment_metrics")], counts)


if __name__ == "__main__":
    unittest.main()
