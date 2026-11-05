"""Checkpoints e invalidacao em PostgreSQL real, apenas identidades sinteticas."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
import hashlib
import os
import time
import unittest
from unittest.mock import patch

import psycopg
from fastapi.testclient import TestClient

from stroop.domain.web_results import canonical_payload
from tests import test_web_sessions as sessions

# Reutilizar preparacao sintetica sem executar novamente os testes herdados.
Fixtures = type('Fixtures', (), {
    key: value for key, value in vars(sessions.WebSessionsPostgresTests).items()
    if key in {'setUp','setUpClass'} or key.startswith('_') and not key.startswith('__')
})


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'TEST_DATABASE_URL nao configurada')
class WebCheckpointPostgresTests(Fixtures, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.app.state.config=replace(self.app.state.config,read_database_url=self.database_url)

    def send(self, participant, payload, start=0, end=16):
        return participant.post('/api/v1/participant/session/checkpoints',
                                json={**payload, 'trials': payload['trials'][start:end]})

    def observed(self):
        with psycopg.connect(self.database_url) as connection:
            return connection.execute('SELECT count(*) FROM web_session_observations').fetchone()[0]

    def test_ack_prefix_hash_overlap_replay_and_lost_response(self):
        participant, payload, _ = self._completion()
        zero = participant.get('/api/v1/participant/session').json()['checkpoint']
        self.assertEqual(zero, {'confirmed_through':0,'prefix_hash':None,'received_at':None})
        first = self.send(participant,payload,0,3)
        self.assertEqual(first.status_code,200,first.text)
        expected = hashlib.sha256(canonical_payload({**payload,'trials':payload['trials'][:3]})).hexdigest()
        self.assertEqual(first.json()['prefix_hash'],expected)
        self.assertEqual(self.send(participant,payload,0,3).json(),first.json())
        # Consulta apos perder a resposta recupera exatamente o prefixo, sem tentativas.
        status = participant.get('/api/v1/participant/session').json()
        self.assertEqual(status['checkpoint'], {k:v for k,v in first.json().items() if k != 'session_id'})
        self.assertNotIn('trials',status)
        overlap = self.send(participant,payload,1,5)
        self.assertEqual(overlap.status_code,200,overlap.text)
        self.assertEqual(overlap.json()['confirmed_through'],5)
        self.assertEqual(self.observed(),5)
        self.assertEqual(self._counts(),(0,0,0,0,0))
        complete = participant.post('/api/v1/participant/complete',json=payload)
        self.assertEqual(complete.status_code,201,complete.text)
        self.assertEqual(self.observed(),16)
        self.assertEqual(self._counts(),(1,16,12,1,16))
        self.assertEqual(self.send(participant,payload,0,16).status_code,200)
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,200)

    def test_schema_units_versions_and_order_reject_without_writes(self):
        participant,payload,_ = self._completion()
        cases = []
        for field,value in [('participant_id','SINTETICO'),('platform','psychopy'),
                            ('frame_period_ms',True),('app_version','other'),('test_version','0.2.2')]:
            cases.append({**payload,field:value})
        for field,value in [('key_pressed','x'),('reaction_time_ms',False),('trial_start_ms',-1),
                            ('trial_number',True),('condition_id',0),('extra','SINTETICO')]:
            body=deepcopy(payload);body['trials'][0][field]=value;cases.append(body)
        cases.append({**payload,'trials':[]})
        for body in cases:
            with self.subTest(body=body):
                response=self.send(participant,body)
                self.assertIn(response.status_code,(409,422),response.text)
                self.assertEqual(self.observed(),0)
        self.assertEqual(self.send(participant,payload,1,3).status_code,409)
        self.assertEqual(self.observed(),0)

    def test_timing_failure_is_preserved_and_never_official(self):
        participant,payload,_=self._completion()
        payload['trials'][0]['stimulus_offset_ms']+=100
        response=self.send(participant,payload,0,1)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.observed(),1)
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,409)
        self.assertEqual(self._counts(),(0,0,0,0,0))
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT reason,source FROM web_session_invalidations').fetchone(),
                             ('timing_invalid','server'))

    def test_divergence_does_not_overwrite_and_invalidates_completed_result(self):
        participant,payload,issued=self._completion()
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,201)
        listed = self.importer.get(f'/api/v1/projects/{self.project_id}/assessments')
        aggregate = {'projects': [{'project_id': str(self.project_id),
                                  'snapshot': listed.headers['x-assessment-snapshot']}],
                     'filters': {}, 'view': {'test_code': 'stroop_go_nogo_ptbr'}}
        self.assertEqual(self.importer.post('/api/v1/assessments/export', json=aggregate).status_code, 200)
        changed=deepcopy(payload);changed['frame_period_ms']=17
        response=self.send(participant,changed,0,1)
        self.assertEqual((response.status_code,response.json()['error']['code']),(409,'result_conflict'))
        self.assertEqual(self.observed(),16)
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,409)
        project=self.project_id
        listed=self.importer.get(f'/api/v1/projects/{project}/assessments')
        self.assertEqual(listed.json()['items'],[])
        self.assertEqual(self.importer.post('/api/v1/assessments/export', json=aggregate).status_code, 409)
        self.assertEqual(self.importer.get(f'/api/v1/projects/{project}/assessments/options').json()['participant_id'], [])
        with psycopg.connect(self.database_url) as connection:
            receipt=connection.execute('SELECT receipt FROM web_assessments').fetchone()[0]
        detail=self.importer.get(f"/api/v1/projects/{project}/assessments/{receipt['assessment_id']}")
        self.assertFalse(detail.json()['valid_for_result'])
        self.assertIsNone(detail.json()['summary'])
        self.assertEqual(self.importer.get(f"/api/v1/projects/{project}/assessments/{receipt['assessment_id']}/export").status_code,404)
        self.assertEqual(self._counts(),(1,16,12,1,16))

    def test_rollback_before_ack_and_final_rollback_preserve_only_confirmed_prefix(self):
        participant,payload,_=self._completion()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("""CREATE FUNCTION synthetic_fail_checkpoint() RETURNS trigger LANGUAGE plpgsql
                AS $$ BEGIN RAISE EXCEPTION 'synthetic failure'; END $$""")
            connection.execute('''CREATE TRIGGER synthetic_checkpoint_failure BEFORE INSERT ON web_session_checkpoints
                FOR EACH ROW EXECUTE FUNCTION synthetic_fail_checkpoint()''')
        self.assertEqual(self.send(participant,payload,0,3).status_code,503)
        self.assertEqual(self.observed(),0)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('DROP TRIGGER synthetic_checkpoint_failure ON web_session_checkpoints')
        ack=self.send(participant,payload,0,3).json()
        with psycopg.connect(self.database_url) as connection:
            connection.execute('''CREATE TRIGGER synthetic_final_failure BEFORE INSERT ON web_trial_observations
                FOR EACH ROW EXECUTE FUNCTION synthetic_fail_checkpoint()''')
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,503)
        self.assertEqual(self.observed(),3)
        self.assertEqual(participant.get('/api/v1/participant/session').json()['checkpoint']['prefix_hash'],ack['prefix_hash'])
        self.assertEqual(self._counts(),(0,0,0,0,0))
        with psycopg.connect(self.database_url) as connection:
            connection.execute('DROP TRIGGER synthetic_final_failure ON web_trial_observations')
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,201)

    def test_abort_accepts_pending_prefix_without_reopening(self):
        participant,payload,_=self._completion()
        self.assertEqual(self.send(participant,payload,0,2).status_code,200)
        self.assertEqual(participant.post('/api/v1/participant/abort',json={'reason':'focus_lost'}).status_code,200)
        self.assertEqual(self.send(participant,payload,1,4).status_code,200)
        status=participant.get('/api/v1/participant/session').json()
        self.assertEqual((status['state'],status['can_resume'],status['checkpoint']['confirmed_through']),('aborted',False,4))
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,409)
        self.assertEqual(participant.post('/api/v1/participant/start',json={'app_version':payload['app_version']}).status_code,409)
        self.assertEqual(self._counts(),(0,0,0,0,0))

    def test_expiration_zero_partial_full_and_revocation_keep_observations(self):
        for count in (0,5,16):
            participant,payload,issued=self._completion()
            if count:
                self.assertEqual(self.send(participant,payload,0,count).status_code,200)
            before=self.observed()
            with psycopg.connect(self.database_url) as connection:
                connection.execute("""UPDATE web_participant_sessions SET activated_at=CURRENT_TIMESTAMP-interval '31 minutes',
                    expires_at=CURRENT_TIMESTAMP-interval '1 minute' WHERE session_id=%s""",(issued['session_id'],))
            self.assertEqual(self.send(participant,payload).status_code,410)
            self.assertEqual(participant.get('/api/v1/participant/session').status_code,410)
            self.assertEqual(self.observed(),before)
        participant,payload,issued=self._completion()
        self.send(participant,payload,0,2)
        revoked=self.importer.post(f"/api/v1/projects/{self.project_id}/invitations/{issued['invitation_id']}/revoke",json={})
        self.assertEqual(revoked.status_code,204)
        before=self.observed()
        self.assertEqual(self.send(participant,payload).status_code,404)
        self.assertEqual(self.observed(),before)
        self.assertEqual(self._counts(),(0,0,0,0,0))

    def test_invalidation_before_after_end_and_professional_after_expiry(self):
        participant,payload,issued=self._completion()
        receipt=participant.post('/api/v1/participant/complete',json=payload).json()
        url='/api/v1/participant/session/invalidate'
        self.assertTrue(participant.post(url,json={'reason':'focus_lost','event_at_ms':60001}).json()['valid_for_result'])
        result=participant.post(url,json={'reason':'visibility_hidden','event_at_ms':59999})
        self.assertEqual(result.status_code,200,result.text)
        self.assertFalse(result.json()['valid_for_result'])
        self.assertEqual(participant.post(url,json={'reason':'visibility_hidden','event_at_ms':59999}).json(),result.json())
        self.assertEqual(self._counts(),(1,16,12,1,16))
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT receipt FROM web_assessments').fetchone()[0],receipt)
            connection.execute("UPDATE web_participant_sessions SET expires_at=CURRENT_TIMESTAMP-interval '1 minute',activated_at=CURRENT_TIMESTAMP-interval '31 minutes'")
        self.assertEqual(participant.post(url,json={'reason':'reload','event_at_ms':None}).status_code,410)
        path=f"/api/v1/projects/{self.project_id}/sessions/{issued['session_id']}/invalidate"
        self.assertEqual(self.outsider.post(path,json={'reason':'reload','event_at_ms':None}).status_code,404)
        self.assertEqual(self.consulta.post(path,json={'reason':'reload','event_at_ms':None}).status_code,404)
        self.assertEqual(self.importer.post(path,json={'reason':'reload','event_at_ms':None}).status_code,200)

    def test_csrf_and_scope_protected(self):
        participant,payload,issued=self._completion()
        participant.headers.pop('X-CSRF-Token')
        for path,body in [('/api/v1/participant/session/checkpoints',payload),
                          ('/api/v1/participant/session/invalidate',{'reason':'reload','event_at_ms':None})]:
            self.assertEqual(participant.post(path,json=body).status_code,403)
        self.assertEqual(self.observed(),0)

    def test_concurrent_overlap_divergence_and_abort_complete(self):
        for pair in ('equal','divergent','abort','complete'):
            participant,payload,issued=self._completion()
            token=participant.cookies.get('__Host-stroop_participant')
            csrf=participant.headers['X-CSRF-Token']
            changed=deepcopy(payload)
            if pair=='divergent': changed['frame_period_ms']=17
            operations=[('/api/v1/participant/session/checkpoints',{**payload,'trials':payload['trials'][:4]})]
            operations.append(('/api/v1/participant/abort',{'reason':'focus_lost'}) if pair=='abort' else
                              ('/api/v1/participant/complete',payload) if pair=='complete' else
                              ('/api/v1/participant/session/checkpoints',{**changed,'trials':changed['trials'][:6]}))
            def send(operation):
                with TestClient(self.app,base_url=sessions.ORIGIN) as client:
                    client.cookies.set('__Host-stroop_participant',token)
                    return client.post(operation[0],json=operation[1],headers={'Origin':sessions.ORIGIN,'X-CSRF-Token':csrf})
            with ThreadPoolExecutor(max_workers=2) as pool:
                statuses=sorted(response.status_code for response in pool.map(send,operations))
            self.assertEqual(statuses,[200,409] if pair=='divergent' else [200,201] if pair=='complete' else [200,200],pair)
        # Corrida abort/complete pode preservar um resultado historico, mas abort nao
        # autoriza complete. Violacao tardia passa pela invalidacao explicita.

    def test_concurrent_invalidation_and_complete_never_leave_valid_result(self):
        participant,payload,issued=self._completion()
        token=participant.cookies.get('__Host-stroop_participant')
        csrf=participant.headers['X-CSRF-Token']
        operations=[('/api/v1/participant/complete',payload),
                    ('/api/v1/participant/session/invalidate',{'reason':'visibility_hidden','event_at_ms':59000})]
        def send(operation):
            with TestClient(self.app,base_url=sessions.ORIGIN) as client:
                client.cookies.set('__Host-stroop_participant',token)
                return client.post(operation[0],json=operation[1],headers={'Origin':sessions.ORIGIN,'X-CSRF-Token':csrf})
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses=list(pool.map(send,operations))
        self.assertEqual(responses[1].status_code,200,responses[1].text)
        self.assertIn(responses[0].status_code,(201,409),responses[0].text)
        self.assertEqual(self.importer.get(f'/api/v1/projects/{self.project_id}/assessments').json()['items'],[])
        self.assertEqual(participant.post('/api/v1/participant/complete',json=payload).status_code,409)

    def test_divergent_observation_and_continuity_failure(self):
        participant,payload,_=self._completion()
        self.send(participant,payload,0,3)
        changed=deepcopy(payload)
        trial=changed['trials'][0]
        trial.update(key_pressed='space',reaction_time_ms=620,key_at_ms=920)
        conflict=self.send(participant,changed,0,4)
        self.assertEqual(conflict.status_code,409,conflict.text)
        self.assertEqual(self.observed(),3)
        participant,payload,_=self._completion()
        self.send(participant,payload,0,2)
        payload['trials'][2]['trial_start_ms']+=1
        self.assertEqual(self.send(participant,payload,2,3).status_code,200)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM web_session_invalidations WHERE reason='timing_invalid'").fetchone()[0],1)

    def test_professional_status_partial_and_logical_expiration_no_fake_cause(self):
        participant,payload,issued=self._completion()
        self.send(participant,payload,0,3)
        path=f"/api/v1/projects/{self.project_id}/sessions/{issued['session_id']}"
        status=self.consulta.get(path)
        self.assertEqual(status.status_code,200,status.text)
        self.assertFalse(status.json()['valid_for_result'])
        self.assertEqual(status.json()['checkpoint']['confirmed_through'],3)
        self.assertNotIn('trials',status.json())
        self.assertEqual(self.outsider.get(path).status_code,404)
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE web_participant_sessions SET activated_at=CURRENT_TIMESTAMP-interval '31 minutes',expires_at=CURRENT_TIMESTAMP-interval '1 minute'")
        status=self.consulta.get(path).json()
        self.assertEqual(status['state'],'expired')
        self.assertIsNone(status['abort_reason'])
        self.assertIsNone(status['invalidation'])
        self.assertFalse(status['complete'])
        self.assertEqual(status['checkpoint']['confirmed_through'],3)

    def test_unrepresentable_numbers_fail_closed(self):
        participant,payload,_=self._completion()
        payload['trials'][0].update(key_pressed='space',reaction_time_ms=10**400,key_at_ms=812)
        self.assertEqual(self.send(participant,payload,0,1).status_code,422)
        self.assertEqual(participant.post('/api/v1/participant/session/invalidate',json={'reason':'reload','event_at_ms':10**400}).status_code,422)
        self.assertEqual(self.observed(),0)

    def test_deadline_during_writes_rolls_back_without_ack_or_official_result(self):
        for target in ('web_session_checkpoints', 'web_trial_observations'):
            with self.subTest(target=target):
                participant, payload, issued = self._completion()
                self.assertEqual(self.send(participant, payload, 0, 2).status_code, 200)
                before = self.observed()
                with psycopg.connect(self.database_url) as connection:
                    connection.execute("""CREATE OR REPLACE FUNCTION synthetic_slow_write()
                        RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
                        PERFORM pg_sleep(1); RETURN NEW; END $$""")
                    connection.execute(f'''CREATE TRIGGER synthetic_deadline BEFORE INSERT OR UPDATE
                        ON {target} FOR EACH ROW EXECUTE FUNCTION synthetic_slow_write()''')
                    connection.execute("""UPDATE web_participant_sessions
                        SET activated_at=statement_timestamp()-interval '29 minutes 59.5 seconds',
                            expires_at=statement_timestamp()+interval '0.5 seconds'
                        WHERE session_id=%s""", (issued['session_id'],))
                began = time.monotonic()
                response = (self.send(participant, payload, 2, 3) if target == 'web_session_checkpoints'
                            else participant.post('/api/v1/participant/complete', json=payload))
                self.assertGreaterEqual(time.monotonic() - began, 1)
                self.assertEqual(response.status_code, 410, response.text)
                self.assertEqual(self.observed(), before)
                self.assertEqual(self._counts(), (0, 0, 0, 0, 0))
                with psycopg.connect(self.database_url) as connection:
                    self.assertEqual(connection.execute(
                        'SELECT confirmed_through FROM web_session_checkpoints WHERE session_id=%s',
                        (issued['session_id'],)).fetchone()[0], 2)
                    connection.execute(f'DROP TRIGGER synthetic_deadline ON {target}')

    def test_checkpoint_transport_preserves_all_official_metrics_and_units(self):
        from stroop.domain.web_results import validate_result
        from tests.test_web_results import add_response, synthetic_conditions
        participant, payload, _ = self._completion()
        # Respostas fracionarias preservam a precisao ao atravessar checkpoints.
        for index, rt in ((0, 681), (1, 512.123456789), (3, 731.123456789)):
            add_response(payload['trials'][index], rt)
        expected = validate_result(payload, tuple(t['condition_id'] for t in payload['trials']),
                                   payload['app_version'], synthetic_conditions())
        self.assertEqual(self.send(participant, payload, 0, 4).status_code, 200)
        response = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()['summary'], expected['summary'])
        with psycopg.connect(self.database_url) as connection:
            stored = connection.execute('SELECT metric_code,metric_value,unit FROM assessment_metrics').fetchall()
        self.assertEqual({code: (value, unit) for code, value, unit in stored},
                         {m['metric_code']: (m['metric_value'], m['unit']) for m in expected['metrics']})

    def test_abort_complete_race_preserves_atomic_official_or_incomplete_state(self):
        participant, payload, issued = self._completion()
        self.assertEqual(self.send(participant, payload, 0, 3).status_code, 200)
        token = participant.cookies.get('__Host-stroop_participant')
        csrf = participant.headers['X-CSRF-Token']
        def send(operation):
            with TestClient(self.app, base_url=sessions.ORIGIN) as client:
                client.cookies.set('__Host-stroop_participant', token)
                return client.post(operation[0], json=operation[1],
                                   headers={'Origin': sessions.ORIGIN, 'X-CSRF-Token': csrf})
        with ThreadPoolExecutor(max_workers=2) as pool:
            complete, abort = list(pool.map(send, [('/api/v1/participant/complete', payload),
                ('/api/v1/participant/abort', {'reason': 'focus_lost'})]))
        if complete.status_code == 201:
            self.assertEqual(abort.status_code, 409, abort.text)
            self.assertEqual(self._counts(), (1, 16, 12, 1, 16))
        else:
            self.assertEqual(complete.status_code, 409, complete.text)
            self.assertEqual(abort.status_code, 200, abort.text)
            self.assertEqual(self._counts(), (0, 0, 0, 0, 0))
            self.assertEqual(self.observed(), 3)
