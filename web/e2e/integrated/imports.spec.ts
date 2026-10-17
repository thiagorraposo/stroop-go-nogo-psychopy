/** Fluxo de importacao real por HTTPS, API, PostgreSQL e papeis WEB. */
import { execFileSync } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { randomUUID } from 'node:crypto'
import { expect, test } from '@playwright/test'

const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const manageScript = fileURLToPath(new URL('./dashboard-manage.py', import.meta.url))
const fixturePath = fileURLToPath(new URL('../../../tests/fixtures/web_results_summary.json', import.meta.url))
type Prepared = { cookie_name: string; token: string; project_id: string }

test('importa CSV redigido, consulta, abre detalhe e exporta pelo fluxo real', async ({ page, context }) => {
  const prepared = JSON.parse(execFileSync(python, [manageScript], {
    input: JSON.stringify({ role: 'importacao' }), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'],
  })) as Prepared
  await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1', path: '/',
    secure: true, httpOnly: true, sameSite: 'Lax' }])

  const fixture = JSON.parse(await readFile(fixturePath, 'utf8')) as { cases: Array<{ name: string; expected_csv: string }> }
  const csv = fixture.cases.find(item => item.name !== 'sem-hits')!.expected_csv
  const assessmentId = randomUUID()
  const upload = csv.replaceAll('00000000-0000-4000-8000-000000000120', assessmentId)
    .replaceAll('P_SINTETICO,NAO_COLETADO,,V_SINTETICA', 'P_SINTETICO_UPLOAD,NAO_COLETADO,,V_UPLOAD')

  await page.goto('/equipe')
  await page.getByLabel('Projeto', { exact: true }).selectOption(prepared.project_id)
  const panel = page.locator('.csv-import-panel')
  await panel.getByLabel('Arquivo CSV (até 5 MiB)').setInputFiles({
    name: 'dados-sinteticos.csv', mimeType: 'text/csv', buffer: Buffer.from(upload),
  })
  await panel.getByRole('button', { name: 'Minimizar e importar CSV' }).click()
  await expect(panel.getByRole('status')).toContainText('Importação concluída', { timeout: 15_000 })

  const results = page.getByRole('table', { name: 'Avaliações filtradas' })
  await expect(results).toContainText('P_SINTETICO_UPLOAD')
  await page.getByRole('button', { name: 'Ver avaliação P_SINTETICO_UPLOAD, visita V_UPLOAD' }).click()
  const detail = page.getByRole('region', { name: 'Detalhe da avaliação' })
  await expect(detail.getByRole('table', { name: 'Tentativas registradas' }).locator('tbody tr')).toHaveCount(16)
  const downloadPromise = page.waitForEvent('download')
  await detail.getByRole('button', { name: 'Exportar CSV oficial' }).click()
  const download = await downloadPromise
  const path = await download.path()
  expect(path).not.toBeNull()
  const exported = await readFile(path!, 'utf8')
  expect(exported.trim().split(/\r?\n/)).toHaveLength(17)
  expect(exported).toContain('P_SINTETICO_UPLOAD')
  expect(exported).toContain('NAO_COLETADO,,V_UPLOAD')
})
