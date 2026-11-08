"""Persistencia transacional dos cadastros centrais de pacientes e avaliadores."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row

from stroop.domain.registry import (
    DuplicateCandidateError,
    InvalidRegistryDataError,
    format_evaluator_code,
    format_patient_code,
)
from stroop.persistence.auth import PersistenceError


class MissingRegistryError(Exception):
    """Registro cadastral ou escopo de projeto nao encontrado."""


class ForbiddenRegistryError(Exception):
    """Conta profissional sem permissao ou sem vinculo ativo em projeto."""


PATIENT_SORTS = {
    "name_asc": "wp.normalized_name ASC, wp.participant_code ASC",
    "name_desc": "wp.normalized_name DESC, wp.participant_code ASC",
    "created_desc": "wp.created_at DESC, wp.participant_code ASC",
    "code_asc": "wp.participant_code ASC",
}

EVALUATOR_SORTS = {
    "name_asc": "we.normalized_name ASC, we.evaluator_code ASC",
    "name_desc": "we.normalized_name DESC, we.evaluator_code ASC",
    "created_desc": "we.created_at DESC, we.evaluator_code ASC",
    "code_asc": "we.evaluator_code ASC",
}


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _audit_auth(connection, issuer: str, subject: str, action: str) -> None:
    connection.execute(
        """INSERT INTO auth_audit_events(issuer, subject, action, outcome, request_id)
           VALUES (%s, %s, %s, 'success', %s)""",
        (issuer, subject, action, uuid4()),
    )


def _authorized_projects(
    connection,
    issuer: str,
    subject: str,
    *,
    require_write: bool,
) -> list[UUID]:
    if require_write:
        user = connection.execute(
            "SELECT active, role FROM public.web_lock_emitter(%s, %s)",
            (issuer, subject),
        ).fetchone()
    else:
        user = connection.execute(
            "SELECT active, role FROM app_users WHERE issuer = %s AND subject = %s",
            (issuer, subject),
        ).fetchone()
    allowed_roles = (
        {"importacao", "administracao"}
        if require_write
        else {"consulta", "importacao", "administracao"}
    )
    if user is None or not user["active"] or user["role"] not in allowed_roles:
        raise ForbiddenRegistryError
    rows = connection.execute(
        """SELECT p.project_id
           FROM web_projects p
           JOIN web_project_members m USING (project_id)
           WHERE p.active AND m.active AND m.issuer = %s AND m.subject = %s
           ORDER BY p.created_at, p.project_id""",
        (issuer, subject),
    ).fetchall()
    project_ids = [row["project_id"] for row in rows]
    if not project_ids:
        raise ForbiddenRegistryError
    return project_ids


def _hydrate_patients(
    connection,
    rows: list[dict],
    authorized_projects: list[UUID],
) -> list[dict]:
    if not rows:
        return []
    patient_ids = [row["id"] for row in rows]
    project_map: dict[UUID, list[str]] = {pid: [] for pid in patient_ids}
    visit_counts: dict[UUID, int] = {pid: 0 for pid in patient_ids}
    assessment_counts: dict[UUID, int] = {pid: 0 for pid in patient_ids}
    last_visits: dict[UUID, datetime | None] = {pid: None for pid in patient_ids}

    if authorized_projects:
        proj_rows = connection.execute(
            """SELECT DISTINCT pp.patient_id, p.code
               FROM web_project_participants pp
               JOIN web_projects p USING (project_id)
               WHERE pp.patient_id = ANY(%s)
                 AND pp.project_id = ANY(%s)
                 AND p.active
               ORDER BY p.code""",
            (patient_ids, authorized_projects),
        ).fetchall()
        for row in proj_rows:
            project_map[row["patient_id"]].append(row["code"])

        visit_rows = connection.execute(
            """SELECT pp.patient_id, COUNT(DISTINCT v.visit_uuid) AS cnt
               FROM web_project_participants pp
               JOIN web_participant_visits v
                 ON (v.project_id, v.participant_uuid) = (pp.project_id, pp.participant_uuid)
               WHERE pp.patient_id = ANY(%s)
                 AND pp.project_id = ANY(%s)
               GROUP BY pp.patient_id""",
            (patient_ids, authorized_projects),
        ).fetchall()
        for row in visit_rows:
            visit_counts[row["patient_id"]] = int(row["cnt"])

        assess_rows = connection.execute(
            """SELECT wa.patient_id,
                      COUNT(*) AS cnt,
                      MAX(wa.completed_at) AS last_completed_at
               FROM web_assessments wa
               WHERE wa.patient_id = ANY(%s)
                 AND wa.project_id = ANY(%s)
                 AND NOT EXISTS (
                     SELECT 1 FROM web_session_invalidations inv
                     WHERE inv.session_id = wa.session_id
                 )
               GROUP BY wa.patient_id""",
            (patient_ids, authorized_projects),
        ).fetchall()
        for row in assess_rows:
            assessment_counts[row["patient_id"]] = int(row["cnt"])
            last_visits[row["patient_id"]] = row["last_completed_at"]

        inv_rows = connection.execute(
            """SELECT i.patient_id, MAX(COALESCE(i.redeemed_at, i.created_at)) AS last_inv_at
               FROM web_invitations i
               WHERE i.patient_id = ANY(%s)
                 AND i.project_id = ANY(%s)
               GROUP BY i.patient_id""",
            (patient_ids, authorized_projects),
        ).fetchall()
        for row in inv_rows:
            pid = row["patient_id"]
            inv_at = row["last_inv_at"]
            if inv_at is not None and (last_visits[pid] is None or inv_at > last_visits[pid]):
                last_visits[pid] = inv_at

    items: list[dict] = []
    for row in rows:
        pid = row["id"]
        items.append(
            {
                "id": str(pid),
                "participant_code": row["participant_code"],
                "full_name": row["full_name"],
                "initials": row["initials"],
                "disambiguation_note": row["disambiguation_note"],
                "is_homonym_confirmed": bool(row["is_homonym_confirmed"]),
                "active": bool(row["active"]),
                "project_codes": project_map.get(pid, []),
                "visit_count": visit_counts.get(pid, 0),
                "assessment_count": assessment_counts.get(pid, 0),
                "last_visit_at": _iso(last_visits.get(pid)),
                "created_at": _iso(row["created_at"]),
                "updated_at": _iso(row["updated_at"]),
            }
        )
    return items


def _hydrate_evaluators(
    connection,
    rows: list[dict],
    authorized_projects: list[UUID],
) -> list[dict]:
    if not rows:
        return []
    evaluator_ids = [row["id"] for row in rows]
    project_map: dict[UUID, set[str]] = {eid: set() for eid in evaluator_ids}
    assessment_counts: dict[UUID, int] = {eid: 0 for eid in evaluator_ids}
    last_assessments: dict[UUID, datetime | None] = {eid: None for eid in evaluator_ids}

    if authorized_projects:
        inv_proj_rows = connection.execute(
            """SELECT DISTINCT i.evaluator_uuid, p.code
               FROM web_invitations i
               JOIN web_projects p USING (project_id)
               WHERE i.evaluator_uuid = ANY(%s)
                 AND i.project_id = ANY(%s)
                 AND p.active""",
            (evaluator_ids, authorized_projects),
        ).fetchall()
        for row in inv_proj_rows:
            project_map[row["evaluator_uuid"]].add(row["code"])

        assess_rows = connection.execute(
            """SELECT wa.evaluator_uuid,
                      COUNT(*) AS cnt,
                      MAX(wa.completed_at) AS last_completed_at
               FROM web_assessments wa
               WHERE wa.evaluator_uuid = ANY(%s)
                 AND wa.project_id = ANY(%s)
                 AND NOT EXISTS (
                     SELECT 1 FROM web_session_invalidations inv
                     WHERE inv.session_id = wa.session_id
                 )
               GROUP BY wa.evaluator_uuid""",
            (evaluator_ids, authorized_projects),
        ).fetchall()
        for row in assess_rows:
            eid = row["evaluator_uuid"]
            assessment_counts[eid] = int(row["cnt"])
            last_assessments[eid] = row["last_completed_at"]

    items: list[dict] = []
    for row in rows:
        eid = row["id"]
        items.append(
            {
                "id": str(eid),
                "evaluator_code": row["evaluator_code"],
                "full_name": row["full_name"],
                "initials": row["initials"],
                "active": bool(row["active"]),
                "project_codes": sorted(project_map.get(eid, set())),
                "assessment_count": assessment_counts.get(eid, 0),
                "last_assessment_at": _iso(last_assessments.get(eid)),
                "created_at": _iso(row["created_at"]),
                "updated_at": _iso(row["updated_at"]),
            }
        )
    return items


def find_duplicate_patients(
    database_url: str,
    *,
    normalized_name: str,
    initials: str | None,
    issuer: str,
    subject: str,
) -> list[dict]:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            like_prefix = f"{normalized_name}%"
            rows = connection.execute(
                """SELECT *
                   FROM web_patients wp
                   WHERE wp.normalized_name = %s
                      OR wp.normalized_name LIKE %s
                      OR %s LIKE (wp.normalized_name || '%%')
                   ORDER BY (wp.normalized_name = %s) DESC,
                            wp.active DESC,
                            wp.normalized_name ASC,
                            wp.created_at DESC
                   LIMIT 25""",
                (normalized_name, like_prefix, normalized_name, normalized_name),
            ).fetchall()
            hydrated = _hydrate_patients(connection, rows, authorized_projects)
            for item, raw in zip(hydrated, rows):
                item["exact_match"] = raw["normalized_name"] == normalized_name
                if initials:
                    item["initials_match"] = item["initials"].casefold() == initials.casefold()
            return hydrated
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def create_patient(
    database_url: str,
    *,
    full_name: str,
    normalized_name: str,
    initials: str,
    disambiguation_note: str,
    confirm_homonym: bool,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s))",
                (f"web_patients:{normalized_name}",),
            )
            existing_rows = connection.execute(
                """SELECT *
                   FROM web_patients wp
                   WHERE wp.normalized_name = %s
                   ORDER BY wp.active DESC, wp.created_at DESC""",
                (normalized_name,),
            ).fetchall()
            if existing_rows and not confirm_homonym:
                candidates = _hydrate_patients(connection, existing_rows, authorized_projects)
                for item in candidates:
                    item["exact_match"] = True
                raise DuplicateCandidateError(candidates)

            seq_row = connection.execute(
                """SELECT nextval('web_patient_code_seq') AS seq_val,
                          (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date AS today_utc"""
            ).fetchone()
            patient_id = uuid4()
            participant_code = format_patient_code(
                seq_row["today_utc"], int(seq_row["seq_val"])
            )
            is_homonym_confirmed = bool(confirm_homonym and existing_rows)
            inserted = connection.execute(
                """INSERT INTO web_patients (
                       id, participant_code, full_name, normalized_name,
                       initials, disambiguation_note, is_homonym_confirmed,
                       active, created_by_issuer, created_by_subject
                   )
                   VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
                   RETURNING *""",
                (
                    patient_id,
                    participant_code,
                    full_name,
                    normalized_name,
                    initials,
                    disambiguation_note,
                    is_homonym_confirmed,
                    issuer,
                    subject,
                ),
            ).fetchone()
            reason_code = (
                "homonym_confirmed" if is_homonym_confirmed else "initial_registration"
            )
            connection.execute(
                """INSERT INTO web_registry_audit_events (
                       entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                   )
                   VALUES ('patient', %s, 'create', %s, %s, %s)""",
                (patient_id, issuer, subject, reason_code),
            )
            _audit_auth(connection, issuer, subject, "manage_patients")
            return _hydrate_patients(connection, [inserted], authorized_projects)[0]
    except (DuplicateCandidateError, ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def list_patients(
    database_url: str,
    *,
    search_normalized: str,
    search_raw: str,
    project_id: UUID | None,
    active_filter: str,
    page: int,
    page_size: int,
    sort: str,
    issuer: str,
    subject: str,
) -> dict:
    order_clause = PATIENT_SORTS.get(sort, PATIENT_SORTS["name_asc"])
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=False
            )
            if project_id is not None and project_id not in authorized_projects:
                raise MissingRegistryError

            clauses: list[str] = ["TRUE"]
            params: list[object] = []
            if active_filter == "true":
                clauses.append("wp.active = TRUE")
            elif active_filter == "false":
                clauses.append("wp.active = FALSE")

            if project_id is not None:
                clauses.append(
                    """EXISTS (
                           SELECT 1 FROM web_project_participants pp
                           WHERE pp.patient_id = wp.id AND pp.project_id = %s
                       )"""
                )
                params.append(project_id)

            if search_normalized or search_raw:
                like_norm = f"%{search_normalized}%"
                like_raw = f"%{search_raw.lower()}%"
                clauses.append(
                    """(wp.normalized_name LIKE %s
                        OR lower(wp.participant_code) LIKE %s
                        OR lower(wp.initials) LIKE %s)"""
                )
                params.extend([like_norm, like_raw, like_raw])

            where_sql = " AND ".join(clauses)
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) AS cnt FROM web_patients wp WHERE {where_sql}",
                    params,
                ).fetchone()["cnt"]
            )
            offset = (page - 1) * page_size
            rows = connection.execute(
                f"""SELECT *
                    FROM web_patients wp
                    WHERE {where_sql}
                    ORDER BY {order_clause}
                    LIMIT %s OFFSET %s""",
                [*params, page_size, offset],
            ).fetchall()
            items = _hydrate_patients(connection, rows, authorized_projects)
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def get_patient(
    database_url: str,
    *,
    patient_id: UUID,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=False
            )
            row = connection.execute(
                "SELECT * FROM web_patients WHERE id = %s",
                (patient_id,),
            ).fetchone()
            if row is None:
                raise MissingRegistryError

            base = _hydrate_patients(connection, [row], authorized_projects)[0]

            projects = connection.execute(
                """SELECT pp.project_id, p.code AS project_code, p.name AS project_name,
                          pp.participant_uuid, pp.pseudonym AS participant_code, pp.created_at
                   FROM web_project_participants pp
                   JOIN web_projects p USING (project_id)
                   WHERE pp.patient_id = %s
                     AND pp.project_id = ANY(%s)
                     AND p.active
                   ORDER BY pp.created_at ASC, p.code ASC""",
                (patient_id, authorized_projects),
            ).fetchall()

            visits = connection.execute(
                """SELECT v.visit_uuid, v.project_id, p.code AS project_code,
                          v.label AS visit, v.created_at
                   FROM web_participant_visits v
                   JOIN web_project_participants pp
                     ON (pp.project_id, pp.participant_uuid) = (v.project_id, v.participant_uuid)
                   JOIN web_projects p ON p.project_id = v.project_id
                   WHERE pp.patient_id = %s
                     AND v.project_id = ANY(%s)
                     AND p.active
                   ORDER BY v.created_at DESC, v.label ASC""",
                (patient_id, authorized_projects),
            ).fetchall()

            assessments = connection.execute(
                """SELECT a.assessment_id, wa.project_id, p.code AS project_code,
                          a.participant_id, a.visit, a.evaluator AS evaluator_code,
                          wa.evaluator_uuid, we.full_name AS evaluator_name,
                          a.test_code, a.test_version, wa.protocol_id, wa.app_version,
                          a.assessment_date, a.started_at, wa.completed_at,
                          NOT EXISTS (
                              SELECT 1 FROM web_session_invalidations inv
                              WHERE inv.session_id = wa.session_id
                          ) AS valid_for_result
                   FROM web_assessments wa
                   JOIN assessments a USING (assessment_id)
                   JOIN web_projects p ON p.project_id = wa.project_id
                   LEFT JOIN web_evaluators we ON we.id = wa.evaluator_uuid
                   WHERE wa.patient_id = %s
                     AND wa.project_id = ANY(%s)
                     AND p.active
                   ORDER BY wa.completed_at DESC, a.assessment_id ASC""",
                (patient_id, authorized_projects),
            ).fetchall()

            sessions = connection.execute(
                """SELECT i.invitation_id, i.session_id, i.project_id, p.code AS project_code,
                          i.visit, i.evaluator_id AS evaluator_code, i.evaluator_uuid,
                          i.test_code, i.test_version, i.state AS invitation_state,
                          s.state AS session_state, i.created_at, i.expires_at,
                          i.redeemed_at, i.revoked_at
                   FROM web_invitations i
                   JOIN web_projects p USING (project_id)
                   LEFT JOIN web_participant_sessions s USING (session_id)
                   WHERE i.patient_id = %s
                     AND i.project_id = ANY(%s)
                     AND p.active
                   ORDER BY i.created_at DESC""",
                (patient_id, authorized_projects),
            ).fetchall()

            audit_rows = connection.execute(
                """SELECT event_id, entity_type, action, reason_code, occurred_at
                   FROM web_registry_audit_events
                   WHERE entity_type IN ('patient', 'participant_link')
                     AND entity_id = %s
                   ORDER BY occurred_at DESC, event_id DESC""",
                (patient_id,),
            ).fetchall()

            base["projects"] = [
                {
                    "project_id": str(item["project_id"]),
                    "project_code": item["project_code"],
                    "project_name": item["project_name"],
                    "participant_uuid": str(item["participant_uuid"]),
                    "participant_code": item["participant_code"],
                    "created_at": _iso(item["created_at"]),
                }
                for item in projects
            ]
            base["visits"] = [
                {
                    "visit_uuid": str(item["visit_uuid"]),
                    "project_id": str(item["project_id"]),
                    "project_code": item["project_code"],
                    "visit": item["visit"],
                    "created_at": _iso(item["created_at"]),
                }
                for item in visits
            ]
            base["assessments"] = [
                {
                    "assessment_id": item["assessment_id"],
                    "project_id": str(item["project_id"]),
                    "project_code": item["project_code"],
                    "participant_id": item["participant_id"],
                    "visit": item["visit"],
                    "evaluator_code": item["evaluator_code"],
                    "evaluator_id": str(item["evaluator_uuid"]) if item["evaluator_uuid"] else None,
                    "evaluator_name": item["evaluator_name"],
                    "test_code": item["test_code"],
                    "test_version": item["test_version"],
                    "protocol_id": item["protocol_id"],
                    "app_version": item["app_version"],
                    "assessment_date": item["assessment_date"],
                    "started_at": item["started_at"],
                    "completed_at": _iso(item["completed_at"]),
                    "valid_for_result": bool(item["valid_for_result"]),
                }
                for item in assessments
            ]
            base["sessions"] = [
                {
                    "invitation_id": str(item["invitation_id"]),
                    "session_id": str(item["session_id"]),
                    "project_id": str(item["project_id"]),
                    "project_code": item["project_code"],
                    "visit": item["visit"],
                    "evaluator_code": item["evaluator_code"],
                    "evaluator_id": str(item["evaluator_uuid"]) if item["evaluator_uuid"] else None,
                    "test_code": item["test_code"],
                    "test_version": item["test_version"],
                    "invitation_state": item["invitation_state"],
                    "session_state": item["session_state"],
                    "created_at": _iso(item["created_at"]),
                    "expires_at": _iso(item["expires_at"]),
                    "redeemed_at": _iso(item["redeemed_at"]),
                    "revoked_at": _iso(item["revoked_at"]),
                }
                for item in sessions
            ]
            base["audit_history"] = [
                {
                    "event_id": str(item["event_id"]),
                    "entity_type": item["entity_type"],
                    "action": item["action"],
                    "reason_code": item["reason_code"],
                    "occurred_at": _iso(item["occurred_at"]),
                }
                for item in audit_rows
            ]
            return base
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def update_patient(
    database_url: str,
    *,
    patient_id: UUID,
    full_name: str | None,
    normalized_name: str | None,
    initials: str | None,
    disambiguation_note: str | None,
    active: bool | None,
    reason_code: str,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            current = connection.execute(
                "SELECT * FROM web_patients WHERE id = %s FOR UPDATE",
                (patient_id,),
            ).fetchone()
            if current is None:
                raise MissingRegistryError

            next_full_name = full_name if full_name is not None else current["full_name"]
            next_norm_name = (
                normalized_name if normalized_name is not None else current["normalized_name"]
            )
            next_initials = initials if initials is not None else current["initials"]
            next_note = (
                disambiguation_note
                if disambiguation_note is not None
                else current["disambiguation_note"]
            )
            next_active = active if active is not None else bool(current["active"])

            if active is not None and active != bool(current["active"]):
                audit_action = "deactivate" if not active else "reactivate"
            else:
                audit_action = "update"

            updated = connection.execute(
                """UPDATE web_patients
                   SET full_name = %s,
                       normalized_name = %s,
                       initials = %s,
                       disambiguation_note = %s,
                       active = %s,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = %s
                   RETURNING *""",
                (
                    next_full_name,
                    next_norm_name,
                    next_initials,
                    next_note,
                    next_active,
                    patient_id,
                ),
            ).fetchone()
            connection.execute(
                """INSERT INTO web_registry_audit_events (
                       entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                   )
                   VALUES ('patient', %s, %s, %s, %s, %s)""",
                (patient_id, audit_action, issuer, subject, reason_code),
            )
            _audit_auth(connection, issuer, subject, "manage_patients")
            return _hydrate_patients(connection, [updated], authorized_projects)[0]
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def create_evaluator(
    database_url: str,
    *,
    full_name: str,
    normalized_name: str,
    initials: str,
    confirm_homonym: bool,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s))",
                (f"web_evaluators:{normalized_name}",),
            )
            existing_rows = connection.execute(
                """SELECT *
                   FROM web_evaluators we
                   WHERE we.normalized_name = %s
                   ORDER BY we.active DESC, we.created_at DESC""",
                (normalized_name,),
            ).fetchall()
            if existing_rows and not confirm_homonym:
                candidates = _hydrate_evaluators(
                    connection, existing_rows, authorized_projects
                )
                for item in candidates:
                    item["exact_match"] = True
                raise DuplicateCandidateError(candidates)

            seq_val = int(
                connection.execute(
                    "SELECT nextval('web_evaluator_code_seq') AS seq_val"
                ).fetchone()["seq_val"]
            )
            evaluator_id = uuid4()
            evaluator_code = format_evaluator_code(seq_val)
            inserted = connection.execute(
                """INSERT INTO web_evaluators (
                       id, evaluator_code, full_name, normalized_name,
                       initials, active, created_by_issuer, created_by_subject
                   )
                   VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s)
                   RETURNING *""",
                (
                    evaluator_id,
                    evaluator_code,
                    full_name,
                    normalized_name,
                    initials,
                    issuer,
                    subject,
                ),
            ).fetchone()
            reason_code = (
                "homonym_confirmed"
                if (confirm_homonym and existing_rows)
                else "initial_registration"
            )
            connection.execute(
                """INSERT INTO web_registry_audit_events (
                       entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                   )
                   VALUES ('evaluator', %s, 'create', %s, %s, %s)""",
                (evaluator_id, issuer, subject, reason_code),
            )
            _audit_auth(connection, issuer, subject, "manage_evaluators")
            return _hydrate_evaluators(connection, [inserted], authorized_projects)[0]
    except (DuplicateCandidateError, ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def list_evaluators(
    database_url: str,
    *,
    search_normalized: str,
    search_raw: str,
    active_filter: str,
    page: int,
    page_size: int,
    sort: str,
    issuer: str,
    subject: str,
) -> dict:
    order_clause = EVALUATOR_SORTS.get(sort, EVALUATOR_SORTS["name_asc"])
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=False
            )
            clauses: list[str] = ["TRUE"]
            params: list[object] = []
            if active_filter == "true":
                clauses.append("we.active = TRUE")
            elif active_filter == "false":
                clauses.append("we.active = FALSE")

            if search_normalized or search_raw:
                like_norm = f"%{search_normalized}%"
                like_raw = f"%{search_raw.lower()}%"
                clauses.append(
                    """(we.normalized_name LIKE %s
                        OR lower(we.evaluator_code) LIKE %s
                        OR lower(we.initials) LIKE %s)"""
                )
                params.extend([like_norm, like_raw, like_raw])

            where_sql = " AND ".join(clauses)
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) AS cnt FROM web_evaluators we WHERE {where_sql}",
                    params,
                ).fetchone()["cnt"]
            )
            offset = (page - 1) * page_size
            rows = connection.execute(
                f"""SELECT *
                    FROM web_evaluators we
                    WHERE {where_sql}
                    ORDER BY {order_clause}
                    LIMIT %s OFFSET %s""",
                [*params, page_size, offset],
            ).fetchall()
            items = _hydrate_evaluators(connection, rows, authorized_projects)
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def get_evaluator(
    database_url: str,
    *,
    evaluator_id: UUID,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=False
            )
            row = connection.execute(
                "SELECT * FROM web_evaluators WHERE id = %s",
                (evaluator_id,),
            ).fetchone()
            if row is None:
                raise MissingRegistryError

            base = _hydrate_evaluators(connection, [row], authorized_projects)[0]

            assessments = connection.execute(
                """SELECT a.assessment_id, wa.project_id, p.code AS project_code,
                          a.participant_id, wa.patient_id, wp.full_name AS patient_name,
                          a.visit, a.test_code, a.test_version, wa.protocol_id,
                          wa.app_version, a.assessment_date, a.started_at, wa.completed_at,
                          NOT EXISTS (
                              SELECT 1 FROM web_session_invalidations inv
                              WHERE inv.session_id = wa.session_id
                          ) AS valid_for_result
                   FROM web_assessments wa
                   JOIN assessments a USING (assessment_id)
                   JOIN web_projects p ON p.project_id = wa.project_id
                   LEFT JOIN web_patients wp ON wp.id = wa.patient_id
                   WHERE wa.evaluator_uuid = %s
                     AND wa.project_id = ANY(%s)
                     AND p.active
                   ORDER BY wa.completed_at DESC, a.assessment_id ASC""",
                (evaluator_id, authorized_projects),
            ).fetchall()

            instruments = sorted({item["test_code"] for item in assessments})
            audit_rows = connection.execute(
                """SELECT event_id, entity_type, action, reason_code, occurred_at
                   FROM web_registry_audit_events
                   WHERE entity_type IN ('evaluator', 'invitation_link')
                     AND entity_id = %s
                   ORDER BY occurred_at DESC, event_id DESC""",
                (evaluator_id,),
            ).fetchall()

            base["instruments"] = instruments
            base["assessments"] = [
                {
                    "assessment_id": item["assessment_id"],
                    "project_id": str(item["project_id"]),
                    "project_code": item["project_code"],
                    "participant_id": item["participant_id"],
                    "patient_id": str(item["patient_id"]) if item["patient_id"] else None,
                    "patient_name": item["patient_name"],
                    "visit": item["visit"],
                    "test_code": item["test_code"],
                    "test_version": item["test_version"],
                    "protocol_id": item["protocol_id"],
                    "app_version": item["app_version"],
                    "assessment_date": item["assessment_date"],
                    "started_at": item["started_at"],
                    "completed_at": _iso(item["completed_at"]),
                    "valid_for_result": bool(item["valid_for_result"]),
                }
                for item in assessments
            ]
            base["audit_history"] = [
                {
                    "event_id": str(item["event_id"]),
                    "entity_type": item["entity_type"],
                    "action": item["action"],
                    "reason_code": item["reason_code"],
                    "occurred_at": _iso(item["occurred_at"]),
                }
                for item in audit_rows
            ]
            return base
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def update_evaluator(
    database_url: str,
    *,
    evaluator_id: UUID,
    full_name: str | None,
    normalized_name: str | None,
    initials: str | None,
    active: bool | None,
    reason_code: str,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            current = connection.execute(
                "SELECT * FROM web_evaluators WHERE id = %s FOR UPDATE",
                (evaluator_id,),
            ).fetchone()
            if current is None:
                raise MissingRegistryError

            next_full_name = full_name if full_name is not None else current["full_name"]
            next_norm_name = (
                normalized_name if normalized_name is not None else current["normalized_name"]
            )
            next_initials = initials if initials is not None else current["initials"]
            next_active = active if active is not None else bool(current["active"])

            if active is not None and active != bool(current["active"]):
                audit_action = "deactivate" if not active else "reactivate"
            else:
                audit_action = "update"

            updated = connection.execute(
                """UPDATE web_evaluators
                   SET full_name = %s,
                       normalized_name = %s,
                       initials = %s,
                       active = %s,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = %s
                   RETURNING *""",
                (
                    next_full_name,
                    next_norm_name,
                    next_initials,
                    next_active,
                    evaluator_id,
                ),
            ).fetchone()
            connection.execute(
                """INSERT INTO web_registry_audit_events (
                       entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                   )
                   VALUES ('evaluator', %s, %s, %s, %s, %s)""",
                (evaluator_id, audit_action, issuer, subject, reason_code),
            )
            _audit_auth(connection, issuer, subject, "manage_evaluators")
            return _hydrate_evaluators(connection, [updated], authorized_projects)[0]
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def relink_assessment(
    database_url: str,
    *,
    project_id: UUID,
    assessment_id: str,
    patient_id: UUID | None = None,
    evaluator_id: UUID | None = None,
    reason_code: str,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            if project_id not in authorized_projects:
                raise ForbiddenRegistryError

            current = connection.execute(
                """SELECT wa.assessment_id, wa.project_id, wa.patient_id,
                          wa.evaluator_uuid, wa.session_id, a.participant_id, a.evaluator
                   FROM web_assessments wa
                   JOIN assessments a USING (assessment_id)
                   WHERE wa.assessment_id = %s AND wa.project_id = %s
                   FOR UPDATE""",
                (assessment_id, project_id),
            ).fetchone()
            if current is None:
                raise MissingRegistryError

            new_patient_id = current["patient_id"]
            if patient_id is not None:
                pat = connection.execute(
                    "SELECT id, participant_code, active FROM web_patients WHERE id = %s",
                    (patient_id,),
                ).fetchone()
                if pat is None:
                    raise MissingRegistryError
                if not pat["active"]:
                    raise InvalidRegistryDataError("Paciente inativo nao pode receber vinculo.")
                part_code = pat["participant_code"]
                connection.execute(
                    """INSERT INTO web_project_participants(participant_uuid, project_id, pseudonym, patient_id)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (project_id, pseudonym) DO UPDATE
                       SET patient_id = COALESCE(web_project_participants.patient_id, EXCLUDED.patient_id)""",
                    (uuid4(), project_id, part_code, patient_id),
                )
                new_part_uuid = connection.execute(
                    "SELECT participant_uuid FROM web_project_participants WHERE project_id = %s AND pseudonym = %s",
                    (project_id, part_code),
                ).fetchone()["participant_uuid"]
                connection.execute(
                    "UPDATE web_assessments SET patient_id = %s WHERE assessment_id = %s",
                    (patient_id, assessment_id),
                )
                connection.execute(
                    "UPDATE assessments SET participant_id = %s WHERE assessment_id = %s",
                    (part_code, assessment_id),
                )
                inv_row = connection.execute(
                    "SELECT visit FROM web_invitations WHERE session_id = %s",
                    (current["session_id"],),
                ).fetchone()
                if inv_row is not None:
                    visit_label = inv_row["visit"]
                    connection.execute(
                        """INSERT INTO web_participant_visits(visit_uuid, project_id, participant_uuid, label)
                           VALUES (%s, %s, %s, %s)
                           ON CONFLICT (project_id, participant_uuid, label) DO NOTHING""",
                        (uuid4(), project_id, new_part_uuid, visit_label),
                    )
                    new_visit_uuid = connection.execute(
                        """SELECT visit_uuid FROM web_participant_visits
                           WHERE project_id = %s AND participant_uuid = %s AND label = %s""",
                        (project_id, new_part_uuid, visit_label),
                    ).fetchone()["visit_uuid"]
                    connection.execute(
                        """UPDATE web_invitations
                           SET patient_id = %s, participant_id = %s, participant_uuid = %s, visit_uuid = %s
                           WHERE session_id = %s""",
                        (patient_id, part_code, new_part_uuid, new_visit_uuid, current["session_id"]),
                    )
                connection.execute(
                    """INSERT INTO web_registry_audit_events (
                           entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                       )
                       VALUES ('participant_link', %s, 'relink', %s, %s, %s)""",
                    (patient_id, issuer, subject, reason_code),
                )
                if current["patient_id"] is not None and current["patient_id"] != patient_id:
                    connection.execute(
                        """INSERT INTO web_registry_audit_events (
                               entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                           )
                           VALUES ('participant_link', %s, 'relink', %s, %s, %s)""",
                        (current["patient_id"], issuer, subject, reason_code),
                    )
                new_patient_id = patient_id

            new_evaluator_uuid = current["evaluator_uuid"]
            if evaluator_id is not None:
                ev = connection.execute(
                    "SELECT id, evaluator_code, active FROM web_evaluators WHERE id = %s",
                    (evaluator_id,),
                ).fetchone()
                if ev is None:
                    raise MissingRegistryError
                if not ev["active"]:
                    raise InvalidRegistryDataError("Avaliador inativo nao pode receber vinculo.")
                ev_code = ev["evaluator_code"]
                connection.execute(
                    "UPDATE web_assessments SET evaluator_uuid = %s WHERE assessment_id = %s",
                    (evaluator_id, assessment_id),
                )
                connection.execute(
                    "UPDATE assessments SET evaluator = %s WHERE assessment_id = %s",
                    (ev_code, assessment_id),
                )
                connection.execute(
                    "UPDATE web_invitations SET evaluator_uuid = %s, evaluator_id = %s WHERE session_id = %s",
                    (evaluator_id, ev_code, current["session_id"]),
                )
                connection.execute(
                    """INSERT INTO web_registry_audit_events (
                           entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                       )
                       VALUES ('invitation_link', %s, 'relink', %s, %s, %s)""",
                    (evaluator_id, issuer, subject, reason_code),
                )
                if current["evaluator_uuid"] is not None and current["evaluator_uuid"] != evaluator_id:
                    connection.execute(
                        """INSERT INTO web_registry_audit_events (
                               entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                           )
                           VALUES ('invitation_link', %s, 'relink', %s, %s, %s)""",
                        (current["evaluator_uuid"], issuer, subject, reason_code),
                    )
                new_evaluator_uuid = evaluator_id

            _audit_auth(connection, issuer, subject, "manage_patients")
            return {
                "assessment_id": assessment_id,
                "project_id": str(project_id),
                "patient_id": str(new_patient_id) if new_patient_id is not None else None,
                "evaluator_id": str(new_evaluator_uuid) if new_evaluator_uuid is not None else None,
                "relinked": True,
            }
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


def relink_invitation(
    database_url: str,
    *,
    project_id: UUID,
    invitation_id: UUID,
    patient_id: UUID | None = None,
    evaluator_id: UUID | None = None,
    reason_code: str,
    issuer: str,
    subject: str,
) -> dict:
    try:
        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            authorized_projects = _authorized_projects(
                connection, issuer, subject, require_write=True
            )
            if project_id not in authorized_projects:
                raise ForbiddenRegistryError

            current = connection.execute(
                """SELECT invitation_id, session_id, project_id, patient_id, evaluator_uuid
                   FROM web_invitations
                   WHERE invitation_id = %s AND project_id = %s
                   FOR UPDATE""",
                (invitation_id, project_id),
            ).fetchone()
            if current is None:
                raise MissingRegistryError

            new_patient_id = current["patient_id"]
            if patient_id is not None:
                pat = connection.execute(
                    "SELECT id, participant_code, active FROM web_patients WHERE id = %s",
                    (patient_id,),
                ).fetchone()
                if pat is None:
                    raise MissingRegistryError
                if not pat["active"]:
                    raise InvalidRegistryDataError("Paciente inativo nao pode receber vinculo.")
                part_code = pat["participant_code"]
                connection.execute(
                    """INSERT INTO web_project_participants(participant_uuid, project_id, pseudonym, patient_id)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (project_id, pseudonym) DO UPDATE
                       SET patient_id = COALESCE(web_project_participants.patient_id, EXCLUDED.patient_id)""",
                    (uuid4(), project_id, part_code, patient_id),
                )
                new_part_uuid = connection.execute(
                    "SELECT participant_uuid FROM web_project_participants WHERE project_id = %s AND pseudonym = %s",
                    (project_id, part_code),
                ).fetchone()["participant_uuid"]
                inv_row = connection.execute(
                    "SELECT visit FROM web_invitations WHERE invitation_id = %s",
                    (invitation_id,),
                ).fetchone()
                if inv_row is not None:
                    visit_label = inv_row["visit"]
                    connection.execute(
                        """INSERT INTO web_participant_visits(visit_uuid, project_id, participant_uuid, label)
                           VALUES (%s, %s, %s, %s)
                           ON CONFLICT (project_id, participant_uuid, label) DO NOTHING""",
                        (uuid4(), project_id, new_part_uuid, visit_label),
                    )
                    new_visit_uuid = connection.execute(
                        """SELECT visit_uuid FROM web_participant_visits
                           WHERE project_id = %s AND participant_uuid = %s AND label = %s""",
                        (project_id, new_part_uuid, visit_label),
                    ).fetchone()["visit_uuid"]
                    connection.execute(
                        """UPDATE web_invitations
                           SET patient_id = %s, participant_id = %s, participant_uuid = %s, visit_uuid = %s
                           WHERE invitation_id = %s""",
                        (patient_id, part_code, new_part_uuid, new_visit_uuid, invitation_id),
                    )
                connection.execute(
                    """INSERT INTO web_registry_audit_events (
                           entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                       )
                       VALUES ('participant_link', %s, 'relink', %s, %s, %s)""",
                    (patient_id, issuer, subject, reason_code),
                )
                if current["patient_id"] is not None and current["patient_id"] != patient_id:
                    connection.execute(
                        """INSERT INTO web_registry_audit_events (
                               entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                           )
                           VALUES ('participant_link', %s, 'relink', %s, %s, %s)""",
                        (current["patient_id"], issuer, subject, reason_code),
                    )
                new_patient_id = patient_id

            new_evaluator_uuid = current["evaluator_uuid"]
            if evaluator_id is not None:
                ev = connection.execute(
                    "SELECT id, evaluator_code, active FROM web_evaluators WHERE id = %s",
                    (evaluator_id,),
                ).fetchone()
                if ev is None:
                    raise MissingRegistryError
                if not ev["active"]:
                    raise InvalidRegistryDataError("Avaliador inativo nao pode receber vinculo.")
                ev_code = ev["evaluator_code"]
                connection.execute(
                    "UPDATE web_invitations SET evaluator_uuid = %s, evaluator_id = %s WHERE invitation_id = %s",
                    (evaluator_id, ev_code, invitation_id),
                )
                connection.execute(
                    """INSERT INTO web_registry_audit_events (
                           entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                       )
                       VALUES ('invitation_link', %s, 'relink', %s, %s, %s)""",
                    (evaluator_id, issuer, subject, reason_code),
                )
                if current["evaluator_uuid"] is not None and current["evaluator_uuid"] != evaluator_id:
                    connection.execute(
                        """INSERT INTO web_registry_audit_events (
                               entity_type, entity_id, action, actor_issuer, actor_subject, reason_code
                           )
                           VALUES ('invitation_link', %s, 'relink', %s, %s, %s)""",
                        (current["evaluator_uuid"], issuer, subject, reason_code),
                    )
                new_evaluator_uuid = evaluator_id

            _audit_auth(connection, issuer, subject, "manage_patients")
            return {
                "invitation_id": str(invitation_id),
                "session_id": str(current["session_id"]),
                "project_id": str(project_id),
                "patient_id": str(new_patient_id) if new_patient_id is not None else None,
                "evaluator_id": str(new_evaluator_uuid) if new_evaluator_uuid is not None else None,
                "relinked": True,
            }
    except (ForbiddenRegistryError, MissingRegistryError):
        raise
    except psycopg.Error as exc:
        raise PersistenceError from exc


__all__ = [
    "DuplicateCandidateError",
    "ForbiddenRegistryError",
    "MissingRegistryError",
    "PersistenceError",
    "create_evaluator",
    "create_patient",
    "find_duplicate_patients",
    "get_evaluator",
    "get_patient",
    "list_evaluators",
    "list_patients",
    "relink_assessment",
    "relink_invitation",
    "update_evaluator",
    "update_patient",
]
