/** W15A: filtros e paginacao HTTPS/API/PostgreSQL reais, sem interceptacao. */
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'

const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const script = fileURLToPath(new URL('./filters-manage.py', import.meta.url))
type Prepared = { cookie_name: string; token: string; projects: string[]; subject: string; assessment_ids: string[] }
function manage(value: Record<string, unknown>): Prepared {
  return JSON.parse(execFileSync(python, [script], { input: JSON.stringify(value), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }))
}

test('filtros combinados entre projetos contam codigos coincidentes e descartam agregado revogado', async ({ page, context }) => {
  const prepared = manage({})
  await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1', path: '/', secure: true, httpOnly: true, sameSite: 'Lax' }])
  const requests: URL[] = []
  page.on('request', request => {
    const url = new URL(request.url())
    if (url.pathname.includes('/assessments')) requests.push(url)
  })
  await page.goto('/equipe')
  await page.getByRole('combobox', { name: 'Projeto', exact: true }).selectOption(prepared.projects[0]!)
  // Aceite integrado usa tambem uma sessao criada pelo formulario W13A real.
  await page.getByLabel('Código do participante', { exact: true }).fill('P_SINTETICO_FILTROS_W13A')
  await page.getByLabel('Visita da sessão', { exact: true }).fill('V_SINTETICA_FILTROS')
  const creating = page.waitForResponse(response => response.url().endsWith(`/projects/${prepared.projects[0]}/invitations`) && response.request().method() === 'POST')
  await page.getByRole('button', { name: 'Gerar convite', exact: true }).click()
  expect((await creating).status()).toBe(201)
  const revoking = page.waitForResponse(response => response.url().includes('/invitations/') && response.url().endsWith('/revoke'))
  await page.getByRole('button', { name: 'Revogar convite', exact: true }).click()
  expect((await revoking).status()).toBe(204)

  const form = page.getByRole('form', { name: 'Filtros da consulta' })
  await form.getByRole('listbox', { name: 'Projetos da consulta', exact: true }).selectOption(prepared.projects)
  await form.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
  const table = page.getByRole('table', { name: 'Avaliações filtradas' })
  await expect(table.locator('tbody tr')).toHaveCount(105)
  const card = (label: string) => page.locator('.dashboard-cards > div').filter({ has: page.getByText(label, { exact: true }) }).locator('dd')
  await expect(card('Avaliações')).toHaveText('105')
  await page.setViewportSize({ width: 390, height: 844 })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.setViewportSize({ width: 1280, height: 720 })
  await page.evaluate(() => { document.documentElement.style.zoom = '2' })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.evaluate(() => { document.documentElement.style.zoom = '' })
  await page.setViewportSize({ width: 1280, height: 720 })
  await expect(card('Participantes únicos')).toHaveText('103')
  expect(requests.some(url => url.searchParams.has('cursor'))).toBe(true)
  expect(requests.filter(url => url.pathname.endsWith('/assessments/options')).length).toBeGreaterThanOrEqual(2)

  await form.getByText('Filtros avançados e ordenação', { exact: true }).click()
  await form.getByLabel('Data inicial', { exact: true }).fill('2026-10-01')
  await form.getByLabel('Data final', { exact: true }).fill('2026-10-03')
  await expect(form.getByLabel('Instrumento da consulta')).toContainText('stroop_go_nogo_ptbr')
  await form.getByLabel('Instrumento da consulta').selectOption('stroop_go_nogo_ptbr')
  await form.getByRole('listbox', { name: 'Participantes (códigos)', exact: true }).selectOption(['P_SINTETICO_W15'])
  await form.getByRole('listbox', { name: 'Visitas', exact: true }).selectOption(['V_SINTETICA'])
  await form.getByRole('listbox', { name: 'Avaliadores (identificação técnica)', exact: true }).selectOption(['LEGADO_NAO_MAPEADO'])
  await form.getByRole('listbox', { name: 'Versões', exact: true }).selectOption(['synthetic.1'])
  await form.getByRole('listbox', { name: 'Plataformas', exact: true }).selectOption(['psychopy'])
  await form.getByRole('button', { name: 'Aplicar filtros', exact: true }).focus()
  await page.keyboard.press('Enter')
  await expect(table.locator('tbody tr')).toHaveCount(2)
  await expect(card('Avaliações')).toHaveText('2')
  await expect(card('Participantes únicos')).toHaveText('2')
  await expect(card('Precisão média')).toHaveText('56,2%')
  await expect(card('Precisão mediana')).toHaveText('56,2%')
  await expect(card('Omissões')).toHaveText('10')
  await expect(card('Comissões')).toHaveText('4')
  await expect(page.getByRole('meter', { name: '2026-10-01: 1 avaliações', exact: true })).toHaveAttribute('value', '1')
  await expect(page.getByRole('meter', { name: '2026-10-03: 1 avaliações', exact: true })).toHaveAttribute('value', '1')
  await expect(card('Mediana dos tempos por avaliação')).toHaveText('0,512 s')
  await page.screenshot({ path: '/tmp/stroop-w15a-filters.png', fullPage: true })
  await form.screenshot({ path: '/tmp/stroop-w15a-filters-form.png' })
  await page.locator('.dashboard-cards').screenshot({ path: '/tmp/stroop-w15a-cards.png' })
  await expect(table).toContainText('2026-10-01T12:00:00')
  await expect(table).toContainText('2026-10-03T12:00:00')
  const combined = requests.filter(url => url.pathname.endsWith('/assessments') && url.searchParams.get('test_version') === 'synthetic.1')
  expect(new Set(combined.map(url => url.pathname.split('/')[4])).size).toBe(2)
  for (const url of combined) {
    expect(Object.fromEntries(url.searchParams)).toMatchObject({ start_date: '2026-10-01', end_date: '2026-10-03',
      test_code: 'stroop_go_nogo_ptbr', participant_id: 'P_SINTETICO_W15', visit: 'V_SINTETICA',
      evaluator_id: 'LEGADO_NAO_MAPEADO', test_version: 'synthetic.1', platform: 'psychopy' })
  }
  // A primeira consulta ainda funciona; falha real no segundo projeto invalida tudo.
  manage({ action: 'membership', project_id: prepared.projects[1], subject: prepared.subject, active: false })
  await form.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
  await expect(page.locator('.professional-dashboard > p[role=alert]')).toHaveText('O recurso solicitado não está disponível.')
  await expect(table).toHaveCount(0)
  await expect(page.locator('.dashboard-cards')).toHaveCount(0)
  manage({ action: 'membership', project_id: prepared.projects[1], subject: prepared.subject, active: true })
  await page.getByRole('button', { name: 'Atualizar consultas', exact: true }).click()
  await expect(table.locator('tbody tr')).toHaveCount(2)
  await expect(card('Participantes únicos')).toHaveText('2')
  await form.getByLabel('Data inicial', { exact: true }).fill('2027-01-01')
  await form.getByLabel('Data final', { exact: true }).fill('2027-01-02')
  await form.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
  await expect(page.getByText('Nenhuma avaliação corresponde aos filtros.', { exact: true })).toBeVisible()
  await expect(table).toHaveCount(0)
  await form.getByRole('button', { name: 'Limpar filtros', exact: true }).click()
  await expect(table).toHaveCount(0)
  await form.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
  await expect(table.locator('tbody tr')).toHaveCount(102)
})
