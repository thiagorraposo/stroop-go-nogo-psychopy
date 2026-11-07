// @vitest-environment jsdom
import { expect, test } from 'vitest'
import { createExperimentHud } from './presentation'
import { PROTOCOL } from './protocol'
import { APP_VERSION } from '../api/participant'

test('progresso usa total recebido e concluídas, sem desempenho agregado ou relógio de prática', () => {
  const hud = createExperimentHud('practice', 6)
  for (const completed of [0, 1, 3, 6]) {
    hud.update(completed)
    expect(hud.element.querySelector('[data-hud="progress"]')?.textContent).toBe(`Prática · ${completed} / 6`)
    expect(hud.element.querySelector('[role="progressbar"]')?.getAttribute('aria-valuenow')).toBe(String(completed))
    expect(hud.element.querySelector('[role="progressbar"]')?.getAttribute('aria-valuemax')).toBe('6')
  }
  expect(hud.element.querySelectorAll('[data-hud]')).toHaveLength(1)
  expect(hud.element.outerHTML).not.toMatch(/accuracy|Precisão|acerto|erro|tooltip|meter/)
})

test('cronômetro recebe elapsed do motor sem acumular ticks nem reescrever DOM a cada quadro', () => {
  const hud = createExperimentHud('main', PROTOCOL.main.trials)
  hud.update(0, 0)
  expect(hud.element.querySelector('[data-hud="time"]')?.textContent).toBe('Tempo: 00:00')
  const observer = new MutationObserver(() => undefined)
  observer.observe(hud.element, { subtree: true, childList: true, attributes: true, characterData: true })
  for (let elapsed = 10; elapsed < 1000; elapsed += 10) hud.update(0, elapsed)
  expect(observer.takeRecords()).toHaveLength(0)
  hud.update(1, 3750)
  expect(hud.element.querySelector('[data-hud="time"]')?.textContent).toBe('Tempo: 00:03')
  hud.update(16, 60000)
  expect(hud.element.querySelector('[data-hud="time"]')?.textContent).toBe('Tempo: 01:00')
  observer.disconnect()
})

test('snapshot e app_version distinguem visual novo sem mudar identificação cognitiva', () => {
  expect(PROTOCOL.visual).toEqual({ id: 'stroop-web-outline', version: '1.0.0' })
  expect(PROTOCOL.hud).toEqual({ live_accuracy: false, main_timer: true, progress: true })
  expect(APP_VERSION).toBe('web-0.1.0+visual.1.0.0')
})
