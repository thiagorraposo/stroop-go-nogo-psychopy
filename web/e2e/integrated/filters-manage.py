"""Fixture W15A exclusivamente sintetica no banco descartavel protegido por common."""
import importlib.util
import json
from pathlib import Path
import sys
from uuid import UUID, uuid4

from common import database_url, ISSUER
import psycopg

spec = importlib.util.spec_from_file_location('dashboard_manage', Path(__file__).with_name('dashboard-manage.py'))
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)


def execute(value):
    database = database_url()
    if value.get('action') == 'membership':
        with psycopg.connect(database) as connection:
            connection.execute('UPDATE web_project_members SET active=%s WHERE project_id=%s AND issuer=%s AND subject=%s',
                               (value['active'], UUID(value['project_id']), ISSUER, value['subject']))
        return {}
    first = dashboard.execute({'role': 'importacao'})
    second = dashboard.execute({'role': 'importacao'})
    with psycopg.connect(database) as connection:
        connection.execute('INSERT INTO web_project_members(project_id,issuer,subject) VALUES(%s,%s,%s)',
                           (UUID(second['project_id']), ISSUER, first['subject']))
        for item, day in ((first, '2026-10-01'), (second, '2026-10-03')):
            connection.execute("UPDATE assessments SET assessment_date=%s,started_at=%s,test_version='synthetic.1' WHERE assessment_id=%s",
                               (day, day + 'T12:00:00', item['assessment_id']))
        # 102 registros no primeiro projeto obrigam o navegador a ler duas paginas reais.
        for index in range(103):
            source = first if index < 101 else second
            target = str(uuid4())
            day = '2026-10-02' if index != 102 else '2026-09-30'
            participant = f'P_SINTETICO_PAGINA_{index:03}' if index < 101 else 'P_SINTETICO_W15'
            visit = 'V_OUTRA_SINTETICA' if index != 102 else 'V_SINTETICA'
            connection.execute('''INSERT INTO assessments
                (assessment_id,test_code,test_version,project,participant_id,participant_name,initials,visit,evaluator,
                 assessment_date,started_at,source_file,imported_at,import_status)
                SELECT %s,test_code,'synthetic.2',project,%s,participant_name,initials,%s,evaluator,%s,%s,
                       source_file,imported_at,import_status FROM assessments WHERE assessment_id=%s''',
                (target, participant, visit, day, day + 'T12:00:00', source['assessment_id']))
            connection.execute('''INSERT INTO assessment_metrics
                (assessment_id,metric_code,metric_label,metric_value,unit,calculated_at)
                SELECT %s,metric_code,metric_label,metric_value,unit,calculated_at
                FROM assessment_metrics WHERE assessment_id=%s''', (target, source['assessment_id']))
            connection.execute('''INSERT INTO trial_results
                (assessment_id,block,trial_number,word,ink_color,condition,correct_response,key_pressed,
                 reaction_time,correct,error_type)
                SELECT %s,block,trial_number,word,ink_color,condition,correct_response,key_pressed,
                       reaction_time,correct,error_type FROM trial_results WHERE assessment_id=%s''',
                (target, source['assessment_id']))
    return {**first, 'projects': [first['project_id'], second['project_id']],
            'assessment_ids': [first['assessment_id'], second['assessment_id']]}


if __name__ == '__main__':
    try:
        sys.stdout.write(json.dumps(execute(json.loads(sys.stdin.read()))))
    except Exception:
        sys.stderr.write('Preparacao sintetica W15A indisponivel.\n')
        raise SystemExit(1) from None
