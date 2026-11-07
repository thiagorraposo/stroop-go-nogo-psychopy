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
    expect([stored.assessments, stored.trials, stored.metrics, stored.observations, stored.confirmed_through])
      .toEqual([1, 16, 12, 16, 16])
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
    await expect.poll(() => manage('state', { session_id: issued.session_id }).confirmed_through).toBe(16)
    expect(manage('state', { session_id: issued.session_id }).assessments).toBe(0)
    await retry.evaluate(element => { (element as HTMLButtonElement).click(); (element as HTMLButtonElement).click() })
    await expect(page.getByRole('status')).toContainText('Resultado recebido pela equipe.')
    expect(bodies.length).toBe(2)
    expect(bodies[0] === bodies[1]).toBe(true)
    const stored = manage('state', { session_id: issued.session_id })
    expect([stored.assessments, stored.trials, stored.metrics, stored.observations, stored.confirmed_through])
      .toEqual([1, 16, 12, 16, 16])
    await expect(page.getByRole('button', { name: 'Começar tarefa' })).toHaveCount(0)
    await page.getByRole('button', { name: 'Finalizar', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Participação encerrada.' })).toBeVisible()
  } finally { await issued.close() }
})

test('receptor incremental HTTPS confirma prefixo e exclui invalidacao tardia do oficial', async ({ page }) => {
  const issued = await invitation()
  try {
    await redeem(page, issued.code)
    const bootstrapResponse = await page.request.get('/api/v1/participant/session')
    const bootstrap = await bootstrapResponse.json()
    const headers = { Origin: new URL(page.url()).origin, 'X-CSRF-Token': bootstrap.csrf_token }
    const payload = {
      protocol_id: bootstrap.protocol_id, test_version: bootstrap.test_version, platform: 'web',
      app_version: 'synthetic-m2-receiver', frame_period_ms: 16,
      trials: bootstrap.main_conditions.map((condition: { condition_id: number }, index: number) => ({
        trial_number: index + 1, condition_id: condition.condition_id, key_pressed: null,
        reaction_time_ms: null, key_at_ms: null, trial_start_ms: index * 3750,
        stimulus_onset_ms: index * 3750 + 300, stimulus_offset_ms: index * 3750 + 2800,
        trial_end_ms: (index + 1) * 3750,
      })),
    }
    expect((await page.request.post('/api/v1/participant/start', { headers, data: { app_version: payload.app_version } })).status()).toBe(200)
    const path = '/api/v1/participant/session/checkpoints'
    const body = { ...payload, trials: payload.trials.slice(0, 3) }
    const first = await page.request.post(path, { headers, data: body })
    expect(first.status()).toBe(200)
    const ack = await first.json()
    expect(ack.confirmed_through).toBe(3)
    expect(ack.prefix_hash).toMatch(/^[a-f0-9]{64}$/)
    expect(await (await page.request.post(path, { headers, data: body })).json()).toEqual(ack)
    expect((await (await page.request.get('/api/v1/participant/session')).json()).checkpoint.confirmed_through).toBe(3)
    const complete = await page.request.post('/api/v1/participant/complete', { headers, data: payload })
    expect(complete.status()).toBe(201)
    const receipt = await complete.json()
    expect(receipt.summary.response_time_seconds).toBeNull()
    expect((await page.request.post('/api/v1/participant/session/invalidate', {
      headers, data: { reason: 'visibility_hidden', event_at_ms: 59000 },
    })).status()).toBe(200)
    const base = `/api/v1/projects/${issued.project_id}`
    const detail = await issued.professional.get(`${base}/assessments/${receipt.assessment_id}`)
    expect((await detail.json()).valid_for_result).toBe(false)
    expect((await issued.professional.get(`${base}/assessments/${receipt.assessment_id}/export`)).status()).toBe(404)
    const state = await issued.professional.get(`${base}/sessions/${issued.session_id}`)
    expect(state.status()).toBe(200)
    expect((await state.json()).checkpoint.confirmed_through).toBe(16)
    expect(manage('state', { session_id: issued.session_id }).assessments).toBe(1)
  } finally { await issued.close() }
})

test('worker incremental preserva prefixo parcial em interrupcao sem resultado oficial e exige pratica em nova sessao', async ({ page }) => {
  const first = await invitation()
  const second = await invitation()
  try {
    await redeem(page, first.code)
    await finishPractice(page)
    await page.getByRole('button', { name: 'Começar tarefa' }).click()
    await expect.poll(() => manage('state', { session_id: first.session_id }).confirmed_through, { timeout: 25_000 })
      .toBeGreaterThanOrEqual(1)
    await expect(page.locator('[data-phase="stimulus"]')).toBeVisible({ timeout: 8_000 })
    await page.keyboard.press('Escape')
    await expect(page.getByRole('alert')).toContainText('observação parcial, sem gerar resultado oficial')
    await expect(page.getByRole('alert')).toContainText('Solicite um novo convite e faça a prática novamente.')
    await expect.poll(() => manage('state', { session_id: first.session_id }).state).toBe('aborted')
    const partial = manage('state', { session_id: first.session_id })
    expect(partial.assessments).toBe(0)
    expect(partial.observations).toBeGreaterThanOrEqual(1)
    expect(partial.confirmed_through).toBe(partial.observations)
    const inspect = await first.professional.get(`/api/v1/projects/${first.project_id}/sessions/${first.session_id}`)
    expect(inspect.status()).toBe(200)
    expect(await inspect.json()).toMatchObject({
      session_id: first.session_id,
      state: 'aborted',
      complete: false,
      valid_for_result: false,
      abort_reason: 'escape',
      checkpoint: { confirmed_through: partial.confirmed_through },
    })

    // Nova sessao nunca retoma do prefixo e exige pratica completa antes do bloco principal.
    await page.getByLabel('Código do convite').fill(second.code)
    await page.getByRole('button', { name: 'Validar convite' }).click()
    await expect(page.getByRole('heading', { name: 'Primeiro, vamos praticar.' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Começar tarefa' })).toHaveCount(0)
  } finally {
    await first.close()
    await second.close()
  }
})
