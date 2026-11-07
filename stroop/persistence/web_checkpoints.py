"""Recepcao incremental serializada pelo mesmo lock do ciclo de vida WEB."""
from __future__ import annotations

from datetime import timezone
import hashlib

import psycopg
from psycopg.types.json import Jsonb

from stroop.domain.auth import opaque_user_id
from stroop.domain.web_results import canonical_payload
from stroop.persistence.auth import PersistenceError
from stroop.persistence.web_sessions import (
    _eligible_session, ConflictError, ResultConflictError, ExpiredError, MissingError,
)


def _hash(value):
    return hashlib.sha256(canonical_payload(value)).hexdigest()


def _time(value):
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def checkpoint_receipt(connection, session_id):
    row = connection.execute(
        'SELECT confirmed_through,prefix_hash,received_at FROM web_session_checkpoints WHERE session_id=%s',
        (session_id,),
    ).fetchone()
    return {'confirmed_through': row[0] if row else 0,
            'prefix_hash': row[1] if row else None,
            'received_at': _time(row[2]) if row else None}


def invalidated(connection, session_id):
    return connection.execute(
        'SELECT 1 FROM web_session_invalidations WHERE session_id=%s', (session_id,),
    ).fetchone() is not None


def mark_invalid(connection, session_id, reason, source, event_at_ms=None, actor_id=None):
    connection.execute(
        """INSERT INTO web_session_invalidations(session_id,reason,source,event_at_ms,actor_id)
           VALUES (%s,%s,%s,%s,%s) ON CONFLICT (session_id) DO NOTHING""",
        (session_id,reason,source,event_at_ms,actor_id),
    )


def _unexpired(connection, row, *, rollback=False):
    if row[1] == 'expired' or row[3] <= connection.execute('SELECT clock_timestamp()').fetchone()[0]:
        if rollback:
            connection.rollback()
            raise ExpiredError
        if row[1] in {'preparing', 'running'}:
            connection.execute("UPDATE web_participant_sessions SET state='expired' WHERE session_id=%s", (row[0],))
            connection.commit()
        raise ExpiredError


def _observations(connection, session_id):
    return [item[0] for item in connection.execute(
        'SELECT payload FROM web_session_observations WHERE session_id=%s ORDER BY trial_number',
        (session_id,),
    ).fetchall()]


def _conflict(connection, session_id):
    # Conservar evidencia de divergencia mesmo quando a requisicao termina em 409.
    mark_invalid(connection, session_id, 'integrity_conflict', 'server')
    connection.commit()
    raise ResultConflictError


def _merge(connection, session_id, payload, *, completed=False):
    saved = _observations(connection, session_id)
    checkpoint = connection.execute(
        'SELECT provenance FROM web_session_checkpoints WHERE session_id=%s', (session_id,),
    ).fetchone()
    provenance = {key: value for key, value in payload.items() if key != 'trials'}
    if checkpoint and _hash(checkpoint[0]) != _hash(provenance):
        _conflict(connection, session_id)
    trials = payload['trials']
    # Posicoes/consecutividade ja validadas pelo dominio; comparar antes de inserir.
    for trial in trials:
        index = trial['trial_number'] - 1
        if index < len(saved) and _hash(saved[index]) != _hash(trial):
            _conflict(connection, session_id)
    if trials[0]['trial_number'] > len(saved) + 1:
        raise ConflictError
    new = [trial for trial in trials if trial['trial_number'] > len(saved)]
    if completed and new:
        raise ConflictError
    return saved, new, provenance


def _store(connection, session_id, saved, new, provenance):
    if not new:
        return
    connection.cursor().executemany(
        """INSERT INTO web_session_observations
           (session_id,trial_number,condition_id,payload,payload_sha256)
           VALUES (%s,%s,%s,%s,%s)""",
        [(session_id,trial['trial_number'],trial['condition_id'],Jsonb(trial),_hash(trial)) for trial in new],
    )
    prefix = saved + new
    connection.execute(
        """INSERT INTO web_session_checkpoints(session_id,provenance,confirmed_through,prefix_hash)
           VALUES (%s,%s,%s,%s) ON CONFLICT (session_id) DO UPDATE
           SET confirmed_through=EXCLUDED.confirmed_through,prefix_hash=EXCLUDED.prefix_hash,
               received_at=clock_timestamp()""",
        (session_id,Jsonb(provenance),len(prefix),_hash({**provenance,'trials':prefix})),
    )


