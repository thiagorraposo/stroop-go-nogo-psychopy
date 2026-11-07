// @vitest-environment jsdom
import { act, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, expect, test, vi } from 'vitest'
import { ExperimentHost } from './ExperimentHost'
import { mountMain } from './main'
import { mountPractice } from './practice'
import { MAIN_CONDITIONS } from './protocol'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
  document.body.replaceChildren()
})

test('o motor conserva seu DOM entre renderizacoes e limpa ao sair', async () => {
  const container = document.createElement('div')
  document.body.append(container)
  const root = createRoot(container)
  const cleanup = vi.fn()
  const mount = vi.fn((host: HTMLDivElement) => {
    host.textContent = 'ESTIMULO SINTETICO'
    return cleanup
  })
  await act(async () => { root.render(<ExperimentHost mount={mount} />) })
  await act(async () => { root.render(<ExperimentHost mount={mount} />) })
  expect(mount).toHaveBeenCalledTimes(1)
  expect(container.textContent).toBe('ESTIMULO SINTETICO')
  expect(cleanup).not.toHaveBeenCalled()
  await act(async () => { root.unmount() })
  expect(cleanup).toHaveBeenCalledTimes(1)
})

test.each(['practice', 'main'] as const)('StrictMode desmonta e remonta plugin %s real sem callbacks residuais', async kind => {
  vi.useFakeTimers({ toFake: ['performance', 'requestAnimationFrame', 'cancelAnimationFrame'] })
  vi.spyOn(document, 'hasFocus').mockReturnValue(true)
  vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('visible')
  vi.spyOn(document, 'readyState', 'get').mockReturnValue('complete')
  const container = document.createElement('div')
  document.body.append(container)
  const root = createRoot(container)
  const onComplete = vi.fn()
  const onInterrupted = vi.fn()
  const mount = vi.fn((host: HTMLDivElement) => kind === 'main'
    ? mountMain(host, { order: MAIN_CONDITIONS, onComplete, onInterrupted })
    : mountPractice(host, { onComplete, onInterrupted }))
  try {
    await act(async () => { root.render(<StrictMode><ExperimentHost mount={mount} /></StrictMode>) })
    await act(async () => { await vi.advanceTimersByTimeAsync(5000) })
    expect(mount).toHaveBeenCalledTimes(2)
    expect(container.querySelectorAll(`.${kind}-runtime`)).toHaveLength(1)
    await act(async () => { root.unmount() })
    window.dispatchEvent(new Event('blur'))
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await act(async () => { await vi.advanceTimersByTimeAsync(100_000) })
    expect(onComplete).not.toHaveBeenCalled()
    expect(onInterrupted).not.toHaveBeenCalled()
    expect(container.textContent).toBe('')
    expect(vi.getTimerCount()).toBe(0)
  } finally {
    if (container.firstChild) await act(async () => { root.unmount() })
  }
})
