"""Persistencia transacional dos projetos, convites e sessoes WEB."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from uuid import uuid4

from stroop.persistence.auth import PersistenceError
from stroop.domain.auth import opaque_user_id


@dataclass(frozen=True, slots=True)
class SessionRecord:
    session_id: UUID
    state: str
    activated_at: datetime
    expires_at: datetime
    started_at: datetime | None
    app_version: str | None
    order: tuple[int, ...]
    receipt: dict | None = None


class ConflictError(Exception):
    """Transicao concorrente ou recurso em estado incompatível."""


class ResultConflictError(ConflictError):
    """A sessao ja possui resultado diferente do payload recebido."""


class ExpiredError(Exception):
    """Convite ou sessao ja expirados."""


class MissingError(Exception):
    """Recurso inexistente ou fora do escopo atual."""


class UnknownCredentialError(MissingError):
    """Credencial estruturalmente valida, mas nao emitida pelo servidor."""


def project_invitation_access(database_url: str, project_id: UUID,
                              issuer: str, subject: str) -> str:
    def operation():
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                """SELECT p.active,m.active,u.active,u.role
                   FROM web_projects p
                   LEFT JOIN web_project_members m ON m.project_id=p.project_id
                     AND m.issuer=%s AND m.subject=%s
                   LEFT JOIN app_users u ON (u.issuer,u.subject)=(%s,%s)
                   WHERE p.project_id=%s""",
                (issuer, subject, issuer, subject, project_id),
            ).fetchone()
        if row is None or not row[0] or row[1] is not True or row[2] is not True:
            return "not_found"
        return "allowed" if row[3] in {"importacao", "administracao"} else "forbidden"
    return _run(operation)


def _run(operation):
    try:
        return operation()
    except (psycopg.Error, ValueError) as exc:
        raise PersistenceError from exc


def _audit(connection, issuer: str, subject: str, action: str) -> None:
    connection.execute(
        """INSERT INTO auth_audit_events(issuer,subject,action,outcome,request_id)
           VALUES (%s,%s,%s,'success',%s)""",
        (issuer, subject, action, uuid4()),
    )


def list_projects(database_url: str, issuer: str, subject: str, *, all_projects: bool,
                  limit: int, offset: int):
    def operation():
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            if all_projects:
                rows = connection.execute(
                    """SELECT p.project_id AS id, p.code, p.name, p.active, p.created_at
                       FROM web_projects p ORDER BY p.created_at, p.project_id LIMIT %s OFFSET %s""",
                    (limit, offset),
                ).fetchall()
            else:
                rows = connection.execute(
                    """SELECT p.project_id AS id, p.code, p.name, p.active, p.created_at
                       FROM web_projects p JOIN web_project_members m USING (project_id)
                       WHERE m.issuer=%s AND m.subject=%s AND m.active
                       ORDER BY p.created_at, p.project_id LIMIT %s OFFSET %s""",
                    (issuer, subject, limit, offset),
                ).fetchall()
        return rows
    return _run(operation)


def create_project(database_url: str, project_id: UUID, code: str, name: str,
                   issuer: str, subject: str):
    def operation():
        with psycopg.connect(database_url) as connection:
            created_at = connection.execute(
                """INSERT INTO web_projects
                   (project_id, code, name, created_by_issuer, created_by_subject)
                   VALUES (%s, %s, %s, %s, %s) RETURNING created_at""",
                (project_id, code, name, issuer, subject),
            ).fetchone()[0]
            _audit(connection, issuer, subject, "manage_projects")
            return created_at
    try:
        return operation()
    except psycopg.errors.UniqueViolation as exc:
        raise ConflictError from exc
    except psycopg.Error as exc:
        raise PersistenceError from exc


def list_members(database_url: str, project_id: UUID, limit: int, offset: int):
    def operation():
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            if connection.execute("SELECT 1 FROM web_projects WHERE project_id=%s", (project_id,)).fetchone() is None:
                return None
            return connection.execute(
                """SELECT m.issuer, m.subject, m.active
                   FROM web_project_members m WHERE m.project_id=%s
                   ORDER BY m.issuer, m.subject LIMIT %s OFFSET %s""", (project_id, limit, offset)
            ).fetchall()
    return _run(operation)


def set_member(database_url: str, project_id: UUID, issuer: str, subject: str,
               active: bool, actor_issuer: str, actor_subject: str) -> bool:
    def operation():
        with psycopg.connect(database_url) as connection:
            project = connection.execute(
                "SELECT 1 FROM web_projects WHERE project_id=%s", (project_id,)
            ).fetchone()
            user = connection.execute(
                "SELECT 1 FROM app_users WHERE issuer=%s AND subject=%s",
                (issuer, subject),
            ).fetchone()
            if project is None or user is None:
                return False
            connection.execute(
                """INSERT INTO web_project_members(project_id, issuer, subject, active)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (project_id, issuer, subject) DO UPDATE SET
                     active=EXCLUDED.active, updated_at=CURRENT_TIMESTAMP""",
                (project_id, issuer, subject, active),
            )
            _audit(connection, actor_issuer, actor_subject, "manage_project_members")
            return True
    return _run(operation)


def create_invitation(database_url: str, invitation_id: UUID, session_id: UUID,
                      project_id: UUID, code_hash: str, participant_id: str,
                      visit: str, issuer: str, subject: str):
    def operation():
        with psycopg.connect(database_url) as connection:
            project = connection.execute(
                "SELECT active,collection_mode FROM web_projects WHERE project_id=%s FOR SHARE",
                (project_id,),
            ).fetchone()
            member = connection.execute(
                "SELECT active FROM web_project_members WHERE project_id=%s AND issuer=%s AND subject=%s FOR SHARE",
                (project_id, issuer, subject),
            ).fetchone()
            user = connection.execute(
                "SELECT active,role FROM app_users WHERE issuer=%s AND subject=%s FOR SHARE",
                (issuer, subject),
            ).fetchone()
            if (project is None or not project[0] or project[1] != 'synthetic'
                    or member is None or not member[0] or user is None
                    or not user[0] or user[1] not in {'importacao','administracao'}):
                return False
            connection.execute(
                """INSERT INTO web_invitations
                   (invitation_id,session_id,project_id,code_sha256,participant_id,visit,
                    evaluator_issuer,evaluator_subject,expires_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,
                           CURRENT_TIMESTAMP + INTERVAL '24 hours')""",
                (invitation_id, session_id, project_id, code_hash, participant_id,
                 visit, issuer, subject),
            )
            _audit(connection, issuer, subject, "create_invitation")
            return connection.execute(
                "SELECT expires_at FROM web_invitations WHERE invitation_id=%s",
                (invitation_id,),
            ).fetchone()[0]
    return _run(operation)


def revoke_invitation(database_url: str, project_id: UUID, invitation_id: UUID,
                      issuer: str, subject: str) -> bool:
    def operation():
        with psycopg.connect(database_url) as connection:
            project = connection.execute(
                "SELECT active FROM web_projects WHERE project_id=%s FOR SHARE",
                (project_id,),
            ).fetchone()
            member = connection.execute(
                "SELECT active FROM web_project_members WHERE project_id=%s AND issuer=%s AND subject=%s FOR SHARE",
                (project_id, issuer, subject),
            ).fetchone()
            user = connection.execute(
                "SELECT active,role FROM app_users WHERE issuer=%s AND subject=%s FOR SHARE",
                (issuer, subject),
            ).fetchone()
            if (project is None or not project[0] or member is None or not member[0]
                    or user is None or not user[0]
                    or user[1] not in {'importacao','administracao'}):
                return False
            row = connection.execute(
                """SELECT session_id,state,revoked_at FROM web_invitations
                   WHERE project_id=%s AND invitation_id=%s FOR UPDATE""",
                (project_id, invitation_id)
            ).fetchone()
            if row is None:
                return False
            if row[1] == 'issued':
                connection.execute(
                    "UPDATE web_invitations SET state='revoked',revoked_at=CURRENT_TIMESTAMP WHERE invitation_id=%s",
                    (invitation_id,),
                )
            elif row[1] == 'redeemed' and row[2] is None:
                connection.execute(
                    "UPDATE web_invitations SET revoked_at=CURRENT_TIMESTAMP WHERE invitation_id=%s",
                    (invitation_id,),
                )
            connection.execute(
                "UPDATE web_participant_sessions SET revoked_at=COALESCE(revoked_at,CURRENT_TIMESTAMP) WHERE session_id=%s",
                (row[0],),
            )
            _audit(connection, issuer, subject, "revoke_invitation")
            return True
    return _run(operation)


def redeem_limit(database_url: str, remote_hash: str, limit: int,
                 window_seconds: int) -> tuple[bool, int]:
    def operation():
        with psycopg.connect(database_url) as connection:
            connection.execute(
                "DELETE FROM web_participant_redeem_limits WHERE window_started_at <= clock_timestamp() - make_interval(secs => %s * 2)",
                (window_seconds,),
            )
            row = connection.execute(
                """INSERT INTO web_participant_redeem_limits
                     (remote_sha256,window_started_at,request_count)
                   VALUES (%s,clock_timestamp(),1)
                   ON CONFLICT(remote_sha256) DO UPDATE SET
                     window_started_at=CASE WHEN web_participant_redeem_limits.window_started_at <= clock_timestamp()-make_interval(secs => %s)
                       THEN clock_timestamp() ELSE web_participant_redeem_limits.window_started_at END,
                     request_count=CASE WHEN web_participant_redeem_limits.window_started_at <= clock_timestamp()-make_interval(secs => %s)
                       THEN 1 ELSE LEAST(web_participant_redeem_limits.request_count+1,%s+1) END
                   RETURNING request_count,GREATEST(1,ceil(extract(epoch FROM
                     (window_started_at+make_interval(secs => %s)-clock_timestamp())))::integer)""",
                (remote_hash, window_seconds, window_seconds, limit, window_seconds),
            ).fetchone()
            return row[0] <= limit, row[1]
    return _run(operation)


def professional_request_limit(database_url: str, credential_hash: str, operation_name: str,
                               limit: int, window_seconds: int) -> tuple[bool, int]:
    return _credential_request_limit(database_url, credential_hash, operation_name,
                                      limit, window_seconds, participant=False)


def participant_request_limit(database_url: str, credential_hash: str, operation_name: str,
                              limit: int, window_seconds: int) -> tuple[bool, int]:
    return _credential_request_limit(database_url, credential_hash, operation_name,
                                      limit, window_seconds, participant=True)


def _credential_request_limit(database_url: str, credential_hash: str, operation_name: str,
                              limit: int, window_seconds: int, *, participant: bool):
    # Nomes fechados internos; nenhum identificador vem da requisicao.
    table = 'web_participant_request_limits' if participant else 'web_professional_request_limits'
    def operation():
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                f"""INSERT INTO {table}
                     (credential_sha256,operation,window_started_at,request_count)
                   VALUES (%s,%s,clock_timestamp(),1)
                   ON CONFLICT (credential_sha256,operation) DO UPDATE SET
                     window_started_at=CASE WHEN {table}.window_started_at <= clock_timestamp()-make_interval(secs => %s)
                       THEN clock_timestamp() ELSE {table}.window_started_at END,
                     request_count=CASE WHEN {table}.window_started_at <= clock_timestamp()-make_interval(secs => %s)
                       THEN 1 ELSE LEAST({table}.request_count+1,%s+1) END
                   RETURNING request_count,GREATEST(1,ceil(extract(epoch FROM
                     (window_started_at+make_interval(secs => %s)-clock_timestamp())))::integer)""",
                (credential_hash, operation_name, window_seconds, window_seconds, limit, window_seconds),
            ).fetchone()
            connection.execute(
                f"DELETE FROM {table} WHERE window_started_at <= clock_timestamp() - make_interval(secs => %s * 2)",
                (window_seconds,),
            )
            return row[0] <= limit, row[1]
    return _run(operation)


def redeem(database_url: str, code_hash: str, token_hash: str,
           condition_order: tuple[int, ...]):
    def operation():
        with psycopg.connect(database_url) as connection:
            candidate = connection.execute(
                """SELECT invitation_id,session_id,project_id,evaluator_issuer,evaluator_subject
                   FROM web_invitations WHERE code_sha256=%s""", (code_hash,)
            ).fetchone()
            if candidate is None:
                raise MissingError
            project = connection.execute(
                "SELECT active,collection_mode FROM web_projects WHERE project_id=%s FOR SHARE",
                (candidate[2],),
            ).fetchone()
            member = connection.execute(
                "SELECT active FROM web_project_members WHERE project_id=%s AND issuer=%s AND subject=%s FOR SHARE",
                (candidate[2],candidate[3],candidate[4]),
            ).fetchone()
            user = connection.execute(
                "SELECT active,role FROM app_users WHERE issuer=%s AND subject=%s FOR SHARE",
                (candidate[3],candidate[4]),
            ).fetchone()
            row = connection.execute(
                """SELECT invitation_id,session_id,state,expires_at,revoked_at
                   FROM web_invitations WHERE invitation_id=%s FOR UPDATE""",
                (candidate[0],),
            ).fetchone()
            if (project is None or not project[0] or project[1] != 'synthetic'
                    or member is None or not member[0] or user is None or not user[0]
                    or user[1] not in {'importacao','administracao'} or row[4] is not None):
                raise MissingError
            if row[2] == 'redeemed':
                raise ConflictError
            if row[2] == 'revoked':
                raise MissingError
            if row[2] == 'expired' or row[3] <= connection.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]:
                connection.execute("UPDATE web_invitations SET state='expired' WHERE invitation_id=%s", (row[0],))
                connection.commit()
                raise ExpiredError
            if row[2] != 'issued':
                raise MissingError
            connection.execute(
                "UPDATE web_invitations SET state='redeemed',redeemed_at=CURRENT_TIMESTAMP WHERE invitation_id=%s",
                (row[0],),
            )
            session = connection.execute(
                """INSERT INTO web_participant_sessions
                   (session_id,participant_token_sha256,state,activated_at,expires_at)
                   VALUES (%s,%s,'preparing',CURRENT_TIMESTAMP,
                           CURRENT_TIMESTAMP+INTERVAL '30 minutes')
                   RETURNING activated_at,expires_at""", (row[1],token_hash)
            ).fetchone()
            connection.cursor().executemany(
                "INSERT INTO web_session_main_order(session_id,trial_number,condition_id) VALUES (%s,%s,%s)",
                [(row[1], index, condition_id) for index, condition_id in enumerate(condition_order, 1)],
            )
            return {"invitation_id": row[0], "session_id": row[1], "state": "preparing",
                    "activated_at": session[0], "expires_at": session[1], "order": condition_order}
    try:
        return operation()
    except (MissingError, ExpiredError, ConflictError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _eligible_session(connection, token_hash: str):
    candidate = connection.execute(
        """SELECT s.session_id,i.project_id,i.evaluator_issuer,i.evaluator_subject
           FROM web_participant_sessions s JOIN web_invitations i USING(session_id)
           WHERE s.participant_token_sha256=%s""",
        (token_hash,),
    ).fetchone()
    if candidate is None:
        raise UnknownCredentialError
    project = connection.execute(
        "SELECT active FROM web_projects WHERE project_id=%s FOR SHARE", (candidate[1],)
    ).fetchone()
    member = connection.execute(
        "SELECT active FROM web_project_members WHERE project_id=%s AND issuer=%s AND subject=%s FOR SHARE",
        (candidate[1],candidate[2],candidate[3]),
    ).fetchone()
    user = connection.execute(
        "SELECT active,role FROM app_users WHERE issuer=%s AND subject=%s FOR SHARE",
        (candidate[2],candidate[3]),
    ).fetchone()
    invitation = connection.execute(
        "SELECT revoked_at FROM web_invitations WHERE session_id=%s FOR UPDATE",
        (candidate[0],),
    ).fetchone()
    if (project is None or not project[0] or member is None or not member[0]
            or user is None or not user[0]
            or user[1] not in {'importacao','administracao'}
            or invitation is None or invitation[0] is not None):
        raise MissingError
    row = connection.execute(
        """SELECT s.session_id,s.state,s.activated_at,s.expires_at,s.started_at,s.app_version,
                  i.project_id,i.evaluator_issuer,i.evaluator_subject,i.revoked_at,
                  p.active,m.active,u.active,u.role,s.revoked_at
           FROM web_participant_sessions s JOIN web_invitations i USING(session_id)
           JOIN web_projects p USING(project_id)
           JOIN web_project_members m ON m.project_id=i.project_id
             AND m.issuer=i.evaluator_issuer AND m.subject=i.evaluator_subject
           JOIN app_users u ON (u.issuer,u.subject)=(i.evaluator_issuer,i.evaluator_subject)
           WHERE s.session_id=%s AND s.participant_token_sha256=%s""", (candidate[0], token_hash)
    ).fetchone()
    if row is None:
        raise UnknownCredentialError
    if row[14] is not None:
        raise MissingError
    return row


def get_participant_session(database_url: str, token_hash: str) -> SessionRecord:
    def operation():
        with psycopg.connect(database_url) as connection:
            row = _eligible_session(connection, token_hash)
            if row[3] <= connection.execute("SELECT clock_timestamp()").fetchone()[0]:
                if row[1] in {'preparing','running'}:
                    connection.execute("UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s",(row[0],))
                    connection.commit()
                raise ExpiredError
            if row[1] == 'expired':
                raise ExpiredError
            order = tuple(item[0] for item in connection.execute(
                "SELECT condition_id FROM web_session_main_order WHERE session_id=%s ORDER BY trial_number",(row[0],)
            ).fetchall())
            receipt = None
            if row[1] == 'completed':
                receipt = connection.execute(
                    "SELECT receipt FROM web_assessments WHERE session_id=%s", (row[0],)
                ).fetchone()[0]
            return SessionRecord(row[0],row[1],row[2],row[3],row[4],row[5],order,receipt)
    try:
        return operation()
    except (MissingError, ExpiredError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def start_participant_session(database_url: str, token_hash: str, app_version: str):
    def operation():
        with psycopg.connect(database_url) as connection:
            row = _eligible_session(connection, token_hash)
            now = connection.execute("SELECT clock_timestamp()").fetchone()[0]
            if row[3] <= now:
                if row[1] in {'preparing','running'}:
                    connection.execute("UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s",(row[0],))
                    connection.commit()
                raise ExpiredError
            if row[1] == 'preparing':
                started = connection.execute(
                    """UPDATE web_participant_sessions SET state='running',started_at=CURRENT_TIMESTAMP,app_version=%s
                       WHERE session_id=%s AND state='preparing' RETURNING started_at""",(app_version,row[0])
                ).fetchone()[0]
                return {"session_id":row[0],"state":"running","started_at":started,"expires_at":row[3]}
            if row[1] == 'running' and row[5] == app_version:
                return {"session_id":row[0],"state":"running","started_at":row[4],"expires_at":row[3]}
            if row[1] == 'expired':
                raise ExpiredError
            raise ConflictError
    try:
        return operation()
    except (MissingError, ExpiredError, ConflictError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def abort_participant_session(database_url: str, token_hash: str, reason: str):
    def operation():
        with psycopg.connect(database_url) as connection:
            row = _eligible_session(connection, token_hash)
            if row[1] == 'aborted':
                return {"session_id":row[0],"state":"aborted"}
            if row[1] == 'expired' or row[3] <= connection.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]:
                connection.execute("UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s AND state IN ('preparing','running')",(row[0],))
                connection.commit()
                raise ExpiredError
            if row[1] not in {'preparing','running'}:
                raise ConflictError
            connection.execute(
                "UPDATE web_participant_sessions SET state='aborted',abort_reason=%s WHERE session_id=%s",
                (reason,row[0]),
            )
            return {"session_id":row[0],"state":"aborted"}
    try:
        return operation()
    except (MissingError, ExpiredError, ConflictError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def complete_participant_session(database_url: str, token_hash: str, payload: dict,
                                 prepare_result):
    """Bloqueia acesso/sessao, normaliza e grava resultado e recibo atomicamente."""
    try:
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            row = _eligible_session(connection, token_hash)
            now = connection.execute("SELECT clock_timestamp()").fetchone()[0]
            if row[1] == 'expired' or row[3] <= now:
                if row[1] in {'preparing', 'running'}:
                    connection.execute(
                        "UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s",
                        (row[0],),
                    )
                    connection.commit()
                raise ExpiredError
            if row[1] not in {'running', 'completed'}:
                raise ConflictError
            order = tuple(item[0] for item in connection.execute(
                "SELECT condition_id FROM web_session_main_order WHERE session_id=%s ORDER BY trial_number",
                (row[0],),
            ).fetchall())
            result = prepare_result(order, row[5])
            if row[1] == 'completed':
                saved = connection.execute(
                    "SELECT payload_sha256,receipt FROM web_assessments WHERE session_id=%s",
                    (row[0],),
                ).fetchone()
                if saved[0] != result['payload_sha256']:
                    raise ResultConflictError
                return saved[1], False

            metadata = connection.execute(
                """SELECT p.code,i.participant_id,i.visit,i.protocol_id
                   FROM web_invitations i JOIN web_projects p USING(project_id)
                   WHERE i.session_id=%s""", (row[0],),
            ).fetchone()
            completed_at = connection.execute("SELECT clock_timestamp()").fetchone()[0]
            if completed_at >= row[3]:
                connection.execute(
                    "UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s", (row[0],)
                )
                connection.commit()
                raise ExpiredError
            assessment_id = str(uuid4())
            timestamp = completed_at.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
            started = row[4].astimezone(timezone.utc)
            receipt = {
                'session_id': str(row[0]), 'assessment_id': assessment_id,
                'state': 'completed', 'completed_at': timestamp,
                'platform': 'web', 'test_code': 'stroop_go_nogo_ptbr',
                'test_version': payload['test_version'], 'protocol_id': metadata[3],
                'app_version': row[5], 'summary': result['summary'],
            }
            connection.execute(
                """INSERT INTO assessments
                   (assessment_id,test_code,test_version,project,participant_id,participant_name,
                    initials,visit,evaluator,assessment_date,started_at,source_file,imported_at,import_status)
                   VALUES (%s,'stroop_go_nogo_ptbr',%s,%s,%s,'NAO_COLETADO',NULL,%s,%s,%s,%s,%s,%s,'valid')""",
                (assessment_id, payload['test_version'], metadata[0], metadata[1], metadata[2],
                 opaque_user_id(row[7],row[8]), started.date().isoformat(),
                 started.isoformat().replace('+00:00','Z'), f'web:{row[0]}', timestamp),
            )
            connection.cursor().executemany(
                """INSERT INTO trial_results
                   (assessment_id,block,trial_number,word,ink_color,condition,
                    correct_response,key_pressed,reaction_time,correct,error_type)
                   VALUES (%s,'main',%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                [(assessment_id, int(item['trial_number']), item['word'], item['ink_color'],
                  item['condition'], item['correct_response'] or None, item['key_pressed'] or None,
                  float(item['reaction_time']) if item['reaction_time'] else None,
                  int(item['correct']), item['error_type']) for item in result['rows']],
            )
            connection.cursor().executemany(
                """INSERT INTO assessment_metrics
                   (assessment_id,metric_code,metric_label,metric_value,unit,calculated_at)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                [(assessment_id, item['metric_code'], item['metric_label'], item['metric_value'],
                  item['unit'], timestamp) for item in result['metrics']],
            )
            connection.execute(
                """INSERT INTO web_assessments
                   (assessment_id,session_id,project_id,protocol_id,app_version,frame_period_ms,
                    payload_sha256,completed_at,receipt)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (assessment_id,row[0],row[6],metadata[3],row[5],payload['frame_period_ms'],
                 result['payload_sha256'],completed_at,Jsonb(receipt)),
            )
            connection.cursor().executemany(
                """INSERT INTO web_trial_observations
                   (assessment_id,trial_number,condition_id,trial_start_ms,stimulus_onset_ms,
                    stimulus_offset_ms,trial_end_ms,key_at_ms,reaction_time_ms)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                [(assessment_id,item['trial_number'],item['condition_id'],item['trial_start_ms'],
                  item['stimulus_onset_ms'],item['stimulus_offset_ms'],item['trial_end_ms'],
                  item['key_at_ms'],item['reaction_time_ms']) for item in payload['trials']],
            )
            connection.execute(
                "UPDATE web_participant_sessions SET state='completed' WHERE session_id=%s", (row[0],)
            )
            return receipt, True
    except psycopg.Error as exc:
        raise PersistenceError from exc


def logout_participant_session(database_url: str, token_hash: str, replacement_hash: str) -> None:
    """Invalida a credencial sem apagar estado completed ou resultados associados."""
    def operation():
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                "SELECT session_id FROM web_participant_sessions WHERE participant_token_sha256=%s",
                (token_hash,),
            ).fetchone()
            if row is None:
                return
            # Mesmo lock do ciclo de vida; revalidar hash depois de aguarda-lo.
            connection.execute("SELECT session_id FROM web_invitations WHERE session_id=%s FOR UPDATE", (row[0],))
            connection.execute(
                """UPDATE web_participant_sessions SET participant_token_sha256=%s,
                   abort_reason=CASE WHEN state IN ('preparing','running') THEN 'user_cancelled' ELSE abort_reason END,
                   state=CASE WHEN state IN ('preparing','running') THEN 'aborted' ELSE state END
                   WHERE session_id=%s AND participant_token_sha256=%s""",
                (replacement_hash, row[0], token_hash),
            )
    return _run(operation)
