"""Conclusao WEB com validacao do dominio dentro da transacao de persistencia."""

from stroop.domain.web_results import InvalidResultError, validate_result
from stroop.persistence.web_sessions import (
    ConflictError, ExpiredError, MissingError, ResultConflictError, UnknownCredentialError,
    complete_participant_session,
)
from stroop.persistence.auth import PersistenceError


def complete(database_url: str, token_hash: str, payload: dict, conditions: list[dict],
             validate_schema=None):
    def prepare(order: tuple[int, ...], app_version: str):
        if validate_schema is not None:
            validate_schema(payload)
        return validate_result(payload, order, app_version, conditions)

    return complete_participant_session(database_url, token_hash, payload, prepare)
