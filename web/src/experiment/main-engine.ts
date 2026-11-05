import { createExperimentHud } from './presentation'
import { MAIN_CONDITIONS, PROTOCOL } from './protocol'
import type { Condition, InterruptionReason } from './protocol'

export type MainTrial = {
  trial_number: number
  condition_id: number
  key_pressed: 'space' | null
  reaction_time_ms: number | null
  trial_start_ms: number
  stimulus_onset_ms: number
  stimulus_offset_ms: number
  trial_end_ms: number
  key_at_ms: number | null
}
export type MainResult = { frame_period_ms: number; trials: MainTrial[]; order: readonly Condition[] }
export type MainTimingTransition = {
  type: 'trial_start' | 'stimulus_onset' | 'stimulus_offset' | 'trial_end'
  trial_number: number
  condition_id: number
  planned_elapsed_ms: number
  observed_elapsed_ms: number
  raf_elapsed_ms: number | null
}
export type MainTimingKeyEvent = {
  type: 'keydown' | 'keyup'
  key: 'Space' | 'Escape'
  phase: Phase
  elapsed_since_runtime_start_ms: number | null
  elapsed_since_main_origin_ms: number | null
  repeat: boolean
  held_before_event: boolean
}
export type MainTimingTrace = {
  schema: 'stroop-w16-timing-trace-v1'
  outcome: 'completed' | 'interrupted'
  interruption_reason: InterruptionReason | null
  countdown_frame_intervals_ms: number[]
  frame_period_ms: number | null
  main_origin_since_runtime_start_ms: number | null
  transitions: MainTimingTransition[]
  keyboard_events: MainTimingKeyEvent[]
}
export type MainOptions = {
  order: readonly Condition[]
  initiallyHeldKeys?: readonly string[]
  onComplete(result: MainResult): void
  onInterrupted(reason: InterruptionReason): void
  onTimingTrace?(trace: MainTimingTrace): void
}
export type MainClock = {
  now(): number
  requestFrame(callback: FrameRequestCallback): number
  cancelFrame(handle: number): void
}
type Phase = 'countdown' | 'fixation' | 'stimulus' | 'blank'
const countdown = ['Prepare-se', '3', '2', '1', 'Começar'] as const
const defaultClock: MainClock = {
  now: () => performance.now(), requestFrame: callback => requestAnimationFrame(callback),
  cancelFrame: handle => cancelAnimationFrame(handle),
}

function validOrder(order: readonly Condition[]): boolean {
  return order.length === 16 && new Set(order.map(row => row.condition_id)).size === 16
    && order.every(row => {
      const source = MAIN_CONDITIONS.find(condition => condition.condition_id === row.condition_id)
      return Number.isInteger(row.condition_id) && source !== undefined && row.word === source.word
        && row.ink_color === source.ink_color && row.condition === source.condition
        && row.correct_response === source.correct_response
        && row.ink_color_display === PROTOCOL.colors[source.ink_color]
    })
    && order.filter(row => row.condition === 'congruent').length === 8
}

/** Compara os decimais serializados sem arredondar tempos, como Decimal(str)
 * no validador Python. Evita aceitar/rejeitar uma igualdade por erro binario
 * de uma subtracao intermediaria no proprio gate. */
function within(terms: number[], limit: number): boolean {
  const decimals = [...terms, limit].map(value => {
    const [mantissa, exponent] = value.toString().toLowerCase().split('e')
    const fraction = mantissa!.split('.')[1]?.length ?? 0
    return { coefficient: BigInt(mantissa!.replace('.', '')), exponent: Number(exponent ?? 0) - fraction }
  })
  const scale = Math.min(...decimals.map(value => value.exponent))
  const integers = decimals.map(value => value.coefficient * 10n ** BigInt(value.exponent - scale))
  const bound = integers.pop()!
  const sum = integers.reduce((total, value) => total + value, 0n)
  return (sum < 0n ? -sum : sum) <= bound
}

