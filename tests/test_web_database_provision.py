"""Grants WEB reais em banco proprio temporario, sem resetar o banco fornecido."""
import contextlib
from datetime import datetime, timezone
import hashlib
import io
import os
import secrets
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import uuid4

import psycopg
from psycopg import sql

from scripts.migrations import apply_migrations
from scripts.provision_web_database import ProvisionError, configuration, provision
from stroop.application import web_results
from stroop.ingestion.instruments import load_instrument_csv
from stroop.persistence import web_imports, web_assessments
from stroop.persistence import web_sessions
from tests.test_web_results import ORDER, synthetic_conditions, synthetic_payload


def uri(base, *, user=None, password=None, database=None):
    parts = urlsplit(base)
    host = parts.hostname
    if ':' in host:
        host = f'[{host}]'
    netloc = f'{quote(user or parts.username, safe="")}:{quote(password or parts.password, safe="")}@{host}'
    if parts.port:
        netloc += f':{parts.port}'
    return urlunsplit((parts.scheme, netloc, '/' + (database or parts.path.lstrip('/')), parts.query, ''))


class ProvisionConfigurationTests(unittest.TestCase):
    def test_rejeita_destinos_roles_e_opcoes_ambiguas(self):
        base = 'postgresql://synthetic_owner:synthetic-only@127.0.0.1:5432/stroop_etapa4_test_roles'
        values = {'API_MIGRATION_DATABASE_URL': base,
                  'API_DATABASE_URL': uri(base, user='synthetic_writer'),
                  'API_READ_DATABASE_URL': uri(base, user='synthetic_reader')}
        self.assertEqual(configuration(values)[1]['user'], 'synthetic_writer')
        for key, value in (
            ('API_DATABASE_URL', base),
            ('API_READ_DATABASE_URL', uri(base, user='synthetic_reader', database='other')),
            ('API_DATABASE_URL', values['API_DATABASE_URL'] + '?options=-crole%3Dpostgres'),
        ):
            changed = {**values, key: value}
            with self.subTest(key=key), self.assertRaises(Exception):
                configuration(changed)


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'TEST_DATABASE_URL nao configurada')
class ProvisionPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = os.environ['TEST_DATABASE_URL']
        if not psycopg.conninfo.conninfo_to_dict(base).get('dbname', '').startswith('stroop_etapa4_test'):
            raise RuntimeError('Banco descartavel obrigatorio')
        suffix = uuid4().hex[:12]
        cls.base = base
        cls.database = f'stroop_etapa4_test_roles_{suffix}'
        cls.writer = f'synthetic_writer_{suffix}'
        cls.reader = f'synthetic_reader_{suffix}'
        cls.owner_dsn = uri(base, database=cls.database)
        cls.writer_dsn = uri(cls.owner_dsn, user=cls.writer, password='synthetic-writer-only')
        cls.reader_dsn = uri(cls.owner_dsn, user=cls.reader, password='synthetic-reader-only')
        with psycopg.connect(base, autocommit=True) as connection:
            connection.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(cls.database)))
        cls.addClassCleanup(cls.cleanup)
        apply_migrations(cls.owner_dsn)
        cls.values = {'API_MIGRATION_DATABASE_URL': cls.owner_dsn,
                      'API_DATABASE_URL': cls.writer_dsn, 'API_READ_DATABASE_URL': cls.reader_dsn}
        provision(cls.values)

    @classmethod
    def cleanup(cls):
        with psycopg.connect(cls.base, autocommit=True) as connection:
            connection.execute(sql.SQL('DROP DATABASE IF EXISTS {} WITH (FORCE)').format(sql.Identifier(cls.database)))
            for name in (cls.writer, cls.reader):
                connection.execute(sql.SQL('DROP ROLE IF EXISTS {}').format(sql.Identifier(name)))

    def denied(self, dsn, statement):
        with psycopg.connect(dsn) as connection:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                connection.execute(statement)

    def test_grants_idempotentes_reader_minimo_writer_sem_ddl_usuarios_ou_mapa(self):
        provision(self.values)
        provision(self.values)
        with psycopg.connect(self.reader_dsn) as connection:
            connection.execute('SELECT assessment_id,participant_id FROM assessments').fetchall()
            connection.execute('SELECT operation_id,project_id,status,assessment_id FROM web_csv_imports').fetchall()
        for statement in ('SELECT participant_name FROM assessments', 'SELECT initials FROM assessments',
                          'UPDATE web_projects SET active=false', 'SELECT * FROM app_users',
                          "SELECT * FROM public.web_lock_emitter('https://accounts.google.com','synthetic')"):
            self.denied(self.reader_dsn, statement)
        for statement in ('CREATE TABLE public.synthetic_forbidden(id integer)',
                          "UPDATE app_users SET role='administracao'", 'DELETE FROM app_users',
                          "INSERT INTO web_legacy_project_links(legacy_project,project_id) VALUES ('SINTETICO',gen_random_uuid())",
                          'UPDATE assessments SET participant_id=participant_id',
                          'DELETE FROM web_csv_imports'):
            self.denied(self.writer_dsn, statement)
        with psycopg.connect(self.owner_dsn) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=%s)", (self.writer,)).fetchone()[0], 0)

    def test_fluxo_real_writer_grava_resultado_e_reader_consulta(self):
        issuer, subject = 'https://accounts.google.com', f'synthetic-admin-{uuid4().hex[:8]}'
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute("INSERT INTO app_users(issuer,subject,role) VALUES(%s,%s,'administracao')", (issuer, subject))
        project, invitation, session = uuid4(), uuid4(), uuid4()
        web_sessions.create_project(self.writer_dsn, project, f'SYNTHETIC_{uuid4().hex[:8]}', 'Sintetico', issuer, subject)
        self.assertTrue(web_sessions.set_member(self.writer_dsn, project, issuer, subject, True, issuer, subject))
        code_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        token_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        web_sessions.create_invitation(self.writer_dsn, invitation, session, project, code_hash, 'P_SINTETICO', 'V1', issuer, subject)
        web_sessions.redeem(self.writer_dsn, code_hash, token_hash, ORDER)
        web_sessions.start_participant_session(self.writer_dsn, token_hash, 'web-0.1.0')
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute("UPDATE web_participant_sessions SET started_at=clock_timestamp()-interval '61 seconds' WHERE session_id=%s", (session,))
        receipt, created = web_results.complete(self.writer_dsn, token_hash, synthetic_payload(), synthetic_conditions())
        self.assertTrue(created)
        with psycopg.connect(self.reader_dsn) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM trial_results WHERE assessment_id=%s', (receipt['assessment_id'],)).fetchone()[0], 16)
            self.assertEqual(connection.execute('SELECT count(*) FROM assessment_metrics WHERE assessment_id=%s', (receipt['assessment_id'],)).fetchone()[0], 12)

    def test_incremental_writer_grants_links_concurrency_and_multiple_assessments(self):
        from concurrent.futures import ThreadPoolExecutor
        issuer, subject = 'https://accounts.google.com', f'synthetic-links-{uuid4().hex[:8]}'
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute("INSERT INTO app_users(issuer,subject,role) VALUES(%s,%s,'importacao')", (issuer,subject))
        projects = [uuid4(),uuid4()]
        for project in projects:
            web_sessions.create_project(self.writer_dsn,project,f'SYNTHETIC_{uuid4().hex[:8]}','Sintetico',issuer,subject)
            web_sessions.set_member(self.writer_dsn,project,issuer,subject,True,issuer,subject)
        def issue(values):
            project,visit = values
            invitation,session = uuid4(),uuid4()
            code = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
            web_sessions.create_invitation(self.writer_dsn,invitation,session,project,code,'P_SINTETICO',visit,issuer,subject)
            return invitation,session,code
        with ThreadPoolExecutor(max_workers=2) as pool:
            issued = list(pool.map(issue,[(projects[0],'V1'),(projects[0],'V1')]))
        issue((projects[0],'V2'))
        issue((projects[1],'V1'))
        with psycopg.connect(self.owner_dsn) as connection:
            self.assertEqual(connection.execute('SELECT count(DISTINCT participant_uuid),count(DISTINCT visit_uuid) FROM web_invitations WHERE project_id=%s',(projects[0],)).fetchone(),(1,2))
            self.assertEqual(connection.execute('SELECT count(DISTINCT participant_uuid) FROM web_invitations WHERE project_id=ANY(%s)',(projects,)).fetchone()[0],2)
        for invitation,session,code in issued:
            token=hashlib.sha256(secrets.token_bytes(32)).hexdigest()
            web_sessions.redeem(self.writer_dsn,code,token,ORDER)
            web_sessions.start_participant_session(self.writer_dsn,token,'web-0.1.0')
            payload=synthetic_payload()
            response=web_results.checkpoint(self.writer_dsn,token,{**payload,'trials':payload['trials'][:3]},synthetic_conditions())
            self.assertEqual(response['confirmed_through'],3)
            self.assertEqual(web_sessions.get_participant_session(self.writer_dsn,token).checkpoint['prefix_hash'],response['prefix_hash'])
            receipt,created=web_results.complete(self.writer_dsn,token,payload,synthetic_conditions())
            self.assertTrue(created)
            allowed,items=web_assessments.list_assessments(self.reader_dsn,projects[0],issuer,subject,limit=10,offset=0)
            self.assertTrue(allowed)
            self.assertTrue(any(row['assessment_id']==receipt['assessment_id'] for row in items))
        self.assertEqual(len(items),2)
        # A revisao tardia consulta apenas o fim principal, inclusive em historico
        # anterior a checkpoints; nao conceder SELECT de todas as observacoes.
        self.assertFalse(web_results.invalidate(self.writer_dsn,token,'focus_lost',59000)['valid_for_result'])
        allowed,valid = web_assessments.list_assessments(
            self.reader_dsn,projects[0],issuer,subject,limit=10,offset=0)
        self.assertTrue(allowed)
        self.assertEqual(len(valid),1)
        self.denied(self.writer_dsn,'SELECT reaction_time_ms FROM web_trial_observations')
        for statement in ('UPDATE web_session_observations SET payload=payload',
                          'UPDATE web_session_checkpoints SET provenance=provenance',
                          'DELETE FROM web_session_observations',
                          'DELETE FROM web_session_invalidations',
                          'UPDATE web_invitations SET participant_uuid=participant_uuid',
                          'UPDATE web_project_participants SET pseudonym=pseudonym'):
            self.denied(self.writer_dsn,statement)
        for statement in ('INSERT INTO web_session_invalidations(session_id,reason,source) SELECT session_id,\'reload\',\'participant\' FROM web_participant_sessions',
                          'UPDATE web_session_checkpoints SET confirmed_through=confirmed_through'):
            self.denied(self.reader_dsn,statement)
        with psycopg.connect(self.writer_dsn) as connection:
            self.assertEqual(connection.execute('SHOW synchronous_commit').fetchone()[0],'on')
            self.assertEqual(connection.execute('SHOW fsync').fetchone()[0],'on')
            with self.assertRaises(psycopg.errors.ForeignKeyViolation):
                connection.execute("""INSERT INTO web_invitations(invitation_id,session_id,project_id,code_sha256,
                    participant_id,visit,evaluator_issuer,evaluator_subject,expires_at,participant_uuid,visit_uuid)
                    SELECT %s,%s,%s,%s,participant_id,visit,evaluator_issuer,evaluator_subject,
                    CURRENT_TIMESTAMP+interval '24 hours',participant_uuid,visit_uuid
                    FROM web_invitations WHERE invitation_id=%s""",
                    (uuid4(),uuid4(),projects[1],hashlib.sha256(secrets.token_bytes(32)).hexdigest(),issued[0][0]))

    def test_papeis_provisionados_importam_e_consultam_csv_web(self):
        issuer, subject = 'https://accounts.google.com', f'synthetic-import-{uuid4().hex[:8]}'
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute("INSERT INTO app_users(issuer,subject,role) VALUES(%s,%s,'importacao')", (issuer, subject))
        project = uuid4()
        project_code = f'SYNTHETIC_{uuid4().hex[:8]}'
        web_sessions.create_project(self.writer_dsn, project, project_code, 'Sintetico', issuer, subject)
        self.assertTrue(web_sessions.set_member(self.writer_dsn, project, issuer, subject, True, issuer, subject))

        source = Path(__file__).parent / 'fixtures/csv/valido_minimo.csv'
        csv_text = source.read_text(encoding='utf-8')
        csv_text = csv_text.replace('Pessoa Ficticia,,', 'NAO_COLETADO,,')
        csv_text = csv_text.replace('00000000-0000-4000-8000-000000000001', str(uuid4()))
        csv_text = csv_text.replace('PROJETO_SINTETICO', 'SYNTHETIC_UNMAPPED_SOURCE')
        operation, assessment = uuid4(), None
        content_hash = hashlib.sha256(csv_text.encode('utf-8')).hexdigest()
        with tempfile.TemporaryDirectory(prefix='stroop-synthetic-import-') as directory:
            csv_path = Path(directory) / 'input.csv'
            csv_path.write_text(csv_text, encoding='utf-8')
            web_imports.begin(self.writer_dsn, operation, project, issuer, subject, content_hash)
            web_imports.mark_validated(self.writer_dsn, operation, project, issuer, subject)
            normalized = load_instrument_csv(csv_path)
            event = web_imports.import_normalized(self.writer_dsn, operation, project, issuer,
                                                 subject, content_hash, normalized,
                                                 '2026-10-17T00:00:00+00:00')
            self.assertEqual(event['status'], 'importado')
            assessment = normalized.metadata['assessment_id']

        allowed, items, _ = web_assessments.list_assessments(
            self.reader_dsn, project, issuer, subject, limit=10, offset=0,
            filters={}, include_snapshot=True)
        self.assertTrue(allowed)
        self.assertEqual([item['assessment_id'] for item in items], [assessment])
        self.assertEqual(items[0]['project_code'], project_code)

    def test_baseline_public_create_recusado_sem_modificar_public(self):
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute('GRANT CREATE ON SCHEMA public TO PUBLIC')
        try:
            with self.assertRaises(ProvisionError):
                provision(self.values)
            with psycopg.connect(self.owner_dsn) as connection:
                self.assertTrue(connection.execute("SELECT has_schema_privilege('public','public','CREATE')").fetchone()[0])
        finally:
            with psycopg.connect(self.owner_dsn) as connection:
                connection.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')

    def test_funcao_definer_preserva_bloqueio_concorrente_sem_update_writer(self):
        issuer, subject = 'https://accounts.google.com', f'synthetic-lock-{uuid4().hex[:8]}'
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute("INSERT INTO app_users(issuer,subject,role) VALUES(%s,%s,'importacao')", (issuer, subject))
        with psycopg.connect(self.writer_dsn) as writer:
            self.assertEqual(writer.execute('SELECT * FROM public.web_lock_emitter(%s,%s)', (issuer, subject)).fetchone(), (True, 'importacao'))
            with psycopg.connect(self.owner_dsn) as owner:
                owner.execute("SET LOCAL lock_timeout='100ms'")
                with self.assertRaises(psycopg.errors.LockNotAvailable):
                    owner.execute('UPDATE app_users SET active=false WHERE issuer=%s AND subject=%s', (issuer, subject))
        with psycopg.connect(self.owner_dsn) as owner:
            owner.execute('UPDATE app_users SET active=false WHERE issuer=%s AND subject=%s', (issuer, subject))
        with psycopg.connect(self.writer_dsn) as writer:
            self.assertEqual(writer.execute('SELECT * FROM public.web_lock_emitter(%s,%s)', (issuer, subject)).fetchone(), (False, 'importacao'))

    def test_membership_ownership_e_superuser_gerenciados_sao_recusados(self):
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute(sql.SQL('ALTER ROLE {} SUPERUSER').format(sql.Identifier(self.writer)))
        try:
            with self.assertRaises(ProvisionError):
                provision(self.values)
        finally:
            with psycopg.connect(self.owner_dsn) as connection:
                connection.execute(sql.SQL('ALTER ROLE {} NOSUPERUSER').format(sql.Identifier(self.writer)))
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(self.reader), sql.Identifier(self.writer)))
        try:
            with self.assertRaises(ProvisionError):
                provision(self.values)
        finally:
            with psycopg.connect(self.owner_dsn) as connection:
                connection.execute(sql.SQL('REVOKE {} FROM {}').format(sql.Identifier(self.reader), sql.Identifier(self.writer)))
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute('CREATE TABLE public.synthetic_owned_probe(id integer)')
            connection.execute(sql.SQL('ALTER TABLE public.synthetic_owned_probe OWNER TO {}').format(sql.Identifier(self.writer)))
        try:
            with self.assertRaises(ProvisionError):
                provision(self.values)
        finally:
            with psycopg.connect(self.owner_dsn) as connection:
                connection.execute('DROP TABLE public.synthetic_owned_probe')

    def test_papel_existente_alheio_e_perigoso_nao_e_assumido(self):
        with psycopg.connect(self.owner_dsn) as connection:
            connection.execute(sql.SQL('COMMENT ON ROLE {} IS NULL').format(sql.Identifier(self.writer)))
        try:
            with self.assertRaises(ProvisionError):
                provision(self.values)
        finally:
            with psycopg.connect(self.owner_dsn) as connection:
                db_oid, owner_oid = connection.execute("SELECT (SELECT oid FROM pg_database WHERE datname=current_database()),(SELECT oid FROM pg_roles WHERE rolname=current_user)").fetchone()
                connection.execute(sql.SQL('COMMENT ON ROLE {} IS {}').format(sql.Identifier(self.writer), sql.Literal(f'stroop-web-role-v1:{db_oid}:{owner_oid}:writer')))
