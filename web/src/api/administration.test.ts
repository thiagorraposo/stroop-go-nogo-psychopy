import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createAdminUser, listAdminUsers, listProjectMembers, setProjectMember, updateAdminUser } from './administration'

const id = 'aHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tAHN5bnRoZXRpYy11c2Vy'
const project = '00000000-0000-4000-8000-000000000001'
const csrf = 's'.repeat(43)
const user = { user_id: id, issuer: 'https://accounts.google.com', subject: 'synthetic-user', email: null, role: 'consulta', active: true }
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>
beforeEach(() => { fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock) })
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })
function json(body: unknown, status = 200) { return new Response(JSON.stringify(body), { status }) }

describe('administracao web', () => {
  it('pagina contas com cursor e contrato fechado', async () => {
    fetchMock.mockResolvedValue(json({ items: [user], next_cursor: 'cursor_sintetico' }))
    await expect(listAdminUsers({ limit: 10 })).resolves.toEqual({ items: [user], next_cursor: 'cursor_sintetico' })
    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/admin/users?limit=10')
    fetchMock.mockResolvedValue(json({ items: [{ ...user, email: 'nome@example.invalid' }], next_cursor: null }))
    await expect(listAdminUsers()).resolves.toMatchObject({ items: [{ email: 'nome@example.invalid' }] })
  })
  it('cria e altera contas por identidade, com CSRF e sem claims no caminho', async () => {
    fetchMock.mockResolvedValue(json(user, 201))
    await createAdminUser({ issuer: user.issuer, subject: user.subject, role: 'consulta', email: null }, csrf)
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('/api/v1/admin/users')
    expect(init?.method).toBe('POST')
    expect((init?.headers as Record<string, string>)['X-CSRF-Token']).toBe(csrf)
    expect(JSON.parse(String(init?.body))).toEqual({ issuer: user.issuer, subject: user.subject, role: 'consulta', email: null })
    fetchMock.mockResolvedValue(json({ user_id: id, role: 'importacao', active: false, email: null }))
    await expect(updateAdminUser(id, { role: 'importacao', active: false, email: null }, csrf))
      .resolves.toEqual({ user_id: id, role: 'importacao', active: false, email: null })
    expect(fetchMock.mock.calls[1]?.[0]).toBe(`/api/v1/admin/users/${id}`)
  })
  it('lista membros sem dados auxiliares e confirma a resposta de vinculo', async () => {
    fetchMock.mockResolvedValue(json({ items: [{ user_id: id, active: true }], next_cursor: null }))
    await expect(listProjectMembers(project)).resolves.toEqual({ items: [{ user_id: id, active: true }], next_cursor: null })
    fetchMock.mockResolvedValue(json({ user_id: id, active: false }))
    await expect(setProjectMember(project, id, false, csrf)).resolves.toEqual({ user_id: id, active: false })
    expect((fetchMock.mock.calls[1]?.[1]?.headers as Record<string, string>)['X-CSRF-Token']).toBe(csrf)
  })
  it('rejeita formatos inesperados e nao inicia solicitacao para payload invalido', async () => {
    fetchMock.mockResolvedValue(json({ items: [{ ...user, issuer: 'https://attacker.invalid' }], next_cursor: null }))
    await expect(listAdminUsers()).rejects.toMatchObject({ code: 'invalid_response' })
    expect(() => createAdminUser({ issuer: user.issuer, subject: 'has space', role: 'consulta', email: null }, csrf))
      .toThrowError(expect.objectContaining({ code: 'invalid_request' }))
    fetchMock.mockResolvedValue(json({ user_id: id, role: 'administracao', active: false, email: null }))
    await expect(updateAdminUser(id, { role: 'consulta', active: false, email: null }, csrf))
      .rejects.toMatchObject({ code: 'invalid_response' })
  })
})
