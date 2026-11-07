// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { SessionInvitation } from './SessionInvitation'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const project = {
  id: '00000000-0000-4000-8000-000000000001',
  code: 'PROJETO_SINTETICO',
  name: 'Pesquisa Sintética',
  active: true,
  created_at: '2026-11-01T10:00:00Z',
}
const profile = {
  user_id: 'conta_compartilhada_sintetica',
  role: 'importacao' as const,
  expires_at: '2026-11-07T18:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const existingPatient = {
  id: '00000000-0000-4000-8000-000000000101',
  participant_code: 'PAT-0001',
  full_name: 'Ana Carolina Sintetica',
  normalized_name: 'ANA CAROLINA SINTETICA',
  initials: 'ACS',
  disambiguation_note: 'Grupo Controle',
  active: true,
  created_at: '2026-11-07T10:00:00Z',
  updated_at: '2026-11-07T10:00:00Z',
  project_count: 1,
  assessment_count: 0,
  last_assessment_at: null,
}

const existingEvaluator = {
  id: '00000000-0000-4000-8000-000000000202',
  evaluator_code: 'EVA-0001',
  full_name: 'Dra. Beatriz Sintetica',
  normalized_name: 'DRA. BEATRIZ SINTETICA',
  initials: 'DBS',
  active: true,
  created_at: '2026-11-07T10:00:00Z',
  updated_at: '2026-11-07T10:00:00Z',
  assessment_count: 0,
  last_assessment_at: null,
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

test('seleciona paciente e avaliador cadastrados, preenche codigo readOnly e iniciais, exibe resumo para conferencia e emite convite', async () => {
  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({ items: [existingPatient], total: 1, page: 1, page_size: 50 })
    }
    if (url.startsWith('/api/v1/evaluators')) {
      return jsonResponse({ items: [existingEvaluator], total: 1, page: 1, page_size: 50 })
    }
    if (url.endsWith(`/projects/${project.id}/invitations`)) {
      return jsonResponse(
        {
          invitation_id: '00000000-0000-4000-8000-000000000301',
          session_id: '00000000-0000-4000-8000-000000000302',
          code: 'SINTETICO_CONVITE_PREP01_1234567890',
          expires_at: '2026-11-07T14:00:00Z',
          state: 'issued',
          summary: {
            project_id: project.id,
            project_code: project.code,
            project_name: project.name,
            patient_id: existingPatient.id,
            participant_code: existingPatient.participant_code,
            participant_name: existingPatient.full_name,
            initials: 'ACS',
            evaluator_id: existingEvaluator.id,
            evaluator_code: existingEvaluator.evaluator_code,
            evaluator_name: existingEvaluator.full_name,
            test_code: 'stroop_go_nogo_ptbr',
            test_version: '0.2.2-web.1',
            protocol_id: 'stroop_go_nogo_ptbr/0.2.2-web.1',
            visit: 'T1',
          },
        },
        201,
      )
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<SessionInvitation project={project} profile={profile} />)
  })

  const patientSelect = container.querySelector('#session-patient-select') as HTMLSelectElement
  const evaluatorSelect = container.querySelector('#session-evaluator-select') as HTMLSelectElement
  const participantInput = container.querySelector('#session-participant') as HTMLInputElement
  const initialsInput = container.querySelector('#session-initials') as HTMLInputElement
  const visitInput = container.querySelector('#session-visit') as HTMLInputElement

  await act(async () => {
    setInputValue(patientSelect, existingPatient.id)
    setInputValue(evaluatorSelect, existingEvaluator.id)
    setInputValue(visitInput, 'T1')
  })

  expect(participantInput.value).toBe('PAT-0001')
  expect(participantInput.readOnly).toBe(true)
  expect(initialsInput.value).toBe('ACS')

  const reviewButton = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Revisar preparação',
  )!
  await act(async () => {
    reviewButton.click()
  })

  const reviewRegion = container.querySelector('[aria-label="Resumo para conferência"]')!
  expect(reviewRegion).not.toBeNull()
  expect(reviewRegion.textContent).toContain('Ana Carolina Sintetica (PAT-0001)')
  expect(reviewRegion.textContent).toContain('Dra. Beatriz Sintetica (EVA-0001)')
  expect(reviewRegion.textContent).toContain('stroop_go_nogo_ptbr · 0.2.2-web.1')

  const confirmButton = [...reviewRegion.querySelectorAll('button')].find(
    btn => btn.textContent === 'Confirmar e emitir convite',
  )!
  await act(async () => {
    confirmButton.click()
  })

  expect(container.textContent).toContain('SINTETICO_CONVITE_PREP01_1234567890')
  expect(container.textContent).toContain('Participante: PAT-0001 · Visita: T1')
  expect(container.textContent).toContain('Paciente: Ana Carolina Sintetica (PAT-0001)')
  expect(container.textContent).toContain('Avaliador: Dra. Beatriz Sintetica (EVA-0001)')
})

test('cadastra paciente inline com alerta de homonimo e confirmacao consciente', async () => {
  let patientCreateCalls = 0
  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.startsWith('/api/v1/patients') && (!init || init.method === 'GET')) {
      return jsonResponse({ items: [existingPatient], total: 1, page: 1, page_size: 50 })
    }
    if (url.startsWith('/api/v1/evaluators') && (!init || init.method === 'GET')) {
      return jsonResponse({ items: [existingEvaluator], total: 1, page: 1, page_size: 50 })
    }
    if (url === '/api/v1/patients' && init?.method === 'POST') {
      patientCreateCalls += 1
      const body = JSON.parse(String(init.body))
      if (!body.confirm_homonym) {
        return jsonResponse(
          {
            error: {
              code: 'duplicate_candidate_found',
              message: 'Possivel homonimo encontrado.',
            },
            candidates: [existingPatient],
            request_id: 'req-homonym-1',
          },
          409,
        )
      }
      return jsonResponse(
        {
          ...existingPatient,
          id: '00000000-0000-4000-8000-000000000109',
          participant_code: 'PAT-0002',
          disambiguation_note: 'Coorte Noturna',
        },
        201,
      )
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<SessionInvitation project={project} profile={profile} />)
  })

  const toggleNewPatient = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Cadastrar novo paciente',
  )!
  await act(async () => {
    toggleNewPatient.click()
  })

  const nameInput = container.querySelector('#new-patient-full-name') as HTMLInputElement
  const initialsInput = container.querySelector('#new-patient-initials') as HTMLInputElement
  const noteInput = container.querySelector('#new-patient-note') as HTMLInputElement

  await act(async () => {
    setInputValue(nameInput, 'Ana Carolina Sintetica')
    setInputValue(noteInput, 'Coorte Noturna')
  })
  expect(initialsInput.value).toBe('ACS')

  const savePatientButton = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Salvar paciente',
  )!
  await act(async () => {
    savePatientButton.click()
  })

  expect(patientCreateCalls).toBe(1)
  const homonymAlert = container.querySelector('[aria-label="Alerta de homônimo de paciente"]')!
  expect(homonymAlert).not.toBeNull()
  expect(homonymAlert.textContent).toContain('PAT-0001')

  const confirmHomonymBtn = [...homonymAlert.querySelectorAll('button')].find(
    btn => btn.textContent === 'Confirmar homônimo e cadastrar paciente',
  )!
  await act(async () => {
    confirmHomonymBtn.click()
  })

  expect(patientCreateCalls).toBe(2)
  const participantInput = container.querySelector('#session-participant') as HTMLInputElement
  expect(participantInput.value).toBe('PAT-0002')
  expect(participantInput.readOnly).toBe(true)
})
