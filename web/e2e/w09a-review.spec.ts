/** Percurso sintetico para validar hierarquia visual sem instrumentar a tarefa. */
import { expect, test } from '@playwright/test'
import { mockParticipant } from './support/participant'

test('capturas sinteticas do tutorial, convite, pratica e encerramento', async ({ page, browserName }) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/')
  await expect(page.getByRole('link', { name: 'Iniciar tutorial' })).toBeVisible()
  await page.screenshot({ path: `/tmp/stroop-w09a-after-home-${browserName}.png`, fullPage: true })

  await page.getByRole('link', { name: 'Iniciar tutorial' }).click()
  await expect(page.getByRole('list', { name: 'Como responder' }).getByRole('listitem')).toHaveCount(3)
  await page.screenshot({ path: `/tmp/stroop-w09a-after-instructions-${browserName}.png`, fullPage: true })

  await mockParticipant(page, 'none')
  await page.getByRole('link', { name: 'Ir para a prática' }).click()
  await page.getByLabel('Código do convite').fill('c'.repeat(43))
  await page.getByRole('button', { name: 'Validar convite' }).click()
  await expect(page.getByRole('heading', { name: 'Primeiro, vamos praticar.' })).toBeVisible()
  await page.screenshot({ path: `/tmp/stroop-w09a-after-preparation-${browserName}.png`, fullPage: true })

  await page.getByLabel('Estou usando um computador ou notebook com teclado físico.').check()
  await page.getByRole('main').focus()
  await page.keyboard.press('Space')
  await page.getByRole('button', { name: 'Começar prática' }).click()
  await expect(page.getByRole('list', { name: 'Etapas da participação' })).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toBeVisible({ timeout: 22_000 })
  await page.screenshot({ path: `/tmp/stroop-w09a-after-practice-summary-${browserName}.png`, fullPage: true })
  await page.close()

  const resultPage = await page.context().browser()!.newPage()
  await mockParticipant(resultPage, 'completed')
  await resultPage.setViewportSize({ width: 1440, height: 1000 })
  await resultPage.goto('/pratica')
  await expect(resultPage.getByText('Tarefa concluída. Obrigado por participar.')).toBeVisible()
  await resultPage.screenshot({ path: `/tmp/stroop-w09a-after-result-${browserName}.png`, fullPage: true })
  await resultPage.getByRole('button', { name: 'Finalizar', exact: true }).click()
  await expect(resultPage.getByRole('heading', { name: 'Participação encerrada.' })).toBeVisible()
  await resultPage.screenshot({ path: `/tmp/stroop-w09a-after-closed-${browserName}.png`, fullPage: true })
  await resultPage.close()
})
