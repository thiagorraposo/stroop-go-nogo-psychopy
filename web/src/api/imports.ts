/** Importacao CSV WEB autenticada; o nome original nunca sai do navegador. */
import { ApiError, record, request } from './client'
import type { ApiPath, ProfessionalProfile } from './client'

export type CsvImportStatus = 'recebido' | 'validado' | 'importado' | 'rejeitado'
export type CsvImportEvent = {
  operation_id: string; status: CsvImportStatus; error_code: string | null
  assessment_id: string | null; created_at: string; updated_at: string
}

const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i
const date = (value: unknown): value is string => typeof value === 'string'
  && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/.test(value)
  && Number.isFinite(Date.parse(value))

function decodeEvent(value: unknown): CsvImportEvent {
  const keys = ['operation_id', 'status', 'error_code', 'assessment_id', 'created_at', 'updated_at']
  if (!record(value) || Object.keys(value).length !== keys.length || keys.some(key => !Object.hasOwn(value, key))
    || typeof value.operation_id !== 'string' || !uuid.test(value.operation_id)
    || !['recebido', 'validado', 'importado', 'rejeitado'].includes(String(value.status))
    || !(value.error_code === null || ['invalid_csv', 'duplicate_assessment', 'validation_or_service_failure'].includes(String(value.error_code)))
    || !(value.assessment_id === null || typeof value.assessment_id === 'string' && /^[A-Za-z0-9_.-]{1,128}$/.test(value.assessment_id))
    || !date(value.created_at) || !date(value.updated_at)) throw new ApiError('invalid_response', 200)
  return value as CsvImportEvent
}

function path(projectId: string, operationId: string): ApiPath {
  if (!uuid.test(projectId) || !uuid.test(operationId)) throw new ApiError('invalid_request', 422)
  return `/api/v1/projects/${projectId}/imports/${operationId}`
}

export function uploadCsvImport(projectId: string, operationId: string, blob: Blob,
  profile: ProfessionalProfile): Promise<CsvImportEvent> {
  return request(path(projectId, operationId), {
    method: 'POST', headers: {
      Accept: 'application/json', 'Content-Type': 'text/csv; charset=utf-8',
      'X-CSRF-Token': profile.csrf_token,
    }, body: blob,
  }, async response => {
    if (response.status !== 200) throw new ApiError('invalid_response', response.status)
    let body: unknown
    try { body = await response.json() } catch { throw new ApiError('invalid_response', 200) }
    return decodeEvent(body)
  }, undefined, 60_000)
}

export function getCsvImportStatus(projectId: string, operationId: string,
  signal?: AbortSignal): Promise<CsvImportEvent> {
  return request(path(projectId, operationId), { method: 'GET', headers: { Accept: 'application/json' } }, async response => {
    if (response.status !== 200) throw new ApiError('invalid_response', response.status)
    let body: unknown
    try { body = await response.json() } catch { throw new ApiError('invalid_response', 200) }
    return decodeEvent(body)
  }, signal)
}
