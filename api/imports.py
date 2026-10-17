"""Importacao CSV minimizada sob vinculo explicito de projeto."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import tempfile
from uuid import UUID

from fastapi import APIRouter, Request

from api.errors import APIError
from api.sessions import _professional_read, _professional_write, _reject_query
from stroop.application import web_imports as application
from stroop.persistence.auth import PersistenceError


router = APIRouter(prefix='/api/v1/projects/{project_id}/imports', tags=['imports'])
CSV_MEDIA_TYPE = re.compile(r'^text/csv(?:\s*;\s*charset=utf-8)?$', re.IGNORECASE)


def _response(event: dict) -> dict:
    return {
        'operation_id': str(event['operation_id']),
        'status': event['status'],
        'error_code': event['error_code'],
        'assessment_id': event['assessment_id'],
        'created_at': event['created_at'].isoformat().replace('+00:00', 'Z'),
        'updated_at': event['updated_at'].isoformat().replace('+00:00', 'Z'),
    }


def _database_error() -> APIError:
    return APIError('service_unavailable')


@router.post('/{operation_id}')
async def upload_csv(project_id: UUID, operation_id: UUID, request: Request):
    _reject_query(request)
    actor = _professional_write(request, 'import_csv')
    content_types = request.headers.getlist('content-type')
    if len(content_types) != 1 or not CSV_MEDIA_TYPE.fullmatch(content_types[0]):
        raise APIError('unsupported_media_type')
    content = await request.body()
    if not content:
        raise APIError('invalid_request')
    digest = hashlib.sha256(content).hexdigest()
    database_url = request.app.state.config.database_url
    try:
        event = application.begin(database_url, operation_id, project_id, actor, digest)
        if event['status'] in {'importado', 'rejeitado'}:
            return _response(event)
        with tempfile.TemporaryDirectory(prefix='stroop-web-import-') as directory:
            path = Path(directory) / f'{operation_id}.csv'
            path.write_bytes(content)
            path.chmod(0o600)
            event = application.process(database_url, operation_id, project_id,
                                        actor, digest, path)
        return _response(event)
    except application.ImportNotFound:
        raise APIError('not_found') from None
    except application.ImportConflict:
        raise APIError('state_conflict') from None
    except PersistenceError:
        raise _database_error() from None


@router.get('/{operation_id}')
async def get_import_status(project_id: UUID, operation_id: UUID, request: Request):
    await request.body()  # Empty-body invariant and request-boundary replay.
    _reject_query(request)
    actor = _professional_read(request, 'import_csv')
    try:
        event = application.status(request.app.state.config.database_url,
                                   operation_id, project_id, actor)
    except PersistenceError:
        raise _database_error() from None
    if event is None:
        raise APIError('not_found')
    return _response(event)
