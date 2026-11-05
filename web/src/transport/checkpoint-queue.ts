/** Executado no Dedicated Worker: nenhum HTTP/JSON/hash no caminho do motor. */
import { ApiError, record, request } from '../api/client'
import type { CompletePayload, PreparingSession } from '../api/participant'
import type { MainTrial } from '../experiment/main-engine'

export type TransportContext = Pick<PreparingSession, 'session_id' | 'csrf_token' | 'expires_at'> &
  Pick<CompletePayload, 'protocol_id' | 'test_version' | 'platform' | 'app_version'>
export type TransportStatus = { state: 'ready' | 'pending' | 'confirmed' | 'stopped';
  confirmed: number; queued: number; attempts: number; reason?: string }
type Checkpoint = { confirmed_through: number; prefix_hash: string | null; received_at: string | null }

function checkpoint(value: unknown): Checkpoint {
  if (!record(value) || Object.keys(value).length !== 3
    || !Number.isInteger(value.confirmed_through) || Number(value.confirmed_through) < 0
    || Number(value.confirmed_through) > 16
    || (value.confirmed_through === 0 ? value.prefix_hash !== null || value.received_at !== null
      : typeof value.prefix_hash !== 'string' || !/^[a-f0-9]{64}$/.test(value.prefix_hash)
        || typeof value.received_at !== 'string' || !Number.isFinite(Date.parse(value.received_at)))) {
    throw new ApiError('invalid_response', 200)
  }
  return value as Checkpoint
}

export class CheckpointQueue {
  private trials: Readonly<MainTrial>[] = []
  private framePeriod: number | undefined
  private confirmed = 0
  private attempts = 0
  private batch: CompletePayload | undefined
  private failures = 0
  private busy = false
  private stopped = false
  private ready = false
  private timer: ReturnType<typeof setTimeout> | undefined
  private expiry: ReturnType<typeof setTimeout> | undefined
  private readonly controller = new AbortController()

  constructor(private readonly context: TransportContext, private readonly notify: (status: TransportStatus) => void) {}
  private status(state: TransportStatus['state'], reason?: string) {
    this.notify({ state, confirmed: this.confirmed, queued: this.trials.length, attempts: this.attempts,
      ...(reason ? { reason } : {}) })
  }
  private alive() { return !this.stopped && Date.now() < Date.parse(this.context.expires_at) }
  private async session(preparing = false) {
    return request('/api/v1/participant/session', { method: 'GET', headers: { Accept: 'application/json' } }, async response => {
      const value: unknown = await response.json()
      if (!record(value) || value.session_id !== this.context.session_id
        || (preparing && (value.state !== 'preparing' || value.expires_at !== this.context.expires_at))) {
        throw new ApiError('invalid_response', response.status)
      }
      return checkpoint(value.checkpoint)
    }, this.controller.signal)
  }
  async prepare() {
    if (this.ready || this.stopped) throw new ApiError('state_conflict', 409)
    const remaining = Date.parse(this.context.expires_at) - Date.now()
    if (!Number.isFinite(remaining) || remaining <= 0 || remaining > 1_800_000) {
      this.stop('expired'); throw new ApiError('session_expired', 410)
    }
    this.expiry = setTimeout(() => this.stop('expired'), remaining)
    try {
      const receipt = await this.session(true)
      if (!this.alive() || receipt.confirmed_through !== 0) throw new ApiError('state_conflict', 409)
      this.ready = true
      this.status('ready')
    } catch (error) { this.stop('not_ready'); throw error }
  }
  enqueue(trial: Readonly<MainTrial>, framePeriod: number) {
    if (!this.alive()) return
    if (!this.ready || trial.trial_number !== this.trials.length + 1 || this.trials.length >= 16
      || !Number.isFinite(framePeriod) || framePeriod < 4 || framePeriod > 50
      || (this.framePeriod !== undefined && framePeriod !== this.framePeriod)
      || !Number.isFinite(trial.trial_end_ms) || !(trial.trial_end_ms > trial.stimulus_offset_ms)) {
      this.stop('invalid_observation'); return
    }
    this.framePeriod = framePeriod
    this.trials.push(Object.freeze({ ...trial }))
    // Eventos de status nao dirigem DOM/React nem agendamento experimental.
    void this.flush()
  }
  private accept(receipt: Checkpoint, sentThrough: number) {
    if (receipt.confirmed_through < this.confirmed || receipt.confirmed_through > sentThrough) {
      throw new ApiError('result_conflict', 409)
    }
    this.confirmed = receipt.confirmed_through
    return this.confirmed >= sentThrough
  }
  private async flush() {
    if (!this.alive() || this.busy || this.timer || this.confirmed === this.trials.length) return
    this.busy = true
    // Preservar exatamente o mesmo lote em retry; agrupar novas posicoes somente apos ACK.
    this.batch ??= { protocol_id: this.context.protocol_id, test_version: this.context.test_version,
      platform: this.context.platform, app_version: this.context.app_version,
      frame_period_ms: this.framePeriod!, trials: this.trials.slice(this.confirmed).map(row => ({ ...row })) }
    const batch = this.batch
    const sentThrough = batch.trials.at(-1)!.trial_number
    this.attempts += 1
    try {
      const receipt = await request('/api/v1/participant/session/checkpoints', {
        method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json',
          'X-CSRF-Token': this.context.csrf_token }, body: JSON.stringify(batch),
      }, async response => {
        const value: unknown = await response.json()
        if (response.status !== 200 || !record(value) || Object.keys(value).length !== 4
          || value.session_id !== this.context.session_id) throw new ApiError('invalid_response', response.status)
        const { session_id: _session, ...body } = value
        return checkpoint(body)
      }, this.controller.signal)
      if (!this.accept(receipt, sentThrough)) throw new ApiError('invalid_response', 200)
      this.batch = undefined; this.failures = 0
    } catch (caught) {
      if (!this.alive()) return
      let error = caught
      if (!(error instanceof ApiError) || error.status === 0 || error.status >= 500 || error.code === 'invalid_response') {
        try {
          if (this.accept(await this.session(), sentThrough)) { this.batch = undefined; this.failures = 0 }
        } catch (recoveryError) {
          if (recoveryError instanceof ApiError && recoveryError.status >= 400 && recoveryError.status < 500) error = recoveryError
        }
      }
      if (this.batch) {
        if (error instanceof ApiError && error.status >= 400 && error.status < 500 && error.status !== 429) {
          this.stop(error.status === 409 ? 'integrity' : 'access'); return
        }
        const backoff = Math.min(8, 2 ** Math.min(this.failures++, 3))
        const seconds = Math.max(backoff, error instanceof ApiError ? error.retryAfter ?? 0 : 0)
        this.timer = setTimeout(() => { this.timer = undefined; void this.flush() }, seconds * 1000)
      }
    } finally {
      this.busy = false
      if (this.alive()) {
        this.status(this.confirmed === this.trials.length ? 'confirmed' : 'pending')
        if (!this.timer) void this.flush()
      }
    }
  }
  stop(reason = 'disposed') {
    if (this.stopped) return
    this.stopped = true
    clearTimeout(this.timer); clearTimeout(this.expiry)
    this.controller.abort()
    this.status('stopped', reason)
    this.trials = []; this.batch = undefined
  }
}
