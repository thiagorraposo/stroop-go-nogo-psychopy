"""Importacoes reais de instrumentos registrados; somente perfis/dados sinteticos."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from uuid import UUID, uuid4

from common import ROOT, ISSUER, database_url
import psycopg
from stroop.application.import_postgres import import_csv

spec = importlib.util.spec_from_file_location('dashboard_manage', Path(__file__).with_name('dashboard-manage.py'))
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)


def execute():
    database = database_url()
    first, second = [dashboard.execute({'role': 'consulta'}) for _ in range(2)]
    with psycopg.connect(database) as connection:
        connection.execute('INSERT INTO web_project_members(project_id,issuer,subject) VALUES(%s,%s,%s)',
                           (UUID(second['project_id']), ISSUER, first['subject']))
        codes = [connection.execute('SELECT code FROM web_projects WHERE project_id=%s', (UUID(item['project_id']),)).fetchone()[0]
                 for item in (first, second)]
    cases = json.loads((ROOT / 'tests/fixtures/web_results_summary.json').read_text())['cases']
    demo = list(csv.DictReader((ROOT / 'tests/fixtures/csv/instrumento_sintetico_demo.csv').open()))
    ids = []
    with tempfile.TemporaryDirectory(prefix='synthetic-w15b-') as directory:
        for index, (rows, participant, visit) in enumerate([
            (list(csv.DictReader(io.StringIO(cases[1]['expected_csv']))), 'P_SINTETICO_W15', 'V_SINTETICA'),
            (list(csv.DictReader(io.StringIO(cases[0]['expected_csv']))), 'P_SINTETICO_SEM_HITS', 'V_ZERO'),
            (demo, 'P_SINTETICO_DEMO', 'V1'), (demo, 'P_SINTETICO_DEMO', 'V2')]):
            assessment_id = str(uuid4()); ids.append(assessment_id)
            for row in rows:
                row.update(project=codes[0], assessment_id=assessment_id, participant_id=participant,
                           visit=visit, participant_name='NOME_SINTETICO_RESTRITO', initials='SS')
                if index == 3 and row['metric_code'] == 'demo_total':
                    row['metric_value'] = '8'
                if index == 3 and row['metric_code'] == 'demo_mean':
                    row['metric_value'] = '3.5'
            path = Path(directory) / f'synthetic-{index}.csv'
            with path.open('w', newline='') as output:
                writer = csv.DictWriter(output, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
            import_csv(path, database)
    return {**first, 'projects': [first['project_id'], second['project_id']], 'codes': codes,
            'no_hits_id': ids[1], 'demo_ids': ids[2:], 'repeated_ids': [first['assessment_id'], ids[0]]}


if __name__ == '__main__':
    try:
        sys.stdout.write(json.dumps(execute()))
    except Exception:
        sys.stderr.write('Preparacao sintetica W15B indisponivel.\n')
        raise SystemExit(1) from None
