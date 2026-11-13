import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { queryAnalysis } from './analysis'
import { analysisQueryBody, defaultQuery } from '../dashboard/query'
import { analysisFixture } from '../test/analysis-fixture'

const body = analysisQueryBody(defaultQuery('11111111-1111-4111-8111-111111111111'))
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>
beforeEach(() => { fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock) })
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })
test('POST único leva consulta/CSRF no corpo e preserva transporte seguro', async () => {
  fetchMock.mockResolvedValue(new Response(JSON.stringify(analysisFixture(body, []))))
  const page = await queryAnalysis(body, 's'.repeat(43))
  expect(page.counts.assessments).toBe(0)
  expect(fetchMock).toHaveBeenCalledWith('/api/v1/analysis/query', expect.objectContaining({
    method: 'POST', credentials: 'same-origin', cache: 'no-store', redirect: 'error', body: JSON.stringify(body),
    headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': 's'.repeat(43) },
  }))
})
test.each([
  { normalized_query: { ...body.query, filters: { status: 'valid' } } },
  { completeness: 'partial' }, { counts: { participants: 0, visits: 0, assessments: 5001, trials: 0 } },
  { expires_at: '2000-01-01T00:00:00Z' }, { next_cursor: 'https://external.invalid' },
  { participant_name: 'NOME_SINTETICO' }, { indicator_definitions: { name: 'NOME_SINTETICO' } },
  { aggregates: [{ project_id: body.query.projects[0], assessments: 1, trials: 0 }] },
  { legacy_export_context: { filters: { participant_name: 'NOME_SINTETICO' }, projects: [] } },
  { capabilities: { exports: true } },
])('recusa contexto incompleto, divergente ou aberto %#', async overrides => {
  fetchMock.mockResolvedValue(new Response(JSON.stringify(analysisFixture(body, [], overrides))))
  await expect(queryAnalysis(body, 's'.repeat(43))).rejects.toMatchObject({ code: 'invalid_response' })
})
test('erro POST nunca tenta GET ou remove filtros para repetir', async () => {
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ error: { code: 'invalid_request' } }), { status: 422 }))
  await expect(queryAnalysis(body, 's'.repeat(43))).rejects.toMatchObject({ status: 422 })
  expect(fetchMock).toHaveBeenCalledTimes(1)
})
