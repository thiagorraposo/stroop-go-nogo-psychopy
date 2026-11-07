"""Operador de fixtures sinteticas; nenhum token/credencial em stdout."""
import json
import sys

from common import PASSWORD, USERNAME, database_url
import psycopg
from stroop.application import local_auth
from stroop.domain.local_auth import LOCAL_ISSUER


def main():
    action = sys.argv[1]
    database = database_url()
    if action == 'reset':
        if not local_auth.provision(database, USERNAME, PASSWORD, recover=True):
            raise RuntimeError('Conta sintetica ausente.')
        with psycopg.connect(database) as connection:
            connection.execute('DELETE FROM web_local_auth_limits')
        result = {'ok': True}
    elif action in {'block', 'unblock'}:
        with psycopg.connect(database) as connection:
            connection.execute('UPDATE app_users SET active=%s WHERE issuer=%s', (action == 'unblock', LOCAL_ISSUER))
        result = {'ok': True}
    elif action == 'state':
        with psycopg.connect(database) as connection:
            row = connection.execute('''SELECT credential_version,
                (SELECT count(*) FROM web_local_sessions WHERE revoked_at IS NULL),
                (SELECT count(*) FROM web_project_members WHERE issuer=%s)
                FROM web_local_credentials''', (LOCAL_ISSUER,)).fetchone()
        result = {'version': row[0], 'sessions': row[1], 'memberships': row[2]}
    else:
        raise RuntimeError('Acao sintetica desconhecida.')
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Falha na fixture local sintetica.', file=sys.stderr)
        raise SystemExit(1) from None
