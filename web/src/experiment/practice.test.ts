// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPracticeRuntime } from './practice-engine'
import type { PracticeClock, PracticeOptions } from './practice-engine'
import { PRACTICE_CONDITIONS, PROTOCOL } from './protocol'
import { mountPractice } from './practice'

class ControlledClock implements PracticeClock {
  time = 100
  nextId = 0
  frames = new Map<number, FrameRequestCallback>()
  now = () => this.time
  requestFrame = (callback: FrameRequestCallback) => {
    const id = ++this.nextId
    this.frames.set(id, callback)
    return id
  }
  cancelFrame = (id: number) => { this.frames.delete(id) }
  step(ms: number) {
    this.time += ms
    const pending = [...this.frames.values()]
    this.frames.clear()
    pending.forEach(callback => callback(this.time))
  }
}

let clock: ControlledClock
let container: HTMLDivElement
let onComplete: ReturnType<typeof vi.fn<PracticeOptions['onComplete']>>
let onInterrupted: ReturnType<typeof vi.fn<PracticeOptions['onInterrupted']>>
const cleanups: (() => void)[] = []

beforeEach(() => {
  vi.spyOn(document, 'hasFocus').mockReturnValue(true)
  vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('visible')
  clock = new ControlledClock()
  container = document.createElement('div')
  document.body.append(container)
  onComplete = vi.fn<PracticeOptions['onComplete']>()
  onInterrupted = vi.fn<PracticeOptions['onInterrupted']>()
})

afterEach(async () => {
  cleanups.splice(0).forEach(cleanup => cleanup())
  await Promise.resolve()
  vi.useRealTimers()
  vi.restoreAllMocks()
  document.body.replaceChildren()
})

function start(extra: Partial<PracticeOptions> = {}) {
  const cleanup = createPracticeRuntime(container, PRACTICE_CONDITIONS,
    { onComplete, onInterrupted, ...extra }, clock)
  cleanups.push(cleanup)
  return cleanup
}

function stimulus() {
  clock.step(PROTOCOL.practice.reminder_ms)
  for (let i = 0; i < 5; i++) clock.step(PROTOCOL.countdown_segment_ms)
  expect(container.dataset.phase).toBe('fixation')
  clock.step(PROTOCOL.practice.fixation_ms)
  expect(container.dataset.phase).toBe('stimulus')
}

function keyboard(type: 'keydown' | 'keyup', timestamp = clock.time,
  options: KeyboardEventInit = {}) {
  const event = new KeyboardEvent(type, { key: ' ', code: 'Space', cancelable: true, ...options })
  Object.defineProperty(event, 'timeStamp', { value: timestamp })
  window.dispatchEvent(event)
  return event
}

function finishTrial() {
  clock.step(PROTOCOL.practice.stimulus_window_ms)
  expect(container.dataset.phase).toBe('blank')
  clock.step(PROTOCOL.practice.blank_interval_ms)
  expect(container.dataset.phase).toBe('feedback')
}

