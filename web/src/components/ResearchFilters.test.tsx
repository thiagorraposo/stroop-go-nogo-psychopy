// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { ResearchFilters } from './ResearchFilters'
import type { ResearchQuery } from './ResearchFilters'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const mockProjects = [
  {
    id: '00000000-0000-4000-8000-000000000001',
    code: 'PROJ_01',
    name: 'Projeto de Teste 1',
    active: true,
    created_at: '2026-10-16T12:00:00Z',
  },
]

let container: HTMLDivElement
let root: ReturnType<typeof createRoot>
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>

beforeEach(() => {
  container = document.createElement('div')
  document.body.append(container)
  root = createRoot(container)
  fetchMock = vi.fn<typeof fetch>()
  vi.stubGlobal('fetch', fetchMock)

  fetchMock.mockImplementation(async () =>
    new Response(
      JSON.stringify({
        participant_id: ['P_001', 'P_002'],
        visit: ['V1', 'V2'],
        evaluator_id: ['EVA-000001'],
        test_version: ['0.2.2-web.1'],
        platform: ['web'],
        test_code: ['stroop_go_nogo_ptbr'],
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    ),
  )
})

afterEach(async () => {
  await act(async () => root.unmount())
  container.remove()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

test('REQ-REL-004: renderiza catalogo completo de filtros combinados e emite query com campos avancados', async () => {
  let appliedQuery: ResearchQuery | null = null

  await act(async () => {
    root.render(
      <ResearchFilters
        projects={mockProjects}
        initialProject={mockProjects[0]!.id}
        loading={false}
        onApply={query => {
          appliedQuery = query
        }}
      />,
    )
  })

  // Confere existência dos campos avançados
  const searchInput = container.querySelector('input[placeholder="Ex: PAT-, V1, EVA-..."]') as HTMLInputElement
  expect(searchInput).not.toBeNull()

  const labels = Array.from(container.querySelectorAll('label')).map(l => l.textContent ?? '')
  expect(labels.some(l => l.includes('Status da avaliação'))).toBe(true)
  expect(labels.some(l => l.includes('Faixa de precisão'))).toBe(true)
  expect(labels.some(l => l.includes('Faixa de tempo de reação (RT)'))).toBe(true)
  expect(labels.some(l => l.includes('Tipo de resposta / erro'))).toBe(true)
  expect(labels.some(l => l.includes('Condição experimental'))).toBe(true)
  expect(labels.some(l => l.includes('Critério de ordenação'))).toBe(true)
  expect(labels.some(l => l.includes('Tratamento explícito de RT ausente'))).toBe(true)

  // Preenche busca textual
  await act(async () => {
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set
    nativeSetter?.call(searchInput, 'PAT-2026')
    searchInput.dispatchEvent(new Event('input', { bubbles: true }))
    searchInput.dispatchEvent(new Event('change', { bubbles: true }))
  })

  // Submete formulário de filtros
  const form = container.querySelector('form')!
  await act(async () => {
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  })

  expect(appliedQuery).not.toBeNull()
  expect(appliedQuery!.projects).toEqual([mockProjects[0]!.id])
  expect(appliedQuery!.advanced).toBeDefined()
  expect(appliedQuery!.advanced?.searchText).toBe('PAT-2026')
  expect(appliedQuery!.advanced?.status).toBe('valid')
  expect(appliedQuery!.advanced?.includeNullRt).toBe(true)
  expect(appliedQuery!.advanced?.sortBy).toBe('date')
  expect(appliedQuery!.advanced?.sortOrder).toBe('desc')
})

test('QUERY7: limpar edita rascunho e exige aplicar para publicar defaults', async () => {
  let appliedQuery: ResearchQuery | null = null

  await act(async () => {
    root.render(
      <ResearchFilters
        projects={mockProjects}
        initialProject={mockProjects[0]!.id}
        loading={false}
        onApply={query => {
          appliedQuery = query
        }}
      />,
    )
  })

  const clearBtn = Array.from(container.querySelectorAll('button')).find(b => b.textContent?.includes('Limpar filtros'))
  expect(clearBtn).toBeDefined()

  await act(async () => {
    clearBtn!.click()
  })

  expect(appliedQuery).toBeNull()
  await act(async () => {
    container.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  })
  expect(appliedQuery).not.toBeNull()
  expect(appliedQuery!.projects).toEqual([mockProjects[0]!.id])
  expect(appliedQuery!.filters).toEqual({})
})

function button(name: string) {
  return [...container.querySelectorAll('button')].find(b => b.textContent?.trim() === name)!
}
async function fill(input: HTMLInputElement, value: string) {
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, value)
    input.dispatchEvent(new Event('input', { bubbles: true }))
  })
}

test('QUERY7: editar, remover chip e limpar não aplicam; descartar restaura o recorte aplicado', async () => {
  const applied = vi.fn()
  await act(async () => root.render(<ResearchFilters projects={mockProjects} initialProject={mockProjects[0]!.id} loading={false} onApply={applied} />))
  const input = container.querySelector('input[placeholder]') as HTMLInputElement
  await fill(input, 'PAT-2026')
  expect(container.textContent).toContain('Alterações não aplicadas')
  expect(applied).not.toHaveBeenCalled()
  await act(async () => button('Aplicar filtros').click())
  expect(applied).toHaveBeenCalledTimes(1)
  expect(container.textContent).not.toContain('Alterações não aplicadas')
  await act(async () => container.querySelector<HTMLButtonElement>('[aria-label^="Remover filtro Busca"]')!.click())
  expect(input.value).toBe('')
  expect(applied).toHaveBeenCalledTimes(1)
  await act(async () => button('Descartar alterações').click())
  expect(input.value).toBe('PAT-2026')
  await act(async () => button('Limpar filtros').click())
  expect(container.textContent).toContain('Alterações não aplicadas')
  expect(applied).toHaveBeenCalledTimes(1)
  await act(async () => button('Aplicar filtros').click())
  expect(applied).toHaveBeenCalledTimes(2)
  expect(applied.mock.lastCall?.[0].advanced.searchText).toBe('')
})
