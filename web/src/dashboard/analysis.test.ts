import { expect, test } from 'vitest'
import cases from '../../../tests/fixtures/web_results_summary.json'
import type { Assessment } from '../api/assessments'
import {
  accuracyByVisit,
  computeOverviewKPIs,
  countByDate,
  filterAssessments,
  formatMetric,
  median,
  OFFICIAL_METRICS_DICTIONARY,
  responseDistribution,
  sortAssessments,
  summarize,
} from './analysis'

const rows: Assessment[] = cases.cases.map((item, index) => ({
  assessment_id: `SYNTHETIC_${index}`,
  participant_id: `P_${index % 2}`,
  visit: 'V1',
  evaluator_id: index === 0 ? 'EVA-000001' : 'EVA-000002',
  created_at: '2026-10-16T00:00:00Z',
  started_at: `2026-10-1${6 + index}T10:00:00Z`,
  platform: 'web',
  test_code: 'stroop_go_nogo_ptbr',
  test_version: '0.2.2-web.1',
  protocol_id: null,
  app_version: null,
  summary: {
    accuracy: item.expected_summary.accuracy,
    response_time_seconds: item.expected_summary.response_time,
    accuracy_go_trials: item.expected_summary.accuracy_go_trials,
    accuracy_no_go_trials: item.expected_summary.accuracy_no_go_trials,
    total_go_trials: item.expected_summary.total_go_trials,
    total_no_go_trials: item.expected_summary.total_no_go_trials,
    total_trials: item.expected_summary.total_trials,
    hits: item.expected_summary.hits,
    omission_errors: item.expected_summary.omission_errors,
    commission_errors: item.expected_summary.commission_errors,
    correct_rejections: item.expected_summary.correct_rejections,
  },
}))

test('agregacao reproduz referencia Python sem transformar ausencia de hits em zero', () => {
  const result = summarize(rows)
  expect(result).toMatchObject({
    assessments: 5,
    participants: 2,
    meanAccuracy: 55,
    medianAccuracy: 56.25,
    omissions: 26,
    commissions: 10,
  })
  expect(result.medianResponseSeconds).toBeCloseTo(0.5060617283944999, 15)
  expect(responseDistribution(rows)).toEqual([
    ['< 0,5 s', 1],
    ['0,5 a < 1 s', 3],
    ['1 a < 1,5 s', 0],
    ['1,5 a < 2 s', 0],
    ['≥ 2 s', 0],
  ])
  expect(accuracyByVisit(rows)).toEqual([['V1', 55]])
})

test('conjunto vazio preserva ausencia de medida e nao modifica fonte da mediana', () => {
  expect(summarize([])).toEqual({
    assessments: 0,
    participants: 0,
    meanAccuracy: null,
    medianAccuracy: null,
    medianResponseSeconds: null,
    omissions: 0,
    commissions: 0,
  })
  const source = [3, 1, 2, 4]
  expect(median(source)).toBe(2.5)
  expect(source).toEqual([3, 1, 2, 4])
})

test('datas legadas sem fuso conservam dia e instrumentos genericos nao recebem metricas Stroop', () => {
  const generic: Assessment = {
    ...rows[0]!,
    started_at: '2026-10-15T23:59:00',
    test_code: 'synthetic_other',
    platform: 'psychopy',
    summary: { metrics: { accuracy: 999 } },
  }
  expect(countByDate([rows[0]!, generic])).toEqual([
    ['2026-10-15', 1],
    ['2026-10-16', 1],
  ])
  expect(summarize([generic]).meanAccuracy).toBe(null)
  expect(accuracyByVisit([generic])).toEqual([])
  expect(responseDistribution([generic]).every(([, count]) => count === 0)).toBe(true)
})

test('faixas de tempo incluem cada fronteira uma vez, sem perder RT positivo pequeno', () => {
  const source = [0.0000001, 0.5, 1, 1.5, 2].map((seconds, index) => ({
    ...rows[index]!,
    summary: { ...rows[index]!.summary, response_time_seconds: seconds },
  })) as Assessment[]
  expect(responseDistribution(source).map(([, count]) => count)).toEqual([1, 1, 1, 1, 1])
})

test('exibicao profissional preserva arredondamento Python em empates e metricas negativas', () => {
  expect(formatMetric(56.25, 1)).toBe('56,2')
  expect(formatMetric(0.5125, 3)).toBe('0,512')
  expect(formatMetric(-0.5125, 3)).toBe('-0,512')
  expect(formatMetric(null, 3)).toBe('—')
})

