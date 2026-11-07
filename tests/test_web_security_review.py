"""Revisao negativa WEB: transporte e separacao de credenciais, sem banco/rede."""

import asyncio
import json
import time
import unittest
from unittest.mock import patch

from fastapi.responses import JSONResponse, Response
from fastapi.testclient import TestClient

from api.auth import PROFESSIONAL_COOKIE, _csrf_token
from api.google_oidc import InvalidOIDCResponse, exchange_code
from api.main import create_app
from api.sessions import PARTICIPANT_COOKIE, _participant_csrf
from tests.test_api_base import ORIGIN, synthetic_config


TOKEN = "synthetic_" + "x" * 43
SECRET = "SYNTHETIC_PRIVATE_REVIEW"


class WebSecurityReviewTests(unittest.TestCase):
    def setUp(self):
        self.config = synthetic_config()
        self.app = create_app(self.config)

        @self.app.get('/api/v1/security-synthetic-json')
        def untrusted_json():
            return JSONResponse({'synthetic_text': '<script>alert("SINTETICO")</script>'}, headers={
                'X-Content-Type-Options': 'unsafe-synthetic',
                'Content-Security-Policy': "default-src *",
                'Referrer-Policy': 'unsafe-url', 'Cross-Origin-Resource-Policy': 'cross-origin',
                'Cache-Control': 'public', 'X-Frame-Options': 'SAMEORIGIN',
            })

        @self.app.get('/api/v1/security-synthetic-csv')
        def synthetic_csv():
            return Response('coluna\r\nSINTETICO\r\n', media_type='text/csv', headers={
                'Content-Disposition': 'attachment; filename="synthetic.csv"',
            })

        @self.app.get('/api/v1/security-synthetic-error')
        def private_error():
            raise RuntimeError(SECRET)

        self.client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(self.client.close)

    def assert_headers(self, response):
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        self.assertEqual(response.headers['Referrer-Policy'], 'no-referrer')
        self.assertEqual(response.headers['Cross-Origin-Resource-Policy'], 'same-origin')
        self.assertEqual(response.headers['Content-Security-Policy'],
                         "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        for name in ('cache-control', 'content-security-policy', 'x-frame-options',
                     'x-content-type-options', 'referrer-policy', 'cross-origin-resource-policy'):
            self.assertEqual(len(response.headers.get_list(name)), 1)
        self.assertNotIn('access-control-allow-origin', response.headers)
        self.assertNotIn('access-control-allow-credentials', response.headers)

    def test_headers_protegem_json_csv_erros_e_substituem_valores_inseguros(self):
        responses = [self.client.get('/health/live'),
                     self.client.get('/api/v1/security-synthetic-json'),
                     self.client.get('/api/v1/security-synthetic-csv'),
                     self.client.get('/rota-sintetica-inexistente'),
                     self.client.get('/api/v1/auth/me'),
                     self.client.post('/api/v1/participant/start', json={}),
                     self.client.post('/api/v1/participant/redeem', content=b'{',
                                      headers={'Content-Type': 'application/json'})]
        for response in responses:
            with self.subTest(status=response.status_code):
                self.assert_headers(response)
        self.assertEqual(responses[1].headers['Content-Type'], 'application/json')
        self.assertIn('<script>', responses[1].json()['synthetic_text'])
        self.assertEqual(responses[2].headers['Content-Disposition'],
                         'attachment; filename="synthetic.csv"')

    def test_falha_privada_logs_e_header_de_correlacao_nao_refletem_entrada(self):
        with self.assertLogs('stroop.api', 'WARNING') as logs:
            response = self.client.get('/api/v1/security-synthetic-error',
                                       params={'segredo': SECRET}, headers={'X-Request-ID': SECRET})
        self.assertEqual(response.status_code, 500)
        self.assert_headers(response)
        self.assertNotIn(SECRET, response.text)
        self.assertNotIn(SECRET, repr(list(response.headers.items())))
        self.assertNotIn(SECRET, ' '.join(logs.output))
        self.assertEqual(len(logs.records), 1)
        self.assertEqual(logs.records[0].getMessage(),
                         f"request_failed request_id={response.headers['X-Request-ID']}")
        self.assertIsNone(logs.records[0].exc_info)

    def test_cors_preflight_e_origem_externa_nao_abrem_leitura(self):
        for method, path, headers in (
            ('OPTIONS', '/api/v1/projects', {'Origin': 'https://externo.invalid',
                                           'Access-Control-Request-Method': 'GET'}),
            ('GET', '/api/v1/participant/session', {'Origin': 'https://externo.invalid'}),
        ):
            response = self.client.request(method, path, headers=headers)
            self.assertIn(response.status_code, (401, 405))
            self.assert_headers(response)

    def test_cookies_participante_e_profissional_nao_sao_intercambiaveis(self):
        for path, cookie in (
            ('/api/v1/auth/me', f'{PARTICIPANT_COOKIE}={TOKEN}'),
            ('/api/v1/projects', f'{PARTICIPANT_COOKIE}={TOKEN}'),
            ('/api/v1/participant/session', f'{PROFESSIONAL_COOKIE}={TOKEN}'),
        ):
            with self.subTest(path=path), patch('api.auth.web_auth.find_professional_session') as professional, \
                    patch('api.sessions.persistence.participant_request_limit') as participant:
                response = self.client.get(path, headers={'Cookie': cookie})
            self.assertEqual(response.status_code, 401)
            professional.assert_not_called()
            participant.assert_not_called()

    def test_cookies_duplicados_nao_aceitam_primeiro_ou_ultimo_valor(self):
        for path, cookie_name in (('/api/v1/auth/me', PROFESSIONAL_COOKIE),
                                  ('/api/v1/participant/session', PARTICIPANT_COOKIE)):
            for headers in (
                [('Cookie', f'{cookie_name}={TOKEN}; {cookie_name}={TOKEN}')],
                [('Cookie', f'{cookie_name}={TOKEN}'), ('Cookie', f'{cookie_name}={TOKEN}')],
            ):
                with self.subTest(path=path), patch('api.auth.web_auth.find_professional_session') as professional, \
                        patch('api.sessions.persistence.participant_request_limit') as participant:
                    response = self.client.get(path, headers=headers)
                self.assertEqual(response.status_code, 401)
                professional.assert_not_called()
                participant.assert_not_called()

    def test_host_nao_depende_de_forwarded_e_rejeita_ambiguidade(self):
        for headers in (
            [('Host', 'externo.invalid'), ('X-Forwarded-Host', 'synthetic.example.test')],
            [('Host', 'synthetic.example.test'), ('Host', 'externo.invalid')],
            [('Host', 'synthetic.example.test:444')],
            [('Host', 'synthetic.example.test@externo.invalid')],
        ):
            response = self.client.get('/health/live', headers=headers)
            self.assertEqual(response.status_code, 422)
            self.assert_headers(response)
        accepted = self.client.get('/health/live', headers={'X-Forwarded-Host': 'externo.invalid'})
        self.assertEqual(accepted.status_code, 200)

    def test_origin_exato_unico_e_csrf_participante_distinto_do_profissional(self):
        participant_csrf = _participant_csrf(self.config, TOKEN)
        professional_csrf = _csrf_token(self.config, TOKEN)
        self.assertNotEqual(participant_csrf, professional_csrf)
        cookie = ('Cookie', f'{PARTICIPANT_COOKIE}={TOKEN}')
        cases = [
            [cookie, ('Origin', ORIGIN), ('X-CSRF-Token', professional_csrf)],
            [cookie, ('Origin', ORIGIN + '/'), ('X-CSRF-Token', participant_csrf)],
            [cookie, ('Origin', 'null'), ('X-CSRF-Token', participant_csrf)],
            [cookie, ('X-Forwarded-Origin', ORIGIN), ('X-CSRF-Token', participant_csrf)],
            [cookie, ('Origin', ORIGIN), ('Origin', ORIGIN), ('X-CSRF-Token', participant_csrf)],
            [cookie, ('Origin', ORIGIN), ('X-CSRF-Token', participant_csrf), ('X-CSRF-Token', participant_csrf)],
        ]
        for headers in cases:
            with self.subTest(case=cases.index(headers)), patch('api.sessions.persistence.participant_request_limit') as limit:
                response = self.client.post('/api/v1/participant/start', json={'app_version': 'web-0.1.0'}, headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()['error']['code'], 'csrf_failed')
            limit.assert_not_called()

    def test_origin_exato_obrigatorio_antes_de_resgate_e_logout_sem_cookie(self):
        for path, body in (('/api/v1/participant/redeem', {'code': 's' * 43}),
                           ('/api/v1/participant/logout', {}), ('/api/v1/auth/logout', {})):
            for origin in ('https://externo.invalid', ORIGIN + '/', 'null', ''):
                response = self.client.post(path, json=body, headers={'Origin': origin})
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()['error']['code'], 'csrf_failed')

    def test_logout_sem_cookie_idempotente_preserva_flags_e_nao_cria_sessao(self):
        for path, name in (('/api/v1/auth/logout', PROFESSIONAL_COOKIE),
                           ('/api/v1/participant/logout', PARTICIPANT_COOKIE)):
            response = self.client.post(path, json={}, headers={'Origin': ORIGIN})
            self.assertEqual(response.status_code, 204)
            self.assert_headers(response)
            cookie = response.headers['Set-Cookie']
            for flag in (f'{name}=', 'Secure', 'HttpOnly', 'SameSite=lax', 'Path=/', 'Max-Age=0'):
                self.assertIn(flag, cookie)
            self.assertNotIn('Domain=', cookie)

    def test_content_length_ambiguo_incorreto_e_transfer_encoding_recusados(self):
        cases = [
            [(b'content-length', b'0')], [(b'content-length', b'3')],
            [(b'content-length', b'2'), (b'content-length', b'2')],
            [(b'content-length', b'2'), (b'transfer-encoding', b'chunked')],
            [(b'transfer-encoding', b'gzip, chunked')],
            [(b'transfer-encoding', b'chunked'), (b'transfer-encoding', b'chunked')],
        ]
        for headers in cases:
            with self.subTest(headers=headers):
                status, body = self.asgi_body(headers)
                self.assertEqual(status, 400)
                self.assertEqual(body['error']['code'], 'invalid_json')
        # ASGI ja entrega chunks decodificados, e o fluxo valido sem CL permanece suportado.
        for headers in ([], [(b'content-length', b'2')], [(b'transfer-encoding', b'chunked')]):
            status, body = self.asgi_body(headers)
            self.assertEqual(status, 405)  # /health/live nao recebe POST; transporte aceitou o corpo.
            self.assertEqual(body['error']['code'], 'method_not_allowed')

    def asgi_body(self, extra_headers):
        async def invoke():
            messages = []
            async def receive():
                return {'type': 'http.request', 'body': b'{}', 'more_body': False}
            async def send(message):
                messages.append(message)
            await self.app({
                'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
                'method': 'POST', 'scheme': 'https', 'path': '/health/live',
                'raw_path': b'/health/live', 'query_string': b'', 'root_path': '',
                'headers': [(b'host', b'synthetic.example.test'), (b'content-type', b'application/json'), *extra_headers],
                'client': ('127.0.0.1', 1234), 'server': ('synthetic.example.test', 443),
            }, receive, send)
            start = next(m for m in messages if m['type'] == 'http.response.start')
            content = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
            return start['status'], json.loads(content)
        return asyncio.run(invoke())


