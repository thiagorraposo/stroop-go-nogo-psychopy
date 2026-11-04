import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts.backup_postgres import BackupError, create_backup, generate_key


class WebBackupTests(unittest.TestCase):
    def test_servico_compose_com_hifen_e_aceito_sem_relaxar_sql(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key = root / 'keys' / 'backup.key'
            generate_key(key)
            compose = root / 'compose.yaml'
            compose.write_text('services: {}')
            environment = root / 'config.env'
            environment.write_text('')
            process = Mock(stdout=io.BytesIO(b'SYNTHETIC_DUMP'))
            process.wait.return_value = 0
            process.poll.return_value = 0
            with patch('scripts.backup_postgres.subprocess.Popen', return_value=process) as run:
                artifact = create_backup(compose_file=compose, env_file=environment,
                    key_file=key, output_directory=root / 'backups', database='synthetic',
                    user='synthetic', service='web-postgres')
            self.assertTrue(artifact.is_file())
            self.assertNotIn(b'SYNTHETIC_DUMP', artifact.read_bytes())
            self.assertIn('web-postgres', run.call_args.args[0])
            self.assertIn('--env-file', run.call_args.args[0])
            for service in ('--all', 'web;command', 'web/postgres'):
                with self.subTest(service=service), self.assertRaises(BackupError):
                    create_backup(compose_file=compose, env_file=environment,
                        key_file=key, output_directory=root / 'backups', database='synthetic',
                        user='synthetic', service=service)
