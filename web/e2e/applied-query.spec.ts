import { analysisFixture } from '../src/test/analysis-fixture'
/** QUERY7: navegador real e HTTP sintético; integração real usa suíte separada. */
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
const id = '11111111-1111-4111-8111-111111111111'
const base = `/api/v1/projects/${id}/assessments`
const row = { assessment_id: 'SYNTHETIC_QUERY7', participant_id: 'P_SINTETICO', visit: 'V1', evaluator_id: null,
  created_at: '2026-11-11T12:00:00Z', started_at: '2026-11-11T12:00:00Z', platform: 'web' as const, test_code: 'stroop_go_nogo_ptbr', test_version: '1', protocol_id: null, app_version: null,
  summary: { accuracy: 75, accuracy_go_trials: 75, accuracy_no_go_trials: 75, total_go_trials: 8, total_no_go_trials: 8, response_time_seconds: 0.625, total_trials: 16, hits: 6, correct_rejections: 6, omission_errors: 2, commission_errors: 2 } }
async function access(page: Page) {
  await page.route('**/api/v1/auth/me', r => r.fulfill({ json: { user_id: 'synthetic', role: 'consulta', csrf_token: 's'.repeat(43), expires_at: new Date(Date.now() + 3600000).toISOString() } }))
  await page.route('**/api/v1/projects?*', r => r.fulfill({ json: { items: [{ id, code: 'QUERY7', name: 'Sintético', active: true, created_at: row.created_at }], next_cursor: null } }))
  await page.route(`**${base}/options*`, r => r.fulfill({ json: { participant_id: ['P_SINTETICO'], visit: ['V1'], evaluator_id: [], test_version: ['1'], platform: ['web'], test_code: [row.test_code] } }))
  await page.route('**/api/v1/analysis/query', r => r.fulfill({ json: analysisFixture(r.request().postDataJSON(), [row]) }))
  await page.goto('/equipe')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toContainText('P_SINTETICO')
}
const apply = (page: Page) => page.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()

test('rascunho, chips, limpar e descartar mantêm contexto entre módulos e bloqueiam download', async ({ page }) => {
  await access(page)
  const download = page.getByRole('button', { name: 'Exportar visão filtrada', exact: true })
  await expect(download).toBeEnabled()
  await page.getByLabel('Data inicial', { exact: true }).fill('2026-11-01')
  await expect(download).toBeDisabled()
  await page.getByRole('button', { name: 'Avaliações e histórico', exact: true }).click()
  await expect(page.getByLabel('Data inicial', { exact: true })).toHaveValue('2026-11-01')
  await apply(page)
  await page.getByRole('button', { name: 'Resultados e análises', exact: true }).click()
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('2026-11-01')
  await page.getByRole('button', { name: /^Remover filtro Período:/ }).click()
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('2026-11-01')
  await page.getByRole('button', { name: 'Descartar alterações', exact: true }).click()
  await expect(page.getByLabel('Data inicial', { exact: true })).toHaveValue('2026-11-01')
  await page.getByRole('button', { name: 'Exportações', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Pré-visualizar contagem e amostra' })).toBeDisabled()
  await page.getByRole('button', { name: 'Limpar filtros', exact: true }).click()
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('2026-11-01')
  await apply(page)
  await page.getByRole('button', { name: 'Visão geral (Dashboard)', exact: true }).click()
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('sem restrições adicionais')
  await expect(download).toBeEnabled()
})

test('recorte avançado não exporta conjunto maior; buscar opções não perde seleção', async ({ page }) => {
  await access(page)
  let exports = 0
  await page.route('**/api/v1/assessments/export', r => { exports++; return r.abort() })
  await page.getByText('Filtros avançados e ordenação', { exact: true }).click()
  await page.getByRole('listbox', { name: 'Participantes (códigos)', exact: true }).selectOption('P_SINTETICO')
  await page.getByRole('searchbox', { name: 'Buscar opções de participantes (códigos)', exact: true }).fill('SEM_CORRESPONDENCIA')
  await expect(page.getByRole('listbox', { name: 'Participantes (códigos)', exact: true })).toHaveValues(['P_SINTETICO'])
  await page.getByRole('listbox', { name: 'Instrumento da consulta', exact: true }).selectOption(row.test_code)
  await page.getByRole('combobox', { name: 'Faixa de precisão', exact: true }).selectOption('50to80')
  await apply(page)
  await expect(page.getByRole('button', { name: 'Exportar visão filtrada', exact: true })).toBeDisabled()
  await expect(page.getByText(/nenhum arquivo sem esses filtros/)).toBeVisible()
  expect(exports).toBe(0)
})

for (const failure of ['snapshot', 'revogacao', 'logout']) {
  test(`${failure}: limpa resultados; voltar/avançar não recupera dados após encerrar acesso`, async ({ page }) => {
    await access(page)
    if (failure === 'logout') {
      await page.route('**/api/v1/auth/logout', r => r.fulfill({ status: 204 }))
      await page.getByRole('button', { name: 'Encerrar sessão', exact: true }).click()
    } else {
      await page.route('**/api/v1/analysis/query', r => r.fulfill({ status: failure === 'snapshot' ? 409 : 403,
        json: { error: { code: failure === 'snapshot' ? 'state_conflict' : 'permission_denied' } } }))
      await apply(page)
    }
    await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toHaveCount(0)
    await expect(page.locator('.dashboard-cards')).toHaveCount(0)
    if (failure === 'snapshot') {
      await expect(page.getByRole('alert')).toContainText('nenhum total parcial')
      await page.getByRole('button', { name: 'Resultados e análises', exact: true }).click()
      await expect(page.locator('.dashboard-cards')).toHaveCount(0)
    } else {
      await page.route('**/api/v1/auth/me', r => r.fulfill({ status: 401, json: { error: { code: 'authentication_required' } } }))
      await expect(page.getByRole('button', { name: 'Entrar', exact: true })).toBeVisible()
      await page.getByRole('link', { name: 'Participação', exact: true }).click()
      await page.goBack()
      await expect(page.getByRole('button', { name: 'Entrar', exact: true })).toBeVisible()
      await page.goForward(); await page.goBack()
      await expect(page.getByRole('main')).not.toContainText('P_SINTETICO')
    }
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
    expect(page.url()).not.toContain('P_SINTETICO')
  })
}
