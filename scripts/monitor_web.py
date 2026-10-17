#!/usr/bin/env python3
"""Sinal operacional local WEB, sem publicar contagens ou dados na API."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ('web-postgres', 'web-api', 'web-proxy')
COUNTS = '''import json, os
import psycopg
from api.config import secret_value
with psycopg.connect(secret_value(os.environ,'API_READ_DATABASE_URL'),connect_timeout=3,
    options='-c default_transaction_read_only=on -c statement_timeout=3000') as db:
    db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
    result={}
    for table,column in [('web_assessments','assessment_id'),('trial_results','assessment_id'),('assessment_metrics','assessment_id')]:
        from psycopg import sql
        result[table]=db.execute(sql.SQL('SELECT COUNT({}) FROM public.{}').format(sql.Identifier(column),sql.Identifier(table))).fetchone()[0]
print(json.dumps(result))
'''


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=15, check=False)
    if result.returncode:
        raise RuntimeError
    return result.stdout


def check(env_file: Path, project: str) -> dict:
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'status': 'unavailable', 'alert': True}
    try:
        if not env_file.is_file() or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,62}', project):
            return report
        base = ['docker', 'compose', '--env-file', str(env_file), '--project-name', project,
                '-f', str(ROOT / 'compose.web.yaml'), '--profile', 'web']
        states = {}
        for service in SERVICES:
            container = command([*base, 'ps', '--quiet', service]).strip()
            if not re.fullmatch(r'[0-9a-f]{12,64}', container):
                raise RuntimeError
            state = json.loads(command(['docker', 'inspect', container]))[0]['State']
            states[service] = state.get('Health', {}).get('Status') == 'healthy' and state.get('Running') is True
        report['services'] = states
        if not all(states.values()):
            return report
        counts = json.loads(command([*base, 'exec', '-T', 'web-api', 'python', '-c', COUNTS]))
        if set(counts) != {'web_assessments', 'trial_results', 'assessment_metrics'} or any(
            type(value) is not int or value < 0 for value in counts.values()
        ):
            raise RuntimeError
        report.update(status='ready', alert=False, counts=counts)
    except Exception:
        pass
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', required=True, type=Path)
    parser.add_argument('--project-name', required=True)
    args = parser.parse_args()
    report = check(args.env_file, args.project_name)
    print(json.dumps(report))
    return int(report['alert'])


if __name__ == '__main__':
    raise SystemExit(main())
