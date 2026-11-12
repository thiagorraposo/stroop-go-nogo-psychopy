/** Dados e respostas HTTP sinteticos para filtros; integracao real tem suite propria. */
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
const first = '11111111-1111-4111-8111-111111111111', second = '22222222-2222-4222-8222-222222222222'
const facets = { participant_id: ['P_SINTETICO'], visit: ['V1', 'V2'], evaluator_id: ['LEGADO_NAO_MAPEADO'], test_version: ['1.0.0'], platform: ['web'], test_code: ['stroop_go_nogo_ptbr'] }
const row = (id: string) => ({ assessment_id: id, participant_id: 'P_SINTETICO', visit: 'V1', evaluator_id: null,
  created_at: '2026-10-16T12:00:00Z', started_at: '2026-10-16T12:00:00Z', platform: 'web', test_code: 'stroop_go_nogo_ptbr', test_version: '1.0.0', protocol_id: 'synthetic-v1', app_version: 'web-0.1.0',
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
  await page.route('**/api/v1/projects/*/assessments?*', r => {
    const url = new URL(r.request().url()), multi = url.pathname.includes(second)
    return r.fulfill({ json: { items: [row(multi ? 'S2' : url.searchParams.has('cursor') ? 'S1B' : 'S1')], next_cursor: !multi && url.searchParams.has('participant_id') && !url.searchParams.has('cursor') ? 'next' : null } })
  })
  await open(page)
  await page.getByLabel('Projetos da consulta', { exact: true }).selectOption([first, second])
  await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption('P_SINTETICO'); await apply(page)
  await expect(card(page, 'Avaliações')).toHaveText('3'); await expect(card(page, 'Participantes únicos')).toHaveText('2')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' }).locator('tbody tr')).toHaveCount(3)
})

test('combina datas/listas/instrumento no servidor e limpa pelo teclado', async ({ page }) => {
  await access(page); let observed: URL | undefined
  await page.route('**/api/v1/projects/*/assessments?*', r => {
    const url = new URL(r.request().url()); if (url.searchParams.has('start_date')) observed = url
    return r.fulfill({ json: { items: [row('S1')], next_cursor: null } })
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
  expect(observed?.searchParams.getAll('visit')).toEqual(['V1', 'V2'])
  expect(observed?.searchParams.get('end_date')).toBe('2026-10-17')
  expect(observed?.searchParams.get('test_code')).toBe('stroop_go_nogo_ptbr')
  expect(observed?.searchParams.get('evaluator_id')).toBe('LEGADO_NAO_MAPEADO')
  await page.getByRole('button', { name: 'Limpar filtros' }).focus(); await page.keyboard.press('Enter')
  await expect(page.getByLabel('Data inicial')).toHaveValue(''); await expect(page.getByRole('listbox', { name: 'Visitas', exact: true })).toHaveValues([])
  await expect(page.getByText('Alterações não aplicadas.', { exact: false })).toBeVisible()
  await apply(page)
  await expect(page.getByText(/^Filtros aplicados:/)).toContainText('sem restrições adicionais')
})

for (const mode of ['falha projeto', 'cursor repetido', 'limite 5000']) {
  test(`${mode} invalida agregado sem totais parciais`, async ({ page }) => {
    await access(page); let filtering = false
    await page.route('**/api/v1/projects/*/assessments?*', r => {
      const url = new URL(r.request().url())
      if (!filtering) return r.fulfill({ json: { items: [row('INITIAL')], next_cursor: null } })
      if (mode === 'falha projeto' && url.pathname.includes(second)) return r.fulfill({ status: 503, json: { error: { code: 'permission_denied' } } })
      const index = Number(url.searchParams.get('cursor')?.replace('c', '') ?? '0')
      const items = mode === 'limite 5000' ? Array.from({ length: 100 }, (_, n) => row(`S_${index}_${n}`)) : [row(`S_${index}`)]
      return r.fulfill({ json: { items, next_cursor: mode === 'falha projeto' ? null : mode === 'cursor repetido' ? 'c1' : `c${index + 1}` } })
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
  await page.route('**/api/v1/projects/*/assessments?*', async r => {
    const url = new URL(r.request().url())
    if (url.searchParams.has('participant_id')) { started(); await gate; await r.fulfill({ json: { items: [row('ATRASADA')], next_cursor: null } }).catch(() => undefined); return }
    return r.fulfill({ json: { items: [row(url.pathname.includes(second) ? 'ATUAL' : 'INICIAL')], next_cursor: null } })
  })
  await open(page); await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption('P_SINTETICO'); await apply(page); await received
  await page.getByLabel('Projetos da consulta', { exact: true }).selectOption(second); await page.getByLabel('Participantes (códigos)', { exact: true }).selectOption([]); await apply(page); release()
  await expect(card(page, 'Avaliações')).toHaveText('1')
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' })).toContainText('PROJETO_1')
  await expect(page.getByLabel('Participantes (códigos)', { exact: true })).toHaveValues([])
})
