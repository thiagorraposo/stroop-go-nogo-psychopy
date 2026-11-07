import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import shared from '../../../tests/fixtures/web_results_summary.json'
import { ApiError } from '../api/client'
import { APP_VERSION, PROTOCOL_ID, TEST_VERSION } from '../api/participant'
import type { CompletedSession, PreparingSession, Receipt, RunningSession } from '../api/participant'
import { MAIN_CONDITIONS } from '../experiment/protocol'
import type { MainResult, MainTrial } from '../experiment/main-engine'
import { ParticipantRun } from './ParticipantRun'

const common = { session_id: '00000000-0000-4000-8000-000000000130',
  activated_at: '2026-10-16T13:00:00Z', expires_at: '2026-10-16T13:30:00Z', csrf_token: 's'.repeat(43) }
const preparing: PreparingSession = { ...common, state: 'preparing', protocol_id: PROTOCOL_ID,
  test_version: TEST_VERSION, main_conditions: shared.cases[1]!.order.map(id => MAIN_CONDITIONS.find(row => row.condition_id === id)!) }
const running: RunningSession = { ...common, state: 'running' }
const metrics = shared.cases[1]!.expected_summary
const receipt: Receipt = { session_id: common.session_id, assessment_id: '00000000-0000-4000-8000-000000000131',
  state: 'completed', completed_at: '2026-10-16T13:02:00Z', platform: 'web', test_code: 'stroop_go_nogo_ptbr',
  test_version: TEST_VERSION, protocol_id: PROTOCOL_ID, app_version: APP_VERSION,
  summary: { accuracy: metrics.accuracy, response_time_seconds: metrics.response_time, total_trials: 16,
    hits: metrics.hits, omission_errors: metrics.omission_errors, commission_errors: metrics.commission_errors,
    correct_rejections: metrics.correct_rejections } }
const completed: CompletedSession = { ...receipt, csrf_token: common.csrf_token, expires_at: common.expires_at }
const result = (): MainResult => ({ order: structuredClone(preparing.main_conditions), frame_period_ms: 16.666667,
  trials: structuredClone(shared.cases[1]!.trials) as MainTrial[] })
const ports = () => ({ getParticipantSession: vi.fn().mockResolvedValue(preparing),
  redeemInvitation: vi.fn().mockResolvedValue(common), startParticipant: vi.fn().mockResolvedValue(undefined),
  completeParticipant: vi.fn().mockResolvedValue(receipt), abortParticipant: vi.fn().mockResolvedValue(undefined),
  logoutParticipant: vi.fn().mockResolvedValue(undefined) })
const runs: ParticipantRun[] = []
const make = (port = ports()) => { const run = new ParticipantRun(port); runs.push(run); return { run, port } }
const settle = async () => { for (let step = 0; step < 10; step++) await Promise.resolve() }
beforeEach(() => { vi.useFakeTimers(); vi.setSystemTime('2026-10-16T13:05:00Z') })
afterEach(() => { runs.splice(0).forEach(run => run.dispose()); vi.useRealTimers() })

test('pagina running aborta reload sem executar nem concluir novamente', async () => {
  const port = ports()
  port.getParticipantSession.mockResolvedValue(running)
  const { run } = make(port)
  await run.activate()
  expect(port.abortParticipant).toHaveBeenCalledExactlyOnceWith(common.csrf_token, common.session_id, 'reload')
  expect(run.getSnapshot()).toMatchObject({ phase: 'invite', busy: false })
  expect(port.startParticipant).not.toHaveBeenCalled()
  expect(port.completeParticipant).not.toHaveBeenCalled()
})

