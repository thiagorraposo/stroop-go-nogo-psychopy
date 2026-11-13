/** Agregacoes descritivas sobre o conjunto autorizado filtrado, sem normas. */
import { formatHalfEven } from '../experiment/summary'
import type { Assessment } from '../api/assessments'

export type OfficialMetricDefinition = {
  code: string
  label: string
  origin: string
  definition: string
  unit: string
  nullTreatment: string
}

export const OFFICIAL_METRICS_DICTIONARY: readonly OfficialMetricDefinition[] = [
  {
    code: 'accuracy',
    label: 'Precisão geral',
    origin: 'Fórmula oficial Stroop Go/No-Go: (hits + correct_rejections) / total_trials * 100',
    definition: 'Proporção percentual de respostas corretas sobre o total de tentativas do teste (estímulos Go e No-Go).',
    unit: '%',
    nullTreatment: 'Nulo (—) se o teste não possuir tentativas válidas.',
  },
  {
    code: 'accuracy_go_trials',
    label: 'Precisão Go',
    origin: 'Fórmula oficial Stroop Go/No-Go: hits / total_go_trials * 100',
    definition: 'Proporção percentual de acertos em estímulos Go (respostas com barra de espaço).',
    unit: '%',
    nullTreatment: 'Nulo (—) se não houver tentativas Go.',
  },
  {
    code: 'accuracy_no_go_trials',
    label: 'Precisão No-Go',
    origin: 'Fórmula oficial Stroop Go/No-Go: correct_rejections / total_no_go_trials * 100',
    definition: 'Proporção percentual de inibições motoras corretas em estímulos No-Go (sem resposta).',
    unit: '%',
    nullTreatment: 'Nulo (—) se não houver tentativas No-Go.',
  },
  {
    code: 'response_time_seconds',
    label: 'Tempo de reação mediano',
    origin: 'Fórmula oficial Stroop Go/No-Go: mediana aritmética dos RTs de acertos (hits)',
    definition: 'Tempo mediano decorrido entre o surgimento do estímulo e o pressionamento da barra de espaço nas tentativas Go corretas.',
    unit: 's (3 casas decimais)',
    nullTreatment: 'Explicitamente nulo (—) quando hits = 0; nunca transformado em zero para não falsear a latência física.',
  },
  {
    code: 'omission_errors',
    label: 'Erros de omissão',
    origin: 'Contagem direta de tentativas Go sem resposta dentro do tempo limite',
    definition: 'Número de estímulos Go em que o participante não emitiu resposta motora esperada.',
    unit: 'contagem inteira',
    nullTreatment: 'Não admite nulo: sempre zero ou número inteiro positivo (≥ 0).',
  },
  {
    code: 'commission_errors',
    label: 'Erros de comissão',
    origin: 'Contagem direta de respostas emitidas indevidamente em tentativas No-Go',
    definition: 'Número de estímulos No-Go em que o participante pressionou a barra de espaço (falha de inibição motora).',
    unit: 'contagem inteira',
    nullTreatment: 'Não admite nulo: sempre zero ou número inteiro positivo (≥ 0).',
  },
]

export type AdvancedFilterCriteria = {
  searchText?: string
  status?: 'all' | 'valid' | 'invalid'
  accuracyRange?: 'all' | 'under50' | '50to80' | '80plus'
  rtRange?: 'all' | 'under500ms' | '500to1000ms' | '1000to1500ms' | '1500msPlus'
  includeNullRt?: boolean
  sortBy?: 'date' | 'participant' | 'accuracy' | 'response_time'
  sortOrder?: 'asc' | 'desc'
}

export function median(values: readonly number[]): number | null {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[middle]! : (sorted[middle - 1]! + sorted[middle]!) / 2
}

