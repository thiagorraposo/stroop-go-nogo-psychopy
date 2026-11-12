import { expect, test } from 'vitest'
import { defaultQuery, normalizeQuery, queryKey, supportsLegacyExport } from './query'

test('QUERY7: normaliza seleções equivalentes, vazios e transporte sem perder dimensões', () => {
  const first = { projects: ['b', 'a', 'b'], filters: { participant_id: ['B', 'A', 'A'], visit: [], limit: 1, test_code: '' } }
  const second = { projects: ['a', 'b'], filters: { participant_id: ['A', 'B'] } }
  expect(queryKey(first)).toBe(queryKey(second))
  expect(normalizeQuery(first).filters).toEqual({ participant_id: ['A', 'B'] })
  const key = queryKey(second)
  expect(queryKey({ ...second, filters: { ...second.filters, platform: ['web'] } })).not.toBe(key)
  expect(queryKey({ ...second, filters: { ...second.filters, test_version: ['2'] } })).not.toBe(key)
  expect(queryKey({ ...second, filters: { ...second.filters, test_code: 'other' } })).not.toBe(key)
})

test('QUERY7: qualquer recorte avançado não suportado bloqueia exportação agregada', () => {
  const query = defaultQuery('a')
  expect(supportsLegacyExport(query)).toBe(true)
  for (const changes of [{ searchText: 'PAT-1' }, { status: 'all' as const }, { accuracyRange: 'under50' as const },
    { rtRange: 'under500ms' as const }, { includeNullRt: false }, { condition: 'go' as const }, { responseType: 'hits' as const }]) {
    expect(supportsLegacyExport({ ...query, advanced: { ...query.advanced!, ...changes } })).toBe(false)
  }
  expect(supportsLegacyExport({ ...query, advanced: { ...query.advanced!, sortBy: 'participant', sortOrder: 'asc' } })).toBe(true)
})
