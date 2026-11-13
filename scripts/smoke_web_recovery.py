#!/usr/bin/env python3
"""Ensaio WEB sintetico: backup, restauracao, falha de banco e rollback."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile
import time

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.backup_postgres import (BackupError, create_backup, generate_key,
                                    recovery_snapshot_sql, restore_isolated)
from scripts.monitor_web import check
from scripts.migrations import discover_migrations
from scripts.smoke_web_compose import API_IMAGE, PROXY_IMAGE, SYNTHETIC_DATABASE, WebComposeSmoke, _run


class RecoveryComposeSmoke(WebComposeSmoke):
    """Acrescenta cadastros/vinculos auditados a coleta sintetica existente."""

    def _invitation_fixture(self, headers):
        entities = []
        for resource, name in (('patients', 'Paciente sintetico recuperacao'),
                               ('evaluators', 'Avaliador sintetico recuperacao')):
            status, _, entity = self._json_request(
                'POST', '/api/v1/' + resource, {'full_name': name}, headers)
            self._assert(status == 201)
            entities.append(entity)
        return ({'patient_id': entities[0]['id'], 'evaluator_id': entities[1]['id'],
                 'test_code': 'stroop_go_nogo_ptbr', 'visit': 'V1'},
                entities[0]['participant_code'])


def recovery_snapshot(stack):
    helper = '''import json, os
import psycopg
from api.config import secret_value
with psycopg.connect(secret_value(os.environ, 'API_MIGRATION_DATABASE_URL')) as db:
    db.execute("SET TIME ZONE 'UTC'")
    invalid = db.execute("""SELECT COUNT(*) FROM web_assessments w
        JOIN assessments a USING(assessment_id)
        JOIN web_invitations i USING(session_id)
        LEFT JOIN web_patients p ON p.id=w.patient_id
        LEFT JOIN web_evaluators e ON e.id=w.evaluator_uuid
        WHERE p.id IS NULL OR e.id IS NULL
          OR p.participant_code IS DISTINCT FROM a.participant_id
          OR e.evaluator_code IS DISTINCT FROM a.evaluator
          OR i.patient_id IS DISTINCT FROM w.patient_id
          OR i.evaluator_uuid IS DISTINCT FROM w.evaluator_uuid""").fetchone()[0]
    if invalid:
        raise SystemExit(2)
    value = db.execute(SQL).fetchone()[0]
print(json.dumps(value))
'''
    # SET is separate so psycopg returns the SELECT result directly.
    sql = recovery_snapshot_sql().split('; ', 1)[1]
    result = stack.compose('run', '--rm', '--no-deps', '--interactive', '--entrypoint',
                           'python', 'web-provision', '-', input_text=helper.replace('SQL', repr(sql)))
    snapshot = json.loads(result)
    for table in ('web_patients', 'web_evaluators', 'web_registry_audit_events',
                  'auth_audit_events', 'web_assessments', 'web_local_credentials',
                  'web_local_sessions'):
        stack._assert(snapshot[table]['count'] > 0)
    return snapshot


def verify_receipt_rejection(stack, root, key):
    """Uma copia da fixture com recibo desvinculado deve falhar na restauracao."""
    helper = '''import os
import psycopg
from api.config import secret_value
with psycopg.connect(secret_value(os.environ, 'API_MIGRATION_DATABASE_URL')) as db:
    db.execute(SQL)
'''

    def update_receipt(value):
        sql = ("UPDATE web_assessments SET receipt=jsonb_set(receipt, "
               "'{assessment_id}', to_jsonb(" + value + "))")
        stack.compose('run', '--rm', '--no-deps', '--interactive', '--entrypoint',
                      'python', 'web-provision', '-',
                      input_text=helper.replace('SQL', repr(sql)))

    update_receipt("'00000000-0000-0000-0000-000000000000'::text")
    try:
        backup = create_backup(
            compose_file=Path(__file__).resolve().parents[1] / 'compose.web.yaml',
            key_file=key, output_directory=root / 'invalid-receipt-backups',
            database=SYNTHETIC_DATABASE, user='stroop_owner', service='web-postgres',
            project_name=stack.project, env_file=stack.environment_file,
        )
        try:
            restore_isolated(backup, key, verify_web=True)
        except BackupError as error:
            if str(error) != 'Restauracao isolada sem verificacao estrutural.':
                raise
        else:
            raise RuntimeError('Recibo desvinculado aceito indevidamente')
    finally:
        update_receipt('assessment_id::text')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-image', default=API_IMAGE)
    parser.add_argument('--proxy-image', default=PROXY_IMAGE)
    options = parser.parse_args(argv)
    stack = None
    candidate = None
    stage = 'stack'
    try:
        with tempfile.TemporaryDirectory(prefix='stroop-web-recovery-') as directory:
            root = Path(directory)
            stack = RecoveryComposeSmoke(root, False, api_image=options.api_image,
                                    proxy_image=options.proxy_image)
            try:
                stack.run()
                stage = 'monitor'
                before = check(stack.environment_file, stack.project)
                stack._assert(before['status'] == 'ready' and before['counts']['web_assessments'] == 1)
                key = root / 'keys' / 'recovery.key'
                key.parent.mkdir(mode=0o700)
                generate_key(key)
                snapshot = recovery_snapshot(stack)
                started = time.monotonic()
                stage = 'backup'
                backup = create_backup(compose_file=Path(__file__).resolve().parents[1] / 'compose.web.yaml',
                    key_file=key, output_directory=root / 'backups', database=SYNTHETIC_DATABASE,
                    user='stroop_owner', service='web-postgres', project_name=stack.project,
                    env_file=stack.environment_file)
                stage = 'restore'
                migrations, assessments = restore_isolated(backup, key, verify_web=True,
                                                            expected_snapshot=snapshot)
                stack._assert(migrations == len(discover_migrations()) and assessments == 1)
                restoration_seconds = round(time.monotonic() - started, 3)
                stage = 'invalid-snapshot'
                changed = {name: dict(value) for name, value in snapshot.items()}
                changed['assessment_metrics']['sha256'] = '0' * 64
                try:
                    restore_isolated(backup, key, verify_web=True, expected_snapshot=changed)
                except BackupError as error:
                    if str(error) != 'Restauracao isolada diverge da origem sintetica.':
                        raise
                else:
                    raise RuntimeError('Conteudo divergente com mesma contagem aceito')
                stage = 'invalid-receipt'
                verify_receipt_rejection(stack, root, key)
                stage = 'outage'
                stack.compose('stop', 'web-postgres')
                outage = check(stack.environment_file, stack.project)
                stack._assert(outage['alert'] and outage['status'] == 'unavailable')
                stack.compose('start', 'web-postgres')
                stack.wait_healthy('web-postgres')
                stack.wait_healthy('web-api')
                # Candidato deliberadamente invalido, sem alterar a imagem aceita.
                stage = 'rollback'
                candidate = stack.project + ':invalid-candidate'
                context = root / 'candidate-context'
                context.mkdir(mode=0o700)
                dockerfile = context / 'Dockerfile'
                dockerfile.write_text(f'FROM {stack.api_image}\nENTRYPOINT ["python","-c","raise SystemExit(1)"]\n')
                _run(['docker','build','-f',str(dockerfile),'-t',candidate,str(context)])
                override = root / 'rollback.yaml'
                override.write_text(f'services:\n  web-api:\n    image: {candidate}\n    restart: "no"\n')
                _run([*stack._compose_prefix,'-f',str(override),'up','-d','--no-deps','--no-build','web-api'])
                time.sleep(2)
                stack._assert(check(stack.environment_file,stack.project)['alert'])
                stack.compose('up','-d','--no-deps','--no-build','--force-recreate','web-api')
                stack.wait_healthy('web-api')
                after = check(stack.environment_file, stack.project)
                stack._assert(after['status'] == 'ready' and after['counts'] == before['counts'])
                print(json.dumps({'status':'passed','restoration_seconds':restoration_seconds,
                    'restored_assessments':assessments,'restored_migrations':migrations,'database_outage_detected':True,
                    'invalid_receipt_rejected':True,
                    'same_count_changed_content_rejected':True,
                    'registry_links_metrics_audit_snapshot_verified':True,
                    'restored_table_counts':{name: value['count'] for name, value in snapshot.items()},
                    'failed_candidate_rollback':True,'counts_preserved':True}))
            finally:
                stack.cleanup()
                stack = None
        return 0
    except Exception as error:
        print(f'Ensaio WEB de recuperacao falhou em {stage} ({type(error).__name__}); detalhes suprimidos.',file=sys.stderr)
        return 1
    finally:
        if candidate:
            subprocess.run(['docker','image','rm',candidate],capture_output=True,check=False)


if __name__ == '__main__':
    raise SystemExit(main())
