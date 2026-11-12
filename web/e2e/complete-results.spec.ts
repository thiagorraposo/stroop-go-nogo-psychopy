/** W15B: UI com respostas sinteticas; integracao real tem suite propria. */
import { expect, test } from '@playwright/test'
const project = '11111111-1111-4111-8111-111111111111'
const base = `/api/v1/projects/${project}/assessments`
const summary = { accuracy: 50, accuracy_go_trials: 0, accuracy_no_go_trials: 100, total_go_trials: 8, total_no_go_trials: 8,
  response_time_seconds: null, total_trials: 16, hits: 0, correct_rejections: 8, omission_errors: 8, commission_errors: 0 }
const stroop = { assessment_id: 'SYNTHETIC_NO_HITS', participant_id: 'P_SINTETICO', visit: 'V1', evaluator_id: null,
  created_at: '2026-10-16T12:00:00Z', started_at: '2026-10-16T12:00:00Z', platform: 'psychopy',
  test_code: 'stroop_go_nogo_ptbr', test_version: '1.0', protocol_id: null, app_version: null, summary }
const demo = { ...stroop, assessment_id: 'SYNTHETIC_DEMO', test_code: 'instrumento_sintetico_demo', summary: { metrics: { demo_total: 4, demo_mean: 2.5 } } }

test('tabela completa e detalhe preservam Go/No-Go e ausencia de RT sem acertos', async ({ page }) => {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { user_id: 'synthetic', role: 'consulta', csrf_token: 's'.repeat(43), expires_at: new Date(Date.now() + 3600000).toISOString() } }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [{ id: project, code: 'SYNTHETIC_W15B', name: 'Pesquisa sintetica', active: true, created_at: stroop.created_at }], next_cursor: null } }))
  await page.route(`**${base}/options*`, route => route.fulfill({ json: { participant_id: ['P_SINTETICO'], visit: ['V1'], evaluator_id: ['LEGADO_NAO_MAPEADO'], test_version: ['1.0'], platform: ['psychopy'], test_code: [stroop.test_code, demo.test_code] } }))
  await page.route(`**${base}?*`, route => route.fulfill({ json: { items: [stroop, demo].filter(row => !new URL(route.request().url()).searchParams.get('test_code') || row.test_code === new URL(route.request().url()).searchParams.get('test_code')), next_cursor: null } }))
  await page.route(`**${base}/${stroop.assessment_id}`, route => route.fulfill({ json: { ...stroop, project_id: project, session_id: null,
    completed_at: null, frame_period_ms: null, metrics: [
      { metric_code: 'accuracy_go_trials', metric_label: 'Precisão Go', metric_value: 0, unit: '%' },
      { metric_code: 'accuracy_no_go_trials', metric_label: 'Precisão No-Go', metric_value: 100, unit: '%' },
      { metric_code: 'response_time', metric_label: 'Tempo de resposta', metric_value: null, unit: 'seconds' }], trials: [] } }))
  await page.goto('/equipe')
  await page.getByRole('listbox', { name: 'Instrumento da consulta', exact: true }).selectOption(stroop.test_code)
  await page.getByRole('button', { name: 'Aplicar filtros' }).click()
  const table = page.getByRole('table', { name: 'Avaliações filtradas' })
  await expect(table.locator('tbody tr')).toHaveCount(1)
  for (const label of ['Avaliador', 'Precisão Go (%)', 'Precisão No-Go (%)', 'Omissões', 'Comissões', 'Acertos', 'Rejeições corretas']) {
    await expect(table.getByRole('columnheader', { name: label, exact: true })).toBeVisible()
  }
  await expect(table.locator('tbody tr')).toContainText('100,0')
  await expect(table.locator('tbody tr')).toContainText('—')
  await page.getByRole('button', { name: 'Ver avaliação P_SINTETICO, visita V1' }).click()
  const detail = page.getByRole('region', { name: 'Detalhe da avaliação' })
  await expect(detail).toBeFocused()
  await expect(detail).toContainText(stroop.assessment_id)
  await expect(detail).toContainText(project)
  await expect(detail).toContainText('Legado sem identificação técnica')
  await expect(detail).toContainText('—')
  await page.getByRole('button', { name: 'Fechar detalhe', exact: true }).click()
  await page.getByRole('listbox', { name: 'Instrumento da consulta', exact: true }).selectOption(demo.test_code)
  await page.getByRole('button', { name: 'Aplicar filtros' }).click()
  await expect(page.getByRole('table', { name: 'Métricas por instrumento e avaliação' })).toContainText('2,500')
  await expect(page.getByRole('table', { name: 'Métricas por instrumento e avaliação' })).toContainText('4')
  await expect(page.getByText('Precisão média', { exact: true })).toHaveCount(0)
})
