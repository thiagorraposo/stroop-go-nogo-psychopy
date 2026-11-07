"""Finalizacao de acesso participante sem apagar dados sinteticos concluidos."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import os
import unittest

import psycopg
from fastapi.testclient import TestClient

from api.sessions import PARTICIPANT_COOKIE
from tests import test_web_sessions as helpers


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'TEST_DATABASE_URL nao configurada')
class ParticipantLogoutTests(unittest.TestCase):
    def setUp(self):
        self.database_url = os.environ['TEST_DATABASE_URL']
        if not psycopg.conninfo.conninfo_to_dict(self.database_url).get('dbname', '').startswith('stroop_etapa4_test'):
            raise RuntimeError('Banco descartavel obrigatorio')
        self.h = helpers.WebSessionsPostgresTests()
        self.h.database_url = self.database_url
        self.addCleanup(self.h.doCleanups)
        self.h.setUp()

    def copy_client(self, participant):
        copy = self.h._participant_client()
        self.addCleanup(copy.close)
        copy.cookies.update(participant.cookies)
        copy.headers['X-CSRF-Token'] = participant.headers['X-CSRF-Token']
        return copy

    def test_preparacao_logout_invalida_cookie_e_hash_com_repeticao_idempotente(self):
        participant, payload, issued = self.h._completion(start=False)
        replay = self.copy_client(participant)
        response = participant.post('/api/v1/participant/logout', json={})
        self.assertEqual(response.status_code, 204, response.text)
        self.assertIn('Max-Age=0', response.headers['set-cookie'])
        self.assertIn('Secure', response.headers['set-cookie'])
        self.assertIn('HttpOnly', response.headers['set-cookie'])
        self.assertEqual(replay.get('/api/v1/participant/session').status_code, 401)
        self.assertEqual(participant.post('/api/v1/participant/logout', json={}).status_code, 204)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT state,abort_reason FROM web_participant_sessions').fetchone(),
                             ('aborted', 'user_cancelled'))
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0], 0)

    def test_recibo_headers_e_logout_preservam_resultado_sem_reabrir_acesso(self):
        participant, payload, _ = self.h._completion()
        complete = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(complete.status_code, 201, complete.text)
        bootstrap = participant.get('/api/v1/participant/session')
        recovered=bootstrap.json()
        self.assertEqual(recovered.pop('checkpoint')['confirmed_through'],16)
        self.assertEqual(recovered, complete.json())
        self.assertEqual(bootstrap.headers['x-csrf-token'], participant.headers['X-CSRF-Token'])
        self.assertTrue(bootstrap.headers['x-session-expires-at'].endswith('Z'))
        replay = self.copy_client(participant)
        self.assertEqual(participant.post('/api/v1/participant/logout', json={}).status_code, 204)
        self.assertEqual(replay.post('/api/v1/participant/complete', json=payload).status_code, 401)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT state FROM web_participant_sessions').fetchone()[0], 'completed')
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0], 1)
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM trial_results').fetchone()[0], 16)
            self.assertEqual(connection.execute('SELECT receipt FROM web_assessments').fetchone()[0], complete.json())

    def test_origem_csrf_corpo_fechado_e_cookie_profissional_nao_substitui_participante(self):
        participant, payload, _ = self.h._completion(start=False)
        for headers in ({'Origin': 'https://other.synthetic.test'}, {'X-CSRF-Token': 'x' * 43}):
            response = participant.post('/api/v1/participant/logout', json={}, headers=headers)
            self.assertEqual(response.status_code, 403)
        self.assertEqual(participant.post('/api/v1/participant/logout', json={'extra': True}).status_code, 422)
        self.assertEqual(participant.get('/api/v1/participant/session').status_code, 200)
        anonymous = TestClient(self.h.app, base_url=helpers.ORIGIN)
        self.addCleanup(anonymous.close)
        self.assertEqual(anonymous.post('/api/v1/participant/logout', json={}).status_code, 403)
        self.assertEqual(anonymous.post('/api/v1/participant/logout', json={}, headers={'Origin': helpers.ORIGIN}).status_code, 204)
        self.assertEqual(self.h.admin.post('/api/v1/participant/logout', json={}).status_code, 204)
        self.assertEqual(self.h.admin.get('/api/v1/auth/me').status_code, 200)

    def test_logout_concorrente_com_conclusao_nunca_restaura_credencial_ou_grava_parcial(self):
        participant, payload, _ = self.h._completion()
        ending = self.copy_client(participant)
        old_token = participant.cookies.get(PARTICIPANT_COOKIE)
        with ThreadPoolExecutor(max_workers=2) as executor:
            complete = executor.submit(participant.post, '/api/v1/participant/complete', json=payload)
            logout = executor.submit(ending.post, '/api/v1/participant/logout', json={})
            response, ended = complete.result(), logout.result()
        self.assertEqual(ended.status_code, 204, ended.text)
        self.assertIn(response.status_code, (201, 401), response.text)
        self.assertEqual(participant.get('/api/v1/participant/session').status_code, 401)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM web_participant_sessions WHERE participant_token_sha256=%s',
                                               (sha256(old_token.encode()).hexdigest(),)).fetchone()[0], 0)
            assessments = connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0]
            self.assertIn(assessments, (0, 1))
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM trial_results').fetchone()[0], 16 * assessments)
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessment_metrics').fetchone()[0], 12 * assessments)
