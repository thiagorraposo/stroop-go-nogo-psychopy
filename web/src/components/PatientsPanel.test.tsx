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
