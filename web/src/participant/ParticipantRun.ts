/** Coordenacao em RAM: rede/credencial nunca participam do relogio experimental. */
import * as api from '../api/participant'
import type { AbortReason, CompletePayload, ParticipantSession, PreparingSession, Receipt } from '../api/participant'
import { ApiError } from '../api/client'
import type { MainResult } from '../experiment/main-engine'
import { summarizeMain } from '../experiment/summary'
import type { DisplaySummary } from '../experiment/summary'

type API = Pick<typeof api, 'getParticipantSession' | 'redeemInvitation' | 'startParticipant' |
  'completeParticipant' | 'abortParticipant' | 'logoutParticipant'>
export type ParticipantView =
  | { phase: 'loading' }
  | { phase: 'blocked'; message: string }
  | { phase: 'invite'; message: string | null; busy: boolean }
  | { phase: 'preparing'; session: PreparingSession }
  | { phase: 'result'; summary: DisplaySummary; delivery: 'sending' | 'pending' | 'saved';
      message: string | null; canRetry: boolean; finishing: boolean }

function uncertain(error: unknown) {
  return error instanceof ApiError && (error.status === 0 || error.status >= 500 || error.code === 'invalid_response')
}
function terminal(error: unknown) {
  return error instanceof ApiError && error.status >= 400 && error.status < 500 && error.status !== 429
}
function display(receipt: Receipt): DisplaySummary {
  return { accuracy: receipt.summary.accuracy, response_time: receipt.summary.response_time_seconds,
    total_trials: receipt.summary.total_trials, hits: receipt.summary.hits,
    omission_errors: receipt.summary.omission_errors, commission_errors: receipt.summary.commission_errors,
    correct_rejections: receipt.summary.correct_rejections }
}

export class ParticipantRun {
  private view: ParticipantView = { phase: 'loading' }
  private listeners = new Set<() => void>()
  private active = false
  private version = 0
  private io: AbortController | undefined
  private context: ParticipantSession | undefined
  private payload: CompletePayload | undefined
  private engineStarted = false
  private startAttempted = false
  private startPending = false
  private startPromise: Promise<void> | undefined
  private sending = false
  private expiry: ReturnType<typeof setTimeout> | undefined
  private retryTimer: ReturnType<typeof setTimeout> | undefined

