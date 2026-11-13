import { analysisFixture } from '../src/test/analysis-fixture'
import { expect, test } from '@playwright/test'

const projectId = '11111111-1111-4111-8111-111111111111'
const project = { id: projectId, code: 'SYNTHETIC_IMPORT', name: 'Pesquisa sintetica', active: true,
  created_at: '2026-10-16T12:00:00Z' }
const profile = { user_id: 'c3ludGhldGljLXVzZXI', role: 'administracao',
  expires_at: new Date(Date.now() + 3_600_000).toISOString(), csrf_token: 's'.repeat(43) }

async function access(page: import('@playwright/test').Page) {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: profile }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [project], next_cursor: null } }))
  await page.route('**/api/v1/projects/*/assessments/options*', route => route.fulfill({ json: {
    participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: ['psychopy'],
    test_code: ['stroop_go_nogo_ptbr'],
  } }))
  await page.route('**/api/v1/analysis/query', route => route.fulfill({ json: analysisFixture(route.request().postDataJSON(), []) }))
}

test('EXP-CSV-01: comprova ausencia de painel e comandos de importacao CSV na UI do produto', async ({ page }) => {
  await access(page)
  await page.goto('/equipe')

  // Verifica que o painel de importacao CSV foi completamente retirado da interface
  await expect(page.locator('.csv-import-panel')).toHaveCount(0)
  await expect(page.getByRole('button', { name: /importar csv/i })).toHaveCount(0)
  await expect(page.getByLabel(/Arquivo CSV/i)).toHaveCount(0)
  await expect(page.getByText('Importar CSV')).toHaveCount(0)
})

test('EXP-CSV-01: nenhuma rota de importacao CSV e disparada na navegacao operacional', async ({ page }) => {
  let importCalled = false
  await page.route('**/api/v1/projects/*/imports/**', route => {
    importCalled = true
    return route.fulfill({ status: 410, json: { error: { code: 'csv_import_disabled' } } })
  })
  await access(page)
  await page.goto('/equipe')

  // Garante que o fluxo padrao nao dispara nenhuma chamada de importacao CSV
  expect(importCalled).toBe(false)
  await expect(page.locator('.csv-import-panel')).toHaveCount(0)
})
