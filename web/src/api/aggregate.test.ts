import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { exportAssessmentView } from './aggregate'

const project = '00000000-0000-4000-8000-000000000001'
const context = { projects: [{ project_id: project, snapshot: 'a'.repeat(64) }], filters: { participant_id: ['P_SINTETICO'] } }
const view = { test_code: 'stroop_go_nogo_ptbr' }
const csrf = 's'.repeat(43)
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>
beforeEach(() => { fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock) })
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })

describe('exportacao agregada manual', () => {
  it('envia filtros e snapshots no corpo protegido e recebe blob com nome fixo', async () => {
    fetchMock.mockResolvedValue(new Response('assessment_id\r\nSINTETICO\r\n', { headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="stroop_go_nogo_ptbr_avaliacoes.csv"',
    } }))
    const result = await exportAssessmentView(context, view, csrf)
    expect(result.filename).toBe('stroop_go_nogo_ptbr_avaliacoes.csv')
    expect(result.blob.size).toBeGreaterThan(0)
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('/api/v1/assessments/export')
    expect(init).toMatchObject({ method: 'POST', credentials: 'same-origin', cache: 'no-store', redirect: 'error' })
    expect((init?.headers as Record<string, string>)['X-CSRF-Token']).toBe(csrf)
    expect(JSON.parse(String(init?.body))).toEqual({ projects: context.projects, filters: context.filters, view })
    expect(String(init?.body)).not.toContain('snapshot%')
  })
  it('nao repete POST nem aceita erro, arquivo ou contrato inseguro', async () => {
    fetchMock.mockResolvedValue(new Response('{"error":{"code":"state_conflict"}}', { status: 409 }))
    await expect(exportAssessmentView(context, view, csrf)).rejects.toMatchObject({ code: 'state_conflict' })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    for (const [type, disposition] of [['text/html', 'attachment; filename="x.csv"'], ['text/csv', 'inline']] as const) {
      fetchMock.mockResolvedValue(new Response('x', { headers: { 'Content-Type': type, 'Content-Disposition': disposition } }))
      await expect(exportAssessmentView(context, view, csrf)).rejects.toMatchObject({ code: 'invalid_response' })
    }
    expect(() => exportAssessmentView({ ...context, projects: [{ ...context.projects[0]!, snapshot: 'bad token' }] }, view, csrf))
      .toThrowError(expect.objectContaining({ code: 'invalid_request' }))
    expect(fetchMock).toHaveBeenCalledTimes(3)
  })
})
