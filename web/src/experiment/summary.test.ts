import { expect, test } from 'vitest'
import shared from '../../../tests/fixtures/web_results_summary.json'
import { MAIN_CONDITIONS } from './protocol'
import { formatHalfEven, summarizeMain } from './summary'
import type { MainResult, MainTrial } from './main-engine'

for (const fixture of shared.cases) {
  test(`paridade Python: ${fixture.name}`, () => {
    const result: MainResult = {
      frame_period_ms: fixture.frame_period_ms,
      order: fixture.order.map(id => MAIN_CONDITIONS.find(row => row.condition_id === id)!),
      trials: structuredClone(fixture.trials) as MainTrial[],
    }
    const before = structuredClone(result)
    const summary = summarizeMain(result)
    for (const [key, expected] of Object.entries(fixture.expected_summary)) {
      const actual = summary[key as keyof typeof summary]
      if (expected === null) expect(actual).toBeNull()
      else expect(actual).toBeCloseTo(expected, 12)
    }
    expect(formatHalfEven(summary.accuracy, 0)).toBe(fixture.expected_display.accuracy)
    expect(summary.response_time === null ? '—' : `${formatHalfEven(summary.response_time, 3)} s`)
      .toBe(fixture.expected_display.response_time)
    expect(result).toEqual(before)
  })
}

test.each([
  [12.5, 0, '12'], [87.5, 0, '88'], [0.5005, 3, '0.500'],
  [0, 3, '0.000'], [0.5125, 3, '0.512'], [0.5135, 3, '0.513'],
])('formata float como Python sem mudar medida: %s', (value, digits, expected) => {
  expect(formatHalfEven(value, digits)).toBe(expected)
})

test('rejeita resumo parcial e medidas/formatacao invalidas', () => {
  expect(() => summarizeMain({ order: [], trials: [], frame_period_ms: 16 })).toThrow()
  expect(() => formatHalfEven(NaN, 3)).toThrow()
  expect(() => formatHalfEven(-1, 3)).toThrow()
  expect(() => formatHalfEven(1, 7)).toThrow()
})
