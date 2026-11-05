import type { MainTrial } from '../experiment/main-engine'
import type { TransportContext, TransportStatus } from './checkpoint-queue'
import type { TransportMessage } from './checkpoint.worker'

/** Preparar antes da contagem; falha do worker nunca degrada para envio final-only. */
export async function prepareCheckpointWorker(context: TransportContext,
  onStatus: (status: TransportStatus) => void = () => undefined) {
  const worker = new Worker(new URL('./checkpoint.worker.ts', import.meta.url), { type: 'module' })
  let disposed = false
  const send = (message: TransportMessage) => worker.postMessage(message)
  try {
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('transport_not_ready')), 12_000)
      const failed = () => { clearTimeout(timer); reject(new Error('transport_not_ready')) }
      worker.onerror = failed
      worker.onmessageerror = failed
      worker.onmessage = (event: MessageEvent<TransportStatus>) => {
        onStatus(event.data)
        if (event.data.state === 'ready') { clearTimeout(timer); resolve() }
        else if (event.data.state === 'stopped') failed()
      }
      send({ type: 'prepare', context })
    })
  } catch (error) { worker.terminate(); throw error }
  const failed = () => onStatus({ state: 'stopped', confirmed: 0, queued: 0, attempts: 0, reason: 'worker_failed' })
  worker.onerror = failed
  worker.onmessageerror = failed
  return {
    enqueue(trial: Readonly<MainTrial>, framePeriod: number) {
      if (!disposed) send({ type: 'trial', trial, framePeriod })
    },
    dispose() { if (!disposed) { disposed = true; worker.terminate() } },
  }
}