test('pseudonimos iguais em projetos diferentes contam participantes distintos', () => {
  const first = { ...rows[0]!, project_id: 'SYNTHETIC_PROJECT_A', participant_id: 'P_SHARED' }
  const second = { ...rows[1]!, project_id: 'SYNTHETIC_PROJECT_B', participant_id: 'P_SHARED' }
  expect(summarize([first, second, { ...first, assessment_id: 'SYNTHETIC_REPEAT' }]).participants).toBe(2)
})

test('REQ-REL-004: filtros combinados filtram por busca textual, status, precisao e RT', () => {
  const testRows = [
    { ...rows[0]!, participant_id: 'PAT-2026-001', valid_for_result: true },
    { ...rows[1]!, participant_id: 'PAT-2026-002', valid_for_result: false }, // interrompida
    { ...rows[2]!, participant_id: 'PAT-2026-003', valid_for_result: true },
  ]

  // Status valid filtra apenas as oficiais
  const validOnly = filterAssessments(testRows, { status: 'valid' })
  expect(validOnly).toHaveLength(2)
  expect(validOnly.map(r => r.participant_id)).toEqual(['PAT-2026-001', 'PAT-2026-003'])

  // Status invalid filtra apenas as interrompidas
  const invalidOnly = filterAssessments(testRows, { status: 'invalid' })
  expect(invalidOnly).toHaveLength(1)
  expect(invalidOnly[0]?.participant_id).toBe('PAT-2026-002')

  // Busca textual
  const search003 = filterAssessments(testRows, { searchText: '003' })
  expect(search003).toHaveLength(1)
  expect(search003[0]?.participant_id).toBe('PAT-2026-003')

  // Faixa de precisão: under50 vs 50to80
  const under50 = filterAssessments(rows, { accuracyRange: 'under50' })
  expect(under50.every(r => 'accuracy' in r.summary && (r.summary.accuracy ?? 100) < 50)).toBe(true)

  // Faixa de RT com exclusão ou inclusão explícita de nulo
  const nullRtRow: Assessment = {
    ...rows[0]!,
    assessment_id: 'NULL_RT',
    summary: { ...rows[0]!.summary, response_time_seconds: null, hits: 0 },
  }
  const filteredWithNullExcluded = filterAssessments([rows[0]!, nullRtRow], {
    rtRange: 'under500ms',
    includeNullRt: false,
  })
  expect(filteredWithNullExcluded.some(r => r.assessment_id === 'NULL_RT')).toBe(false)

  const filteredWithNullIncluded = filterAssessments([rows[0]!, nullRtRow], {
    rtRange: 'under500ms',
    includeNullRt: true,
  })
  expect(filteredWithNullIncluded.some(r => r.assessment_id === 'NULL_RT')).toBe(true)
})

test('REQ-REL-004: ordenacao deterministica respeita criterios e direcao', () => {
  const sortedByParticipant = sortAssessments(rows, 'participant', 'asc')
  expect(sortedByParticipant[0]?.participant_id).toBe('P_0')

  const sortedByDateDesc = sortAssessments(rows, 'date', 'desc')
  expect(sortedByDateDesc[0]!.started_at >= sortedByDateDesc[1]!.started_at).toBe(true)
})

test('CHG-005: computeOverviewKPIs agrega metricas por status, instrumento e avaliador', () => {
  const kpis = computeOverviewKPIs(rows, 12)
  expect(kpis.totalAssessments).toBe(5)
  expect(kpis.registeredPatients).toBe(12)
  expect(kpis.byStatus.valid).toBe(5)
  expect(kpis.byInstrument['stroop_go_nogo_ptbr']).toBe(5)
  expect(kpis.byEvaluator['EVA-000001']).toBe(1)
  expect(kpis.byEvaluator['EVA-000002']).toBe(4)
})

test('CHG-005: dicionario de metricas oficiais contem todas as 6 metricas com origem, definicao e nulos', () => {
  expect(OFFICIAL_METRICS_DICTIONARY).toHaveLength(6)
  const codes = OFFICIAL_METRICS_DICTIONARY.map(m => m.code)
  expect(codes).toEqual([
    'accuracy',
    'accuracy_go_trials',
    'accuracy_no_go_trials',
    'response_time_seconds',
    'omission_errors',
    'commission_errors',
  ])
  for (const metric of OFFICIAL_METRICS_DICTIONARY) {
    expect(metric.label.length).toBeGreaterThan(0)
    expect(metric.origin.length).toBeGreaterThan(5)
    expect(metric.definition.length).toBeGreaterThan(10)
    expect(metric.unit.length).toBeGreaterThan(0)
    expect(metric.nullTreatment.toLowerCase()).toContain('nulo')
  }
})
