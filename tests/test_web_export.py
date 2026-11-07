"""CSV e paridade de resultados WEB com fontes exclusivamente sinteticas."""
import copy
import csv
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from stroop.application.import_sqlite import import_csv
from stroop.domain.stroop import CANONICAL_COLUMNS, calculate_metrics
from stroop.domain.web_export import export_filename, serialize_assessment_csv
from stroop.domain.web_results import PROTOCOL_ID, TEST_VERSION, validate_result
from stroop.ingestion.stroop_csv import load_and_validate_csv

ROOT = Path(__file__).resolve().parents[1]
SHARED = json.loads((ROOT / 'tests/fixtures/web_results_summary.json').read_text())


class WebExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'condicoes/bloco_principal_stroop_go_nogo_ptbr.csv').open() as source:
            cls.conditions = [{**row, 'condition_id': int(row['trial_number'])}
                              for row in csv.DictReader(source)]

    def normalized(self, fixture):
        return validate_result({
            'protocol_id': PROTOCOL_ID, 'test_version': TEST_VERSION,
            'platform': 'web', 'app_version': '0.1.0',
            'frame_period_ms': fixture['frame_period_ms'], 'trials': fixture['trials'],
        }, tuple(fixture['order']), '0.1.0', self.conditions)

    def test_fixtures_compartilhadas_exportam_e_importam_com_mesmas_metricas(self):
        for fixture in SHARED['cases']:
            with self.subTest(case=fixture['name']), tempfile.TemporaryDirectory() as directory:
                result = self.normalized(fixture)
                content = serialize_assessment_csv(SHARED['metadata'], result['rows'])
                self.assertEqual(content, fixture['expected_csv'])
                self.assertNotIn('NOME SINTETICO NAO EXPORTAR', content)
                path = Path(directory) / SHARED['filename']
                path.write_text(content, encoding='utf-8', newline='')
                rows = load_and_validate_csv(path)
                self.assertEqual(list(rows[0]), CANONICAL_COLUMNS)
                self.assertEqual(len(rows), 16)
                self.assertTrue(all(row['participant_name'] == 'NAO_COLETADO'
                                    and row['initials'] == '' and row['block'] == 'main' for row in rows))
                metrics = {metric['metric_code']: metric['metric_value'] for metric in calculate_metrics(rows)}
                expected_units = {metric['metric_code']: metric['unit'] for metric in result['metrics']}
                self.assertEqual(set(metrics), set(expected_units))
                self.assertAlmostEqual(metrics['omission_errors_percentage'],
                                       fixture['expected_summary']['omission_errors'] /
                                       fixture['expected_summary']['total_go_trials'] * 100)
                for key, expected in fixture['expected_summary'].items():
                    self.assertAlmostEqual(metrics[key], 0 if expected is None else expected, places=12)
                imported = import_csv(path, Path(directory) / 'synthetic.sqlite3')
                self.assertEqual(imported['trials_imported'], 16)
                with sqlite3.connect(Path(directory) / 'synthetic.sqlite3') as connection:
                    self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone(), (1,))
                    self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessment_metrics').fetchone(), (12,))
                    imported_metrics = connection.execute(
                        'SELECT metric_code,metric_value,unit FROM assessment_metrics').fetchall()
                for code, value, unit in imported_metrics:
                    self.assertAlmostEqual(value, metrics[code], places=12)
                    self.assertEqual(unit, expected_units[code])
                self.assertEqual(rows[0]['started_at'], '2026-10-17T02:30:45Z')
                self.assertEqual(rows[0]['assessment_date'], '2026-10-17')

    def test_nome_utc_seguro_sem_identificadores(self):
        self.assertEqual(export_filename(SHARED['metadata']['started_at']),
                         'stroop_go_nogo_ptbr_2026-10-17_02h30m45s_trials.csv')
        for value in ('', '../escape', '2026-10-16T10:00:00', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                export_filename(value)

    def test_escapa_delimitadores_e_neutraliza_formulas_em_metadados(self):
        rows = self.normalized(SHARED['cases'][0])['rows']
        for value in ('=1+1', '+1', '-1', '@SUM(1)', ' \t=1', '\nSINTETICO'):
            metadata = {**SHARED['metadata'], 'project': value}
            exported = list(csv.DictReader(io.StringIO(serialize_assessment_csv(metadata, rows))))
            self.assertEqual(exported[0]['project'], "'" + value)
        quoted = 'PROJETO SINTÉTICO, "aspas"\nsegunda linha'
        exported = list(csv.DictReader(io.StringIO(serialize_assessment_csv(
            {**SHARED['metadata'], 'project': quoted}, rows))))
        self.assertEqual(exported[0]['project'], quoted)

    def test_nao_exporta_pratica_parcial_nem_resposta_inconsistente(self):
        rows = self.normalized(SHARED['cases'][0])['rows']
        for mutate in (
            lambda data: data.pop(),
            lambda data: data[0].update(block='practice'),
            lambda data: data[0].update(trial_number='2'),
            lambda data: data[0].update(reaction_time='0.1'),
            lambda data: data[0].update(key_pressed='enter'),
            lambda data: data[0].update(key_pressed='space', reaction_time=float('nan')),
            lambda data: data[0].update(key_pressed='space', reaction_time=float('inf')),
            lambda data: data[0].update(key_pressed='space', reaction_time=True),
            lambda data: data[0].update(key_pressed='space', reaction_time=0),
            lambda data: data[0].update(key_pressed='space', reaction_time=2.5),
        ):
            data = copy.deepcopy(rows)
            mutate(data)
            with self.subTest(data=data[0]), self.assertRaises(ValueError):
                serialize_assessment_csv(SHARED['metadata'], data)

    def test_legado_preserva_rotulos_instante_e_quantidade_sem_inventar_fuso(self):
        rows = load_and_validate_csv(ROOT / 'tests/fixtures/csv/valido_minimo.csv')
        metadata = {**rows[0], 'assessment_id': 'synthetic-legacy-assessment',
                    'started_at': '2026-01-01T10:00:00'}
        output = list(csv.DictReader(io.StringIO(serialize_assessment_csv(metadata, rows))))
        self.assertEqual(len(output), 4)
        self.assertEqual(output[0]['started_at'], '2026-01-01T10:00:00')
        self.assertEqual(output[0]['assessment_id'], 'synthetic-legacy-assessment')
        self.assertEqual(output[0]['participant_name'], 'NAO_COLETADO')
        self.assertEqual(export_filename(metadata['started_at'], allow_naive=True),
                         'stroop_go_nogo_ptbr_2026-01-01_10h00m00s_trials.csv')

    def test_nao_muda_entrada_e_deriva_classificacao_pelo_nucleo(self):
        rows = self.normalized(SHARED['cases'][1])['rows']
        rows[0].update(correct='0', error_type='DADO_SINTETICO_INCORRETO')
        before = copy.deepcopy(rows)
        exported = list(csv.DictReader(io.StringIO(serialize_assessment_csv(SHARED['metadata'], rows))))
        self.assertEqual(rows, before)
        self.assertEqual(exported[0]['error_type'], 'commission')
        self.assertEqual(exported[0]['correct'], '0')


if __name__ == '__main__':
    unittest.main()
