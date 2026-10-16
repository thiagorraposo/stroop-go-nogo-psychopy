// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMainRuntime, validMainResult } from './main-engine'
import type { MainClock, MainOptions, MainResult } from './main-engine'
import { mountMain } from './main'
import { MAIN_CONDITIONS } from './protocol'
import type { Condition } from './protocol'

class ControlledClock implements MainClock {
  time = 100
  nextId = 0
  frames = new Map<number, FrameRequestCallback>()
  now = () => this.time
  requestFrame = (callback: FrameRequestCallback) => {
    const id = ++this.nextId
    this.frames.set(id, callback)
    return id
  }
  cancelFrame = (handle: number) => { this.frames.delete(handle) }
  tickAt(time: number, stamp = time) {
    this.time = time
    const pending = [...this.frames.values()]
    this.frames.clear()
    pending.forEach(callback => callback(stamp))
  }
  advance(ms: number, period = 10) {
    const target = this.time + ms
    while (this.time < target && this.frames.size) this.tickAt(Math.min(this.time + period, target))
  }
}

let clock: ControlledClock
let container: HTMLDivElement
let onComplete: ReturnType<typeof vi.fn<MainOptions['onComplete']>>
let onInterrupted: ReturnType<typeof vi.fn<MainOptions['onInterrupted']>>
const cleanups: (() => void)[] = []

beforeEach(() => {
  vi.spyOn(document, 'hasFocus').mockReturnValue(true)
  vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('visible')
  clock = new ControlledClock()
  container = document.createElement('div')
  document.body.append(container)
  onComplete = vi.fn<MainOptions['onComplete']>()
  onInterrupted = vi.fn<MainOptions['onInterrupted']>()
})

afterEach(async () => {
  cleanups.splice(0).forEach(cleanup => cleanup())
  await Promise.resolve()
  vi.useRealTimers()
  vi.restoreAllMocks()
  document.body.replaceChildren()
})

function start(extra: Partial<MainOptions> = {}) {
  const cleanup = createMainRuntime(container, {
    order: MAIN_CONDITIONS, onComplete, onInterrupted, ...extra,
  }, clock)
  cleanups.push(cleanup)
  return cleanup
}

function mainStart() {
  clock.advance(2750)
  expect(container.dataset.phase).toBe('fixation')
  return clock.time
}

function firstStimulus() {
  const origin = mainStart()
  clock.advance(300)
  expect(container.dataset.phase).toBe('stimulus')
  return origin
}

function keyboard(type: 'keydown' | 'keyup', timestamp = clock.time, options: KeyboardEventInit = {}) {
  const event = new KeyboardEvent(type, { key: ' ', code: 'Space', cancelable: true, ...options })
  Object.defineProperty(event, 'timeStamp', { value: timestamp })
  window.dispatchEvent(event)
  return event
}

function finish(origin: number): MainResult {
  clock.advance(origin + 60000 - clock.time)
  expect(onInterrupted).not.toHaveBeenCalled()
  expect(onComplete).toHaveBeenCalledTimes(1)
  return onComplete.mock.calls[0]![0]
}

function syntheticResult(): MainResult {
  return {
    frame_period_ms: 10, order: MAIN_CONDITIONS.map(row => ({ ...row })),
    trials: MAIN_CONDITIONS.map((row, index) => ({
      trial_number: index + 1, condition_id: row.condition_id, key_pressed: null,
      reaction_time_ms: null, key_at_ms: null, trial_start_ms: index * 3750,
      stimulus_onset_ms: index * 3750 + 300, stimulus_offset_ms: index * 3750 + 2800,
      trial_end_ms: (index + 1) * 3750,
    })),
  }
}

