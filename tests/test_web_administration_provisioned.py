"""Administracao HTTP e SQL com o writer real, sem privilegios de proprietario."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import os
import secrets
import threading
import unittest
from uuid import uuid4

import psycopg
from psycopg import sql
from fastapi.testclient import TestClient

from api.config import APIConfig
from api.main import create_app
from scripts.migrations import apply_migrations
from scripts.provision_web_database import provision
from stroop.application import web_administration
from stroop.domain.auth import AppUser, ForbiddenOperationError, LastAdminProtectionError
from tests.test_web_database_provision import uri


ISSUER = 'https://accounts.google.com'
ORIGIN = 'https://synthetic.example.test'
SIGNATURE = 'public.web_manage_user(text,text,text,text,text,text,text,boolean)'


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'TEST_DATABASE_URL nao configurada')
class WebAdministrationProvisionedTests(unittest.TestCase):
    def setUp(self):
        self.base = os.environ['TEST_DATABASE_URL']
        if not psycopg.conninfo.conninfo_to_dict(self.base).get('dbname', '').startswith('stroop_etapa4_test'):
            raise RuntimeError('Banco PostgreSQL descartavel obrigatorio')
        suffix = uuid4().hex[:12]
        self.database = f'stroop_etapa4_test_admin_{suffix}'
        self.writer = f'synthetic_admin_writer_{suffix}'
        self.reader = f'synthetic_admin_reader_{suffix}'
        self.owner_dsn = uri(self.base, database=self.database)
        self.writer_dsn = uri(self.owner_dsn, user=self.writer, password='synthetic-writer-only')
        self.reader_dsn = uri(self.owner_dsn, user=self.reader, password='synthetic-reader-only')
        with psycopg.connect(self.base, autocommit=True) as db:
            db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(self.database)))
        self.addCleanup(self.cleanup)
        apply_migrations(self.owner_dsn)
        self.environment = {'API_MIGRATION_DATABASE_URL': self.owner_dsn,
                            'API_DATABASE_URL': self.writer_dsn,
                            'API_READ_DATABASE_URL': self.reader_dsn}
        provision(self.environment)
        self.actor = self.seed_user('synthetic-primary-admin', 'administracao')

    def cleanup(self):
        with psycopg.connect(self.base, autocommit=True) as db:
            db.execute(sql.SQL('DROP DATABASE IF EXISTS {} WITH (FORCE)').format(sql.Identifier(self.database)))
            for name in (self.writer, self.reader):
                db.execute(sql.SQL('DROP ROLE IF EXISTS {}').format(sql.Identifier(name)))

    def seed_user(self, subject, role, active=True):
        with psycopg.connect(self.owner_dsn) as db:
            db.execute('INSERT INTO app_users(issuer,subject,role,active) VALUES(%s,%s,%s,%s)',
                       (ISSUER, subject, role, active))
        return AppUser(ISSUER, subject, None, role, active)

    def client(self, actor=None):
        actor = actor or self.actor
        token = secrets.token_urlsafe(32)
        with psycopg.connect(self.owner_dsn) as db:
            db.execute("""INSERT INTO web_professional_sessions
                (token_sha256,issuer,subject,oidc_expires_at,expires_at)
                VALUES(%s,%s,%s,CURRENT_TIMESTAMP+INTERVAL '1 hour',
                       CURRENT_TIMESTAMP+INTERVAL '1 hour')""",
                       (sha256(token.encode('ascii')).hexdigest(), actor.issuer, actor.subject))
        config = APIConfig(auth_mode="oidc", database_url=self.writer_dsn, read_database_url=self.reader_dsn,
                           public_origin=ORIGIN, app_env='test',
                           oidc_client_id='synthetic-client-id',
                           oidc_client_secret='synthetic-client-secret-never-use',
                           session_secret='synthetic-session-secret-never-use-0000000000')
        client = TestClient(create_app(config), base_url=ORIGIN)
        self.addCleanup(client.close)
        client.headers['Cookie'] = '__Host-stroop_professional=' + token
        me = client.get('/api/v1/auth/me')
        self.assertEqual(me.status_code, 200)
        client.headers.update({'Origin': ORIGIN, 'X-CSRF-Token': me.json()['csrf_token']})
        return client

    def test_http_cadastra_edita_e_audita_com_writer_restrito(self):
        client = self.client()
        response = client.post('/api/v1/admin/users', json={
            'issuer': ISSUER, 'subject': 'synthetic-managed-user', 'role': 'consulta'})
        self.assertEqual(response.status_code, 201, response.text)
        user_id = response.json()['user_id']
        response = client.put('/api/v1/admin/users/' + user_id,
                              json={'role': 'importacao', 'active': False, 'email': None})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual((response.json()['role'], response.json()['active']), ('importacao', False))
        listed = client.get('/api/v1/admin/users')
        self.assertEqual(listed.status_code, 200)
        self.assertEqual([(u['role'], u['active']) for u in listed.json()['items']
                          if u['user_id'] == user_id], [('importacao', False)])
        with psycopg.connect(self.owner_dsn) as db:
            row = db.execute("""SELECT created_by_issuer,created_by_subject
                FROM app_users WHERE issuer=%s AND subject='synthetic-managed-user'""", (ISSUER,)).fetchone()
            self.assertEqual(row, (self.actor.issuer, self.actor.subject))
            self.assertEqual(db.execute("SELECT count(*) FROM auth_audit_events WHERE action='manage_users' AND outcome='success'").fetchone()[0], 2)
        duplicate = client.post('/api/v1/admin/users', json={
            'issuer': ISSUER, 'subject': 'synthetic-managed-user', 'role': 'consulta'})
        self.assertEqual(duplicate.status_code, 422)
        with psycopg.connect(self.owner_dsn) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM auth_audit_events WHERE action='manage_users' AND outcome='success'").fetchone()[0], 2)

    def test_http_perfil_consulta_nao_pode_gerir_contas(self):
        client = self.client(self.seed_user('synthetic-reader-actor', 'consulta'))
        response = client.post('/api/v1/admin/users', json={
            'issuer': ISSUER, 'subject': 'synthetic-forbidden-target', 'role': 'administracao'})
        self.assertEqual(response.status_code, 403)
        with psycopg.connect(self.owner_dsn) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM app_users WHERE subject='synthetic-forbidden-target'").fetchone()[0], 0)

    def test_funcao_revalida_ator_bloqueado_e_nao_admin_sem_alteracao(self):
        for actor in (self.seed_user('synthetic-reader', 'consulta'),
                      self.seed_user('synthetic-blocked-admin', 'administracao', False)):
            # O valor recebido em memoria nao substitui a revalidacao do estado SQL.
            stale_actor = AppUser(actor.issuer, actor.subject, None, 'administracao', True)
            with self.subTest(subject=actor.subject), self.assertRaises(ForbiddenOperationError):
                web_administration.create_user(self.writer_dsn, ISSUER,
                    'synthetic-not-created', 'administracao', None, stale_actor)
        with psycopg.connect(self.owner_dsn) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM app_users WHERE subject='synthetic-not-created'").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM auth_audit_events WHERE action='manage_users' AND outcome='success'").fetchone()[0], 0)

    def test_funcao_nao_concede_dml_direto_execucao_publica_ou_reader(self):
        provision(self.environment)
        with psycopg.connect(self.owner_dsn) as db:
            self.assertFalse(db.execute("""SELECT EXISTS (
                SELECT 1 FROM pg_proc p,
                LATERAL aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a
                WHERE p.oid=to_regprocedure(%s) AND a.grantee=0 AND a.privilege_type='EXECUTE')""", (SIGNATURE,)).fetchone()[0])
            self.assertFalse(db.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')', (self.reader, SIGNATURE)).fetchone()[0])
        statements = [
            (self.writer_dsn, "INSERT INTO app_users(issuer,subject,role) VALUES('https://accounts.google.com','synthetic-direct','administracao')"),
            (self.writer_dsn, "UPDATE app_users SET role='administracao'"),
            (self.writer_dsn, 'DELETE FROM app_users'),
            (self.reader_dsn, "SELECT public.web_manage_user('create','https://accounts.google.com','synthetic-primary-admin','https://accounts.google.com','synthetic-forbidden','consulta',NULL,TRUE)"),
        ]
        for dsn, statement in statements:
            with self.subTest(statement=statement), psycopg.connect(dsn) as db:
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    db.execute(statement)

    def test_ultimo_admin_protegido_http_e_concorrencia_real(self):
        client = self.client()
        me = client.get('/api/v1/auth/me').json()
        response = client.put('/api/v1/admin/users/' + me['user_id'],
                              json={'role': 'consulta', 'active': True, 'email': None})
        self.assertEqual(response.status_code, 409, response.text)
        second = self.seed_user('synthetic-secondary-admin', 'administracao')
        barrier = threading.Barrier(2)

        def demote(actor):
            barrier.wait(timeout=10)
            try:
                web_administration.update_user(self.writer_dsn, actor.issuer, actor.subject,
                    role='consulta', active=True, email=None, actor=actor)
                return 'updated'
            except LastAdminProtectionError:
                return 'last_admin'

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(demote, (self.actor, second)))
        self.assertCountEqual(results, ['updated', 'last_admin'])
        with psycopg.connect(self.owner_dsn) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM app_users WHERE active AND role='administracao'").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM auth_audit_events WHERE action='manage_users' AND outcome='success'").fetchone()[0], 1)
