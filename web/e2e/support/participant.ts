/** Doubles apenas para testes isolados do DOM/motor; W13 exige suite HTTPS real. */
import { readFileSync } from 'node:fs'
import type { Page } from '@playwright/test'

const protocol = JSON.parse(readFileSync(new URL('../../../condicoes/web_protocol.json', import.meta.url), 'utf8'))
function source(name: string) {
  return readFileSync(new URL(`../../../condicoes/${name}`, import.meta.url), 'utf8').trim().split(/\r?\n/).slice(1).map(line => {
    const [id, word, color, , kind, response] = line.split(',')
    return { condition_id: Number(id), word, ink_color: color, ink_color_display: protocol.colors[color!],
      condition: kind, correct_response: response === 'space' ? 'space' : null }
  })
}
const main = source('bloco_principal_stroop_go_nogo_ptbr.csv')
const practice = source('pratica_stroop_go_nogo_ptbr.csv')
const order = [9, 1, 10, 2, 11, 3, 12, 4, 13, 5, 14, 6, 15, 7, 16, 8]

export async function mockParticipant(page: Page, initial: 'preparing' | 'running' | 'none' = 'preparing') {
  let state: 'preparing' | 'running' | 'completed' | 'aborted' | 'none' = initial
  let receipt: Record<string, unknown> | undefined
  let startCalls = 0
  let completeCalls = 0
  const now = Date.now()
  const common = { session_id: '00000000-0000-4000-8000-000000000130',
    activated_at: new Date(now).toISOString(), expires_at: new Date(now + 1_800_000).toISOString(), csrf_token: 's'.repeat(43) }
  await page.route('**/api/v1/participant/**', async route => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const json = async (body: unknown, status = 200, headers: Record<string, string> = {}) => route.fulfill({
      status, contentType: 'application/json', headers, body: JSON.stringify(body),
    })
    const error = async (code: string, status: number) => json({ error: { code }, request_id: 'synthetic-browser' }, status)
    if (request.method() === 'POST' && request.headers().origin !== new URL(request.url()).origin) return error('csrf_failed', 403)
    if (path.endsWith('/session')) {
      if (state === 'none') return error('authentication_required', 401)
      if (state === 'aborted') return error('state_conflict', 409)
      if (state === 'completed') return json(receipt, 200, {
        'X-CSRF-Token': common.csrf_token, 'X-Session-Expires-At': common.expires_at,
      })
      if (state === 'running') return json({ ...common, state, can_resume: false })
      return json({ ...common, state, can_resume: false, protocol_id: 'stroop_go_nogo_ptbr/0.2.2-web.1',
        test_code: 'stroop_go_nogo_ptbr', test_version: '0.2.2-web.1', platform: 'web', protocol,
        practice_conditions: practice,
        main_conditions: order.map((id, index) => ({ ...main.find(row => row.condition_id === id)!, trial_number: index + 1 })) })
    }
    if (path.endsWith('/redeem')) { state = 'preparing'; return json({ ...common, state }, 201) }
    if (request.headers()['x-csrf-token'] !== common.csrf_token) return error('csrf_failed', 403)
    if (path.endsWith('/start')) {
      startCalls += 1; state = 'running'
      return json({ session_id: common.session_id, state, started_at: new Date().toISOString(), expires_at: common.expires_at })
    }
    if (path.endsWith('/complete')) {
      completeCalls += 1
      const payload = request.postDataJSON()
      const outcomes = payload.trials.map((trial: { condition_id: number; key_pressed: string | null }) => {
        const go = main.find(row => row.condition_id === trial.condition_id)!.condition === 'congruent'
        return go ? trial.key_pressed ? 'hit' : 'omission' : trial.key_pressed ? 'commission' : 'correct_rejection'
      }) as string[]
      const count = (name: string) => outcomes.filter(value => value === name).length
      const hitTimes = payload.trials.filter((_: unknown, index: number) => outcomes[index] === 'hit')
        .map((trial: { reaction_time_ms: number }) => trial.reaction_time_ms / 1000).sort((a: number, b: number) => a - b) as number[]
      const middle = Math.floor(hitTimes.length / 2)
      const rt = hitTimes.length === 0 ? null : hitTimes.length % 2 ? hitTimes[middle]!
        : (hitTimes[middle - 1]! + hitTimes[middle]!) / 2
      state = 'completed'
      receipt = { session_id: common.session_id, assessment_id: '00000000-0000-4000-8000-000000000131',
        state, completed_at: new Date().toISOString(), platform: 'web', test_code: 'stroop_go_nogo_ptbr',
        test_version: '0.2.2-web.1', protocol_id: 'stroop_go_nogo_ptbr/0.2.2-web.1', app_version: payload.app_version,
        summary: { accuracy: (count('hit') + count('correct_rejection')) / 16 * 100,
          response_time_seconds: rt, total_trials: 16, hits: count('hit'), omission_errors: count('omission'),
          commission_errors: count('commission'), correct_rejections: count('correct_rejection') } }
      return json(receipt, 201)
    }
    if (path.endsWith('/abort')) { state = 'aborted'; return json({ session_id: common.session_id, state }) }
    if (path.endsWith('/logout')) { state = 'none'; return route.fulfill({ status: 204 }) }
    return error('not_found', 404)
  })
  return { counts: () => ({ start: startCalls, complete: completeCalls }) }
}
