"""Validacao criptografica OIDC com certificado RSA sintetico e sem rede."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import json
from unittest.mock import patch
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from api.config import APIConfig
from api.google_oidc import InvalidOIDCResponse, exchange_code


CLIENT_ID = "synthetic-client-id"
NONCE = "synthetic-oidc-nonce-value"
KID = "synthetic-key"


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


class GoogleOIDCCryptographicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "synthetic.invalid")])
        now = datetime.now(timezone.utc)
        cls.certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(cls.private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1))
            .sign(cls.private_key, hashes.SHA256())
            .public_bytes(serialization.Encoding.PEM)
            .decode("ascii")
        )
        cls.config = APIConfig(
            database_url="postgresql://synthetic:synthetic@127.0.0.1/stroop_etapa4_test_oidc",
            public_origin="https://synthetic.example.test",
            app_env="test",
            oidc_client_id=CLIENT_ID,
            oidc_client_secret="synthetic-client-secret-never-use",
            session_secret="synthetic-session-secret-never-use-0000000000",
        )

    @classmethod
    def token(cls, **changes):
        now = int(datetime.now(timezone.utc).timestamp())
        claims = {
            "iss": "https://accounts.google.com",
            "sub": "synthetic-professional-subject",
            "aud": CLIENT_ID,
            "exp": now + 300,
            "iat": now,
            "nonce": NONCE,
            "azp": CLIENT_ID,
        }
        claims.update(changes)
        header = {"alg": "RS256", "kid": KID, "typ": "JWT"}
        signing_input = (
            _b64url(json.dumps(header, separators=(",", ":")).encode())
            + "."
            + _b64url(json.dumps(claims, separators=(",", ":")).encode())
        )
        signature = cls.private_key.sign(
            signing_input.encode("ascii"), padding.PKCS1v15(), hashes.SHA256()
        )
        return signing_input + "." + _b64url(signature)

    def exchange(self, token):
        metadata = {
            "issuer": "https://accounts.google.com",
            "token_endpoint": "https://oauth2.googleapis.com/token",
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
            "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
            "token_endpoint_auth_methods_supported": ["client_secret_post"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
        with (
            patch("api.google_oidc._fetch_json", side_effect=[metadata, {"id_token": token}]),
            patch("google.oauth2.id_token._fetch_certs", return_value={KID: self.certificate}),
        ):
            return exchange_code(
                self.config,
                code="synthetic-authorization-code",
                code_verifier="synthetic-pkce-verifier",
                expected_nonce=NONCE,
            )

    def test_assinatura_issuer_audience_exp_nonce_e_azp_validos(self):
        claims = self.exchange(self.token())
        self.assertEqual(claims["sub"], "synthetic-professional-subject")

    def test_assinatura_invalida_e_recusada(self):
        valid = self.token().split(".")
        signature = bytearray(base64.urlsafe_b64decode(valid[2] + "=="))
        signature[0] ^= 1
        valid[2] = _b64url(bytes(signature))
        with self.assertRaises(InvalidOIDCResponse):
            self.exchange(".".join(valid))

    def test_claims_expirado_emissor_audiencia_nonce_e_azp_invalidos_sao_recusados(self):
        invalid_claims = (
            {"exp": int(datetime.now(timezone.utc).timestamp()) - 1},
            {"iss": "https://issuer.invalid"},
            {"aud": "another-client-id"},
            {"nonce": "different-synthetic-nonce"},
            {"azp": "another-client-id"},
        )
        for changes in invalid_claims:
            with self.subTest(changes=changes), self.assertRaises(InvalidOIDCResponse):
                self.exchange(self.token(**changes))


if __name__ == "__main__":
    unittest.main()