def reconcile_complete(connection, session_id, payload, *, completed):
    # Historico anterior a 0011 nao recebe ACK fabricado em um retry.
    saved = _observations(connection, session_id)
    if completed and not saved:
        return
    saved, new, provenance = _merge(connection, session_id, payload, completed=completed)
    _store(connection, session_id, saved, new, provenance)


def checkpoint(database_url, token_hash, payload, prepare):
    try:
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            row = _eligible_session(connection, token_hash)
            _unexpired(connection, row)
            if row[1] not in {'running','aborted','completed'} or row[4] is None:
                raise ConflictError
            order = tuple(item[0] for item in connection.execute(
                'SELECT condition_id FROM web_session_main_order WHERE session_id=%s ORDER BY trial_number',
                (row[0],),
            ).fetchall())
            saved = _observations(connection, row[0])
            # Schema antes de usar qualquer posicao recebida. A continuidade do trecho
            # sobreposto e conferida desde sua posicao inicial, sem reconstruir motor.
            prepare(order, row[5], 0, schema_only=True)
            first = payload['trials'][0]['trial_number']
            if first > len(saved) + 1:
                raise ConflictError
            previous_end = saved[first-2]['trial_end_ms'] if first > 1 else 0
            result = prepare(order, row[5], previous_end)
            # Sessoes historicas completed nao podem ganhar observacoes novas.
            if row[1] == 'completed' and not saved:
                raise ConflictError
            saved, new, provenance = _merge(connection, row[0], payload, completed=row[1] == 'completed')
            if not result['timing_valid']:
                mark_invalid(connection, row[0], 'timing_invalid', 'server')
            _store(connection, row[0], saved, new, provenance)
            # Validar novamente o prazo imediatamente antes do commit/ACK.
            _unexpired(connection, row, rollback=True)
            return {'session_id': str(row[0]), **checkpoint_receipt(connection, row[0])}
    except psycopg.Error as exc:
        raise PersistenceError from exc


def _invalidate_locked(connection, row, reason, event_at_ms, source, actor_id=None):
    # Eventos posteriores ao encerramento integro nao invalidam o bloco.
    if row[1] == 'completed' and event_at_ms is not None:
        end = connection.execute(
            """SELECT o.trial_end_ms FROM web_trial_observations o
               JOIN web_assessments a USING(assessment_id)
               WHERE a.session_id=%s AND o.trial_number=16""", (row[0],),
        ).fetchone()
        if end and event_at_ms >= end[0] and not invalidated(connection, row[0]):
            return {'session_id':str(row[0]), 'valid_for_result':True}
    mark_invalid(connection, row[0], reason, source, event_at_ms, actor_id)
    if row[1] in {'preparing','running'}:
        connection.execute(
            "UPDATE web_participant_sessions SET state='aborted',abort_reason=%s WHERE session_id=%s",
            (reason,row[0]),
        )
    return {'session_id':str(row[0]), 'valid_for_result':False}


def invalidate(database_url, token_hash, reason, event_at_ms):
    try:
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            row = _eligible_session(connection, token_hash)
            _unexpired(connection, row)
            return _invalidate_locked(connection,row,reason,event_at_ms,'participant')
    except psycopg.Error as exc:
        raise PersistenceError from exc


def invalidate_professional(database_url, project_id, session_id, actor, reason, event_at_ms):
    try:
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            project = connection.execute(
                'SELECT active FROM web_projects WHERE project_id=%s FOR SHARE', (project_id,),
            ).fetchone()
            member = connection.execute(
                'SELECT active FROM web_project_members WHERE project_id=%s AND issuer=%s AND subject=%s FOR SHARE',
                (project_id,actor.issuer,actor.subject),
            ).fetchone()
            user = connection.execute('SELECT active,role FROM public.web_lock_emitter(%s,%s)',
                                      (actor.issuer,actor.subject)).fetchone()
            if (not project or not project[0] or not member or not member[0] or not user
                    or not user[0] or user[1] not in {'importacao','administracao'}):
                raise MissingError
            invitation = connection.execute(
                'SELECT session_id FROM web_invitations WHERE project_id=%s AND session_id=%s FOR UPDATE',
                (project_id,session_id),
            ).fetchone()
            if not invitation:
                raise MissingError
            row = connection.execute('SELECT session_id,state FROM web_participant_sessions WHERE session_id=%s',
                                      (session_id,)).fetchone()
            if not row:
                raise MissingError
            return _invalidate_locked(connection,row,reason,event_at_ms,'professional',
                                      opaque_user_id(actor.issuer,actor.subject))
    except psycopg.Error as exc:
        raise PersistenceError from exc
