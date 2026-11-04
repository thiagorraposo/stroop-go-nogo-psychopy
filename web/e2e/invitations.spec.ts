/** Doubles sinteticos; nao substituem o aceite HTTPS/PostgreSQL real. */
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
const id = '11111111-1111-4111-8111-111111111111', other = '22222222-2222-4222-8222-222222222222'
const invitation = { invitation_id: '33333333-3333-4333-8333-333333333333', session_id: '44444444-4444-4444-8444-444444444444',
  code: 'SINTETICO_NAO_UTILIZAVEL_123456789', expires_at: '2026-10-18T13:00:00Z', state: 'issued' }
const endpoint = `**/api/v1/projects/${id}/invitations`
const panel = (p: Page) => p.getByRole('region', { name: 'Preparar sessão' })
const code = (p: Page) => p.getByRole('status', { name: 'Código do convite' })
async function access(page: Page, role = 'importacao', active = true) {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { user_id: 'avaliador_sintetico', role,
    expires_at: new Date(Date.now() + 3600000).toISOString(), csrf_token: 's'.repeat(43) } }))
  const project = { id, code: 'PROJETO_SINTETICO', name: 'Pesquisa sintetica', active, created_at: '2026-10-16T12:00:00Z' }
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [project,
    { ...project, id: other, code: 'OUTRO_SINTETICO', active: true }], next_cursor: null } }))
  await page.route('**/api/v1/projects/*/assessments?*', route => route.fulfill({ json: { items: [], next_cursor: null } }))
  await page.goto('/equipe'); await expect(page.getByLabel('Projeto', { exact: true })).toBeVisible()
}
async function fill(page: Page) {
  await page.getByLabel('Código do participante', { exact: true }).fill(' P_SINTETICO ')
  await page.getByLabel('Visita da sessão').fill(' V_2 ')
}
for (const [role, active] of [['consulta', true], ['importacao', false], ['administracao', false]] as const) {
  test(`${role} ativo=${active} sem controles`, async ({ page }) => {
    await access(page, role, active); await expect(panel(page)).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Gerar convite' })).toHaveCount(0)
  })
}
for (const role of ['importacao', 'administracao']) {
  test(`${role} valida, normaliza, cria e revoga`, async ({ page }, testInfo) => {
    let created = 0, revoked = 0
    await page.route(endpoint, route => {
      created++; expect(route.request().postDataJSON()).toEqual({ participant_id: 'P_SINTETICO', visit: 'V_2' })
      expect(route.request().headers()['x-csrf-token']).toBe('s'.repeat(43))
      return route.fulfill({ status: 201, json: invitation })
    })
    await page.route(`${endpoint}/${invitation.invitation_id}/revoke`, route => {
      revoked++; expect(route.request().postDataJSON()).toEqual({}); return route.fulfill({ status: 204 })
    })
    await access(page, role); await page.getByRole('button', { name: 'Gerar convite' }).click()
    await expect(panel(page).getByRole('alert')).toHaveCount(2)
    await page.getByLabel('Código do participante', { exact: true }).fill('codigo invalido')
    await page.getByLabel('Visita da sessão').fill('V_2')
    await page.getByRole('button', { name: 'Gerar convite' }).click()
    await expect(page.getByLabel('Código do participante', { exact: true })).toHaveAttribute('aria-invalid', 'true')
    expect(created).toBe(0); await fill(page); await page.getByLabel('Visita da sessão').press('Enter')
    await expect(code(page)).toHaveText(invitation.code); await expect(panel(page)).toBeFocused()
    await expect(panel(page)).toContainText('Participante: P_SINTETICO · Visita: V_2')
    await expect(panel(page)).toContainText('avaliador_sintetico')
    if (role === 'importacao' && testInfo.project.name === 'chromium') await page.screenshot({ path: '/tmp/stroop-w13a-invite.png', fullPage: true })
    await expect(page.getByRole('link', { name: 'Abrir prática em outra aba' })).toHaveAttribute('href', '/pratica')
    expect(page.url()).not.toContain(invitation.code)
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
    await page.getByRole('button', { name: 'Revogar convite', exact: true }).click()
    await expect(panel(page).getByRole('status')).toContainText('Revogação confirmada')
    await expect(code(page)).toHaveCount(0); expect(created).toBe(1); expect(revoked).toBe(1)
    await page.getByRole('button', { name: 'Preparar outra sessão' }).click()
    await expect(page.getByLabel('Código do participante', { exact: true })).toBeFocused()
  })
}
test('duplo envio em espera faz apenas um POST', async ({ page }) => {
  let calls = 0, release!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  await page.route(endpoint, async route => { calls++; await gate; await route.fulfill({ status: 201, json: invitation }) })
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click()
  await expect(page.getByRole('button', { name: 'Gerando convite…' })).toBeDisabled()
  await panel(page).locator('form').evaluate(form => {
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  })
  release(); await expect(code(page)).toHaveText(invitation.code); expect(calls).toBe(1)
})
test('falha de rede mostra resultado desconhecido sem repetir', async ({ page }) => {
  let calls = 0
  await page.route(endpoint, route => { calls++; return route.abort('failed') })
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click()
  await expect(panel(page).getByRole('alert')).toContainText('A sessão pode ter sido criada')
  await expect(panel(page).getByRole('alert')).toContainText('Sem identificador confirmado')
  await expect(page.getByRole('button', { name: 'Gerar convite', exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Revogar convite', exact: true })).toHaveCount(0); expect(calls).toBe(1)
})
test('troca projeto descarta resposta pendente e limpa codigo confirmado', async ({ page }) => {
  let release!: () => void, started!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  const received = new Promise<void>(resolve => { started = resolve })
  await page.route(endpoint, async route => { started(); await gate; await route.fulfill({ status: 201, json: invitation }).catch(() => undefined) })
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click(); await received
  await page.getByLabel('Projeto', { exact: true }).selectOption(other)
  await expect(page.getByLabel('Código do participante', { exact: true })).toHaveValue('')
  release(); await expect(panel(page)).not.toContainText(invitation.code)
  await page.getByLabel('Projeto', { exact: true }).selectOption(id)
  await page.unroute(endpoint); await page.route(endpoint, route => route.fulfill({ status: 201, json: invitation }))
  await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click(); await expect(code(page)).toHaveText(invitation.code)
  await page.getByLabel('Projeto', { exact: true }).selectOption(other)
  await expect(panel(page)).not.toContainText(invitation.code); await expect(page.getByLabel('Visita da sessão')).toHaveValue('')
})
test('logout apaga codigo confirmado', async ({ page }) => {
  await page.route(endpoint, route => route.fulfill({ status: 201, json: invitation }))
  await page.route('**/api/v1/auth/logout', route => route.fulfill({ status: 204 }))
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click()
  await expect(code(page)).toHaveText(invitation.code)
  await page.getByRole('button', { name: 'Encerrar sessão', exact: true }).click()
  await expect(panel(page)).toHaveCount(0); await expect(page.locator('body')).not.toContainText(invitation.code)
})
