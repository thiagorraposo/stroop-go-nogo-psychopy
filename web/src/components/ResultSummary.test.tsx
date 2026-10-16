// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { expect, test, vi } from 'vitest'
import { ResultSummaryPanel } from './ResultSummary'
import type { ResultSummary } from '../experiment/summary'

Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
const summary: ResultSummary = { accuracy: 12.5, accuracy_go_trials: 25,
  accuracy_no_go_trials: 0, omission_errors: 6, omission_errors_percentage: 75,
  commission_errors: 8, response_time: 0.5125, total_trials: 16,
  total_go_trials: 8, total_no_go_trials: 8, hits: 2, correct_rejections: 0 }

test('resumo descritivo acessivel, sem exportacao participante nem salvo ficticio', async () => {
  const container = document.createElement('div')
  document.body.append(container)
  const root = createRoot(container)
  const finish = vi.fn()
  try {
    await act(async () => { root.render(<ResultSummaryPanel summary={summary} onFinish={finish} />) })
    expect(container.querySelector('h1')?.textContent).toBe('Resumo da execução')
    expect(document.activeElement).toBe(container.querySelector('section'))
    expect(container.textContent).toContain('12%')
    expect(container.textContent).toContain('0.512 s')
    expect(container.textContent).toContain('não representa diagnóstico')
    expect(container.querySelector('[role="status"]')?.textContent).toContain('ainda não possui confirmação')
    expect(container.querySelectorAll('a[download]')).toHaveLength(0)
    expect(container.querySelectorAll('button')).toHaveLength(1)
    await act(async () => { container.querySelector('button')!.click() })
    expect(finish).toHaveBeenCalledOnce()
    await act(async () => { root.render(<ResultSummaryPanel summary={{ ...summary, hits: 0, response_time: null }} onFinish={finish} />) })
    expect([...container.querySelectorAll('dd')].map(node => node.textContent)).toContain('—')
  } finally {
    await act(async () => { root.unmount() })
    container.remove()
  }
})
