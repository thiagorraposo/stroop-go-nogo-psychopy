import { ApiError, apiErrorMessage, record, request } from './client'
import { MAIN_CONDITIONS, PRACTICE_CONDITIONS, PROTOCOL } from '../experiment/protocol'
import type { Condition, InterruptionReason } from '../experiment/protocol'
import type { MainResult, MainTrial } from '../experiment/main-engine'
import { validMainResult } from '../experiment/main-engine'
import packageInfo from '../../package.json'

export const APP_VERSION = `web-${packageInfo.version}+visual.${PROTOCOL.visual.version}`
export const PROTOCOL_ID = 'stroop_go_nogo_ptbr/0.2.2-web.1'
export const TEST_VERSION = '0.2.2-web.1'
type CommonSession = { session_id: string; activated_at: string; expires_at: string; csrf_token: string }
export type PreparingSession = CommonSession & {
  state: 'preparing'; protocol_id: typeof PROTOCOL_ID; test_version: typeof TEST_VERSION;
  main_conditions: readonly Condition[]
}
export type RunningSession = CommonSession & { state: 'running' }
export type Receipt = {
  session_id: string; assessment_id: string; state: 'completed'; completed_at: string;
  platform: 'web'; test_code: 'stroop_go_nogo_ptbr'; test_version: typeof TEST_VERSION;
  protocol_id: typeof PROTOCOL_ID; app_version: string;
  summary: { accuracy: number; response_time_seconds: number | null; total_trials: number;
    hits: number; omission_errors: number; commission_errors: number; correct_rejections: number }
}
export type CompletedSession = Receipt & { csrf_token: string; expires_at: string }
export type ParticipantSession = PreparingSession | RunningSession | CompletedSession
export type CompletePayload = {
  protocol_id: typeof PROTOCOL_ID; test_version: typeof TEST_VERSION; platform: 'web';
  app_version: string; frame_period_ms: number; trials: readonly Readonly<MainTrial>[]
}
export type AbortReason = InterruptionReason | 'reload' | 'user_cancelled'

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
function invalid(status = 200): never { throw new ApiError('invalid_response', status) }
function closed(value: unknown, fields: readonly string[]): value is Record<string, unknown> {
  return record(value) && Object.keys(value).length === fields.length && fields.every(key => Object.hasOwn(value, key))
}
function utc(value: unknown): value is string {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/.test(value)
    && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 19) === value.slice(0, 19)
}
function common(value: Record<string, unknown>): CommonSession {
  if (typeof value.session_id !== 'string' || !uuid.test(value.session_id)
    || !utc(value.activated_at) || !utc(value.expires_at)
    || !(Date.parse(value.expires_at) > Date.parse(value.activated_at))
    || Date.parse(value.expires_at) - Date.parse(value.activated_at) > 1_800_000
    || typeof value.csrf_token !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(value.csrf_token)) invalid()
  return { session_id: value.session_id, activated_at: value.activated_at,
    expires_at: value.expires_at, csrf_token: value.csrf_token }
}
function same(value: unknown, expected: unknown): boolean {
  if (Object.is(value, expected)) return true
  if (!record(value) || !record(expected)) return false
  const keys = Object.keys(expected)
  return Object.keys(value).length === keys.length && keys.every(key => same(value[key], expected[key]))
}
function conditions(value: unknown, pool: readonly Condition[], main: boolean): Condition[] {
  if (!Array.isArray(value) || value.length !== pool.length) invalid()
  const ids = new Set<number>()
  return value.map((item: unknown, index) => {
    const keys = ['condition_id', 'word', 'ink_color', 'ink_color_display', 'condition', 'correct_response']
    if (main) keys.push('trial_number')
    if (!closed(item, keys) || typeof item.condition_id !== 'number' || !Number.isInteger(item.condition_id)
      || ids.has(item.condition_id) || (main && item.trial_number !== index + 1)) invalid()
    const source = pool.find(row => row.condition_id === item.condition_id)
    if (!source || !Object.entries(source).every(([key, expected]) => item[key] === expected)) invalid()
    ids.add(item.condition_id)
    return { ...source }
  })
}
function receipt(value: unknown): Receipt {
  if (!closed(value, ['session_id', 'assessment_id', 'state', 'completed_at', 'platform',
    'test_code', 'test_version', 'protocol_id', 'app_version', 'summary'])
    || typeof value.session_id !== 'string' || !uuid.test(value.session_id)
    || typeof value.assessment_id !== 'string' || !uuid.test(value.assessment_id)
    || value.state !== 'completed' || !utc(value.completed_at) || value.platform !== 'web'
    || value.test_code !== 'stroop_go_nogo_ptbr' || value.test_version !== TEST_VERSION
    || value.protocol_id !== PROTOCOL_ID || typeof value.app_version !== 'string'
    || !/^[A-Za-z0-9_.+-]{1,64}$/.test(value.app_version)
    || !closed(value.summary, ['accuracy', 'response_time_seconds', 'total_trials', 'hits',
      'omission_errors', 'commission_errors', 'correct_rejections'])) invalid()
  const summary = value.summary
  for (const key of ['total_trials', 'hits', 'omission_errors', 'commission_errors', 'correct_rejections']) {
    if (typeof summary[key] !== 'number' || !Number.isInteger(summary[key]) || summary[key] < 0 || summary[key] > 16) invalid()
  }
  if (summary.total_trials !== 16 || Number(summary.hits) + Number(summary.omission_errors) !== 8
    || Number(summary.correct_rejections) + Number(summary.commission_errors) !== 8
    || summary.accuracy !== (Number(summary.hits) + Number(summary.correct_rejections)) / 16 * 100
    || (summary.hits === 0 ? summary.response_time_seconds !== null
      : typeof summary.response_time_seconds !== 'number' || !Number.isFinite(summary.response_time_seconds)
        || !(summary.response_time_seconds > 0 && summary.response_time_seconds < 2.5))) invalid()
  return value as unknown as Receipt
}
function session(value: unknown): PreparingSession | RunningSession | Receipt {
  if (!record(value)) invalid()
  if (value.valid_for_result === false || value.state === 'aborted') throw new ApiError('state_conflict', 409)
  if (Object.hasOwn(value, 'checkpoint')) {
    const checkpoint = value.checkpoint
    if (!closed(checkpoint, ['confirmed_through', 'prefix_hash', 'received_at'])
      || !Number.isInteger(checkpoint.confirmed_through) || Number(checkpoint.confirmed_through) < 0
      || Number(checkpoint.confirmed_through) > 16
      || (checkpoint.confirmed_through === 0 ? checkpoint.prefix_hash !== null || checkpoint.received_at !== null
        : typeof checkpoint.prefix_hash !== 'string' || !/^[a-f0-9]{64}$/.test(checkpoint.prefix_hash) || !utc(checkpoint.received_at))) invalid()
    const { checkpoint: _checkpoint, ...body } = value
    value = body
  }
  if (!record(value)) invalid()
  if (value.state === 'completed') return receipt(value)
  const keys = ['session_id', 'state', 'activated_at', 'expires_at', 'csrf_token', 'can_resume']
  if (value.state === 'running') {
    if (!closed(value, keys) || value.can_resume !== false) invalid()
    return { ...common(value), state: 'running' }
  }
  keys.push('protocol_id', 'test_code', 'test_version', 'platform', 'protocol', 'practice_conditions', 'main_conditions')
  if (!closed(value, keys) || value.can_resume !== false || value.state !== 'preparing'
    || value.protocol_id !== PROTOCOL_ID || value.test_code !== 'stroop_go_nogo_ptbr'
    || value.test_version !== TEST_VERSION || value.platform !== 'web' || !same(value.protocol, PROTOCOL)) invalid()
  conditions(value.practice_conditions, PRACTICE_CONDITIONS, false)
  return { ...common(value), state: 'preparing', protocol_id: PROTOCOL_ID, test_version: TEST_VERSION,
    main_conditions: conditions(value.main_conditions, MAIN_CONDITIONS, true) }
}
async function json(response: Response): Promise<unknown> {
  try { return await response.json() } catch { return invalid(response.status) }
}
const accept = { Accept: 'application/json' }
function post(body: unknown, csrf?: string): RequestInit {
  return { method: 'POST', headers: { ...accept, 'Content-Type': 'application/json',
    ...(csrf === undefined ? {} : { 'X-CSRF-Token': csrf }) }, body: JSON.stringify(body) }
}

