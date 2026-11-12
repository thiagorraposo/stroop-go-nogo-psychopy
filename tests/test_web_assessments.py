"""Consultas reais com papel SELECT, escopo e coletas inequivocamente sinteticas."""
from dataclasses import replace
import csv
import io
import os
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import psycopg
from psycopg import sql
from fastapi.testclient import TestClient

from api.config import APIConfig, ConfigurationError
from stroop.application.import_postgres import import_csv
from stroop.persistence import web_assessments as persistence
from tests import test_web_sessions as helpers

ROOT = Path(__file__).resolve().parents[1]
READER = 'synthetic_w14_reader'


class ReadConfigTests(unittest.TestCase):
    def test_config_leitura_nao_usa_fallback_e_valida_uri_sem_expor_valores(self):
        values = {'APP_ENV': 'test', 'API_DATABASE_URL': 'postgresql://synthetic@127.0.0.1/synthetic',
                  'API_PUBLIC_ORIGIN': helpers.ORIGIN, 'OIDC_CLIENT_ID': 'synthetic-client-id',
                  'OIDC_CLIENT_SECRET': 'synthetic-client-secret-never-use',
                  'API_SESSION_SECRET': 'synthetic-session-secret-never-use-0000000000'}
        self.assertEqual(APIConfig.from_env(values).read_database_url, '')
        uri = 'postgresql://synthetic_reader:synthetic-only@127.0.0.1/synthetic'
        config = APIConfig.from_env({**values, 'API_READ_DATABASE_URL': uri})
        self.assertEqual(config.read_database_url, uri)
        self.assertNotIn('synthetic-only', repr(config))
        for invalid in ('sqlite:///local.db', 'postgresql:///missing_host', 'postgresql://host/', 'bad secret'):
            with self.subTest(value=invalid), self.assertRaises(ConfigurationError) as error:
                APIConfig.from_env({**values, 'API_READ_DATABASE_URL': invalid})
            self.assertNotIn(invalid, str(error.exception))


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'TEST_DATABASE_URL nao configurada')
class WebAssessmentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = os.environ['TEST_DATABASE_URL']
        if not psycopg.conninfo.conninfo_to_dict(cls.database_url).get('dbname', '').startswith('stroop_etapa4_test'):
            raise RuntimeError('Banco descartavel obrigatorio')
        with psycopg.connect(cls.database_url, autocommit=True) as connection:
            if not connection.execute('SELECT 1 FROM pg_roles WHERE rolname=%s', (READER,)).fetchone():
                connection.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(
                    sql.Identifier(READER), sql.Literal('synthetic-read-only')))
        uri = urlsplit(cls.database_url)
        cls.read_url = urlunsplit((uri.scheme,
            f'{READER}:synthetic-read-only@{uri.hostname}:{uri.port}', uri.path, uri.query, ''))

    def setUp(self):
        self.h = helpers.WebSessionsPostgresTests()
        self.h.database_url = self.database_url
        self.addCleanup(self.h.doCleanups)
        self.h.setUp()
        with psycopg.connect(self.database_url) as connection:
            connection.execute(sql.SQL('GRANT USAGE ON SCHEMA public TO {}').format(sql.Identifier(READER)))
            for table, columns in persistence.REQUIRED_COLUMNS.items():
                connection.execute(sql.SQL('GRANT SELECT ({}) ON {} TO {}').format(
                    sql.SQL(',').join(map(sql.Identifier, sorted(columns))),
                    sql.Identifier(table), sql.Identifier(READER)))
        self.h.app.state.config = replace(self.h.app.state.config, read_database_url=self.read_url)
        self.path = f'/api/v1/projects/{self.h.project_id}/assessments'

    def complete(self, **kwargs):
        participant, payload, issued = self.h._completion(**kwargs)
        response = participant.post('/api/v1/participant/complete', json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json(), participant

    def legacy(self):
        with (ROOT / 'tests/fixtures/csv/valido_minimo.csv').open() as source:
            rows = list(csv.DictReader(source))
        assessment_id = str(uuid4())
        for row in rows:
            row.update(project='SYNTHETIC_WEB', assessment_id=assessment_id,
                       participant_name='NOME_SINTETICO_RESTRITO', initials='SR',
                       evaluator='AVALIADOR_SINTETICO_RESTRITO')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic_legacy.csv'
            with path.open('w', newline='') as output:
                writer = csv.DictWriter(output, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            import_csv(path, self.database_url)
        return assessment_id

    def link_legacy(self, active=True):
        with psycopg.connect(self.database_url) as connection:
            connection.execute('''INSERT INTO web_legacy_project_links(legacy_project,project_id,active)
                VALUES ('SYNTHETIC_WEB',%s,%s) ON CONFLICT(legacy_project)
                DO UPDATE SET active=EXCLUDED.active''', (self.h.project_id, active))

    def test_lista_detalhe_exportacao_reais_com_credencial_select(self):
        receipt, participant = self.complete()
        for client in (self.h.admin, self.h.importer, self.h.consulta):
            response = client.get(self.path)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(len(response.json()['items']), 1)
            item = response.json()['items'][0]
            self.assertEqual({key: item['summary'][key] for key in receipt['summary']}, receipt['summary'])
            self.assertEqual(item['summary']['total_go_trials'], 8)
            self.assertEqual(item['summary']['total_no_go_trials'], 8)
            self.assertEqual(item['summary']['accuracy_go_trials'], 100 * receipt['summary']['hits'] / 8)
            self.assertEqual(item['summary']['accuracy_no_go_trials'], 100 * receipt['summary']['correct_rejections'] / 8)
            self.assertEqual(item['platform'], 'web')
            self.assertNotIn('participant_name', response.text)
            detail = client.get(self.path + '/' + receipt['assessment_id'])
            self.assertEqual(detail.status_code, 200, detail.text)
            self.assertEqual(len(detail.json()['trials']), 16)
            self.assertEqual(len(detail.json()['metrics']), 12)
            exported = client.get(self.path + '/' + receipt['assessment_id'] + '/export')
            self.assertEqual(exported.status_code, 200, exported.text)
            self.assertEqual(exported.headers['cache-control'], 'no-store')
            self.assertIn('text/csv', exported.headers['content-type'])
            rows = list(csv.DictReader(io.StringIO(exported.text)))
            self.assertEqual(len(rows), 16)
            self.assertEqual(rows[0]['participant_name'], 'NAO_COLETADO')
            self.assertEqual(rows[0]['initials'], '')
            self.assertNotIn('P_SINTETICO', exported.headers['content-disposition'])
        self.assertEqual(participant.get(self.path).status_code, 401)
        with psycopg.connect(self.read_url) as connection:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                connection.execute("UPDATE web_projects SET active=false")
        with psycopg.connect(self.read_url) as connection:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                connection.execute('SELECT participant_name,initials FROM assessments')
        with persistence._connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SHOW transaction_read_only').fetchone()['transaction_read_only'], 'on')
            with self.assertRaises(psycopg.errors.ReadOnlySqlTransaction):
                connection.execute("UPDATE web_projects SET active=false")

    def test_legado_nao_e_associado_por_codigo_mapa_explicito_mascara_e_revoga(self):
        legacy_id = self.legacy()
        self.assertEqual(self.h.consulta.get(self.path).json()['items'], [])
        self.assertEqual(self.h.consulta.get(f'{self.path}/{legacy_id}').status_code, 404)
        self.link_legacy()
        listed = self.h.consulta.get(self.path)
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(listed.json()['items'][0]['platform'], 'psychopy')
        detail = self.h.consulta.get(f'{self.path}/{legacy_id}')
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertIsNone(detail.json()['protocol_id'])
        self.assertIsNone(detail.json()['frame_period_ms'])
        self.assertTrue(all(row['trial_start_ms'] is None for row in detail.json()['trials']))
        exported = self.h.consulta.get(f'{self.path}/{legacy_id}/export')
        self.assertEqual(exported.status_code, 200, exported.text)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(exported.text)))), 4)
        self.assertIn('LEGADO_NAO_MAPEADO', exported.text)
        for response in (listed, detail, exported):
            for restricted in ('NOME_SINTETICO_RESTRITO', 'AVALIADOR_SINTETICO_RESTRITO'):
                self.assertNotIn(restricted, response.text)
        self.link_legacy(False)
        self.assertEqual(self.h.consulta.get(f'{self.path}/{legacy_id}/export').status_code, 404)

    def test_rotulo_legado_longo_preservado_sem_impor_novo_limite_ao_csv_antigo(self):
        legacy_id = self.legacy()
        label = 'PROJETO_SINTETICO_' + 'X' * 240
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE assessments SET project=%s WHERE assessment_id=%s', (label, legacy_id))
            connection.execute('INSERT INTO web_legacy_project_links(legacy_project,project_id) VALUES (%s,%s)',
                               (label, self.h.project_id))
        response = self.h.consulta.get(self.path + '/' + legacy_id)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn(label, response.text)

    def test_escopo_revalidado_admin_sem_vinculo_e_acesso_cruzado_recebem404(self):
        receipt, _ = self.complete()
        for suffix in ('', '/' + receipt['assessment_id'], '/' + receipt['assessment_id'] + '/export'):
            self.assertEqual(self.h.outsider.get(self.path + suffix).status_code, 404)
        self.h._set_member(self.h.admin, helpers.ADMIN, False)
        self.assertEqual(self.h.admin.get(self.path).status_code, 404)
        self.h._set_member(self.h.admin, helpers.CONSULTA, False)
        self.assertEqual(self.h.consulta.get(self.path + '/' + receipt['assessment_id'] + '/export').status_code, 404)
        self.assertEqual(self.h.importer.get(f'/api/v1/projects/{uuid4()}/assessments').status_code, 404)

    def test_paginacao_assinada_vinculada_a_usuario_projeto_e_filtros(self):
        first, _ = self.complete()
        second, _ = self.complete()
        response = self.h.consulta.get(self.path + '?limit=1')
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(len(body['items']), 1)
        cursor = body['next_cursor']
        self.assertTrue(cursor)
        next_page = self.h.consulta.get(self.path, params={'limit': 1, 'cursor': cursor})
        self.assertEqual(next_page.status_code, 200, next_page.text)
        self.assertNotEqual(body['items'][0]['assessment_id'], next_page.json()['items'][0]['assessment_id'])
        self.assertIsNone(next_page.json()['next_cursor'])
        self.assertEqual(self.h.importer.get(self.path, params={'cursor': cursor}).status_code, 422)
        self.assertEqual(self.h.consulta.get(
            f'/api/v1/projects/{uuid4()}/assessments', params={'cursor': cursor}).status_code, 422)
        self.assertEqual(self.h.consulta.get(self.path, params={'cursor': cursor, 'visit': 'OTHER_SYNTHETIC'}).status_code, 422)
        self.assertEqual(self.h.consulta.get(self.path + '?participant_id=NOT_FOUND').json()['items'], [])
        self.assertEqual(len(self.h.consulta.get(self.path + '?visit=V_SINTETICA').json()['items']), 2)

    def test_metricas_stroop_recalculadas_e_ausencia_de_hits_no_http(self):
        receipt, _ = self.complete(no_responses=True)
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessment_metrics SET metric_value=1 WHERE metric_code='accuracy'")
            connection.execute("UPDATE trial_results SET correct=0,error_type='commission'")
        listed = self.h.consulta.get(self.path)
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual({key: listed.json()['items'][0]['summary'][key] for key in receipt['summary']}, receipt['summary'])
        self.assertEqual(listed.json()['items'][0]['summary']['accuracy_go_trials'], 0)
        self.assertEqual(listed.json()['items'][0]['summary']['accuracy_no_go_trials'], 100)
        detail = self.h.consulta.get(self.path + '/' + receipt['assessment_id'])
        self.assertEqual(detail.status_code, 200, detail.text)
        metrics = {metric['metric_code']: metric['metric_value'] for metric in detail.json()['metrics']}
        self.assertEqual(metrics['accuracy'], 50)
        self.assertIsNone(metrics['response_time'])
        self.assertEqual(sum(row['correct'] for row in detail.json()['trials']), 8)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute(
                "SELECT metric_value FROM assessment_metrics WHERE metric_code='accuracy'").fetchone()[0], 1)

    def _assert_condition_absence(self, absent):
        assessment_id = self.legacy()
        self.link_legacy()
        with psycopg.connect(self.database_url) as connection:
            connection.execute('DELETE FROM trial_results WHERE assessment_id=%s AND condition=%s', (assessment_id, absent))
            if absent == 'congruent':
                connection.execute('UPDATE trial_results SET trial_number=trial_number-2 WHERE assessment_id=%s', (assessment_id,))
        listed = self.h.consulta.get(self.path)
        self.assertEqual(listed.status_code, 200, listed.text)
        summary = listed.json()['items'][0]['summary']
        detail_response = self.h.consulta.get(self.path + '/' + assessment_id)
        self.assertEqual(detail_response.status_code, 200, detail_response.text)
        self.assertEqual(summary, detail_response.json()['summary'])
        detail_metrics = {metric['metric_code']: metric['metric_value'] for metric in detail_response.json()['metrics']}
        missing = 'go' if absent == 'congruent' else 'no_go'
        present = 'no_go' if absent == 'congruent' else 'go'
        self.assertEqual(summary[f'total_{missing}_trials'], 0)
        self.assertIsNone(summary[f'accuracy_{missing}_trials'])
        self.assertIsNone(detail_metrics[f'accuracy_{missing}_trials'])
        self.assertEqual(summary[f'total_{present}_trials'], 2)
        self.assertEqual(summary[f'accuracy_{present}_trials'], 50)
        self.assertEqual(summary['total_trials'], 2)
        if absent == 'congruent':
            self.assertIsNone(summary['response_time_seconds'])
            self.assertIsNone(detail_metrics['omission_errors_percentage'])

    def test_w15b_sem_tentativas_go_e_ausencia_nao_zero(self):
        self._assert_condition_absence('congruent')

    def test_w15c_exportacao_agregada_revalida_snapshot_metadados_e_permissao(self):
        receipt, _ = self.complete()
        listed = self.h.consulta.get(self.path, params={'limit': 1})
        self.assertEqual(listed.status_code, 200, listed.text)
        snapshot = listed.headers.get('x-assessment-snapshot')
        self.assertTrue(snapshot)
        self.assertNotIn('=', snapshot)
        body = {'projects': [{'project_id': str(self.h.project_id), 'snapshot': snapshot}],
                'filters': {}, 'view': {'test_code': 'stroop_go_nogo_ptbr'}}
        exported = self.h.consulta.post('/api/v1/assessments/export', json=body)
        self.assertEqual(exported.status_code, 200, exported.text)
        self.assertEqual(exported.headers['cache-control'], 'no-store')
        self.assertEqual(exported.headers['content-disposition'],
                         'attachment; filename="stroop_go_nogo_ptbr_avaliacoes.csv"')
        rows = list(csv.DictReader(io.StringIO(exported.text)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['assessment_id'], receipt['assessment_id'])
        self.assertIn('accuracy_go_trials_percent', rows[0])
        self.assertNotIn('participant_name', rows[0])
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessments SET visit='V_SINTETICA_ALTERADA'")
        changed = self.h.consulta.post('/api/v1/assessments/export', json=body)
        self.assertEqual(changed.status_code, 409, changed.text)
        self.assertEqual(changed.json()['error']['code'], 'state_conflict')
        self.h._set_member(self.h.admin, helpers.CONSULTA, False)
        self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json=body).status_code, 404)
        malformed = {**body, 'extra': 'SINTETICO'}
        self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json=malformed).status_code, 422)

    def test_w15b_sem_tentativas_nogo_e_ausencia_nao_zero(self):
        self._assert_condition_absence('incongruent')

    def test_w15b_summary_profissional_recalculado_e_recibo_preservado(self):
        receipt, participant = self.complete()
        original_keys = {'accuracy', 'response_time_seconds', 'total_trials', 'hits',
                         'omission_errors', 'commission_errors', 'correct_rejections'}
        self.assertEqual(set(receipt['summary']), original_keys)
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessment_metrics SET metric_value=1 WHERE metric_code IN ('accuracy_go_trials','accuracy_no_go_trials','total_go_trials','total_no_go_trials')")
        listed = self.h.consulta.get(self.path).json()['items'][0]['summary']
        detail = self.h.consulta.get(self.path + '/' + receipt['assessment_id']).json()
        metrics = {metric['metric_code']: metric['metric_value'] for metric in detail['metrics']}
        self.assertEqual(set(listed), original_keys | {'accuracy_go_trials', 'accuracy_no_go_trials', 'total_go_trials', 'total_no_go_trials'})
        self.assertEqual(detail['summary'], listed)
        for key in ('accuracy_go_trials', 'accuracy_no_go_trials', 'total_go_trials', 'total_no_go_trials'):
            self.assertEqual(listed[key], metrics[key])
        recovered = participant.get('/api/v1/participant/session').json()
        self.assertEqual(recovered.pop('checkpoint')['confirmed_through'],16)
        self.assertEqual(recovered, receipt)
        self.assertEqual(set(recovered['summary']), original_keys)

    def test_schema_incompleto_falha_fechado_sem_sql_e_projeto_inativo_e404(self):
        receipt, _ = self.complete()
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE web_projects SET active=false')
        self.assertEqual(self.h.consulta.get(self.path).status_code, 404)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE web_projects SET active=true')
            connection.execute('DROP TABLE web_legacy_project_links')
        response = self.h.consulta.get(self.path)
        self.assertEqual(response.status_code, 503, response.text)
        self.assertNotIn('web_legacy_project_links', response.text)
        self.assertNotIn('SELECT', response.text)

    def test_id_de_avaliacao_nao_cruza_outro_projeto_mesmo_com_ambos_vinculos(self):
        receipt, _ = self.complete()
        response = self.h.admin.post('/api/v1/projects', json={
            'code': 'SECOND_SYNTHETIC', 'name': 'Outro projeto sintetico'})
        self.assertEqual(response.status_code, 201, response.text)
        project = response.json()['id']
        user_id = helpers.opaque_user_id(helpers.ISSUER, helpers.CONSULTA)
        self.assertEqual(self.h.admin.put(f'/api/v1/projects/{project}/members/{user_id}',
                                         json={'active': True}).status_code, 200)
        other = f'/api/v1/projects/{project}/assessments'
        self.assertEqual(self.h.consulta.get(other).json()['items'], [])
        for suffix in ('', '/export'):
            self.assertEqual(self.h.consulta.get(other + '/' + receipt['assessment_id'] + suffix).status_code, 404)

    def test_instrumento_generico_preserva_metricas_sem_fabricar_tentativas_stroop(self):
        assessment_id = self.legacy()
        self.link_legacy()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessments SET test_code='synthetic_demo' WHERE assessment_id=%s", (assessment_id,))
            connection.execute('DELETE FROM trial_results WHERE assessment_id=%s', (assessment_id,))
            connection.execute('DELETE FROM assessment_metrics WHERE assessment_id=%s', (assessment_id,))
            for code, value, unit in (('synthetic_value', 42, 'count'), ('response_time', 0.75, 'seconds')):
                connection.execute('''INSERT INTO assessment_metrics
                    (assessment_id,metric_code,metric_label,metric_value,unit,calculated_at)
                    VALUES (%s,%s,'Metrica sintetica',%s,%s,CURRENT_TIMESTAMP::text)''',
                    (assessment_id, code, value, unit))
        listed = self.h.consulta.get(self.path)
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(listed.json()['items'][0]['summary']['metrics'],
                         {'synthetic_value': 42, 'response_time': 0.75})
        detail = self.h.consulta.get(self.path + '/' + assessment_id)
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertEqual(detail.json()['trials'], [])
        values = {metric['metric_code']: metric['metric_value'] for metric in detail.json()['metrics']}
        self.assertEqual(values['response_time'], 0.75)
        self.assertEqual(self.h.consulta.get(self.path + '/' + assessment_id + '/export').status_code, 422)

    def test_bloqueio_e_expiracao_profissional_sao_revalidados_na_consulta(self):
        receipt, _ = self.complete()
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE app_users SET active=false WHERE subject=%s', (helpers.CONSULTA,))
        self.assertEqual(self.h.consulta.get(self.path).status_code, 403)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE app_users SET active=true WHERE subject=%s', (helpers.CONSULTA,))
        client = self.h._client(helpers.CONSULTA)
        self.addCleanup(client.close)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('''UPDATE web_professional_sessions
                SET created_at=CURRENT_TIMESTAMP-INTERVAL '1 hour',
                    expires_at=CURRENT_TIMESTAMP-INTERVAL '1 second' WHERE subject=%s''', (helpers.CONSULTA,))
        self.assertEqual(client.get(self.path + '/' + receipt['assessment_id'] + '/export').status_code, 401)

    def test_w15a_filtros_combinados_opcoes_e_periodo_inclusivo(self):
        receipt, _ = self.complete()
        legacy = self.legacy()
        self.link_legacy()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessments SET assessment_date='2026-01-01' WHERE assessment_id=%s", (receipt['assessment_id'],))
            connection.execute("UPDATE assessments SET assessment_date='2026-01-02',participant_id='P SINTETICO HISTORICO',visit='V HISTORICA' WHERE assessment_id=%s", (legacy,))
        all_items = self.h.consulta.get(self.path).json()['items']
        web = next(item for item in all_items if item['platform'] == 'web')
        params = [('start_date', '2026-01-01'), ('end_date', '2026-01-01'),
                  ('participant_id', web['participant_id']), ('participant_id', 'OUTRO_SINTETICO'),
                  ('visit', web['visit']), ('platform', 'web'), ('platform', 'psychopy'),
                  ('evaluator_id', web['evaluator_id']), ('test_version', web['test_version']),
                  ('test_code', web['test_code'])]
        response = self.h.consulta.get(self.path, params=params)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([item['assessment_id'] for item in response.json()['items']], [receipt['assessment_id']])
        legacy_response = self.h.consulta.get(self.path, params={'participant_id': 'P SINTETICO HISTORICO',
            'visit': 'V HISTORICA', 'evaluator_id': 'LEGADO_NAO_MAPEADO', 'start_date': '2026-01-02', 'end_date': '2026-01-02'})
        self.assertEqual([item['assessment_id'] for item in legacy_response.json()['items']], [legacy])
        options = self.h.consulta.get(self.path + '/options')
        self.assertEqual(options.status_code, 200, options.text)
        self.assertEqual(set(options.json()), {'participant_id', 'visit', 'evaluator_id', 'test_version', 'platform', 'test_code'})
        self.assertIn('LEGADO_NAO_MAPEADO', options.json()['evaluator_id'])
        self.assertNotIn('AVALIADOR_SINTETICO_RESTRITO', options.text)
        narrowed = self.h.consulta.get(self.path + '/options', params={'start_date': '2026-01-01', 'end_date': '2026-01-01'})
        self.assertEqual(narrowed.json()['platform'], ['web'])
        self.assertEqual(self.h.outsider.get(self.path + '/options').status_code, 404)
        self.h._set_member(self.h.admin, helpers.CONSULTA, False)
        self.assertEqual(self.h.consulta.get(self.path + '/options').status_code, 404)

    def test_w15a_cursor_canonico_rejeita_concorrencia(self):
        self.complete()
        self.legacy()
        self.link_legacy()
        params = [('limit', '1'), ('platform', 'web'), ('platform', 'psychopy')]
        first = self.h.consulta.get(self.path, params=params).json()
        cursor = first['next_cursor']
        self.assertTrue(cursor)
        reordered = [('cursor', cursor), ('platform', 'psychopy'), ('platform', 'web')]
        self.assertEqual(self.h.consulta.get(self.path, params=reordered).status_code, 200)
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessments SET visit='V_SINTETICA_ALTERADA'")
        conflict = self.h.consulta.get(self.path, params=reordered)
        self.assertEqual(conflict.status_code, 409, conflict.text)
        self.assertEqual(conflict.json()['error']['code'], 'state_conflict')

    def test_query7_multisselecao_instrumentos_cursor_snapshot_csv_e_revogacao(self):
        receipt, _ = self.complete()
        legacy = self.legacy()
        self.link_legacy()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE assessments SET test_code='instrumento_sintetico_demo' WHERE assessment_id=%s", (legacy,))
        stroop = 'stroop_go_nogo_ptbr'
        demo = 'instrumento_sintetico_demo'
        params = [('test_code', stroop), ('test_code', demo), ('limit', '1')]
        first = self.h.consulta.get(self.path, params=params)
        self.assertEqual(first.status_code, 200, first.text)
        cursor = first.json()['next_cursor']
        self.assertTrue(cursor)
        reordered = [('test_code', demo), ('test_code', stroop), ('cursor', cursor)]
        second = self.h.consulta.get(self.path, params=reordered)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual({item['assessment_id'] for item in first.json()['items'] + second.json()['items']},
                         {legacy, receipt['assessment_id']})
        # A cursor cannot be reused for a different instrument selection.
        self.assertEqual(self.h.consulta.get(self.path, params={'test_code': stroop, 'cursor': cursor}).status_code, 422)
        body = {'projects': [{'project_id': str(self.h.project_id),
                              'snapshot': first.headers['x-assessment-snapshot']}],
                'filters': {'test_code': [demo, stroop]}, 'view': {'test_code': stroop}}
        headers = {'X-CSRF-Token': self.h.consulta.headers['X-CSRF-Token']}
        exported = self.h.consulta.post('/api/v1/assessments/export', json=body, headers=headers)
        self.assertEqual(exported.status_code, 200, exported.text)
        exported_rows = list(csv.DictReader(io.StringIO(exported.text)))
        self.assertEqual([item['assessment_id'] for item in exported_rows], [receipt['assessment_id']])
        body['filters'] = {'test_code': [stroop]}
        self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json=body, headers=headers).status_code, 422)
        # The old single-string client and the new single-item list share scope.
        single = self.h.consulta.get(self.path, params={'test_code': stroop})
        body['projects'][0]['snapshot'] = single.headers['x-assessment-snapshot']
        for value in (stroop, [stroop]):
            body['filters'] = {'test_code': value}
            self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json=body, headers=headers).status_code, 200)
        self.h._set_member(self.h.admin, helpers.CONSULTA, False)
        self.assertEqual(self.h.consulta.get(self.path, params=params).status_code, 404)
        self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json=body, headers=headers).status_code, 404)

    def test_query7_condition_response_same_main_trial_and_full_metrics(self):
        receipt, _ = self.complete()
        self.legacy()
        self.link_legacy()
        baseline = {item['assessment_id']: item['summary'] for item in self.h.consulta.get(self.path).json()['items']}
        scoped = [('test_code', 'stroop_go_nogo_ptbr')]
        for condition in ('congruent', 'incongruent'):
            for response in ('hit', 'omission', 'commission', 'correct_rejection'):
                with self.subTest(condition=condition, response=response):
                    # Expected membership comes from the canonical detail, not stored
                    # correctness/error_type or an independent EXISTS per dimension.
                    expected = set()
                    for assessment_id in baseline:
                        detail = self.h.consulta.get(self.path + '/' + assessment_id).json()
                        if any(trial['condition'] == condition and trial['error_type'] == response
                               for trial in detail['trials']):
                            expected.add(assessment_id)
                    result = self.h.consulta.get(self.path, params=[*scoped,
                        ('condition', condition), ('response_type', response)])
                    self.assertEqual(result.status_code, 200, result.text)
                    self.assertEqual({item['assessment_id'] for item in result.json()['items']}, expected)
                    for item in result.json()['items']:
                        self.assertEqual(item['summary'], baseline[item['assessment_id']])
        # Congruent trials and commissions coexist in both fixtures, but never
        # on the same trial. A conjunction of separate EXISTS would leak them.
        incompatible = self.h.consulta.get(self.path, params=[*scoped,
            ('condition', 'congruent'), ('response_type', 'commission')])
        self.assertEqual(incompatible.json()['items'], [])
        # OR within each dimension, main-only, and domain rules rather than the
        # denormalized error flag. Main trial metrics stay unchanged.
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE trial_results SET error_type='omission',correct=0 WHERE assessment_id=%s",
                               (receipt['assessment_id'],))
        params = [*scoped, ('condition', 'incongruent'), ('condition', 'congruent'),
                  ('response_type', 'hit'), ('response_type', 'omission'), ('limit', '1')]
        first = self.h.consulta.get(self.path, params=params)
        self.assertEqual(first.status_code, 200, first.text)
        cursor = first.json()['next_cursor']
        self.assertTrue(cursor)
        reordered = [*scoped, ('condition', 'congruent'), ('condition', 'incongruent'),
                     ('response_type', 'omission'), ('response_type', 'hit'), ('cursor', cursor)]
        second = self.h.consulta.get(self.path, params=reordered)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(len(first.json()['items'] + second.json()['items']), 2)
        changed = [*scoped, ('response_type', 'commission'), ('cursor', cursor)]
        self.assertEqual(self.h.consulta.get(self.path, params=changed).status_code, 422)
        # Late source mutation expires an unchanged query, even with equal count.
        with psycopg.connect(self.database_url) as connection:
            connection.execute("UPDATE trial_results SET reaction_time=reaction_time+0.001 WHERE assessment_id=%s AND reaction_time IS NOT NULL",
                               (receipt['assessment_id'],))
        self.assertEqual(self.h.consulta.get(self.path, params=reordered).status_code, 409)
        body = {'projects': [{'project_id': str(self.h.project_id), 'snapshot': first.headers['x-assessment-snapshot']}],
                'filters': {'test_code': ['stroop_go_nogo_ptbr'], 'condition': ['congruent']},
                'view': {'test_code': 'stroop_go_nogo_ptbr'}}
        self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json=body).status_code, 422)
        self.h._set_member(self.h.admin, helpers.CONSULTA, False)
        self.assertEqual(self.h.consulta.get(self.path, params=params).status_code, 404)

    def test_query7_trial_filter_excludes_practice_only_matches(self):
        receipt, _ = self.complete(no_responses=True)
        with psycopg.connect(self.database_url) as connection:
            connection.execute("""INSERT INTO trial_results
                (assessment_id,block,trial_number,word,ink_color,condition,correct_response,key_pressed,
                 reaction_time,correct,error_type)
                VALUES (%s,'practice',1,'AZUL','blue','congruent','space','space',0.5,1,'hit')""",
                (receipt['assessment_id'],))
        result = self.h.consulta.get(self.path, params={'test_code': 'stroop_go_nogo_ptbr', 'response_type': 'hit'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['items'], [])

    def test_query7_trial_filters_require_explicit_instrument_capability(self):
        for params in ({'condition': 'congruent'},
                       {'test_code': 'other', 'response_type': 'hit'},
                       [('test_code', 'stroop_go_nogo_ptbr'), ('test_code', 'other'), ('condition', 'congruent')],
                       {'test_code': 'stroop_go_nogo_ptbr', 'condition': 'go'},
                       {'test_code': 'stroop_go_nogo_ptbr', 'response_type': 'hits'},
                       [('test_code', 'stroop_go_nogo_ptbr')] + [('response_type', 'hit')] * 101):
            response = self.h.consulta.get(self.path, params=params)
            self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.h.consulta.get(self.path + '/options', params={'condition': 'congruent'}).status_code, 422)

    def test_w15a_queries_datas_e_listas_invalidas(self):
        for params in ({'start_date': '2026-02-30'}, {'start_date': '2026-03-01', 'end_date': '2026-02-01'},
                       {'platform': 'mobile'}, {'evaluator_id': 'nome@email'}, {'test_version': ''},
                       {'participant_id': 'P' * 513}, {'visit': '\x00'},
                       [('test_code', str(i)) for i in range(101)],
                       [('visit', str(i)) for i in range(101)]):
            response = self.h.consulta.get(self.path, params=params)
            self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.h.consulta.get(self.path + '/options', params={'visit': 'V'}).status_code, 422)
        injection = self.h.consulta.get(self.path, params={'participant_id': "P_SYNTHETIC' OR 1=1 --"})
        self.assertEqual(injection.status_code, 200)
        self.assertEqual(injection.json()['items'], [])

    def test_w15a_limites_facetas_e_conjunto_fecham_sem_truncar(self):
        legacy = self.legacy()
        self.link_legacy()
        with psycopg.connect(self.database_url) as connection:
            connection.execute("""INSERT INTO assessments
                (assessment_id,test_code,test_version,project,participant_id,participant_name,initials,visit,
                 evaluator,assessment_date,started_at,source_file,imported_at,import_status)
                SELECT 'SYNTHETIC_LIMIT_' || n,a.test_code,a.test_version,a.project,'P_SYNTHETIC_' || n,
                    'NAO_COLETADO',NULL,a.visit,a.evaluator,a.assessment_date,a.started_at,
                    'synthetic-limit',a.imported_at,a.import_status
                FROM assessments a CROSS JOIN generate_series(1,201) n WHERE a.assessment_id=%s""", (legacy,))
        response = self.h.consulta.get(self.path + '/options')
        self.assertEqual(response.status_code, 422, response.text)
        self.assertNotIn('items', response.json())
        with psycopg.connect(self.database_url) as connection:
            connection.execute("""INSERT INTO assessments
                (assessment_id,test_code,test_version,project,participant_id,participant_name,initials,visit,
                 evaluator,assessment_date,started_at,source_file,imported_at,import_status)
                SELECT 'SYNTHETIC_VOLUME_' || n,a.test_code,a.test_version,a.project,'P_SYNTHETIC',
                    'NAO_COLETADO',NULL,a.visit,a.evaluator,a.assessment_date,a.started_at,
                    'synthetic-volume',a.imported_at,a.import_status
                FROM assessments a CROSS JOIN generate_series(1,5000) n WHERE a.assessment_id=%s""", (legacy,))
        self.assertEqual(self.h.consulta.get(self.path).status_code, 422)
        body = self.analysis_body()
        response = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(response.status_code, 422, response.text)
        self.assertNotIn('items', response.json())
        body['query']['assessment_ids'] = [legacy]
        response = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['counts']['assessments'], 1)

    def test_queries_fechadas_credencial_ausente_e_limite(self):
        for query in ('?limit=0', '?limit=101', '?limit=2&limit=3', '?test_code=a&test_code=../invalid',
                      '?cursor=bad', '?participant_id=', '?visit=%20', '?unknown=1'):
            self.assertEqual(self.h.consulta.get(self.path + query).status_code, 422, query)
        self.h.app.state.config = replace(self.h.app.state.config, read_database_url='')
        response = self.h.consulta.get(self.path)
        self.assertEqual(response.status_code, 503, response.text)
        self.h.app.state.config = replace(self.h.app.state.config, read_database_url=self.read_url,
                                         professional_read_rate_limit=1)
        # Limite em banco e independente da credencial de consulta SELECT.
        with psycopg.connect(self.database_url) as connection:
            connection.execute('DELETE FROM web_professional_request_limits')
        self.assertEqual(self.h.consulta.get(self.path).status_code, 200)
        limited = self.h.consulta.get(self.path)
        self.assertEqual(limited.status_code, 429, limited.text)
        self.assertIn('retry-after', limited.headers)

    def analysis_body(self, filters=None, **page):
        return {'query': {'projects': [str(self.h.project_id)], 'filters': filters or {}},
                'grouping': {'level': 'assessment', 'dimension': 'project'}, 'page': page}

    def test_analysis_post_normaliza_aliases_pagina_e_mantem_metricas_completas(self):
        first, _ = self.complete()
        second, _ = self.complete()
        body = self.analysis_body({'test_code': ['stroop_go_nogo_ptbr'], 'platform': ['web']}, size=1)
        response = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result['counts'], {'participants': 1, 'visits': 1, 'assessments': 2, 'trials': 32})
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['aggregates'][0]['assessments'], 2)
        self.assertFalse(result['capabilities']['exports'])
        self.assertEqual(response.headers['cache-control'], 'no-store')
        body['page']['cursor'] = result['next_cursor']
        other = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(other.status_code, 200, other.text)
        last = other.json()
        self.assertIsNone(last['next_cursor'])
        self.assertEqual(last['query_id'], result['query_id'])
        self.assertEqual(last['content_fingerprint'], result['content_fingerprint'])
        self.assertEqual({item['assessment_id'] for item in result['items'] + last['items']},
                         {first['assessment_id'], second['assessment_id']})
        for item in result['items'] + last['items']:
            detail = self.h.consulta.get(self.path + '/' + item['assessment_id']).json()
            self.assertEqual(item['summary'], detail['summary'])
        alias = self.analysis_body({'participant_id': [result['items'][0]['participant_id']]})
        a = self.h.consulta.post('/api/v1/analysis/query', json=alias).json()
        alias['query']['filters'] = {'participant_code': [result['items'][0]['participant_id']]}
        b = self.h.consulta.post('/api/v1/analysis/query', json=alias).json()
        self.assertEqual(a['query_fingerprint'], b['query_fingerprint'])
        self.assertEqual(a['normalized_query'], b['normalized_query'])

    def test_analysis_post_selecao_explicita_tentativas_e_capacidade_fechada(self):
        receipt, _ = self.complete()
        detail = self.h.consulta.get(self.path + '/' + receipt['assessment_id']).json()
        body = self.analysis_body({'test_code': ['stroop_go_nogo_ptbr'], 'condition': ['congruent'],
                                   'response_type': ['hit', 'omission']})
        result = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(result.status_code, 200, result.text)
        matched = [trial for trial in detail['trials'] if trial['condition'] == 'congruent'
                   and trial['error_type'] in ('hit', 'omission')]
        self.assertEqual(result.json()['counts']['trials'], len(matched))
        if matched:
            self.assertEqual(result.json()['items'][0]['summary'], detail['summary'])
        for filters in ({'patient_id': 'NOME_SINTETICO'}, {'accuracy_min': 50}, {'platform': ['legacy']},
                        {'condition': ['congruent']}, {'status': 'aborted'},
                        {'participant_id': ['A'], 'participant_code': ['B']},
                        {'date_from': '2026-02-30'}, {'start_date': '2026-01-01', 'date_from': '2026-02-01'}):
            with self.subTest(filters=filters):
                response = self.h.consulta.post('/api/v1/analysis/query', json=self.analysis_body(filters))
                self.assertEqual(response.status_code, 422, response.text)
                self.assertNotIn('NOME_SINTETICO', response.text)
        body = self.analysis_body()
        body['query']['assessment_ids'] = []
        response = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['counts']['assessments'], 0)
        body['query']['assessment_ids'] = [str(uuid4())]
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 409)

    def test_analysis_post_reautoriza_snapshot_expiracao_csrf_e_sem_fallback(self):
        receipt, participant = self.complete()
        self.complete()
        body = self.analysis_body(size=1)
        initial = self.h.consulta.post('/api/v1/analysis/query', json=body)
        self.assertEqual(initial.status_code, 200, initial.text)
        cursor = initial.json()['next_cursor']
        body['page']['cursor'] = cursor
        self.assertEqual(self.h.admin.post('/api/v1/analysis/query', json=body).status_code, 422)
        from datetime import datetime, timedelta, timezone
        from unittest.mock import patch
        with patch('api.analysis.datetime') as clock:
            clock.now.return_value = datetime.now(timezone.utc) + timedelta(minutes=16)
            self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 409)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE trial_results SET word=%s WHERE assessment_id=%s AND trial_number=1',
                               ('SYNTHETIC_CHANGED', receipt['assessment_id']))
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 409)
        body['page']['cursor'] = ('A' if cursor[0] != 'A' else 'B') + cursor[1:]
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 422)
        body = self.analysis_body()
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body,
                                            headers={'X-CSRF-Token': 'invalid'}).status_code, 403)
        self.assertEqual(participant.post('/api/v1/analysis/query', json=body).status_code, 401)
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query?unknown=1', json=body).status_code, 422)
        body['query']['projects'].append(str(uuid4()))
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 404)

        body = self.analysis_body()
        self.h.app.state.config = replace(self.h.app.state.config, read_database_url='')
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 503)
        self.h.app.state.config = replace(self.h.app.state.config, read_database_url=self.read_url)
        user_id = helpers.opaque_user_id(helpers.ISSUER, helpers.CONSULTA)
        self.assertEqual(self.h.admin.put(f'/api/v1/projects/{self.h.project_id}/members/{user_id}',
                                         json={'active': False}).status_code, 200)
        self.assertEqual(self.h.consulta.post('/api/v1/analysis/query', json=body).status_code, 404)

    def test_analysis_metricas_oficiais_limites_rt_nulo_e_busca_codigo(self):
        measured, _ = self.complete()
        absent, _ = self.complete(no_responses=True)
        base = {'test_code': ['stroop_go_nogo_ptbr']}
        def select(filters, **page):
            response = self.h.consulta.post('/api/v1/analysis/query', json=self.analysis_body({**base, **filters}, **page))
            self.assertEqual(response.status_code, 200, response.text)
            return response.json()
        for filters, expected in (
                ({'rt_median_min_ms': 512.25, 'rt_median_max_ms': 513, 'include_null_rt': False}, {measured['assessment_id']}),
                ({'rt_median_max_ms': 512.25, 'include_null_rt': False}, set()),
                ({'rt_median_max_ms': 512.25, 'include_null_rt': True}, {absent['assessment_id']}),
                ({'include_null_rt': False}, {measured['assessment_id']}),
                ({'accuracy_min': 50, 'accuracy_max': 51}, {measured['assessment_id'], absent['assessment_id']}),
                ({'accuracy_max': 50}, set()),
                ({'patient_search': 'p_sintetico'}, {measured['assessment_id'], absent['assessment_id']}),
                ({'patient_search': 'NOME_SINTETICO_RESTRITO'}, set()),
                ({'patient_search': '%'}, set())):
            with self.subTest(filters=filters):
                result = select(filters)
                self.assertEqual({item['assessment_id'] for item in result['items']}, expected)
                self.assertEqual(result['counts']['trials'], len(expected) * 16)
                self.assertIsNone(result['legacy_export_context'])
        for sort in ('response_time_asc', 'response_time_desc'):
            result = select({}, sort=sort)
            self.assertEqual([item['assessment_id'] for item in result['items']], [measured['assessment_id'], absent['assessment_id']])
        result = select({'response_type': ['hit'], 'rt_median_min_ms': 512, 'include_null_rt': False})
        self.assertEqual(result['items'][0]['summary']['total_trials'], 16)
        self.assertEqual(result['counts']['trials'], measured['summary']['hits'])

    def test_analysis_preserva_exportacao_basica_no_mesmo_snapshot(self):
        self.complete()
        response = self.h.consulta.post('/api/v1/analysis/query', json=self.analysis_body()).json()
        exported = self.h.consulta.post('/api/v1/assessments/export', json={
            **response['legacy_export_context'], 'view': {'test_code': 'stroop_go_nogo_ptbr'}})
        self.assertEqual(exported.status_code, 200, exported.text)
        item = response['items'][0]
        self.assertIn(item['assessment_id'], exported.text)
        with psycopg.connect(self.database_url) as connection:
            connection.execute('UPDATE trial_results SET reaction_time=reaction_time+0.01 WHERE assessment_id=%s AND reaction_time IS NOT NULL',
                               (item['assessment_id'],))
        self.assertEqual(self.h.consulta.post('/api/v1/assessments/export', json={
            **response['legacy_export_context'], 'view': {'test_code': 'stroop_go_nogo_ptbr'}}).status_code, 409)
