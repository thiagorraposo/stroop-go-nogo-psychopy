"""Preparacao sintetica isolada W15; banco descartavel validado por common."""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
from uuid import UUID, uuid4

from common import ROOT, ISSUER, PASSWORD, database_url, fixture_user, fixture_session, primary_subject
import psycopg
from api.auth import PROFESSIONAL_COOKIE
from stroop.domain.auth import opaque_user_id
from stroop.application.import_postgres import import_csv


def execute(value):
    database = database_url()
    if value.get('action') == 'revoke':
        with psycopg.connect(database) as connection:
            connection.execute('UPDATE web_project_members SET active=false WHERE project_id=%s AND subject=%s',
                               (UUID(value['project_id']), value['subject']))
        return {}
    role = value['role']
    if role not in ('consulta', 'importacao', 'administracao'):
        raise ValueError('Perfil sintetico invalido')
    subject = fixture_user(role)
    actor_subject = primary_subject()
    project_id = uuid4()
    label = 'SYNTHETIC_DASH_' + uuid4().hex
    with psycopg.connect(database) as connection:
        connection.execute('''INSERT INTO web_projects(project_id,code,name,created_by_issuer,created_by_subject)
            VALUES(%s,%s,'Pesquisa sintetica W15',%s,%s)''', (project_id, label, ISSUER, actor_subject))
        connection.execute('INSERT INTO web_project_members(project_id,issuer,subject) VALUES(%s,%s,%s)',
                           (project_id, ISSUER, subject))
        connection.execute('INSERT INTO web_legacy_project_links(legacy_project,project_id) VALUES(%s,%s)',
                           (label, project_id))
    fixture = json.loads((ROOT / 'tests/fixtures/web_results_summary.json').read_text())['cases'][1]
    rows = list(csv.DictReader(io.StringIO(fixture['expected_csv'])))
    assessment_id = str(uuid4())
    for row in rows:
        row.update(project=label, assessment_id=assessment_id, participant_id='P_SINTETICO_W15',
                   visit='V_SINTETICA', participant_name='NOME_SINTETICO_RESTRITO', initials='SS')
    with tempfile.TemporaryDirectory(prefix='synthetic-w15-') as directory:
        path = Path(directory) / 'synthetic.csv'
        with path.open('w', newline='') as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        import_csv(path, database)
    token, _ = fixture_session(subject)
    from api.auth import _csrf_token
    from api.config import APIConfig
    from common import environment
    csrf = _csrf_token(APIConfig.from_env(environment()), token)
    return {'cookie_name': PROFESSIONAL_COOKIE, 'token': token, 'csrf': csrf, 'project_id': str(project_id),
            'subject': subject, 'assessment_id': assessment_id,
            'evaluator_id': opaque_user_id(ISSUER, subject),
            'username': f'synthetic-{UUID(subject).hex}', 'password': PASSWORD}


if __name__ == '__main__':
    try:
        sys.stdout.write(json.dumps(execute(json.loads(sys.stdin.read()))))
    except Exception:
        sys.stderr.write('Preparacao sintetica W15 indisponivel.\n')
        raise SystemExit(1) from None
