"""Integracao de convites e ciclo de sessao com PostgreSQL sintetico."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import os
import secrets
import unittest

import psycopg
from fastapi.testclient import TestClient

from api.auth import PROFESSIONAL_COOKIE, _csrf_token, opaque_user_id
from api.config import APIConfig
from api.main import create_app
from api.sessions import _participant_csrf
from scripts.migrations import apply_migrations
from stroop.application import auth as auth_application
from stroop.persistence import web_auth


ORIGIN = "https://synthetic.example.test"
ISSUER = "https://accounts.google.com"
ADMIN = "synthetic-web-admin"
IMPORTER = "synthetic-web-importer"
CONSULTA = "synthetic-web-consulta"
OUTSIDER = "synthetic-web-outsider"


@unittest.skipUnless(os.environ.get("TEST_DATABASE_URL"), "TEST_DATABASE_URL nao configurada")
class WebSessionsPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = os.environ["TEST_DATABASE_URL"]
        db_name = psycopg.conninfo.conninfo_to_dict(cls.database_url).get("dbname", "")
        if not db_name.startswith("stroop_etapa4_test"):
            raise RuntimeError("Banco PostgreSQL descartavel obrigatorio")

    def setUp(self):
        with psycopg.connect(self.database_url, autocommit=True) as connection:
            connection.execute("DROP SCHEMA public CASCADE")
            connection.execute("CREATE SCHEMA public")
        apply_migrations(self.database_url)
        auth_application.bootstrap_admin(self.database_url, ISSUER, ADMIN)
        admin = self._claims(ADMIN)
        administrator = auth_application.authorize(self.database_url, admin, "manage_users")
        for subject, role in ((IMPORTER, "importacao"), (CONSULTA, "consulta"),
                              (OUTSIDER, "importacao")):
            auth_application.create_user(self.database_url, ISSUER, subject,
                                         role, None, administrator)
        self.app = create_app(self._config())
        self.admin = self._client(ADMIN)
        self.importer = self._client(IMPORTER)
        self.consulta = self._client(CONSULTA)
        self.outsider = self._client(OUTSIDER)
        for client in (self.admin, self.importer, self.consulta, self.outsider):
            self.addCleanup(client.close)
        self.project_id = self._create_project()
        self._set_member(self.admin, ADMIN)
        self._set_member(self.admin, IMPORTER)
        self._set_member(self.admin, CONSULTA)

    def _config(self):
        return APIConfig(
            database_url=self.database_url, public_origin=ORIGIN, app_env="test",
            oidc_client_id="synthetic-client-id",
            oidc_client_secret="synthetic-client-secret-never-use",
            session_secret="synthetic-session-secret-never-use-0000000000",
        )

    @staticmethod
    def _claims(subject):
        return {"iss": ISSUER, "sub": subject,
                "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())}

    def _client(self, subject, register=True):
        token = secrets.token_urlsafe(32)
        if register:
            user = auth_application.authorize(
                self.database_url, self._claims(subject), "view_dashboard"
            )
            web_auth.create_professional_session(
                self.database_url, sha256(token.encode("ascii")).hexdigest(),
                user.issuer, user.subject, int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            )
        client = TestClient(self.app, base_url=ORIGIN)
        client.cookies.set(PROFESSIONAL_COOKIE, token)
        client.headers.update({
            "Origin": ORIGIN,
            "X-CSRF-Token": _csrf_token(self._config(), token),
        })
        return client

    def _create_project(self):
        response = self.admin.post("/api/v1/projects", json={
            "code": "SYNTHETIC_WEB", "name": "Projeto sintetico",
        })
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    def _set_member(self, client, subject, active=True):
        response = client.put(
            f"/api/v1/projects/{self.project_id}/members/{opaque_user_id(ISSUER, subject)}",
            json={"active": active},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def _issue(self, client=None):
        response = (client or self.importer).post(
            f"/api/v1/projects/{self.project_id}/invitations",
            json={"participant_id": "P_SINTETICO", "visit": "V_SINTETICA"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def _participant_client(self):
        client = TestClient(self.app, base_url=ORIGIN)
        client.headers.update({"Origin": ORIGIN})
        return client

    def _completion(self, *, no_responses=False, start=True):
        issued = self._issue()
        participant = self._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post('/api/v1/participant/redeem', json={'code': issued['code']})
        self.assertEqual(redeemed.status_code, 201, redeemed.text)
        participant.headers['X-CSRF-Token'] = redeemed.json()['csrf_token']
        bootstrap = participant.get('/api/v1/participant/session').json()
        payload = {
            'protocol_id': bootstrap['protocol_id'], 'test_version': bootstrap['test_version'],
            'platform': 'web', 'app_version': 'synthetic-web-0.1.0',
            'frame_period_ms': 16, 'trials': [],
        }
        for index, condition in enumerate(bootstrap['main_conditions']):
            start_ms = index * 3750
            responds = not no_responses and condition['condition_id'] % 2 == 0
            payload['trials'].append({
                'trial_number': index + 1, 'condition_id': condition['condition_id'],
                'key_pressed': 'space' if responds else None,
                'reaction_time_ms': 512.25 if responds else None,
                'trial_start_ms': start_ms, 'stimulus_onset_ms': start_ms + 300,
                'stimulus_offset_ms': start_ms + 2800, 'trial_end_ms': start_ms + 3750,
                'key_at_ms': start_ms + 812.25 if responds else None,
            })
        if start:
            response = participant.post('/api/v1/participant/start', json={'app_version': payload['app_version']})
            self.assertEqual(response.status_code, 200, response.text)
        return participant, payload, issued

    def _counts(self):
        with psycopg.connect(self.database_url) as connection:
            return tuple(connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                         for table in ('assessments', 'trial_results', 'assessment_metrics',
                                       'web_assessments', 'web_trial_observations'))

    def test_complete_recalcula_quatro_respostas_e_recupera_recibo(self):
        participant, payload, issued = self._completion()
        response = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        receipt = response.json()
        self.assertEqual(receipt['summary'], {
            'accuracy': 50, 'response_time_seconds': 0.51225, 'total_trials': 16,
            'hits': 4, 'omission_errors': 4, 'commission_errors': 4, 'correct_rejections': 4,
        })
        self.assertEqual((receipt['platform'], receipt['state']), ('web', 'completed'))
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertEqual(self._counts(), (1, 16, 12, 1, 16))
        self.assertEqual(participant.get('/api/v1/participant/session').json(), receipt)
        self.assertEqual(participant.post('/api/v1/participant/abort', json={'reason': 'user_cancelled'}).status_code, 409)
        self.assertEqual(participant.post('/api/v1/participant/start', json={'app_version': payload['app_version']}).status_code, 409)
        with psycopg.connect(self.database_url) as connection:
            values = connection.execute(
                'SELECT participant_name,initials,evaluator,source_file FROM assessments'
            ).fetchone()
            self.assertEqual(values, ('NAO_COLETADO', None, opaque_user_id(ISSUER, IMPORTER), f"web:{issued['session_id']}"))
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM trial_results WHERE reaction_time = 0.51225"
            ).fetchone()[0], 8)

    def test_complete_sem_hits_preserva_sentinel_e_null_http(self):
        participant, payload, _ = self._completion(no_responses=True)
        response = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertIsNone(response.json()['summary']['response_time_seconds'])
        self.assertEqual(response.json()['summary']['hits'], 0)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute(
                "SELECT metric_value FROM assessment_metrics WHERE metric_code='response_time'"
            ).fetchone()[0], 0.0)

    def test_complete_retry_numerico_equivalente_e_conflito(self):
        participant, payload, _ = self._completion()
        first = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(first.status_code, 201, first.text)
        retry_payload = deepcopy(payload)
        retry_payload['frame_period_ms'] = 16.0
        retry_payload['trials'][0]['trial_start_ms'] = -0.0
        retry = participant.post('/api/v1/participant/complete', json=retry_payload)
        self.assertEqual(retry.status_code, 200, retry.text)
        self.assertEqual(retry.json(), first.json())
        different = deepcopy(payload)
        different['frame_period_ms'] = 17
        conflict = participant.post('/api/v1/participant/complete', json=different)
        self.assertEqual((conflict.status_code, conflict.json()['error']['code']), (409, 'result_conflict'))
        self.assertEqual(self._counts(), (1, 16, 12, 1, 16))

    def test_complete_invalido_nao_grava_nem_muda_running(self):
        participant, payload, issued = self._completion()
        cases = []
        for key, value in [('protocol_id', 'wrong'), ('test_version', 'wrong'),
                           ('platform', 'psychopy'), ('app_version', 'wrong'),
                           ('frame_period_ms', True), ('trials', payload['trials'][:15])]:
            invalid = deepcopy(payload)
            invalid[key] = value
            cases.append(invalid)
        for key, value in [('condition_id', 0), ('trial_number', True),
                           ('stimulus_offset_ms', 2800 + 17), ('trial_start_ms', 1)]:
            invalid = deepcopy(payload)
            invalid['trials'][0][key] = value
            cases.append(invalid)
        invalid = deepcopy(payload)
        invalid['summary'] = {'accuracy': 100}
        cases.append(invalid)
        invalid = deepcopy(payload)
        invalid['trials'][0].update(key_pressed='space', reaction_time_ms=5e-324,
                                     key_at_ms=300.00000000000006)
        cases.append(invalid)
        for index, invalid in enumerate(cases):
            with self.subTest(case=index):
                response = participant.post('/api/v1/participant/complete', json=invalid)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertEqual(self._counts(), (0, 0, 0, 0, 0))
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute(
                'SELECT state FROM web_participant_sessions WHERE session_id=%s', (issued['session_id'],)
            ).fetchone()[0], 'running')

    def test_complete_rollback_real_e_retry_apos_falha(self):
        participant, payload, _ = self._completion()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("""CREATE FUNCTION synthetic_fail_result() RETURNS trigger
                LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic rollback probe'; END $$""")
            connection.execute("""CREATE TRIGGER synthetic_result_failure BEFORE INSERT
                ON web_trial_observations FOR EACH ROW EXECUTE FUNCTION synthetic_fail_result()""")
        failed = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(failed.status_code, 503, failed.text)
        self.assertNotIn('synthetic rollback probe', failed.text)
        self.assertEqual(self._counts(), (0, 0, 0, 0, 0))
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT state FROM web_participant_sessions').fetchone()[0], 'running')
            connection.execute('DROP TRIGGER synthetic_result_failure ON web_trial_observations')
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 201)

    def test_complete_concorrente_identico_e_diferente(self):
        for different in (False, True):
            with self.subTest(different=different):
                participant, payload, _ = self._completion()
                bodies = [deepcopy(payload), deepcopy(payload)]
                if different:
                    bodies[1]['frame_period_ms'] = 17
                cookie = participant.cookies.get('__Host-stroop_participant')
                csrf = participant.headers['X-CSRF-Token']
                def send(body):
                    with TestClient(self.app, base_url=ORIGIN) as client:
                        client.cookies.set('__Host-stroop_participant', cookie)
                        return client.post('/api/v1/participant/complete', json=body,
                                           headers={'Origin': ORIGIN, 'X-CSRF-Token': csrf})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    responses = list(pool.map(send, bodies))
                self.assertEqual(sorted(item.status_code for item in responses), [201, 409] if different else [200, 201])
                if not different:
                    self.assertEqual(responses[0].json(), responses[1].json())
        self.assertEqual(self._counts(), (2, 32, 24, 2, 32))

    def test_complete_expirado_nao_altera_resultado_concluido(self):
        participant, payload, issued = self._completion()
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 201)
        with psycopg.connect(self.database_url) as connection:
            connection.execute("""UPDATE web_participant_sessions SET
                activated_at=CURRENT_TIMESTAMP-INTERVAL '31 minutes',
                expires_at=CURRENT_TIMESTAMP-INTERVAL '1 minute' WHERE session_id=%s""", (issued['session_id'],))
        self.assertEqual(participant.get('/api/v1/participant/session').status_code, 410)
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 410)
        self.assertEqual(participant.post('/api/v1/participant/start', json={'app_version': payload['app_version']}).status_code, 410)
        self.assertEqual(self._counts(), (1, 16, 12, 1, 16))
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT state FROM web_participant_sessions').fetchone()[0], 'completed')

    def test_complete_exige_estado_credencial_csrf_e_acesso(self):
        participant, payload, issued = self._completion(start=False)
        self.assertEqual(self.importer.post('/api/v1/participant/complete', json={}).status_code, 401)
        self.assertEqual(participant.post('/api/v1/participant/complete', json={}).status_code, 409)
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 409)
        self.assertEqual(self.importer.post('/api/v1/participant/complete', json=payload).status_code, 401)
        participant.post('/api/v1/participant/start', json={'app_version': payload['app_version']})
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload,
                                         headers={'X-CSRF-Token': 'invalid'}).status_code, 403)
        self.importer.post(f"/api/v1/projects/{self.project_id}/invitations/{issued['invitation_id']}/revoke", json={})
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 404)
        self.assertEqual(self._counts(), (0, 0, 0, 0, 0))
        aborted, aborted_payload, _ = self._completion()
        self.assertEqual(aborted.post('/api/v1/participant/abort', json={'reason': 'focus_lost'}).status_code, 200)
        self.assertEqual(aborted.post('/api/v1/participant/complete', json=aborted_payload).status_code, 409)
        self.assertEqual(self._counts(), (0, 0, 0, 0, 0))

    def test_credencial_participante_desconhecida_e_401(self):
        unknown = self._participant_client()
        self.addCleanup(unknown.close)
        token = secrets.token_urlsafe(32)
        unknown.cookies.set('__Host-stroop_participant', token)
        unknown.headers['X-CSRF-Token'] = _participant_csrf(self._config(), token)
        self.assertEqual(unknown.get('/api/v1/participant/session').status_code, 401)
        self.assertEqual(unknown.post('/api/v1/participant/complete', json={}).status_code, 401)

    def test_limites_participantes_isolam_leitura_escrita_e_profissional(self):
        participant, payload, _ = self._completion()
        self.app.state.config = replace(self._config(), participant_read_rate_limit=1,
                                        participant_write_rate_limit=1)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('DELETE FROM web_participant_request_limits')
        self.assertEqual(participant.get('/api/v1/participant/session').status_code, 200)
        limited = participant.get('/api/v1/participant/session')
        self.assertEqual(limited.status_code, 429)
        self.assertGreaterEqual(int(limited.headers['retry-after']), 1)
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 201)
        self.assertEqual(participant.post('/api/v1/participant/complete', json=payload).status_code, 429)
        self.assertEqual(self.admin.get('/api/v1/projects').status_code, 200)
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute('SELECT credential_sha256,request_count FROM web_participant_request_limits').fetchall()
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(len(row[0]) == 64 and row[1] == 2 for row in rows))
            self.assertTrue(all(participant.cookies.get('__Host-stroop_participant') not in row[0] for row in rows))

    def test_projeto_convite_hash_ordem_bootstrap_start_e_abort(self):
        issued = self._issue()
        self.assertEqual(len(issued["code"]), 43)
        self.assertNotIn(issued["code"], str(self._read_invitation(issued["invitation_id"])))
        self.assertEqual(issued["state"], "issued")
        self.assertEqual(__import__("uuid").UUID(issued["session_id"]).version, 4)

        participant = self._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post("/api/v1/participant/redeem", json={"code": issued["code"]})
        self.assertEqual(redeemed.status_code, 201, redeemed.text)
        csrf = redeemed.json()["csrf_token"]
        self.assertIn("__Host-stroop_participant", redeemed.headers["set-cookie"])
        bootstrap = participant.get("/api/v1/participant/session")
        self.assertEqual(bootstrap.status_code, 200, bootstrap.text)
        data = bootstrap.json()
        self.assertEqual(data["state"], "preparing")
        self.assertEqual(len(data["practice_conditions"]), 4)
        self.assertEqual(len(data["main_conditions"]), 16)
        self.assertEqual(data["protocol"]["main"]["trial_ms"], 3750)
        self.assertEqual(data["protocol"]["main"]["duration_ms"], 60000)
        condition_order = [item["condition_id"] for item in data["main_conditions"]]
        self.assertEqual(sorted(condition_order), list(range(1, 17)))
        session_id = data["session_id"]
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT array_agg(condition_id ORDER BY trial_number) FROM web_session_main_order WHERE session_id=%s",
                    (session_id,),
                ).fetchone()[0], condition_order,
            )

        headers = {"Origin": ORIGIN, "X-CSRF-Token": csrf}
        started = participant.post("/api/v1/participant/start",
                                   json={"app_version": "web-0.1.0"}, headers=headers)
        self.assertEqual(started.status_code, 200, started.text)
        again = participant.post("/api/v1/participant/start",
                                 json={"app_version": "web-0.1.0"}, headers=headers)
        self.assertEqual(again.status_code, 200)
        self.assertEqual(again.json()["started_at"], started.json()["started_at"])
        conflict = participant.post("/api/v1/participant/start",
                                    json={"app_version": "web-0.2.0"}, headers=headers)
        self.assertEqual(conflict.status_code, 409)
        aborted = participant.post("/api/v1/participant/abort",
                                   json={"reason": "focus_lost"}, headers=headers)
        self.assertEqual((aborted.status_code, aborted.json()["state"]), (200, "aborted"))
        self.assertEqual(participant.get("/api/v1/participant/session").status_code, 409)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 0)

    def test_limite_de_leitura_profissional_por_credencial(self):
        self.app.state.config = replace(self._config(), professional_read_rate_limit=1)
        first = self.admin.get("/api/v1/projects")
        second = self.admin.get("/api/v1/projects")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertGreaterEqual(int(second.headers["retry-after"]), 1)

    def _read_invitation(self, invitation_id):
        with psycopg.connect(self.database_url) as connection:
            return connection.execute(
                "SELECT code_sha256,state FROM web_invitations WHERE invitation_id=%s",
                (invitation_id,),
            ).fetchone()

    def test_convite_uso_unico_e_resgate_concorrente(self):
        issued = self._issue()
        def redeem_once(_):
            client = self._participant_client()
            try:
                return client.post("/api/v1/participant/redeem",
                                   json={"code": issued["code"]}).status_code
            finally:
                client.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(redeem_once, range(2)))
        self.assertEqual(sorted(statuses), [201, 409])
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM web_participant_sessions").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM web_session_main_order").fetchone()[0], 16)

    def test_expiracao_revogacao_e_autorizacao_negativa(self):
        denied = self.consulta.post(
            f"/api/v1/projects/{self.project_id}/invitations",
            json={"participant_id": "P_SINTETICO", "visit": "V1"},
        )
        self.assertEqual(denied.status_code, 403)
        missing = self.outsider.get("/api/v1/projects")
        self.assertEqual((missing.status_code, missing.json()["items"]), (200, []))
        cross_project = self.outsider.post(
            f"/api/v1/projects/{self.project_id}/invitations",
            json={"participant_id": "P_SINTETICO", "visit": "V1"},
        )
        self.assertEqual(cross_project.status_code, 404)

        expired_invitation = self._issue()
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "UPDATE web_invitations SET created_at=CURRENT_TIMESTAMP-INTERVAL '24 hours', expires_at=CURRENT_TIMESTAMP-INTERVAL '1 second' WHERE invitation_id=%s",
                (expired_invitation["invitation_id"],),
            )
        expired_redeem = self._participant_client()
        self.addCleanup(expired_redeem.close)
        response = expired_redeem.post(
            "/api/v1/participant/redeem", json={"code": expired_invitation["code"]}
        )
        self.assertEqual(response.status_code, 410)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute(
                "SELECT state FROM web_invitations WHERE invitation_id=%s",
                (expired_invitation["invitation_id"],),
            ).fetchone()[0], "expired")

        issued = self._issue()
        participant = self._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post("/api/v1/participant/redeem", json={"code": issued["code"]})
        session_id = redeemed.json()["session_id"]
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE web_participant_sessions SET activated_at=CURRENT_TIMESTAMP-INTERVAL '31 minutes',expires_at=CURRENT_TIMESTAMP-INTERVAL '1 minute' WHERE session_id=%s", (session_id,))
        expired = participant.get("/api/v1/participant/session")
        self.assertEqual(expired.status_code, 410)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute("SELECT state FROM web_participant_sessions WHERE session_id=%s", (session_id,)).fetchone()[0], "expired")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 0)

    def test_revogacao_de_vinculo_bloqueia_convite_e_sessao(self):
        issued = self._issue()
        self._set_member(self.admin, IMPORTER, active=False)
        participant = self._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post("/api/v1/participant/redeem", json={"code": issued["code"]})
        self.assertEqual(redeemed.status_code, 404)

    def test_revogar_convite_apos_resgate_invalida_credencial_participante(self):
        issued = self._issue()
        participant = self._participant_client()
        self.addCleanup(participant.close)
        redeemed = participant.post("/api/v1/participant/redeem", json={"code": issued["code"]})
        self.assertEqual(redeemed.status_code, 201)
        revoked = self.importer.post(
            f"/api/v1/projects/{self.project_id}/invitations/{issued['invitation_id']}/revoke",
            json={},
        )
        self.assertEqual(revoked.status_code, 204, revoked.text)
        self.assertEqual(participant.get("/api/v1/participant/session").status_code, 404)

    def test_rate_limit_de_resgate_tem_hmac_e_retry_after(self):
        self.app.state.config = replace(self.app.state.config, redeem_rate_limit=1)
        participant = self._participant_client()
        self.addCleanup(participant.close)
        first = participant.post("/api/v1/participant/redeem", json={"code": "X" * 43})
        second = participant.post("/api/v1/participant/redeem", json={"code": "Y" * 43})
        self.assertEqual(first.status_code, 404)
        self.assertEqual(second.status_code, 429)
        self.assertGreaterEqual(int(second.headers["retry-after"]), 1)
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT remote_sha256,request_count FROM web_participant_redeem_limits"
            ).fetchone()
        self.assertEqual(row[1], 2)
        self.assertEqual(len(row[0]), 64)
        self.assertNotIn("127.0.0.1", row[0])

    def test_paginas_tem_cursor_assinado_e_limitado_ao_escopo(self):
        response = self.admin.post("/api/v1/projects", json={
            "code": "SYNTHETIC_WEB_2", "name": "Segundo projeto sintetico",
        })
        self.assertEqual(response.status_code, 201, response.text)
        first = self.admin.get("/api/v1/projects?limit=1")
        self.assertEqual(first.status_code, 200)
        cursor = first.json()["next_cursor"]
        self.assertIsNotNone(cursor)
        second = self.admin.get("/api/v1/projects", params={"limit": 1, "cursor": cursor})
        self.assertEqual(second.status_code, 200)
        self.assertNotEqual(first.json()["items"][0]["id"], second.json()["items"][0]["id"])
        tampered = self.importer.get(
            "/api/v1/projects", params={"limit": 1, "cursor": cursor}
        )
        self.assertEqual(tampered.status_code, 422)
        invalid_limit = self.admin.get("/api/v1/projects?limit=101")
        self.assertEqual(invalid_limit.status_code, 422)

        members = self.admin.get(
            f"/api/v1/projects/{self.project_id}/members?limit=1"
        )
        self.assertEqual(members.status_code, 200)
        self.assertIsNotNone(members.json()["next_cursor"])


if __name__ == "__main__":
    unittest.main()
