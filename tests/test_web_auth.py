"""Fluxo HTTP OIDC e sessoes profissionais com dados de identidade sinteticos."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import psycopg
from fastapi import Request
from fastapi.testclient import TestClient

from api.config import APIConfig
from api.auth import opaque_user_id, require_professional
from api.main import create_app
from scripts.migrations import apply_migrations
from stroop.application import auth as auth_application
from stroop.persistence import web_auth


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://synthetic.example.test"
DATABASE = "postgresql://synthetic:SYNTHETIC_SECRET@127.0.0.1:1/stroop_etapa4_test_auth"
ISSUER = "https://accounts.google.com"
SUBJECT = "synthetic-professional-subject"


def config() -> APIConfig:
    return APIConfig(auth_mode="oidc",
        database_url=DATABASE,
        public_origin=ORIGIN,
        app_env="test",
        oidc_client_id="synthetic-client-id",
        oidc_client_secret="synthetic-client-secret-never-use",
        session_secret="synthetic-session-secret-never-use-0000000000",
    )


def verified_claims(subject: str = SUBJECT, *, expires_at: int | None = None):
    return {
        "iss": ISSUER,
        "sub": subject,
        "exp": expires_at or int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "nonce": "synthetic-nonce-from-transaction",
        "aud": "synthetic-client-id",
    }


class WebAuthContractTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config())
        self.client = TestClient(self.app, base_url=ORIGIN, follow_redirects=False)
        self.addCleanup(self.client.close)

    def test_rotas_rejeitam_query_inesperada_e_corpo_em_get(self):
        for response in (
            self.client.get("/api/v1/auth/login?return_to=https://attacker.invalid"),
            self.client.get("/api/v1/auth/me?extra=synthetic"),
        ):
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()["error"]["code"], "invalid_request")
        response = self.client.request(
            "GET", "/api/v1/auth/login", content=b"{}",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 422)

    def test_logout_exige_origem_e_csrf_ou_e_idempotente_sem_cookie(self):
        rejected = self.client.post("/api/v1/auth/logout", json={}, headers={"Origin": "https://attacker.invalid"})
        self.assertEqual((rejected.status_code, rejected.json()["error"]["code"]), (403, "csrf_failed"))
        accepted = self.client.post("/api/v1/auth/logout", json={}, headers={"Origin": ORIGIN})
        self.assertEqual(accepted.status_code, 204)

    def test_callback_malformado_nao_reflete_query_e_limpa_state(self):
        response = self.client.get(
            "/api/v1/auth/callback?state=synthetic-state&state=synthetic-duplicate&code=synthetic-code",
            headers={"Cookie": "__Host-stroop_oidc_state=synthetic-state"},
        )
        self.assertEqual((response.status_code, response.json()["error"]["code"]), (400, "invalid_oidc_state"))
        self.assertNotIn("synthetic-code", response.text)
        self.assertIn("__Host-stroop_oidc_state", response.headers["set-cookie"])


@unittest.skipUnless(os.environ.get("TEST_DATABASE_URL"), "TEST_DATABASE_URL nao configurada")
class WebAuthPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = os.environ["TEST_DATABASE_URL"]
        database = psycopg.conninfo.conninfo_to_dict(cls.database_url).get("dbname", "")
        if not database.startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco PostgreSQL descartavel obrigatorio")

    def setUp(self):
        with psycopg.connect(self.database_url, autocommit=True) as connection:
            connection.execute("DROP SCHEMA public CASCADE")
            connection.execute("CREATE SCHEMA public")
        apply_migrations(self.database_url)
        auth_application.bootstrap_admin(
            self.database_url, ISSUER, SUBJECT, "synthetic@example.invalid"
        )
        administrator = auth_application.authorize(
            self.database_url, verified_claims(), "manage_users"
        )
        auth_application.create_user(
            self.database_url,
            ISSUER,
            "synthetic-secondary-admin",
            "administracao",
            None,
            administrator,
        )
        self.app = create_app(configured_database(self.database_url))
        self.client = TestClient(self.app, base_url=ORIGIN, follow_redirects=False)
        self.addCleanup(self.client.close)

        @self.app.get("/api/v1/synthetic/admin-only")
        def admin_only(request: Request):
            user = require_professional(request, "manage_users")
            return {"role": user.role}

    def _start_login(self):
        with patch("api.auth.authorization_url", return_value="https://accounts.google.com/o/oauth2/v2/auth?synthetic=1") as build_url:
            response = self.client.get("/api/v1/auth/login")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "https://accounts.google.com/o/oauth2/v2/auth?synthetic=1")
        state_cookie = response.cookies.get("__Host-stroop_oidc_state")
        self.assertIsNotNone(state_cookie)
        self.assertIn("secure", response.headers["set-cookie"].lower())
        self.assertIn("httponly", response.headers["set-cookie"].lower())
        self.assertIn("samesite=lax", response.headers["set-cookie"].lower())
        self.assertIn("path=/", response.headers["set-cookie"].lower())
        return state_cookie, build_url.call_args.kwargs

    def _callback(self, state_cookie, *, subject=SUBJECT, force_state_cookie=False, extra=None):
        claims = verified_claims(subject)
        headers = {"Cookie": f"__Host-stroop_oidc_state={state_cookie}"} if force_state_cookie else None
        with patch("api.auth.exchange_code", return_value=claims) as exchange:
            response = self.client.get(
                "/api/v1/auth/callback",
                params={"state": state_cookie, "code": "synthetic-code", **(extra or {})},
                headers=headers,
            )
        return response, exchange

    def test_callback_google_com_metadados_e_alias_legado(self):
        from dataclasses import replace
        self.app = create_app(replace(configured_database(self.database_url), oidc_callback_path="/oauth2callback"))
        self.client.close()
        self.client = TestClient(self.app, base_url=ORIGIN, follow_redirects=False)
        self.addCleanup(self.client.close)
        state, _ = self._start_login()
        with patch("api.auth.exchange_code", return_value=verified_claims()) as exchange:
            response = self.client.get("/oauth2callback", params={
                "state": state, "code": "synthetic-code", "scope": "openid email profile",
                "authuser": "0", "prompt": "consent", "hd": "synthetic.example.test",
                "iss": "https://accounts.google.com",
            })
        self.assertEqual(response.status_code, 303)
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 200)
        self.assertEqual(exchange.call_args.kwargs["code"], "synthetic-code")
        replay, _ = self._callback(state, force_state_cookie=True, extra={"scope": "openid"})
        self.assertEqual(replay.json()["error"]["code"], "invalid_oidc_state")

    def test_callback_metadados_nao_contornam_validacoes(self):
        for extra in (
            {"iss": "https://attacker.invalid"}, {"unexpected": "synthetic"},
            {"error": "access_denied"}, {"state": "A" * 43},
        ):
            with self.subTest(extra=extra):
                state, _ = self._start_login()
                response, exchange = self._callback(state, extra=extra)
                self.assertEqual(response.json()["error"]["code"], "invalid_oidc_state")
                exchange.assert_not_called()

    def test_login_pkce_transacao_uso_unico_cookie_hash_e_me(self):
        state, authorization_args = self._start_login()
        self.assertEqual(len(authorization_args["state"]), 43)
        self.assertEqual(len(authorization_args["nonce"]), 43)
        self.assertEqual(len(authorization_args["code_challenge"]), 43)
        with psycopg.connect(self.database_url) as connection:
            transaction = connection.execute(
                "SELECT state_sha256, nonce, code_verifier FROM web_oidc_transactions"
            ).fetchone()
        self.assertEqual(transaction[0], sha256(state.encode("ascii")).hexdigest())
        self.assertEqual(transaction[1], authorization_args["nonce"])
        self.assertNotEqual(transaction[2], state)

        callback, exchange = self._callback(state)
        self.assertEqual(callback.status_code, 303)
        self.assertEqual(callback.headers["location"], "/")
        self.assertIn("code_verifier", exchange.call_args.kwargs)
        self.assertEqual(exchange.call_args.kwargs["expected_nonce"], authorization_args["nonce"])
        cookie = callback.cookies.get("__Host-stroop_professional")
        self.assertIsNotNone(cookie)
        self.assertGreaterEqual(len(cookie), 43)
        self.assertIn("secure", callback.headers["set-cookie"].lower())
        self.assertIn("httponly", callback.headers["set-cookie"].lower())
        self.assertIn("samesite=lax", callback.headers["set-cookie"].lower())
        self.assertNotIn("domain=", callback.headers["set-cookie"].lower())
        with psycopg.connect(self.database_url) as connection:
            session_row = connection.execute(
                """SELECT token_sha256, created_at, oidc_expires_at, expires_at
                   FROM web_professional_sessions"""
            ).fetchone()
            self.assertEqual(session_row[0], sha256(cookie.encode("ascii")).hexdigest())
            self.assertLessEqual(session_row[3], session_row[2])
            self.assertLessEqual(session_row[3], session_row[1] + timedelta(hours=8))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM web_oidc_transactions").fetchone()[0], 0)

        profile = self.client.get("/api/v1/auth/me")
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["user_id"], opaque_user_id(ISSUER, SUBJECT))
        self.assertEqual(profile.json()["role"], "administracao")
        csrf = profile.json()["csrf_token"]
        self.assertNotEqual(csrf, cookie)
        replay, _ = self._callback(state, force_state_cookie=True)
        self.assertEqual(replay.status_code, 400)
        self.assertEqual(replay.json()["error"]["code"], "invalid_oidc_state")

    def test_identidade_nao_cadastrada_nao_cria_sessao(self):
        state, _ = self._start_login()
        failed, _ = self._callback(state, subject="synthetic-not-registered")
        self.assertEqual(failed.status_code, 401)
        self.assertEqual(failed.json()["error"]["code"], "authentication_required")
        self.assertEqual(failed.json()["registration_request"], {"issuer": ISSUER, "subject": "synthetic-not-registered"})
        self.assertNotIn("email", failed.json()["registration_request"])
        self.assertNotIn("__Host-stroop_professional", failed.headers.get("set-cookie", ""))
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM web_professional_sessions").fetchone()[0], 0)

    def test_sessao_revalida_bloqueio_e_logout_exige_csrf(self):
        state, _ = self._start_login()
        callback, _ = self._callback(state)
        self.assertEqual(callback.status_code, 303)
        token = callback.cookies.get("__Host-stroop_professional")
        profile = self.client.get("/api/v1/auth/me")
        csrf = profile.json()["csrf_token"]

        bad = self.client.post(
            "/api/v1/auth/logout", json={}, headers={"Origin": ORIGIN, "X-CSRF-Token": "invalid"}
        )
        self.assertEqual((bad.status_code, bad.json()["error"]["code"]), (403, "csrf_failed"))
        self.assertEqual(
            web_auth.find_professional_session(self.database_url, sha256(token.encode()).hexdigest()).subject,
            SUBJECT,
        )

        admin = auth_application.authorize(
            self.database_url,
            verified_claims("synthetic-secondary-admin"),
            "manage_users",
        )
        auth_application.update_user(
            self.database_url,
            ISSUER,
            SUBJECT,
            role="administracao",
            active=False,
            email="synthetic@example.invalid",
            actor=admin,
        )
        blocked = self.client.get("/api/v1/auth/me")
        self.assertEqual((blocked.status_code, blocked.json()["error"]["code"]), (403, "account_blocked"))

        auth_application.update_user(
            self.database_url,
            ISSUER,
            SUBJECT,
            role="administracao",
            active=True,
            email="synthetic@example.invalid",
            actor=admin,
        )
        logged_out_response = self.client.post(
            "/api/v1/auth/logout", json={}, headers={"Origin": ORIGIN, "X-CSRF-Token": csrf}
        )
        self.assertEqual(logged_out_response.status_code, 204)
        logged_out = self.client.get("/api/v1/auth/me")
        self.assertEqual((logged_out.status_code, logged_out.json()["error"]["code"]), (401, "authentication_required"))

    def test_login_limita_tentativas_por_endereco_sem_persistir_ip(self):
        self.app.state.config = configured_database(
            self.database_url, login_rate_limit=2, login_rate_window_seconds=60
        )
        with patch(
            "api.auth.authorization_url",
            return_value="https://accounts.google.com/o/oauth2/v2/auth?synthetic=1",
        ) as authorization:
            responses = [self.client.get("/api/v1/auth/login") for _ in range(3)]
            extra_attempts = [self.client.get("/api/v1/auth/login") for _ in range(5)]
        self.assertEqual([response.status_code for response in responses], [303, 303, 429])
        self.assertTrue(all(response.status_code == 429 for response in extra_attempts))
        self.assertGreaterEqual(int(responses[2].headers["Retry-After"]), 1)
        self.assertLessEqual(int(responses[2].headers["Retry-After"]), 60)
        self.assertEqual(authorization.call_count, 2)
        with psycopg.connect(self.database_url) as connection:
            hashed_address, count = connection.execute(
                "SELECT remote_sha256, request_count FROM web_login_rate_limits"
            ).fetchone()
            self.assertRegex(hashed_address, r"^[0-9a-f]{64}$")
            self.assertEqual(count, 3)
            self.assertNotIn("testclient", hashed_address)

    def test_perfil_consulta_e_recusado_em_operacao_administrativa(self):
        administrator = auth_application.authorize(
            self.database_url, verified_claims(), "manage_users"
        )
        auth_application.create_user(
            self.database_url,
            ISSUER,
            "synthetic-reader",
            "consulta",
            None,
            administrator,
        )
        state, _ = self._start_login()
        callback, _ = self._callback(state, subject="synthetic-reader")
        self.assertEqual(callback.status_code, 303)
        self.assertEqual(self.client.get("/api/v1/auth/me").json()["role"], "consulta")
        denied = self.client.get("/api/v1/synthetic/admin-only")
        self.assertEqual((denied.status_code, denied.json()["error"]["code"]), (403, "permission_denied"))


def configured_database(database_url: str, **settings) -> APIConfig:
    return APIConfig(auth_mode="oidc",
        database_url=database_url,
        public_origin=ORIGIN,
        app_env="test",
        oidc_client_id="synthetic-client-id",
        oidc_client_secret="synthetic-client-secret-never-use",
        session_secret="synthetic-session-secret-never-use-0000000000",
        **settings,
    )


if __name__ == "__main__":
    unittest.main()
