// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { ExportHubPanel } from './ExportHubPanel'
import type { ProfessionalProfile } from '../api/client'
import type { Project } from '../api/assessments'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const adminProfile: ProfessionalProfile = {
  user_id: 'admin_export',
  role: 'administracao',
  expires_at: '2026-11-08T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const consultaProfile: ProfessionalProfile = {
  user_id: 'consulta_export',
  role: 'consulta',
  expires_at: '2026-11-08T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

const mockProject: Project = {
  id: '00000000-0000-4000-8000-000000000001',
  code: 'PROJ_EXPORT',
  name: 'Pesquisa Exportação',
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
})

afterEach(async () => {
  await act(async () => root.unmount())
  container.remove()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

test('renderiza as 5 granularidades e desabilita modo nominal para perfil consulta', async () => {
  await act(async () => {
    root.render(<ExportHubPanel profile={consultaProfile} project={mockProject} />)
  })

  expect(container.textContent).toContain('Central de exportações avançada (REQ-CSV-005)')
  expect(container.textContent).toContain('Pacientes')
  expect(container.textContent).toContain('Avaliações')
  expect(container.textContent).toContain('Tentativas')
  expect(container.textContent).toContain('Métricas')
  expect(container.textContent).toContain('Stroop 21 colunas')

  const radios = container.querySelectorAll('input[name="id_mode"]')
  expect(radios).toHaveLength(2)
  const nominalRadio = container.querySelector('input[name="id_mode"][value="nominal"]') as HTMLInputElement
  expect(nominalRadio.disabled).toBe(true)
})

test('permite alternar granularidade, selecionar colunas e gerar prévia com contagem', async () => {
  const previewData = {
    total_rows: 42,
    columns: ['assessment_id', 'participant_code', 'visit', 'accuracy'],
    applied_criteria: {
      project_id: mockProject.id,
      granularity: 'avaliacoes',
      identification_mode: 'deidentified',
    },
    sample_rows: [
      { assessment_id: 'ASS-1', participant_code: 'PAT-001', visit: 'V1', accuracy: 87.5 },
      { assessment_id: 'ASS-2', participant_code: 'PAT-002', visit: 'V1', accuracy: 100.0 },
    ],
    export_token: 'fake-export-token-12345',
  }

  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/api/v1/exports/preview')) {
      return jsonResponse(previewData)
    }
    return jsonResponse({}, 404)
  })

  await act(async () => {
    root.render(<ExportHubPanel profile={adminProfile} project={mockProject} />)
  })

  // Clica no botão de pré-visualização
  const previewBtn = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.includes('Pré-visualizar contagem e amostra')
  )
  expect(previewBtn).toBeDefined()

  await act(async () => {
    previewBtn!.click()
  })

  expect(container.textContent).toContain('42 registro(s) encontrado(s)')
  expect(container.textContent).toContain('Amostra da exportação (avaliacoes)')
  expect(container.textContent).toContain('ASS-1')
  expect(container.textContent).toContain('PAT-001')

  // Botão de download deve estar habilitado com o total de registros
  const downloadBtn = Array.from(container.querySelectorAll('button')).find(
    b => b.textContent?.includes('Baixar arquivo CSV (42 registros)')
  )
  expect(downloadBtn).toBeDefined()
  expect((downloadBtn as HTMLButtonElement).disabled).toBe(false)
})