export function summarize(rows: readonly (Assessment & { project_id?: string })[]) {
  const accuracies: number[] = [], times: number[] = []
  let omissions = 0, commissions = 0
  for (const row of rows) {
    if ('metrics' in row.summary) continue
    if (row.summary.accuracy !== null) accuracies.push(row.summary.accuracy)
    if (row.summary.response_time_seconds !== null) times.push(row.summary.response_time_seconds)
    omissions += row.summary.omission_errors
    commissions += row.summary.commission_errors
  }
  return {
    assessments: rows.length,
    participants: new Set(rows.map(row => JSON.stringify([row.project_id ?? '', row.participant_id]))).size,
    meanAccuracy: accuracies.length ? accuracies.reduce((a, b) => a + b, 0) / accuracies.length : null,
    medianAccuracy: median(accuracies),
    medianResponseSeconds: median(times),
    omissions,
    commissions,
  }
}

export function countByDate(rows: readonly Assessment[]): [string, number][] {
  const dates = new Map<string, number>()
  for (const row of rows) {
    const day = row.started_at.slice(0, 10)
    dates.set(day, (dates.get(day) ?? 0) + 1)
  }
  return [...dates].sort(([a], [b]) => a.localeCompare(b))
}

export function accuracyByVisit(rows: readonly Assessment[]): [string, number][] {
  const values = new Map<string, number[]>()
  for (const row of rows) {
    if (!('accuracy' in row.summary) || row.summary.accuracy === null) continue
    const group = values.get(row.visit) ?? []
    group.push(row.summary.accuracy)
    values.set(row.visit, group)
  }
  return [...values].sort(([a], [b]) => a.localeCompare(b)).map(([visit, scores]) => [
    visit,
    scores.reduce((a, b) => a + b, 0) / scores.length,
  ])
}

export function responseDistribution(rows: readonly Assessment[]): [string, number][] {
  const groups: [string, number][] = [
    ['< 0,5 s', 0],
    ['0,5 a < 1 s', 0],
    ['1 a < 1,5 s', 0],
    ['1,5 a < 2 s', 0],
    ['≥ 2 s', 0],
  ]
  for (const row of rows) {
    if (!('response_time_seconds' in row.summary) || row.summary.response_time_seconds === null) continue
    const index = Math.min(4, Math.max(0, Math.floor(row.summary.response_time_seconds / 0.5)))
    groups[index]![1] += 1
  }
  return groups
}

/** Exibicao igual ao formatador Python do Streamlit, com separador pt-BR. */
export function formatMetric(value: number | null, digits = 0): string {
  if (value === null) return '—'
  const sign = value < 0 || Object.is(value, -0) ? '-' : ''
  return sign + formatHalfEven(Math.abs(value), digits).replace('.', ',')
}

/** Filtra avaliações no cliente aplicando o catálogo avançado de filtros determinísticos (REQ-REL-004). */
export function filterAssessments<T extends Assessment & { project_id?: string; valid_for_result?: boolean }>(
  rows: readonly T[],
  criteria?: AdvancedFilterCriteria,
): T[] {
  if (!criteria) return [...rows]
  return rows.filter(row => {
    // 1. Filtro por status (válida vs interrompida/inválida)
    if (criteria.status === 'valid') {
      if (row.valid_for_result === false) return false
    } else if (criteria.status === 'invalid') {
      if (row.valid_for_result !== false) return false
    }

    // 2. Busca textual por código, participante, visita ou avaliador
    if (criteria.searchText) {
      const needle = criteria.searchText.trim().toLowerCase()
      if (needle.length > 0) {
        const haystacks = [
          row.assessment_id,
          row.participant_id,
          row.visit,
          row.evaluator_id ?? '',
          row.test_code,
          row.test_version,
          row.project_id ?? '',
        ].map(s => s.toLowerCase())
        if (!haystacks.some(s => s.includes(needle))) return false
      }
    }

    // 3. Faixa de precisão (aplicável a Stroop)
    if (criteria.accuracyRange && criteria.accuracyRange !== 'all') {
      if (!('accuracy' in row.summary) || row.summary.accuracy === null) return false
      const acc = row.summary.accuracy
      if (criteria.accuracyRange === 'under50' && acc >= 50) return false
      if (criteria.accuracyRange === '50to80' && (acc < 50 || acc >= 80)) return false
      if (criteria.accuracyRange === '80plus' && acc < 80) return false
    }

    // 4. Faixa de tempo de reação mediano e tratamento explícito de ausência
    if (criteria.rtRange && criteria.rtRange !== 'all') {
      if (!('response_time_seconds' in row.summary)) return false
      const rt = row.summary.response_time_seconds
      if (rt === null) {
        if (!criteria.includeNullRt) return false
      } else {
        if (criteria.rtRange === 'under500ms' && rt >= 0.5) return false
        if (criteria.rtRange === '500to1000ms' && (rt < 0.5 || rt >= 1.0)) return false
        if (criteria.rtRange === '1000to1500ms' && (rt < 1.0 || rt >= 1.5)) return false
        if (criteria.rtRange === '1500msPlus' && rt < 1.5) return false
      }
    }

    return true
  })
}

