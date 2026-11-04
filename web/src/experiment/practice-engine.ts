import { PROTOCOL } from './protocol'
import type { Condition, InterruptionReason, PracticeSummary } from './protocol'

export type PracticeOptions = {
  onComplete(summary: PracticeSummary): void
  onInterrupted(reason: InterruptionReason): void
  initiallyHeldKeys?: readonly string[]
}
export type PracticeClock = {
  now(): number
  requestFrame(callback: FrameRequestCallback): number
  cancelFrame(handle: number): void
}
type Phase = 'reminder' | 'countdown' | 'fixation' | 'stimulus' | 'blank' | 'feedback'
type Outcome = 'hit' | 'omission' | 'commission' | 'correct_rejection'

const countdown = ['Prepare-se', '3', '2', '1', 'Começar'] as const
const feedback: Readonly<Record<Outcome, string>> = {
  hit: '✓ Correto', correct_rejection: '✓ Correto',
  omission: 'Pressione ESPAÇO quando a cor combina',
  commission: 'Não responda quando a cor não combina',
}
const defaultClock: PracticeClock = {
  now: () => performance.now(),
  requestFrame: callback => requestAnimationFrame(callback),
  cancelFrame: handle => cancelAnimationFrame(handle),
}

function keyId(key: string): string {
  return key === ' ' || key === 'Spacebar' || key === 'Space' ? 'Space' : key
}

/** Python round usado pela barra original: empates exatos arredondam para par. */
function barCount(value: number): number {
  const floor = Math.floor(value)
  return value - floor === 0.5 ? floor + floor % 2 : Math.round(value)
}

