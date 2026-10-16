import { afterEach, expect, test, vi } from 'vitest'
import shared from '../../../tests/fixtures/web_results_summary.json'
import { ApiError } from './client'
import { abortParticipant, APP_VERSION, completeParticipant, completionPayload, getParticipantSession,
  participantErrorMessage, PROTOCOL_ID, redeemInvitation, startParticipant, TEST_VERSION, logoutParticipant } from './participant'
import type { PreparingSession } from './participant'
import { MAIN_CONDITIONS, PRACTICE_CONDITIONS, PROTOCOL } from '../experiment/protocol'
import type { MainResult, MainTrial } from '../experiment/main-engine'

const sessionId = '00000000-0000-4000-8000-000000000130'
const assessmentId = '00000000-0000-4000-8000-000000000131'
const common = { session_id: sessionId, activated_at: '2026-10-16T13:00:00Z',
  expires_at: '2026-10-16T13:30:00Z', csrf_token: 's'.repeat(43) }
const order = shared.cases[1]!.order.map(id => MAIN_CONDITIONS.find(row => row.condition_id === id)!)
const preparing = { ...common, state: 'preparing' as const, can_resume: false,
  protocol_id: PROTOCOL_ID, test_code: 'stroop_go_nogo_ptbr', test_version: TEST_VERSION,
  platform: 'web', protocol: PROTOCOL, practice_conditions: PRACTICE_CONDITIONS,
  main_conditions: order.map((row, index) => ({ ...row, trial_number: index + 1 })) }
const model: PreparingSession = { ...common, state: 'preparing', protocol_id: PROTOCOL_ID,
  test_version: TEST_VERSION, main_conditions: order }
const expected = shared.cases[1]!.expected_summary
const receipt = { session_id: sessionId, assessment_id: assessmentId, state: 'completed',
  completed_at: '2026-10-16T13:02:00Z', platform: 'web', test_code: 'stroop_go_nogo_ptbr',
  test_version: TEST_VERSION, protocol_id: PROTOCOL_ID, app_version: APP_VERSION,
  summary: { accuracy: expected.accuracy, response_time_seconds: expected.response_time,
    total_trials: expected.total_trials, hits: expected.hits, omission_errors: expected.omission_errors,
    commission_errors: expected.commission_errors, correct_rejections: expected.correct_rejections } }
