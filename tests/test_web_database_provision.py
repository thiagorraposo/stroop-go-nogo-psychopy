"""Grants WEB reais em banco proprio temporario, sem resetar o banco fornecido."""
import contextlib
from datetime import datetime, timezone
import hashlib
import io
import os
import secrets
import unittest
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import uuid4

import psycopg
from psycopg import sql

from scripts.migrations import apply_migrations
from scripts.provision_web_database import ProvisionError, configuration, provision
from stroop.application import web_results
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
        for statement in ('SELECT participant_name FROM assessments', 'SELECT initials FROM assessments',
                          'UPDATE web_projects SET active=false', 'SELECT * FROM app_users',
                          "SELECT * FROM public.web_lock_emitter('https://accounts.google.com','synthetic')"):
            self.denied(self.reader_dsn, statement)
        for statement in ('CREATE TABLE public.synthetic_forbidden(id integer)',
                          "UPDATE app_users SET role='administracao'", 'DELETE FROM app_users',
                          "INSERT INTO web_legacy_project_links(legacy_project,project_id) VALUES ('SINTETICO',gen_random_uuid())",
                          'UPDATE assessments SET participant_id=participant_id'):
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
