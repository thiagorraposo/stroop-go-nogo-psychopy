"""Persistencia transacional de importacoes CSV WEB e seu escopo explicito."""
from __future__ import annotations

from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from stroop.persistence.auth import PersistenceError
from stroop.persistence.postgres import insert_normalized_assessment


class ImportNotFound(Exception):
    """Projeto ou operacao nao esta no escopo autorizado."""


class ImportConflict(Exception):
    """Operacao reapresentada com dados ou estado divergentes."""


def _connect(database_url: str):
    try:
        return psycopg.connect(database_url, connect_timeout=5, row_factory=dict_row)
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _authorize(connection, project_id: UUID, issuer: str, subject: str) -> None:
    user = connection.execute(
        "SELECT active,role FROM public.web_lock_emitter(%s,%s)", (issuer, subject),
    ).fetchone()
    if user is None or not user['active'] or user['role'] not in {'importacao', 'administracao'}:
        raise ImportNotFound
    row = connection.execute(
        """SELECT 1 FROM web_projects p
           JOIN web_project_members m ON m.project_id=p.project_id
           WHERE p.project_id=%s AND p.active AND m.active
             AND m.issuer=%s AND m.subject=%s
           FOR SHARE OF p,m""",
        (project_id, issuer, subject),
    ).fetchone()
    if row is None:
        raise ImportNotFound


def _operation(connection, operation_id: UUID):
    return connection.execute(
        """SELECT operation_id, project_id, issuer, subject, content_sha256,
                  status, error_code, assessment_id, created_at, updated_at
           FROM web_csv_imports WHERE operation_id=%s FOR UPDATE""",
        (operation_id,),
    ).fetchone()


def begin(database_url: str, operation_id: UUID, project_id: UUID,
          issuer: str, subject: str, content_sha256: str) -> dict:
    try:
        with _connect(database_url) as connection:
            _authorize(connection, project_id, issuer, subject)
            connection.execute(
                """INSERT INTO web_csv_imports
                   (operation_id,project_id,issuer,subject,content_sha256,status)
                   VALUES (%s,%s,%s,%s,%s,'recebido') ON CONFLICT DO NOTHING""",
                (operation_id, project_id, issuer, subject, content_sha256),
            )
            row = _operation(connection, operation_id)
            if (row is None or row['project_id'] != project_id or row['issuer'] != issuer
                    or row['subject'] != subject or row['content_sha256'].strip() != content_sha256):
                raise ImportConflict
            return dict(row)
    except (ImportNotFound, ImportConflict):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def mark_validated(database_url: str, operation_id: UUID, project_id: UUID,
                   issuer: str, subject: str) -> dict:
    try:
        with _connect(database_url) as connection:
            _authorize(connection, project_id, issuer, subject)
            row = _operation(connection, operation_id)
            if row is None or row['project_id'] != project_id or row['issuer'] != issuer or row['subject'] != subject:
                raise ImportNotFound
            if row['status'] == 'recebido':
                row = connection.execute(
                    """UPDATE web_csv_imports SET status='validado',updated_at=CURRENT_TIMESTAMP
                       WHERE operation_id=%s RETURNING *""", (operation_id,),
                ).fetchone()
            return dict(row)
    except ImportNotFound:
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def reject(database_url: str, operation_id: UUID, project_id: UUID,
           issuer: str, subject: str, error_code: str) -> dict:
    try:
        with _connect(database_url) as connection:
            _authorize(connection, project_id, issuer, subject)
            row = _operation(connection, operation_id)
            if row is None or row['project_id'] != project_id or row['issuer'] != issuer or row['subject'] != subject:
                raise ImportNotFound
            if row['status'] in {'importado', 'rejeitado'}:
                return dict(row)
            row = connection.execute(
                """UPDATE web_csv_imports SET status='rejeitado',error_code=%s,
                   updated_at=CURRENT_TIMESTAMP WHERE operation_id=%s RETURNING *""",
                (error_code, operation_id),
            ).fetchone()
            return dict(row)
    except ImportNotFound:
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def import_normalized(database_url: str, operation_id: UUID, project_id: UUID,
                      issuer: str, subject: str, content_sha256: str,
                      normalized, timestamp: str) -> dict:
    try:
        with _connect(database_url) as connection:
            _authorize(connection, project_id, issuer, subject)
            row = _operation(connection, operation_id)
            if (row is None or row['project_id'] != project_id or row['issuer'] != issuer
                    or row['subject'] != subject or row['content_sha256'].strip() != content_sha256):
                raise ImportConflict
            if row['status'] in {'importado', 'rejeitado'}:
                return dict(row)
            if row['status'] != 'validado':
                raise ImportConflict
            assessment_id = normalized.metadata['assessment_id']
            # Serialize WEB attempts for the same global ID without requiring
            # table-wide UPDATE/LOCK privileges from the runtime writer.
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (str(assessment_id),),
            )
            if connection.execute(
                "SELECT 1 FROM assessments WHERE assessment_id=%s", (assessment_id,),
            ).fetchone() is not None:
                updated = connection.execute(
                    """UPDATE web_csv_imports SET status='rejeitado',
                       error_code='duplicate_assessment',updated_at=CURRENT_TIMESTAMP
                       WHERE operation_id=%s RETURNING *""", (operation_id,),
                ).fetchone()
                return dict(updated)
            insert_normalized_assessment(
                connection, normalized, f'web-import:{operation_id}', timestamp,
            )
            updated = connection.execute(
                """UPDATE web_csv_imports SET status='importado',assessment_id=%s,
                   updated_at=CURRENT_TIMESTAMP WHERE operation_id=%s RETURNING *""",
                (assessment_id, operation_id),
            ).fetchone()
            return dict(updated)
    except (ImportNotFound, ImportConflict):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def status(database_url: str, operation_id: UUID, project_id: UUID,
           issuer: str, subject: str) -> dict | None:
    try:
        with _connect(database_url) as connection:
            _authorize(connection, project_id, issuer, subject)
            row = connection.execute(
                """SELECT operation_id,project_id,issuer,subject,status,error_code,
                          assessment_id,created_at,updated_at
                   FROM web_csv_imports WHERE operation_id=%s""", (operation_id,),
            ).fetchone()
            if row is None or row['project_id'] != project_id or row['issuer'] != issuer or row['subject'] != subject:
                return None
            return dict(row)
    except ImportNotFound:
        return None
    except psycopg.Error as exc:
        raise PersistenceError from exc
