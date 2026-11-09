/** EXP-CSV-01: Verificacao integrada de ausencia de upload CSV e bloqueio 410 no modo produto por HTTPS real. */
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { randomUUID } from 'node:crypto'
import { expect, test } from '@playwright/test'

const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const manageScript = fileURLToPath(new URL('./dashboard-manage.py', import.meta.url))
type Prepared = { cookie_name: string; token: string; csrf: string; project_id: string }

test('EXP-CSV-01: comprova ausencia de upload CSV na UI e bloqueio 410 no backend integrado', async ({ page, context }) => {
  const prepared = JSON.parse(execFileSync(python, [manageScript], {
    input: JSON.stringify({ role: 'administracao' }), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'],
  })) as Prepared
  await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1', path: '/',
    secure: true, httpOnly: true, sameSite: 'Lax' }])

  // 1. Navega para /equipe e seleciona o projeto
  await page.goto('/equipe')
  await page.getByLabel('Projeto', { exact: true }).selectOption(prepared.project_id)

  // 2. Comprova ausencia completa de painel, formulario ou botao de importacao CSV
  await expect(page.locator('.csv-import-panel')).toHaveCount(0)
  await expect(page.getByRole('button', { name: /importar csv/i })).toHaveCount(0)
  await expect(page.getByLabel(/Arquivo CSV/i)).toHaveCount(0)
  await expect(page.getByText('Importar CSV')).toHaveCount(0)

  // 3. Requisicao direta ao endpoint de importacao pelo cliente HTTPS comprova bloqueio 410 Gone
  const operationId = randomUUID()
  const response = await page.request.post(`/api/v1/projects/${prepared.project_id}/imports/${operationId}`, {
    data: 'project,participant_id\nPROJ,P1\n',
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'X-CSRF-Token': prepared.csrf,
      Origin: new URL(page.url()).origin,
    },
  })
  expect(response.status()).toBe(410)
  const body = await response.json()
  expect(body.error.code).toBe('csv_import_disabled')
})
