/** Operacoes administrativas por identidade tecnica opaca. */
import { ApiError, record, request } from './client'
import type { ApiPath } from './client'
import type { Project } from './assessments'

export type AdminUser = { user_id: string;
  role: 'consulta' | 'importacao' | 'administracao'; active: boolean }
export type AdminPage<T> = { items: T[]; next_cursor: string | null }
export type ProjectMember = { user_id: string; active: boolean }
export type AdminPageOptions = { cursor?: string; limit?: number; signal?: AbortSignal }
const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i
const token = /^[A-Za-z0-9_-]{1,512}$/
function fail(): never { throw new ApiError('invalid_response', 200) }
function input(valid: boolean): void { if (!valid) throw new ApiError('invalid_request', 422) }
function closed(value: unknown, keys: string[]): value is Record<string, unknown> {
  return record(value) && Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key))
}
function page<T>(value: unknown, decode: (item: unknown) => T): AdminPage<T> {
  if (!closed(value, ['items', 'next_cursor']) || !Array.isArray(value.items)
    || !(value.next_cursor === null || typeof value.next_cursor === 'string' && token.test(value.next_cursor))) return fail()
  return { items: value.items.map(decode), next_cursor: value.next_cursor }
}
function user(value: unknown): AdminUser {
  if (!closed(value, ['user_id', 'role', 'active'])
    || typeof value.user_id !== 'string' || !token.test(value.user_id)
    || !['consulta', 'importacao', 'administracao'].includes(String(value.role)) || typeof value.active !== 'boolean') return fail()
  return value as AdminUser
}
function member(value: unknown): ProjectMember {
  if (!closed(value, ['user_id', 'active']) || typeof value.user_id !== 'string' || !token.test(value.user_id)
    || typeof value.active !== 'boolean') return fail()
  return value as ProjectMember
}
function query(options: AdminPageOptions = {}): URLSearchParams {
  input(options.limit === undefined || Number.isInteger(options.limit) && options.limit >= 1 && options.limit <= 100)
  input(options.cursor === undefined || token.test(options.cursor))
  const params = new URLSearchParams()
  if (options.limit !== undefined) params.set('limit', String(options.limit))
  if (options.cursor) params.set('cursor', options.cursor)
  return params
}
async function json<T>(path: ApiPath, method: string, body: unknown, signal: AbortSignal | undefined,
  decode: (value: unknown) => T, expected: number): Promise<T> {
  return request(path, { method, headers: { Accept: 'application/json', ...(body === undefined ? {} : {
    'Content-Type': 'application/json', 'X-CSRF-Token': (body as { csrf: string }).csrf,
  }) }, ...(body === undefined ? {} : { body: JSON.stringify(Object.fromEntries(Object.entries(body as object).filter(([key]) => key !== 'csrf'))) }) },
  async response => {
    if (response.status !== expected) throw new ApiError('invalid_response', response.status)
    let value: unknown
    try { value = await response.json() } catch { return fail() }
    return decode(value)
  }, signal)
}
function requestData(body: object, csrf: string): object {
  input(/^[A-Za-z0-9_-]{43}$/.test(csrf))
  return { ...body, csrf }
}
export function listAdminUsers(options: AdminPageOptions = {}): Promise<AdminPage<AdminUser>> {
  const params = query(options)
  return json(`/api/v1/admin/users${params.size ? `?${params}` : ''}` as ApiPath, 'GET', undefined, options.signal,
    value => page(value, user), 200)
}
export function updateAdminUser(userId: string, value: { role: AdminUser['role']; active: boolean }, csrf: string): Promise<AdminUser> {
  input(token.test(userId) && ['consulta', 'importacao', 'administracao'].includes(value.role)
    && typeof value.active === 'boolean')
  return json(`/api/v1/admin/users/${userId}` as ApiPath, 'PATCH', requestData(value, csrf), undefined, responseValue => {
    const decoded = user(responseValue)
    if (decoded.user_id !== userId || decoded.role !== value.role || decoded.active !== value.active) return fail()
    return decoded
  }, 200)
}
export function revokeAdminSessions(userId: string, csrf: string): Promise<void> {
  input(token.test(userId) && /^[A-Za-z0-9_-]{43}$/.test(csrf))
  return request(`/api/v1/admin/users/${userId}/sessions/revoke` as ApiPath, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: '{}',
  }, async response => { if (response.status !== 204) throw new ApiError('invalid_response', response.status) })
}
export function createProject(value: { code: string; name: string }, csrf: string): Promise<Project> {
  input(/^[A-Za-z0-9_.-]{1,64}$/.test(value.code) && value.name.trim().length >= 1 && value.name.trim().length <= 120)
  return json('/api/v1/projects', 'POST', requestData(value, csrf), undefined, value => {
    if (!closed(value, ['id', 'code', 'name', 'active', 'created_at']) || typeof value.id !== 'string' || !uuid.test(value.id)
      || typeof value.code !== 'string' || typeof value.name !== 'string' || typeof value.active !== 'boolean'
      || typeof value.created_at !== 'string' || !Number.isFinite(Date.parse(value.created_at))) return fail()
    return value as Project
  }, 201)
}
export function listProjectMembers(projectId: string, options: AdminPageOptions = {}): Promise<AdminPage<ProjectMember>> {
  input(uuid.test(projectId))
  const params = query(options)
  return json(`/api/v1/projects/${projectId}/members${params.size ? `?${params}` : ''}` as ApiPath,
    'GET', undefined, options.signal, value => page(value, member), 200)
}
export function setProjectMember(projectId: string, userId: string, active: boolean, csrf: string): Promise<ProjectMember> {
  input(uuid.test(projectId) && token.test(userId) && typeof active === 'boolean')
  return json(`/api/v1/projects/${projectId}/members/${userId}` as ApiPath, 'PUT', requestData({ active }, csrf), undefined, value => {
    if (!closed(value, ['user_id', 'active']) || value.user_id !== userId || value.active !== active) return fail()
    return value as ProjectMember
  }, 200)
}
