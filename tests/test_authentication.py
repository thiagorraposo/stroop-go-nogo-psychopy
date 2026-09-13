"""Autenticacao OIDC e autorizacao com identidades sinteticas."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import psycopg

from dashboard import app, auth
from scripts import gerenciar_usuarios
from scripts.migrations import apply_migrations


ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get("TEST_DATABASE_URL", "")
ISSUER = "https://accounts.google.com"
FUTURE = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())


def claims(subject: str, *, expiration: int = FUTURE, email: str | None = None):
    result = {"iss": ISSUER, "sub": subject, "exp": expiration}
    if email is not None:
        result["email"] = email
    return result


class IdentityValidationTests(unittest.TestCase):
    def test_iss_sub_sao_identidade_e_email_e_apenas_auxiliar(self):
        first = auth.parse_identity(claims("synthetic-sub", email="first@example.invalid"))
        second = auth.parse_identity(claims("synthetic-sub", email="second@example.invalid"))
        self.assertEqual((first.issuer, first.subject), (second.issuer, second.subject))
        self.assertNotEqual(first.email, second.email)

    def test_issuer_e_claims_invalidas_sao_recusadas(self):
        invalid = [
            {"iss": "https://invalid.example", "sub": "x", "exp": FUTURE},
            {"iss": ISSUER, "sub": "", "exp": FUTURE},
            {"iss": ISSUER, "sub": "x", "exp": "invalid"},
        ]
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(auth.InvalidIdentityError):
                auth.parse_identity(item)

    def test_expiracao_e_verificada_explicitamente(self):
        identity = auth.parse_identity(claims("synthetic-sub", expiration=10))
        with self.assertRaises(auth.ExpiredIdentityError):
            auth.ensure_not_expired(
                identity, datetime.fromtimestamp(10, timezone.utc)
            )

    def test_perfis_e_permissoes_minimas(self):
        self.assertEqual(auth.ROLES, ("consulta", "importacao", "administracao"))
        self.assertEqual(
            auth.PERMISSIONS["import_csv"],
            frozenset({"importacao", "administracao"}),
        )
        self.assertEqual(auth.PERMISSIONS["manage_users"], frozenset({"administracao"}))

    def test_secrets_reais_sao_ignorados_e_exemplo_e_ficticio(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        example = (ROOT / ".streamlit" / "secrets.toml.example").read_text(
            encoding="utf-8"
        )
        self.assertIn("**/.streamlit/secrets.toml", gitignore)
        self.assertIn("cliente-google-ficticio", example)
        self.assertNotIn("access_token", example)

    def test_dashboard_usa_oidc_google_sem_autocadastro(self):
        source = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8")
        self.assertIn('streamlit_module.login("google")', source)
        self.assertNotIn("INSERT INTO app_users", source)
        self.assertIn('authorize(database_url, claims, "export_dashboard")', source)
        self.assertIn('claims, "import_csv"', source)

    def test_areas_nao_autorizadas_nao_aparecem(self):
        reader = auth.AppUser(ISSUER, "reader", None, "consulta", True)
        importer = auth.AppUser(ISSUER, "importer", None, "importacao", True)
        admin = auth.AppUser(ISSUER, "admin", None, "administracao", True)
        self.assertEqual(app.available_sections(reader), ["Resultados"])
        self.assertEqual(
            app.available_sections(importer), ["Resultados", "Importacao"]
        )
        self.assertEqual(
            app.available_sections(admin),
            ["Resultados", "Importacao", "Administracao"],
        )

    def test_exportacao_revalida_autorizacao_no_clique(self):
        user = auth.AppUser(ISSUER, "reader", None, "consulta", True)
        with patch.object(app, "authorize", return_value=user) as authorize_call, patch.object(
            app, "record_operation"
        ) as audit_call:
            payload = app._protected_export(
                claims("reader"), [{"assessment_date": "2026-01-01"}], None
            )
        self.assertTrue(payload.startswith(b"assessment_date"))
        authorize_call.assert_called_once()
        self.assertEqual(authorize_call.call_args.args[-1], "export_dashboard")
        audit_call.assert_called_once()

    def test_exportacao_recusada_nao_entrega_dados(self):
        with patch.object(
            app, "authorize", side_effect=auth.BlockedUserError("bloqueado")
        ):
            self.assertEqual(app._protected_export(claims("reader"), [], None), b"")


@unittest.skipUnless(URL, "TEST_DATABASE_URL nao configurada")
class AuthorizationIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not psycopg.conninfo.conninfo_to_dict(URL).get("dbname", "").startswith(
            "stroop_etapa4_test"
        ):
            raise RuntimeError("Banco descartavel obrigatorio")

    def setUp(self):
        with psycopg.connect(URL, autocommit=True) as connection:
            connection.execute("DROP SCHEMA public CASCADE")
            connection.execute("CREATE SCHEMA public")
        apply_migrations(URL)

    def bootstrap(self, subject="synthetic-admin"):
        auth.bootstrap_admin(URL, ISSUER, subject, "admin@example.invalid")
        return auth.authorize(URL, claims(subject), "manage_users")

    def audit_outcomes(self):
        with psycopg.connect(URL) as connection:
            return [
                row[0]
                for row in connection.execute(
                    "SELECT outcome FROM auth_audit_events ORDER BY audit_id"
                )
            ]

    def test_bootstrap_e_unico_e_nao_existe_autocadastro(self):
        auth.bootstrap_admin(URL, ISSUER, "synthetic-admin")
        with self.assertRaises(auth.InvalidIdentityError):
            auth.bootstrap_admin(URL, ISSUER, "synthetic-other")
        with self.assertRaises(auth.UnregisteredUserError):
            auth.authorize(URL, claims("synthetic-unknown"), "view_dashboard")
        with psycopg.connect(URL) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0], 1)

    def test_perfis_controlam_operacoes(self):
        admin = self.bootstrap()
        auth.create_user(URL, ISSUER, "synthetic-reader", "consulta", None, admin)
        auth.create_user(URL, ISSUER, "synthetic-importer", "importacao", None, admin)
        self.assertEqual(
            auth.authorize(URL, claims("synthetic-reader"), "view_dashboard").role,
            "consulta",
        )
        with self.assertRaises(auth.ForbiddenOperationError):
            auth.authorize(URL, claims("synthetic-reader"), "import_csv")
        self.assertEqual(
            auth.authorize(URL, claims("synthetic-importer"), "import_csv").role,
            "importacao",
        )
        with self.assertRaises(auth.ForbiddenOperationError):
            auth.authorize(URL, claims("synthetic-importer"), "manage_users")

    def test_bloqueio_e_expiracao_sao_revalidados(self):
        admin = self.bootstrap()
        auth.create_user(URL, ISSUER, "synthetic-reader", "consulta", None, admin)
        auth.update_user(
            URL,
            ISSUER,
            "synthetic-reader",
            role="consulta",
            active=False,
            email=None,
            actor=admin,
        )
        with self.assertRaises(auth.BlockedUserError):
            auth.authorize(URL, claims("synthetic-reader"), "view_dashboard")
        with self.assertRaises(auth.ExpiredIdentityError):
            auth.authorize(URL, claims("synthetic-admin", expiration=1), "view_dashboard")
        self.assertIn("denied_blocked", self.audit_outcomes())
        self.assertIn("denied_expired", self.audit_outcomes())

    def test_recusas_repetidas_sao_limitadas(self):
        for _ in range(auth.DENIAL_LIMIT):
            with self.assertRaises(auth.UnregisteredUserError):
                auth.authorize(URL, claims("synthetic-unknown"), "view_dashboard")
        with self.assertRaises(auth.RateLimitedError):
            auth.authorize(URL, claims("synthetic-unknown"), "view_dashboard")
        self.assertEqual(self.audit_outcomes()[-1], "rate_limited")

    def test_ultima_conta_administrativa_ativa_e_preservada(self):
        admin = self.bootstrap()
        with self.assertRaises(auth.InvalidIdentityError):
            auth.update_user(
                URL,
                ISSUER,
                admin.subject,
                role="consulta",
                active=True,
                email=None,
                actor=admin,
            )

    def test_recuperacao_nao_cria_usuario_automaticamente(self):
        admin = self.bootstrap()
        auth.create_user(URL, ISSUER, "synthetic-recovery", "consulta", None, admin)
        auth.recover_admin(URL, ISSUER, "synthetic-recovery")
        recovered = auth.authorize(URL, claims("synthetic-recovery"), "manage_users")
        self.assertEqual(recovered.role, "administracao")
        with self.assertRaises(auth.InvalidIdentityError):
            auth.recover_admin(URL, ISSUER, "synthetic-missing")

    def test_auditoria_minima_nao_armazena_email_ou_conteudo_clinico(self):
        self.bootstrap()
        with psycopg.connect(URL) as connection:
            columns = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'auth_audit_events'
                    """
                )
            }
        self.assertEqual(
            columns,
            {"audit_id", "occurred_at", "issuer", "subject", "action", "outcome", "request_id"},
        )

    def test_cli_exige_confirmacao_para_recuperacao(self):
        self.bootstrap()
        environment = {"AUTH_DATABASE_URL": URL}
        with patch.dict(os.environ, environment, clear=True):
            result = gerenciar_usuarios.main(
                ["recover-admin", "--issuer", ISSUER, "--subject", "synthetic-admin"]
            )
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
