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

test('cadastra novo avaliador, seleciona automaticamente e exibe resumo compacto', async () => {
  let evaluatorCreateCalls = 0
  const createdEvaluator = {
    ...existingEvaluator,
    id: '00000000-0000-4000-8000-000000000209',
    evaluator_code: 'EVA-0002',
    full_name: 'Dr. Carlos Sintetico',
    initials: 'DCS',
  }

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.startsWith('/api/v1/patients') && (!init || init.method === 'GET')) {
      return jsonResponse({ items: [existingPatient], total: 1, page: 1, page_size: 50 })
    }
    if (url.startsWith('/api/v1/evaluators') && (!init || init.method === 'GET')) {
      return jsonResponse({ items: [existingEvaluator], total: 1, page: 1, page_size: 50 })
    }
    if (url === '/api/v1/evaluators' && init?.method === 'POST') {
      evaluatorCreateCalls += 1
      return jsonResponse(createdEvaluator, 201)
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<SessionInvitation project={project} profile={profile} />)
  })

  const toggleNewEvaluator = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Cadastrar novo avaliador',
  )!
  await act(async () => {
    toggleNewEvaluator.click()
  })

  const nameInput = container.querySelector('#new-evaluator-full-name') as HTMLInputElement
  const initialsInput = container.querySelector('#new-evaluator-initials') as HTMLInputElement

  await act(async () => {
    setInputValue(nameInput, 'Dr. Carlos Sintetico')
  })
  expect(initialsInput.value).toBe('DCS')

  const saveEvaluatorButton = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Salvar avaliador',
  )!
  await act(async () => {
    saveEvaluatorButton.click()
  })

  expect(evaluatorCreateCalls).toBe(1)
  const evaluatorSelect = container.querySelector('#session-evaluator-select') as HTMLSelectElement
  expect(evaluatorSelect.value).toBe(createdEvaluator.id)
  expect(container.textContent).toContain('Dr. Carlos Sintetico')
  expect(container.textContent).toContain('EVA-0002')
})

test('rejeita cadastro inválido de paciente com nome curto', async () => {
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
      return jsonResponse({}, 201)
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
  await act(async () => {
    setInputValue(nameInput, 'A')
  })

  const savePatientButton = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Salvar paciente',
  )!
  await act(async () => {
    savePatientButton.click()
  })

  expect(patientCreateCalls).toBe(0)
  expect(container.textContent).toContain('Informe o nome completo do paciente (2 a 120 caracteres).')
})

test('perfil consulta tem ações proibidas desabilitadas com aviso claro', async () => {
  const consultaProfile = {
    ...profile,
    role: 'consulta' as const,
  }

  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({ items: [existingPatient], total: 1, page: 1, page_size: 50 })
    }
    if (url.startsWith('/api/v1/evaluators')) {
      return jsonResponse({ items: [existingEvaluator], total: 1, page: 1, page_size: 50 })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<SessionInvitation project={project} profile={consultaProfile} />)
  })

  expect(container.textContent).toContain('Modo de Consulta (leitura)')
  const toggleNewPatient = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Cadastrar novo paciente',
  )!
  expect(toggleNewPatient.disabled).toBe(true)

  const toggleNewEvaluator = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Cadastrar novo avaliador',
  )!
  expect(toggleNewEvaluator.disabled).toBe(true)

  const submitButton = [...container.querySelectorAll('button')].find(
    btn => btn.getAttribute('type') === 'submit',
  )!
  expect(submitButton.disabled).toBe(true)
})

