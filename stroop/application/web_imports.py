"""Orquestracao de importacao CSV WEB com validacao compartilhada."""
from __future__ import annotations

import csv
from pathlib import Path
from uuid import UUID

from stroop.application import clock
from stroop.domain.errors import ImportValidationError, InstrumentValidationError
from stroop.ingestion.instruments import load_instrument_csv
from stroop.persistence import web_imports as persistence
from stroop.persistence.auth import PersistenceError

ImportNotFound = persistence.ImportNotFound
ImportConflict = persistence.ImportConflict
MAX_RECORDS = 10_000


def _check_record_limit(path: Path) -> None:
    with path.open('r', newline='', encoding='utf-8-sig') as source:
        for number, _ in enumerate(csv.reader(source), start=1):
            if number > MAX_RECORDS + 1:
                raise ValueError


def begin(database_url, operation_id: UUID, project_id: UUID, actor, content_sha256: str):
    return persistence.begin(database_url, operation_id, project_id, actor.issuer,
                             actor.subject, content_sha256)


def status(database_url, operation_id: UUID, project_id: UUID, actor):
    return persistence.status(database_url, operation_id, project_id, actor.issuer, actor.subject)


def process(database_url, operation_id: UUID, project_id: UUID, actor,
            content_sha256: str, csv_path: Path) -> dict:
    try:
        _check_record_limit(csv_path)
        normalized = load_instrument_csv(csv_path)
    except (InstrumentValidationError, ImportValidationError, OSError, UnicodeError,
            ValueError, OverflowError, csv.Error):
        return persistence.reject(database_url, operation_id, project_id, actor.issuer,
                                  actor.subject, 'invalid_csv')

    # A rota aceita somente a copia minimizada produzida pelo cliente. A
    # validacao do servidor protege contra clientes alternativos ou adulterados.
    if (normalized.metadata.get('participant_name') != 'NAO_COLETADO'
            or normalized.metadata.get('initials', '') != ''):
        return persistence.reject(database_url, operation_id, project_id, actor.issuer,
                                  actor.subject, 'invalid_csv')

    event = persistence.mark_validated(database_url, operation_id, project_id,
                                       actor.issuer, actor.subject)
    if event['status'] in {'importado', 'rejeitado'}:
        return event
    return persistence.import_normalized(
        database_url, operation_id, project_id, actor.issuer, actor.subject,
        content_sha256, normalized, clock.utc_now_iso(),
    )
