/** W15C: download de snapshot PostgreSQL/API/HTTPS reais, sem interceptacoes. */
import { execFileSync } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'
import type { Page, BrowserContext } from '@playwright/test'
const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const script = (name: string) => fileURLToPath(new URL(`./${name}-manage.py`, import.meta.url))
type Prepared = { cookie_name: string; token: string; projects: string[]; subject: string; demo_ids?: string[] }
function manage(name: string, value = {}): Prepared {
  return JSON.parse(execFileSync(python, [script(name)], { input: JSON.stringify(value), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }))
}
async function open(page: Page, context: BrowserContext, prepared: Prepared) {
  await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1', path: '/', secure: true, httpOnly: true, sameSite: 'Lax' }])
  await page.goto('/equipe')
  await page.getByRole('combobox', { name: 'Projeto', exact: true }).selectOption(prepared.projects[0]!)
  await page.getByRole('listbox', { name: 'Projetos da consulta', exact: true }).selectOption(prepared.projects)
  await page.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
}
async function download(page: Page) {
  const response = page.waitForResponse(value => value.url().endsWith('/api/v1/assessments/export'))
  const event = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Exportar visão filtrada', exact: true }).click()
  const [result, file] = await Promise.all([response, event])
  expect(result.status()).toBe(200)
  expect(result.headers()['cache-control']).toContain('no-store')
  expect(result.headers()['content-type']).toContain('text/csv')
  expect(file.suggestedFilename()).not.toContain('P_SINTETICO')
  const path = await file.path(); expect(path).not.toBeNull()
  const contents = await readFile(path!, 'utf8')
  expect(contents).not.toContain('NOME_SINTETICO_RESTRITO')
  const lines = contents.replace(/^\uFEFF/, '').trim().split(/\r?\n/)
  return { lines, headers: lines[0]!.split(','), request: result.request() }
}

test('CSV real corresponde a todas paginas/projetos e filtros; vinculo revogado impede novo download', async ({ page, context }) => {
  const prepared = manage('filters')
  await open(page, context, prepared)
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' }).locator('tbody tr')).toHaveCount(105)
  const all = await download(page)
  expect(all.lines).toHaveLength(106)
  const body = all.request.postDataJSON()
  expect(body.projects).toHaveLength(2)
  expect(body.projects.every((project: { snapshot: string }) => /^[A-Za-z0-9_-]{100,1024}$/.test(project.snapshot))).toBe(true)
  expect(new Set(all.lines.slice(1).map(line => line.split(',')[all.headers.indexOf('assessment_id')])).size).toBe(105)
  expect(all.headers).toContain('accuracy_percent'); expect(all.headers).toContain('response_time_seconds')
  expect(all.headers).not.toContain('participant_name'); expect(all.headers).not.toContain('initials')
  expect(all.headers).not.toContain('source_file')
  await page.getByLabel('Data inicial', { exact: true }).fill('2026-10-01')
  await page.getByLabel('Data final', { exact: true }).fill('2026-10-03')
  await page.getByRole('listbox', { name: 'Participantes (códigos)', exact: true }).selectOption('P_SINTETICO_W15')
  await page.getByRole('listbox', { name: 'Versões', exact: true }).selectOption('synthetic.1')
  await page.getByRole('listbox', { name: 'Visitas', exact: true }).selectOption('V_SINTETICA')
  await page.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
  await expect(page.getByRole('table', { name: 'Avaliações filtradas' }).locator('tbody tr')).toHaveCount(2)
  const filtered = await download(page)
  expect(filtered.lines).toHaveLength(3)
  for (const line of filtered.lines.slice(1)) {
    const cells = line.split(',')
    expect(cells[filtered.headers.indexOf('accuracy_percent')]).toBe('56.25')
    expect(Number(cells[filtered.headers.indexOf('response_time_seconds')])).toBeCloseTo(0.512123456789, 10)
  }
  expect(filtered.request.postDataJSON().filters).toMatchObject({ start_date: '2026-10-01', end_date: '2026-10-03', participant_id: ['P_SINTETICO_W15'], test_version: ['synthetic.1'], visit: ['V_SINTETICA'] })
  manage('filters', { action: 'membership', project_id: prepared.projects[1], subject: prepared.subject, active: false })
  let downloads = 0; page.on('download', () => downloads++)
  const refused = page.waitForResponse(value => value.url().endsWith('/api/v1/assessments/export'))
  await page.getByRole('button', { name: 'Exportar visão filtrada', exact: true }).click()
  expect((await refused).status()).toBe(404)
  expect(downloads).toBe(0)
  expect(page.url()).not.toContain(body.projects[0].snapshot)
  expect(await page.evaluate(() => [document.cookie, localStorage.length, sessionStorage.length])).toEqual(['', 0, 0])
})

test('CSV demonstrativo real conserva metricas proprias e nao mistura contagens Stroop', async ({ page, context }) => {
  const prepared = manage('complete-results')
  await open(page, context, prepared)
  await page.getByRole('combobox', { name: 'Instrumento', exact: true }).selectOption('instrumento_sintetico_demo')
  await expect(page.getByRole('table', { name: 'Métricas por instrumento e avaliação' }).locator('tbody tr')).toHaveCount(4)
  const output = await download(page)
  expect(output.lines).toHaveLength(3)
  expect(output.request.postDataJSON().view).toMatchObject({ test_code: 'instrumento_sintetico_demo' })
  for (const id of prepared.demo_ids!) expect(output.lines.join('\n')).toContain(id)
  expect(output.headers).toContain('demo_total_count'); expect(output.headers).toContain('demo_mean_unit')
  expect(output.headers).not.toContain('omission_errors_count')
})
