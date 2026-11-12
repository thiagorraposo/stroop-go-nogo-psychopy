/** QUERY7: POST normalizado em HTTPS/API/PG reais, sem interceptação HTTP. */
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'
const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const script = fileURLToPath(new URL('./dashboard-manage.py', import.meta.url))

test('POST vincula consulta normalizada, população A/T e revogação sem nominal em URL', async ({ page, context }) => {
  const prepared = JSON.parse(execFileSync(python, [script], { input: JSON.stringify({ role: 'consulta' }), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }))
  await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1', path: '/', secure: true, httpOnly: true, sameSite: 'Lax' }])
  await page.goto('/equipe')
  await expect(page.getByRole('form', { name: 'Filtros da consulta' })).toBeVisible()
  const responses = await page.evaluate(async ({ project, csrf, assessment }) => {
    const query = async (filters: Record<string, unknown>, token = csrf) => {
      const response = await fetch('/api/v1/analysis/query', { method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
        body: JSON.stringify({ query: { projects: [project], filters },
          grouping: { level: 'assessment', dimension: 'project' }, page: { size: 1 } }) })
      return { status: response.status, body: await response.json(), cache: response.headers.get('cache-control') }
    }
    const detail = await (await fetch(`/api/v1/projects/${project}/assessments/${assessment}`)).json()
    return { first: await query({ platform: ['psychopy'] }),
      canonical: await query({ platform: ['psychopy_local'] }),
      trials: await query({ test_code: ['stroop_go_nogo_ptbr'], condition: ['congruent'], response_type: ['hit', 'omission'] }),
      unsupported: await query({ patient_search: 'NOME_SINTETICO_RESTRITO' }),
      csrf: await query({}, 'invalid'), detail }
  }, { project: prepared.project_id as string, csrf: prepared.csrf as string, assessment: prepared.assessment_id as string })
  expect(responses.first.status).toBe(200)
  expect(responses.first.cache).toBe('no-store')
  expect(responses.first.body.normalized_query).toEqual(responses.canonical.body.normalized_query)
  expect(responses.first.body.query_fingerprint).toBe(responses.canonical.body.query_fingerprint)
  expect(responses.first.body.counts.assessments).toBe(1)
  expect(responses.first.body.items[0].summary).toEqual(responses.detail.summary)
  expect(responses.first.body.capabilities.exports).toBe(false)
  expect(responses.trials.status).toBe(200)
  const selected = responses.detail.trials.filter((trial: { condition: string; error_type: string }) =>
    trial.condition === 'congruent' && ['hit', 'omission'].includes(trial.error_type))
  expect(responses.trials.body.counts.trials).toBe(selected.length)
  expect(responses.trials.body.items[0].summary).toEqual(responses.detail.summary)
  expect(responses.unsupported.status).toBe(422)
  expect(responses.csrf.status).toBe(403)
  expect(JSON.stringify(responses.first.body)).not.toContain('NOME_SINTETICO_RESTRITO')
  execFileSync(python, [script], { input: JSON.stringify({ action: 'revoke', project_id: prepared.project_id, subject: prepared.subject }), stdio: ['pipe', 'pipe', 'pipe'] })
  const revoked = await page.evaluate(async ({ project, csrf }) => {
    const response = await fetch('/api/v1/analysis/query', { method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf },
      body: JSON.stringify({ query: { projects: [project], filters: {} },
        grouping: { level: 'assessment', dimension: 'project' }, page: {} }) })
    return response.status
  }, { project: prepared.project_id as string, csrf: prepared.csrf as string })
  expect(revoked).toBe(404)
  expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
  expect(page.url()).not.toContain('SINTETICO')
})
