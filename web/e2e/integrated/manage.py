"""Operacoes sinteticas de teste por stdin/stdout, sem rotas extras na API."""
import json
import sys
from uuid import UUID

from common import ISSUER, database_url, environment, fixture_session, fixture_user, primary_subject
import psycopg
from api.auth import PROFESSIONAL_COOKIE, _csrf_token
from api.config import APIConfig
from stroop.domain.auth import opaque_user_id
from stroop.persistence import web_sessions


def execute(action, value):
    database = database_url()
    if action == 'fixture_user':
        subject = fixture_user(value['role'])
        return {'subject': subject, 'user_id': opaque_user_id(ISSUER, subject)}
    if action == 'professional':
        subject = value.get('subject') or primary_subject()
        token, user_id = fixture_session(subject)
        return {'cookie_name': PROFESSIONAL_COOKIE, 'token': token,
                'csrf': _csrf_token(APIConfig.from_env(environment()), token), 'user_id': user_id}
    session_id = UUID(value['session_id'])
    with psycopg.connect(database) as connection:
        if action == 'expire':
            connection.execute("""UPDATE web_participant_sessions
                SET activated_at=CURRENT_TIMESTAMP-INTERVAL '31 minutes',
                    expires_at=CURRENT_TIMESTAMP-INTERVAL '1 minute' WHERE session_id=%s""", (session_id,))
        elif action == 'running':
            token = connection.execute('SELECT participant_token_sha256 FROM web_participant_sessions WHERE session_id=%s', (session_id,)).fetchone()[0]
            connection.commit()
            web_sessions.start_participant_session(database, token, 'web-0.1.0')
        elif action != 'state':
            raise ValueError('Acao de teste invalida.')
        row = connection.execute('''SELECT s.state,s.abort_reason,w.assessment_id,w.receipt FROM web_participant_sessions s
            LEFT JOIN web_assessments w USING(session_id) WHERE s.session_id=%s''', (session_id,)).fetchone()
        if row is None:
            return {'state': None, 'assessments': 0}
        assessment_id = row[2]
        trials = connection.execute('SELECT COUNT(*) FROM trial_results WHERE assessment_id=%s', (assessment_id,)).fetchone()[0]
        metrics = connection.execute('SELECT COUNT(*) FROM assessment_metrics WHERE assessment_id=%s', (assessment_id,)).fetchone()[0]
        return {'state': row[0], 'reason': row[1], 'assessment_id': assessment_id,
                'receipt': row[3], 'assessments': int(assessment_id is not None), 'trials': trials, 'metrics': metrics}


if __name__ == '__main__':
    try:
        result = execute(sys.argv[1], json.loads(sys.stdin.read() or '{}'))
        sys.stdout.write(json.dumps(result))
    except Exception:
        sys.stderr.write('Operacao sintetica de teste indisponivel.\n')
        raise SystemExit(1) from None
