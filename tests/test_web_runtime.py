"""Configuracao e operacoes da imagem API com arquivos inequivocamente sinteticos."""
import argparse
import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from api.config import APIConfig, ConfigurationError, secret_value
from api.runtime import healthcheck, main, migrate, trusted_proxies
from tests.test_api_base import DATABASE, ORIGIN, synthetic_config


def environment():
    return {'API_AUTH_MODE':'oidc', 'API_DATABASE_URL': DATABASE, 'API_PUBLIC_ORIGIN': ORIGIN, 'APP_ENV': 'test',
            'OIDC_CLIENT_ID': 'synthetic-client-id', 'OIDC_CLIENT_SECRET': 'synthetic-client-secret',
            'API_SESSION_SECRET': 'synthetic-session-secret-00000000000000'}


class SecretFilesTests(unittest.TestCase):
    def test_env_existente_preservado_sem_descoberta_de_arquivos(self):
        with patch('api.config.os.open') as opened:
            config = APIConfig.from_env(environment())
        opened.assert_not_called()
        self.assertEqual(config.database_url, DATABASE)
        self.assertEqual(config.read_database_url, '')

    def test_secrets_explicitos_arquivo_utf8_lf_crlf_sem_vazar_no_repr(self):
        values = environment()
        values['API_READ_DATABASE_URL'] = DATABASE
        with tempfile.TemporaryDirectory() as directory:
            for index, key in enumerate(('API_DATABASE_URL', 'API_READ_DATABASE_URL', 'OIDC_CLIENT_ID',
                                         'OIDC_CLIENT_SECRET', 'API_SESSION_SECRET')):
                value = values.pop(key)
                path = Path(directory) / f'synthetic-secret-{index}'
                path.write_bytes((value + ('\r\n' if index % 2 else '\n')).encode())
                values[f'{key}_FILE'] = str(path)
            config = APIConfig.from_env(values)
        self.assertEqual(config.database_url, DATABASE)
        self.assertEqual(config.read_database_url, DATABASE)
        self.assertEqual(config.oidc_client_secret, 'synthetic-client-secret')
        self.assertNotIn('synthetic-secret', repr(config))

    def test_falhas_de_arquivo_fechadas_conflito_utf8_tamanho_ausencia_tipo(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'SYNTHETIC_PRIVATE_PATH'
            cases = [b'', b'\xff', b'a' * 16385]
            for content in cases:
                path.write_bytes(content)
                with self.subTest(content_size=len(content)), self.assertRaises(ConfigurationError) as caught:
                    secret_value({'SECRET_FILE': str(path)}, 'SECRET')
                self.assertEqual(str(caught.exception), 'Configuracao da API ausente ou invalida.')
            for values in ({'SECRET': '', 'SECRET_FILE': str(path)}, {'SECRET_FILE': ''},
                           {'SECRET_FILE': directory}, {'SECRET_FILE': str(path) + '-missing'}):
                with self.subTest(case=list(values)), self.assertRaises(ConfigurationError) as caught:
                    secret_value(values, 'SECRET')
                self.assertNotIn('SYNTHETIC_PRIVATE_PATH', str(caught.exception))
            fifo = Path(directory) / 'synthetic-fifo'
            os.mkfifo(fifo)
            with self.assertRaises(ConfigurationError):
                secret_value({'SECRET_FILE': str(fifo)}, 'SECRET')

    def test_quebra_de_linha_extra_e_valor_invalido_nao_sao_silenciosamente_corrigidos(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic-secret'
            for content in ('synthetic-secret\n\n', 'synthetic secret', 'curto'):
                path.write_text(content)
                values = environment()
                del values['API_SESSION_SECRET']
                values['API_SESSION_SECRET_FILE'] = str(path)
                with self.assertRaises(ConfigurationError):
                    APIConfig.from_env(values)


class RuntimeTests(unittest.TestCase):
    def test_serve_valida_uma_vez_sem_migrations_accesslog_ou_proxy_implicito(self):
        config = synthetic_config()
        application = object()
        with patch('api.runtime.APIConfig.from_env', return_value=config) as configured, \
                patch('api.main.create_app', return_value=application) as factory, \
                patch('uvicorn.run') as run, patch('scripts.migrations.apply_migrations') as migrations:
            self.assertEqual(main(['serve']), 0)
        configured.assert_called_once_with()
        factory.assert_called_once_with(config)
        migrations.assert_not_called()
        self.assertEqual(run.call_args.args, (application,))
        self.assertEqual(run.call_args.kwargs['host'], '0.0.0.0')
        self.assertEqual(run.call_args.kwargs['port'], 8000)
        self.assertFalse(run.call_args.kwargs['access_log'])
        self.assertFalse(run.call_args.kwargs['proxy_headers'])
        self.assertEqual(run.call_args.kwargs['forwarded_allow_ips'], '')
        self.assertFalse(run.call_args.kwargs['server_header'])

    def test_serve_confianca_proxy_somente_opt_in_e_lista_fechada(self):
        for setting in ('127.0.0.1,10.3.0.0/24,::1', '*'):
            with patch('api.runtime.APIConfig.from_env', return_value=synthetic_config()), \
                    patch('uvicorn.run') as run:
                self.assertEqual(main(['serve', '--forwarded-allow-ips', setting]), 0)
            self.assertTrue(run.call_args.kwargs['proxy_headers'])
            self.assertEqual(run.call_args.kwargs['forwarded_allow_ips'], setting)
        for setting in ('', 'proxy', 'https://proxy', '127.0.0.1,', '127.0.0.1, *', '*/0', '999.2.3.4'):
            with self.subTest(setting=setting), self.assertRaises(argparse.ArgumentTypeError):
                trusted_proxies(setting)

    def test_inicializacao_invalida_nao_imprime_segredo_traceback_nem_inicia_uvicorn(self):
        output = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), patch('uvicorn.run') as run, contextlib.redirect_stderr(output):
            self.assertEqual(main(['serve']), 1)
        run.assert_not_called()
        self.assertNotIn('Traceback', output.getvalue())
        self.assertIn('configuracao indisponivel ou invalida', output.getvalue())

    def test_migrate_usa_somente_credencial_ddl_explicita_sem_config_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic-migrator'
            path.write_text(DATABASE + '\n')
            output = io.StringIO()
            with patch('scripts.migrations.apply_migrations', return_value=['0001_synthetic.sql']) as apply, \
                    contextlib.redirect_stdout(output), patch('api.runtime.APIConfig.from_env') as config:
                self.assertEqual(migrate({'API_MIGRATION_DATABASE_URL_FILE': str(path)}), 0)
            config.assert_not_called()
            apply.assert_called_once_with(DATABASE)
            self.assertEqual(output.getvalue(), 'Migrations aplicadas: 1\n')
        for values in ({'API_DATABASE_URL': DATABASE}, {'API_MIGRATION_DATABASE_URL': 'sqlite:///SYNTHETIC_SECRET'},
                       {'API_MIGRATION_DATABASE_URL': 'postgresql://'},
                       {'API_MIGRATION_DATABASE_URL': DATABASE, 'API_MIGRATION_DATABASE_URL_FILE': '/missing'}):
            output = io.StringIO()
            with patch('scripts.migrations.apply_migrations') as apply, contextlib.redirect_stderr(output):
                self.assertEqual(migrate(values), 1)
            apply.assert_not_called()
            self.assertEqual(output.getvalue(), 'Nao foi possivel aplicar as migrations da API.\n')

    def test_migrate_falha_fechada_sem_dsn_e_sem_uvicorn(self):
        output = io.StringIO()
        with patch.dict(os.environ, {'API_MIGRATION_DATABASE_URL': DATABASE}, clear=True), \
                patch('scripts.migrations.apply_migrations', side_effect=RuntimeError('SYNTHETIC_SECRET')), \
                patch('uvicorn.run') as run, contextlib.redirect_stderr(output):
            self.assertEqual(main(['migrate']), 1)
        run.assert_not_called()
        self.assertNotIn('SYNTHETIC_SECRET', output.getvalue())

    def test_healthcheck_host_publico_porta_ipv6_sem_proxyenv_nem_leitura_secrets(self):
        for origin, host in ((ORIGIN, 'synthetic.example.test'), ('https://127.0.0.1:4373', '127.0.0.1:4373'),
                             ('https://[::1]:443/', '[::1]')):
            response = MagicMock()
            response.status = 200
            response.read.return_value = b'{"status":"ready"}'
            response.__enter__.return_value = response
            opener = MagicMock()
            opener.open.return_value = response
            with patch('api.runtime.build_opener', return_value=opener) as build, \
                    patch('api.runtime.secret_value') as secret:
                self.assertEqual(healthcheck({'API_PUBLIC_ORIGIN': origin, 'HTTP_PROXY': 'http://externo.invalid'}), 0)
            secret.assert_not_called()
            self.assertEqual(build.call_args.args[0].proxies, {})
            request = opener.open.call_args.args[0]
            self.assertEqual(request.full_url, 'http://127.0.0.1:8000/health/ready')
            self.assertEqual(request.get_header('Host'), host)
            self.assertEqual(opener.open.call_args.kwargs['timeout'], 4)
            response.read.assert_called_once_with(1025)

    def test_healthcheck_falhas_silenciosas_sem_bypass_de_prontidao(self):
        for origin in ('', 'http://synthetic.example.test', ORIGIN + '/path', 'https://user:secret@host',
                       'https://host?x=1', 'https://host:bad', 'https://bad host'):
            with patch('api.runtime.build_opener') as opened:
                self.assertEqual(healthcheck({'API_PUBLIC_ORIGIN': origin}), 1)
            opened.assert_not_called()
        for status, body in ((503, b'{"status":"ready"}'), (200, b'{"status":"ok"}'), (200, b'not-json')):
            response = MagicMock(status=status)
            response.__enter__.return_value = response
            response.read.return_value = body
            with patch('api.runtime.build_opener') as build:
                build.return_value.open.return_value = response
                self.assertEqual(healthcheck({'API_PUBLIC_ORIGIN': ORIGIN}), 1)
        with patch('api.runtime.build_opener') as build:
            build.return_value.open.side_effect = HTTPError('http://127.0.0.1', 503, 'synthetic', {}, None)
            self.assertEqual(healthcheck({'API_PUBLIC_ORIGIN': ORIGIN}), 1)
