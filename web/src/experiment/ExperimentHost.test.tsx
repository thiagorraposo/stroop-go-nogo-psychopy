// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, expect, test, vi } from 'vitest'
import { ExperimentHost } from './ExperimentHost'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
afterEach(() => { document.body.replaceChildren() })

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
