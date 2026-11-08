// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { PatientsPanel } from './PatientsPanel'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const profileAdmin = {
  user_id: 'admin_sintetico',
  role: 'administracao' as const,
  expires_at: '2026-11-07T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const mockPatient1 = {
  id: '00000000-0000-4000-8000-000000000001',
  participant_code: 'PAT-0001',
  full_name: 'Ana Carolina Sintetica',
  normalized_name: 'ANA CAROLINA SINTETICA',
  initials: 'ACS',
  disambiguation_note: 'Grupo Controle',
  active: true,
  created_at: '2026-11-01T10:00:00Z',
  updated_at: '2026-11-01T10:00:00Z',
  project_count: 1,
  assessment_count: 2,
  last_assessment_at: '2026-11-05T14:30:00Z',
}

const mockPatientDetail = {
  ...mockPatient1,
  projects: [
    {
      project_id: '11111111-1111-4111-8111-111111111111',
      project_code: 'PROJ_DEMO',
      project_name: 'Projeto Demonstracao',
      participant_code: 'P01',
      created_at: '2026-11-01T10:00:00Z',
    },
  ],
  visits: [
    {
      visit_uuid: '22222222-2222-4222-8222-222222222222',
      project_id: '11111111-1111-4111-8111-111111111111',
      project_code: 'PROJ_DEMO',
      visit: 'V1',
      created_at: '2026-11-02T10:00:00Z',
    },
  ],
  assessments: [
    {
      assessment_id: '33333333-3333-4333-8333-333333333333',
      project_id: '11111111-1111-4111-8111-111111111111',
      project_code: 'PROJ_DEMO',
      test_code: 'stroop_go_nogo_ptbr',
      test_version: '1.0.0',
      visit: 'V1',
      created_at: '2026-11-05T14:30:00Z',
    },
  ],
  sessions: [
    {
      invitation_id: '55555555-5555-5555-8555-555555555555',
      session_id: '66666666-6666-6666-8666-666666666666',
      project_id: '11111111-1111-4111-8111-111111111111',
      project_code: 'PROJ_DEMO',
      visit: 'V1',
      evaluator_code: 'EVA-0001',
      test_code: 'stroop_go_nogo_ptbr',
      test_version: '1.0.0',
      invitation_state: 'completed',
      session_state: 'completed',
      created_at: '2026-11-05T14:00:00Z',
    },
  ],
  audit_history: [
    {
      event_id: '77777777-7777-7777-8777-777777777777',
      entity_type: 'patient',
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

test('renderiza listagem de pacientes com código PAT-... e abre ficha detalhada', async () => {
  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/api/v1/patients/00000000-0000-4000-8000-000000000001')) {
      return jsonResponse(mockPatientDetail)
    }
    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({
        items: [mockPatient1],
        total: 1,
        page: 1,
        page_size: 20,
      })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<PatientsPanel profile={profileAdmin} />)
  })

  // Confere que a tabela listou o paciente
  expect(container.textContent).toContain('PAT-0001')
  expect(container.textContent).toContain('Ana Carolina Sintetica')
  expect(container.textContent).toContain('Grupo Controle')

  // Clica para ver a ficha detalhada
  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  expect(viewButton).not.toBeNull()

  await act(async () => {
    viewButton.click()
  })

  // Confere que a ficha foi carregada e exibida com projetos e histórico
  expect(container.textContent).toContain('Ficha cadastral do paciente')
  expect(container.textContent).toContain('Projeto Demonstracao')
  expect(container.textContent).toContain('stroop_go_nogo_ptbr')
})

test('cria novo paciente com verificação de homônimo e confirmação consciente', async () => {
  let created = false
  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    const method = init?.method ?? 'GET'

    if (url.includes('/api/v1/patients/duplicates')) {
      return jsonResponse({
        normalized_name: 'ANA CAROLINA SINTETICA',
        candidates: [
          {
            id: mockPatient1.id,
            participant_code: mockPatient1.participant_code,
            full_name: mockPatient1.full_name,
            initials: mockPatient1.initials,
            disambiguation_note: mockPatient1.disambiguation_note,
            active: mockPatient1.active,
            created_at: mockPatient1.created_at,
          },
        ],
      })
    }

    if (url.startsWith('/api/v1/patients') && method === 'POST') {
      created = true
      return jsonResponse(
        {
          id: '00000000-0000-4000-8000-000000000002',
          participant_code: 'PAT-0002',
          full_name: 'Ana Carolina Sintetica',
          initials: 'ACS',
          disambiguation_note: 'Homônimo confirmado',
          active: true,
          created_at: '2026-11-07T12:00:00Z',
          updated_at: '2026-11-07T12:00:00Z',
          project_count: 0,
          assessment_count: 0,
          last_assessment_at: null,
        },
        201,
      )
    }

    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({
        items: created ? [mockPatient1, { ...mockPatient1, id: '2', participant_code: 'PAT-0002' }] : [mockPatient1],
        total: created ? 2 : 1,
        page: 1,
        page_size: 20,
      })
    }

    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<PatientsPanel profile={profileAdmin} />)
  })

  // Abre formulário de cadastro
  const openCreateButton = container.querySelector('button.primary') as HTMLButtonElement
  await act(async () => {
    openCreateButton.click()
  })

  expect(container.textContent).toContain('Novo cadastro de paciente')

  const nameInput = container.querySelector('#patient-fullname') as HTMLInputElement
  await act(async () => {
    setInputValue(nameInput, 'Ana Carolina Sintetica')
  })
  await act(async () => {
    nameInput.focus()
    nameInput.blur()
    nameInput.dispatchEvent(new FocusEvent('blur', { bubbles: true }))
    await new Promise(r => setTimeout(r, 50))
  })

  // Confere alerta de homônimo
  expect(container.textContent).toContain('foram encontrados pacientes com nome semelhante')

  // Marca checkbox de confirmação
  const homonymCheckbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement
  expect(homonymCheckbox).not.toBeNull()
  await act(async () => {
    homonymCheckbox.click()
  })

  // Submete
  const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
  await act(async () => {
    submitButton.click()
  })

  expect(created).toBe(true)
  expect(container.textContent).toContain('Paciente cadastrado com sucesso! Código gerado: PAT-0002')
})