test('duplo clique compartilha start e nenhuma confirmacao de envio e antecipada', async () => {
  const { run, port } = make()
  await run.activate()
  let started!: () => void
  port.startParticipant.mockImplementationOnce(() => new Promise<void>(resolve => { started = resolve }))
  const first = run.start()
  const second = run.start()
  expect(port.startParticipant).toHaveBeenCalledTimes(1)
  started()
  await Promise.all([first, second])
  let accepted!: (value: Receipt) => void
  port.completeParticipant.mockImplementationOnce(() => new Promise<Receipt>(resolve => { accepted = resolve }))
  run.complete(result())
  await run.send()
  expect(port.completeParticipant).toHaveBeenCalledTimes(1)
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'sending', canRetry: false })
  accepted(receipt)
  await settle()
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'saved', summary: { hits: metrics.hits } })
  expect(JSON.stringify(run.getSnapshot())).not.toContain('trial_start_ms')
  expect(JSON.stringify(run.getSnapshot())).not.toContain('csrf_token')
  await run.send()
  expect(port.completeParticipant).toHaveBeenCalledTimes(1)
})

test('resposta perdida recupera recibo confirmado sem novo envio', async () => {
  const { run, port } = make()
  await run.activate(); await run.start()
  port.completeParticipant.mockRejectedValueOnce(new ApiError('request_timeout', 0))
  port.getParticipantSession.mockResolvedValueOnce(completed)
  run.complete(result()); await settle()
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'saved' })
  expect(port.completeParticipant).toHaveBeenCalledTimes(1)
})

test('falha de rede conserva somente payload original e retry nao repete tarefa', async () => {
  const { run, port } = make()
  await run.activate(); await run.start()
  port.completeParticipant.mockRejectedValueOnce(new ApiError('network_error', 0))
  port.getParticipantSession.mockResolvedValueOnce(running)
  run.complete(result()); await settle()
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'pending', canRetry: true })
  const payload = port.completeParticipant.mock.calls[0]![1]
  await run.send()
  expect(port.completeParticipant.mock.calls[1]![1]).toBe(payload)
  expect(port.startParticipant).toHaveBeenCalledTimes(1)
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'saved' })
  expect(await run.finish()).toBe(true)
  expect(port.logoutParticipant.mock.calls[0]![0]).toBe(common.csrf_token)
  expect(run.getSnapshot()).toEqual({ phase: 'invite', message: null, busy: false })
})

test('start pode repetir mesmo corpo antes de executar; erro fatal nao reinicia', async () => {
  const { run, port } = make()
  await run.activate()
  port.startParticipant.mockRejectedValueOnce(new ApiError('request_timeout', 0))
  await expect(run.start()).rejects.toMatchObject({ code: 'request_timeout' })
  expect(run.getSnapshot()).toMatchObject({ phase: 'preparing' })
  await run.start()
  expect(port.startParticipant.mock.calls[1]![0]).toBe(port.startParticipant.mock.calls[0]![0])
  await expect(run.start()).rejects.toMatchObject({ code: 'state_conflict' })
  run.interrupt('focus_lost')
  expect(port.abortParticipant).toHaveBeenCalledWith(common.csrf_token, common.session_id, 'focus_lost')
  expect(run.getSnapshot()).toMatchObject({ phase: 'invite' })
})

test('expiracao descarta payload nao confirmado e impede qualquer retry', async () => {
  const { run, port } = make()
  await run.activate(); await run.start()
  port.completeParticipant.mockRejectedValueOnce(new ApiError('network_error', 0))
  port.getParticipantSession.mockResolvedValueOnce(running)
  run.complete(result()); await settle()
  vi.advanceTimersByTime(25 * 60 * 1000)
  expect(run.getSnapshot()).toMatchObject({ phase: 'invite', busy: false })
  await run.send()
  expect(port.completeParticipant).toHaveBeenCalledTimes(1)
  expect(JSON.stringify(run.getSnapshot())).not.toContain('trial')
})

test('desmontagem cancela operacao e nao aceita inicio atrasado', async () => {
  const { run, port } = make()
  await run.activate()
  let resolve!: () => void
  port.startParticipant.mockImplementationOnce(() => new Promise<void>(done => { resolve = done }))
  const failed = expect(run.start()).rejects.toMatchObject({ code: 'request_cancelled' })
  run.dispose()
  expect(port.startParticipant.mock.calls[0]![1].aborted).toBe(true)
  resolve(); await failed
  expect(run.getSnapshot()).toEqual({ phase: 'loading' })
  expect(port.abortParticipant).toHaveBeenCalledWith(common.csrf_token, common.session_id, 'user_cancelled')
})

