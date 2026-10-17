import { expect, test } from '@playwright/test'
import { finishPractice, invitation, manage, redeem } from './fixtures'

test('HTTPS real usa cookie HttpOnly e expiracao nao produz avaliacao', async ({ page, context }) => {
  const issued = await invitation()
  try {
    await redeem(page, issued.code)
    const cookie = (await context.cookies()).find(item => item.name === '__Host-stroop_participant')
    expect(cookie?.httpOnly).toBe(true)
    expect(cookie?.secure).toBe(true)
    expect(cookie?.sameSite).toBe('Lax')
    expect(await page.evaluate(() => document.cookie)).toBe('')
    expect(await page.evaluate(() => localStorage.length + sessionStorage.length)).toBe(0)
    await expect(page).toHaveURL('/pratica')
    manage('expire', { session_id: issued.session_id })
    await page.reload()
    await expect(page.getByRole('alert')).toContainText('expirou')
    await expect(page.locator('[data-phase]')).toHaveCount(0)
    const stored = manage('state', { session_id: issued.session_id })
    expect(stored.state).toBe('expired')
    expect(stored.assessments).toBe(0)
  } finally { await issued.close() }
})

test('refresh de running exige novo convite e aborta sem reconstruir motor', async ({ page }) => {
  const issued = await invitation()
  try {
    await redeem(page, issued.code)
    manage('running', { session_id: issued.session_id })
    await page.reload()
    await expect(page.getByRole('alert')).toContainText('execução anterior foi interrompida')
    await expect.poll(() => manage('state', { session_id: issued.session_id }).state).toBe('aborted')
    const stored = manage('state', { session_id: issued.session_id })
    expect(stored.reason).toBe('reload')
    expect(stored.assessments).toBe(0)
    await expect(page.locator('[data-phase]')).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Começar tarefa' })).toHaveCount(0)
  } finally { await issued.close() }
})

test('principal real recupera recibo perdido sem duplicar avaliacao e encerra credencial', async ({ page, context }) => {
  const issued = await invitation()
  try {
    await redeem(page, issued.code)
    await finishPractice(page)
    let completions = 0
    await page.route('**/api/v1/participant/complete', async route => {
      completions += 1
      const response = await route.fetch({ maxRedirects: 0 })
      expect(response.status()).toBe(201)
      // Falha de transporte depois do commit real: GET deve recuperar o recibo.
      await route.abort('failed')
    })
    await page.getByRole('button', { name: 'Começar tarefa' }).click()
    await expect(page.getByRole('heading', { name: 'Resumo da execução' })).toBeVisible({ timeout: 70_000 })
    await expect(page.getByRole('status')).toContainText('Resultado recebido pela equipe.', { timeout: 15_000 })
    expect(completions).toBe(1)
    const stored = manage('state', { session_id: issued.session_id })
    expect(stored.state).toBe('completed')
    expect([stored.assessments, stored.trials, stored.metrics]).toEqual([1, 16, 12])
    expect(await page.evaluate(() => localStorage.length + sessionStorage.length)).toBe(0)
    const detail = await issued.professional.get(`/api/v1/projects/${issued.project_id}/assessments/${stored.assessment_id}`)
    expect(detail.status()).toBe(200)
    await page.getByRole('button', { name: 'Finalizar', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Participação encerrada.' })).toBeVisible()
    expect((await context.cookies()).some(item => item.name === '__Host-stroop_participant')).toBe(false)
    expect((await page.request.get('/api/v1/participant/session')).status()).toBe(401)
    expect(manage('state', { session_id: issued.session_id }).assessments).toBe(1)
  } finally { await issued.close() }
})

test('reenvio manual conserva corpo e duplo clique grava uma unica avaliacao', async ({ page }) => {
  const issued = await invitation()
  try {
    await redeem(page, issued.code)
    await finishPractice(page)
    const bodies: string[] = []
    await page.route('**/api/v1/participant/complete', async route => {
      bodies.push(route.request().postData() ?? '')
      if (bodies.length === 1) await route.abort('failed')
      else await route.continue()
    })
    await page.getByRole('button', { name: 'Começar tarefa' }).click()
    await expect(page.getByRole('heading', { name: 'Resumo da execução' })).toBeVisible({ timeout: 70_000 })
    const retry = page.getByRole('button', { name: 'Reenviar resultado', exact: true })
    await expect(retry).toBeEnabled({ timeout: 15_000 })
    await expect(page.getByRole('status')).not.toContainText('Resultado recebido pela equipe.')
    expect(manage('state', { session_id: issued.session_id }).assessments).toBe(0)
    await retry.evaluate(element => { (element as HTMLButtonElement).click(); (element as HTMLButtonElement).click() })
    await expect(page.getByRole('status')).toContainText('Resultado recebido pela equipe.')
    expect(bodies.length).toBe(2)
    expect(bodies[0] === bodies[1]).toBe(true)
    const stored = manage('state', { session_id: issued.session_id })
    expect([stored.assessments, stored.trials, stored.metrics]).toEqual([1, 16, 12])
    await expect(page.getByRole('button', { name: 'Começar tarefa' })).toHaveCount(0)
    await page.getByRole('button', { name: 'Finalizar', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Participação encerrada.' })).toBeVisible()
  } finally { await issued.close() }
})
