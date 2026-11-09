"""Provisionamento WEB explicito, transacional e restrito a papeis gerenciados."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Mapping

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.config import postgres_database_url, secret_value
from stroop.persistence.web_assessments import REQUIRED_COLUMNS


ROLE = re.compile(r'^[a-z][a-z0-9_]{0,62}$')
MARKER = 'stroop-web-role-v1'
LOCK_ID = 849403019
# DML operacional; nunca conceder UPDATE/INSERT de usuarios ou mapa legado.
WRITER = {
    'schema_migrations': ('SELECT',),
    'web_local_credentials': ('SELECT', 'UPDATE (password_hash,credential_version,updated_at)'),
    'web_local_sessions': ('SELECT', 'INSERT', 'UPDATE (last_activity_at,revoked_at)', 'DELETE'),
    'web_local_auth_limits': ('SELECT', 'INSERT', 'UPDATE', 'DELETE'),
    'web_local_auth_events': ('INSERT (principal_id,action)',),
    'app_users': ('SELECT (issuer,subject,email,role,active)',),
    'auth_audit_events': ('SELECT (issuer,subject,outcome,occurred_at)',
                          'INSERT (issuer,subject,action,outcome,request_id)'),
    'web_oidc_transactions': ('SELECT', 'INSERT', 'DELETE'),
    'web_professional_sessions': ('SELECT', 'INSERT', 'DELETE'),
    'web_login_rate_limits': ('SELECT', 'INSERT', 'UPDATE', 'DELETE'),
    'web_projects': ('SELECT', 'INSERT', 'UPDATE (name)'),
    'web_project_members': ('SELECT', 'INSERT', 'UPDATE (active,updated_at)'),
    'web_invitations': ('SELECT', 'INSERT', 'UPDATE (state,redeemed_at,revoked_at)'),
    'web_participant_sessions': ('SELECT', 'INSERT',
        'UPDATE (state,started_at,app_version,revoked_at,abort_reason,participant_token_sha256)'),
    'web_session_main_order': ('SELECT', 'INSERT'),
    'web_project_participants': ('SELECT', 'INSERT', 'UPDATE (patient_id)'),
    'web_participant_visits': ('SELECT', 'INSERT'),
    'web_patients': (
        'SELECT', 'INSERT',
        'UPDATE (full_name,normalized_name,initials,disambiguation_note,is_homonym_confirmed,active,updated_at)',
    ),
    'web_evaluators': (
        'SELECT', 'INSERT',
        'UPDATE (full_name,normalized_name,initials,active,updated_at)',
    ),
    'web_registry_audit_events': ('SELECT', 'INSERT'),
    'web_legacy_entity_links': ('SELECT', 'INSERT', 'UPDATE (active)'),
    'web_session_observations': ('SELECT', 'INSERT'),
    'web_session_checkpoints': ('SELECT', 'INSERT',
        'UPDATE (confirmed_through,prefix_hash,received_at)'),
    'web_session_invalidations': ('SELECT', 'INSERT'),
    'web_participant_redeem_limits': ('SELECT', 'INSERT', 'UPDATE', 'DELETE'),
    'web_professional_request_limits': ('SELECT', 'INSERT', 'UPDATE', 'DELETE'),
    'web_participant_request_limits': ('SELECT', 'INSERT', 'UPDATE', 'DELETE'),
    'assessments': ('SELECT (assessment_id)', 'INSERT'), 'trial_results': ('INSERT',),
    'assessment_metrics': ('INSERT',), 'web_assessments': ('SELECT', 'INSERT'),
    'web_trial_observations': ('SELECT (assessment_id,trial_number,trial_end_ms)', 'INSERT'),
    'web_csv_imports': ('SELECT', 'INSERT', 'UPDATE'),
}


class ProvisionError(RuntimeError):
    """Erro fechado de preparacao, nunca com DSN/role/password retornados."""


def _fail():
    raise ProvisionError('Provisionamento WEB recusado; verifique a configuracao e o baseline do banco.') from None


def configuration(environment: Mapping[str, str]) -> tuple[str, dict, dict]:
    dsns = [postgres_database_url(secret_value(environment, key)) for key in
            ('API_MIGRATION_DATABASE_URL', 'API_DATABASE_URL', 'API_READ_DATABASE_URL')]
    parts = [conninfo_to_dict(value) for value in dsns]
    endpoints = [(item.get('host', ''), item.get('hostaddr', ''), item.get('port', '5432'), item['dbname']) for item in parts]
    if len(set(endpoints)) != 1 or len({item.get('user') for item in parts}) != 3:
        _fail()
    for item in parts:
        if (not ROLE.fullmatch(item.get('user', '')) or item['user'].startswith('pg_')
                or not item.get('password') or ',' in item.get('host', '')
                or ',' in item.get('port', '')):
            _fail()
        # DSN nao pode selecionar outro papel/search_path por opcoes libpq.
        if any(key not in {'host', 'hostaddr', 'port', 'dbname', 'user', 'password', 'sslmode',
                           'sslrootcert', 'sslcert', 'sslkey', 'connect_timeout', 'application_name',
                           'channel_binding', 'target_session_attrs'} for key in item):
            _fail()
    return dsns[0], parts[1], parts[2]


def _baseline(connection):
    # Nao modificar PUBLIC em banco compartilhado. Baseline inseguro exige acao do operador.
    if connection.execute("""SELECT EXISTS (
        SELECT 1 FROM pg_namespace n, LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) a
        WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema'
          AND a.grantee=0 AND a.privilege_type='CREATE')""").fetchone()[0]:
        _fail()
    if connection.execute("""SELECT EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace,
        LATERAL aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) a
        WHERE n.nspname='public' AND c.relkind IN ('r','p','S') AND a.grantee=0)""").fetchone()[0]:
        _fail()
    if connection.execute("""SELECT EXISTS (
        SELECT 1 FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace,
        LATERAL aclexplode(a.attacl) acl WHERE n.nspname='public' AND acl.grantee=0)""").fetchone()[0]:
        _fail()
    if connection.execute("""SELECT EXISTS (
        SELECT 1 FROM pg_database d,
        LATERAL aclexplode(COALESCE(d.datacl,acldefault('d',d.datdba))) a
        WHERE d.datname=current_database() AND a.grantee=0 AND a.privilege_type='CREATE')""").fetchone()[0]:
        _fail()
    # Uma funcao DEFINER desconhecida e executavel por PUBLIC ampliaria os papeis.
    if connection.execute("""SELECT EXISTS (
        SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace,
        LATERAL aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a
        WHERE n.nspname='public' AND p.prosecdef AND a.grantee=0 AND a.privilege_type='EXECUTE')""").fetchone()[0]:
        _fail()


def _role(connection, settings, kind, db_oid, owner_oid):
    name = settings['user']
    marker = f'{MARKER}:{db_oid}:{owner_oid}:{kind}'
    row = connection.execute("""SELECT oid,rolsuper,rolcreaterole,rolcreatedb,rolreplication,rolbypassrls,
        shobj_description(oid,'pg_authid') FROM pg_roles WHERE rolname=%s""", (name,)).fetchone()
    if row:
        oid = row[0]
        if any(row[1:6]) or row[6] != marker:
            _fail()
        if connection.execute('SELECT EXISTS(SELECT 1 FROM pg_auth_members WHERE roleid=%s OR member=%s)', (oid, oid)).fetchone()[0]:
            _fail()
        if connection.execute("SELECT EXISTS(SELECT 1 FROM pg_shdepend WHERE refclassid='pg_authid'::regclass AND refobjid=%s AND (deptype='o' OR dbid NOT IN (0,%s)))", (oid, db_oid)).fetchone()[0]:
            _fail()
        if connection.execute("""SELECT EXISTS (
            SELECT 1 FROM pg_shdepend d,
              LATERAL pg_identify_object(d.classid,d.objid,d.objsubid) identified
            WHERE d.refclassid='pg_authid'::regclass AND d.refobjid=%s AND d.deptype='a'
              AND ((d.dbid=%s AND identified.schema IS DISTINCT FROM 'public'
                   AND NOT (d.classid='pg_namespace'::regclass AND d.objid='public'::regnamespace))
                OR (d.dbid=0 AND d.classid='pg_database'::regclass AND d.objid<>%s)))""",
                (oid, db_oid, db_oid)).fetchone()[0]:
            _fail()
    else:
        connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT PASSWORD {}').format(sql.Identifier(name), sql.Literal(settings['password'])))
        connection.execute(sql.SQL('COMMENT ON ROLE {} IS {}').format(sql.Identifier(name), sql.Literal(marker)))
    connection.execute(sql.SQL('ALTER ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT PASSWORD {}').format(sql.Identifier(name), sql.Literal(settings['password'])))
    connection.execute(sql.SQL('ALTER ROLE {} RESET ALL').format(sql.Identifier(name)))
    # Limpeza e somente do papel exclusivo gerenciado, nunca PUBLIC/outros papeis.
    connection.execute(sql.SQL('REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM {}').format(sql.Identifier(name)))
    connection.execute(sql.SQL('REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM {}').format(sql.Identifier(name)))
    connection.execute(sql.SQL('REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM {}').format(sql.Identifier(name)))
    for table, columns in connection.execute("""SELECT c.relname,array_agg(a.attname ORDER BY a.attnum)
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
        WHERE n.nspname='public' AND c.relkind IN ('r','p') GROUP BY c.relname""").fetchall():
        connection.execute(sql.SQL('REVOKE ALL PRIVILEGES ({}) ON TABLE public.{} FROM {}').format(
            sql.SQL(',').join(map(sql.Identifier, columns)), sql.Identifier(table), sql.Identifier(name)))
    connection.execute(sql.SQL('REVOKE ALL PRIVILEGES ON SCHEMA public FROM {}').format(sql.Identifier(name)))
    connection.execute(sql.SQL('GRANT USAGE ON SCHEMA public TO {}').format(sql.Identifier(name)))
    return name


def provision(environment: Mapping[str, str] | None = None):
    values = os.environ if environment is None else environment
    try:
        owner_dsn, writer, reader = configuration(values)
        with psycopg.connect(owner_dsn, connect_timeout=5) as connection:
            connection.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
            db_name, db_oid, owner_oid = connection.execute("SELECT current_database(),(SELECT oid FROM pg_database WHERE datname=current_database()),(SELECT oid FROM pg_roles WHERE rolname=current_user)").fetchone()
            _baseline(connection)
            functions = ('public.web_lock_emitter(text,text)',
                         'public.web_manage_user(text,text,text,text,text,text,text,boolean)')
            for signature in functions:
                function = connection.execute('SELECT proowner,prosecdef FROM pg_proc WHERE oid=to_regprocedure(%s)', (signature,)).fetchone()
                if not function or function != (owner_oid, True):
                    _fail()
            writer_name = _role(connection, writer, 'writer', db_oid, owner_oid)
            reader_name = _role(connection, reader, 'reader', db_oid, owner_oid)
            for name in (writer_name, reader_name):
                connection.execute(sql.SQL('REVOKE ALL PRIVILEGES ON DATABASE {} FROM {}').format(sql.Identifier(db_name), sql.Identifier(name)))
                connection.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(sql.Identifier(db_name), sql.Identifier(name)))
            for table, privileges in WRITER.items():
                for privilege in privileges:
                    connection.execute(sql.SQL('GRANT {} ON TABLE public.{} TO {}').format(sql.SQL(privilege), sql.Identifier(table), sql.Identifier(writer_name)))
            for table, columns in REQUIRED_COLUMNS.items():
                connection.execute(sql.SQL('GRANT SELECT ({}) ON TABLE public.{} TO {}').format(
                    sql.SQL(',').join(map(sql.Identifier, sorted(columns))), sql.Identifier(table), sql.Identifier(reader_name)))
            for sequence in (
                'auth_audit_events_audit_id_seq',
                'trial_results_trial_result_id_seq',
                'assessment_metrics_metric_id_seq',
                'web_patient_code_seq',
                'web_evaluator_code_seq',
            ):
                connection.execute(sql.SQL('GRANT USAGE ON SEQUENCE public.{} TO {}').format(sql.Identifier(sequence), sql.Identifier(writer_name)))
            connection.execute(sql.SQL('GRANT EXECUTE ON FUNCTION public.web_lock_emitter(text,text) TO {}').format(sql.Identifier(writer_name)))
            connection.execute(sql.SQL('GRANT EXECUTE ON FUNCTION public.web_manage_user(text,text,text,text,text,text,text,boolean) TO {}').format(sql.Identifier(writer_name)))
    except ProvisionError:
        raise
    except Exception:
        _fail()


def main():
    try:
        provision()
    except Exception:
        print('Provisionamento WEB recusado; verifique a configuracao e o baseline do banco.', file=sys.stderr)
        return 1
    print('Papeis WEB provisionados.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
