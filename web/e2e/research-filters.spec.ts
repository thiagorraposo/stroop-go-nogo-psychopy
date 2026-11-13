import { analysisFixture } from '../src/test/analysis-fixture'
/** Dados e respostas HTTP sinteticos para filtros; integracao real tem suite propria. */
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
const first = '11111111-1111-4111-8111-111111111111', second = '22222222-2222-4222-8222-222222222222'
const facets = { participant_id: ['P_SINTETICO'], visit: ['V1', 'V2'], evaluator_id: ['LEGADO_NAO_MAPEADO'], test_version: ['1.0.0'], platform: ['web'], test_code: ['stroop_go_nogo_ptbr'] }
const row = (id: string) => ({ assessment_id: id, participant_id: 'P_SINTETICO', visit: 'V1', evaluator_id: null,
  created_at: '2026-10-16T12:00:00Z', started_at: '2026-10-16T12:00:00Z', platform: 'web' as const, test_code: 'stroop_go_nogo_ptbr', test_version: '1.0.0', protocol_id: 'synthetic-v1', app_version: 'web-0.1.0',
  summary: { accuracy: 75, accuracy_go_trials: 75, accuracy_no_go_trials: 75, total_go_trials: 8, total_no_go_trials: 8, response_time_seconds: 0.625, total_trials: 16, hits: 6, correct_rejections: 6, omission_errors: 2, commission_errors: 2 } })
const card = (page: Page, title: string) => page.locator('.dashboard-cards > div').filter({ has: page.getByText(title, { exact: true }) }).locator('dd')
async function access(page: Page) {
  await page.route('**/api/v1/auth/me', r => r.fulfill({ json: { user_id: 'sintetico', role: 'consulta', csrf_token: 's'.repeat(43), expires_at: new Date(Date.now() + 3600000).toISOString() } }))
  await page.route('**/api/v1/projects?*', r => r.fulfill({ json: { items: [first, second].map((id, index) => ({ id, code: `PROJETO_${index}`, name: 'Pesquisa sintetica', active: true, created_at: '2026-10-16T12:00:00Z' })), next_cursor: null } }))
  await page.route('**/api/v1/projects/*/assessments/options*', r => r.fulfill({ json: facets }))
}
async function open(page: Page) { await page.goto('/equipe'); await expect(card(page, 'Avaliações')).toHaveText('1'); await page.getByText('Filtros avançados e ordenação', { exact: true }).click() }
async function apply(page: Page) { await page.getByRole('button', { name: 'Aplicar filtros' }).click() }

test('agrega todos projetos/paginas e distingue participantes por projeto', async ({ page }) => {
  await access(page)
  await page.route('**/api/v1/analysis/query', r => {
    const body = r.request().postDataJSON(), multi = body.query.projects.length > 1
    const all = multi ? [{ ...row('S1'), project_id: first }, { ...row('S1B'), project_id: first }, { ...row('S2'), project_id: second }] : [row('INITIAL')]
    const cursor = body.page.cursor
    return r.fulfill({ json: analysisFixture(body, all, multi ? { items: cursor ? all.slice(2) : all.slice(0, 2), next_cursor: cursor ? null : 'next' } : {}) })
  })
  await open(page)
  await page.getByLabel('Projetos da consulta', { exact: true }).selectOption([first, second])
  await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption('P_SINTETICO'); await apply(page)
  await expect(card(page, 'Avaliações')).toHaveText('3'); await expect(card(page, 'Participantes únicos')).toHaveText('2')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' }).locator('tbody tr')).toHaveCount(3)
})

test('combina datas/listas/instrumento no corpo POST e limpa pelo teclado', async ({ page }) => {
  await access(page); let observed: Record<string, unknown> | undefined
  await page.route('**/api/v1/analysis/query', r => {
    const body = r.request().postDataJSON()
    expect(r.request().method()).toBe('POST')
    expect(r.request().headers()['x-csrf-token']).toBe('s'.repeat(43))
    if (body.query.filters.date_from) observed = body.query.filters
    return r.fulfill({ json: analysisFixture(body, [row('S1')]) })
  })
  await open(page)
  await page.getByLabel('Data inicial').fill('2026-10-01'); await page.getByLabel('Data final').fill('2026-10-17')
  await page.getByRole('listbox', { name: 'Instrumento da consulta', exact: true }).selectOption('stroop_go_nogo_ptbr')
  await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption('P_SINTETICO')
  await page.getByRole('listbox', { name: 'Visitas', exact: true }).selectOption(['V1', 'V2'])
  await page.getByRole('listbox', { name: 'Avaliadores (identificação técnica)', exact: true }).selectOption('LEGADO_NAO_MAPEADO')
  await page.getByRole('listbox', { name: 'Versões', exact: true }).selectOption('1.0.0'); await page.getByRole('listbox', { name: 'Plataformas', exact: true }).selectOption('web')
  await page.getByRole('button', { name: 'Aplicar filtros' }).focus(); await page.keyboard.press('Enter')
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('2026-10-01')
  expect(observed).toMatchObject({ visit: ['V1', 'V2'], date_to: '2026-10-17', test_code: ['stroop_go_nogo_ptbr'], evaluator_id: ['LEGADO_NAO_MAPEADO'] })
  await page.getByRole('button', { name: 'Limpar filtros' }).focus(); await page.keyboard.press('Enter')
  await expect(page.getByLabel('Data inicial')).toHaveValue(''); await expect(page.getByRole('listbox', { name: 'Visitas', exact: true })).toHaveValues([])
  await expect(page.getByText('Alterações não aplicadas.', { exact: false })).toBeVisible()
  await apply(page)
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('sem restrições adicionais')
})

