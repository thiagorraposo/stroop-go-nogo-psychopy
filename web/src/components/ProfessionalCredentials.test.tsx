// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { getProfessionalProfile, loginProfessional, request } from '../api/client'
import { ProfessionalLogin, ProfessionalPassword } from './ProfessionalCredentials'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
const profile = { user_id: 'c3ludGhldGlj', role: 'administracao' as const,
  expires_at: '2026-11-06T18:02:01Z', csrf_token: 'a'.repeat(43) }
const secret = '  Frase sintética 🌱 com espaços  '
let container: HTMLDivElement
let root: ReturnType<typeof createRoot>
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>
beforeEach(() => {
  container = document.createElement('div'); document.body.append(container); root = createRoot(container)
  fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock)
})
afterEach(async () => { await act(async () => root.unmount()); container.remove(); vi.unstubAllGlobals(); vi.restoreAllMocks() })
function response(body: unknown, status = 200) { return new Response(JSON.stringify(body), { status }) }
function input(name: string): HTMLInputElement { return container.querySelector(`[name="${name}"]`)! }
async function submit() { await act(async () => { container.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })) }) }

test('login acessivel envia senha integra em JSON, limpa imediatamente e abre perfil validado', async () => {
  const authenticated = vi.fn()
  let resolve!: (value: Response) => void
  fetchMock.mockImplementation(() => new Promise<Response>(done => { resolve = done }))
  await act(async () => root.render(<ProfessionalLogin onAuthenticated={authenticated} />))
  expect(document.activeElement).toBe(input('username'))
  expect(input('username').autocomplete).toBe('username')
  expect(input('password').autocomplete).toBe('current-password')
  expect(input('password').type).toBe('password')
  input('username').value = ' Synthetic '; input('password').value = secret
  await submit()
  expect(input('password').value).toBe('')
  expect(container.querySelector('button')?.disabled).toBe(true)
  expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/auth/login')
  expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({ method: 'POST', credentials: 'same-origin', cache: 'no-store', body: JSON.stringify({ username: ' Synthetic ', password: secret }) })
  expect(authenticated).not.toHaveBeenCalled()
  await act(async () => resolve(response(profile)))
  expect(authenticated).toHaveBeenCalledWith(profile)
  expect(container.innerHTML).not.toContain(secret)
})

test('falha de login usa erro generico e nao ecoa resposta nem conserva senha', async () => {
  fetchMock.mockResolvedValue(response({ error: { code: 'authentication_required', message: secret } }, 401))
  const authenticated = vi.fn()
  await act(async () => root.render(<ProfessionalLogin onAuthenticated={authenticated} />))
  input('username').value = 'synthetic'; input('password').value = secret
  await submit()
  expect(container.querySelector('[role="alert"]')?.textContent).toBe('Usuário ou senha inválidos.')
  expect(input('password').value).toBe('')
  expect(document.activeElement).toBe(input('password'))
  expect(authenticated).not.toHaveBeenCalled()
})

test('saida limpa senha e cancela requisicao pendente sem autenticar depois', async () => {
  let resolve!: (value: Response) => void
  fetchMock.mockImplementation(() => new Promise<Response>(done => { resolve = done }))
  const authenticated = vi.fn()
  await act(async () => root.render(<ProfessionalLogin onAuthenticated={authenticated} />))
  input('username').value = 'synthetic'; input('password').value = secret
  await submit()
  const signal = fetchMock.mock.calls[0]?.[1]?.signal
  await act(async () => root.render(<p>Outra página</p>))
  expect(signal?.aborted).toBe(true)
  await act(async () => resolve(response(profile)))
  expect(authenticated).not.toHaveBeenCalled()
})

test('troca de senha limpa os tres campos e encerra sessao somente apos 204', async () => {
  const ended = vi.fn()
  let resolve!: (value: Response) => void
  fetchMock.mockImplementation(() => new Promise<Response>(done => { resolve = done }))
  await act(async () => root.render(<ProfessionalPassword profile={profile} onEnded={ended} />))
  input('current-password').value = secret; input('new-password').value = `${secret}!`; input('confirm-password').value = `${secret}!`
  await submit()
  expect([...container.querySelectorAll('input')].every(node => node.value === '')).toBe(true)
  expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/auth/password')
  expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({ body: JSON.stringify({ current_password: secret, new_password: `${secret}!` }), headers: { 'X-CSRF-Token': profile.csrf_token } })
  expect(ended).not.toHaveBeenCalled()
  await act(async () => resolve(new Response(null, { status: 204 })))
  expect(ended).toHaveBeenCalledOnce()
})

test('confirmacao divergente limpa campos sem enviar e permite corrigir', async () => {
  await act(async () => root.render(<ProfessionalPassword profile={profile} onEnded={vi.fn()} />))
  input('current-password').value = secret; input('new-password').value = secret; input('confirm-password').value = 'Outra frase sintética'
  await submit()
  expect(fetchMock).not.toHaveBeenCalled()
  expect(container.querySelector('[role="alert"]')?.textContent).toContain('não corresponde')
  expect([...container.querySelectorAll('input')].every(node => node.value === '')).toBe(true)
})

test('pagehide apaga entradas de senha antes de restauracao do navegador', async () => {
  await act(async () => root.render(<ProfessionalLogin onAuthenticated={vi.fn()} />))
  input('password').value = secret
  await act(async () => window.dispatchEvent(new Event('pagehide')))
  expect(input('password').value).toBe('')
})

test('401 profissional sinaliza limpeza da area; login e participante nao encerram outro fluxo', async () => {
  const ended = vi.fn()
  window.addEventListener('stroop-professional-session-ended', ended)
  try {
    fetchMock.mockImplementation(async () => response({ error: { code: 'authentication_required' } }, 401))
    await expect(getProfessionalProfile()).rejects.toMatchObject({ status: 401 })
    expect(ended).toHaveBeenCalledTimes(1)
    await expect(loginProfessional('synthetic', secret)).rejects.toMatchObject({ status: 401 })
    await expect(request('/api/v1/participant/session', { method: 'GET' }, async () => undefined)).rejects.toMatchObject({ status: 401 })
    expect(ended).toHaveBeenCalledTimes(1)
  } finally { window.removeEventListener('stroop-professional-session-ended', ended) }
})