function mainResult(): MainResult {
  return { frame_period_ms: shared.cases[1]!.frame_period_ms,
    trials: structuredClone(shared.cases[1]!.trials) as MainTrial[], order: structuredClone(order) }
}
function mock(body: unknown, status = 200, headers: Record<string, string> = {}) {
  const fetchMock = vi.fn().mockResolvedValue(Response.json(body, { status, headers }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })

function transport(call: unknown[]) {
  expect(call[1]).toMatchObject({ credentials: 'same-origin', cache: 'no-store', redirect: 'error' })
  return call[1] as RequestInit
}

test('bootstrap conserva ordem persistida e valida todos os dados aprovados', async () => {
  const fetchMock = mock(preparing)
  const value = await getParticipantSession()
  expect(value).toEqual(model)
  expect(fetchMock.mock.calls[0]![0]).toBe('/api/v1/participant/session')
  expect(transport(fetchMock.mock.calls[0]!)).toMatchObject({ method: 'GET' })
  expect(value.state === 'preparing' && value.main_conditions.map(row => row.condition_id)).toEqual(shared.cases[1]!.order)
})

test.each([
  (value: typeof preparing) => Object.assign(value, { participant_name: 'DADO_SINTETICO_PROIBIDO' }),
  (value: typeof preparing) => { value.can_resume = true },
  (value: typeof preparing) => { value.protocol.main.fixation_ms = 301 },
  (value: typeof preparing) => { value.practice_conditions[0]!.word = 'ESTIMULO_SINTETICO_INVALIDO' },
  (value: typeof preparing) => { value.main_conditions[0]!.ink_color_display = '#FFFFFF' },
  (value: typeof preparing) => { value.main_conditions[0]!.trial_number = 2 },
  (value: typeof preparing) => { value.main_conditions[1]!.condition_id = value.main_conditions[0]!.condition_id },
  (value: typeof preparing) => { value.expires_at = '2026-02-30T13:30:00Z' },
])('rejeita bootstrap adulterado sem incluir seus dados no erro: %s', async mutate => {
  const value = structuredClone(preparing)
  mutate(value)
  mock(value)
  await expect(getParticipantSession()).rejects.toMatchObject({ code: 'invalid_response' })
})

test('running nao oferece retomada e recibo completed pode ser recuperado', async () => {
  mock({ ...common, state: 'running', can_resume: false })
  expect((await getParticipantSession()).state).toBe('running')
  mock(receipt, 200, { 'X-CSRF-Token': common.csrf_token, 'X-Session-Expires-At': common.expires_at })
  expect(await getParticipantSession()).toEqual({ ...receipt, csrf_token: common.csrf_token, expires_at: common.expires_at })
  mock(receipt)
  await expect(getParticipantSession()).rejects.toMatchObject({ code: 'invalid_response' })
})

test('resgate usa corpo e origem relativa, sem URL ou storage para o convite', async () => {
  const fetchMock = mock({ ...common, state: 'preparing' }, 201)
  expect(await redeemInvitation('c'.repeat(43))).toEqual(common)
  expect(fetchMock.mock.calls[0]![0]).toBe('/api/v1/participant/redeem')
  expect(transport(fetchMock.mock.calls[0]!)).toMatchObject({ method: 'POST', body: JSON.stringify({ code: 'c'.repeat(43) }) })
  expect(() => redeemInvitation('inválido')).toThrow(ApiError)
})

test('start fixa versao e exige recibo correto antes do motor', async () => {
  const fetchMock = mock({ session_id: sessionId, state: 'running',
    started_at: '2026-10-16T13:01:00Z', expires_at: common.expires_at })
  await startParticipant(model)
  expect(transport(fetchMock.mock.calls[0]!)).toMatchObject({ method: 'POST',
    headers: { 'X-CSRF-Token': common.csrf_token }, body: JSON.stringify({ app_version: APP_VERSION }) })
  mock({ session_id: assessmentId, state: 'running', started_at: '2026-10-16T13:01:00Z', expires_at: common.expires_at })
  await expect(startParticipant(model)).rejects.toMatchObject({ code: 'invalid_response' })
})

test('conclusao mantem mesmo corpo imutavel em retries sem campos adicionais', async () => {
  const result = mainResult()
  Object.assign(result.trials[0]!, { participant_name: 'CAMPO_SINTETICO_PROIBIDO' })
  const payload = completionPayload(model, result)
  expect(Object.isFrozen(payload)).toBe(true)
  expect(Object.isFrozen(payload.trials[0])).toBe(true)
  expect(JSON.stringify(payload)).not.toContain('participant_name')
  const fetchMock = vi.fn().mockResolvedValueOnce(Response.json(receipt, { status: 201 }))
    .mockResolvedValueOnce(Response.json(receipt, { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  expect(await completeParticipant(model, payload)).toEqual(receipt)
  result.trials[0]!.key_pressed = null
  expect(await completeParticipant(model, payload)).toEqual(receipt)
  expect(fetchMock.mock.calls[0]![0]).toBe('/api/v1/participant/complete')
  const first = transport(fetchMock.mock.calls[0]!)
  const retry = transport(fetchMock.mock.calls[1]!)
  expect(first.body).toBe(retry.body)
  expect(JSON.parse(first.body as string).trials[1].reaction_time_ms).toBe(shared.cases[1]!.trials[1]!.reaction_time_ms)
  expect(() => completionPayload({ ...model, main_conditions: [...order].reverse() }, mainResult())).toThrow(ApiError)
})

test('aborto e keepalive com CSRF; recibos adulterados nao confirmam salvamento', async () => {
  const fetchMock = mock({ session_id: sessionId, state: 'aborted' })
  await abortParticipant(common.csrf_token, sessionId, 'reload')
  expect(transport(fetchMock.mock.calls[0]!)).toMatchObject({ keepalive: true, body: '{"reason":"reload"}',
    headers: { 'X-CSRF-Token': common.csrf_token } })
  const bad = structuredClone(receipt)
  bad.summary.hits += 1
  mock(bad, 201)
  await expect(completeParticipant(model, completionPayload(model, mainResult()))).rejects.toMatchObject({ code: 'invalid_response' })
  mock({ ...receipt, session_id: assessmentId }, 201)
  await expect(completeParticipant(model, completionPayload(model, mainResult()))).rejects.toMatchObject({ code: 'invalid_response' })
  mock({ error: { code: 'authentication_required', message: 'TEXTO_SINTETICO_NAO_CONFIAVEL' } }, 401)
  const error = await getParticipantSession().catch(error => error)
  expect(participantErrorMessage(error)).not.toContain('Google')
  expect(participantErrorMessage(error)).not.toContain('TEXTO_SINTETICO')
})

test('logout limpa acesso com CSRF e exige confirmacao 204', async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }))
  vi.stubGlobal('fetch', fetchMock)
  await logoutParticipant(common.csrf_token)
  expect(fetchMock.mock.calls[0]![0]).toBe('/api/v1/participant/logout')
  expect(transport(fetchMock.mock.calls[0]!)).toMatchObject({ method: 'POST', body: '{}',
    headers: { 'X-CSRF-Token': common.csrf_token } })
  mock({}, 200)
  await expect(logoutParticipant(common.csrf_token)).rejects.toMatchObject({ code: 'invalid_response' })
})