test('seleciona modalidade presencial e emite convite com parâmetros válidos', async () => {
  let createdPayload: any = null

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({ items: [existingPatient], total: 1, page: 1, page_size: 50 })
    }
    if (url.startsWith('/api/v1/evaluators')) {
      return jsonResponse({ items: [existingEvaluator], total: 1, page: 1, page_size: 50 })
    }
    if (url.endsWith(`/projects/${project.id}/invitations`) && init?.method === 'POST') {
      createdPayload = JSON.parse(String(init.body))
      return jsonResponse(
        {
          invitation_id: '00000000-0000-4000-8000-000000000301',
          session_id: '00000000-0000-4000-8000-000000000302',
          code: 'SINTETICO_PRESENCIAL_1234567890',
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
            visit: 'V1',
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

  // Seleciona paciente e avaliador
  const patientSelect = container.querySelector('#session-patient-select') as HTMLSelectElement
  const evaluatorSelect = container.querySelector('#session-evaluator-select') as HTMLSelectElement
  const visitInput = container.querySelector('#session-visit') as HTMLInputElement

  await act(async () => {
    setInputValue(patientSelect, existingPatient.id)
    setInputValue(evaluatorSelect, existingEvaluator.id)
    setInputValue(visitInput, 'V1')
  })

  // Seleciona modalidade presencial
  const presencialButton = [...container.querySelectorAll('.mode-card')].find(btn =>
    btn.textContent?.includes('Presencial'),
  ) as HTMLButtonElement
  expect(presencialButton).toBeDefined()
  await act(async () => {
    presencialButton.click()
  })
  expect(presencialButton.classList.contains('active')).toBe(true)

  // Botão primário agora indica Iniciar avaliação
  const submitButton = [...container.querySelectorAll('button')].find(
    btn => btn.getAttribute('type') === 'submit',
  )!
  expect(submitButton.textContent).toBe('Iniciar avaliação')

  // Clica em Revisar preparação
  const reviewButton = [...container.querySelectorAll('button')].find(
    btn => btn.textContent === 'Revisar preparação',
  )!
  await act(async () => {
    reviewButton.click()
  })

  const reviewRegion = container.querySelector('[aria-label="Resumo para conferência"]')!
  expect(reviewRegion.textContent).toContain('Presencial (Iniciar Agora)')

  const confirmBtn = [...reviewRegion.querySelectorAll('button')].find(
    btn => btn.textContent === 'Confirmar e emitir convite',
  )!
  await act(async () => {
    confirmBtn.click()
  })

  expect(createdPayload).toEqual({
    patient_id: existingPatient.id,
    evaluator_id: existingEvaluator.id,
    visit: 'V1',
    test_code: 'stroop_go_nogo_ptbr',
    initials: 'ACS',
  })
  expect(container.textContent).toContain('SINTETICO_PRESENCIAL_1234567890')
})

test('busca paciente e avaliador por texto ou código atualizando resultados e informando quando vazio sem apagar formulário', async () => {
  let searchedPatientTerm = ''
  let searchedEvaluatorTerm = ''

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.startsWith('/api/v1/patients') && (!init || init.method === 'GET')) {
      const parsedUrl = new URL(url, 'http://localhost')
      searchedPatientTerm = parsedUrl.searchParams.get('search') ?? ''
      if (searchedPatientTerm === 'Inexistente') {
        return jsonResponse({ items: [], total: 0, page: 1, page_size: 50 })
      }
      return jsonResponse({ items: [existingPatient], total: 1, page: 1, page_size: 50 })
    }
    if (url.startsWith('/api/v1/evaluators') && (!init || init.method === 'GET')) {
      const parsedUrl = new URL(url, 'http://localhost')
      searchedEvaluatorTerm = parsedUrl.searchParams.get('search') ?? ''
      if (searchedEvaluatorTerm === 'Inexistente') {
        return jsonResponse({ items: [], total: 0, page: 1, page_size: 50 })
      }
      return jsonResponse({ items: [existingEvaluator], total: 1, page: 1, page_size: 50 })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<SessionInvitation project={project} profile={profile} />)
  })

  // Preenche visita previamente
  const visitInput = container.querySelector('#session-visit') as HTMLInputElement
  await act(async () => {
    setInputValue(visitInput, 'V_PRESERVADA')
  })
  expect(visitInput.value).toBe('V_PRESERVADA')

  // Busca paciente por código PAT-0001
  const patientSearchInput = container.querySelector('#session-patient-search') as HTMLInputElement
  await act(async () => {
    setInputValue(patientSearchInput, 'PAT-0001')
  })
  expect(searchedPatientTerm).toBe('PAT-0001')

  // Visita não foi apagada
  expect(visitInput.value).toBe('V_PRESERVADA')

  // Busca termo inexistente e verifica feedback amigável
  await act(async () => {
    setInputValue(patientSearchInput, 'Inexistente')
  })
  expect(searchedPatientTerm).toBe('Inexistente')
  expect(container.textContent).toContain('Nenhum paciente cadastrado encontrado para "Inexistente"')

  // Visita permanece intacta
  expect(visitInput.value).toBe('V_PRESERVADA')

  // Busca avaliador por código EVA-0001
  const evaluatorSearchInput = container.querySelector('#session-evaluator-search') as HTMLInputElement
  await act(async () => {
    setInputValue(evaluatorSearchInput, 'EVA-0001')
  })
  expect(searchedEvaluatorTerm).toBe('EVA-0001')

  // Busca avaliador inexistente
  await act(async () => {
    setInputValue(evaluatorSearchInput, 'Inexistente')
  })
  expect(searchedEvaluatorTerm).toBe('Inexistente')
  expect(container.textContent).toContain('Nenhum avaliador encontrado para "Inexistente"')
})