describe('motor imperativo da pratica', () => {
  it('preserva lembrete, cinco segmentos de contagem e fixacao antes da resposta', () => {
    start()
    expect(container.dataset.phase).toBe('reminder')
    expect(container.querySelector<HTMLElement>('.practice-hud')!.hidden).toBe(true)
    expect(container.querySelector<HTMLElement>('.practice-stimulus-card')!.style.background).toBe('transparent')
    expect(container.textContent).toContain('Precisão: —')
    expect(container.textContent).toContain('Tempo: --:--')
    expect(container.style.cursor).toBe('none')
    clock.step(1499)
    expect(container.dataset.phase).toBe('reminder')
    clock.step(1)
    for (const message of ['Prepare-se', '3', '2', '1', 'Começar']) {
      expect(container.dataset.phase).toBe('countdown')
      expect(container.querySelector('.practice-stimulus-card')?.textContent).toBe(message)
      clock.step(549)
      expect(container.querySelector('.practice-stimulus-card')?.textContent).toBe(message)
      clock.step(1)
    }
    expect(container.dataset.phase).toBe('fixation')
    expect(container.querySelector<HTMLElement>('.practice-hud')!.hidden).toBe(false)
    expect(container.querySelector('.practice-stimulus-card')?.textContent).toBe('+')
    clock.step(299)
    expect(container.dataset.phase).toBe('fixation')
    clock.step(1)
    expect(container.dataset.phase).toBe('stimulus')
  })

  it('usa palavra por textContent e paleta efetiva do protocolo no cartao claro', () => {
    start()
    stimulus()
    const card = container.querySelector<HTMLElement>('.practice-stimulus-card')!
    expect(card.textContent).toBe('VERDE')
    expect(card.style.color).toBe('rgb(64, 255, 0)')
    expect(card.style.background).toBe('rgb(248, 250, 252)')
    expect(container.dataset.conditionId).toBe('1')
    expect(container.dataset.condition).toBe('congruent')
    expect(container.dataset.trialNumber).toBe('1')
    expect(container.querySelector<HTMLElement>('section > p')!.hidden).toBe(false)
  })

  it('aceita primeira nova Space sem abreviar estimulo, blank ou feedback e atualiza HUD ao fim', () => {
    start()
    stimulus()
    clock.time += 20
    expect(keyboard('keydown').defaultPrevented).toBe(true)
    expect(container.textContent).toContain('Precisão: —')
    expect(container.dataset.phase).toBe('stimulus')
    clock.step(1979)
    expect(container.dataset.phase).toBe('stimulus')
    clock.step(1)
    expect(container.dataset.phase).toBe('blank')
    expect(container.querySelector<HTMLElement>('.practice-stimulus-card')!.style.background).toBe('transparent')
    expect(container.querySelector<HTMLElement>('section > p')!.hidden).toBe(true)
    expect(container.textContent).toContain('Precisão: —')
    clock.step(499)
    expect(container.dataset.phase).toBe('blank')
    clock.step(1)
    expect(container.dataset.outcome).toBe('hit')
    expect(container.querySelector<HTMLElement>('.practice-hud')!.hidden).toBe(true)
    expect(container.querySelector<HTMLElement>('.practice-stimulus-card')!.style.background).toBe('transparent')
    expect(container.textContent).toContain('Precisão: 100%')
    expect(container.textContent).toContain('[##########]')
    clock.step(499)
    expect(container.dataset.phase).toBe('feedback')
    clock.step(1)
    expect(container.dataset.phase).toBe('fixation')
  })

  it('executa quatro condicoes uma vez e produz as quatro classificacoes sem persistencia', () => {
    start()
    stimulus()
    const ids: string[] = []
    const outcomes: string[] = []
    for (let index = 0; index < 4; index++) {
      ids.push(container.dataset.conditionId!)
      if (index < 2) {
        clock.time += 10
        keyboard('keyup')
        keyboard('keydown')
        clock.step(1990)
      } else clock.step(2000)
      clock.step(500)
      outcomes.push(container.dataset.outcome!)
      expect(onComplete).not.toHaveBeenCalled()
      clock.step(500)
      if (index !== 3) clock.step(300)
    }
    expect(ids).toEqual(['1', '2', '3', '4'])
    expect(outcomes).toEqual(['hit', 'commission', 'omission', 'correct_rejection'])
    expect(onComplete).toHaveBeenCalledExactlyOnceWith({ correct: 2, total: 4 })
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(clock.frames.size).toBe(0)
    expect(container.textContent).toBe('')
  })

  it.each(['Space', ' '])('nao herda a tecla %s mantida na navegacao e exige soltar', key => {
    start({ initiallyHeldKeys: [key] })
    stimulus()
    clock.time += 10
    keyboard('keydown')
    keyboard('keydown', clock.time, { repeat: true })
    finishTrial()
    expect(container.dataset.outcome).toBe('omission')
  })

  it('permite nova pressao apos keyup de tecla herdada', () => {
    start({ initiallyHeldKeys: ['Space', 'Enter'] })
    stimulus()
    clock.time += 10
    keyboard('keyup')
    keyboard('keydown')
    finishTrial()
    expect(container.dataset.outcome).toBe('hit')
  })

  it('rastreia tecla mantida desde countdown/fixacao e ignora repeticao', () => {
    start()
    keyboard('keydown')
    stimulus()
    clock.time += 10
    keyboard('keydown', clock.time, { repeat: true })
    finishTrial()
    expect(container.dataset.outcome).toBe('omission')
  })

  it('descarta navegacao anterior solta e aceita primeira nova pressao experimental', () => {
    start()
    keyboard('keydown')
    keyboard('keyup')
    stimulus()
    clock.time += 10
    keyboard('keydown')
    keyboard('keyup')
    keyboard('keydown')
    finishTrial()
    expect(container.dataset.outcome).toBe('hit')
  })

  it('ignora Space mantida de feedback para proximo estimulo', () => {
    start()
    stimulus()
    finishTrial()
    keyboard('keydown')
    clock.step(500)
    clock.step(300)
    clock.time += 10
    keyboard('keydown', clock.time, { repeat: true })
    finishTrial()
    expect(container.dataset.outcome).toBe('correct_rejection')
  })

  it.each([
    ['inicio exato', 0, 100], ['anterior ao onset', -1, 100],
    ['fim exato', 2000, 2000], ['apos fim', 2001, 2001],
    ['evento futuro', 101, 100], ['evento enfileirado', 100, 2001],
    ['entrega no deadline', 100, 2000], ['timestamp nao finito', NaN, 100],
  ])('rejeita %s sem tolerar a fronteira aberta', (_name, timestampDelta, callbackDelta) => {
    start()
    stimulus()
    const onset = clock.time
    clock.time += Number(callbackDelta)
    keyboard('keydown', onset + Number(timestampDelta))
    clock.step(Math.max(0, onset + 2000 - clock.time))
    clock.step(500)
    expect(container.dataset.outcome).toBe('omission')
  })

  it('aceita RT positivo sem quantizacao e evento anterior ao fim exclusivo', () => {
    start()
    stimulus()
    clock.time += 1999.999
    keyboard('keydown')
    clock.step(0.0011)
    clock.step(500)
    expect(container.dataset.outcome).toBe('hit')
  })

  it('Enter/clique e repeticao sem keyup nunca sao respostas experimentais', () => {
    start()
    stimulus()
    clock.time += 100
    keyboard('keydown', clock.time, { key: 'Enter', code: 'Enter' })
    container.click()
    keyboard('keydown', clock.time, { repeat: true })
    clock.step(1900)
    clock.step(500)
    expect(container.dataset.outcome).toBe('omission')
  })

  it.each(['focus_lost', 'visibility_hidden', 'page_closed', 'escape'] as const)(
    'interrompe por %s, descarta rodada e limpa callbacks/listeners/frames', reason => {
      start()
      stimulus()
      if (reason === 'focus_lost') window.dispatchEvent(new Event('blur'))
      if (reason === 'visibility_hidden') {
        vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('hidden')
        document.dispatchEvent(new Event('visibilitychange'))
      }
      if (reason === 'page_closed') window.dispatchEvent(new Event('pagehide'))
      if (reason === 'escape') keyboard('keydown', clock.time, { key: 'Escape', code: 'Escape' })
      expect(onInterrupted).toHaveBeenCalledExactlyOnceWith(reason)
      expect(onComplete).not.toHaveBeenCalled()
      expect(container.textContent).toBe('')
      expect(container.style.cursor).toBe('')
      expect(clock.frames.size).toBe(0)
      window.dispatchEvent(new Event('blur'))
      keyboard('keydown', clock.time, { key: 'Escape' })
      clock.step(100_000)
      expect(onInterrupted).toHaveBeenCalledTimes(1)
    },
  )

  it('revalida visibilidade e foco antes de iniciar', () => {
    vi.spyOn(document, 'hasFocus').mockReturnValue(false)
    start()
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('focus_lost')
    expect(clock.frames.size).toBe(0)
    onInterrupted.mockClear()
    vi.spyOn(document, 'hasFocus').mockReturnValue(true)
    vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('hidden')
    start()
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('visibility_hidden')
  })

  it('recusa relogio invalido e ordem incompleta', () => {
    start()
    clock.step(-1)
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    onInterrupted.mockClear()
    cleanups.push(createPracticeRuntime(container, PRACTICE_CONDITIONS.slice(0, 3),
      { onComplete, onInterrupted }, clock))
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
  })

  it('cleanup e idempotente e nao notifica interrupcao ao desmontar', () => {
    container.style.cursor = 'crosshair'
    const cleanup = start()
    stimulus()
    cleanup()
    cleanup()
    expect(clock.frames.size).toBe(0)
    expect(container.style.cursor).toBe('crosshair')
    expect(container.dataset.phase).toBeUndefined()
    keyboard('keydown', clock.time, { key: 'Escape' })
    window.dispatchEvent(new Event('blur'))
    clock.step(100_000)
    expect(onComplete).not.toHaveBeenCalled()
    expect(onInterrupted).not.toHaveBeenCalled()
  })
})

