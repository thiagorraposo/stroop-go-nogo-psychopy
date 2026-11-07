"""Compatibilidade opt-in com callback Google previamente cadastrado."""
from dataclasses import replace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from api.config import APIConfig, ConfigurationError
from api.google_oidc import InvalidOIDCResponse, authorization_url, exchange_code
from api.main import create_app
from api.auth import callback
from test_web_auth import config, ORIGIN


METADATA = {
    'issuer': 'https://accounts.google.com',
    'response_types_supported': ['code'],
    'code_challenge_methods_supported': ['S256'],
    'token_endpoint_auth_methods_supported': ['client_secret_post'],
    'id_token_signing_alg_values_supported': ['RS256'],
    'authorization_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_endpoint': 'https://oauth2.googleapis.com/token',
    'jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs',
}


class CallbackCompatibilityTests(unittest.TestCase):
    def test_config_recusa_callback_arbitrario(self):
        for value in ('/attacker', '//attacker.invalid', '/oauth2callback?x=1', None, []):
            with self.subTest(value=value), self.assertRaises(ConfigurationError):
                replace(config(), oidc_callback_path=value)

    def test_config_from_env_preserva_padrao_e_opcao(self):
        environment = dict(API_AUTH_MODE='oidc', API_DATABASE_URL=config().database_url, APP_ENV='test',
                           API_PUBLIC_ORIGIN=ORIGIN, OIDC_CLIENT_ID=config().oidc_client_id,
                           OIDC_CLIENT_SECRET=config().oidc_client_secret,
                           API_SESSION_SECRET=config().session_secret)
        self.assertEqual(APIConfig.from_env(environment).oidc_callback_path, '/api/v1/auth/callback')
        self.assertEqual(APIConfig.from_env({**environment, 'OIDC_CALLBACK_PATH': '/oauth2callback'}).oidc_callback_path, '/oauth2callback')

    def test_alias_inativo_retorna_404(self):
        with TestClient(create_app(config()), base_url=ORIGIN) as client:
            self.assertEqual(client.get('/oauth2callback').status_code, 404)

    def test_alias_ativo_preserva_handler_e_rejeita_state_sem_trocar_code(self):
        app = create_app(replace(config(), oidc_callback_path='/oauth2callback'))
        alias = next(route for route in app.routes if getattr(route, 'path', None) == '/oauth2callback')
        self.assertIs(alias.endpoint, callback)
        with TestClient(app, base_url=ORIGIN, follow_redirects=False) as client:
            with patch('api.auth.exchange_code') as exchange:
                response = client.get('/oauth2callback?state=synthetic-state&code=synthetic-secret')
                exchange.assert_not_called()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['error']['code'], 'invalid_oidc_state')
            self.assertNotIn('synthetic-secret', response.text)
            self.assertNotIn('location', response.headers)
            self.assertIn('__Host-stroop_oidc_state', response.headers['set-cookie'])
            self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_urls_autorizacao_e_troca_usam_mesmo_callback(self):
        for path in ('/api/v1/auth/callback', '/oauth2callback'):
            settings = replace(config(), oidc_callback_path=path)
            with patch('api.google_oidc._fetch_json', return_value=METADATA):
                url = authorization_url(settings, state='synthetic', nonce='synthetic', code_challenge='synthetic')
            self.assertEqual(parse_qs(urlsplit(url).query)['redirect_uri'], [ORIGIN + path])
            with patch('api.google_oidc._fetch_json', side_effect=[METADATA, {}]) as fetch:
                with self.assertRaises(InvalidOIDCResponse):
                    exchange_code(settings, code='synthetic', code_verifier='synthetic', expected_nonce='synthetic')
            self.assertEqual(fetch.call_args.kwargs['data']['redirect_uri'], ORIGIN + path)
