"""Conclusao WEB com validacao do dominio dentro da transacao de persistencia."""

from stroop.domain.web_results import InvalidResultError, validate_result
from stroop.persistence.web_sessions import (
    ConflictError, ExpiredError, MissingError, ResultConflictError, UnknownCredentialError,
    complete_participant_session,
)
from stroop.persistence.auth import PersistenceError


def complete(database_url: str, token_hash: str, payload: dict, conditions: list[dict],
             validate_schema=None):
    def prepare(order: tuple[int, ...], app_version: str, *, observations_only=False):
        if validate_schema is not None:
            validate_schema(payload)
        if observations_only:
            from stroop.domain.web_results import validate_checkpoint
            return validate_checkpoint(payload, order, app_version, conditions)
        return validate_result(payload, order, app_version, conditions)

    return complete_participant_session(database_url, token_hash, payload, prepare)


def checkpoint(database_url, token_hash, payload, conditions, validate_schema=None):
    from stroop.domain.web_results import validate_checkpoint
    from stroop.persistence.web_checkpoints import checkpoint as persist

    def prepare(order, app_version, previous_end, *, schema_only=False):
        if validate_schema:
            validate_schema(payload)
        # Nao usar indices antes de conferir inclusive os tipos estritos do dominio.
        from stroop.domain.web_results import OrderConflictError
        try:
            return validate_checkpoint(payload, order, app_version, conditions,
                                       previous_end if not schema_only else 0)
        except OrderConflictError:
            raise ConflictError from None
    return persist(database_url, token_hash, payload, prepare)


def invalidate(database_url, token_hash, reason, event_at_ms):
    from stroop.persistence.web_checkpoints import invalidate as persist
    return persist(database_url, token_hash, reason, event_at_ms)


def invalidate_professional(database_url, project_id, session_id, actor, reason, event_at_ms):
    from stroop.persistence.web_checkpoints import invalidate_professional as persist
    return persist(database_url, project_id, session_id, actor, reason, event_at_ms)