class OIDCReviewTests(unittest.TestCase):
    def test_nonce_nao_ascii_e_recusado_com_erro_oidc_fechado_sem_typeerror(self):
        metadata = {
            'issuer': 'https://accounts.google.com',
            'token_endpoint_auth_methods_supported': ['client_secret_post'],
            'id_token_signing_alg_values_supported': ['RS256'],
            'authorization_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_endpoint': 'https://oauth2.googleapis.com/token',
            'jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs',
        }
        claims = {'nonce': 'sintetico_ç', 'iss': 'https://accounts.google.com',
                  'exp': int(time.time()) + 300, 'iat': int(time.time()), 'sub': 'synthetic-sub'}
        with patch('api.google_oidc._fetch_json', side_effect=[metadata, {'id_token': 'synthetic-id-token'}]), \
                patch('api.google_oidc.verify_oauth2_token', return_value=claims), \
                self.assertRaises(InvalidOIDCResponse):
            exchange_code(synthetic_config(), code='synthetic-code', code_verifier='synthetic-verifier',
                          expected_nonce='synthetic-nonce')


class LocalAuthSecurityReviewTests(unittest.TestCase):
    def setUp(self):
        self.config = synthetic_config(auth_mode='local', oidc_client_id='', oidc_client_secret='',
                                       oidc_callback_path='/oauth2callback')
        self.app = create_app(self.config)
        self.client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(self.client.close)

    def test_corte_oidc_retorna_404_com_headers_seguros_sem_consultar_provedor(self):
        for path in ('/api/v1/auth/login', '/api/v1/auth/callback', '/oauth2callback'):
            with self.subTest(path=path), patch('api.auth.authorization_url') as auth_url, \
                    patch('api.auth.exchange_code') as exchange:
                response = self.client.get(path)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json()['error']['code'], 'not_found')
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            auth_url.assert_not_called()
            exchange.assert_not_called()

    def test_cookies_e_duplicatas_recusados_no_modo_local_sem_consultar_sessao(self):
        for path, headers in (
            ('/api/v1/auth/me', [('Cookie', f'{PARTICIPANT_COOKIE}={TOKEN}')]),
            ('/api/v1/projects', [('Cookie', f'{PARTICIPANT_COOKIE}={TOKEN}')]),
            ('/api/v1/participant/session', [('Cookie', f'{PROFESSIONAL_COOKIE}={TOKEN}')]),
            ('/api/v1/auth/me', [('Cookie', f'{PROFESSIONAL_COOKIE}={TOKEN}; {PROFESSIONAL_COOKIE}={TOKEN}')]),
            ('/api/v1/auth/me', [('Cookie', f'{PROFESSIONAL_COOKIE}={TOKEN}'), ('Cookie', f'{PROFESSIONAL_COOKIE}={TOKEN}')]),
        ):
            with self.subTest(path=path, headers=headers), \
                    patch('api.auth.local_application.session_context') as local_context, \
                    patch('api.sessions.persistence.participant_request_limit') as participant_limit:
                response = self.client.get(path, headers=headers)
            self.assertEqual(response.status_code, 401)
            local_context.assert_not_called()
            participant_limit.assert_not_called()

    def test_login_senha_e_revogacao_exigem_origin_unico_e_limitam_corpo_4kib(self):
        for path, body in (
            ('/api/v1/auth/login', {'username': 'synthetic', 'password': 'x' * 20}),
            ('/api/v1/auth/password', {'current_password': 'x' * 20, 'new_password': 'y' * 20}),
        ):
            for origin_headers in ([], [('Origin', 'null')], [('Origin', 'https://externo.invalid')],
                                   [('Origin', ORIGIN), ('Origin', ORIGIN)]):
                with self.subTest(path=path, origin_headers=origin_headers), \
                        patch('api.local_auth.application.authenticate') as auth_call, \
                        patch('api.local_auth.application.change_password_limited') as pwd_call:
                    response = self.client.post(path, json=body, headers=origin_headers)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()['error']['code'], 'csrf_failed')
                auth_call.assert_not_called()
                pwd_call.assert_not_called()
            too_large = self.client.post(
                path, content=b'{"password":"' + b'x' * 4096 + b'"}',
                headers={'Origin': ORIGIN, 'Content-Type': 'application/json'},
            )
            self.assertEqual(too_large.status_code, 413)
            self.assertEqual(too_large.json()['error']['code'], 'body_too_large')

    def test_falha_interna_em_login_local_nao_loga_usuario_ou_senha(self):
        secret_user = 'synthetic_user_secret'
        secret_pass = 'Synthetic_Password_Secret_2026!'
        with patch('api.local_auth.application.authenticate', side_effect=RuntimeError(secret_pass)), \
                self.assertLogs('stroop.api', 'WARNING') as logs:
            response = self.client.post(
                '/api/v1/auth/login',
                json={'username': secret_user, 'password': secret_pass},
                headers={'Origin': ORIGIN},
            )
        self.assertEqual(response.status_code, 500)
        self.assertNotIn(secret_user, response.text)
        self.assertNotIn(secret_pass, response.text)
        self.assertNotIn(secret_user, ' '.join(logs.output))
        self.assertNotIn(secret_pass, ' '.join(logs.output))
