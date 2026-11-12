/** W15C: navegador com HTTP sintetico; suite integrated prova backend real. */
import { readFile } from 'node:fs/promises'
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
const project = '11111111-1111-4111-8111-111111111111'
const snapshot = 'a'.repeat(64)
const base = `/api/v1/projects/${project}/assessments`
const endpoint = '**/api/v1/assessments/export'
const csrf = 's'.repeat(43)
const assessment = { assessment_id: 'SYNTHETIC_EXPORT', participant_id: 'P_SINTETICO', visit: 'V1', evaluator_id: null,
  created_at: '2026-10-16T12:00:00Z', started_at: '2026-10-16T12:00:00Z', platform: 'web', test_code: 'stroop_go_nogo_ptbr',
  test_version: '1.0', protocol_id: 'synthetic', app_version: '1.0', summary: { accuracy: 75, accuracy_go_trials: 75,
    accuracy_no_go_trials: 75, total_go_trials: 8, total_no_go_trials: 8, response_time_seconds: 0.625,
    total_trials: 16, hits: 6, correct_rejections: 6, omission_errors: 2, commission_errors: 2 } }
async function access(page: Page, role = 'consulta') {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { user_id: 'synthetic', role, csrf_token: csrf, expires_at: new Date(Date.now() + 3600000).toISOString() } }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [{ id: project, code: 'SYNTHETIC_EXPORT', name: 'Pesquisa sintetica', active: true, created_at: assessment.created_at }], next_cursor: null } }))
  await page.route(`**${base}/options*`, route => route.fulfill({ json: { participant_id: ['P_SINTETICO'], visit: ['V1'], evaluator_id: [], test_version: ['1.0'], platform: ['web'], test_code: [assessment.test_code] } }))
  await page.route(`**${base}?*`, route => route.fulfill({ headers: { 'X-Assessment-Snapshot': snapshot }, json: { items: [assessment], next_cursor: null } }))
  await page.goto('/equipe')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' }).locator('tbody tr')).toHaveCount(1)
}
for (const role of ['consulta', 'importacao', 'administracao']) {
  test(`${role} exporta manualmente snapshot autorizado sem token em URL ou storage`, async ({ page }) => {
    await access(page, role)
    await page.route(endpoint, async route => {
      const request = route.request()
      expect(request.method()).toBe('POST')
      expect(request.headers()['x-csrf-token']).toBe(csrf)
      expect(request.url()).not.toContain(snapshot)
      expect(request.postDataJSON()).toMatchObject({ projects: [{ project_id: project, snapshot }], filters: {}, view: { test_code: assessment.test_code } })
      return route.fulfill({ headers: { 'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': 'attachment; filename="stroop_go_nogo_ptbr_avaliacoes.csv"', 'Cache-Control': 'no-store' }, body: 'assessment_id,participant_id\r\nSYNTHETIC_EXPORT,P_SINTETICO\r\n' })
    })
    const downloading = page.waitForEvent('download')
    await page.getByRole('button', { name: 'Exportar visão filtrada', exact: true }).focus()
    await page.keyboard.press('Enter')
    const download = await downloading
    const path = await download.path()
    expect(path).not.toBeNull()
    expect(await readFile(path!, 'utf8')).toContain('SYNTHETIC_EXPORT,P_SINTETICO')
    expect(page.url()).not.toContain(snapshot)
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
    await expect(page.getByRole('main')).not.toContainText(csrf)
  })
}
for (const failure of ['conflict', 'permission', 'network']) {
  test(`falha ${failure} nao gera download ou repete POST automaticamente`, async ({ page }) => {
    await access(page)
    let count = 0, downloads = 0
    page.on('download', () => downloads++)
    await page.route(endpoint, route => {
      count++
      return failure === 'network' ? route.abort('failed') : route.fulfill({ status: failure === 'conflict' ? 409 : 403,
        json: { error: { code: failure === 'conflict' ? 'state_conflict' : 'permission_denied' } } })
    })
    await page.getByRole('button', { name: 'Exportar visão filtrada', exact: true }).click()
    if (failure === 'network') await expect(page.getByRole('button', { name: 'Exportar visão filtrada', exact: true })).toBeEnabled()
    else await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toHaveCount(0)
    if (failure === 'permission') await expect(page.getByRole('button', { name: 'Entrar', exact: true })).toBeVisible()
    else await expect(page.getByRole('main')).toContainText(/alterad|permite|conexão|disponível|novamente|atualiz/i)
    expect(count).toBe(1); expect(downloads).toBe(0)
  })
}

test('troca de consulta cancela exportacao antiga sem iniciar download atrasado', async ({ page }) => {
  await access(page)
  let start!: () => void, release!: () => void, downloads = 0
  const started = new Promise<void>(resolve => { start = resolve }), gate = new Promise<void>(resolve => { release = resolve })
  page.on('download', () => downloads++)
  await page.route(endpoint, async route => {
    start(); await gate
    await route.fulfill({ headers: { 'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename="stroop_go_nogo_ptbr_avaliacoes.csv"' }, body: 'synthetic\r\n' }).catch(() => undefined)
  })
  await page.getByRole('button', { name: 'Exportar visão filtrada', exact: true }).click()
  await started
  await page.getByLabel('Data inicial', { exact: true }).fill('2026-01-01')
  release()
  await expect(page.getByRole('button', { name: 'Exportar visão filtrada', exact: true })).toBeDisabled()
  await page.getByRole('button', { name: 'Descartar alterações' }).click()
  await expect(page.getByRole('button', { name: 'Exportar visão filtrada', exact: true })).toBeEnabled()
  expect(downloads).toBe(0)
})
