/** W13A: emissao pela interface e coleta HTTPS/PostgreSQL reais, sem mocks. */
import { execFileSync } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'
import type { BrowserContext, Page } from '@playwright/test'
import { finishPractice, manage, redeem } from './fixtures'

const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const script = fileURLToPath(new URL('./dashboard-manage.py', import.meta.url))
type Prepared = { cookie_name: string; token: string; project_id: string; evaluator_id: string }
async function professional(page: Page, context: BrowserContext, role: string): Promise<Prepared> {
  const prepared: Prepared = JSON.parse(execFileSync(python, [script], {
    input: JSON.stringify({ role }), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'],
  }))
  await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1',
    path: '/', secure: true, httpOnly: true, sameSite: 'Lax' }])
  await page.goto('/equipe')
  await page.getByRole('combobox', { name: 'Projeto', exact: true }).selectOption(prepared.project_id)
  return prepared
}
async function issue(page: Page, project: string, participant: string, visit: string) {
  await page.getByLabel('Código do participante', { exact: true }).fill(` ${participant} `)
  await page.getByLabel('Visita da sessão', { exact: true }).fill(` ${visit} `)
  const response = page.waitForResponse(value => value.url().endsWith(`/projects/${project}/invitations`)
    && value.request().method() === 'POST')
  await page.getByRole('button', { name: 'Gerar convite', exact: true }).focus()
  await page.keyboard.press('Enter')
  const created = await response
  expect(created.status()).toBe(201)
  const issued = await created.json() as { session_id: string; invitation_id: string; code: string }
  await expect(page.getByLabel('Código do convite', { exact: true })).toHaveText(issued.code)
  expect(page.url()).not.toContain(issued.code)
  expect(await page.evaluate(() => [document.cookie, localStorage.length, sessionStorage.length])).toEqual(['', 0, 0])
  return issued
}

test('cadastro pela equipe conserva metadados ate recibo, consulta e CSV reais', async ({ page, context }) => {
  const prepared = await professional(page, context, 'importacao')
  const participant = 'P_SINTETICO_W13A'
  const visit = 'VISITA_W13A'
  const issued = await issue(page, prepared.project_id, participant, visit)
  const participantPage = await context.newPage()
  try {
    await redeem(participantPage, issued.code)
    await finishPractice(participantPage)
    await participantPage.getByRole('button', { name: 'Começar tarefa' }).click()
    await expect(participantPage.getByRole('heading', { name: 'Resumo da execução' })).toBeVisible({ timeout: 70_000 })
    await expect(participantPage.getByRole('status')).toContainText('Resultado recebido pela equipe.', { timeout: 15_000 })
    const stored = manage('state', { session_id: issued.session_id })
    expect([stored.state, stored.assessments, stored.trials, stored.metrics]).toEqual(['completed', 1, 16, 12])
    await page.reload()
    await page.getByRole('combobox', { name: 'Projeto', exact: true }).selectOption(prepared.project_id)
    await page.getByRole('button', { name: `Ver avaliação ${participant}, visita ${visit}` }).click()
    const detail = page.getByRole('region', { name: 'Detalhe da avaliação' })
    await expect(detail).toBeVisible()
    const response = await page.request.get(`/api/v1/projects/${prepared.project_id}/assessments/${stored.assessment_id}`)
    expect(response.status()).toBe(200)
    const assessment = await response.json()
    expect(assessment).toMatchObject({ participant_id: participant, visit, evaluator_id: prepared.evaluator_id,
      project_id: prepared.project_id, session_id: issued.session_id, platform: 'web' })
    const downloading = page.waitForEvent('download')
    await detail.getByRole('button', { name: 'Exportar CSV oficial' }).click()
    const download = await downloading
    const path = await download.path()
    expect(path).not.toBeNull()
    const lines = (await readFile(path!, 'utf8')).trim().split(/\r?\n/)
    const headers = lines[0]!.replace(/^\uFEFF/, '').split(',')
    expect(lines).toHaveLength(17)
    for (const line of lines.slice(1)) {
      const cells = line.split(',')
      for (const [column, value] of [['participant_id', participant], ['visit', visit], ['evaluator', prepared.evaluator_id]]) {
        expect(cells[headers.indexOf(column!)]).toBe(value)
      }
    }
    await participantPage.getByRole('button', { name: 'Finalizar', exact: true }).click()
    await expect(participantPage.getByRole('heading', { name: 'Participação encerrada.' })).toBeVisible()
  } finally { await participantPage.close() }
})

test('administracao vinculada emite e revoga pela tela impedindo resgate', async ({ page, context }) => {
  const prepared = await professional(page, context, 'administracao')
  const issued = await issue(page, prepared.project_id, 'P_SINTETICO_REVOGADO', 'V_REVOGADA')
  const revoked = page.waitForResponse(value => value.url().endsWith(`/invitations/${issued.invitation_id}/revoke`)
    && value.request().method() === 'POST')
  await page.getByRole('button', { name: 'Revogar convite', exact: true }).click()
  expect((await revoked).status()).toBe(204)
  await page.getByRole('button', { name: 'Preparar outra sessão', exact: true }).click()
  await expect(page.getByLabel('Código do participante', { exact: true })).toHaveValue('')
  const participant = await context.newPage()
  try {
    await participant.goto('/pratica')
    await participant.getByLabel('Código do convite').fill(issued.code)
    const redemption = participant.waitForResponse(value => value.url().endsWith('/participant/redeem'))
    await participant.getByRole('button', { name: 'Validar convite' }).click()
    expect((await redemption).ok()).toBe(false)
    await expect(participant.getByRole('alert')).toBeVisible()
    await expect(participant.getByRole('heading', { name: 'Primeiro, vamos praticar.' })).toHaveCount(0)
    expect(manage('state', { session_id: issued.session_id }).assessments).toBe(0)
  } finally { await participant.close() }
})

test('consulta vinculada nao recebe controles de cadastro ou revogacao', async ({ page, context }) => {
  await professional(page, context, 'consulta')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Gerar convite', exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Revogar convite', exact: true })).toHaveCount(0)
  await expect(page.getByLabel('Código do participante', { exact: true })).toHaveCount(0)
})
