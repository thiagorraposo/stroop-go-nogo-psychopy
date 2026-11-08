// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { EvaluatorsPanel } from './EvaluatorsPanel'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const profileAdmin = {
  user_id: 'admin_sintetico',
  role: 'administracao' as const,
  expires_at: '2026-11-07T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const mockEvaluator1 = {
  id: '00000000-0000-4000-8000-000000000101',
  evaluator_code: 'EVA-0001',
  full_name: 'Dra. Beatriz Sintetica',
  normalized_name: 'DRA. BEATRIZ SINTETICA',
  initials: 'DBS',
  active: true,
  created_at: '2026-11-01T10:00:00Z',
  updated_at: '2026-11-01T10:00:00Z',
  assessment_count: 5,
  last_assessment_at: '2026-11-06T11:00:00Z',
}

const mockEvaluatorDetail = {
  ...mockEvaluator1,
  assessments: [
    {
      assessment_id: '44444444-4444-4444-8444-444444444444',
      project_id: '11111111-1111-4111-8111-111111111111',
      project_code: 'PROJ_DEMO',
      test_code: 'stroop_go_nogo_ptbr',
      test_version: '1.0.0',
      visit: 'V1',
      created_at: '2026-11-06T11:00:00Z',
    },
  ],
}

let container: HTMLDivElement
let root: ReturnType<typeof createRoot>
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function setInputValue(element: HTMLInputElement | HTMLSelectElement, value: string) {
  const prototype =
    element instanceof HTMLSelectElement ? HTMLSelectElement.prototype : HTMLInputElement.prototype
  const setter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set
  setter?.call(element, value)
  element.dispatchEvent(new Event('input', { bubbles: true }))
  element.dispatchEvent(new Event('change', { bubbles: true }))
}

beforeEach(() => {
  container = document.createElement('div')
  document.body.append(container)
  root = createRoot(container)
  fetchMock = vi.fn<typeof fetch>()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(async () => {
  await act(async () => root.unmount())
  container.remove()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

test('renderiza avaliadores, exibe aviso arquitetural e abre ficha detalhada', async () => {
  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/api/v1/evaluators/00000000-0000-4000-8000-000000000101')) {
      return jsonResponse(mockEvaluatorDetail)
    }
    if (url.startsWith('/api/v1/evaluators')) {
      return jsonResponse({
        items: [mockEvaluator1],
        total: 1,
        page: 1,
        page_size: 20,
      })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<EvaluatorsPanel profile={profileAdmin} />)
  })

  // Confere aviso arquitetural (distinção entre autenticação e identificação de autoria)
  expect(container.textContent).toContain('Aviso arquitetural (ADR-006 / ADR-007)')
  expect(container.textContent).toContain('conta compartilhada para autenticação local')

  // Confere que a tabela listou o avaliador com código EVA-...
  expect(container.textContent).toContain('EVA-0001')
  expect(container.textContent).toContain('Dra. Beatriz Sintetica')

  // Abre ficha
  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  expect(viewButton).not.toBeNull()
  await act(async () => {
    viewButton.click()
  })

  expect(container.textContent).toContain('Ficha cadastral do avaliador')
  expect(container.textContent).toContain('Avaliações conduzidas por este avaliador')
  expect(container.textContent).toContain('44444444-4444-4444-8444-444444444444')
})

test('cadastra novo avaliador e atualiza lista', async () => {
  let created = false
  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    const method = init?.method ?? 'GET'

    if (url.startsWith('/api/v1/evaluators') && method === 'POST') {
      created = true
      return jsonResponse(
        {
          id: '00000000-0000-4000-8000-000000000102',
          evaluator_code: 'EVA-0002',
          full_name: 'Dr. Carlos Sintetico',
          initials: 'DCS',
          active: true,
          created_at: '2026-11-07T12:00:00Z',
          updated_at: '2026-11-07T12:00:00Z',
          assessment_count: 0,
          last_assessment_at: null,
        },
        201,
      )
    }

    if (url.startsWith('/api/v1/evaluators')) {
      return jsonResponse({
        items: created ? [mockEvaluator1, { ...mockEvaluator1, id: '2', evaluator_code: 'EVA-0002' }] : [mockEvaluator1],
        total: created ? 2 : 1,
        page: 1,
        page_size: 20,
      })
    }

    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<EvaluatorsPanel profile={profileAdmin} />)
  })

  const openButton = container.querySelector('button.primary') as HTMLButtonElement
  await act(async () => {
    openButton.click()
  })

  const nameInput = container.querySelector('#evaluator-fullname') as HTMLInputElement
  await act(async () => {
    setInputValue(nameInput, 'Dr. Carlos Sintetico')
  })

  const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
  await act(async () => {
    submitButton.click()
  })

  expect(created).toBe(true)
  expect(container.textContent).toContain('Avaliador cadastrado com sucesso! Código gerado: EVA-0002')
})
