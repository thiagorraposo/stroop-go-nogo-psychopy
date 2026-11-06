/** React/build + API + PG reais em HTTPS; credenciais exclusivamente sinteticas. */
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { expect, request, test } from '@playwright/test'
import type { Page } from '@playwright/test'

const origin = 'https://127.0.0.1:4473'
const username = 'synthetic-local-https'
const password = 'Frase sintética HTTPS local 2026 🌱'
const otherPassword = 'Outra frase sintética HTTPS 2026 🌻'
const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const management = fileURLToPath(new URL('./manage.py', import.meta.url))
const cookieName = '__Host-stroop_professional'
type Profile = { user_id: string; role: string; csrf_token: string; expires_at: string }

function manage(action: string): Record<string, number | boolean> {
  return JSON.parse(execFileSync(python, [management, action], { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }))
}
async function login(page: Page): Promise<Profile> {
  await page.goto('/equipe')
  await expect(page.getByLabel('Usuário', { exact: true })).toBeVisible()
  await page.getByLabel('Usuário', { exact: true }).fill(username)
  await page.getByLabel('Senha', { exact: true }).fill(password)
  const response = page.waitForResponse(value => value.url() === `${origin}/api/v1/auth/login` && value.request().method() === 'POST')
  await page.getByRole('button', { name: 'Entrar', exact: true }).click()
  const value = await response
  expect(value.status()).toBe(200)
  const profile = await value.json() as Profile
  await expect(page.getByRole('heading', { name: 'Resultados da pesquisa' })).toBeVisible()
  return profile
}
async function replay(page: Page) {
  const cookie = (await page.context().cookies()).find(value => value.name === cookieName)
  if (!cookie) throw new Error('Cookie sintetico profissional ausente.')
  return request.newContext({ baseURL: origin, ignoreHTTPSErrors: true,
    extraHTTPHeaders: { Cookie: `${cookieName}=${cookie.value}`, Origin: origin } })
}

test.beforeEach(() => { manage('reset') })
test('login React local, cookies, CSRF e conta sem vinculos implicitos', async ({ page }) => {
  const profile = await login(page)
  expect(Object.keys(profile).sort()).toEqual(['csrf_token', 'expires_at', 'role', 'user_id'])
  expect(profile.role).toBe('administracao')
  expect(manage('state').memberships).toBe(0)
  const cookie = (await page.context().cookies()).find(value => value.name === cookieName)
  expect(Boolean(cookie?.secure && cookie.httpOnly && cookie.sameSite === 'Lax' && cookie.path === '/' && cookie.value.length >= 43)).toBe(true)
  expect((await page.request.get('/api/v1/auth/me')).status()).toBe(200)
  const denied = await page.request.post('/api/v1/projects', { headers: { Origin: origin }, data: { code: 'SYNTHETIC_DENIED', name: 'Synthetic' } })
  expect(denied.status()).toBe(403)
  expect((await denied.json()).error.code).toBe('csrf_failed')
  await page.getByRole('button', { name: 'Administração', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Contas e permissões' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Cadastrar conta' })).toHaveCount(0)
  await expect(page.getByText('Google', { exact: false })).toHaveCount(0)
  const accounts = await page.request.get('/api/v1/admin/users')
  expect(accounts.status()).toBe(200)
  expect((await accounts.json()).items).toEqual([{ user_id: profile.user_id, role: 'administracao', active: true }])
})