describe('bloco principal imperativo', () => {
  it('mede rAF durante cinco segmentos de contagem sem iniciar o cronometro', () => {
    start()
    for (const message of ['Prepare-se', '3', '2', '1', 'Começar']) {
      expect(container.dataset.phase).toBe('countdown')
      expect(container.querySelector('.main-stimulus-card')?.textContent).toBe(message)
      expect(container.querySelector<HTMLElement>('.main-hud')!.hidden).toBe(true)
      clock.advance(550)
    }
    expect(container.dataset.phase).toBe('fixation')
    expect(container.querySelector('[data-hud="time"]')?.textContent).toBe('Tempo: 00:00')
    expect(container.querySelector('[data-hud="accuracy"]')?.textContent).toBe('Precisão: —')
    expect(container.querySelector<HTMLElement>('.main-hud')!.hidden).toBe(false)
    const result = finish(clock.time)
    expect(result.frame_period_ms).toBe(10)
  })

  it('preserva ordem recebida, 16 tentativas contiguas e origem local sem contagem', () => {
    const order = [...MAIN_CONDITIONS].reverse()
    start({ order })
    const origin = mainStart()
    const result = finish(origin)
    expect(result.trials.map(row => row.condition_id)).toEqual(order.map(row => row.condition_id))
    expect(result.trials).toHaveLength(16)
    expect(result.trials[0]!.trial_start_ms).toBe(0)
    expect(result.trials[15]!.trial_end_ms).toBe(60000)
    expect(result.trials[0]!.stimulus_onset_ms).toBe(300)
    expect(result.trials[0]!.stimulus_offset_ms).toBe(2800)
    expect(result.trials.every((row, index) => index === 0
      || row.trial_start_ms === result.trials[index - 1]!.trial_end_ms)).toBe(true)
    expect(validMainResult(result)).toBe(true)
    expect(clock.frames.size).toBe(0)
    expect(container.textContent).toBe('')
  })

  it('nao encurta estimulo/intervalo por resposta e atualiza HUD somente no fim', () => {
    start()
    const origin = firstStimulus()
    clock.time += 100
    keyboard('keydown')
    expect(container.dataset.phase).toBe('stimulus')
    expect(container.textContent).toContain('Precisão: —')
    clock.advance(2394) // Antes do quadro mais proximo do offset.
    expect(container.dataset.phase).toBe('stimulus')
    clock.tickAt(origin + 2800)
    expect(container.dataset.phase).toBe('blank')
    expect(container.querySelector<HTMLElement>('.main-stimulus-card')!.style.background).toBe('transparent')
    expect(container.textContent).toContain('Precisão: —')
    clock.advance(944) // Antes do quadro mais proximo do fim.
    expect(container.dataset.phase).toBe('blank')
    clock.tickAt(origin + 3750)
    expect(container.dataset.phase).toBe('fixation')
    expect(container.querySelector('[data-hud="accuracy"]')?.textContent).toBe('Precisão: 100%')
    expect(container.querySelector('[data-hud="progress"]')?.textContent).toContain('tentativa 2 de 16')
    expect(container.querySelector('[data-hud="time"]')?.textContent).toBe('Tempo: 00:03')
    const result = finish(origin)
    expect(result.trials[0]!.reaction_time_ms).toBe(100)
    expect(result.trials[0]!.trial_end_ms).toBe(3750)
  })

  it('exercita quatro classificacoes sem feedback ou instrucao no principal', () => {
    start()
    const origin = mainStart()
    for (let index = 0; index < 16; index++) {
      clock.advance(300)
      expect(container.dataset.phase).toBe('stimulus')
      expect(container.dataset.conditionId).toBe(String(index + 1))
      expect(container.dataset.trialNumber).toBe(String(index + 1))
      expect(container.textContent).not.toContain('ESPAÇO apenas')
      if (index === 0 || index === 8) {
        clock.time += 123.456
        keyboard('keyup')
        keyboard('keydown')
        clock.tickAt(origin + index * 3750 + 2800)
      } else clock.advance(2500)
      expect(container.dataset.phase).toBe('blank')
      expect(container.dataset.outcome).toBeUndefined()
      clock.advance(950)
    }
    const result = onComplete.mock.calls[0]![0]
    const classifications = result.trials.map((trial, index) => result.order[index]!.condition === 'congruent'
      ? trial.key_pressed === 'space' ? 'hit' : 'omission'
      : trial.key_pressed === 'space' ? 'commission' : 'correct_rejection')
    expect(new Set(classifications)).toEqual(new Set(['hit', 'omission', 'commission', 'correct_rejection']))
    expect(result.trials[0]!.reaction_time_ms).toBeCloseTo(123.456, 9)
    expect(validMainResult(result)).toBe(true)
  })

  it('usa primeira nova Space e preserva o primeiro timestamp sem quantizar RT', () => {
    start()
    const origin = firstStimulus()
    clock.time += 0.0001
    keyboard('keydown')
    keyboard('keyup')
    clock.time += 100
    keyboard('keydown')
    const result = finish(origin)
    expect(result.trials[0]!.reaction_time_ms).toBeGreaterThan(0)
    expect(result.trials[0]!.reaction_time_ms).toBeLessThan(0.001)
    expect(result.trials[0]!.key_at_ms).toBeCloseTo(300.0001, 9)
  })

  it.each([
    ['inicio exato', 0, 100], ['precoce', -1, 100], ['fim exato', 2500, 2500],
    ['tardio', 2501, 2501], ['evento futuro', 101, 100], ['enfileirado', 100, 2501],
    ['entrega no deadline', 100, 2500], ['timestamp invalido', NaN, 100],
  ])('rejeita %s por timestamp e entrega, mantendo o restante do bloco', (_name, timestampDelta, deliveryDelta) => {
    start()
    const origin = firstStimulus()
    const onset = clock.time
    clock.time += Number(deliveryDelta)
    keyboard('keydown', onset + Number(timestampDelta))
    clock.tickAt(clock.time)
    const result = finish(origin)
    expect(result.trials[0]!.key_pressed).toBeNull()
    expect(result.trials[0]!.reaction_time_ms).toBeNull()
    expect(result.trials[0]!.key_at_ms).toBeNull()
  })

  it('rejeita entrega apos offset nominal mesmo antes de 2500 ms do onset observado', () => {
    start()
    const origin = mainStart()
    clock.advance(290)
    clock.tickAt(origin + 310)
    clock.time = origin + 2801
    keyboard('keydown', origin + 2700)
    clock.tickAt(clock.time)
    const result = finish(origin)
    expect(result.trials[0]!.stimulus_onset_ms).toBe(310)
    expect(result.trials[0]!.key_pressed).toBeNull()
  })

  it('aceita resposta imediatamente anterior ao deadline exclusivo', () => {
    start()
    const origin = firstStimulus()
    clock.time = origin + 2799.999
    keyboard('keydown')
    clock.tickAt(origin + 2800)
    const result = finish(origin)
    expect(result.trials[0]!.reaction_time_ms).toBeCloseTo(2499.999, 9)
  })

  it.each(['Space', ' '])('nao aceita tecla %s herdada da navegacao nem repeat', held => {
    start({ initiallyHeldKeys: [held] })
    const origin = firstStimulus()
    clock.time += 100
    keyboard('keydown')
    keyboard('keydown', clock.time, { repeat: true })
    expect(finish(origin).trials[0]!.key_pressed).toBeNull()
  })

  it('exige keyup apos tecla mantida em countdown/fixacao antes da nova resposta', () => {
    start()
    keyboard('keydown')
    const origin = firstStimulus()
    clock.time += 100
    keyboard('keydown', clock.time, { repeat: true })
    keyboard('keyup')
    clock.time += 100
    keyboard('keydown')
    expect(finish(origin).trials[0]!.reaction_time_ms).toBe(200)
  })

  it('ignora Enter, cliques e tecla mantida atravessando tentativas', () => {
    start()
    const origin = firstStimulus()
    clock.time += 100
    keyboard('keydown', clock.time, { key: 'Enter', code: 'Enter' })
    container.click()
    keyboard('keydown', clock.time, { repeat: true })
    clock.tickAt(origin + 2800)
    keyboard('keydown')
    clock.advance(950 + 300)
    keyboard('keydown', clock.time, { repeat: true })
    const result = finish(origin)
    expect(result.trials.slice(0, 2).every(row => row.key_pressed === null)).toBe(true)
  })

  it('agenda no quadro mais proximo sem fabricar instantes nem relaxar gates', () => {
    start()
    const origin = mainStart()
    clock.tickAt(origin + 294.999)
    expect(container.dataset.phase).toBe('fixation')
    clock.tickAt(origin + 295)
    expect(container.dataset.phase).toBe('stimulus')
    clock.tickAt(origin + 2794.999)
    expect(container.dataset.phase).toBe('stimulus')
    clock.tickAt(origin + 2795)
    expect(container.dataset.phase).toBe('blank')
    clock.tickAt(origin + 3745)
    expect(container.dataset.phase).toBe('fixation')
    const result = finish(origin)
    expect(result.trials[0]).toMatchObject({ trial_start_ms: 0,
      stimulus_onset_ms: 295, stimulus_offset_ms: 2795, trial_end_ms: 3745 })
    expect(result.trials[1]!.trial_start_ms).toBe(3745)
    expect(validMainResult(result)).toBe(true)
  })

  it('nao acumula atraso: novo inicio observado e compartilhado, onset seguinte segue origem global', () => {
    start()
    const origin = mainStart()
    clock.advance(2800)
    clock.tickAt(origin + 3760)
    expect(container.dataset.phase).toBe('fixation')
    clock.advance(290)
    expect(container.dataset.phase).toBe('stimulus')
    const result = finish(origin)
    expect(result.trials[0]!.trial_end_ms).toBe(3760)
    expect(result.trials[1]!.trial_start_ms).toBe(3760)
    expect(result.trials[1]!.stimulus_onset_ms).toBe(4050)
    expect(result.trials[1]!.trial_end_ms).toBe(7500)
    expect(result.trials[15]!.trial_end_ms).toBe(60000)
  })

  it('aceita gate de um quadro na igualdade e interrompe alem dela', () => {
    start()
    const origin = mainStart()
    clock.advance(290)
    clock.tickAt(origin + 310)
    expect(container.dataset.phase).toBe('stimulus')
    expect(onInterrupted).not.toHaveBeenCalled()
    const cleanup = cleanups.pop()!
    cleanup()
    clock = new ControlledClock()
    start()
    const secondOrigin = mainStart()
    clock.advance(290)
    clock.tickAt(secondOrigin + 310.000001)
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    expect(onComplete).not.toHaveBeenCalled()
  })

  it('rejeita duracao de estimulo mesmo quando transicoes isoladas passam', () => {
    start()
    const origin = mainStart()
    clock.advance(2800)
    clock.tickAt(origin + 3760)
    clock.tickAt(origin + 4070) // 310 depois do inicio observado: limite de um quadro.
    expect(container.dataset.phase).toBe('stimulus')
    clock.tickAt(origin + 6550) // Duracao 2480: diferenca de dois quadros.
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    expect(onComplete).not.toHaveBeenCalled()
  })

  it('rejeita inicio nominal fora do gate mesmo com duracao local aceitavel', () => {
    start()
    const origin = mainStart()
    clock.advance(2800)
    clock.tickAt(origin + 3760)
    clock.tickAt(origin + 4060)
    clock.tickAt(origin + 6560)
    clock.tickAt(origin + 7520)
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    expect(onComplete).not.toHaveBeenCalled()
  })

  it.each([4, 50])('mede periodo inclusivo de %s ms sem assumir 60 Hz', period => {
    start()
    clock.advance(3000, period)
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(container.dataset.phase).not.toBe('countdown')
  })

  it.each([3, 51])('recusa periodo medido fora do intervalo: %s ms', period => {
    start()
    clock.advance(3500, period)
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    expect(onComplete).not.toHaveBeenCalled()
  })

  it.each(['focus_lost', 'visibility_hidden', 'page_closed', 'escape'] as const)(
    'descarta resultados por %s, sem resumo parcial ou retomada', reason => {
      start()
      mainStart()
      clock.advance(4000)
      if (reason === 'focus_lost') window.dispatchEvent(new Event('blur'))
      if (reason === 'visibility_hidden') {
        vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('hidden')
        document.dispatchEvent(new Event('visibilitychange'))
      }
      if (reason === 'page_closed') window.dispatchEvent(new Event('pagehide'))
      if (reason === 'escape') keyboard('keydown', clock.time, { key: 'Escape', code: 'Escape' })
      expect(onInterrupted).toHaveBeenCalledExactlyOnceWith(reason)
      expect(onComplete).not.toHaveBeenCalled()
      expect(clock.frames.size).toBe(0)
      expect(container.textContent).toBe('')
      keyboard('keydown', clock.time, { key: 'Escape' })
      expect(onInterrupted).toHaveBeenCalledTimes(1)
    },
  )

  it('revalida foco, visibilidade, ordem e relogio antes e durante a execucao', () => {
    vi.spyOn(document, 'hasFocus').mockReturnValue(false)
    start()
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('focus_lost')
    onInterrupted.mockClear()
    vi.spyOn(document, 'hasFocus').mockReturnValue(true)
    vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('hidden')
    start()
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('visibility_hidden')
    onInterrupted.mockClear()
    vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('visible')
    start({ order: MAIN_CONDITIONS.slice(0, 15) })
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    onInterrupted.mockClear()
    start()
    clock.tickAt(99)
    expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
  })

  it('cleanup idempotente restaura cursor e nao emite callbacks posteriores', () => {
    container.style.cursor = 'crosshair'
    const cleanup = start()
    firstStimulus()
    cleanup()
    cleanup()
    expect(container.style.cursor).toBe('crosshair')
    expect(clock.frames.size).toBe(0)
    expect(container.dataset.phase).toBeUndefined()
    keyboard('keydown', clock.time, { key: 'Escape' })
    window.dispatchEvent(new Event('blur'))
    expect(onComplete).not.toHaveBeenCalled()
    expect(onInterrupted).not.toHaveBeenCalled()
  })

  it('rejeita troca de IDs entre Go e NoGo e alteracoes nos estimulos canonicos', () => {
    const mutations: ((order: Condition[]) => void)[] = [
      order => { order[0]!.word = 'ALTERADO' },
      order => { order[0]!.ink_color = 'blue' },
      order => { order[0]!.ink_color_display = '#ABCDEF' },
      order => { [order[0]!.condition_id, order[8]!.condition_id] = [9, 1] },
    ]
    for (const mutate of mutations) {
      onInterrupted.mockClear()
      const order = MAIN_CONDITIONS.map(row => ({ ...row }))
      mutate(order)
      start({ order })
      expect(onInterrupted).toHaveBeenCalledExactlyOnceWith('timing_invalid')
    }
  })
})

