import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'deploy/vps-rollback.sh'


class VPSRollbackTests(unittest.TestCase):
    def execute(self, healthy):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, body in {
                'docker': '#!/bin/sh\nprintf "%s\\n" "$*" >> "$SYNTHETIC_COMMAND_LOG"\n',
                'curl': '#!/bin/sh\nexit "$SYNTHETIC_HEALTH_STATUS"\n',
                'sleep': '#!/bin/sh\nexit 0\n',
            }.items():
                path = root / name
                path.write_text(body)
                path.chmod(0o700)
            log = root / 'commands.log'
            result = subprocess.run(['/bin/sh', str(SCRIPT)], capture_output=True, text=True,
                env={**os.environ, 'PATH': str(root), 'SYNTHETIC_COMMAND_LOG': str(log),
                     'SYNTHETIC_HEALTH_STATUS': '0' if healthy else '1'})
            return result, log.read_text()

    def test_legado_so_e_confirmado_apos_resposta_https(self):
        result, commands = self.execute(True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Legado respondeu via HTTPS', result.stdout)
        self.assertIn('start stroop-production-dashboard-1 stroop-production-proxy-1', commands)
        self.assertNotIn('start stroop-web-web-proxy-1', commands)

    def test_legado_sem_saude_retorna_ao_proxy_web(self):
        result, commands = self.execute(False)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Legado respondeu', result.stdout)
        self.assertTrue(commands.endswith('stop stroop-production-proxy-1\nstart stroop-web-web-proxy-1\n'))
