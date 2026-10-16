import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'

async function finishPractice(page: Page) {
  await page.goto('/pratica')
  await page.getByLabel('Estou usando um computador ou notebook com teclado físico.').check()
  await page.getByRole('main').focus()
  await page.keyboard.press('Space')
  await page.getByRole('button', { name: 'Começar prática', exact: true }).click()
  // Sem desempenho minimo: uma rodada completa, mesmo sem responder, habilita principal.
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toBeVisible({ timeout: 22_000 })
}

test('principal executa 16 condicoes reais sem feedback nem encurtar resposta', { tag: '@timing' }, async ({ page }) => {
  test.setTimeout(100_000)
  await finishPractice(page)
  await page.keyboard.down('Space')
  await page.getByRole('button', { name: 'Começar bloco principal' }).click()
  const ids: number[] = []
  const kinds: string[] = []
  for (let trial = 1; trial <= 16; trial += 1) {
    const observed = await page.waitForFunction(index => {
      if (document.querySelector('h1')?.textContent === 'Execução interrompida.') {
        const temporal = document.querySelector('main')?.textContent?.includes('tempos de apresentação')
        throw new Error(temporal ? 'Gate temporal interrompeu o principal.' : 'Principal interrompido.')
      }
      const element = document.querySelector('[data-phase="stimulus"]')
      if (element?.getAttribute('data-trial-number') !== String(index)) return null
      return { id: Number(element.getAttribute('data-condition-id')), kind: element.getAttribute('data-condition') }
    }, trial, { polling: 'raf', timeout: 8_000 })
    const condition = await observed.jsonValue()
    ids.push(condition!.id)
    kinds.push(condition!.kind!)
    await expect(page.locator('[data-phase="feedback"]')).toHaveCount(0)
    await expect(page.getByText('ESPAÇO apenas quando combinar', { exact: true })).toHaveCount(0)
    if (trial === 1) await page.keyboard.up('Space')
    else if (trial <= 3) {
      await page.keyboard.press('Space')
      await expect(page.locator('[data-phase="stimulus"]')).toBeVisible()
    }
  }
  await expect(page.getByRole('heading', { name: 'Bloco concluído.' })).toBeVisible({ timeout: 5_000 })
  expect(ids.sort((a, b) => a - b)).toEqual(Array.from({ length: 16 }, (_, i) => i + 1))
  expect(kinds.filter(kind => kind === 'congruent')).toHaveLength(8)
  expect(kinds.filter(kind => kind === 'incongruent')).toHaveLength(8)
  await expect(page.getByText('Você concluiu as 16 tentativas principais.')).toBeVisible()
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })))
    .toEqual({ local: 0, session: 0 })
})

test('Escape no principal descarta execucao e exige nova sessao com pratica', { tag: '@timing' }, async ({ page }) => {
  test.setTimeout(35_000)
  await finishPractice(page)
  await page.getByRole('button', { name: 'Começar bloco principal' }).click()
  await expect(page.locator('[data-phase="stimulus"]')).toBeVisible({ timeout: 8_000 })
  await page.keyboard.press('Escape')
  await expect(page.getByRole('heading', { name: 'Execução interrompida.' })).toBeVisible()
  await expect(page.getByRole('alert')).toContainText('nova sessão e fazer a prática novamente')
  await expect(page.getByRole('button', { name: 'Começar bloco principal' })).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Bloco concluído.' })).toHaveCount(0)
})
