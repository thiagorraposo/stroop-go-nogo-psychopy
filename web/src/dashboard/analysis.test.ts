import { expect, test } from 'vitest'
import cases from '../../../tests/fixtures/web_results_summary.json'
import type { Assessment } from '../api/assessments'
import { accuracyByVisit, countByDate, median, responseDistribution, summarize } from './analysis'
const rows: Assessment[] = cases.cases.map((item, index) => ({
  assessment_id: `SYNTHETIC_${index}`, participant_id: `P_${index % 2}`, visit: 'V1', evaluator_id: null,
  created_at: '2026-10-16T00:00:00Z', started_at: '2026-10-16T00:00:00Z', platform: 'web',
  test_code: 'stroop_go_nogo_ptbr', test_version: '0.2.2-web.1', protocol_id: null, app_version: null,
  summary: { accuracy: item.expected_summary.accuracy, response_time_seconds: item.expected_summary.response_time,
    total_trials: item.expected_summary.total_trials, hits: item.expected_summary.hits,
    omission_errors: item.expected_summary.omission_errors, commission_errors: item.expected_summary.commission_errors,
    correct_rejections: item.expected_summary.correct_rejections },
}))
test('agregacao reproduz referencia Python sem transformar ausencia de hits em zero', () => {
  const result = summarize(rows)
  expect(result).toMatchObject({ assessments: 5, participants: 2, meanAccuracy: 55, medianAccuracy: 56.25,
    omissions: 26, commissions: 10 })
  expect(result.medianResponseSeconds).toBeCloseTo(0.5060617283944999, 15)
  expect(responseDistribution(rows)).toEqual([['< 0,5 s', 1], ['0,5 a < 1 s', 3], ['1 a < 1,5 s', 0], ['1,5 a < 2 s', 0], ['≥ 2 s', 0]])
  expect(accuracyByVisit(rows)).toEqual([['V1', 55]])
})
test('conjunto vazio preserva ausencia de medida e nao modifica fonte da mediana', () => {
  expect(summarize([])).toEqual({ assessments: 0, participants: 0, meanAccuracy: null,
    medianAccuracy: null, medianResponseSeconds: null, omissions: 0, commissions: 0 })
  const source = [3, 1, 2, 4]; expect(median(source)).toBe(2.5); expect(source).toEqual([3, 1, 2, 4])
})
test('datas legadas sem fuso conservam dia e instrumentos genericos nao recebem metricas Stroop', () => {
  const generic: Assessment = { ...rows[0]!, started_at: '2026-10-15T23:59:00',
    test_code: 'synthetic_other', platform: 'psychopy', summary: { metrics: { accuracy: 999 } } }
  expect(countByDate([rows[0]!, generic])).toEqual([['2026-10-15', 1], ['2026-10-16', 1]])
  expect(summarize([generic]).meanAccuracy).toBe(null)
  expect(accuracyByVisit([generic])).toEqual([])
  expect(responseDistribution([generic]).every(([, count]) => count === 0)).toBe(true)
})
test('faixas de tempo incluem cada fronteira uma vez, sem perder RT positivo pequeno', () => {
  const source = [0.0000001, 0.5, 1, 1.5, 2].map((seconds, index) => ({
    ...rows[index]!, summary: { ...rows[index]!.summary, response_time_seconds: seconds },
  })) as Assessment[]
  expect(responseDistribution(source).map(([, count]) => count)).toEqual([1, 1, 1, 1, 1])
})
