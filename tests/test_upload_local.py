"""Upload local com entradas sinteticas, sem iniciar servidor nos testes."""
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import psycopg
from scripts import upload_local as upload
from scripts.migrations import apply_migrations

DATA = (Path(__file__).parent / 'fixtures/csv/valido_minimo.csv').read_bytes()
URL = os.environ.get('TEST_DATABASE_URL', '')


class UploadTests(unittest.TestCase):
    def test_estados_auditoria_e_remocao(self):
        events, paths = [], []
        def importer(path, *args, **kwargs):
            paths.append(path)
            self.assertEqual(path.read_bytes(), DATA)
            self.assertNotIn('SYNTHETIC_PRIVATE', str(path))
        with tempfile.TemporaryDirectory() as root, patch.object(upload, 'import_csv', side_effect=importer):
            result = upload.process_upload(DATA, '../../SYNTHETIC_PRIVATE.csv', 'unused', temp_root=root, audit=events.append)
            self.assertEqual(list(Path(root).iterdir()), [])
        self.assertEqual(result['statuses'], ['recebido', 'validado', 'importado'])
        self.assertTrue(all(not p.exists() for p in paths))
        for event in events:
            self.assertEqual(set(event), {'id', 'origin', 'at', 'status'})
        self.assertNotIn('SYNTHETIC_PRIVATE', json.dumps(events))

    def test_limites_extensao_encoding_e_nul(self):
        with patch.object(upload, 'import_csv') as importer:
            for data, name in ((DATA, 'a.exe'), (b'', 'a.csv'), (b'x'*(upload.MAX_BYTES+1), 'a.csv'),
                               (b'\xff', 'a.csv'), (b'\0', 'a.csv')):
                with self.subTest(name=name, size=len(data)):
                    self.assertEqual(upload.process_upload(data, name, '')['statuses'][-1], 'rejeitado')
        importer.assert_not_called()

    def test_csv_invalido_nao_persiste_e_limpa(self):
        with tempfile.TemporaryDirectory() as root:
            result = upload.process_upload(b'bad,header\n1,2', 'x.csv', '', temp_root=root)
            self.assertEqual(result['statuses'], ['recebido', 'rejeitado'])
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_falha_banco_nao_expoe_detalhes_e_limpa(self):
        with tempfile.TemporaryDirectory() as root, patch.object(upload, 'import_csv', side_effect=[{}, upload.PostgresImportError('SYNTHETIC_SECRET')]):
            result = upload.process_upload(DATA, 'x.csv', '', temp_root=root)
            self.assertEqual(list(Path(root).iterdir()), [])
        self.assertEqual(result['statuses'], ['recebido', 'validado', 'rejeitado'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))

    def test_conteudo_nao_executado(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / 'marker'
            data = f"__import__('pathlib').Path({str(target)!r}).touch()".encode()
            result = upload.process_upload(data, 'script.csv', '', temp_root=root)
            self.assertEqual(result['statuses'][-1], 'rejeitado')
            self.assertFalse(target.exists())

    def test_producao_e_habilitacao_recusadas(self):
        with patch.dict(os.environ, {'APP_ENV': 'production', 'DATABASE_URL': 'unused'}), patch.object(upload, 'UploadServer') as server:
            self.assertEqual(upload.main(['--local']), 1)
            server.assert_not_called()
        with patch.dict(os.environ, {'APP_ENV': 'local', 'DATABASE_URL': 'unused'}), patch.object(upload, 'UploadServer') as server:
            self.assertEqual(upload.main([]), 1)
            server.assert_not_called()

    def handler(self, **headers):
        handler = object.__new__(upload.UploadHandler)
        handler.server = SimpleNamespace(server_port=8765, origin='http://127.0.0.1:8765', token='synthetic', database_url='', temp_root=None, audit=None)
        handler.path = '/upload'
        handler.headers = Message()
        defaults = {'Host': '127.0.0.1:8765', 'Origin': 'http://127.0.0.1:8765',
                    'X-Upload-Token': 'synthetic', 'Content-Type': 'text/csv',
                    'Content-Length': str(len(DATA)), 'X-Upload-Name': 'synthetic.csv'}
        defaults.update(headers)
        for key, value in defaults.items():
            if value is not None:
                handler.headers[key] = value
        handler.rfile = io.BytesIO(DATA)
        handler.reply = lambda code, payload, **kwargs: setattr(handler, 'result', (code, payload))
        return handler

    def test_http_recusa_origem_host_token(self):
        with patch.object(upload, 'process_upload') as process:
            for key in ('Host', 'Origin', 'X-Upload-Token'):
                h = self.handler(**{key: 'https://invalid.example'})
                h.do_POST()
                self.assertEqual(h.result[0], 403)
                self.assertEqual(h.rfile.tell(), 0)
        process.assert_not_called()

    def test_http_limite_tipo_multipart_e_chunked(self):
        with patch.object(upload, 'process_upload') as process:
            for headers in ({'Content-Length': str(upload.MAX_BYTES+1)}, {'Content-Length': '-1'},
                            {'Content-Length': None}, {'Content-Type': 'multipart/form-data'},
                            {'Transfer-Encoding': 'chunked'}):
                h = self.handler(**headers)
                h.do_POST()
                self.assertEqual(h.result[0], 400)
                self.assertEqual(h.rfile.tell(), 0)
        process.assert_not_called()

    def test_http_corpo_truncado_e_cabecalho_duplicado(self):
        h = self.handler()
        h.rfile = io.BytesIO(DATA[:5])
        h.do_POST()
        self.assertEqual(h.result[0], 400)
        h = self.handler()
        h.headers['Content-Length'] = '1'
        h.do_POST()
        self.assertEqual(h.result[0], 400)

    def test_http_encaminha_um_arquivo(self):
        h = self.handler()
        with patch.object(upload, 'process_upload', return_value={'statuses': ['importado']}) as process:
            h.do_POST()
        self.assertEqual(h.result[0], 200)
        self.assertEqual(process.call_args.args[:2], (DATA, 'synthetic.csv'))

    def test_get_nao_serve_arquivos_e_usa_token(self):
        h = self.handler()
        h.path = '/'
        h.do_GET()
        self.assertEqual(h.result[0], 200)
        self.assertIn("'X-Upload-Token':'synthetic'", h.result[1])
        h.path = '/../../anything'
        h.do_GET()
        self.assertEqual(h.result[0], 403)

    def test_utf8_bom_aceito(self):
        with patch.object(upload, 'import_csv'):
            self.assertEqual(upload.process_upload(b'\xef\xbb\xbf'+DATA, 'x.CSV', '')['statuses'][-1], 'importado')


@unittest.skipUnless(URL, 'TEST_DATABASE_URL nao configurada')
class UploadIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not psycopg.conninfo.conninfo_to_dict(URL).get('dbname', '').startswith('stroop_etapa4_test'):
            raise RuntimeError('Banco descartavel obrigatorio')

    def setUp(self):
        with psycopg.connect(URL, autocommit=True) as c:
            c.execute('DROP SCHEMA public CASCADE')
            c.execute('CREATE SCHEMA public')
        apply_migrations(URL)

    def test_upload_completo_e_duplicado_sem_residuos(self):
        with tempfile.TemporaryDirectory() as root:
            first = upload.process_upload(DATA, 'synthetic.csv', URL, temp_root=root)
            second = upload.process_upload(DATA, 'synthetic.csv', URL, temp_root=root)
            self.assertEqual(first['statuses'][-1], 'importado')
            self.assertEqual(second['statuses'][-1], 'rejeitado')
            self.assertEqual(list(Path(root).iterdir()), [])
        with psycopg.connect(URL) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM assessments').fetchone()[0], 1)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM trial_results').fetchone()[0], 4)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM assessment_metrics').fetchone()[0], 12)
            self.assertIn(first['id'], c.execute('SELECT source_file FROM assessments').fetchone()[0])

    def test_uploads_simultaneos_isolados_e_idempotentes(self):
        with tempfile.TemporaryDirectory() as root, ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: upload.process_upload(DATA, 'synthetic.csv', URL, temp_root=root), range(2)))
            self.assertEqual(list(Path(root).iterdir()), [])
        self.assertNotEqual(results[0]['id'], results[1]['id'])
        self.assertCountEqual([r['statuses'][-1] for r in results], ['importado', 'rejeitado'])
