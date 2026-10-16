"""Garantias do runner CI; Git temporario, sem Docker, banco ou dados locais."""
from pathlib import Path
import contextlib
import io
import os
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import verify_web_ci as ci


class WebCIRunnerTests(unittest.TestCase):
    def test_database_descartavel_local_explicito_sem_refletir_credencial(self):
        ci.database_guard('postgresql://synthetic:synthetic-only@127.0.0.1:5432/stroop_etapa4_test_ci')
        for value in ('', 'postgresql://synthetic:SECRET@remote.invalid:5432/stroop_etapa4_test_ci',
                      'postgresql://synthetic:SECRET@127.0.0.1:5432/production',
                      'postgresql://synthetic:SECRET@127.0.0.1:5432/stroop_etapa4_test_ci?options=unsafe',
                      'postgresql://synthetic:SECRET@127.0.0.1:bad/stroop_etapa4_test_ci'):
            with self.subTest(value=value), self.assertRaises(ci.CheckFailure) as caught:
                ci.database_guard(value)
            self.assertNotIn('SECRET', str(caught.exception))

    def test_fontes_git_excluem_dados_e_ignorados_sem_ler_conteudo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '--quiet'], cwd=root, check=True)
            for name in ('source.py', 'Dockerfile', 'data/tracked.csv', 'database/tracked.sqlite', '.env.example'):
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('SINTETICO')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            (root / 'untracked.py').write_text('SINTETICO')
            self.assertEqual(set(ci.tracked_sources(root)), {Path('source.py'), Path('Dockerfile'), Path('.env.example')})

    def test_env_operacional_versionado_bloqueia_antes_de_abrir(self):
        result = SimpleNamespace(returncode=0, stdout=b'source.py\0.env\0')
        with patch.object(ci.subprocess, 'run', return_value=result), self.assertRaises(ci.CheckFailure), \
                patch.object(Path, 'read_text', side_effect=AssertionError('Nao pode abrir ambiente')):
            ci.tracked_sources()

    def test_chaves_versionadas_bloqueiam_por_nome_sem_ler(self):
        for name in ('key.pem', 'private.key', 'secret.p12', 'certificate.pfx'):
            result = SimpleNamespace(returncode=0, stdout=name.encode() + b'\0')
            with self.subTest(name=name), patch.object(ci.subprocess, 'run', return_value=result), \
                    self.assertRaises(ci.CheckFailure):
                ci.tracked_sources()

    def test_symlink_versionado_nao_copia_arquivo_externo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'link.py').symlink_to('/nonexistent-synthetic')
            result = SimpleNamespace(returncode=0, stdout=b'link.py\0')
            with patch.object(ci.subprocess, 'run', return_value=result), self.assertRaises(ci.CheckFailure):
                ci.tracked_sources(root)

    def test_falha_de_comando_nao_reflete_argumentos_e_impede_continuar(self):
        with patch.object(ci.subprocess, 'run', return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(ci.CheckFailure) as caught:
                ci.run(['synthetic-command', 'PRIVATE_VALUE'])
            self.assertNotIn('PRIVATE_VALUE', str(caught.exception))
        with patch.object(ci, 'scan_sources', side_effect=ci.CheckFailure('Falha sintetica')), \
                patch.object(ci, 'python_suite') as suite, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ci.main(['all']), 1)
            suite.assert_not_called()

    def test_scanner_imprime_somente_path_linha_regra_e_descarta_saida_bruta(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'source.py').write_text('value = 42\n')
            result = SimpleNamespace(returncode=1)
            def scan_result(command, **kwargs):
                report = next(command[index + 1].split(':/report:rw')[0] for index, item in enumerate(command)
                              if item == '--volume' and command[index + 1].endswith(':/report:rw'))
                (Path(report) / 'findings.txt').write_text('PRIVATE_VALUE\n/scan/source.py\t8\tgithub-pat\n')
                return result
            stream = io.StringIO()
            with patch.object(ci, 'tracked_sources', return_value=[Path('source.py')]), \
                    patch.object(ci.subprocess, 'run', side_effect=scan_result), \
                    contextlib.redirect_stderr(stream), self.assertRaises(ci.SecretFinding):
                ci.scan_sources(root)
            self.assertIn('source.py:8 regra=github-pat', stream.getvalue())
            self.assertNotIn('PRIVATE_VALUE', stream.getvalue())

    def test_self_test_nao_confunde_indisponibilidade_com_deteccao(self):
        with patch.object(ci, 'run'), patch.object(ci, 'scan_sources', side_effect=[None, ci.CheckFailure('Infra sintetica')]), \
                self.assertRaises(ci.CheckFailure):
            ci.secret_self_test()

    def test_discovery_aceita_pasta_tests_sem_init(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'tests').mkdir()
            (root / 'tests/test_ci_synthetic_discovery.py').write_text(
                'import unittest\nclass Synthetic(unittest.TestCase):\n'
                '    def test_one(self): self.assertEqual(1, 1)\n')
            output = io.StringIO()
            with patch.object(ci, 'ROOT', root), \
                    patch.object(ci.unittest, 'defaultTestLoader', unittest.TestLoader()), \
                    patch.dict(os.environ, {'TEST_DATABASE_URL': 'postgresql://synthetic@127.0.0.1:5432/stroop_etapa4_test_ci'}), \
                    contextlib.redirect_stderr(output):
                self.assertEqual(ci.python_suite(), 0)
            self.assertIn('Ran 1 test', output.getvalue())
            self.assertFalse((root / 'tests/__init__.py').exists())

    def test_skips_e_falhas_python_bloqueiam_entrega(self):
        for success, skipped, expected in ((True, [], 0), (True, [('synthetic', 'skip')], 1), (False, [], 1)):
            result = SimpleNamespace(skipped=skipped, wasSuccessful=lambda: success)
            with self.subTest(success=success, skipped=bool(skipped)), \
                    patch.dict(os.environ, {'TEST_DATABASE_URL': 'postgresql://synthetic@127.0.0.1:5432/stroop_etapa4_test_ci'}), \
                    patch.object(ci.unittest.defaultTestLoader, 'discover', return_value=unittest.TestSuite()), \
                    patch.object(ci.unittest, 'TextTestRunner') as runner, contextlib.redirect_stderr(io.StringIO()):
                runner.return_value.run.return_value = result
                self.assertEqual(ci.python_suite(), expected)
