"""Persistencia transacional dos projetos, convites e sessoes WEB."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from uuid import uuid4

from stroop.persistence.auth import PersistenceError


@dataclass(frozen=True, slots=True)
class SessionRecord:
    session_id: UUID
    state: str
    activated_at: datetime
    expires_at: datetime
    started_at: datetime | None
    app_version: str | None
    order: tuple[int, ...]


class ConflictError(Exception):
    """Transicao concorrente ou recurso em estado incompatível."""


class ExpiredError(Exception):
    """Convite ou sessao ja expirados."""


class MissingError(Exception):
    """Recurso inexistente ou fora do escopo atual."""


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
    def operation():
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                """INSERT INTO web_professional_request_limits
                     (credential_sha256,operation,window_started_at,request_count)
                   VALUES (%s,%s,clock_timestamp(),1)
                   ON CONFLICT (credential_sha256,operation) DO UPDATE SET
                     window_started_at=CASE WHEN web_professional_request_limits.window_started_at <= clock_timestamp()-make_interval(secs => %s)
                       THEN clock_timestamp() ELSE web_professional_request_limits.window_started_at END,
                     request_count=CASE WHEN web_professional_request_limits.window_started_at <= clock_timestamp()-make_interval(secs => %s)
                       THEN 1 ELSE LEAST(web_professional_request_limits.request_count+1,%s+1) END
                   RETURNING request_count,GREATEST(1,ceil(extract(epoch FROM
                     (window_started_at+make_interval(secs => %s)-clock_timestamp())))::integer)""",
                (credential_hash, operation_name, window_seconds, window_seconds, limit, window_seconds),
            ).fetchone()
            connection.execute(
                "DELETE FROM web_professional_request_limits WHERE window_started_at <= clock_timestamp() - make_interval(secs => %s * 2)",
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
        raise MissingError
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
           WHERE s.session_id=%s""", (candidate[0],)
    ).fetchone()
    if row is None or row[14] is not None:
        raise MissingError
    return row


def get_participant_session(database_url: str, token_hash: str) -> SessionRecord:
    def operation():
        with psycopg.connect(database_url) as connection:
            row = _eligible_session(connection, token_hash)
            if row[3] <= connection.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0] and row[1] in {'preparing','running'}:
                connection.execute("UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s",(row[0],))
                connection.commit()
                row = (*row[:1], 'expired', *row[2:])
            if row[1] == 'expired':
                raise ExpiredError
            order = tuple(item[0] for item in connection.execute(
                "SELECT condition_id FROM web_session_main_order WHERE session_id=%s ORDER BY trial_number",(row[0],)
            ).fetchall())
            return SessionRecord(row[0],row[1],row[2],row[3],row[4],row[5],order)
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
            now = connection.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]
            if row[3] <= now:
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
