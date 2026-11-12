// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { ProfessionalDashboard } from './ProfessionalDashboard'
import { getAssessment, getAssessmentOptions, listAssessments, listProjects } from '../api/assessments'
import type { Assessment, Page } from '../api/assessments'

vi.mock('../api/assessments', async importOriginal => ({
  ...await importOriginal<typeof import('../api/assessments')>(),
  listProjects: vi.fn(), listAssessments: vi.fn(), getAssessmentOptions: vi.fn(), getAssessment: vi.fn(),
}))
vi.mock('../api/patients', () => ({ listPatients: vi.fn(async () => ({ total: 0 })) }))
Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
const project = '11111111-1111-4111-8111-111111111111'
const second = '22222222-2222-4222-8222-222222222222'
const profile = { user_id: 'synthetic', role: 'consulta' as const, csrf_token: 's'.repeat(43), expires_at: '2099-01-01T00:00:00Z' }
const row = (id: string): Assessment => ({ assessment_id: id, participant_id: id, visit: 'V1', evaluator_id: null,
  created_at: '2026-11-11T00:00:00Z', started_at: '2026-11-11T00:00:00Z', platform: 'web', test_code: 'stroop_go_nogo_ptbr',
  test_version: '1', protocol_id: null, app_version: null,
  summary: { accuracy: 100, accuracy_go_trials: 100, accuracy_no_go_trials: 100, total_go_trials: 1, total_no_go_trials: 1,
    response_time_seconds: 0.5, total_trials: 2, hits: 1, correct_rejections: 1, omission_errors: 0, commission_errors: 0 } })
const page = (id: string): Page<Assessment> => ({ items: [row(id)], next_cursor: null, snapshot: 'synthetic' })
function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (error: unknown) => void
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
let host: HTMLDivElement
let root: ReturnType<typeof createRoot>
function button(name: string) { return [...host.querySelectorAll('button')].find(b => b.textContent?.trim() === name)! }
async function start() { await act(async () => root.render(<ProfessionalDashboard profile={profile} />)) }
async function applyDate() {
  await act(async () => {
    const input = host.querySelector('input[type=date]')!
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, '2026-11-01')
    input.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await act(async () => button('Aplicar filtros').click())
}
beforeEach(() => {
  vi.resetAllMocks()
  host = document.createElement('div'); document.body.append(host); root = createRoot(host)
  vi.mocked(listProjects).mockResolvedValue({ items: [project, second].map((id, i) => ({ id, code: `SYNTHETIC_${i}`, name: 'Sintético', active: true, created_at: '2026-11-11T00:00:00Z' })), next_cursor: null })
  vi.mocked(getAssessmentOptions).mockResolvedValue({ participant_id: [], visit: [], evaluator_id: [], test_version: ['1'], platform: ['web'], test_code: ['stroop_go_nogo_ptbr'] })
})
afterEach(async () => { await act(async () => root.unmount()); host.remove() })

test('QUERY7: resposta antiga, mesmo ignorando AbortSignal, não substitui projeto aplicado novo', async () => {
  const old = deferred<Page<Assessment>>()
  vi.mocked(listAssessments).mockImplementation(id => id === project ? old.promise : Promise.resolve(page('ATUAL')))
  await start()
  await act(async () => {
    const select = host.querySelector('select[multiple]') as HTMLSelectElement
    for (const option of select.options) option.selected = option.value === second
    select.dispatchEvent(new Event('change', { bubbles: true }))
  })
  await act(async () => button('Aplicar filtros').click())
  expect(host.querySelector('table.results-table')?.textContent).toContain('ATUAL')
  await act(async () => old.resolve(page('ATRASADA')))
  expect(host.textContent).not.toContain('ATRASADA')
  expect(host.querySelector('table.results-table')?.textContent).toContain('ATUAL')
})

test('QUERY7: erro na segunda página remove todo conjunto e nenhum total parcial aparece em outro módulo', async () => {
  const tail = deferred<Page<Assessment>>()
  vi.mocked(listAssessments).mockImplementation((_id, options) => options?.cursor ? tail.promise : Promise.resolve({ ...page('PARCIAL'), next_cursor: 'next' }))
  await start()
  expect(host.querySelector('.dashboard-cards')).toBeNull()
  await act(async () => tail.reject(new Error('synthetic-failure')))
  expect(host.querySelector('table.results-table')).toBeNull()
  await act(async () => button('Resultados e análises').click())
  expect(host.querySelector('.dashboard-cards')).toBeNull()
  expect(host.textContent).not.toContain('PARCIAL')
  expect(host.querySelector('[role=alert]')).not.toBeNull()
})

test('QUERY7: detalhe pendente do recorte anterior não reaparece depois de aplicar', async () => {
  vi.mocked(listAssessments).mockImplementation((_id, options) => Promise.resolve(page(options?.start_date ? 'ATUAL' : 'ANTIGA')))
  const detail = deferred<Awaited<ReturnType<typeof getAssessment>>>()
  vi.mocked(getAssessment).mockReturnValue(detail.promise)
  await start()
  await act(async () => [...host.querySelectorAll('button')].find(b => b.getAttribute('aria-label')?.startsWith('Ver avaliação'))!.click())
  await applyDate()
  await act(async () => detail.resolve({ ...row('ANTIGA'), project_id: project, session_id: null, completed_at: null, metrics: [], trials: [], frame_period_ms: null }))
  expect(host.querySelector('[aria-label="Detalhe da avaliação"]')).toBeNull()
  expect(host.querySelector('table.results-table')?.textContent).toContain('ATUAL')
})

test('QUERY7: mesma consulta/rascunho atravessa análise, histórico e exportação sem reaplicar', async () => {
  vi.mocked(listAssessments).mockResolvedValue(page('ATUAL'))
  await start(); await applyDate()
  const count = vi.mocked(listAssessments).mock.calls.length
  for (const name of ['Avaliações e histórico', 'Resultados e análises', 'Exportações', 'Visão geral (Dashboard)']) {
    await act(async () => button(name).click())
    expect((host.querySelector('input[type=date]') as HTMLInputElement).value).toBe('2026-11-01')
  }
  expect(vi.mocked(listAssessments).mock.calls.length).toBe(count)
  expect(host.querySelectorAll('form[aria-label="Filtros da consulta"]')).toHaveLength(1)
})