describe('plugin real jsPsych', () => {
  it('executa rodada completa sem rede nem armazenamento e conclui uma unica vez', async () => {
    vi.useFakeTimers({ toFake: ['performance', 'requestAnimationFrame', 'cancelAnimationFrame'] })
    const fetch = vi.spyOn(globalThis, 'fetch')
    cleanups.push(mountPractice(container, { onComplete, onInterrupted }))
    await vi.advanceTimersByTimeAsync(18_000)
    expect(onComplete).toHaveBeenCalledExactlyOnceWith({ correct: 2, total: 4 })
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(fetch).not.toHaveBeenCalled()
    expect(localStorage.length).toBe(0)
    expect(sessionStorage.length).toBe(0)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('desmontagem imediata nao inicia plugin atrasado nem emite callbacks', async () => {
    vi.useFakeTimers({ toFake: ['performance', 'requestAnimationFrame', 'cancelAnimationFrame'] })
    const cleanup = mountPractice(container, { onComplete, onInterrupted })
    cleanups.push(cleanup)
    cleanup()
    await vi.advanceTimersByTimeAsync(20_000)
    expect(onComplete).not.toHaveBeenCalled()
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(container.textContent).toBe('')
    expect(vi.getTimerCount()).toBe(0)
  })

  it('remove a espera de load quando desmonta antes de o documento estar pronto', async () => {
    vi.spyOn(document, 'readyState', 'get').mockReturnValue('loading')
    const remove = vi.spyOn(window, 'removeEventListener')
    const cleanup = mountPractice(container, { onComplete, onInterrupted })
    cleanups.push(cleanup)
    cleanup()
    window.dispatchEvent(new Event('load'))
    await Promise.resolve()
    expect(remove).toHaveBeenCalledWith('load', expect.any(Function))
    expect(container.textContent).toBe('')
    expect(onComplete).not.toHaveBeenCalled()
    expect(onInterrupted).not.toHaveBeenCalled()
  })
})