for (const mode of ['falha projeto', 'cursor repetido', 'limite 5000', 'fingerprint alterado']) {
  test(`${mode} invalida agregado sem totais parciais`, async ({ page }) => {
    await access(page); let filtering = false
    await page.route('**/api/v1/analysis/query', r => {
      const body = r.request().postDataJSON()
      if (!filtering) return r.fulfill({ json: analysisFixture(body, [row('INITIAL')]) })
      if (mode === 'falha projeto' || mode === 'limite 5000') return r.fulfill({ status: mode === 'limite 5000' ? 422 : 503, json: { error: { code: mode === 'limite 5000' ? 'invalid_request' : 'service_unavailable' } } })
      const all = [row('S0'), row('S1'), row('S2')]
      return r.fulfill({ json: analysisFixture(body, all, { items: [{ ...row(body.page.cursor ? 'S1' : 'S0'), project_id: first }],
        next_cursor: 'c1', ...(body.page.cursor && mode === 'fingerprint alterado' ? { content_fingerprint: 'c'.repeat(64) } : {}) }) })
    })
    await open(page); filtering = true
    await page.getByLabel('Projetos da consulta', { exact: true }).selectOption([first, second]); await apply(page)
    await expect(page.getByRole('alert')).toBeVisible(); await expect(page.locator('.dashboard-cards')).toHaveCount(0)
    await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Atualizar consultas' })).toBeVisible()
  })
}

test('troca de projeto cancela consulta anterior sem reaplicar resposta atrasada', async ({ page }) => {
  await access(page); let started!: () => void, release!: () => void
  const received = new Promise<void>(r => { started = r }), gate = new Promise<void>(r => { release = r })
  await page.route('**/api/v1/analysis/query', async r => {
    const body = r.request().postDataJSON()
    if (body.query.filters.participant_code) { started(); await gate; await r.fulfill({ json: analysisFixture(body, [row('ATRASADA')]) }).catch(() => undefined); return }
    return r.fulfill({ json: analysisFixture(body, [row(body.query.projects.includes(second) ? 'ATUAL' : 'INICIAL')]) })
  })
  await open(page); await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption('P_SINTETICO'); await apply(page); await received
  await page.getByLabel('Projetos da consulta', { exact: true }).selectOption(second); await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption([]); await apply(page); release()
  await expect(card(page, 'Avaliações')).toHaveText('1')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toContainText('PROJETO_1')
  await expect(page.getByLabel('Participantes (códigos)', { exact: true })).toHaveValues([])
})

test('multisseleções de condição/resposta mantêm acesso em larguras, zoom e reflow', async ({ page }, info) => {
  await access(page)
  await page.route('**/api/v1/analysis/query', r => r.fulfill({ json: analysisFixture(r.request().postDataJSON(), [row('S1')]) }))
  await open(page)
  const form = page.getByRole('form', { name: 'Filtros da consulta' })
  const condition = form.getByRole('listbox', { name: 'Condição experimental', exact: true })
  const response = form.getByRole('listbox', { name: 'Tipo de resposta / erro', exact: true })
  await condition.selectOption(['congruent', 'incongruent'])
  await response.selectOption(['hit', 'omission'])
  await form.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
  const error = form.getByRole('alert')
  await expect(error).toContainText('Selecione somente o instrumento Stroop')
  expect(await form.getAttribute('aria-describedby')).toBe(await error.getAttribute('id'))
  for (const width of [360, 768, 1024, 1366, 1920, 320]) {
    await page.setViewportSize({ width, height: 900 })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `scroll global em ${width}`).toBe(true)
    for (const control of [condition, response]) {
      await control.focus()
      await expect(control).toBeFocused()
      const bounds = await control.boundingBox()
      expect(bounds!.x).toBeGreaterThanOrEqual(0)
      expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(width)
    }
    if (width === 360) await form.screenshot({ path: info.outputPath('trial-filters-360.png') })
  }
  for (const width of [1366, 1920]) {
    await page.setViewportSize({ width, height: 1080 })
    await page.evaluate(() => { document.documentElement.style.zoom = '2' })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await expect(response).toHaveValues(['hit', 'omission'])
    await page.evaluate(() => { document.documentElement.style.zoom = '' })
  }
  await page.setViewportSize({ width: 1280, height: 1080 })
  await page.evaluate(() => { document.documentElement.style.zoom = '4' })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await expect(response).toHaveValues(['hit', 'omission'])
  await page.evaluate(() => { document.documentElement.style.zoom = '' })
  await page.setViewportSize({ width: 1366, height: 1080 })
  await form.screenshot({ path: info.outputPath('trial-filters-1366.png') })
})