/** Rodada imperativa: React e rede nunca participam da temporizacao. */
export function createPracticeRuntime(container: HTMLElement, order: readonly Condition[],
  options: PracticeOptions, clock: PracticeClock = defaultClock): () => void {
  let active = true
  let frame: number | undefined
  let phase: Phase = 'reminder'
  let phaseStart = clock.now()
  let lastNow = phaseStart
  let deadline = phaseStart + PROTOCOL.practice.reminder_ms
  let countdownIndex = 0
  let index = 0
  let response = false
  let completed = 0
  let correct = 0
  const held = new Set(options.initiallyHeldKeys?.map(keyId))
  const previousCursor = container.style.cursor
  const surface = document.createElement('section')
  surface.className = 'practice-runtime'
  surface.setAttribute('aria-label', 'Prática')
  Object.assign(surface.style, { background: '#0B1020', color: '#F8FAFC',
    minHeight: '100dvh', height: '100dvh', width: '100%', position: 'relative',
    display: 'grid', placeItems: 'center', fontFamily: 'system-ui, sans-serif' })
  const hud = document.createElement('div')
  hud.className = 'practice-hud'
  Object.assign(hud.style, { display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: '16px',
    position: 'absolute', top: '24px', left: '24px', right: '24px', fontSize: 'min(2.8vh, 20px)' })
  const accuracy = document.createElement('span')
  accuracy.dataset.hud = 'accuracy'
  const accuracyBar = document.createElement('span')
  accuracyBar.dataset.hud = 'accuracy-bar'
  accuracyBar.setAttribute('aria-hidden', 'true')
  const progress = document.createElement('span')
  progress.dataset.hud = 'progress'
  const time = document.createElement('span')
  time.textContent = 'Tempo: --:--'
  hud.append(accuracy, accuracyBar, progress, time)
  const reminder = document.createElement('p')
  reminder.textContent = 'ESPAÇO apenas quando combinar'
  Object.assign(reminder.style, { position: 'absolute', top: '70%', left: '12px', right: '12px',
    margin: '0', textAlign: 'center', fontSize: 'min(3vh, 22px)' })
  const card = document.createElement('div')
  card.className = 'practice-stimulus-card'
  Object.assign(card.style, { display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontWeight: '700', textAlign: 'center', lineHeight: '1.2', boxSizing: 'border-box' })
  surface.append(hud, reminder, card)
  container.replaceChildren(surface)
  container.style.cursor = 'none'

  function updateHud() {
    accuracy.textContent = completed === 0 ? 'Precisão: —' : `Precisão: ${Math.round(correct / completed * 100).toString().padStart(2, '0')}%`
    const filled = completed === 0 ? 0 : barCount(correct / completed * 10)
    accuracyBar.textContent = `[${'#'.repeat(filled)}${'-'.repeat(10 - filled)}]`
    progress.textContent = `Prática — tentativa ${Math.min(index + 1, order.length)} de ${order.length}`
  }

  function render() {
    container.dataset.phase = phase
    delete container.dataset.conditionId
    delete container.dataset.condition
    delete container.dataset.trialNumber
    delete container.dataset.outcome
    const showHud = phase === 'fixation' || phase === 'stimulus' || phase === 'blank'
    hud.hidden = !showHud
    hud.style.display = showHud ? 'flex' : 'none'
    reminder.hidden = phase !== 'stimulus'
    reminder.style.display = phase === 'stimulus' ? 'block' : 'none'
    card.style.background = phase === 'stimulus' ? '#F8FAFC' : 'transparent'
    card.style.color = '#F8FAFC'
    card.style.width = phase === 'stimulus' ? 'min(82vh, calc(100vw - 48px))' : 'min(90vw, 1100px)'
    card.style.height = phase === 'stimulus' ? '24vh' : 'auto'
    card.style.fontSize = phase === 'stimulus' ? 'min(9vh, 9vw)'
      : phase === 'fixation' ? '6vh'
      : phase === 'feedback' ? 'min(5.2vh, 5.2vw)'
      : phase === 'countdown' ? '8vh' : 'min(4vh, 4vw)'
    if (phase === 'reminder') card.textContent = 'PRESSIONE ESPAÇO APENAS QUANDO A PALAVRA E A COR COMBINAREM.'
    else if (phase === 'countdown') card.textContent = countdown[countdownIndex] ?? ''
    else if (phase === 'fixation') card.textContent = '+'
    else if (phase === 'blank') card.textContent = ''
    else if (phase === 'stimulus') {
      const condition = order[index]!
      card.textContent = condition.word
      card.style.color = PROTOCOL.colors[condition.ink_color]
      container.dataset.conditionId = String(condition.condition_id)
      container.dataset.condition = condition.condition
      container.dataset.trialNumber = String(index + 1)
    } else {
      const condition = order[index]!
      const outcome: Outcome = condition.condition === 'congruent'
        ? response ? 'hit' : 'omission'
        : response ? 'commission' : 'correct_rejection'
      card.textContent = feedback[outcome]
      container.dataset.outcome = outcome
    }
    updateHud()
  }

  function cleanup() {
    if (!active) return
    active = false
    if (frame !== undefined) clock.cancelFrame(frame)
    window.removeEventListener('keydown', keydown, true)
    window.removeEventListener('keyup', keyup, true)
    window.removeEventListener('blur', blur)
    window.removeEventListener('pagehide', pagehide)
    document.removeEventListener('visibilitychange', visibility)
    held.clear()
    container.style.cursor = previousCursor
    delete container.dataset.phase
    delete container.dataset.conditionId
    delete container.dataset.condition
    delete container.dataset.trialNumber
    delete container.dataset.outcome
    surface.remove()
  }

  function interrupt(reason: InterruptionReason) {
    if (!active) return
    cleanup()
    options.onInterrupted(reason)
  }

  function readNow(): number | undefined {
    const now = clock.now()
    if (!Number.isFinite(now) || now < lastNow) {
      interrupt('timing_invalid')
      return undefined
    }
    lastNow = now
    return now
  }

  function keydown(event: KeyboardEvent) {
    if (!active) return
    if (event.key === 'Escape') {
      event.preventDefault()
      interrupt('escape')
      return
    }
    const key = keyId(event.code || event.key)
    const previouslyHeld = held.has(key)
    held.add(key)
    if (key !== 'Space') return
    event.preventDefault()
    const now = readNow()
    if (now === undefined || phase !== 'stimulus' || previouslyHeld || event.repeat || response) return
    const timestamp = event.timeStamp
    // Mesmo evento originado na janela e recusado se sua entrega ultrapassou
    // o deadline. Eventos futuros, antigos e fim exato nunca geram resposta.
    if (Number.isFinite(timestamp) && phaseStart < timestamp && timestamp < deadline
      && timestamp <= now && now < deadline) response = true
  }

  function keyup(event: KeyboardEvent) { held.delete(keyId(event.code || event.key)) }
  function blur() { interrupt('focus_lost') }
  function pagehide() { interrupt('page_closed') }
  function visibility() {
    if (document.visibilityState !== 'visible') interrupt('visibility_hidden')
  }

  function enter(next: Phase, now: number, duration: number) {
    phase = next
    phaseStart = now
    deadline = now + duration
    render()
  }

  function tick() {
    if (!active) return
    const now = readNow()
    if (now === undefined) return
    if (now >= deadline) {
      if (phase === 'reminder') enter('countdown', now, PROTOCOL.countdown_segment_ms)
      else if (phase === 'countdown') {
        countdownIndex += 1
        if (countdownIndex < countdown.length) enter('countdown', now, PROTOCOL.countdown_segment_ms)
        else enter('fixation', now, PROTOCOL.practice.fixation_ms)
      } else if (phase === 'fixation') enter('stimulus', now, PROTOCOL.practice.stimulus_window_ms)
      else if (phase === 'stimulus') enter('blank', now, PROTOCOL.practice.blank_interval_ms)
      else if (phase === 'blank') {
        completed += 1
        if ((order[index]!.condition === 'congruent') === response) correct += 1
        enter('feedback', now, PROTOCOL.practice.feedback_ms)
      } else {
        index += 1
        response = false
        if (index === order.length) {
          const summary = { correct, total: completed }
          cleanup()
          options.onComplete(summary)
          return
        }
        enter('fixation', now, PROTOCOL.practice.fixation_ms)
      }
    }
    if (active) frame = clock.requestFrame(tick)
  }

  window.addEventListener('keydown', keydown, true)
  window.addEventListener('keyup', keyup, true)
  window.addEventListener('blur', blur)
  window.addEventListener('pagehide', pagehide)
  document.addEventListener('visibilitychange', visibility)
  if (order.length !== PROTOCOL.practice.trials || new Set(order.map(row => row.condition_id)).size !== 4
    || order.filter(row => row.condition === 'congruent').length !== 2
    || !Number.isFinite(phaseStart)) interrupt('timing_invalid')
  else if (document.visibilityState !== 'visible') interrupt('visibility_hidden')
  else if (!document.hasFocus()) interrupt('focus_lost')
  else {
    render()
    frame = clock.requestFrame(tick)
  }
  return cleanup
}
