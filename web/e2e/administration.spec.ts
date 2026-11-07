import { expect, test } from '@playwright/test'
const adminId = 'aHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tAHN5bnRoZXRpYy1hZG1pbg'
const userId = 'aHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tAHN5bnRoZXRpYy11c2Vy'
const project = '11111111-1111-4111-8111-111111111111'
const csrf = 's'.repeat(43)
const initialUsers = [
  { user_id: adminId, role: 'administracao', active: true },
  { user_id: userId, role: 'consulta', active: true },
]

test('administra contas, projetos e vinculos com confirmacao; outros perfis nao veem area', async ({ page }) => {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { user_id: adminId, role: 'administracao', csrf_token: csrf, expires_at: new Date(Date.now() + 3600000).toISOString() } }))
  let users = [...initialUsers]
  let revokedTarget = ''
  await page.route('**/api/v1/admin/users?*', route => route.fulfill({ json: { items: users, next_cursor: null } }))
  await page.route('**/api/v1/admin/users', async route => {
    expect(route.request().method()).toBe('GET')
    return route.fulfill({ json: { items: users, next_cursor: null } })
  })
  await page.route(/\/api\/v1\/admin\/users\/[A-Za-z0-9_-]+\/sessions\/revoke$/, async route => {
    expect(route.request().method()).toBe('POST')
    expect(route.request().headers()['x-csrf-token']).toBe(csrf)
    expect(route.request().postDataJSON()).toEqual({})
    revokedTarget = new URL(route.request().url()).pathname.split('/').at(-3)!
    return route.fulfill({ status: 204 })
  })
  await page.route(/\/api\/v1\/admin\/users\/[A-Za-z0-9_-]+$/, async route => {
    expect(route.request().method()).toBe('PATCH')
    expect(route.request().headers()['x-csrf-token']).toBe(csrf)
    const body = route.request().postDataJSON()
    const target = new URL(route.request().url()).pathname.split('/').at(-1)!
    users = users.map(item => item.user_id === target ? { ...item, ...body } : item)
    return route.fulfill({ json: { user_id: target, ...body } })
  })
  const memberships = new Map<string, boolean>()
  await page.route(/\/api\/v1\/projects\/[a-f0-9-]+\/members(?:\?.*)?$/, route => {
    const items = [...memberships].map(([memberId, active]) => ({ user_id: memberId, active }))
    return route.fulfill({ json: { items, next_cursor: null } })
  })
  await page.route(/\/api\/v1\/projects\/[a-f0-9-]+\/members\/[A-Za-z0-9_-]+$/, async route => {
    expect(route.request().headers()['x-csrf-token']).toBe(csrf)
    const body = route.request().postDataJSON()
    const memberId = new URL(route.request().url()).pathname.split('/').at(-1)!
    memberships.set(memberId, body.active)
    return route.fulfill({ json: { user_id: memberId, active: body.active } })
  })
  await page.route(/\/api\/v1\/projects(?:\?.*)?$/, route => {
    if (route.request().method() === 'GET') return route.fulfill({ json: { items: [{ id: project, code: 'SYNTHETIC_ADMIN', name: 'Projeto sintetico', active: true, created_at: '2026-10-17T10:00:00Z' }], next_cursor: null } })
    const body = route.request().postDataJSON()
    expect(route.request().headers()['x-csrf-token']).toBe(csrf)
    return route.fulfill({ status: 201, json: { id: '22222222-2222-4222-8222-222222222222', ...body, active: true, created_at: '2026-10-17T10:00:00Z' } })
  })
  await page.goto('/equipe')
  await page.getByRole('button', { name: 'Administração', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Contas e permissões' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Cadastrar conta' })).toHaveCount(0)
  await expect(page.getByRole('row', { name: new RegExp(userId) })).toBeVisible()
  await page.getByLabel('Código do projeto', { exact: true }).fill('SYNTHETIC_CREATED')
  await page.getByLabel('Nome do projeto', { exact: true }).fill('Projeto criado sintetico')
  await page.getByRole('button', { name: 'Criar projeto', exact: true }).click()
  await page.getByLabel('Conta para vincular', { exact: true }).selectOption(userId)
  await page.once('dialog', dialog => dialog.accept())
  await page.getByRole('button', { name: 'Ativar vínculo', exact: true }).click()
  await expect(page.getByRole('row', { name: new RegExp(`${userId} Ativo`) })).toBeVisible()
  await page.once('dialog', dialog => dialog.accept())
  await page.getByRole('row', { name: new RegExp(`${userId} Ativo`) }).getByRole('button', { name: 'Revogar' }).click()
  await expect(page.getByRole('row', { name: new RegExp(`${userId} Revogado`) })).toBeVisible()

  await page.once('dialog', dialog => dialog.accept())
  await page.getByRole('row', { name: new RegExp(`${userId} consulta`) }).getByRole('button', { name: 'Encerrar sessões' }).click()
  await expect(page.getByRole('status')).toHaveText('Sessões encerradas.')
  expect(revokedTarget).toBe(userId)

  await page.getByLabel('Conta para alterar', { exact: true }).selectOption(userId)
  await page.getByLabel('Conta ativa', { exact: true }).uncheck()
  await page.once('dialog', dialog => dialog.accept())
  await page.getByRole('button', { name: 'Confirmar alterações', exact: true }).click()
  await expect(page.getByRole('row', { name: /Bloqueada/ })).toBeVisible()
})

test('perfil sem administracao nao recebe navegacao administrativa', async ({ page }) => {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { user_id: 'synthetic-user', role: 'consulta', csrf_token: csrf, expires_at: new Date(Date.now() + 3600000).toISOString() } }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [], next_cursor: null } }))
  await page.goto('/equipe')
  await expect(page.getByRole('navigation', { name: 'Áreas profissionais' })).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Administração' })).toHaveCount(0)
})
