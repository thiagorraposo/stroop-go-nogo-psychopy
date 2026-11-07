import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { listAdminUsers, listProjectMembers, revokeAdminSessions, setProjectMember, updateAdminUser } from './administration'

const id = 'c3ludGhldGljLWxvY2FsLXVzZXI'
const project = '00000000-0000-4000-8000-000000000001'
const csrf = 's'.repeat(43)
const user = { user_id: id, role: 'consulta', active: true }
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>
beforeEach(() => { fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock) })
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })
function json(body: unknown, status = 200) { return new Response(JSON.stringify(body), { status }) }

describe('administracao local web', () => {
  it('pagina contas por identidade opaca com cursor e contrato fechado', async () => {
    fetchMock.mockResolvedValue(json({ items: [user], next_cursor: 'cursor_sintetico' }))
    await expect(listAdminUsers({ limit: 10 })).resolves.toEqual({ items: [user], next_cursor: 'cursor_sintetico' })
    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/admin/users?limit=10')
  })
  it('altera perfil e estado com PATCH e CSRF', async () => {
    fetchMock.mockResolvedValue(json({ user_id: id, role: 'importacao', active: false }))
    await expect(updateAdminUser(id, { role: 'importacao', active: false }, csrf))
      .resolves.toEqual({ user_id: id, role: 'importacao', active: false })
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe(`/api/v1/admin/users/${id}`)
    expect(init?.method).toBe('PATCH')
    expect((init?.headers as Record<string, string>)['X-CSRF-Token']).toBe(csrf)
    expect(JSON.parse(String(init?.body))).toEqual({ role: 'importacao', active: false })
  })
  it('revoga sessoes com corpo vazio e exige confirmacao 204', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }))
    await expect(revokeAdminSessions(id, csrf)).resolves.toBeUndefined()
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/v1/admin/users/${id}/sessions/revoke`)
    expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({ method: 'POST', body: '{}', headers: { 'X-CSRF-Token': csrf } })
    fetchMock.mockResolvedValue(json({}))
    await expect(revokeAdminSessions(id, csrf)).rejects.toMatchObject({ code: 'invalid_response' })
  })
  it('lista membros sem dados auxiliares e confirma a resposta de vinculo', async () => {
    fetchMock.mockResolvedValue(json({ items: [{ user_id: id, active: true }], next_cursor: null }))
    await expect(listProjectMembers(project)).resolves.toEqual({ items: [{ user_id: id, active: true }], next_cursor: null })
    fetchMock.mockResolvedValue(json({ user_id: id, active: false }))
    await expect(setProjectMember(project, id, false, csrf)).resolves.toEqual({ user_id: id, active: false })
    expect((fetchMock.mock.calls[1]?.[1]?.headers as Record<string, string>)['X-CSRF-Token']).toBe(csrf)
  })
  it('rejeita contrato legado ou dados de credencial e resposta divergente', async () => {
    for (const extra of [{ issuer: 'https://accounts.google.com' }, { password_hash: 'synthetic-invalid' }, { email: null }]) {
      fetchMock.mockResolvedValue(json({ items: [{ ...user, ...extra }], next_cursor: null }))
      await expect(listAdminUsers()).rejects.toMatchObject({ code: 'invalid_response' })
    }
    fetchMock.mockResolvedValue(json({ user_id: id, role: 'administracao', active: false }))
    await expect(updateAdminUser(id, { role: 'consulta', active: false }, csrf))
      .rejects.toMatchObject({ code: 'invalid_response' })
  })
})