  constructor(private readonly port: API = api) {}
  getSnapshot = (): ParticipantView => this.view
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener) } }
  private set(view: ParticipantView) { this.view = view; this.listeners.forEach(listener => listener()) }
  private current(version: number) { return this.active && version === this.version }
  private cancelIO() { this.version += 1; this.io?.abort(); this.io = undefined }
  private beginIO() { this.cancelIO(); this.io = new AbortController(); return { version: this.version, signal: this.io.signal } }
  private clear() {
    clearTimeout(this.expiry); clearTimeout(this.retryTimer)
    this.expiry = undefined; this.retryTimer = undefined
    this.context = undefined; this.payload = undefined
    this.engineStarted = false; this.startAttempted = false; this.startPending = false; this.sending = false
  }
  private invite(message: string | null) {
    this.cancelIO(); this.clear()
    this.set({ phase: 'invite', message, busy: false })
  }
  private deadline(expiresAt: string) {
    clearTimeout(this.expiry)
    const sessionId = this.context?.session_id
    // UX local conservadora; o servidor continua sendo a autoridade do prazo.
    const delay = Math.min(1_800_000, Math.max(0, Date.parse(expiresAt) - Date.now()))
    this.expiry = setTimeout(() => {
      if (!this.active || this.context?.session_id !== sessionId) return
      this.bestEffortAbort('user_cancelled')
      this.invite('Seu acesso expirou. Solicite um novo convite à equipe.')
    }, delay)
  }
  private bestEffortAbort(reason: AbortReason) {
    const context = this.context
    if (!context || context.state === 'completed') return
    void this.port.abortParticipant(context.csrf_token, context.session_id, reason).catch(() => undefined)
  }
  activate() { this.active = true; return this.load() }
  dispose(reason: AbortReason = 'user_cancelled', notify = false) {
    if (this.engineStarted || this.startAttempted || this.startPending) this.bestEffortAbort(reason)
    this.active = false; this.cancelIO(); this.clear(); this.view = { phase: 'loading' }
    if (notify) this.listeners.forEach(listener => listener())
  }
  blocked(message: string) { this.set({ phase: 'blocked', message }) }

  private async accept(session: ParticipantSession, version: number) {
    if (!this.current(version)) return
    this.context = session
    if (session.state === 'running') {
      // Pagina recarregada nao sabe quais estimulos ja foram apresentados.
      this.bestEffortAbort('reload')
      this.invite('A execução anterior foi interrompida. Solicite um novo convite e faça a prática novamente.')
    } else if (session.state === 'completed') {
      this.payload = undefined; this.engineStarted = false
      this.deadline(session.expires_at)
      this.set({ phase: 'result', summary: display(session), delivery: 'saved',
        message: null, canRetry: false, finishing: false })
    } else {
      this.deadline(session.expires_at)
      this.set({ phase: 'preparing', session })
    }
  }
  async load() {
    if (!this.active || this.engineStarted || this.startPending || this.sending) return
    const { version, signal } = this.beginIO()
    this.set({ phase: 'loading' })
    try { await this.accept(await this.port.getParticipantSession(signal), version) }
    catch (error) {
      if (this.current(version)) this.invite(error instanceof ApiError && error.status === 401
        ? null : api.participantErrorMessage(error))
    }
  }
  async redeem(code: string) {
    if (!this.active || this.view.phase !== 'invite' || this.view.busy) return
    const { version, signal } = this.beginIO()
    this.set({ phase: 'invite', message: null, busy: true })
    let redeemedId: string | undefined
    try {
      const redeemed = await this.port.redeemInvitation(code, signal)
      redeemedId = redeemed.session_id
      const session = await this.port.getParticipantSession(signal)
      if (session.session_id !== redeemed.session_id) throw new ApiError('invalid_response', 200)
      await this.accept(session, version)
    } catch (error) {
      if (!this.current(version)) return
      if (uncertain(error)) {
        try {
          const recovered = await this.port.getParticipantSession(signal)
          if (redeemedId && recovered.session_id !== redeemedId) throw new ApiError('state_conflict', 409)
          await this.accept(recovered, version); return
        }
        catch { /* Resposta de resgate perdida nao permite emitir outra credencial. */ }
      }
      if (this.current(version)) this.invite(api.participantErrorMessage(error))
    }
  }
  async start() {
    if (this.startPromise) return this.startPromise
    const context = this.context
    if (!this.active || !context || context.state !== 'preparing' || this.engineStarted) {
      throw new ApiError('state_conflict', 409)
    }
    const { version, signal } = this.beginIO()
    this.startPending = true; this.startAttempted = true
    const operation = this.port.startParticipant(context, signal).then(() => {
      if (!this.current(version)) throw new ApiError('request_cancelled', 0)
      this.engineStarted = true
    }).catch(error => {
      if (this.current(version) && terminal(error)) this.invite(api.participantErrorMessage(error))
      throw error
    }).finally(() => { if (this.current(version)) this.startPending = false })
    this.startPromise = operation
    try { await operation } finally { if (this.startPromise === operation) this.startPromise = undefined }
  }
  interrupt(reason: AbortReason) {
    if (!this.active) return
    this.bestEffortAbort(reason)
    this.invite((reason === 'timing_invalid' ? 'Não foi possível manter os tempos de apresentação nesta execução.'
      : 'A execução foi interrompida e não gerou resultado.') + ' Solicite um novo convite e faça a prática novamente.')
  }
  complete(result: MainResult) {
    const context = this.context
    if (!this.active || !this.engineStarted || !context || context.state !== 'preparing' || this.payload) return
    try {
      this.payload = api.completionPayload(context, result)
      const metrics = summarizeMain(result)
      const summary: DisplaySummary = { accuracy: metrics.accuracy, response_time: metrics.response_time,
        total_trials: metrics.total_trials, hits: metrics.hits, omission_errors: metrics.omission_errors,
        commission_errors: metrics.commission_errors, correct_rejections: metrics.correct_rejections }
      this.engineStarted = false
      this.set({ phase: 'result', summary, delivery: 'pending', message: null, canRetry: true, finishing: false })
      void this.send()
    } catch { this.interrupt('timing_invalid') }
  }
  private saved(receipt: Receipt, context: PreparingSession) {
    this.payload = undefined
    this.context = { ...receipt, csrf_token: context.csrf_token, expires_at: context.expires_at }
    this.set({ phase: 'result', summary: display(receipt), delivery: 'saved',
      message: null, canRetry: false, finishing: false })
  }
  async send() {
    const context = this.context
    const payload = this.payload
    if (!this.active || this.sending || !payload || !context || context.state !== 'preparing'
      || this.view.phase !== 'result' || !this.view.canRetry || this.view.finishing) return
    const summary = this.view.summary
    const { version, signal } = this.beginIO()
    this.sending = true
    this.set({ phase: 'result', summary, delivery: 'sending', message: null, canRetry: false, finishing: false })
    try {
      const receipt = await this.port.completeParticipant(context, payload, signal)
      if (this.current(version)) this.saved(receipt, context)
    } catch (error) {
      if (!this.current(version)) return
      if (uncertain(error)) {
        try {
          const recovered = await this.port.getParticipantSession(signal)
          if (!this.current(version)) return
          if (recovered.session_id !== context.session_id) throw new ApiError('state_conflict', 409)
          if (recovered.state === 'completed') {
            if (recovered.app_version !== payload.app_version) throw new ApiError('result_conflict', 409)
            this.saved(recovered, context); return
          }
          if (recovered.state !== 'running') throw new ApiError('state_conflict', 409)
        } catch (recoveryError) { if (terminal(recoveryError)) error = recoveryError }
      }
      if (!this.current(version)) return
      if (terminal(error)) { this.invite(api.participantErrorMessage(error)); return }
      const wait = error instanceof ApiError && error.status === 429 ? error.retryAfter ?? 1 : 0
      this.set({ phase: 'result', summary, delivery: 'pending', message: api.participantErrorMessage(error),
        canRetry: wait === 0, finishing: false })
      if (wait > 0) this.retryTimer = setTimeout(() => {
        if (this.current(version) && this.view.phase === 'result' && this.view.delivery === 'pending') {
          this.set({ ...this.view, canRetry: true })
        }
      }, Math.min(wait * 1000, 1_800_000))
    } finally { if (this.current(version)) this.sending = false }
  }
  async finish(): Promise<boolean> {
    if (!this.active || this.view.phase !== 'result' || this.view.finishing || this.sending) return false
    const before = this.view
    const context = this.context
    const { version, signal } = this.beginIO()
    this.set({ ...before, finishing: true, message: null })
    try {
      await this.port.logoutParticipant(context?.csrf_token, signal)
      if (!this.current(version)) return false
      this.invite(null)
      return true
    } catch (error) {
      if (this.current(version)) this.set({ ...before, finishing: false, message: api.participantErrorMessage(error) })
      return false
    }
  }
}