describe('gates finais equivalentes ao contrato HTTP', () => {
  it('aceita corpo nominal e mantem listas/condicoes na ordem definida', () => {
    expect(validMainResult(syntheticResult())).toBe(true)
  })

  it.each([-1, 1])('aceita desvio total inclusivo de 100 ms: direcao %s', direction => {
    const result = syntheticResult()
    result.frame_period_ms = 50
    result.trials[0]!.trial_end_ms += direction * 50
    for (const trial of result.trials.slice(1)) {
      trial.trial_start_ms += direction * 50
      trial.stimulus_onset_ms += direction * 50
      trial.stimulus_offset_ms += direction * 50
      trial.trial_end_ms += direction * 50
    }
    result.trials[15]!.trial_end_ms += direction * 50
    expect(validMainResult(result)).toBe(true)
    result.trials[15]!.trial_end_ms += direction * 0.001
    expect(validMainResult(result)).toBe(false)
  })

  it('nao relaxa fronteiras de RT nem tolerancia decimal de 0.001 ms', () => {
    const result = syntheticResult()
    const trial = result.trials[0]!
    trial.key_pressed = 'space'
    trial.key_at_ms = 812
    trial.reaction_time_ms = 512.001
    expect(validMainResult(result)).toBe(true)
    trial.reaction_time_ms = 511.999
    expect(validMainResult(result)).toBe(true)
    trial.reaction_time_ms = 512.001001
    expect(validMainResult(result)).toBe(false)
    trial.key_at_ms = 300
    trial.reaction_time_ms = 0.0001
    expect(validMainResult(result)).toBe(false)
    trial.key_at_ms = 2800
    trial.reaction_time_ms = 2499.9999
    expect(validMainResult(result)).toBe(false)
    trial.key_at_ms = 300.00000000000006
    trial.reaction_time_ms = 5e-324
    expect(validMainResult(result)).toBe(false)
  })

  it('rejeita adulteracoes de versao temporal, ordem, contagem e finitude', () => {
    const mutations: ((result: MainResult) => void)[] = [
      result => { result.frame_period_ms = 50.00001 },
      result => { result.frame_period_ms = NaN },
      result => { result.trials.pop() },
      result => { result.trials[0]!.condition_id = 2 },
      result => { result.trials[0]!.trial_number = 2 },
      result => { result.trials[0]!.trial_start_ms = 0.001 },
      result => { result.trials[1]!.trial_start_ms += 0.001 },
      result => { result.trials[0]!.stimulus_onset_ms = Infinity },
      result => { result.trials[0]!.stimulus_onset_ms += 10.000001 },
      result => { result.trials[0]!.stimulus_offset_ms += 10.000001 },
      result => { result.trials[0]!.reaction_time_ms = 100 },
    ]
    for (const mutate of mutations) {
      const result = syntheticResult()
      mutate(result)
      expect(validMainResult(result)).toBe(false)
    }
  })
})

