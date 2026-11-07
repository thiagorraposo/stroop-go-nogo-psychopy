/** Gestao de contas e acesso comprovados pela interface e API HTTPS real. */
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { randomUUID } from 'node:crypto'
import { expect, test, request } from '@playwright/test'

const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const management = fileURLToPath(new URL('./manage.py', import.meta.url))
function session(value: Record<string, unknown> = {}) {
  return JSON.parse(execFileSync(python, [management, 'professional'], { input: JSON.stringify(value),
    encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] })) as {
      cookie_name: string; token: string; csrf: string; user_id: string
    }
}

test('administra perfil sintetico/projeto, prepara sessao e acesso depende do vinculo ativo', async ({ page, context }) => {
  const admin = session()
  // Operador prepara perfil sintetico adicional somente para regressao; UI nao cadastra.
  const seeded = JSON.parse(execFileSync(python, [management, 'fixture_user'], {
    input: JSON.stringify({ role: 'importacao' }), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'],
  })) as { subject: string; user_id: string }
  const subject = seeded.subject
  const memberUserId = seeded.user_id
  await context.addCookies([{ name: admin.cookie_name, value: admin.token, domain: '127.0.0.1', path: '/',
    secure: true, httpOnly: true, sameSite: 'Lax' }])
  await page.goto('/equipe')
  await page.getByRole('button', { name: 'Administração', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Cadastrar conta' })).toHaveCount(0)
  const accounts = page.getByRole('table', { name: 'Contas cadastradas' })
  await expect(accounts.getByRole('row').filter({ hasText: memberUserId })).toBeVisible()

  const projectCode = `SYNTHETIC_${randomUUID().replaceAll('-', '')}`
  await page.getByLabel('Código do projeto').fill(projectCode)
  await page.getByLabel('Nome do projeto').fill('Projeto sintetico W15D')
  await page.getByRole('button', { name: 'Criar projeto' }).click()
  await expect(page.getByLabel('Projeto para vínculos')).toContainText(projectCode)
  await page.getByLabel('Conta para vincular').selectOption({ label: `${memberUserId} — importacao` })
  page.once('dialog', dialog => void dialog.accept())
  await page.getByRole('button', { name: 'Ativar vínculo' }).click()
  await expect(page.getByRole('table', { name: 'Vínculos do projeto selecionado' })).toContainText(memberUserId)

  const member = session({ subject })
  const projectId = await page.getByLabel('Projeto para vínculos').inputValue()
  const importerContext = await page.context().browser()!.newContext({ ignoreHTTPSErrors: true })
  const importerPage = await importerContext.newPage()
  await importerContext.addCookies([{ name: member.cookie_name, value: member.token, domain: '127.0.0.1', path: '/',
    secure: true, httpOnly: true, sameSite: 'Lax' }])
  await importerPage.goto('/equipe')
  await importerPage.getByRole('combobox', { name: 'Projeto', exact: true }).selectOption(projectId)
  const preparation = importerPage.getByRole('region', { name: 'Preparar sessão' })
  await preparation.getByLabel('Código do participante').fill('P_SINTETICO_W15D')
  await preparation.getByLabel('Visita da sessão').fill('V_SINTETICA')
  await preparation.getByRole('button', { name: 'Gerar convite' }).click()
  const code = (await preparation.getByLabel('Código do convite').textContent())!.trim()

  const participant = await request.newContext({ baseURL: 'https://127.0.0.1:4373', ignoreHTTPSErrors: true,
    extraHTTPHeaders: { Origin: 'https://127.0.0.1:4373' } })
  const redeemed = await participant.post('/api/v1/participant/redeem', { data: { code } })
  expect(redeemed.status()).toBe(201)
  const csrf = (await redeemed.json()).csrf_token as string
  const bootstrapResponse = await participant.get('/api/v1/participant/session')
  expect(bootstrapResponse.status()).toBe(200)
  const bootstrap = await bootstrapResponse.json()
  const started = await participant.post('/api/v1/participant/start', {
    data: { app_version: 'synthetic-web-0.1.0' }, headers: { 'X-CSRF-Token': csrf } })
  expect(started.status()).toBe(200)
  const payload = { protocol_id: bootstrap.protocol_id, test_version: bootstrap.test_version,
    platform: 'web', app_version: 'synthetic-web-0.1.0', frame_period_ms: 16,
    trials: bootstrap.main_conditions.map((condition: { condition_id: number }, index: number) => {
      const startMs = index * 3750
      const responds = condition.condition_id % 2 === 0
      return { trial_number: index + 1, condition_id: condition.condition_id,
        key_pressed: responds ? 'space' : null, reaction_time_ms: responds ? 512.25 : null,
        trial_start_ms: startMs, stimulus_onset_ms: startMs + 300, stimulus_offset_ms: startMs + 2800,
        trial_end_ms: startMs + 3750, key_at_ms: responds ? startMs + 812.25 : null }
    }) }
  const completed = await participant.post('/api/v1/participant/complete', {
    data: payload, headers: { 'X-CSRF-Token': csrf } })
  expect(completed.status()).toBe(201)
  await importerPage.reload()
  await expect(importerPage.getByRole('table', { name: 'Avaliações filtradas' })).toContainText('P_SINTETICO_W15D')

  const credentials = await request.newContext({ baseURL: 'https://127.0.0.1:4373', ignoreHTTPSErrors: true,
    extraHTTPHeaders: { Cookie: `${member.cookie_name}=${member.token}` } })
  try {
    const linked = await credentials.get('/api/v1/projects')
    expect(linked.status()).toBe(200)
    expect(JSON.stringify(await linked.json())).toContain(projectCode)

    const row = accounts.getByRole('row').filter({ hasText: memberUserId })
    const revoke = page.getByRole('table', { name: 'Vínculos do projeto selecionado' }).getByRole('row').filter({ hasText: memberUserId })
    page.once('dialog', dialog => void dialog.accept())
    await revoke.getByRole('button', { name: 'Revogar' }).click()
    await expect(revoke).toContainText('Revogado')
    await expect(row).toContainText(memberUserId)
    const revoked = await credentials.get('/api/v1/projects')
    expect(revoked.status()).toBe(200)
    expect(JSON.stringify(await revoked.json())).not.toContain(projectCode)

    page.once('dialog', dialog => void dialog.accept())
    await row.getByRole('button', { name: 'Editar' }).click()
    await page.getByLabel('Conta ativa').uncheck()
    await page.getByRole('button', { name: 'Confirmar alterações' }).click()
    await expect(row).toContainText('Bloqueada')
    const blocked = await credentials.get('/api/v1/auth/me')
    expect(blocked.status()).toBe(401)
    expect(await blocked.json()).toMatchObject({ error: { code: 'authentication_required' } })
  } finally {
    await participant.dispose()
    await importerContext.close()
    await credentials.dispose()
  }
})
