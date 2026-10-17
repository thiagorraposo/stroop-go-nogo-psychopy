import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.monitor_web import check


class MonitorWebTests(unittest.TestCase):
    def test_projeto_invalido_nao_executa_comando(self):
        with tempfile.NamedTemporaryFile() as environment, patch('scripts.monitor_web.command') as run:
            result = check(Path(environment.name), 'bad;command')
        self.assertTrue(result['alert'])
        run.assert_not_called()

    def test_indisponibilidade_nao_reflete_erro_secreto(self):
        with tempfile.NamedTemporaryFile() as environment, patch('scripts.monitor_web.command',
                side_effect=RuntimeError('SYNTHETIC_PRIVATE_VALUE')):
            result = check(Path(environment.name), 'synthetic-monitor')
        self.assertEqual(result['status'], 'unavailable')
        self.assertNotIn('SYNTHETIC_PRIVATE_VALUE', json.dumps(result))
        self.assertNotIn('counts', result)

    def test_banco_indisponivel_dispara_alerta_sem_executar_consulta(self):
        replies = []
        for healthy in (False, True, True):
            replies.extend(['a' * 64, json.dumps([{'State': {'Running': True,
                'Health': {'Status': 'healthy' if healthy else 'unhealthy'}}}])])
        with tempfile.NamedTemporaryFile() as environment, patch('scripts.monitor_web.command',
                side_effect=replies) as run:
            result = check(Path(environment.name), 'synthetic-monitor')
        self.assertTrue(result['alert'])
        self.assertNotIn('counts', result)
        self.assertEqual(run.call_count, 6)

    def test_contagens_nao_podem_incluir_campos_identificaveis(self):
        replies = []
        for _ in range(3):
            replies.extend(['a' * 64, json.dumps([{'State': {'Running': True,
                'Health': {'Status': 'healthy'}}}])])
        replies.append(json.dumps({'web_assessments': 1, 'trial_results': 16,
            'assessment_metrics': 12, 'participant_name': 'SYNTHETIC_PRIVATE_VALUE'}))
        with tempfile.NamedTemporaryFile() as environment, patch('scripts.monitor_web.command',
                side_effect=replies):
            result = check(Path(environment.name), 'synthetic-monitor')
        self.assertTrue(result['alert'])
        self.assertNotIn('SYNTHETIC_PRIVATE_VALUE', json.dumps(result))
