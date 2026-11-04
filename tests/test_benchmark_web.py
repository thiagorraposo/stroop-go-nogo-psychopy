import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.benchmark_web import main, percentile, summarize
from scripts.smoke_web_compose import SmokeFailure, WebComposeSmoke


class BenchmarkWebTests(unittest.TestCase):
    def test_rejeicoes_e_resposta_invalida_nao_contam_como_sucesso(self):
        records = [
            {'status': 200, 'valid': True, 'elapsed_ms': 10},
            {'status': 200, 'valid': True, 'elapsed_ms': 200},
            {'status': 200, 'valid': False, 'elapsed_ms': 1},
            {'status': 429, 'valid': False, 'elapsed_ms': 2},
            {'status': 'transport_error', 'valid': False, 'elapsed_ms': 3000},
        ]
        result = summarize(records, 10, 1, 10)
        self.assertEqual(result['successful_requests'], 2)
        self.assertEqual(result['successful_rps'], .2)
        self.assertEqual(result['success_latency_ms']['p95'], 200)
        self.assertEqual(result['invalid_200_responses'], 1)
        self.assertEqual(result['scheduled_requests'], 10)
        self.assertFalse(result['all_scheduled_succeeded'])
        self.assertEqual(result['statuses']['429'], 1)

    def test_cauda_percentil_nao_e_media_nem_interpolacao_para_baixo(self):
        self.assertEqual(percentile(list(range(1, 21)), .95), 19)
        self.assertIsNone(percentile([], .95))
        summary = summarize([], 5, 1, 5)
        self.assertIsNone(summary['success_latency_ms']['p95'])
        self.assertFalse(summary['all_scheduled_succeeded'])

    def test_niveis_invalidos_nao_iniciam_docker_ou_gravam_saida(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'synthetic.json'
            for levels in ('0', '33', '4,1', '1,1', 'abc', ''):
                with self.subTest(levels=levels), patch('scripts.benchmark_web.WebComposeSmoke') as stack:
                    with self.assertRaises(SystemExit), patch('sys.stderr'):
                        main(['--levels', levels, '--output', str(output)])
                    stack.assert_not_called()
                    self.assertFalse(output.exists())

    def test_evidencia_existente_nao_e_sobrescrita(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'synthetic.json'
            output.write_text(json.dumps({'synthetic': 'preserve'}))
            with patch('scripts.benchmark_web.WebComposeSmoke') as stack:
                with self.assertRaises(FileExistsError):
                    main(['--output', str(output)])
                stack.assert_not_called()
            self.assertEqual(json.loads(output.read_text()), {'synthetic': 'preserve'})

    def test_imagem_invalida_nao_alcanca_docker_nem_dockerfile(self):
        with tempfile.TemporaryDirectory() as directory:
            for image in ('image\nRUN unsafe', '--privileged', 'image:tag with-space'):
                with self.subTest(image=image), patch('scripts.smoke_web_compose._run') as run:
                    with self.assertRaises(SmokeFailure):
                        WebComposeSmoke(Path(directory), False, api_image=image)
                    run.assert_not_called()
