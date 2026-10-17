/** Doubles HTTP sinteticos: UI profissional, sem reivindicar integracao real. */
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import type { Assessment, AssessmentDetail } from '../src/api/assessments'
const projectId = '11111111-1111-4111-8111-111111111111'
const project = { id: projectId, code: 'SYNTHETIC_DASHBOARD', name: 'Pesquisa sintetica', active: true, created_at: '2026-10-16T12:00:00Z' }
const base = `/api/v1/projects/${projectId}/assessments`
const profile = { user_id: 'c3ludGhldGljLXVzZXI', expires_at: new Date(Date.now() + 3_600_000).toISOString(), csrf_token: 's'.repeat(43) }
function row(id: string, platform: 'web' | 'psychopy' = 'web'): Assessment {
  return { assessment_id: id, participant_id: `P_SINTETICO_${id}`, visit: 'V1', evaluator_id: null,
    created_at: '2026-10-16T12:00:00Z', started_at: '2026-10-16T12:00:00Z', platform,
    test_code: 'stroop_go_nogo_ptbr', test_version: '1.0.0', protocol_id: platform === 'web' ? 'synthetic-v1' : null,
    app_version: platform === 'web' ? 'web-0.1.0' : null,
    summary: { accuracy: 75, accuracy_go_trials: 75, accuracy_no_go_trials: 75, total_go_trials: 8, total_no_go_trials: 8, response_time_seconds: 0.625, total_trials: 16, hits: 6, correct_rejections: 6, omission_errors: 2, commission_errors: 2 } }
}
const first = row('web1'), second = row('local2', 'psychopy')
const generic: Assessment = { ...row('generic3'), test_code: 'teste_sintetico', summary: { metrics: { pontos: 999 } } }
const detail: AssessmentDetail = { ...first, project_id: projectId, session_id: '22222222-2222-4222-8222-222222222222',
  completed_at: '2026-10-16T12:01:00Z', frame_period_ms: 16.666,
  metrics: [{ metric_code: 'accuracy', metric_label: 'Precisão', metric_value: 75, unit: '%' }],
  trials: [{ trial_number: 1, condition_id: 1, word: 'AZUL', ink_color: 'azul', condition: 'congruent',
    correct_response: 'space', key_pressed: 'space', correct: true, error_type: 'hit', trial_start_ms: 0,
    stimulus_onset_ms: 300, stimulus_offset_ms: 2800, trial_end_ms: 3750, key_at_ms: 925,
    reaction_time_ms: 625, reaction_time_seconds: 0.625 }] }
