"""Replicacao de ciphertext sintetico, sem SSH, chaves ou backups operacionais."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.backup_postgres import encrypt_stream
from scripts import replicate_web_backup as pull


SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('synthetic_backup_export', SOURCE / 'deploy/vps-export-encrypted-backup.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


class EncryptedBackupReplicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='stroop-synthetic-replication-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.remote = self.root / 'remote'
        self.remote.mkdir(mode=0o700)
        self.destination = self.root / 'copies'
        key = self.root / 'synthetic-ssh-key'
        key.write_bytes(b'synthetic-placeholder-not-a-real-key')
        key.chmod(0o600)
        known = self.root / 'synthetic-known-hosts'
        known.write_text('synthetic.invalid synthetic-placeholder\n')
        self.config = {'host': 'synthetic.invalid', 'user': 'synthetic', 'port': 22022,
                       'key_file': str(key), 'known_hosts_file': str(known),
                       'destination': str(self.destination)}
        self.commands = []

    def backup(self, directory=None, created=NOW, text=b'synthetic PostgreSQL dump fixture'):
        directory = directory or self.remote
        directory.mkdir(mode=0o700, exist_ok=True)
        name = 'stroop-' + created.strftime('%Y%m%dT%H%M%SZ') + '.dump.enc'
        path = directory / name
        encrypted = io.BytesIO()
        encrypt_stream(io.BytesIO(text), encrypted, bytes(range(32)))
        path.write_bytes(encrypted.getvalue())
        path.chmod(0o600)
        path.with_suffix(path.suffix + '.sha256').write_text(sha256(path.read_bytes()).hexdigest() + '  ' + name + '\n')
        return path

    def fetch(self, config, command, destination, limit):
        self.commands.append(command)
        data = io.BytesIO()
        exporter.export(command, base=self.remote, output=data)
        self.assertLessEqual(len(data.getvalue()), limit)
        destination.write(data.getvalue())

    def run_pull(self, fetch=None, now=NOW):
        with patch.object(pull, '_fetch', side_effect=fetch or self.fetch):
            return pull.run_once(self.config, now=now)

    def test_replica_ciphertext_confere_checksum_e_reexecucao_nao_baixa_novamente(self):
        source = self.backup()
        first = self.run_pull()
        self.assertEqual((first['status'], first['alert']), ('copied', False))
        target = self.destination / source.name
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.destination.stat().st_mode & 0o777, 0o700)
        self.assertTrue(target.with_suffix(target.suffix + '.sha256').is_file())
        before = target.stat().st_ino
        self.commands.clear()
        second = self.run_pull()
        self.assertEqual(second['status'], 'already_current')
        self.assertEqual(self.commands, ['manifest'])
        self.assertEqual(target.stat().st_ino, before)

    def test_download_tampered_nunca_publica_e_remove_temporario(self):
        self.backup()
        def tamper(config, command, destination, limit):
            if command == 'manifest':
                self.fetch(config, command, destination, limit)
            else:
                source = sorted(self.remote.glob('*.dump.enc'))[-1].read_bytes()
                destination.write(source[:-1] + bytes([source[-1] ^ 1]))
        with self.assertRaises(pull.ReplicationError):
            self.run_pull(tamper)
        self.assertEqual(list(self.destination.glob('*.dump.enc')), [])
        self.assertEqual(list(self.destination.glob('.encrypted-backup-*')), [])

    def test_colisao_existente_ou_symlink_nao_sobrescreve_evidencia(self):
        source = self.backup()
        self.destination.mkdir(mode=0o700)
        target = self.destination / source.name
        target.write_bytes(b'previous-evidence-do-not-overwrite')
        with self.assertRaises(pull.ReplicationError):
            self.run_pull()
        self.assertEqual(target.read_bytes(), b'previous-evidence-do-not-overwrite')
        target.unlink()
        original = self.root / 'synthetic-preserved-file'
        original.write_bytes(b'original')
        target.symlink_to(original)
        with self.assertRaises(pull.ReplicationError):
            self.run_pull()
        self.assertEqual(original.read_bytes(), b'original')

    def test_copia_antiga_preservada_mas_alerta_rpo_e_futuro_rejeitado(self):
        self.backup(created=NOW - timedelta(hours=25))
        report = self.run_pull()
        self.assertEqual((report['status'], report['alert'], report['copied']), ('stale', True, True))
        self.backup(created=NOW + timedelta(minutes=6))
        with self.assertRaises(pull.ReplicationError):
            self.run_pull()

    def test_retencao_so_remove_ciphertext_validado_com_checksum(self):
        self.destination.mkdir(mode=0o700)
        for hour in range(1, 32):
            self.backup(self.destination, NOW - timedelta(hours=hour))
        unverified = self.destination / 'stroop-20200101T000000Z.dump.enc'
        unverified.write_bytes(b'preserve-unverified-file')
        unrelated = self.destination / 'notes.txt'
        unrelated.write_text('synthetic operator note')
        self.backup()
        report = self.run_pull()
        self.assertEqual(report['retained_generations'], 30)
        self.assertEqual(len(list(self.destination.glob('*.dump.enc'))), 31)
        self.assertTrue(unverified.is_file())
        self.assertTrue(unrelated.is_file())

    def test_manifest_download_fixa_nome_mesmo_se_nova_geracao_aparece(self):
        first = self.backup()
        def race(config, command, destination, limit):
            self.fetch(config, command, destination, limit)
            if command == 'manifest':
                self.backup(created=NOW + timedelta(seconds=1))
        self.assertEqual(self.run_pull(race)['status'], 'copied')
        self.assertEqual(list(self.destination.glob('*.dump.enc')), [self.destination / first.name])

    def test_exportador_recusa_comandos_paths_symlinks_plaintext_e_checksum_errado(self):
        source = self.backup()
        for command in ('', 'sh', 'manifest; id', 'manifest extra', 'download ../keys/private',
                        'download ' + source.name + ';id', 'download /etc/passwd'):
            with self.subTest(command=command), self.assertRaises(Exception):
                exporter.export(command, base=self.remote, output=io.BytesIO())
        source.with_suffix(source.suffix + '.sha256').write_text('0' * 64 + '  ' + source.name + '\n')
        with self.assertRaises(Exception):
            exporter.export('manifest', base=self.remote, output=io.BytesIO())
        source.write_bytes(b'plaintext' * 100)
        with self.assertRaises(Exception):
            exporter.export('download ' + source.name, base=self.remote, output=io.BytesIO())
        source.unlink()
        source.symlink_to(self.root / 'synthetic-ssh-key')
        with self.assertRaises(Exception):
            exporter.export('manifest', base=self.remote, output=io.BytesIO())

    def test_configuracao_recusa_injecao_chave_publica_e_chave_dentro_do_destino(self):
        for key, value in (('host', '-oProxyCommand=id'), ('user', 'user;id'), ('port', True),
                           ('key_file', 'relative-key'), ('destination', str(self.root))):
            with self.subTest(key=key), self.assertRaises(pull.ReplicationError):
                pull.configuration({**self.config, key: value})
        Path(self.config['key_file']).chmod(0o644)
        with self.assertRaises(pull.ReplicationError):
            pull.configuration(self.config)

    def test_manifest_malformado_nao_cria_arquivo_fora_do_destino(self):
        self.backup()
        def malformed(config, command, destination, limit):
            data = io.BytesIO()
            exporter.export('manifest', base=self.remote, output=data)
            value = json.loads(data.getvalue())
            value['name'] = '../../outside.dump.enc'
            destination.write(json.dumps(value).encode())
        with self.assertRaises(pull.ReplicationError):
            self.run_pull(malformed)
        self.assertFalse((self.root / 'outside.dump.enc').exists())

    def test_cli_config_privada_e_erro_fechado_sem_path_ou_segredo(self):
        config = self.root / 'config.json'
        config.write_text(json.dumps(self.config))
        config.chmod(0o644)
        output = io.StringIO()
        with patch('sys.stdout', output):
            self.assertEqual(pull.main(['--config', str(config)]), 1)
        self.assertEqual(json.loads(output.getvalue()),
                         {'status': 'unavailable', 'alert': True, 'error': 'replication_failed'})
        self.assertNotIn(str(self.root), output.getvalue())

    def test_status_privado_registra_sucesso_atraso_e_falha_sem_segredos(self):
        status = self.root / 'status'
        status.mkdir(mode=0o700)
        last = status / 'last-result.json'
        config = self.root / 'pull.json'
        config.write_text(json.dumps(self.config))
        config.chmod(0o600)
        reports = [dict(status='already_current', alert=False, copied=False),
                   dict(status='stale', alert=True, backup_age_seconds=90000)]
        for report in reports:
            with patch.object(pull, 'run_once', return_value=report), patch('sys.stdout', io.StringIO()):
                self.assertEqual(pull.main(['--config', str(config), '--status-file', str(last)]), int(report['alert']))
            stored = json.loads(last.read_text())
            self.assertIn('checked_at', stored)
            self.assertEqual(stored['status'], report['status'])
            self.assertEqual(last.stat().st_mode & 0o777, 0o600)
        with patch.object(pull, 'run_once', side_effect=OSError('private-secret')), patch('sys.stdout', io.StringIO()):
            self.assertEqual(pull.main(['--config', str(config), '--status-file', str(last)]), 1)
        self.assertEqual(json.loads(last.read_text())['error'], 'replication_failed')
        self.assertNotIn('private-secret', last.read_text())
        self.assertEqual(list(status.glob('.replication-status-*')), [])

    def test_status_nao_segue_symlink_nem_usa_diretorio_publico(self):
        self.root.chmod(0o700)
        target = self.root / 'preserved'
        target.write_text('preserved')
        link = self.root / 'last-result.json'
        link.symlink_to(target)
        with self.assertRaises(pull.ReplicationError):
            pull.save_status(link, {'alert': False})
        self.assertEqual(target.read_text(), 'preserved')
        self.root.chmod(0o755)
        with self.assertRaises(pull.ReplicationError):
            pull.save_status(self.root / 'new.json', {'alert': False})


if __name__ == '__main__':
    unittest.main()
