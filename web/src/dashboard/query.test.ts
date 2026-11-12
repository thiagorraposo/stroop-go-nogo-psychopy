import { expect, test } from 'vitest'
import { defaultQuery, normalizeQuery, queryKey, supportsLegacyExport, assessmentQueryFilters } from './query'

test('QUERY7: normaliza seleções equivalentes, vazios e transporte sem perder dimensões', () => {
  const first = { projects: ['b', 'a', 'b'], filters: { participant_id: ['B', 'A', 'A'], visit: [], limit: 1, test_code: '' } }
  const second = { projects: ['a', 'b'], filters: { participant_id: ['A', 'B'] } }
  expect(queryKey(first)).toBe(queryKey(second))
  expect(normalizeQuery(first).filters).toEqual({ participant_id: ['A', 'B'] })
  const key = queryKey(second)
  expect(queryKey({ ...second, filters: { ...second.filters, platform: ['web'] } })).not.toBe(key)
  expect(queryKey({ ...second, filters: { ...second.filters, test_version: ['2'] } })).not.toBe(key)
  expect(queryKey({ ...second, filters: { ...second.filters, test_code: 'other' } })).not.toBe(key)
  expect(queryKey({ projects: ['a'], filters: { test_code: ['b', 'a', 'b'] } }))
    .toBe(queryKey({ projects: ['a'], filters: { test_code: ['a', 'b'] } }))
  expect(queryKey({ projects: ['a'], filters: { test_code: 'a' } }))
    .toBe(queryKey({ projects: ['a'], filters: { test_code: ['a'] } }))
})

test('QUERY7: qualquer recorte avançado não suportado bloqueia exportação agregada', () => {
  const query = defaultQuery('a')
  expect(supportsLegacyExport(query)).toBe(true)
  for (const changes of [{ searchText: 'PAT-1' }, { status: 'all' as const }, { accuracyRange: 'under50' as const },
    { rtRange: 'under500ms' as const }, { includeNullRt: false }, { condition: ['congruent'] as import('./query').Condition[] }, { responseType: ['hit'] as import('./query').ResponseType[] }]) {
    expect(supportsLegacyExport({ ...query, advanced: { ...query.advanced!, ...changes } })).toBe(false)
  }
  expect(supportsLegacyExport({ ...query, advanced: { ...query.advanced!, sortBy: 'participant', sortOrder: 'asc' } })).toBe(true)
})

test('QUERY7: condição/resposta são conjuntos canônicos e chegam integralmente ao servidor', () => {
  const query = defaultQuery('a')
  query.filters.test_code = ['stroop_go_nogo_ptbr']
  query.advanced!.condition = ['incongruent', 'congruent', 'congruent']
  query.advanced!.responseType = ['omission', 'hit', 'hit']
  const equivalent = structuredClone(query)
  equivalent.advanced!.condition = ['congruent', 'incongruent']
  equivalent.advanced!.responseType = ['hit', 'omission']
  expect(queryKey(query)).toBe(queryKey(equivalent))
  expect(assessmentQueryFilters(query)).toEqual({ test_code: ['stroop_go_nogo_ptbr'],
    condition: ['congruent', 'incongruent'], response_type: ['hit', 'omission'] })
  equivalent.advanced!.responseType = ['commission']
  expect(queryKey(equivalent)).not.toBe(queryKey(query))
  expect(supportsLegacyExport(query)).toBe(false)
})