describe('wrapper jsPsych real do principal', () => {
  it('completa somente apos todo bloco, sem rede, storage ou logs', async () => {
    vi.useFakeTimers({ toFake: ['performance', 'requestAnimationFrame', 'cancelAnimationFrame'] })
    const fetch = vi.spyOn(globalThis, 'fetch')
    const log = vi.spyOn(console, 'log')
    const warn = vi.spyOn(console, 'warn')
    cleanups.push(mountMain(container, { order: MAIN_CONDITIONS, onComplete, onInterrupted }))
    await vi.advanceTimersByTimeAsync(62_000)
    expect(onComplete).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(1500)
    expect(onComplete).toHaveBeenCalledTimes(1)
    expect(validMainResult(onComplete.mock.calls[0]![0])).toBe(true)
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(fetch).not.toHaveBeenCalled()
    expect(log).not.toHaveBeenCalled()
    expect(warn).not.toHaveBeenCalled()
    expect(localStorage.length).toBe(0)
    expect(sessionStorage.length).toBe(0)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('desmontagem antes de load ou do primeiro trial nao produz resultado', async () => {
    vi.useFakeTimers({ toFake: ['performance', 'requestAnimationFrame', 'cancelAnimationFrame'] })
    vi.spyOn(document, 'readyState', 'get').mockReturnValue('loading')
    const cleanup = mountMain(container, { order: MAIN_CONDITIONS, onComplete, onInterrupted })
    cleanups.push(cleanup)
    cleanup()
    window.dispatchEvent(new Event('load'))
    await vi.advanceTimersByTimeAsync(100_000)
    expect(onComplete).not.toHaveBeenCalled()
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(container.textContent).toBe('')
    expect(vi.getTimerCount()).toBe(0)
  })
})
