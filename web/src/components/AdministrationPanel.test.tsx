// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AdministrationPanel } from './AdministrationPanel'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })

const adminProfile = {
  user_id: 'admin_local_sintetico',
  role: 'administracao' as const,
  expires_at: '2026-11-08T22:00:00Z',
  csrf_token: 'c'.repeat(43),
}

let container: HTMLDivElement
let root: ReturnType<typeof createRoot>
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>

beforeEach(() => {
  container = document.createElement('div')
  document.body.append(container)
  root = createRoot(container)
  fetchMock = vi.fn<typeof fetch>()
  vi.stubGlobal('fetch', fetchMock)

  fetchMock.mockImplementation(async input => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/api/v1/projects') && !url.includes('/members')) {
      return new Response(
        JSON.stringify({
          items: [{ id: '00000000-0000-4000-8000-000000000001', code: 'PROJ_ADMIN', name: 'Projeto Admin', active: true, created_at: '2026-10-16T12:00:00Z' }],
          next_cursor: null,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      )
    }
    if (url.includes('/members')) {
      return new Response(JSON.stringify({ items: [], next_cursor: null }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    }
    if (url.includes('/api/v1/admin/users')) {
      return new Response(
        JSON.stringify({
          items: [
            { user_id: 'admin_local_sintetico', role: 'administracao', active: true },
            { user_id: 'leitor_sintetico', role: 'consulta', active: true },
          ],
          next_cursor: null,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      )
    }
    return new Response(JSON.stringify({}), { status: 404, headers: { 'Content-Type': 'application/json' } })
  })
})

afterEach(async () => {
  await act(async () => root.unmount())
  container.remove()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

test('WEB-018: renderiza painel com aviso arquitetural ADR-006 / ADR-007 distinguindo conta local de cadastro de avaliadores', async () => {
  let navigatedToEvaluators = false

  await act(async () => {
    root.render(
      <AdministrationPanel
        profile={adminProfile}
        onNavigateToEvaluators={() => {
          navigatedToEvaluators = true
        }}
      />,
    )
  })

  // Confere existência do banner de distinção arquitetural
  const noticeCard = container.querySelector('[aria-label="Aviso de distinção arquitetural"]')
  expect(noticeCard).not.toBeNull()
  expect(noticeCard!.textContent).toContain('Distinção arquitetural importante (ADR-006 / ADR-007)')
  expect(noticeCard!.textContent).toContain('conta técnica local compartilhada')
  expect(noticeCard!.textContent).toContain('cadastro central de avaliadores responsáveis')

  // Testa botão de navegação para módulo de avaliadores
  const navBtn = noticeCard!.querySelector('button')
  expect(navBtn).not.toBeNull()
  expect(navBtn!.textContent).toBe('Ir para Avaliadores')

  await act(async () => {
    navBtn!.click()
  })
  expect(navigatedToEvaluators).toBe(true)

  // Confere tabela de contas cadastradas
  const table = container.querySelector('table')
  expect(table).not.toBeNull()
  expect(table!.textContent).toContain('admin_local_sintetico')
  expect(table!.textContent).toContain('leitor_sintetico')
})
