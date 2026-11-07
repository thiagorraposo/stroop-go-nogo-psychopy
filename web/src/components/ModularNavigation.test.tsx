// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { ProfessionalDashboard } from './ProfessionalDashboard'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const adminProfile = {
  user_id: 'admin_sintetico',
  role: 'administracao' as const,
  expires_at: '2026-11-07T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const consultaProfile = {
  user_id: 'leitor_sintetico',
  role: 'consulta' as const,
  expires_at: '2026-11-07T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const mockProject = {
  id: '00000000-0000-4000-8000-000000000001',
  code: 'PROJ_MODULAR',
  name: 'Pesquisa Modular',
  active: true,
  created_at: '2026-11-01T10:00:00Z',
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

beforeEach(() => {
  container = document.createElement('div')
  document.body.append(container)
  root = createRoot(container)
  fetchMock = vi.fn<typeof fetch>()
  vi.stubGlobal('fetch', fetchMock)

  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/api/v1/projects') && !url.includes('/assessments')) {
      return jsonResponse({ items: [mockProject], next_cursor: null })
    }
    if (url.includes('/assessments/options')) {
      return jsonResponse({
        participant_id: [],
        visit: [],
        evaluator_id: [],
        test_version: [],
        platform: ['web'],
        test_code: ['stroop_go_nogo_ptbr'],
      })
    }
    if (url.includes('/assessments')) {
      return jsonResponse({ items: [], next_cursor: null })
    }
    if (url.includes('/api/v1/patients')) {
      return jsonResponse({ items: [], total: 0, page: 1, page_size: 20 })
    }
    if (url.includes('/api/v1/evaluators')) {
      return jsonResponse({ items: [], total: 0, page: 1, page_size: 20 })
    }
    if (url.includes('/api/v1/administration/users')) {
      return jsonResponse({ items: [], next_cursor: null })
    }
    return jsonResponse({}, 404)
  })
})

afterEach(async () => {
  await act(async () => root.unmount())
  container.remove()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

test('exibe os 8 botões modulares para perfil administração e permite navegar entre todos eles', async () => {
  await act(async () => {
    root.render(<ProfessionalDashboard profile={adminProfile} />)
  })

  const nav = container.querySelector('nav[aria-label="Módulos administrativos"]')
  expect(nav).not.toBeNull()

  const buttons = Array.from(nav!.querySelectorAll('button')).map(b => b.textContent?.trim())
  expect(buttons).toEqual([
    'Visão geral (Dashboard)',
    'Pacientes',
    'Avaliadores',
    'Preparar avaliação',
    'Avaliações e histórico',
    'Resultados e análises',
    'Exportações',
    'Administração',
  ])

  // 1. Módulo inicial é Visão geral (Dashboard)
  expect(container.textContent).toContain('Resultados da pesquisa')

  // 2. Navega para Pacientes
  const pacientesButton = nav!.querySelectorAll('button')[1]!
  await act(async () => {
    pacientesButton.click()
  })
  expect(container.textContent).toContain('Cadastro centralizado de participantes/pacientes')
  expect(pacientesButton.getAttribute('aria-pressed')).toBe('true')

  // 3. Navega para Avaliadores
  const avaliadoresButton = nav!.querySelectorAll('button')[2]!
  await act(async () => {
    avaliadoresButton.click()
  })
  expect(container.textContent).toContain('Cadastro centralizado de avaliadores responsáveis')
  expect(avaliadoresButton.getAttribute('aria-pressed')).toBe('true')

  // 4. Navega para Preparar avaliação
  const prepararButton = nav!.querySelectorAll('button')[3]!
  await act(async () => {
    prepararButton.click()
  })
  expect(container.textContent).toContain('Emissão de convites de uso único para aplicação da Tarefa de Correspondência de Cores')
  expect(prepararButton.getAttribute('aria-pressed')).toBe('true')

  // 5. Navega para Avaliações e histórico
  const historicoButton = nav!.querySelectorAll('button')[4]!
  await act(async () => {
    historicoButton.click()
  })
  expect(container.textContent).toContain('Acompanhamento operacional de sessões')
  expect(historicoButton.getAttribute('aria-pressed')).toBe('true')

  // 6. Navega para Resultados e análises
  const resultadosButton = nav!.querySelectorAll('button')[5]!
  await act(async () => {
    resultadosButton.click()
  })
  expect(container.textContent).toContain('Visualizações descritivas e análises de pesquisa')
  expect(resultadosButton.getAttribute('aria-pressed')).toBe('true')

  // 7. Navega para Exportações
  const exportacoesButton = nav!.querySelectorAll('button')[6]!
  await act(async () => {
    exportacoesButton.click()
  })
  expect(container.textContent).toContain('Central de exportações')
  expect(container.textContent).toContain('Granularidades e políticas de exportação (REQ-CSV-005)')
  expect(exportacoesButton.getAttribute('aria-pressed')).toBe('true')

  // 8. Navega para Administração
  const adminButton = nav!.querySelectorAll('button')[7]!
  await act(async () => {
    adminButton.click()
  })
  expect(container.textContent).toContain('Contas e permissões')
  expect(adminButton.getAttribute('aria-pressed')).toBe('true')
})

test('perfil consulta não exibe botão de Administração', async () => {
  await act(async () => {
    root.render(<ProfessionalDashboard profile={consultaProfile} />)
  })

  const nav = container.querySelector('nav[aria-label="Módulos administrativos"]')
  expect(nav).not.toBeNull()

  const buttons = Array.from(nav!.querySelectorAll('button')).map(b => b.textContent?.trim())
  expect(buttons).not.toContain('Administração')
  expect(buttons).toHaveLength(7)
})