/** Gate completo de consistencia do contrato; nao certifica latencia fisica. */
export function validMainResult(result: MainResult): boolean {
  const frame = result.frame_period_ms
  if (!Number.isFinite(frame) || frame < 4 || frame > 50 || !validOrder(result.order)
    || result.trials.length !== 16) return false
  let previousEnd = 0
  for (const [index, trial] of result.trials.entries()) {
    const s = trial.trial_start_ms
    const onset = trial.stimulus_onset_ms
    const offset = trial.stimulus_offset_ms
    const end = trial.trial_end_ms
    if (trial.trial_number !== index + 1 || trial.condition_id !== result.order[index]!.condition_id
      || ![s, onset, offset, end].every(Number.isFinite)
      || !(0 <= s && s < onset && onset < offset && offset < end && end <= 60100)
      || s !== previousEnd || !within([s, -index * 3750], frame)
      || !within([onset, -s, -300], frame) || !within([offset, -s, -2800], frame)
      || !within([end, -s, -3750], frame) || !within([offset, -onset, -2500], frame)) return false
    if (trial.key_pressed === null) {
      if (trial.reaction_time_ms !== null || trial.key_at_ms !== null) return false
    } else {
      const rt = trial.reaction_time_ms
      const keyAt = trial.key_at_ms
      if (trial.key_pressed !== 'space' || rt === null || keyAt === null
        || !Number.isFinite(rt) || !Number.isFinite(keyAt) || !(rt > 0 && rt < 2500)
        || !Number.isFinite(rt / 1000) || rt / 1000 <= 0
        || !(onset < keyAt && keyAt < offset) || !within([keyAt, -onset, -rt], 0.001)) return false
    }
    previousEnd = end
  }
  return previousEnd >= 59900 && previousEnd <= 60100
}

function keyId(value: string) { return ['Space', ' ', 'Spacebar'].includes(value) ? 'Space' : value }