test('resgate perdido consulta credencial existente sem reutilizar o codigo', async () => {
  const port = ports()
  port.getParticipantSession.mockRejectedValueOnce(new ApiError('authentication_required', 401))
  port.redeemInvitation.mockRejectedValueOnce(new ApiError('network_error', 0))
  const { run } = make(port)
  await run.activate()
  await run.redeem('c'.repeat(43))
  expect(run.getSnapshot()).toMatchObject({ phase: 'preparing' })
  expect(port.redeemInvitation).toHaveBeenCalledTimes(1)
})

test('429 impede reenvio imediato; erro fatal nunca confirma nem reenvia', async () => {
  const { run, port } = make()
  await run.activate(); await run.start()
  port.completeParticipant.mockRejectedValueOnce(new ApiError('rate_limited', 429, 2))
  run.complete(result()); await settle()
  await run.send()
  expect(port.completeParticipant).toHaveBeenCalledTimes(1)
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'pending', canRetry: false })
  vi.advanceTimersByTime(2000)
  port.completeParticipant.mockRejectedValueOnce(new ApiError('session_expired', 410))
  await run.send()
  expect(run.getSnapshot()).toMatchObject({ phase: 'invite' })
  await run.send()
  expect(port.completeParticipant).toHaveBeenCalledTimes(2)
})

test('worker incremental bloqueia inicio quando indisponivel, encaminha tentativas e preserva parcial na interrupcao', async () => {
  const port = { ...ports(), invalidateParticipant: vi.fn().mockResolvedValue(false) }
  const enqueue = vi.fn()
  const dispose = vi.fn()
  const prepareTransport = vi.fn()
    .mockRejectedValueOnce(new ApiError('service_unavailable', 503))
    .mockImplementation(async (_context, onStatus) => {
      onStatus?.({ state: 'ready', confirmed: 0, queued: 0, attempts: 0 })
      return { enqueue, dispose }
    })
  const run = new ParticipantRun(port, prepareTransport)
  runs.push(run)
  await run.activate()
  await expect(run.start()).rejects.toMatchObject({ code: 'service_unavailable' })
  // Tentativa nao deve ser encaminhada se o worker nao ficou pronto.
  run.recordTrial(result().trials[0]!, 16.666667)
  expect(enqueue).not.toHaveBeenCalled()
  await run.start()
  expect(prepareTransport).toHaveBeenCalledTimes(2)
  run.recordTrial(result().trials[0]!, 16.666667)
  expect(enqueue).toHaveBeenCalledExactlyOnceWith(result().trials[0], 16.666667)
  run.interrupt('escape')
  expect(dispose).toHaveBeenCalledWith(true)
  expect(run.getSnapshot()).toMatchObject({
    phase: 'invite',
    message: expect.stringContaining('observação parcial, sem gerar resultado oficial'),
  })
})

test('invalidacao tardia apos conclusao distingue evento antes e depois do fim do bloco', async () => {
  const port = { ...ports(), invalidateParticipant: vi.fn().mockResolvedValueOnce(true).mockResolvedValueOnce(false) }
  const run = new ParticipantRun(port)
  runs.push(run)
  await run.activate(); await run.start()
  run.complete(result()); await settle()
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'saved' })
  // Evento apos o encerramento integro (valid_for_result: true) preserva o resultado salvo.
  await run.invalidate('focus_lost', 60001)
  expect(run.getSnapshot()).toMatchObject({ phase: 'result', delivery: 'saved' })
  // Violacao tardia anterior ao fim (valid_for_result: false) invalida o resultado e exige novo convite/pratica.
  await run.invalidate('visibility_hidden', 59000)
  expect(port.invalidateParticipant).toHaveBeenCalledTimes(2)
  expect(run.getSnapshot()).toMatchObject({
    phase: 'invite',
    message: expect.stringContaining('invalidada e não possui resultado oficial'),
  })
})