export function getParticipantSession(signal?: AbortSignal): Promise<ParticipantSession> {
  return request('/api/v1/participant/session', { method: 'GET', headers: accept }, async response => {
    if (response.status !== 200) invalid(response.status)
    const value = session(await json(response))
    if (value.state !== 'completed') return value
    const csrf = response.headers.get('X-CSRF-Token')
    const expires = response.headers.get('X-Session-Expires-At')
    if (!csrf || !/^[A-Za-z0-9_-]{43}$/.test(csrf) || !utc(expires)) invalid()
    return { ...value, csrf_token: csrf, expires_at: expires }
  }, signal)
}
export function redeemInvitation(code: string, signal?: AbortSignal): Promise<CommonSession> {
  if (!/^[A-Za-z0-9_-]{32,128}$/.test(code)) throw new ApiError('invalid_request', 422)
  return request('/api/v1/participant/redeem', post({ code }), async response => {
    if (response.status !== 201) invalid(response.status)
    const value = await json(response)
    if (!closed(value, ['session_id', 'state', 'activated_at', 'expires_at', 'csrf_token']) || value.state !== 'preparing') invalid(201)
    return common(value)
  }, signal)
}
export function startParticipant(preparing: PreparingSession, signal?: AbortSignal): Promise<void> {
  return request('/api/v1/participant/start', post({ app_version: APP_VERSION }, preparing.csrf_token), async response => {
    if (response.status !== 200) invalid(response.status)
    const value = await json(response)
    if (!closed(value, ['session_id', 'state', 'started_at', 'expires_at'])
      || value.session_id !== preparing.session_id || value.state !== 'running'
      || !utc(value.started_at) || value.expires_at !== preparing.expires_at) invalid()
  }, signal)
}
export function completionPayload(preparing: PreparingSession, result: MainResult): CompletePayload {
  if (!validMainResult(result) || result.order.some((row, index) =>
    row.condition_id !== preparing.main_conditions[index]?.condition_id)) throw new ApiError('invalid_result', 422)
  return Object.freeze({ protocol_id: preparing.protocol_id, test_version: preparing.test_version,
    platform: 'web', app_version: APP_VERSION, frame_period_ms: result.frame_period_ms,
    trials: Object.freeze(result.trials.map(trial => Object.freeze({
      trial_number: trial.trial_number, condition_id: trial.condition_id,
      key_pressed: trial.key_pressed, reaction_time_ms: trial.reaction_time_ms,
      trial_start_ms: trial.trial_start_ms, stimulus_onset_ms: trial.stimulus_onset_ms,
      stimulus_offset_ms: trial.stimulus_offset_ms, trial_end_ms: trial.trial_end_ms,
      key_at_ms: trial.key_at_ms,
    }))) })
}
export function completeParticipant(preparing: PreparingSession, payload: CompletePayload, signal?: AbortSignal): Promise<Receipt> {
  return request('/api/v1/participant/complete', post(payload, preparing.csrf_token), async response => {
    if (response.status !== 200 && response.status !== 201) invalid(response.status)
    const value = receipt(await json(response))
    if (value.session_id !== preparing.session_id || value.app_version !== payload.app_version) invalid(response.status)
    return value
  }, signal)
}
export function abortParticipant(csrf: string, sessionId: string, reason: AbortReason): Promise<void> {
  return request('/api/v1/participant/abort', { ...post({ reason }, csrf), keepalive: true }, async response => {
    if (response.status !== 200) invalid(response.status)
    const value = await json(response)
    if (!closed(value, ['session_id', 'state']) || value.session_id !== sessionId || value.state !== 'aborted') invalid()
  })
}
export function invalidateParticipant(csrf: string, sessionId: string, reason: AbortReason,
  eventAtMs: number | null = null): Promise<boolean> {
  return request('/api/v1/participant/session/invalidate',
    { ...post({ reason, event_at_ms: eventAtMs }, csrf), keepalive: true }, async response => {
      if (response.status !== 200) invalid(response.status)
      const value = await json(response)
      if (!closed(value, ['session_id', 'valid_for_result']) || value.session_id !== sessionId
        || typeof value.valid_for_result !== 'boolean') invalid()
      return value.valid_for_result
    })
}
export function participantErrorMessage(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) return 'Este acesso não está disponível. Utilize um convite válido.'
  if (error instanceof ApiError && error.code === 'csrf_failed') return 'Não foi possível verificar este acesso. Entre em contato com a equipe.'
  if (error instanceof ApiError && error.code === 'state_conflict') {
    return 'Esta sessão não pode continuar e não gerou resultado oficial. Observações parciais não permitem retomada; solicite um novo convite à equipe.'
  }
  return apiErrorMessage(error)
}

export function logoutParticipant(csrf?: string, signal?: AbortSignal): Promise<void> {
  return request('/api/v1/participant/logout', post({}, csrf), async response => {
    if (response.status !== 204) invalid(response.status)
  }, signal)
}
