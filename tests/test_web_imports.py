"""Importacao WEB com banco PostgreSQL descartavel e dados sinteticos."""
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

from stroop.persistence import web_assessments
from tests import test_web_sessions as helpers


ROOT = Path(__file__).resolve().parents[1]
READER = 'synthetic_w15e_reader'


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'TEST_DATABASE_URL nao configurada')
class WebCsvImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = os.environ['TEST_DATABASE_URL']
        if not psycopg.conninfo.conninfo_to_dict(cls.database_url).get('dbname', '').startswith('stroop_etapa4_test'):
            raise RuntimeError('Banco PostgreSQL descartavel obrigatorio')
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
            for table, columns in web_assessments.REQUIRED_COLUMNS.items():
                connection.execute(sql.SQL('GRANT SELECT ({}) ON {} TO {}').format(
                    sql.SQL(',').join(map(sql.Identifier, sorted(columns))),
                    sql.Identifier(table), sql.Identifier(READER)))
        self.h.app.state.config = replace(self.h.app.state.config, read_database_url=self.read_url)
        self.path = f'/api/v1/projects/{self.h.project_id}/imports'
        self.assessments_path = f'/api/v1/projects/{self.h.project_id}/assessments'

    @staticmethod
    def csv_bytes(assessment_id=None, participant_name='NAO_COLETADO', initials=''):
        with (ROOT / 'tests/fixtures/csv/valido_minimo.csv').open(encoding='utf-8', newline='') as source:
            rows = list(csv.DictReader(source))
        assessment_id = assessment_id or str(uuid4())
        for row in rows:
            row.update(project='SYNTHETIC_UNMAPPED_LABEL', participant_id='P_SYNTHETIC_W15E',
                       participant_name=participant_name, initials=initials,
                       visit='V_SYNTHETIC_W15E', evaluator='E_SYNTHETIC_W15E',
                       assessment_id=assessment_id)
        output = io.StringIO(newline='')
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator='\r\n')
        writer.writeheader(); writer.writerows(rows)
        return output.getvalue().encode('utf-8'), assessment_id

    def upload(self, client, content, operation_id=None):
        operation_id = operation_id or uuid4()
        response = client.post(f'{self.path}/{operation_id}', content=content,
                               headers={'Content-Type': 'text/csv; charset=utf-8'})
        return response, operation_id

    def test_importa_no_projeto_explicitamente_selecionado_e_consulta_dashboard_real(self):
        content, assessment_id = self.csv_bytes()
        uploaded, operation_id = self.upload(self.h.importer, content)
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        self.assertEqual(uploaded.json()['status'], 'importado')
        self.assertEqual(uploaded.json()['assessment_id'], assessment_id)
        status = self.h.importer.get(f'{self.path}/{operation_id}')
        self.assertEqual(status.status_code, 200, status.text)
        self.assertEqual(status.json()['status'], 'importado')
        listed = self.h.consulta.get(self.assessments_path)
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual([row['assessment_id'] for row in listed.json()['items']], [assessment_id])
        detail = self.h.consulta.get(f'{self.assessments_path}/{assessment_id}')
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertEqual(detail.json()['project_id'], str(self.h.project_id))
        self.assertEqual(detail.json()['platform'], 'psychopy')
        exported = self.h.consulta.get(f'{self.assessments_path}/{assessment_id}/export')
        self.assertEqual(exported.status_code, 200, exported.text)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(exported.text)))), 4)
        self.assertIn('NAO_COLETADO', exported.text)
        self.assertNotIn('SYNTHETIC_UNMAPPED_LABEL', listed.text)

    def test_rejeita_nome_sem_gravar_payload_e_rejeita_duplicata_sem_sobrescrever(self):
        raw, assessment_id = self.csv_bytes(participant_name='NOME_SINTETICO_RESTRITO', initials='NS')
        rejected, op = self.upload(self.h.importer, raw)
        self.assertEqual(rejected.status_code, 200, rejected.text)
        self.assertEqual(rejected.json()['status'], 'rejeitado')
        self.assertEqual(rejected.json()['error_code'], 'invalid_csv')
        self.assertNotIn('NOME_SINTETICO_RESTRITO', rejected.text)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0], 0)
            self.assertEqual(connection.execute('SELECT status FROM web_csv_imports WHERE operation_id=%s', (op,)).fetchone()[0], 'rejeitado')

        safe, assessment_id = self.csv_bytes(assessment_id)
        first, _ = self.upload(self.h.importer, safe)
        second, duplicate_operation = self.upload(self.h.importer, safe)
        self.assertEqual(first.json()['status'], 'importado')
        self.assertEqual(second.json()['status'], 'rejeitado')
        self.assertEqual(second.json()['error_code'], 'duplicate_assessment')
        self.assertEqual(self.h.importer.get(f'{self.path}/{duplicate_operation}').json()['status'], 'rejeitado')
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0], 1)

    def test_perfil_sem_permissao_e_projeto_sem_vinculo_nao_importam(self):
        content, _ = self.csv_bytes()
        denied, _ = self.upload(self.h.consulta, content)
        self.assertEqual(denied.status_code, 403, denied.text)
        response = self.h.admin.post('/api/v1/projects', json={
            'code': 'SYNTHETIC_OTHER', 'name': 'Projeto sintetico sem vinculo',
        })
        self.assertEqual(response.status_code, 201, response.text)
        other_path = f"/api/v1/projects/{response.json()['id']}/imports/{uuid4()}"
        cross = self.h.importer.post(other_path, content=content,
                                     headers={'Content-Type': 'text/csv; charset=utf-8'})
        self.assertEqual(cross.status_code, 404, cross.text)
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM web_csv_imports').fetchone()[0], 0)

    def test_auditoria_e_avaliacao_sao_atomicas_e_retry_reusa_operacao(self):
        content, assessment_id = self.csv_bytes()
        operation_id = uuid4()
        with psycopg.connect(self.database_url) as connection:
            connection.execute('''CREATE FUNCTION synthetic_fail_import_audit() RETURNS trigger
                LANGUAGE plpgsql AS $$ BEGIN
                    IF NEW.status = 'importado' THEN RAISE EXCEPTION 'synthetic audit failure'; END IF;
                    RETURN NEW;
                END $$''')
            connection.execute('''CREATE TRIGGER synthetic_fail_import_audit
                BEFORE UPDATE ON web_csv_imports FOR EACH ROW
                EXECUTE FUNCTION synthetic_fail_import_audit()''')
        failed, _ = self.upload(self.h.importer, content, operation_id)
        self.assertEqual(failed.status_code, 503, failed.text)
        status = self.h.importer.get(f'{self.path}/{operation_id}')
        self.assertEqual(status.status_code, 200, status.text)
        self.assertEqual(status.json()['status'], 'validado')
        with psycopg.connect(self.database_url) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments WHERE assessment_id=%s', (assessment_id,)).fetchone()[0], 0)
            connection.execute('DROP TRIGGER synthetic_fail_import_audit ON web_csv_imports')
            connection.execute('DROP FUNCTION synthetic_fail_import_audit()')
        retried, _ = self.upload(self.h.importer, content, operation_id)
        self.assertEqual(retried.status_code, 200, retried.text)
        self.assertEqual(retried.json()['status'], 'importado')
        self.assertEqual(self.h.importer.get(f'{self.path}/{operation_id}').json()['status'], 'importado')


if __name__ == '__main__':
    unittest.main()
