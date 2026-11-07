#!/usr/bin/env python3
"""Ensaio descartavel de restore local fechado ate recuperacao do operador.

Nao saneia backups automaticamente nem opera ambiente existente. Cria pilha e
banco novos, restaura snapshot antigo sem servir esse banco, recupera a conta e
so entao testa API em processo com writer/reader dedicados. Secrets sinteticos
ficam em memoria/stdin; dump fica apenas no container descartavel.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import secrets
import sys
import tempfile

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.smoke_web_compose import HOST, SYNTHETIC_DATABASE, WebComposeSmoke


def _operator(stack, helper):
    return stack.compose('run', '--rm', '--no-deps', '--interactive', '--entrypoint',
                         'python', 'web-provision', '-', input_text=helper)


def verify_restore(stack):
    before_password = secrets.token_urlsafe(36)
    source_password = secrets.token_urlsafe(36)
    restored_password = secrets.token_urlsafe(36)
    # O fluxo existente completa coleta, consulta, CSV e replay reais em HTTPS.
    project_id, assessment_id, original_admin, _ = stack._collect_and_query()
    username = 'synthetic-smoke-admin'
    seed = f'''import os
from api.config import secret_value
from stroop.application.local_auth import provision
assert provision(secret_value(os.environ,'API_MIGRATION_DATABASE_URL'),{username!r},{before_password!r},recover=True)
print('prepared')
'''
    stack._assert(_operator(stack, seed) == 'prepared')
    origin = f'https://{HOST}:{stack.https_port}'
    status, headers, profile = stack._json_request('POST', '/api/v1/auth/login',
        {'username': username, 'password': before_password}, {'Origin': origin})
    stack._assert(status == 200 and profile['user_id'] == original_admin['user_id'])
    token = headers['set-cookie'].split(';', 1)[0].partition('=')[2]
    admin = {'cookie': token, 'csrf': profile['csrf_token'], 'user_id': profile['user_id']}
    # Somente colunas concedidas ao reader; nenhuma ampliacao para recibo/hash.
    queries = [
        ('assessment', 'SELECT assessment_id,test_code,test_version,project,participant_id,visit,evaluator,assessment_date,started_at,imported_at,import_status FROM assessments WHERE assessment_id=%s'),
        ('trials', 'SELECT assessment_id,block,trial_number,word,ink_color,condition,correct_response,key_pressed,reaction_time,correct,error_type FROM trial_results WHERE assessment_id=%s ORDER BY block,trial_number'),
        ('metrics', 'SELECT assessment_id,metric_code,metric_label,metric_value,unit FROM assessment_metrics WHERE assessment_id=%s ORDER BY metric_code'),
        ('provenance', 'SELECT assessment_id,session_id,project_id,platform,protocol_id,app_version,frame_period_ms,completed_at FROM web_assessments WHERE assessment_id=%s'),
        ('observations', 'SELECT assessment_id,trial_number,condition_id,trial_start_ms,stimulus_onset_ms,stimulus_offset_ms,trial_end_ms,key_at_ms,reaction_time_ms FROM web_trial_observations WHERE assessment_id=%s ORDER BY trial_number'),
    ]
    fingerprint_code = f'''def fingerprint(database_url):
    with psycopg.connect(database_url) as db:
        db.execute('SET TRANSACTION READ ONLY')
        rows={{name:db.execute(query,({assessment_id!r},)).fetchall() for name,query in {queries!r}}}
    assert [len(rows[name]) for name in ('assessment','trials','metrics','provenance','observations')]==[1,16,12,1,16]
    return hashlib.sha256(json.dumps(rows,default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def receipt_fingerprint(owner):
    with psycopg.connect(owner) as db:
        row=db.execute('SELECT receipt,payload_sha256,session_id FROM web_assessments WHERE assessment_id=%s',({assessment_id!r},)).fetchone()
    assert row[0]['assessment_id']=={assessment_id!r} and row[0]['state']=='completed'
    assert row[0]['session_id']==str(row[2]) and row[0]['platform']=='web'
    return hashlib.sha256(json.dumps(row,default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()
'''
    capture = f'''import hashlib,json,os,psycopg
from api.config import secret_value
{fingerprint_code}
owner=secret_value(os.environ,'API_MIGRATION_DATABASE_URL')
reader=secret_value(os.environ,'API_READ_DATABASE_URL')
with psycopg.connect(owner) as db:
    version=db.execute('SELECT credential_version FROM web_local_credentials').fetchone()[0]
print(json.dumps({{'science':fingerprint(reader),'receipt':receipt_fingerprint(owner),'credential_version':version}}))
'''
    before = json.loads(_operator(stack, capture))

    snapshot = '/tmp/synthetic-local-auth-' + secrets.token_hex(6) + '.dump'
    target = 'stroop_etapa4_test_restore_local_' + secrets.token_hex(6)
    # Cliente PostgreSQL 17 do proprio container; nenhum dump antigo/real e aberto.
    stack.compose('exec', '-T', 'web-postgres', 'pg_dump', '--username', 'stroop_owner',
                  '--dbname', SYNTHETIC_DATABASE, '--format=custom', '--file', snapshot)
    rotate = f'''import os
from api.config import secret_value
from stroop.application.local_auth import provision, session_context
from hashlib import sha256
owner=secret_value(os.environ,'API_MIGRATION_DATABASE_URL')
assert provision(owner,{username!r},{source_password!r},recover=True)
assert session_context(owner,sha256({token!r}.encode()).hexdigest(),'view_dashboard')[0]=='invalid'
print('rotated')
'''
    stack._assert(_operator(stack, rotate) == 'rotated')
    stack.compose('exec', '-T', 'web-postgres', 'createdb', '--username', 'stroop_owner', target)
    stack.compose('exec', '-T', 'web-postgres', 'psql', '--username', 'stroop_owner',
                  '--dbname', target, '--set=ON_ERROR_STOP=1', '--command',
                  f'REVOKE CONNECT ON DATABASE {target} FROM PUBLIC')
    # Mantem ACL das funcoes. As roles do banco fonte nao recebem CONNECT no alvo.
    stack.compose('exec', '-T', 'web-postgres', 'pg_restore', '--username', 'stroop_owner',
                  '--dbname', target, '--exit-on-error', '--single-transaction', '--no-owner', snapshot)
    helper = f'''import base64, hashlib, json, os, secrets
from urllib.parse import urlsplit, urlunsplit
import psycopg
from psycopg import sql
from api.config import APIConfig, secret_value
from api.main import create_app
from fastapi.testclient import TestClient
from scripts.provision_web_database import provision as provision_roles
from stroop.application import local_auth

def target_url(value):
    parts=urlsplit(value)
    return urlunsplit((parts.scheme,parts.netloc,'/'+{target!r},parts.query,''))
owner=target_url(secret_value(os.environ,'API_MIGRATION_DATABASE_URL'))
old_hash=hashlib.sha256({token!r}.encode()).hexdigest()
expected_subject=base64.urlsafe_b64decode({admin['user_id']!r}+'==').decode().split('\\0',1)[1]
with psycopg.connect(owner) as db:
    principal,version=db.execute('SELECT principal_id,credential_version FROM web_local_credentials').fetchone()
    assert str(principal)==expected_subject and version=={before['credential_version']!r}
    assert db.execute('SELECT revoked_at FROM web_local_sessions WHERE token_sha256=%s',(old_hash,)).fetchone()==(None,)
    assert not db.execute("SELECT has_database_privilege('stroop_writer',%s,'CONNECT')",({target!r},)).fetchone()[0]
    assert not db.execute("SELECT has_database_privilege('stroop_reader',%s,'CONNECT')",({target!r},)).fetchone()[0]
# O snapshot antigo contem credencial/token antigos; nao e servido nessa condicao.
assert local_auth.provision(owner,{username!r},{restored_password!r},recover=True)
assert local_auth.session_context(owner,old_hash,'view_dashboard')[0]=='invalid'
with psycopg.connect(owner) as db:
    assert db.execute('SELECT principal_id,credential_version FROM web_local_credentials').fetchone()==(principal,{before['credential_version']+1!r})
    assert db.execute('SELECT count(*) FROM web_project_members WHERE project_id=%s AND subject=%s AND active',({project_id!r},expected_subject)).fetchone()==(1,)
    assert db.execute('SELECT count(*) FROM web_local_sessions WHERE revoked_at IS NULL').fetchone()==(0,)
    db.execute(sql.SQL('REVOKE CREATE ON DATABASE {{}} FROM PUBLIC').format(sql.Identifier({target!r})))
    db.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
# Somente depois da recuperacao, novas roles dedicadas recebem CONNECT/grants.
suffix=secrets.token_hex(5)
root=urlsplit(owner)
def role_url(kind):
    return urlunsplit((root.scheme,kind+'_'+suffix+':'+secrets.token_urlsafe(24)+'@'+root.hostname+':'+str(root.port),root.path,root.query,''))
writer,reader=role_url('restore_writer'),role_url('restore_reader')
provision_roles({{'API_MIGRATION_DATABASE_URL':owner,'API_DATABASE_URL':writer,'API_READ_DATABASE_URL':reader}})
{fingerprint_code}
assert fingerprint(reader)=={before['science']!r}
assert receipt_fingerprint(owner)=={before['receipt']!r}
with psycopg.connect(reader) as db:
    assert not db.execute("SELECT has_column_privilege(current_user,'public.web_assessments','receipt','SELECT')").fetchone()[0]
config=APIConfig(database_url=writer,read_database_url=reader,public_origin={origin!r},app_env='test',
                 session_secret=secrets.token_urlsafe(48),auth_mode='local')
with TestClient(create_app(config),base_url={origin!r}) as client:
    client.cookies.set('__Host-stroop_professional',{token!r})
    assert client.get('/api/v1/auth/me').status_code==401
    client.cookies.clear()
    for password in ({before_password!r},{source_password!r}):
        assert client.post('/api/v1/auth/login',json={{'username':{username!r},'password':password}},headers={{'Origin':{origin!r}}}).status_code==401
    response=client.post('/api/v1/auth/login',json={{'username':{username!r},'password':{restored_password!r}}},headers={{'Origin':{origin!r}}})
    assert response.status_code==200
    assert response.json()['user_id']=={admin['user_id']!r}
    response=client.get('/api/v1/projects')
    assert response.status_code==200 and any(row['id']=={project_id!r} for row in response.json()['items'])
print(json.dumps({{'status':'passed','old_token_rejected':True,'old_passwords_rejected':True,
    'new_login_status':200,'principal_and_project_grant_preserved':True,'credential_version':{before['credential_version']+1!r},
    'assessment_preserved':True,'trials_preserved':16,'metrics_preserved':12,'observations_preserved':16,
    'science_checked_by_restricted_reader':True,'canonical_receipt_checked_by_operator':True,
    'reader_receipt_privilege_not_expanded':True,
    'restore_closed_until_operator_recovery':True,'automatic_backup_sanitization':False,
    'restored_api_transport':'in-process TestClient after recovery'}}))
'''
    report = json.loads(_operator(stack, helper))
    stack._assert(report['status'] == 'passed')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-image', default='stroop-web-api:m6-final')
    parser.add_argument('--proxy-image', default='stroop-web-proxy:m6-final')
    args = parser.parse_args(argv)
    stack = None
    try:
        with tempfile.TemporaryDirectory(prefix='stroop-local-auth-restore-') as directory:
            stack = WebComposeSmoke(Path(directory), False, api_image=args.api_image, proxy_image=args.proxy_image)
            try:
                stack.start_stack()
                report = verify_restore(stack)
                print(json.dumps(report))
            finally:
                stack.cleanup()
        return 0
    except Exception:
        print('Restore local sintetico falhou; detalhes e secrets suprimidos.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
