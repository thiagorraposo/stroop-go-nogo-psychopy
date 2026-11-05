import { CheckpointQueue } from './checkpoint-queue'
import type { TransportContext } from './checkpoint-queue'
import type { MainTrial } from '../experiment/main-engine'

export type TransportMessage = { type: 'prepare'; context: TransportContext } |
  { type: 'trial'; trial: Readonly<MainTrial>; framePeriod: number } | { type: 'stop' }
let queue: CheckpointQueue | undefined
self.onmessage = (event: MessageEvent<TransportMessage>) => {
  const message = event.data
  if (message.type === 'prepare') {
    if (queue) return
    queue = new CheckpointQueue(message.context, status => self.postMessage(status))
    void queue.prepare().catch(() => undefined) // Estado seguro comunicado por stopped.
  } else if (message.type === 'trial') queue?.enqueue(message.trial, message.framePeriod)
  else { queue?.stop(); self.close() }
}
