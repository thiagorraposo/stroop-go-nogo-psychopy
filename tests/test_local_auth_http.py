"""Contrato HTTP local com PostgreSQL descartavel real, sem doubles de senha."""
from dataclasses import replace
from hashlib import sha256
import os
import unittest
from uuid import uuid4
from unittest.mock import patch

import psycopg
from fastapi.testclient import TestClient

from api.config import APIConfig
from api.main import create_app
from api.auth import PROFESSIONAL_COOKIE
from scripts.migrations import apply_migrations
from stroop.application.local_auth import provision
from stroop.domain.local_auth import LOCAL_ISSUER
from tests.test_local_auth import PASSWORD, OTHER

ORIGIN = 'https://synthetic.example.test'
DSN = os.environ.get('TEST_DATABASE_URL', '')


@unittest.skipUnless(DSN, 'TEST_DATABASE_URL nao configurada')
class LocalAuthHTTPTests(unittest.TestCase):
    def setUp(self):
        if not psycopg.conninfo.conninfo_to_dict(DSN).get('dbname','').startswith('stroop_etapa4_test'):
            raise RuntimeError('PG descartavel obrigatorio')
        with psycopg.connect(DSN, autocommit=True) as c:
            c.execute('DROP SCHEMA public CASCADE')
            c.execute('CREATE SCHEMA public')
        apply_migrations(DSN)
        provision(DSN, 'synthetic', PASSWORD)
        self.config = APIConfig(database_url=DSN, read_database_url=DSN, public_origin=ORIGIN, app_env='test',
            oidc_client_id='', oidc_client_secret='', session_secret='synthetic-only-session-signature-2026', auth_mode='local')
        self.app = create_app(self.config)
        self.client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(self.client.close)

    def rows(self, sql, args=()):
        with psycopg.connect(DSN) as c:
            return c.execute(sql, args).fetchall()

    def login(self, **body):
        return self.client.post('/api/v1/auth/login', json={'username':'  SYNTHETIC ', 'password':PASSWORD} | body,
                                headers={'Origin': ORIGIN})

    def signed(self):
        response = self.login()
        self.assertEqual(response.status_code, 200, response.text)
        self.client.headers.update({'Origin': ORIGIN, 'X-CSRF-Token': response.json()['csrf_token']})
        return response

    def test_login_cookie_rotacao_me_logout_e_replay(self):
        first = self.signed()
        token = self.client.cookies.get(PROFESSIONAL_COOKIE)
        self.assertEqual(set(first.json()), {'user_id','role','expires_at','csrf_token'})
        self.assertEqual(first.json()['role'], 'administracao')
        for part in ('Secure', 'HttpOnly', 'SameSite=lax', 'Path=/', 'Max-Age='):
            self.assertIn(part, first.headers['set-cookie'])
        self.assertNotIn('Domain=', first.headers['set-cookie'])
        self.assertNotIn(token, first.text)
        self.assertNotIn(PASSWORD, first.text)
        second = self.signed()
        self.assertNotEqual(token, self.client.cookies.get(PROFESSIONAL_COOKIE))
        self.assertIsNotNone(self.rows('SELECT revoked_at FROM web_local_sessions WHERE token_sha256=%s',
                                     (sha256(token.encode()).hexdigest(),))[0][0])
        before = self.rows('SELECT last_activity_at FROM web_local_sessions WHERE revoked_at IS NULL')
        me = self.client.get('/api/v1/auth/me')
        self.assertEqual(me.json(), second.json())
        self.assertEqual(before, self.rows('SELECT last_activity_at FROM web_local_sessions WHERE revoked_at IS NULL'))
        token = self.client.cookies.get(PROFESSIONAL_COOKIE)
        self.assertEqual(self.client.post('/api/v1/auth/logout',json={}).status_code, 204)
        self.assertEqual(self.client.get('/api/v1/auth/me',headers={'Cookie':PROFESSIONAL_COOKIE+'='+token}).status_code,401)
        self.assertEqual(self.client.post('/api/v1/auth/logout',json={}).status_code,204)

    def test_csrf_origin_queries_body_limits_et_schema(self):
        body = {'username':'synthetic','password':PASSWORD}
        for origin in (None, 'null', 'https://attacker.invalid'):
            response = self.client.post('/api/v1/auth/login', json=body, headers={} if origin is None else {'Origin':origin})
            self.assertEqual(response.status_code,403)
        for path, kwargs, status in (
            ('/api/v1/auth/login?extra=1', {'json':body},422),
            ('/api/v1/auth/login', {'json':body | {'role':'administracao'}},422),
            ('/api/v1/auth/login', {'json':body | {'password':1}},422),
            ('/api/v1/auth/login', {'content':'x'*4097,'headers':{'Content-Type':'application/json'}},413),
            ('/api/v1/auth/login', {'content':'{}','headers':{'Content-Type':'text/plain'}},415),
        ):
            headers = {'Origin':ORIGIN} | kwargs.pop('headers',{})
            self.assertEqual(self.client.post(path,headers=headers,**kwargs).status_code,status)
        self.assertEqual(self.rows('SELECT count(*) FROM web_local_sessions'),[(0,)])
        for path in ('/api/v1/auth/login','/api/v1/auth/callback','/oauth2callback'):
            self.assertEqual(self.client.get(path).status_code,404)

    def test_erros_genericos_limites_conta_e_origem_e_indisponibilidade(self):
        known = self.login(password=OTHER)
        unknown = self.login(username='missing',password=OTHER)
        self.assertEqual(known.status_code,401)
        self.assertEqual(known.json()['error'],unknown.json()['error'])
        with psycopg.connect(DSN) as c:
            c.execute('UPDATE app_users SET active=FALSE WHERE issuer=%s',(LOCAL_ISSUER,))
        blocked = self.login()
        self.assertEqual(known.json()['error'],blocked.json()['error'])
        self.assertNotIn('registration_request',blocked.text)
        for _ in range(3): self.login(password=OTHER)
        limited = self.login()
        self.assertEqual(limited.status_code,429,limited.text)
        self.assertTrue(limited.headers['retry-after'].isdigit())
        client = TestClient(create_app(replace(self.config,login_rate_limit=2)),base_url=ORIGIN)
        self.addCleanup(client.close)
        # Origens ASGI iguais compartilham contador apesar do identificador distinto.
        self.assertEqual(client.post('/api/v1/auth/login',json={'username':'another','password':PASSWORD},
                                     headers={'Origin':ORIGIN,'X-Forwarded-For':'198.51.100.20'}).status_code,429)
        with psycopg.connect(DSN) as c: c.execute('DROP TABLE web_local_auth_limits')
        self.assertEqual(self.login().status_code,503)

    def test_senha_troca_revoga_todas_e_requer_csrf_senha_atual(self):
        self.signed()
        first = self.client.cookies.get(PROFESSIONAL_COOKIE)
        body = {'current_password':PASSWORD,'new_password':OTHER}
        response = self.client.post('/api/v1/auth/password',json=body,headers={'X-CSRF-Token':'invalid'})
        self.assertEqual(response.status_code,403)
        response = self.client.post('/api/v1/auth/password',json=body | {'current_password':OTHER})
        self.assertEqual(response.status_code,401)
        response = self.client.post('/api/v1/auth/password',json=body)
        self.assertEqual(response.status_code,204,response.text)
        self.assertIn('Max-Age=0',response.headers['set-cookie'])
        self.assertEqual(self.client.get('/api/v1/auth/me',headers={'Cookie':PROFESSIONAL_COOKIE+'='+first}).status_code,401)
        self.assertEqual(self.login().status_code,401)
        self.assertEqual(self.login(password=OTHER).status_code,200)
        self.assertEqual(self.rows('SELECT credential_version FROM web_local_credentials'),[(2,)])

    def test_gestao_local_ultimo_admin_revogacao_sem_vinculo_implicito(self):
        login = self.signed()
        user_id = login.json()['user_id']
        users = self.client.get('/api/v1/admin/users')
        self.assertEqual(users.status_code,200,users.text)
        self.assertEqual(users.json()['items'],[{'user_id':user_id,'role':'administracao','active':True}])
        response = self.client.post('/api/v1/admin/users',json={'issuer':'https://accounts.google.com',
            'subject':'synthetic-new','role':'administracao'})
        self.assertEqual(response.status_code,403)
        for body in ({'role':'consulta','active':True},{'role':'administracao','active':False}):
            self.assertEqual(self.client.patch('/api/v1/admin/users/'+user_id,json=body).status_code,409)
        self.assertEqual(self.client.patch('/api/v1/admin/users/'+user_id,json={'role':'administracao','active':True}).status_code,200)
        self.assertEqual(self.rows('SELECT count(*) FROM web_project_members'),[(0,)])
        response = self.client.post('/api/v1/admin/users/'+user_id+'/sessions/revoke',json={})
        self.assertEqual(response.status_code,204,response.text)
        self.assertEqual(self.client.get('/api/v1/auth/me').status_code,401)

    def test_atividade_so_apos_acesso_autorizado_e_inatividade(self):
        self.signed()
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_sessions SET created_at=clock_timestamp()-INTERVAL '10 minutes', last_activity_at=CURRENT_TIMESTAMP-INTERVAL '5 minutes', absolute_expires_at=CURRENT_TIMESTAMP+INTERVAL '7 hours'")
        before = self.rows('SELECT last_activity_at FROM web_local_sessions')
        self.assertEqual(self.client.get('/api/v1/auth/me').status_code,200)
        self.assertEqual(self.client.get('/api/v1/projects/'+str(uuid4())+'/assessments').status_code,404)
        self.assertEqual(self.rows('SELECT last_activity_at FROM web_local_sessions'),before)
        projects = self.client.get('/api/v1/projects')
        self.assertEqual(projects.status_code,200,projects.text)
        self.assertGreater(self.rows('SELECT last_activity_at FROM web_local_sessions')[0][0],before[0][0])
        self.assertIn('set-cookie',projects.headers)
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_sessions SET created_at=clock_timestamp()-INTERVAL '31 minutes', last_activity_at=CURRENT_TIMESTAMP-INTERVAL '30 minutes', absolute_expires_at=CURRENT_TIMESTAMP+INTERVAL '7 hours'")
        self.assertEqual(self.client.get('/api/v1/auth/me').status_code,401)


    def test_revogacao_apos_commit_nao_transforma_sucesso_em_erro(self):
        self.signed()
        from api.local_session import record_activity
        from stroop.persistence.local_auth import revoke
        def revoke_before_renewal(database_url, token_hash):
            revoke(database_url, token_hash)
            return record_activity(database_url, token_hash)
        with patch('api.local_session.record_activity', side_effect=revoke_before_renewal):
            result = self.client.post('/api/v1/projects',json={'code':'SYNTHETIC','name':'Synthetic committed project'})
        self.assertEqual(result.status_code,201,result.text)
        self.assertEqual(self.rows("SELECT count(*) FROM web_projects WHERE code='SYNTHETIC'"),[(1,)])
        self.assertIn('Max-Age=0',result.headers['set-cookie'])
        self.assertEqual(self.client.get('/api/v1/auth/me').status_code,401)


    def test_admin_local_protegido_mesmo_com_google_historico_e_bloqueio_nao_ressuscita(self):
        primary = self.signed().json()
        extra = uuid4()
        with psycopg.connect(DSN) as c:
            c.execute("INSERT INTO app_users(issuer,subject,role) VALUES ('https://accounts.google.com','synthetic-history','administracao')")
            # Fixture exclusiva do operador; produto nao oferece segunda conta.
            c.execute("INSERT INTO app_users(issuer,subject,role) VALUES (%s,%s,'consulta')", (LOCAL_ISSUER,str(extra)))
            c.execute("INSERT INTO web_local_credentials(principal_id,username,password_hash) SELECT %s,'synthetic-extra',password_hash FROM web_local_credentials LIMIT 1",(extra,))
        result = self.client.patch('/api/v1/admin/users/'+primary['user_id'],json={'role':'consulta','active':True})
        self.assertEqual(result.status_code,409,result.text)
        other = TestClient(self.app,base_url=ORIGIN)
        self.addCleanup(other.close)
        login = other.post('/api/v1/auth/login',json={'username':'synthetic-extra','password':PASSWORD},headers={'Origin':ORIGIN})
        self.assertEqual(login.status_code,200,login.text)
        other_id = login.json()['user_id']
        for active in (False,True):
            result = self.client.patch('/api/v1/admin/users/'+other_id,json={'role':'consulta','active':active})
            self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(other.get('/api/v1/auth/me').status_code,401)


    def test_gestao_e_sessao_obedecem_ordem_usuario_antes_de_sessao(self):
        from concurrent.futures import ThreadPoolExecutor
        import time
        from stroop.application.web_administration import update_user
        from stroop.domain.auth import AppUser
        admin = self.signed().json()
        principal = self.rows('SELECT principal_id FROM web_local_credentials')[0][0]
        second = uuid4()
        with psycopg.connect(DSN) as c:
            c.execute("INSERT INTO app_users(issuer,subject,role) VALUES (%s,%s,'administracao')",(LOCAL_ISSUER,str(second)))
            c.execute("INSERT INTO web_local_credentials(principal_id,username,password_hash) SELECT %s,'synthetic-second-admin',password_hash FROM web_local_credentials LIMIT 1",(second,))
        actor = AppUser(LOCAL_ISSUER,str(principal),None,'administracao',True)
        token_hash = self.rows('SELECT token_sha256 FROM web_local_sessions WHERE revoked_at IS NULL')[0][0]
        # Reproduz a fase de login/rotacao que ja segura o usuario, antes da sessao.
        with ThreadPoolExecutor(max_workers=1) as pool:
            with psycopg.connect(DSN) as holder:
                holder.execute('SELECT * FROM public.web_lock_emitter(%s,%s)',(LOCAL_ISSUER,str(principal)))
                update = pool.submit(update_user,DSN,LOCAL_ISSUER,str(principal),role='consulta',
                                     active=True,email=None,actor=actor)
                deadline = time.monotonic()+5
                waiting = False
                while time.monotonic()<deadline:
                    waiting = self.rows("SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE datname=current_database() AND query LIKE 'SELECT public.web_manage_user(%%' AND wait_event_type='Lock')")[0][0]
                    if waiting: break
                    time.sleep(.01)
                self.assertTrue(waiting,'Gestor sintetico deve aguardar row lock do usuario.')
                holder.execute("SET LOCAL lock_timeout='500ms'")
                holder.execute('UPDATE web_local_sessions SET last_activity_at=clock_timestamp() WHERE token_sha256=%s',(token_hash,))
            update.result(timeout=10)
        self.assertEqual(self.client.get('/api/v1/auth/me').status_code,401)

    def test_rehash_credencial_existente_nao_aplica_nova_politica_de_cadastro(self):
        from argon2 import PasswordHasher, Type, extract_parameters
        common = '123456789123456'
        encoded = PasswordHasher(time_cost=2,memory_cost=19456,parallelism=1,type=Type.ID).hash(common)
        with psycopg.connect(DSN) as c:
            c.execute('UPDATE web_local_credentials SET password_hash=%s',(encoded,))
        response = self.login(password=common)
        self.assertEqual(response.status_code,200,response.text)
        replacement = self.rows('SELECT password_hash,credential_version FROM web_local_credentials')[0]
        self.assertNotEqual(replacement[0],encoded)
        self.assertGreaterEqual(extract_parameters(replacement[0]).memory_cost,65536)
        self.assertEqual(replacement[1],1)


class LocalAuthConfigTests(unittest.TestCase):
    def test_modo_local_sem_google_e_sem_ler_arquivos_legados(self):
        from api.config import ConfigurationError
        values = {'API_DATABASE_URL':'postgresql://synthetic:synthetic@127.0.0.1:1/stroop_etapa4_test_local',
                  'APP_ENV':'test','API_PUBLIC_ORIGIN':ORIGIN,'API_SESSION_SECRET':'synthetic-only-session-signature-2026',
                  'OIDC_CLIENT_SECRET_FILE':'/synthetic-nonexistent-should-not-open'}
        config = APIConfig.from_env(values)
        self.assertEqual((config.auth_mode,config.oidc_client_id,config.oidc_client_secret),('local','',''))
        for changes in ({'API_AUTH_MODE':'unknown'}, {'API_AUTH_MODE':'oidc','APP_ENV':'production'}, {'API_AUTH_MODE':'oidc','APP_ENV':'development'}):
            with self.assertRaises(ConfigurationError):
                APIConfig.from_env(values | changes)
