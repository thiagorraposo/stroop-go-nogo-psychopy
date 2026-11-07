import { execFileSync } from 'node:child_process'
import { writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { expect, test } from '@playwright/test'
import type { MainResult, MainTimingTrace } from '../src/experiment/main-engine'
import type { TransportStatus } from '../src/transport/checkpoint-queue'

type Scenario = 'healthy' | 'slow' | 'lost' | 'unavailable'
type Capture = {
  trace?: MainTimingTrace; result?: MainResult; interruption?: string;
  statuses: TransportStatus[]; copies: number[]; callbackTimes: number[];
  started?: number; preparationError?: string; cleanup(): void
}
declare global { interface Window { web011: Capture } }
const scenarios: Scenario[] = ['healthy', 'slow', 'lost', 'unavailable', 'healthy', 'slow', 'lost', 'unavailable', 'healthy', 'slow']
const sessionId = '00000000-0000-4000-8000-000000000130'

for (const [index, scenario] of scenarios.entries()) {
  test(`DEC-04 replica ${index + 1}/10 ${scenario}`, async ({ page, context, browser }, info) => {
    const startedAt = new Date().toISOString()
    const navigationEvents: { at: string; path: string }[] = []
    page.on('framenavigated', frame => {
      if (frame === page.mainFrame()) navigationEvents.push({ at: new Date().toISOString(), path: new URL(frame.url()).pathname })
    })
    const expiresAt = new Date(Date.now() + 1_800_000).toISOString()
    let received = 0
    let running = false
    let available = false
    let requests = 0
    let lost = false
    const rows: unknown[] = []
    const calls: { at: number; through: number; status: string; bytes: number }[] = []
    const receipt = () => ({ confirmed_through: received,
      prefix_hash: received ? createHash('sha256').update(JSON.stringify(rows)).digest('hex') : null,
      received_at: received ? startedAt : null })
    await context.route('**/api/v1/participant/**', async route => {
      const request = route.request()
      const path = new URL(request.url()).pathname
      const json = (body: unknown, status = 200) => route.fulfill({ status, contentType: 'application/json',
        headers: { 'Cache-Control': 'no-store' }, body: JSON.stringify(body) })
      if (path.endsWith('/session')) return json({ session_id: sessionId, state: running ? 'running' : 'preparing',
        expires_at: expiresAt, checkpoint: receipt() })
      if (!path.endsWith('/checkpoints')) return json({ error: { code: 'not_found' } }, 404)
      if (request.method() !== 'POST' || request.headers()['x-csrf-token'] !== 's'.repeat(43)
        || request.headers().origin !== new URL(request.url()).origin) return json({ error: { code: 'csrf_failed' } }, 403)
      requests += 1
      const body = request.postDataJSON() as { trials: { trial_number: number }[] }
      const call = { at: Date.now(), through: body.trials.at(-1)!.trial_number, status: 'pending', bytes: request.postData()!.length }
      calls.push(call)
      if (scenario === 'unavailable' && !available) { call.status = '503'; return json({ error: { code: 'service_unavailable' } }, 503) }
      // ACK mantido em voo por mais de uma tentativa: agrupamento real no worker.
      if (scenario === 'slow') await new Promise(resolve => setTimeout(resolve, 4500))
      for (const trial of body.trials) {
        if (trial.trial_number > received + 1) { call.status = '409'; return json({ error: { code: 'state_conflict' } }, 409) }
        if (trial.trial_number <= received) {
          if (JSON.stringify(rows[trial.trial_number - 1]) !== JSON.stringify(trial)) {
            call.status = '409'; return json({ error: { code: 'result_conflict' } }, 409)
          }
        } else { rows.push(trial); received += 1 }
      }
      if (scenario === 'lost' && !lost) { lost = true; call.status = 'lost-after-commit'; return route.abort('failed') }
      call.status = '200'
      return json({ session_id: sessionId, ...receipt() })
    })
    await page.goto('/')
    await expect(page.getByRole('main')).toBeFocused()
    await page.bringToFront()
    // Ensaiar motor/jsPsych/worker reais com HTTP double; integracao API/PG e UX ficam em M4.
    let capture: Omit<Capture, 'cleanup'> | undefined
    let drainCompleted = false
    try {
      await page.evaluate(async expiresAt => {
        const enginePath = '/src/experiment/main.ts'
        const practicePath = '/src/experiment/practice.ts'
        const workerPath = '/src/transport/checkpoint-worker.ts'
        const protocolPath = '/src/experiment/protocol.ts'
        const apiPath = '/src/api/participant.ts'
        const { mountPractice } = await import(/* @vite-ignore */ practicePath) as typeof import('../src/experiment/practice')
        const { mountMain } = await import(/* @vite-ignore */ enginePath) as typeof import('../src/experiment/main')
        const { prepareCheckpointWorker } = await import(/* @vite-ignore */ workerPath) as typeof import('../src/transport/checkpoint-worker')
        const { MAIN_CONDITIONS } = await import(/* @vite-ignore */ protocolPath) as typeof import('../src/experiment/protocol')
        const api = await import(/* @vite-ignore */ apiPath) as typeof import('../src/api/participant')
        const host = document.createElement('div')
        Object.assign(host.style, { position: 'fixed', inset: '0', zIndex: '9999' })
        document.body.replaceChildren(host)
        window.web011 = { statuses: [], copies: [], callbackTimes: [], cleanup() {} }
        try {
          const worker = await prepareCheckpointWorker({ session_id: '00000000-0000-4000-8000-000000000130',
            csrf_token: 's'.repeat(43), expires_at: expiresAt, protocol_id: api.PROTOCOL_ID,
            test_version: api.TEST_VERSION, platform: 'web', app_version: `${api.APP_VERSION}.transport.1` }, status => {
              window.web011.statuses.push(status)
              window.web011.callbackTimes.push(performance.now())
            })
          // Armar botao apos prontidao; nunca aguardar rede dentro da contagem.
          const button = document.createElement('button')
          button.textContent = 'Iniciar campanha sintética'
          button.onclick = () => {
            window.web011.started = performance.now()
            const cleanup = mountMain(host, { order: MAIN_CONDITIONS,
              onTimingTrace: trace => { window.web011.trace = trace },
              onTrialComplete: (trial, period) => {
                const before = performance.now()
                worker.enqueue(trial, period)
                window.web011.copies.push(performance.now() - before)
              },
              onComplete: result => { window.web011.result = result },
              onInterrupted: reason => { window.web011.interruption = reason },
            })
            window.web011.cleanup = () => { cleanup(); worker.dispose() }
          }
          const practiceCleanup = mountPractice(host, {
            onComplete: () => host.replaceChildren(button),
            onInterrupted: reason => { window.web011.preparationError = `practice_${reason}` },
          })
          window.web011.cleanup = () => { practiceCleanup(); worker.dispose() }
        } catch { window.web011.preparationError = 'transport_not_ready' }
      }, expiresAt)
      await expect(page.getByRole('button', { name: 'Iniciar campanha sintética' })).toBeVisible({ timeout: 25_000 })
      running = true
      await page.getByRole('button', { name: 'Iniciar campanha sintética' }).click()
      await expect(page.locator('[data-phase="stimulus"]')).toBeVisible({ timeout: 8000 })
      await page.keyboard.press('Space')
      // Poll de baixa frequencia; relogio real, nenhum clock mock/trace/video por quadro.
      await expect.poll(() => page.evaluate(() => Boolean(window.web011.trace)), { timeout: 66_000, intervals: [1000] }).toBe(true)
    } finally {
      available = true // Recuperacao depois do trecho experimental; nunca alongar o bloco.
      try {
        await expect.poll(() => page.evaluate(() => {
          const data = window.web011
          return Boolean(data && data.statuses.at(-1)?.confirmed === data.copies.length)
        }), { timeout: 22_000, intervals: [1000] }).toBe(true).then(() => { drainCompleted = true }).catch(() => undefined)
      } finally {
        capture = await page.evaluate(() => {
          if (!window.web011) return { statuses: [], copies: [], callbackTimes: [], preparationError: 'fixture_missing_after_navigation' }
          const { cleanup: _cleanup, ...data } = window.web011
          return data
        }).catch(() => ({ statuses: [], copies: [], callbackTimes: [], preparationError: 'page_unavailable' }))
        const trace = capture.trace
        const errors = trace?.transitions.map(row => Math.abs(row.observed_elapsed_ms - row.planned_elapsed_ms)) ?? []
        const duration = trace?.outcome === 'completed' ? trace.transitions.at(-1)?.observed_elapsed_ms : null
        const artifact = { schema: 'stroop-web011-engineering-v1', started_at: startedAt,
          commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
          worktree_diff_sha256: createHash('sha256').update(execFileSync('git', ['diff', 'HEAD', '--', 'web'], { encoding: 'utf8' })).digest('hex'),
          browser: browser.version(), project: info.project.name, scenario, replica: index + 1,
          presentation: 'stroop-web-outline/1.0.0', app_version: 'web-0.1.0+visual.1.0.0.transport.1',
          mode: 'headed-real-clock-real-worker-http-double', physical_latency_measured: false, server_integration_measured: false,
          environment: await page.evaluate(() => ({ userAgent: navigator.userAgent, platform: navigator.platform,
            viewport: [innerWidth, innerHeight], screen: [screen.width, screen.height], dpr: devicePixelRatio,
            visible: document.visibilityState, focused: document.hasFocus() })).catch(() => ({ unavailable: true })),
          summary: { outcome: trace?.outcome, reason: trace?.interruption_reason,
            frame_period_ms: trace?.frame_period_ms, transitions: trace?.transitions.length,
            max_transition_error_ms: errors.length ? Math.max(...errors) : null,
            duration_ms: duration, duration_error_ms: duration == null ? null : Math.abs(duration - 60000),
            max_copy_ms: capture.copies.length ? Math.max(...capture.copies) : null,
            complete_trials_delivered: capture.copies.length, confirmed: received, requests, drain_completed: drainCompleted },
          capture, navigation_events: navigationEvents, transport_calls: calls, received_observations: rows }
        const path = info.outputPath('engineering.json')
        await writeFile(path, JSON.stringify(artifact, null, 2))
        await info.attach('engineering-raw-and-summary', { path, contentType: 'application/json' })
        await page.evaluate(() => window.web011?.cleanup()).catch(() => undefined)
      }
    }
    // Evidencia preservada antes de qualquer assercao de aceite. Falhas nao sao substituidas.
    expect(capture?.trace?.outcome, capture?.trace?.interruption_reason ?? '').toBe('completed')
    const trace = capture!.trace!
    expect(trace.transitions).toHaveLength(64)
    expect(Math.max(...trace.transitions.map(row => Math.abs(row.observed_elapsed_ms - row.planned_elapsed_ms)))).toBeLessThanOrEqual(trace.frame_period_ms!)
    expect(Math.abs(trace.transitions.at(-1)!.observed_elapsed_ms - 60000)).toBeLessThanOrEqual(100)
    expect(capture!.copies).toHaveLength(16)
    expect(received).toBe(16)
    expect(drainCompleted).toBe(true)
    expect(capture!.statuses.some(status => status.state === 'stopped')).toBe(false)
    if (scenario === 'lost') expect(lost).toBe(true)
    if (scenario === 'unavailable') expect(calls.some(call => call.status === '503')).toBe(true)
  })
}