async function access(page: Page, role = 'consulta') {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { ...profile, role } }))
  await page.route('**/api/v1/projects/*/assessments/options*', route => route.fulfill({ json: { participant_id: ['P_SINTETICO_AUSENTE'], visit: ['V2'], evaluator_id: [], test_version: [], platform: ['web', 'psychopy'], test_code: ['stroop_go_nogo_ptbr', 'teste_sintetico'] } }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [project], next_cursor: null } }))
}
function card(page: Page, title: string) {
  return page.locator('.dashboard-cards > div').filter({ has: page.getByText(title, { exact: true }) }).locator('dd')
}
for (const [role, label] of [['consulta', 'Consulta'], ['importacao', 'Coleta e importação'], ['administracao', 'Administração']]) {
  test(`perfil ${role} consulta metricas de referencia`, async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.name))
    await access(page, role)
    await page.route(`**${base}?*`, route => route.fulfill({ json: { items: [first, second], next_cursor: null } }))
    await page.goto('/equipe')
    await expect(page.getByText(label!, { exact: true })).toBeVisible()
    await expect(card(page, 'Avaliações')).toHaveText('2')
    await expect(card(page, 'Participantes únicos')).toHaveText('2')
    await expect(card(page, 'Precisão média')).toHaveText('75,0%')
    await expect(card(page, 'Precisão mediana')).toHaveText('75,0%')
    await expect(card(page, 'Mediana dos tempos por avaliação')).toHaveText('0,625 s')
    await expect(card(page, 'Omissões')).toHaveText('4')
    await expect(card(page, 'Comissões')).toHaveText('4')
    await expect(page.getByRole('meter', { name: '2026-10-16: 2 avaliações' })).toBeVisible()
    await expect(page.getByRole('main')).toContainText('não representa avaliação clínica ou diagnóstico')
    if (role === 'consulta') {
      await page.screenshot({ path: '/tmp/stroop-w15-dashboard.png', fullPage: true })
      await page.setViewportSize({ width: 390, height: 844 })
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
      await page.screenshot({ path: '/tmp/stroop-w15-dashboard-mobile.png', fullPage: true })
    }
    expect(errors).toEqual([])
    await expect(page.getByRole('main')).not.toContainText(profile.csrf_token)
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
  })
}
test('aguarda todas as paginas e descarta subconjunto em falha', async ({ page }) => {
  await access(page)
  let release!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  let fail = false
  await page.route(`**${base}?*`, async route => {
    const cursor = new URL(route.request().url()).searchParams.get('cursor')
    if (!cursor) return route.fulfill({ json: { items: [first], next_cursor: 'synthetic_next' } })
    expect(cursor).toBe('synthetic_next'); await gate
    return fail ? route.fulfill({ status: 403, json: { error: { code: 'permission_denied', message: 'SYNTHETIC_SECRET' } } })
      : route.fulfill({ json: { items: [second], next_cursor: null } })
  })
  await page.goto('/equipe')
  await expect(page.getByText(/^Carregando avaliações/)).toContainText('1 recebidas')
  await expect(page.locator('.dashboard-cards')).toHaveCount(0)
  release(); await expect(card(page, 'Avaliações')).toHaveText('2')
  fail = true; await page.getByRole('button', { name: 'Aplicar filtros' }).click()
  await expect(page.getByRole('alert')).toHaveText('Seu perfil não permite esta operação.')
  await expect(page.locator('.dashboard-cards')).toHaveCount(0)
  await expect(page.getByRole('table')).toHaveCount(0)
  await expect(page.getByRole('main')).not.toContainText('SYNTHETIC_SECRET')
})
test('separa instrumento/plataforma e aplica filtros vazios pelo teclado', async ({ page }) => {
  await access(page)
  let filtered = false
  await page.route(`**${base}?*`, route => {
    const query = new URL(route.request().url()).searchParams
    if (query.has('participant_id')) {
      expect(query.get('participant_id')).toBe('P_SINTETICO_AUSENTE'); expect(query.get('visit')).toBe('V2'); filtered = true
      return route.fulfill({ json: { items: [], next_cursor: null } })
    }
    return route.fulfill({ json: { items: [first, second, generic], next_cursor: null } })
  })
  await page.goto('/equipe'); await expect(card(page, 'Avaliações')).toHaveText('2')
  await page.getByRole('combobox', { name: /^Instrumento$/ }).selectOption(generic.test_code)
  await expect(card(page, 'Avaliações')).toHaveText('1')
  await expect(page.getByText('Precisão média', { exact: true })).toHaveCount(0)
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toContainText(generic.participant_id)
  await page.getByLabel('Participantes (códigos)').selectOption('P_SINTETICO_AUSENTE')
  await page.getByRole('listbox', { name: 'Visitas', exact: true }).selectOption('V2')
  await page.getByRole('button', { name: 'Aplicar filtros' }).focus(); await page.keyboard.press('Enter')
  await expect(page.getByText('Nenhuma avaliação corresponde aos filtros.', { exact: true })).toBeVisible()
  expect(filtered).toBe(true); await expect(page.locator('.dashboard-cards')).toHaveCount(0)
})
test('abre detalhe pelo teclado, exporta CSV e trata revogacao segura', async ({ page }) => {
  await access(page)
  await page.route(`**${base}?*`, route => route.fulfill({ json: { items: [first], next_cursor: null } }))
  await page.route(`**${base}/${first.assessment_id}`, route => route.fulfill({ json: detail }))
  let denied = false
  await page.route(`**${base}/${first.assessment_id}/export`, route => denied
    ? route.fulfill({ status: 404, json: { error: { code: 'not_found', message: 'SYNTHETIC_SECRET' } } })
    : route.fulfill({ status: 200, headers: { 'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="stroop_go_nogo_ptbr_2026-10-16_12h00m00s_trials.csv"' },
      body: 'participant_id,participant_name\nP_SINTETICO_web1,NAO_COLETADO\n' }))
  await page.goto('/equipe')
  await page.getByRole('button', { name: `Ver avaliação ${first.participant_id}, visita V1` }).focus(); await page.keyboard.press('Enter')
  const panel = page.getByRole('region', { name: 'Detalhe da avaliação' })
  await expect(panel).toBeFocused()
  await expect(panel.getByRole('table', { name: 'Tentativas registradas' })).toContainText('0,625')
  const downloaded = page.waitForEvent('download')
  await panel.getByRole('button', { name: 'Exportar CSV oficial' }).click()
  expect((await downloaded).suggestedFilename()).toBe('stroop_go_nogo_ptbr_2026-10-16_12h00m00s_trials.csv')
  await expect(panel.getByRole('status')).toHaveText('Arquivo preparado para download.')
  denied = true; await panel.getByRole('button', { name: 'Exportar CSV oficial' }).click()
  await expect(panel.getByRole('status')).toHaveText('O recurso solicitado não está disponível.')
  await expect(page.getByRole('main')).not.toContainText('SYNTHETIC_SECRET')
  await panel.getByRole('button', { name: 'Fechar detalhe' }).click(); await expect(panel).toHaveCount(0)
})
