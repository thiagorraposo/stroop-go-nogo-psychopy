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
  instruments: ['stroop_go_nogo_ptbr'],
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
  audit_history: [
    {
      event_id: '88888888-8888-8888-8888-888888888888',
      entity_type: 'evaluator',
      action: 'create',
      reason_code: 'cadastro_inicial',
      occurred_at: '2026-11-01T10:00:00Z',
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

test('exibe instrumentos e trilha de auditoria na ficha detalhada do avaliador', async () => {
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

  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  await act(async () => {
    viewButton.click()
  })

  // Confere instrumentos utilizados
  expect(container.textContent).toContain('Instrumentos utilizados')
  expect(container.textContent).toContain('stroop_go_nogo_ptbr')

  // Confere trilha de auditoria
  expect(container.textContent).toContain('Trilha de auditoria cadastral')
  expect(container.textContent).toContain('cadastro_inicial')
})

test('edita dados cadastrais do avaliador com motivo obrigatório', async () => {
  let patchPayload: unknown = null
  let currentDetail = { ...mockEvaluatorDetail }

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    const method = init?.method ?? 'GET'

    if (url.includes('/api/v1/evaluators/00000000-0000-4000-8000-000000000101') && method === 'PATCH') {
      patchPayload = JSON.parse(init?.body as string)
      currentDetail = {
        ...currentDetail,
        full_name: 'Dra. Beatriz Sintetica Retificada',
        initials: 'DBSR',
      }
      return jsonResponse(currentDetail)
    }

    if (url.includes('/api/v1/evaluators/00000000-0000-4000-8000-000000000101')) {
      return jsonResponse(currentDetail)
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

  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  await act(async () => {
    viewButton.click()
  })

  const editButton = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.trim() === 'Editar cadastro',
  )
  expect(editButton).not.toBeUndefined()
  await act(async () => {
    editButton!.click()
  })

  expect(container.textContent).toContain('Editar dados cadastrais do avaliador')

  const nameInput = container.querySelector('#edit-evaluator-fullname') as HTMLInputElement
  const initialsInput = container.querySelector('#edit-evaluator-initials') as HTMLInputElement
  const reasonInput = container.querySelector('#edit-evaluator-reason') as HTMLInputElement

  await act(async () => {
    setInputValue(nameInput, 'Dra. Beatriz Sintetica Retificada')
    setInputValue(initialsInput, 'DBSR')
    setInputValue(reasonInput, 'correcao_titulacao')
  })

  const saveButton = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.trim() === 'Salvar alterações',
  )
  expect(saveButton).not.toBeUndefined()
  await act(async () => {
    saveButton!.click()
  })

  expect(patchPayload).toEqual({
    full_name: 'Dra. Beatriz Sintetica Retificada',
    initials: 'DBSR',
    reason_code: 'correcao_titulacao',
  })
  expect(container.textContent).toContain('atualizado com sucesso (evento auditado)')
})

test('executa procedimento administrativo auditado para correção de vínculo da avaliação conduzida', async () => {
  let relinkCalled = false
  let relinkPayload: unknown = null

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    const method = init?.method ?? 'GET'

    if (url.includes('/relink') && method === 'POST') {
      relinkCalled = true
      relinkPayload = JSON.parse(init?.body as string)
      return jsonResponse({
        assessment_id: '44444444-4444-4444-8444-444444444444',
        project_id: '11111111-1111-4111-8111-111111111111',
        patient_id: '00000000-0000-4000-8000-000000000001',
        evaluator_id: '00000000-0000-4000-8000-000000000101',
        relinked: true,
      })
    }

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

  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  await act(async () => {
    viewButton.click()
  })

  const relinkButton = container.querySelector(
    'button[aria-label^="Corrigir vínculo da avaliação"]',
  ) as HTMLButtonElement
  expect(relinkButton).not.toBeNull()
  await act(async () => {
    relinkButton.click()
  })

  expect(container.textContent).toContain('Correção auditada de vínculo — Avaliação')

  const patientInput = container.querySelector('#relink-evaluator-new-pat') as HTMLInputElement
  const reasonInput = container.querySelector('#relink-evaluator-reason') as HTMLInputElement

  await act(async () => {
    setInputValue(patientInput, '00000000-0000-4000-8000-000000000001')
    setInputValue(reasonInput, 'correcao_erro_humano_paciente')
  })

  const submitRelinkButton = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.trim() === 'Confirmar revinculação auditada',
  )
  expect(submitRelinkButton).not.toBeUndefined()
  await act(async () => {
    submitRelinkButton!.click()
  })

  expect(relinkCalled).toBe(true)
  expect(relinkPayload).toEqual({
    patient_id: '00000000-0000-4000-8000-000000000001',
    reason_code: 'correcao_erro_humano_paciente',
  })
  expect(container.textContent).toContain('corrigido com sucesso (evento auditado)')
})