/** Ordena as avaliações com semântica determinística. */
export function sortAssessments<T extends Assessment>(
  rows: readonly T[],
  sortBy: AdvancedFilterCriteria['sortBy'] = 'date',
  sortOrder: AdvancedFilterCriteria['sortOrder'] = 'desc',
): T[] {
  const modifier = sortOrder === 'asc' ? 1 : -1
  return [...rows].sort((a, b) => {
    if (sortBy === 'participant') {
      const cmp = a.participant_id.localeCompare(b.participant_id)
      return cmp !== 0 ? cmp * modifier : a.started_at.localeCompare(b.started_at) * -1
    }
    if (sortBy === 'accuracy') {
      const accA = 'accuracy' in a.summary ? a.summary.accuracy : null
      const accB = 'accuracy' in b.summary ? b.summary.accuracy : null
      if (accA === null && accB === null) return 0
      if (accA === null) return 1
      if (accB === null) return -1
      const cmp = accA - accB
      return cmp !== 0 ? cmp * modifier : a.started_at.localeCompare(b.started_at) * -1
    }
    if (sortBy === 'response_time') {
      const rtA = 'response_time_seconds' in a.summary ? a.summary.response_time_seconds : null
      const rtB = 'response_time_seconds' in b.summary ? b.summary.response_time_seconds : null
      if (rtA === null && rtB === null) return 0
      if (rtA === null) return 1
      if (rtB === null) return -1
      const cmp = rtA - rtB
      return cmp !== 0 ? cmp * modifier : a.started_at.localeCompare(b.started_at) * -1
    }
    // Padrão: por data de início
    const cmp = a.started_at.localeCompare(b.started_at)
    return cmp !== 0 ? cmp * modifier : a.assessment_id.localeCompare(b.assessment_id)
  })
}

export type OverviewKPIs = {
  totalAssessments: number
  uniqueParticipants: number
  registeredPatients: number | null
  byStatus: { valid: number; invalid: number }
  byInstrument: Record<string, number>
  byProject: Record<string, number>
  byEvaluator: Record<string, number>
  temporalEvolution: [string, number][]
  summary: ReturnType<typeof summarize>
}

/** Calcula os KPIs e distribuições descritivas da Visão Geral (CHG-005). */
export function computeOverviewKPIs(
  rows: readonly (Assessment & { project_id?: string; valid_for_result?: boolean })[],
  registeredPatientsCount: number | null = null,
): OverviewKPIs {
  const byStatus = { valid: 0, invalid: 0 }
  const byInstrument: Record<string, number> = {}
  const byProject: Record<string, number> = {}
  const byEvaluator: Record<string, number> = {}

  for (const row of rows) {
    if (row.valid_for_result === false) byStatus.invalid += 1
    else byStatus.valid += 1

    byInstrument[row.test_code] = (byInstrument[row.test_code] ?? 0) + 1
    const p = row.project_id ?? 'principal'
    byProject[p] = (byProject[p] ?? 0) + 1
    const ev = row.evaluator_id ?? 'Não informado'
    byEvaluator[ev] = (byEvaluator[ev] ?? 0) + 1
  }

  return {
    totalAssessments: rows.length,
    uniqueParticipants: new Set(rows.map(row => JSON.stringify([row.project_id ?? '', row.participant_id]))).size,
    registeredPatients: registeredPatientsCount,
    byStatus,
    byInstrument,
    byProject,
    byEvaluator,
    temporalEvolution: countByDate(rows),
    summary: summarize(rows),
  }
}
