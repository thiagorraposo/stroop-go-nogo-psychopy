"""Operacoes sinteticas de teste por stdin/stdout, sem rotas extras na API."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import secrets
import sys
from uuid import UUID

from common import ISSUER, SUBJECT, database_url, environment
import psycopg
from api.auth import PROFESSIONAL_COOKIE, _csrf_token
from api.config import APIConfig
from stroop.application import auth
from stroop.domain.auth import opaque_user_id
from stroop.persistence import web_auth, web_sessions


def execute(action, value):
    database = database_url()
    if action == 'professional':
        expires = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        user = auth.authorize(database, {'iss': ISSUER, 'sub': SUBJECT, 'exp': expires}, 'view_dashboard')
        token = secrets.token_urlsafe(32)
        web_auth.create_professional_session(database, sha256(token.encode()).hexdigest(), ISSUER, SUBJECT, expires)
        return {'cookie_name': PROFESSIONAL_COOKIE, 'token': token,
                'csrf': _csrf_token(APIConfig.from_env(environment()), token),
                'user_id': opaque_user_id(user.issuer, user.subject)}
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