test('inexistente, senha incorreta e bloqueio tem resposta generica; origem obrigatoria', async ({ page }) => {
  await page.goto('/equipe')
  const noOrigin = await page.request.post('/api/v1/auth/login', { data: { username, password } })
  expect(noOrigin.status()).toBe(403)
  const failures: unknown[] = []
  for (const [user, secret] of [[username, otherPassword], ['synthetic-missing-local', password]]) {
    const response = await page.request.post('/api/v1/auth/login', { headers: { Origin: origin }, data: { username: user, password: secret } })
    expect(response.status()).toBe(401)
    failures.push((await response.json()).error)
  }
  manage('block')
  const blocked = await page.request.post('/api/v1/auth/login', { headers: { Origin: origin }, data: { username, password } })
  expect(blocked.status()).toBe(401)
  failures.push((await blocked.json()).error)
  expect(failures).toEqual(Array(3).fill({ code: 'authentication_required', message: 'Usuário ou senha inválidos.' }))
  expect((await page.context().cookies()).some(cookie => cookie.name === cookieName)).toBe(false)
  manage('unblock')
  await page.getByLabel('Usuário', { exact: true }).fill(username)
  await page.getByLabel('Senha', { exact: true }).fill(otherPassword)
  await page.getByRole('button', { name: 'Entrar', exact: true }).click()
  await expect(page.getByRole('alert')).toHaveText('Usuário ou senha inválidos.')
  await expect(page.getByLabel('Senha', { exact: true })).toHaveValue('')
})

test('logout pela UI revoga replay e repeticao sem cookie e idempotente', async ({ page }) => {
  await login(page)
  const previous = await replay(page)
  try {
    await page.getByRole('button', { name: 'Encerrar sessão', exact: true }).click()
    await expect(page.getByLabel('Usuário', { exact: true })).toBeVisible()
    expect((await previous.get('/api/v1/auth/me')).status()).toBe(401)
    expect((await page.request.post('/api/v1/auth/logout', { headers: { Origin: origin }, data: {} })).status()).toBe(204)
    expect(manage('state').sessions).toBe(0)
  } finally { await previous.dispose() }
})

test('troca de senha React revoga todas as sessoes e exige novo login', async ({ page }) => {
  await login(page)
  const independent = await request.newContext({ baseURL: origin, ignoreHTTPSErrors: true, extraHTTPHeaders: { Origin: origin } })
  try {
    expect((await independent.post('/api/v1/auth/login', { data: { username, password } })).status()).toBe(200)
    await page.getByText('Alterar senha', { exact: true }).click()
    await page.getByLabel('Senha atual', { exact: true }).fill(password)
    await page.getByLabel('Nova senha', { exact: true }).fill(otherPassword)
    await page.getByLabel('Confirmar nova senha', { exact: true }).fill(otherPassword)
    const changed = page.waitForResponse(value => value.url().endsWith('/api/v1/auth/password'))
    await page.getByRole('button', { name: 'Confirmar nova senha e encerrar sessões' }).click()
    expect((await changed).status()).toBe(204)
    await expect(page.getByLabel('Usuário', { exact: true })).toBeVisible()
    expect((await independent.get('/api/v1/auth/me')).status()).toBe(401)
    expect((await page.request.post('/api/v1/auth/login', { headers: { Origin: origin }, data: { username, password } })).status()).toBe(401)
    expect((await page.request.post('/api/v1/auth/login', { headers: { Origin: origin }, data: { username, password: otherPassword } })).status()).toBe(200)
  } finally { await independent.dispose() }
})

test('ultimo admin protegido e revogacao administrativa invalida replay', async ({ page }) => {
  const profile = await login(page)
  const headers = { Origin: origin, 'X-CSRF-Token': profile.csrf_token }
  const protectedAdmin = await page.request.patch(`/api/v1/admin/users/${profile.user_id}`, { headers, data: { role: 'consulta', active: true } })
  expect(protectedAdmin.status()).toBe(409)
  const create = await page.request.post('/api/v1/admin/users', { headers,
    data: { issuer: 'https://accounts.google.com', subject: 'synthetic-extra-denied', role: 'consulta', email: null } })
  expect(create.status()).toBe(403)
  const previous = await replay(page)
  try {
    await page.getByRole('button', { name: 'Administração', exact: true }).click()
    page.once('dialog', dialog => dialog.accept())
    await page.getByRole('button', { name: 'Encerrar sessões', exact: true }).click()
    await expect(page.getByLabel('Usuário', { exact: true })).toBeVisible()
    expect((await previous.get('/api/v1/auth/me')).status()).toBe(401)
  } finally { await previous.dispose() }
})
