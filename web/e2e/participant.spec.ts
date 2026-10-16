import { expect, test } from '@playwright/test'
import { mockParticipant } from './support/participant'

test('convite e obrigatorio, codigo fica mascarado e duplo clique nao duplica resgate', async ({ page }) => {
  await mockParticipant(page, 'none')
  let redeems = 0
  page.on('request', request => { if (new URL(request.url()).pathname.endsWith('/participant/redeem')) redeems += 1 })
  await page.goto('/pratica')
  const code = page.getByLabel('Código do convite')
  await expect(code).toHaveAttribute('type', 'password')
  await expect(page.getByRole('button', { name: 'Começar prática', exact: true })).toHaveCount(0)
  await code.fill('invalido')
  await page.getByRole('button', { name: 'Validar convite' }).click()
  await expect(page.getByRole('alert')).toContainText('Confira o código')
  expect(redeems).toBe(0)
  await code.fill('c'.repeat(43))
  await page.getByRole('button', { name: 'Validar convite' }).evaluate((button: HTMLButtonElement) => {
    button.click(); button.click()
  })
  await expect(page.getByRole('heading', { name: 'Vamos praticar primeiro.' })).toBeVisible()
  expect(redeems).toBe(1)
  await expect(page).toHaveURL('/pratica')
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })))
    .toEqual({ local: 0, session: 0 })
})

test('trava nativa impede outra aba de obter a mesma sessao e libera ao fechar', async ({ page, context }) => {
  await mockParticipant(page)
  await page.goto('/pratica')
  await expect(page.getByRole('heading', { name: 'Vamos praticar primeiro.' })).toBeVisible()
  const other = await context.newPage()
  await mockParticipant(other)
  let reads = 0
  other.on('request', request => { if (new URL(request.url()).pathname.endsWith('/participant/session')) reads += 1 })
  await other.goto('/pratica')
  await expect(other.getByRole('alert')).toContainText('outra aba')
  expect(reads).toBe(0)
  await page.close()
  await other.getByRole('button', { name: 'Verificar novamente' }).click()
  await expect(other.getByRole('heading', { name: 'Vamos praticar primeiro.' })).toBeVisible()
  expect(reads).toBe(1)
  await other.close()
})

test('bootstrap running aborta reload e nao reconstrui motor pelo servidor', async ({ page }) => {
  await mockParticipant(page, 'running')
  let reason: unknown
  page.on('request', request => {
    if (new URL(request.url()).pathname.endsWith('/participant/abort')) reason = request.postDataJSON().reason
  })
  await page.goto('/pratica')
  await expect(page.getByRole('alert')).toContainText('execução anterior foi interrompida')
  await expect.poll(() => reason).toBe('reload')
  await expect(page.locator('[data-phase]')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Começar bloco principal' })).toHaveCount(0)
})
