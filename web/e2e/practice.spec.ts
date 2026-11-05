import { mockParticipant } from './support/participant'
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'

test.beforeEach(async ({ page }) => { await mockParticipant(page) })

async function feedbackOutcome(page: Page): Promise<string> {
  // O feedback dura 500 ms; observar a cada quadro evita perder a fase
  // entre tentativas de assercao com backoff maior que sua duracao.
  const outcome = await page.waitForFunction(() =>
    document.querySelector('[data-phase="feedback"]')?.getAttribute('data-outcome'),
  undefined, { polling: 'raf', timeout: 5_000 })
  return await outcome.jsonValue() as string
}

async function prepare(page: Page) {
  await page.goto('/pratica')
  await expect(page.getByRole('button', { name: 'Começar prática', exact: true })).toBeDisabled()
  await page.getByLabel('Estou usando um computador ou notebook com teclado físico.').check()
  await page.getByRole('main').focus()
  await page.keyboard.press('Space')
  await expect(page.getByRole('status')).toHaveText('Teclado verificado.')
  await expect(page.getByRole('button', { name: 'Começar prática', exact: true })).toBeEnabled()
}

test('navegacao por teclado nao inicia treino sem confirmar e testar o teclado', async ({ page }) => {
  await page.goto('/')
  // O foco inicial e aplicado pelo effect que sucede a instalacao dos listeners.
  // goto aguarda load, mas nao garante que o React ja montou a navegacao.
  await expect(page.getByRole('main')).toBeFocused()
  await page.keyboard.press('Space')
  await expect(page).toHaveURL('/instrucoes')
  await expect(page.getByRole('main')).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL('/pratica')
  await page.getByLabel('Estou usando um computador ou notebook com teclado físico.').check()
  await expect(page.getByRole('button', { name: 'Começar prática', exact: true })).toBeDisabled()
  await page.getByRole('main').focus()
  await page.keyboard.press('Space')
  await expect(page.getByRole('button', { name: 'Começar prática', exact: true })).toBeEnabled()
  await expect(page.locator('[data-phase]')).toHaveCount(0)
})

test('rodada real mostra quatro feedbacks sem encurtar estimulo e pode repetir', async ({ page }) => {
  test.setTimeout(45_000)
  await prepare(page)
  await page.getByRole('button', { name: 'Começar prática', exact: true }).click()
  const ids = new Set<string>()
  const outcomes = new Set<string>()
  const responded = new Set<string>()
  for (let trial = 1; trial <= 4; trial += 1) {
    const stimulus = page.locator('[data-phase="stimulus"]')
    await expect(stimulus).toBeVisible({ timeout: 12_000 })
    await expect(stimulus).toHaveAttribute('data-trial-number', String(trial))
    ids.add((await stimulus.getAttribute('data-condition-id'))!)
    const condition = (await stimulus.getAttribute('data-condition'))!
    if (!responded.has(condition)) {
      responded.add(condition)
      await page.keyboard.press('Space')
      await expect(stimulus).toBeVisible()
    }
    outcomes.add(await feedbackOutcome(page))
  }
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toBeVisible()
  expect([...ids].sort()).toEqual(['1', '2', '3', '4'])
  expect([...outcomes].sort()).toEqual(['commission', 'correct_rejection', 'hit', 'omission'])
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })))
    .toEqual({ local: 0, session: 0 })
  await page.keyboard.press('r')
  await expect(page.locator('[data-phase="reminder"]')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toHaveCount(0)
  await page.keyboard.press('Escape')
  await expect(page.getByRole('alert')).toContainText('treino foi interrompido')
})

test('tecla mantida da navegacao nao responde e interrupcao descarta a rodada', async ({ page }) => {
  test.setTimeout(30_000)
  await prepare(page)
  await page.keyboard.down('Space')
  await page.getByRole('button', { name: 'Começar prática', exact: true }).click()
  const stimulus = page.locator('[data-phase="stimulus"]')
  await expect(stimulus).toBeVisible({ timeout: 12_000 })
  const kind = await stimulus.getAttribute('data-condition')
  await page.keyboard.down('Space')
  expect(await feedbackOutcome(page)).toBe(kind === 'congruent' ? 'omission' : 'correct_rejection')
  await page.keyboard.up('Space')
  await page.keyboard.press('Escape')
  await expect(page.getByRole('alert')).toContainText('rodada completa')
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toHaveCount(0)
  await page.getByRole('button', { name: 'Recomeçar prática' }).click()
  await expect(page.locator('[data-phase="reminder"]')).toBeVisible()
  await page.evaluate(() => window.dispatchEvent(new Event('blur')))
  await expect(page.getByRole('alert')).toContainText('treino foi interrompido')
})

test.describe('dispositivo fora do MVP', () => {
  test.use({ userAgent: 'Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 Chrome/155.0.0.0 Mobile Safari/537.36' })
  test('bloqueia celular antes de qualquer pratica', async ({ page }) => {
    await page.goto('/pratica')
    await expect(page.getByRole('alert')).toContainText('computador Windows ou Linux')
    await expect(page.getByRole('button', { name: 'Começar prática', exact: true })).toHaveCount(0)
    await expect(page.locator('[data-phase]')).toHaveCount(0)
  })
})