test('exibe sessões vinculadas e trilha de auditoria cadastral na ficha detalhada', async () => {
  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/api/v1/patients/00000000-0000-4000-8000-000000000001')) {
      return jsonResponse(mockPatientDetail)
    }
    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({
        items: [mockPatient1],
        total: 1,
        page: 1,
        page_size: 20,
      })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<PatientsPanel profile={profileAdmin} />)
  })

  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  await act(async () => {
    viewButton.click()
  })

  // Confere sessões e convites preparados
  expect(container.textContent).toContain('Sessões e convites preparados')
  expect(container.textContent).toContain('EVA-0001')

  // Confere trilha de auditoria cadastral
  expect(container.textContent).toContain('Trilha de auditoria cadastral')
  expect(container.textContent).toContain('cadastro_inicial')
})

test('edita dados cadastrais do paciente com motivo obrigatório e atualiza ficha', async () => {
  let patchPayload: unknown = null
  let currentDetail = { ...mockPatientDetail }

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    const method = init?.method ?? 'GET'

    if (url.includes('/api/v1/patients/00000000-0000-4000-8000-000000000001') && method === 'PATCH') {
      patchPayload = JSON.parse(init?.body as string)
      currentDetail = {
        ...currentDetail,
        full_name: 'Ana Carolina Sintetica Retificada',
        initials: 'ACSR',
        disambiguation_note: 'Grupo Retificado',
      }
      return jsonResponse(currentDetail)
    }

    if (url.includes('/api/v1/patients/00000000-0000-4000-8000-000000000001')) {
      return jsonResponse(currentDetail)
    }

    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({
        items: [mockPatient1],
        total: 1,
        page: 1,
        page_size: 20,
      })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<PatientsPanel profile={profileAdmin} />)
  })

  const viewButton = container.querySelector('button[aria-label^="Ver ficha"]') as HTMLButtonElement
  await act(async () => {
    viewButton.click()
  })

  // Clica em Editar cadastro
  const editButton = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.trim() === 'Editar cadastro',
  )
  expect(editButton).not.toBeUndefined()
  await act(async () => {
    editButton!.click()
  })

  expect(container.textContent).toContain('Editar dados cadastrais do paciente')

  // Altera campos
  const nameInput = container.querySelector('#edit-patient-fullname') as HTMLInputElement
  const initialsInput = container.querySelector('#edit-patient-initials') as HTMLInputElement
  const reasonInput = container.querySelector('#edit-patient-reason') as HTMLInputElement

  await act(async () => {
    setInputValue(nameInput, 'Ana Carolina Sintetica Retificada')
    setInputValue(initialsInput, 'ACSR')
    setInputValue(reasonInput, 'correcao_ortografica_homologada')
  })

  const saveButton = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.trim() === 'Salvar alterações',
  )
  expect(saveButton).not.toBeUndefined()
  await act(async () => {
    saveButton!.click()
  })

  expect(patchPayload).toEqual({
    full_name: 'Ana Carolina Sintetica Retificada',
    initials: 'ACSR',
    disambiguation_note: 'Grupo Controle',
    reason_code: 'correcao_ortografica_homologada',
  })
  expect(container.textContent).toContain('atualizado com sucesso (evento auditado)')
})

test('executa procedimento administrativo auditado para correção de vínculo da avaliação', async () => {
  let relinkCalled = false
  let relinkPayload: unknown = null

  fetchMock.mockImplementation(async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    const method = init?.method ?? 'GET'

    if (url.includes('/relink') && method === 'POST') {
      relinkCalled = true
      relinkPayload = JSON.parse(init?.body as string)
      return jsonResponse({
        assessment_id: '33333333-3333-4333-8333-333333333333',
        project_id: '11111111-1111-4111-8111-111111111111',
        patient_id: '00000000-0000-4000-8000-000000000001',
        evaluator_id: '00000000-0000-4000-8000-000000000101',
        relinked: true,
      })
    }

    if (url.includes('/api/v1/patients/00000000-0000-4000-8000-000000000001')) {
      return jsonResponse(mockPatientDetail)
    }

    if (url.startsWith('/api/v1/patients')) {
      return jsonResponse({
        items: [mockPatient1],
        total: 1,
        page: 1,
        page_size: 20,
      })
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<PatientsPanel profile={profileAdmin} />)
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

  const evaluatorInput = container.querySelector('#relink-new-evaluator') as HTMLInputElement
  const reasonInput = container.querySelector('#relink-reason') as HTMLInputElement

  await act(async () => {
    setInputValue(evaluatorInput, '00000000-0000-4000-8000-000000000101')
    setInputValue(reasonInput, 'correcao_erro_humano_avaliador')
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
    evaluator_id: '00000000-0000-4000-8000-000000000101',
    reason_code: 'correcao_erro_humano_avaliador',
  })
  expect(container.textContent).toContain('corrigido com sucesso (evento auditado)')
})
