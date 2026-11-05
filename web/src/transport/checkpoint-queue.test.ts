import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import shared from '../../../tests/fixtures/web_results_summary.json'
import { CheckpointQueue } from './checkpoint-queue'
import type { TransportContext, TransportStatus } from './checkpoint-queue'
import type { MainTrial } from '../experiment/main-engine'

const context: TransportContext = { session_id: 'synthetic-session', csrf_token: 's'.repeat(43),
  expires_at: '2026-11-05T13:30:00Z', protocol_id: 'stroop_go_nogo_ptbr/0.2.2-web.1',
  test_version: '0.2.2-web.1', platform: 'web', app_version: 'web-0.1.0+visual.1.0.0.transport.1' }
const rows = shared.cases[1]!.trials as MainTrial[]
const checkpoint = (n: number) => ({ confirmed_through: n, prefix_hash: n ? 'a'.repeat(64) : null,
  received_at: n ? '2026-11-05T13:00:00Z' : null })
const json = (body: unknown, status = 200, headers = {}) => new Response(JSON.stringify(body), { status, headers })
const session = (n = 0) => json({ ...context, state: 'preparing', checkpoint: checkpoint(n) })
const ack = (n: number) => json({ session_id: context.session_id, ...checkpoint(n) })
const fetchMock = vi.fn<typeof fetch>()
let queue: CheckpointQueue
let states: TransportStatus[]
const settle = async () => { for (let i = 0; i < 100; i++) await Promise.resolve() }
beforeEach(() => {
  vi.useFakeTimers(); vi.setSystemTime('2026-11-05T13:00:00Z')
  vi.stubGlobal('fetch', fetchMock); fetchMock.mockReset()
  states = []; queue = new CheckpointQueue(context, status => states.push(status))
  fetchMock.mockResolvedValueOnce(session())
})
afterEach(() => { queue.stop(); vi.useRealTimers(); vi.unstubAllGlobals() })

test('ACK lento nao bloqueia fila; um voo, prefixo contiguo e sem exposicao de segredo nos estados', async () => {
  await queue.prepare()
  let resolve!: (value: Response) => void
  fetchMock.mockImplementationOnce(() => new Promise(done => { resolve = done }))
  queue.enqueue(rows[0]!, 16.666667)
  queue.enqueue(rows[1]!, 16.666667)
  queue.enqueue(rows[2]!, 16.666667)
  expect(fetchMock).toHaveBeenCalledTimes(2)
  expect(JSON.parse(fetchMock.mock.calls[1]![1]!.body as string).trials).toEqual([rows[0]])
  fetchMock.mockResolvedValueOnce(ack(3))
  resolve(ack(1)); await settle()
  expect(JSON.parse(fetchMock.mock.calls[2]![1]!.body as string).trials).toEqual(rows.slice(1, 3))
  expect(states.at(-1)).toMatchObject({ state: 'confirmed', confirmed: 3, queued: 3 })
  expect(fetchMock.mock.calls[1]![1]).toMatchObject({ credentials: 'same-origin', cache: 'no-store', redirect: 'error' })
  expect(JSON.stringify(states)).not.toContain(context.csrf_token)
})

test('ACK perdido recupera prefixo por consulta e nao repete lote confirmado', async () => {
  await queue.prepare()
  fetchMock.mockRejectedValueOnce(new TypeError('network')).mockResolvedValueOnce(session(1))
  queue.enqueue(rows[0]!, 16.666667); await settle()
  expect(states.at(-1)).toMatchObject({ state: 'confirmed', confirmed: 1, attempts: 1 })
  expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(1)
})

test('retries usam 1/2/4/8 s, mesmo corpo e Retry-After; observacoes novas nao alteram lote em voo', async () => {
  await queue.prepare()
  fetchMock.mockImplementation(async (_path, init) => init?.method === 'POST'
    ? json({ error: { code: 'service_unavailable' } }, 503) : session())
  queue.enqueue(rows[0]!, 16.666667); await settle()
  queue.enqueue(rows[1]!, 16.666667)
  for (const delay of [1000, 2000, 4000, 8000]) {
    const before = fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST').length
    await vi.advanceTimersByTimeAsync(delay - 1)
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(before)
    await vi.advanceTimersByTimeAsync(1); await settle()
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST')).toHaveLength(before + 1)
  }
  const bodies = fetchMock.mock.calls.filter(([, init]) => init?.method === 'POST').map(([, init]) => init!.body)
  expect(new Set(bodies).size).toBe(1)
  fetchMock.mockResolvedValueOnce(json({ error: { code: 'rate_limited' } }, 429, { 'Retry-After': '20' }))
  await vi.advanceTimersByTimeAsync(8000)
  const count = fetchMock.mock.calls.length
  await vi.advanceTimersByTimeAsync(19999)
  expect(fetchMock.mock.calls.length).toBe(count)
  fetchMock.mockResolvedValueOnce(ack(1)).mockResolvedValueOnce(ack(2))
  await vi.advanceTimersByTimeAsync(1); await settle()
  expect(states.at(-1)).toMatchObject({ state: 'confirmed', confirmed: 2 })
})

for (const status of [401, 403, 409, 410]) test(`HTTP ${status} encerra envio sem sobrescrever nem reenviar`, async () => {
  await queue.prepare()
  fetchMock.mockResolvedValueOnce(json({ error: { code: status === 409 ? 'result_conflict' : 'permission_denied' } }, status))
  queue.enqueue(rows[0]!, 16.666667); await settle()
  expect(states.at(-1)).toMatchObject({ state: 'stopped', confirmed: 0, queued: 1 })
  const calls = fetchMock.mock.calls.length
  await vi.advanceTimersByTimeAsync(60_000)
  queue.enqueue(rows[1]!, 16.666667)
  expect(fetchMock.mock.calls).toHaveLength(calls)
})

test('expiracao cancela envio e nenhum evento posterior reabre a fila', async () => {
  await queue.prepare()
  fetchMock.mockImplementation(async (_path, init) => init?.method === 'POST'
    ? json({ error: { code: 'service_unavailable' } }, 503) : session())
  queue.enqueue(rows[0]!, 16.666667); await settle()
  await vi.advanceTimersByTimeAsync(1_800_000)
  expect(states.at(-1)).toMatchObject({ state: 'stopped', reason: 'expired' })
  const count = fetchMock.mock.calls.length
  queue.enqueue(rows[1]!, 16.666667)
  await vi.advanceTimersByTimeAsync(8000)
  expect(fetchMock.mock.calls).toHaveLength(count)
})

test('prefixo preexistente bloqueia prontidao e ACK adiantado falha integridade', async () => {
  fetchMock.mockReset().mockResolvedValueOnce(session(1))
  await expect(queue.prepare()).rejects.toMatchObject({ code: 'state_conflict' })
  expect(states.at(-1)).toMatchObject({ state: 'stopped' })
  queue = new CheckpointQueue(context, status => states.push(status))
  fetchMock.mockResolvedValueOnce(session())
  await queue.prepare()
  fetchMock.mockResolvedValueOnce(ack(2))
  queue.enqueue(rows[0]!, 16.666667); await settle()
  expect(states.at(-1)).toMatchObject({ state: 'stopped', reason: 'integrity' })
})