/** Sequencia inteira ancorada a uma origem monotona, sem somar atrasos por fase. */
export function createMainRuntime(container: HTMLElement, options: MainOptions,
  clock: MainClock = defaultClock): () => void {
  const order = options.order.map(row => ({ ...row }))
  let active = true
  let handle: number | undefined
  let phase: Phase = 'countdown'
  const countdownStart = clock.now()
  let countdownDeadline = countdownStart + PROTOCOL.countdown_segment_ms
  let lastNow = countdownStart
  let countdownIndex = 0
  let origin: number | undefined
  let index = 0
  let current: MainTrial | undefined
  let completed = 0
  let framePeriod: number | undefined
  let lastFrameStamp: number | undefined
  const frameIntervals: number[] = []
  const trials: MainTrial[] = []
  const timingTransitions = options.onTimingTrace ? [] as MainTimingTransition[] : undefined
  const timingKeys = options.onTimingTrace ? [] as MainTimingKeyEvent[] : undefined
  const held = new Set(options.initiallyHeldKeys?.map(keyId))
  const previousCursor = container.style.cursor
  const surface = document.createElement('section')
  surface.className = 'main-runtime'
  surface.dataset.visualVariant = PROTOCOL.visual.id
  surface.dataset.visualVersion = PROTOCOL.visual.version
  surface.setAttribute('aria-label', 'Bloco principal')
  Object.assign(surface.style, { background: '#0B1020', color: '#F8FAFC',
    minHeight: '100dvh', height: '100dvh', width: '100%', position: 'relative',
    display: 'grid', placeItems: 'center', fontFamily: 'system-ui, sans-serif' })
  const presentation = createExperimentHud('main', order.length)
  const hud = presentation.element
  const card = document.createElement('div')
  card.className = 'main-stimulus-card experiment-word'
  Object.assign(card.style, { display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontWeight: '700', textAlign: 'center', lineHeight: '1.2', boxSizing: 'border-box' })
  surface.append(hud, card)
  container.replaceChildren(surface)
  container.style.cursor = 'none'

  function render(elapsed: number) {
    container.dataset.phase = phase
    delete container.dataset.conditionId
    delete container.dataset.condition
    delete container.dataset.trialNumber
    hud.hidden = phase === 'countdown'
    hud.style.display = phase === 'countdown' ? 'none' : 'flex'
    card.style.background = 'transparent'
    card.dataset.stimulus = String(phase === 'stimulus')
    card.style.color = '#F8FAFC'
    card.style.width = phase === 'stimulus' ? 'min(82vh, calc(100vw - 48px))' : 'min(90vw, 1100px)'
    card.style.height = phase === 'stimulus' ? '24vh' : 'auto'
    card.style.fontSize = phase === 'stimulus' ? 'min(9vh, 9vw)' : phase === 'fixation' ? '6vh' : '8vh'
    if (phase === 'countdown') card.textContent = countdown[countdownIndex] ?? ''
    else if (phase === 'fixation') card.textContent = '+'
    else if (phase === 'blank') card.textContent = ''
    else {
      const condition = order[index]!
      card.textContent = condition.word
      card.style.color = PROTOCOL.colors[condition.ink_color]
      container.dataset.conditionId = String(condition.condition_id)
      container.dataset.condition = condition.condition
      container.dataset.trialNumber = String(index + 1)
    }
    presentation.update(completed, elapsed)
  }

  function cleanup() {
    if (!active) return
    active = false
    if (handle !== undefined) clock.cancelFrame(handle)
    window.removeEventListener('keydown', keydown, true)
    window.removeEventListener('keyup', keyup, true)
    window.removeEventListener('blur', blur)
    window.removeEventListener('pagehide', pagehide)
    document.removeEventListener('visibilitychange', visibility)
    held.clear()
    trials.length = 0
    current = undefined
    container.style.cursor = previousCursor
    delete container.dataset.phase
    delete container.dataset.conditionId
    delete container.dataset.condition
    delete container.dataset.trialNumber
    surface.remove()
  }
  function emitTimingTrace(outcome: MainTimingTrace['outcome'], reason: InterruptionReason | null) {
    if (!options.onTimingTrace || !timingTransitions || !timingKeys) return
    options.onTimingTrace({
      schema: 'stroop-w16-timing-trace-v1', outcome, interruption_reason: reason,
      countdown_frame_intervals_ms: [...frameIntervals],
      frame_period_ms: Number.isFinite(framePeriod) ? framePeriod! : null,
      main_origin_since_runtime_start_ms: origin === undefined ? null : origin - countdownStart,
      transitions: [...timingTransitions], keyboard_events: [...timingKeys],
    })
  }
  function recordTransition(type: MainTimingTransition['type'], planned: number,
    observed: number, stamp?: number) {
    if (!timingTransitions || origin === undefined || !current) return
    const rafElapsed = stamp === undefined ? null : stamp - origin
    timingTransitions.push({ type, trial_number: current.trial_number,
      condition_id: current.condition_id, planned_elapsed_ms: planned,
      observed_elapsed_ms: observed,
      raf_elapsed_ms: rafElapsed !== null && Number.isFinite(rafElapsed) ? rafElapsed : null })
  }
  function recordKey(event: KeyboardEvent, type: MainTimingKeyEvent['type'],
    key: MainTimingKeyEvent['key'], heldBefore: boolean) {
    if (!timingKeys) return
    const runtimeElapsed = event.timeStamp - countdownStart
    const mainElapsed = origin === undefined ? null : event.timeStamp - origin
    timingKeys.push({ type, key, phase,
      elapsed_since_runtime_start_ms: Number.isFinite(runtimeElapsed) ? runtimeElapsed : null,
      elapsed_since_main_origin_ms: mainElapsed !== null && Number.isFinite(mainElapsed) ? mainElapsed : null,
      repeat: event.repeat, held_before_event: heldBefore })
  }
  function interrupt(reason: InterruptionReason) {
    if (!active) return
    emitTimingTrace('interrupted', reason)
    cleanup()
    options.onInterrupted(reason)
  }
  function now(): number | undefined {
    const value = clock.now()
    if (!Number.isFinite(value) || value < lastNow) { interrupt('timing_invalid'); return }
    lastNow = value
    return value
  }
  function keydown(event: KeyboardEvent) {
    if (!active) return
    if (event.key === 'Escape') {
      recordKey(event, 'keydown', 'Escape', held.has('Escape'))
      event.preventDefault(); interrupt('escape'); return
    }
    const key = keyId(event.code || event.key)
    const alreadyHeld = held.has(key)
    held.add(key)
    if (key !== 'Space') return
    recordKey(event, 'keydown', 'Space', alreadyHeld)
    event.preventDefault()
    const delivered = now()
    if (delivered === undefined || origin === undefined || !current || phase !== 'stimulus'
      || alreadyHeld || event.repeat || current.key_pressed !== null) return
    const keyAt = event.timeStamp - origin
    const deliveredAt = delivered - origin
    const rt = keyAt - current.stimulus_onset_ms
    const responseDeadline = Math.min(index * 3750 + 2800, current.stimulus_onset_ms + 2500)
    if (Number.isFinite(keyAt) && current.stimulus_onset_ms < keyAt && rt > 0 && rt < 2500
      && keyAt < responseDeadline && keyAt <= deliveredAt && deliveredAt < responseDeadline) {
      current.key_pressed = 'space'
      current.key_at_ms = keyAt
      current.reaction_time_ms = rt
    }
  }
  function keyup(event: KeyboardEvent) {
    const key = keyId(event.code || event.key)
    const heldBefore = held.has(key)
    held.delete(key)
    if (key === 'Space' || key === 'Escape') recordKey(event, 'keyup', key, heldBefore)
  }
  function blur() { interrupt('focus_lost') }
  function pagehide() { interrupt('page_closed') }
  function visibility() { if (document.visibilityState !== 'visible') interrupt('visibility_hidden') }
  function startTrial(start: number, stamp?: number) {
    current = { trial_number: index + 1, condition_id: order[index]!.condition_id,
      key_pressed: null, reaction_time_ms: null, key_at_ms: null,
      trial_start_ms: start, stimulus_onset_ms: NaN, stimulus_offset_ms: NaN, trial_end_ms: NaN }
    recordTransition('trial_start', index * 3750, start, stamp)
    phase = 'fixation'
    render(start)
  }
  function tick(stamp: number) {
    if (!active) return
    const observed = now()
    if (observed === undefined) return
    if (!Number.isFinite(stamp) || (lastFrameStamp !== undefined && stamp <= lastFrameStamp)) {
      interrupt('timing_invalid'); return
    }
    if (phase === 'countdown') {
      if (lastFrameStamp !== undefined && frameIntervals.length < 30) frameIntervals.push(stamp - lastFrameStamp)
      lastFrameStamp = stamp
      if (observed >= countdownDeadline) {
        countdownIndex += 1
        if (countdownIndex < countdown.length) {
          countdownDeadline = observed + PROTOCOL.countdown_segment_ms
          render(0)
        }
        else {
          const samples = [...frameIntervals].sort((a, b) => a - b)
          framePeriod = samples.length === 30 ? (samples[14]! + samples[15]!) / 2 : NaN
          if (!Number.isFinite(framePeriod) || framePeriod < 4 || framePeriod > 50) {
            interrupt('timing_invalid'); return
          }
          origin = observed
          startTrial(0, stamp)
        }
      }
    } else {
      lastFrameStamp = stamp
      const elapsed = observed - origin!
      const nominal = index * 3750
      // Escolher o quadro mais proximo do alvo nominal usa a tolerancia
      // simetrica aprovada; instantes continuam observados e gates inalterados.
      const due = (target: number) => elapsed >= target - framePeriod! / 2
      const trial = current!
      if (phase === 'fixation' && due(nominal + 300)) {
        trial.stimulus_onset_ms = elapsed
        recordTransition('stimulus_onset', nominal + 300, elapsed, stamp)
        if (!(trial.trial_start_ms < elapsed) || !within([elapsed, -trial.trial_start_ms, -300], framePeriod!)) {
          interrupt('timing_invalid'); return
        }
        phase = 'stimulus'
        render(elapsed)
      } else if (phase === 'stimulus' && due(nominal + 2800)) {
        trial.stimulus_offset_ms = elapsed
        recordTransition('stimulus_offset', nominal + 2800, elapsed, stamp)
        if (!(trial.stimulus_onset_ms < elapsed)
          || !within([elapsed, -trial.trial_start_ms, -2800], framePeriod!)
          || !within([elapsed, -trial.stimulus_onset_ms, -2500], framePeriod!)) {
          interrupt('timing_invalid'); return
        }
        phase = 'blank'
        render(elapsed)
      } else if (phase === 'blank' && due(nominal + 3750)) {
        trial.trial_end_ms = elapsed
        recordTransition('trial_end', nominal + 3750, elapsed, stamp)
        if (!(trial.stimulus_offset_ms < elapsed) || elapsed > 60100
          || !within([elapsed, -trial.trial_start_ms, -3750], framePeriod!)) {
          interrupt('timing_invalid'); return
        }
        trials.push(trial)
        completed += 1
        if (completed === 16) {
          const result: MainResult = { frame_period_ms: framePeriod!, trials: trials.map(row => ({ ...row })), order }
          if (!validMainResult(result)) { interrupt('timing_invalid'); return }
          emitTimingTrace('completed', null)
          cleanup()
          options.onComplete(result)
          return
        }
        index += 1
        if (!within([elapsed, -index * 3750], framePeriod!)) { interrupt('timing_invalid'); return }
        startTrial(elapsed, stamp)
      } else presentation.update(completed, elapsed)
    }
    if (active) handle = clock.requestFrame(tick)
  }

  window.addEventListener('keydown', keydown, true)
  window.addEventListener('keyup', keyup, true)
  window.addEventListener('blur', blur)
  window.addEventListener('pagehide', pagehide)
  document.addEventListener('visibilitychange', visibility)
  if (!validOrder(order) || !Number.isFinite(countdownStart) || countdownStart < 0) interrupt('timing_invalid')
  else if (document.visibilityState !== 'visible') interrupt('visibility_hidden')
  else if (!document.hasFocus()) interrupt('focus_lost')
  else { render(0); handle = clock.requestFrame(tick) }
  return cleanup
}
