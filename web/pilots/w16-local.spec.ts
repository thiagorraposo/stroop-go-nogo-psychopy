import { execFileSync } from 'node:child_process'
import { readFile, writeFile } from 'node:fs/promises'
import { expect, test } from '@playwright/test'
import type { Page, TestInfo } from '@playwright/test'
import { mockParticipant } from '../e2e/support/participant'
import type { MainTimingTrace } from '../src/experiment/main-engine'

async function prepare(page: Page) {
  const api = await mockParticipant(page)
  await page.goto('/pratica?w16=1')
  await page.bringToFront()
  await expect(page.getByLabel('Captura técnica W16')).toBeVisible()
  await page.getByLabel('Estou usando um computador ou notebook com teclado físico.').check()
  await page.getByRole('main').focus()
  await page.keyboard.press('Space')
  await page.getByRole('button', { name: 'Começar prática', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toBeVisible({ timeout: 25_000 })
  await page.getByRole('button', { name: 'Começar tarefa', exact: true }).click()
  return api
}

async function preserve(page: Page, info: TestInfo) {
  const panel = page.getByLabel('Captura técnica W16')
  await expect(panel.getByRole('status')).toHaveText('Réplicas nesta aba: 1', { timeout: 72_000 })
  const downloadPromise = page.waitForEvent('download')
  await panel.getByRole('button', { name: 'Exportar JSON' }).click()
  const download = await downloadPromise
  const artifact = info.outputPath('timing.json')
  await download.saveAs(artifact)
  const batch = JSON.parse(await readFile(artifact, 'utf8')) as {
    schema: string; environment: Record<string, unknown>; replicas: { trace: MainTimingTrace }[]
  }
  expect(batch.schema).toBe('stroop-w16-timing-batch-v1')
  expect(batch.replicas).toHaveLength(1)
  const trace = batch.replicas[0]!.trace
  const errors = trace.transitions.map(row => Math.abs(row.observed_elapsed_ms - row.planned_elapsed_ms))
  const lastTrialEnd = trace.transitions.filter(row => row.type === 'trial_end').at(-1)?.observed_elapsed_ms ?? null
  const duration = trace.outcome === 'completed' ? lastTrialEnd : null
  const summary = {
    schema: 'stroop-w16-local-summary-v1',
    commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
    project: info.project.name,
    test: info.title,
    mode: 'headed-automated-keyboard-mocked-api',
    environment: batch.environment,
    outcome: trace.outcome,
    interruption_reason: trace.interruption_reason,
    frame_period_ms: trace.frame_period_ms,
    transition_count: trace.transitions.length,
    max_absolute_transition_error_ms: errors.length ? Math.max(...errors) : null,
    duration_ms: duration,
    last_completed_trial_end_ms: lastTrialEnd,
    duration_error_ms: duration === null ? null : Math.abs(duration - 60000),
    physical_latency_measured: false,
    server_integration_measured: false,
  }
  const summaryPath = info.outputPath('summary.json')
  await writeFile(summaryPath, JSON.stringify(summary, null, 2))
  await info.attach('timing-raw', { path: artifact, contentType: 'application/json' })
  await info.attach('timing-summary', { path: summaryPath, contentType: 'application/json' })
  return { trace, summary }
}

for (let replica = 1; replica <= 10; replica++) {
  test(`replica local ${replica} de 10 preserva tempos e gates`, async ({ page }, info) => {
    const api = await prepare(page)
    // Um evento sintetico exercita o caminho RT; nao representa teclado fisico.
    let captured: Awaited<ReturnType<typeof preserve>>
    try {
      await expect(page.locator('[data-phase="stimulus"]')).toBeVisible({ timeout: 8_000 })
      await page.keyboard.press('Space')
    } finally {
      captured = await preserve(page, info)
    }
    const { trace, summary } = captured
    // A evidencia ja foi salva mesmo se o gate invalidou esta tentativa.
    expect(trace.outcome, trace.interruption_reason ?? '').toBe('completed')
    expect(trace.transitions).toHaveLength(64)
    expect(summary.max_absolute_transition_error_ms).toBeLessThanOrEqual(trace.frame_period_ms!)
    expect(summary.duration_error_ms).toBeLessThanOrEqual(100)
    expect(api.counts()).toEqual({ start: 1, complete: 1 })
  })
}

test('Escape preserva trilha interrompida sem resultado final', async ({ page }, info) => {
  const api = await prepare(page)
  await expect(page.locator('[data-phase="stimulus"]')).toBeVisible({ timeout: 8_000 })
  await page.keyboard.press('Escape')
  const { trace, summary } = await preserve(page, info)
  expect(trace.outcome).toBe('interrupted')
  expect(trace.interruption_reason).toBe('escape')
  expect(summary.duration_ms).toBeNull()
  expect(summary.duration_error_ms).toBeNull()
  expect(trace.transitions.length).toBeGreaterThan(0)
  expect(trace.keyboard_events.some(event => event.key === 'Escape')).toBe(true)
  expect(api.counts()).toEqual({ start: 1, complete: 0 })
})
