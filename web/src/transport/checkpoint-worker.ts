import { ApiError } from '../api/client'
import type { MainTrial } from '../experiment/main-engine'
import type { TransportContext, TransportStatus } from './checkpoint-queue'
import type { TransportMessage } from './checkpoint.worker'

/** Preparar antes da contagem; falha do worker nunca degrada para envio final-only. */
export async function prepareCheckpointWorker(context: TransportContext,
  onStatus: (status: TransportStatus) => void = () => undefined) {
  if (typeof Worker !== 'function') throw new ApiError('service_unavailable', 503)
  const worker = new Worker(new URL('./checkpoint.worker.ts', import.meta.url), { type: 'module' })
  let disposed = false
  let retiring = false
  let enqueued = 0
  let latest: TransportStatus = { state: 'ready', confirmed: 0, queued: 0, attempts: 0 }
  let retireTimer: ReturnType<typeof setTimeout> | undefined
  const send = (message: TransportMessage) => worker.postMessage(message)
  const terminate = () => {
    clearTimeout(retireTimer)
    retireTimer = undefined
    worker.terminate()
  }
  try {
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new ApiError('request_timeout', 0)), 12_000)
      const failed = (error?: { code: string; status: number }) => {
        clearTimeout(timer)
        reject(error ? new ApiError(error.code, error.status) : new ApiError('service_unavailable', 503))
      }
      worker.onerror = () => failed()
      worker.onmessageerror = () => failed()
      worker.onmessage = (event: MessageEvent<TransportStatus>) => {
        latest = event.data
        onStatus(event.data)
        if (event.data.state === 'ready') { clearTimeout(timer); resolve() }
        else if (event.data.state === 'stopped') failed(event.data.error)
      }
      send({ type: 'prepare', context })
    })
  } catch (error) { terminate(); throw error }
  const failed = () => {
    latest = { state: 'stopped', confirmed: latest.confirmed, queued: latest.queued, attempts: latest.attempts, reason: 'worker_failed' }
    onStatus(latest)
    if (retiring) terminate()
  }
  worker.onerror = failed
  worker.onmessageerror = failed
  worker.onmessage = (event: MessageEvent<TransportStatus>) => {
    latest = event.data
    onStatus(event.data)
    if (retiring && (event.data.state === 'stopped' || (event.data.state === 'confirmed' && event.data.confirmed >= enqueued))) {
      terminate()
    }
  }
  return {
    enqueue(trial: Readonly<MainTrial>, framePeriod: number) {
      if (!disposed) {
        enqueued += 1
        send({ type: 'trial', trial, framePeriod })
      }
    },
    dispose(graceful = false) {
      if (disposed) return
      disposed = true
      if (!graceful || enqueued === 0 || latest.state === 'stopped'
        || (latest.state === 'confirmed' && latest.confirmed >= enqueued)) {
        terminate()
        return
      }
      retiring = true
      retireTimer = setTimeout(terminate, 5_000)
    },
  }
}
