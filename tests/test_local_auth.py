"""Credenciais sinteticas e PG descartavel; sem dados/servicos operacionais."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import os
import subprocess
import sys
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

import psycopg
from argon2 import extract_parameters, Type

from scripts.migrations import apply_migrations, MIGRATIONS_DIR
from stroop.application import local_auth as application
from stroop.domain.local_auth import InvalidCredential, LOCAL_ISSUER, normalize_username, validate_password
from stroop.persistence import local_auth as persistence
from stroop.security.passwords import hash_password, verify_password, needs_rehash

# So existe como fixture sintetica; nao e credencial default de qualquer app.
PASSWORD = '  Sintetica-ç-2026 com espacos  '
OTHER = 'Outra frase sintetica 2026!'
DSN = os.environ.get('TEST_DATABASE_URL', '')


def digest(value):
    return sha256(value.encode()).hexdigest()


class LocalPolicyTests(unittest.TestCase):
    def test_normalizacao_e_senha_integra(self):
        self.assertEqual(normalize_username('  SYNTHETIC.User-1_ '), 'synthetic.user-1_')
        for value in ('', 'a b', 'á', 'K', 'a' * 65):
            with self.assertRaises(InvalidCredential): normalize_username(value)
        self.assertEqual(validate_password(PASSWORD), PASSWORD)
        for value in ('a'*14, 'a'*129, '123456789123456', 'QWERTYUIOPASDFGHJKL', 'passwordpassword', '1'*20, '\ud800'*20):
            with self.assertRaises(InvalidCredential): validate_password(value)

    def test_argon2_salt_parametros_verificacao_e_sem_trim(self):
        one, two = hash_password(PASSWORD), hash_password(PASSWORD)
        self.assertNotEqual(one, two)
        parameters = extract_parameters(one)
        self.assertEqual(parameters.type, Type.ID)
        self.assertGreaterEqual(parameters.memory_cost, 19456)
        self.assertGreaterEqual(parameters.time_cost, 2)
        self.assertEqual(parameters.parallelism, 1)
        self.assertTrue(verify_password(one, PASSWORD))
        self.assertFalse(verify_password(one, PASSWORD.strip()))
        self.assertFalse(verify_password(None, PASSWORD))
        self.assertFalse(needs_rehash(one))

    def test_verificacao_limita_concorrencia_e_falha_segura(self):
        from stroop.security.passwords import VERIFY_SLOTS, PasswordServiceUnavailable
        VERIFY_SLOTS.acquire()
        VERIFY_SLOTS.acquire()
        try:
            with self.assertRaises(PasswordServiceUnavailable): verify_password(None, PASSWORD)
            with self.assertRaises(PasswordServiceUnavailable): hash_password(PASSWORD)
        finally:
            VERIFY_SLOTS.release()
            VERIFY_SLOTS.release()
        with self.assertRaises(PasswordServiceUnavailable): verify_password('invalid-encoded-hash', PASSWORD)

    def test_cli_recusa_stdin_sem_eco_ou_senha_em_argumentos(self):
        from scripts.gerenciar_conta_local import main
        with patch('sys.stdin.isatty', return_value=False), patch('sys.stderr'):
            self.assertEqual(main(['bootstrap', 'synthetic']), 1)
        with self.assertRaises(SystemExit), patch('sys.stderr'):
            main(['bootstrap', 'synthetic', '--password', PASSWORD])


@unittest.skipUnless(DSN, 'TEST_DATABASE_URL nao configurada')
class LocalPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not psycopg.conninfo.conninfo_to_dict(DSN).get('dbname','').startswith('stroop_etapa4_test'):
            raise RuntimeError('PG descartavel obrigatorio')

    def setUp(self):
        with psycopg.connect(DSN, autocommit=True) as c:
            c.execute('DROP SCHEMA public CASCADE')
            c.execute('CREATE SCHEMA public')
        apply_migrations(DSN)

    def bootstrap(self):
        self.assertTrue(application.provision(DSN, 'Synthetic', PASSWORD))

    def login(self, token='synthetic-token', username='synthetic', password=PASSWORD, bucket='synthetic', previous=None):
        return application.authenticate(DSN, username, password, digest(bucket), digest(token), previous)

    def rows(self, query, args=()):
        with psycopg.connect(DSN) as c:
            return c.execute(query, args).fetchall()

    def test_upgrade_preserva_identidades_e_vinculos_historicos(self):
        with psycopg.connect(DSN, autocommit=True) as c:
            c.execute('DROP SCHEMA public CASCADE'); c.execute('CREATE SCHEMA public')
        with tempfile.TemporaryDirectory() as directory:
            for path in MIGRATIONS_DIR.glob('*.sql'):
                if path.name[:4] < '0012':
                    Path(directory, path.name).write_text(path.read_text())
            apply_migrations(DSN, Path(directory))
        project = uuid4()
        with psycopg.connect(DSN) as c:
            c.execute("INSERT INTO app_users(issuer,subject,role) VALUES ('https://accounts.google.com','synthetic-old','administracao')")
            c.execute("INSERT INTO web_projects(project_id,code,name,created_by_issuer,created_by_subject) VALUES (%s,'OLD','Synthetic old','https://accounts.google.com','synthetic-old')", (project,))
            c.execute("INSERT INTO web_project_members(project_id,issuer,subject) VALUES (%s,'https://accounts.google.com','synthetic-old')", (project,))
        self.assertEqual(
            apply_migrations(DSN),
            [
                '0012_local_authentication.sql',
                '0013_local_user_management.sql',
                '0014_central_patients_evaluators.sql',
            ],
        )
        self.bootstrap()
        self.assertEqual(self.rows('SELECT issuer,subject FROM web_project_members'), [('https://accounts.google.com','synthetic-old')])
        self.assertEqual(self.rows('SELECT created_by_issuer,created_by_subject FROM web_projects'), [('https://accounts.google.com','synthetic-old')])
        self.assertEqual(self.rows('SELECT count(*) FROM app_users')[0][0], 2)
        self.assertEqual(apply_migrations(DSN), [])

    def test_bootstrap_concorrente_e_recuperacao_atomica(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: application.provision(DSN, 'synthetic', PASSWORD), range(2)))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(self.rows('SELECT count(*) FROM web_project_members')[0][0], 0)
        self.assertEqual(self.login()[0], 'success')
        self.assertTrue(application.provision(DSN, 'synthetic', OTHER, recover=True))
        self.assertIsNotNone(self.rows('SELECT revoked_at FROM web_local_sessions')[0][0])
        self.assertEqual(self.rows('SELECT credential_version FROM web_local_credentials')[0][0], 2)
        self.assertEqual(self.login('old')[0], 'invalid')
        self.assertEqual(self.login('new', password=OTHER)[0], 'success')
        self.assertEqual(self.rows('SELECT count(*) FROM web_project_members')[0][0], 0)

    def test_login_generico_hash_cookie_e_limite_persistente(self):
        self.bootstrap()
        for username in ('synthetic', 'missing'):
            for index in range(5):
                self.assertEqual(self.login(str(uuid4()), username=username, password=OTHER, bucket=username)[0], 'invalid')
            result = self.login(str(uuid4()), username=username, bucket=username)
            self.assertEqual(result[0], 'limited')
            self.assertGreaterEqual(result[1], 1)
        self.assertEqual(self.rows('SELECT count(*) FROM web_local_sessions')[0][0], 0)
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_auth_limits SET window_started_at=clock_timestamp()-INTERVAL '16 minutes'")
        status, details = self.login()
        self.assertEqual(status, 'success')
        principal, role, expires = details
        self.assertEqual(role, 'administracao')
        self.assertEqual(self.rows('SELECT token_sha256 FROM web_local_sessions'), [(digest('synthetic-token'),)])
        self.assertNotIn(PASSWORD, str(self.rows('SELECT * FROM web_local_credentials')))
        self.assertLess(expires.timestamp()-time.time(), 1801)
        self.assertEqual(self.login('replacement', previous=digest('synthetic-token'))[0], 'success')
        self.assertIsNotNone(self.rows('SELECT revoked_at FROM web_local_sessions WHERE token_sha256=%s', (digest('synthetic-token'),))[0][0])

    def test_rotacao_rollback_e_login_concorrente(self):
        self.bootstrap()
        self.login()
        # Falha apos atualizar credencial deve restaurar hash/versao e sessoes.
        original = persistence._event
        def failing(c, action, principal=None):
            if action == 'password_change':
                c.execute('SELECT 1/0')
            original(c, action, principal)
        with patch.object(persistence, '_event', side_effect=failing):
            with self.assertRaises(persistence.PersistenceError):
                application.change_password(DSN, digest('synthetic-token'), PASSWORD, OTHER)
        self.assertEqual(self.rows('SELECT credential_version FROM web_local_credentials'), [(1,)])
        self.assertEqual(self.rows('SELECT revoked_at FROM web_local_sessions'), [(None,)])
        with ThreadPoolExecutor(max_workers=2) as pool:
            login = pool.submit(self.login, 'concurrent')
            rotate = pool.submit(application.change_password, DSN, digest('synthetic-token'), PASSWORD, OTHER)
            self.assertTrue(rotate.result())
            self.assertIn(login.result()[0], ('success','invalid'))
        # Qualquer login antigo que venceu a corrida foi revogado pelo commit.
        self.assertEqual(self.rows('''SELECT count(*) FROM web_local_sessions s JOIN web_local_credentials c USING(principal_id)
            WHERE s.revoked_at IS NULL AND s.credential_version<>c.credential_version'''), [(0,)])
        self.assertEqual(self.login('fresh', password=OTHER)[0], 'success')

    def test_grants_writer_nao_cria_conta_reader_nao_le_hash(self):
        from scripts.provision_web_database import provision
        from psycopg.conninfo import conninfo_to_dict, make_conninfo
        self.bootstrap()
        parts = conninfo_to_dict(DSN)
        # Roles unicos por ensaio, sem reaproveitar papeis operacionais.
        suffix = uuid4().hex[:12]
        writer = make_conninfo(**(parts | {'user':f'm6_writer_{suffix}', 'password':'synthetic-role-password'}))
        reader = make_conninfo(**(parts | {'user':f'm6_reader_{suffix}', 'password':'synthetic-role-password'}))
        # Provisioner exige URIs: as de conexao do teste sao inequivocamente sinteticas.
        def uri(user):
            return f"postgresql://{user}:synthetic-role-password@{parts['host']}:{parts['port']}/{parts['dbname']}"
        writer_uri, reader_uri = uri(f'm6_writer_{suffix}'), uri(f'm6_reader_{suffix}')
        with psycopg.connect(DSN) as c:
            c.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
            c.execute('REVOKE CREATE ON DATABASE '+parts['dbname']+' FROM PUBLIC')
        provision({'API_MIGRATION_DATABASE_URL':DSN,'API_DATABASE_URL':writer_uri,'API_READ_DATABASE_URL':reader_uri})
        for dsn, query in ((reader, 'SELECT password_hash FROM web_local_credentials'),
                           (writer, "DELETE FROM web_local_credentials"),
                           (writer, "CREATE TABLE synthetic_unauthorized(id int)"),
                           (writer, "UPDATE app_users SET active=FALSE")):
            with psycopg.connect(dsn) as c:
                with self.assertRaises(psycopg.errors.InsufficientPrivilege): c.execute(query)
        self.assertEqual(application.authenticate(writer, 'synthetic', PASSWORD, digest('writer'), digest('writer-session'))[0], 'success')
        self.assertEqual(application.session_context(writer,digest('writer-session'),'manage_users')[0], 'success')
        self.assertTrue(persistence.record_activity(writer,digest('writer-session')))
        self.assertTrue(application.change_password(writer, digest('writer-session'), PASSWORD, OTHER))

    def test_sessao_inatividade_teto_versao_bloqueio_e_logout(self):
        self.bootstrap()
        self.login()
        token_hash = digest('synthetic-token')
        def context():
            return application.session_context(DSN, token_hash, 'view_dashboard')
        self.assertEqual(context()[0], 'success')
        before = self.rows('SELECT last_activity_at FROM web_local_sessions')[0][0]
        context()
        self.assertEqual(self.rows('SELECT last_activity_at FROM web_local_sessions')[0][0], before)
        self.assertTrue(persistence.record_activity(DSN, token_hash))
        self.assertGreater(self.rows('SELECT last_activity_at FROM web_local_sessions')[0][0], before)
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_sessions SET created_at=clock_timestamp()-INTERVAL '31 minutes',last_activity_at=clock_timestamp()-INTERVAL '30 minutes',absolute_expires_at=clock_timestamp()+INTERVAL '7 hours'")
        self.assertEqual(context()[0], 'invalid')
        self.assertFalse(persistence.record_activity(DSN, token_hash))
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_sessions SET last_activity_at=CURRENT_TIMESTAMP,created_at=CURRENT_TIMESTAMP-INTERVAL '8 hours',absolute_expires_at=CURRENT_TIMESTAMP")
        self.assertEqual(context()[0], 'invalid')
        self.login('new')
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_credentials SET credential_version=credential_version+1")
        self.assertEqual(application.session_context(DSN,digest('new'),'view_dashboard')[0], 'invalid')
        self.login('current')
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE app_users SET active=FALSE WHERE issuer=%s", (LOCAL_ISSUER,))
        self.assertEqual(application.session_context(DSN,digest('current'),'view_dashboard')[0], 'invalid')
        self.assertEqual(self.login('blocked')[0], 'invalid')
        persistence.revoke(DSN, digest('current'))
        persistence.revoke(DSN, digest('current'))
        self.assertIsNotNone(self.rows('SELECT revoked_at FROM web_local_sessions WHERE token_sha256=%s',(digest('current'),))[0][0])

    def test_falhas_concorrentes_e_perfil_sem_escalada(self):
        self.bootstrap()
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda index: self.login(str(index), password=OTHER), range(6)))
        self.assertEqual(sorted(result[0] for result in results), ['invalid']*5+['limited'])
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE app_users SET role='consulta' WHERE issuer=%s", (LOCAL_ISSUER,))
        self.assertEqual(self.login('reader', bucket='reader')[0], 'success')
        self.assertEqual(application.session_context(DSN,digest('reader'),'view_dashboard')[0], 'success')
        self.assertEqual(application.session_context(DSN,digest('reader'),'manage_users')[0], 'forbidden')

    def test_origem_conta_todas_tentativas_sem_trabalho_criptografico_apos_limite(self):
        self.bootstrap()
        origin = digest('synthetic-origin')
        for index in range(20):
            status, _ = application.authenticate(DSN, 'synthetic', PASSWORD,
                digest('synthetic'), digest(f'origin-session-{index}'), origin_bucket=origin)
            self.assertEqual(status, 'success')
        with patch.object(application, 'verify_password', side_effect=AssertionError('nao verificar')):
            status, retry = application.authenticate(DSN, 'missing', PASSWORD,
                digest('missing'), digest('limited-origin'), origin_bucket=origin)
        self.assertEqual(status, 'limited')
        self.assertGreaterEqual(retry, 1)
        self.assertLessEqual(retry, 60)
        self.assertEqual(self.rows('SELECT count(*) FROM web_local_auth_limits WHERE bucket_sha256=%s',
                                   (digest('missing'),)), [(0,)])
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_auth_limits SET window_started_at=clock_timestamp()-INTERVAL '61 seconds' WHERE bucket_sha256=%s", (origin,))
        self.assertEqual(application.authenticate(DSN, 'synthetic', PASSWORD,
            digest('synthetic'), digest('origin-renewed'), origin_bucket=origin)[0], 'success')

    def test_origem_concorrente_e_admissao_cardinalidade_limitada(self):
        # Testa o contador persistente real; nao substitui verificacao de senha.
        with ThreadPoolExecutor(max_workers=6) as pool:
            retries = list(pool.map(lambda index: persistence._prepare_attempt(DSN,
                digest(f'identity-{index}'), digest('shared-origin'), 3, 60), range(6)))
        self.assertEqual(retries.count(None), 3)
        self.assertEqual(self.rows('SELECT failure_count FROM web_local_auth_limits WHERE bucket_sha256=%s',
                                   (digest('shared-origin'),)), [(3,)])
        self.assertEqual(self.rows('SELECT count(*) FROM web_local_auth_limits'), [(4,)])
        with patch.object(persistence, 'MAX_LIMIT_BUCKETS', 4):
            self.assertEqual(persistence._prepare_attempt(DSN, digest('new-identity'), None, 20, 60), 60)
            admitted = self.rows('SELECT bucket_sha256 FROM web_local_auth_limits WHERE bucket_sha256<>%s LIMIT 1',
                                 (digest('shared-origin'),))[0][0]
            self.assertIsNone(persistence._prepare_attempt(DSN, admitted, None, 20, 60))
            with psycopg.connect(DSN) as c:
                c.execute("UPDATE web_local_auth_limits SET window_started_at=clock_timestamp()-INTERVAL '25 hours'")
            self.assertIsNone(persistence._prepare_attempt(DSN, digest('new-identity'), None, 20, 60))
            self.assertEqual(self.rows('SELECT count(*) FROM web_local_auth_limits'), [(1,)])

    def test_troca_e_login_compartilham_falhas_sem_hash_antecipado(self):
        self.bootstrap()
        self.login()
        for index in range(4):
            self.assertEqual(self.login(f'wrong-login-{index}', password=OTHER)[0], 'invalid')
        with patch.object(application, 'hash_password', side_effect=AssertionError('nao gerar hash')):
            self.assertEqual(application.change_password_limited(DSN, digest('synthetic-token'), OTHER,
                PASSWORD, bucket_for_username=digest, origin_bucket=digest('password-origin'))[0], 'invalid')
            status, retry = application.change_password_limited(DSN, digest('synthetic-token'), PASSWORD,
                OTHER, bucket_for_username=digest, origin_bucket=digest('password-origin'))
            self.assertEqual(status, 'limited')
            self.assertGreaterEqual(retry, 1)
        self.assertEqual(self.login('still-limited')[0], 'limited')
        self.assertEqual(self.rows('SELECT credential_version FROM web_local_credentials'), [(1,)])
        with psycopg.connect(DSN) as c:
            c.execute("UPDATE web_local_auth_limits SET window_started_at=clock_timestamp()-INTERVAL '16 minutes'")
        self.assertEqual(application.change_password_limited(DSN, digest('synthetic-token'), PASSWORD,
            OTHER, bucket_for_username=digest, origin_bucket=digest('password-origin'))[0], 'success')
        self.assertEqual(self.login('new-password', password=OTHER)[0], 'success')
        for index in range(4):
            self.assertEqual(application.change_password_limited(DSN, digest('new-password'), PASSWORD,
                OTHER, bucket_for_username=digest, origin_bucket=digest('password-origin'))[0], 'invalid')
        self.assertEqual(self.login('fifth', password=PASSWORD)[0], 'invalid')
        self.assertEqual(application.change_password_limited(DSN, digest('new-password'), OTHER,
            PASSWORD, bucket_for_username=digest, origin_bucket=digest('password-origin'))[0], 'limited')

    def test_troca_rejeita_politica_antes_contadores_e_nao_hash_sessao_invalida(self):
        self.bootstrap()
        self.login()
        with patch.object(application, 'hash_password', side_effect=AssertionError('nao gerar hash')):
            with self.assertRaises(InvalidCredential):
                application.change_password_limited(DSN, digest('synthetic-token'), PASSWORD,
                    'passwordpassword', bucket_for_username=digest, origin_bucket=digest('origin'))
            self.assertFalse(application.change_password(DSN, digest('missing'), PASSWORD, OTHER))
        self.assertEqual(self.rows('SELECT count(*) FROM web_local_auth_limits'), [(1,)])

    def test_cap_concorrente_e_falha_cripto_nao_apaga_contador_origem(self):
        self.bootstrap()
        with patch.object(persistence, 'MAX_LIMIT_BUCKETS', 4):
            with ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(lambda index: persistence._prepare_attempt(DSN,
                    digest(f'cap-identity-{index}'), digest(f'cap-origin-{index}'), 20, 60), range(6)))
            self.assertEqual(results.count(None), 2)
            self.assertEqual(self.rows('SELECT count(*) FROM web_local_auth_limits'), [(4,)])
        with patch.object(application, 'verify_password', side_effect=RuntimeError('synthetic failure')):
            with self.assertRaises(RuntimeError):
                application.authenticate(DSN, 'synthetic', PASSWORD, digest('synthetic'),
                    digest('no-session'), origin_bucket=digest('failure-origin'))
        self.assertEqual(self.rows('SELECT failure_count FROM web_local_auth_limits WHERE bucket_sha256=%s',
                                   (digest('failure-origin'),)), [(1,)])
        self.assertEqual(self.rows('SELECT failure_count FROM web_local_auth_limits WHERE bucket_sha256=%s',
                                   (digest('synthetic'),)), [(0,)])
        self.assertEqual(self.rows('SELECT count(*) FROM web_local_sessions'), [(0,)])


    def test_limite_compartilhado_entre_processos_sem_senha_em_argv(self):
        self.bootstrap()
        program = """import json, os, sys
from hashlib import sha256
from stroop.application.local_auth import authenticate
v=json.load(sys.stdin)
h=lambda s:sha256(s.encode()).hexdigest()
r=authenticate(os.environ['TEST_DATABASE_URL'], 'synthetic', v['password'],h('synthetic-multiprocess'), h(v['token']))
print(r[0])
"""
        # Processos independentes, conexoes e estado em PG, entrada sintetica via pipe.
        for index in range(6):
            result = subprocess.run([sys.executable, '-c', program], input=json.dumps({'password':OTHER,'token':str(uuid4())}),
                text=True, capture_output=True, check=True,
                env={'TEST_DATABASE_URL':DSN, 'PATH':os.environ.get('PATH','')}, timeout=20)
            self.assertEqual(result.stdout.strip(), 'invalid' if index < 5 else 'limited')
        self.assertEqual(self.rows('SELECT failure_count FROM web_local_auth_limits WHERE bucket_sha256=%s',
                                  (digest('synthetic-multiprocess'),)),[(5,)])
