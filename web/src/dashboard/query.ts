/** Contexto de consulta em RAM. Não é fingerprint de conteúdo/autorização do servidor. */
import type { AssessmentOptions } from '../api/assessments'

export type AdvancedFilterValues = {
  searchText: string
  status: 'valid' | 'all' | 'invalid'
  accuracyRange: 'all' | 'under50' | '50to80' | '80plus'
  rtRange: 'all' | 'under500ms' | '500to1000ms' | '1000to1500ms' | '1500msPlus'
  includeNullRt: boolean
  condition: 'all' | 'congruent' | 'incongruent' | 'go' | 'nogo'
  responseType: 'all' | 'hits' | 'omissions' | 'commissions' | 'correct_rejections'
  sortBy: 'date' | 'participant' | 'accuracy' | 'response_time'
  sortOrder: 'asc' | 'desc'
}

export type ResearchQuery = {
  projects: string[]
  filters: AssessmentOptions
  advanced?: AdvancedFilterValues
}


export const defaultAdvanced: AdvancedFilterValues = {
  searchText: '', status: 'valid', accuracyRange: 'all', rtRange: 'all',
  includeNullRt: true, condition: 'all', responseType: 'all',
  sortBy: 'date', sortOrder: 'desc',
}

export function defaultQuery(project: string): ResearchQuery {
  return { projects: project ? [project] : [], filters: {}, advanced: { ...defaultAdvanced } }
}

/** Remove transporte, vazios e duplicatas; ordena dimensões sem mudar seus valores. */
export function normalizeQuery(query: ResearchQuery): ResearchQuery {
  const filters: AssessmentOptions = {}
  for (const key of ['start_date', 'end_date', 'test_code'] as const) {
    if (query.filters[key]) filters[key] = query.filters[key]
  }
  for (const key of ['participant_id', 'visit', 'evaluator_id', 'test_version', 'platform'] as const) {
    const raw = query.filters[key]
    const values = [...new Set(typeof raw === 'string' ? [raw] : raw ?? [])].sort()
    if (values.length) Object.assign(filters, { [key]: values })
  }
  return {
    projects: [...new Set(query.projects)].sort(), filters,
    advanced: { ...defaultAdvanced, ...query.advanced },
  }
}

/** Identidade local: nunca escrever em URL/storage/log nem apresentar como hash público. */
export function queryKey(query: ResearchQuery): string {
  return JSON.stringify(normalizeQuery(query))
}

/** O agregado atual só suporta dimensões básicas. Falha fechada até WEB-051/053. */
export function supportsLegacyExport(query: ResearchQuery): boolean {
  const a = normalizeQuery(query).advanced!
  return !a.searchText && a.status === 'valid' && a.accuracyRange === 'all'
    && a.rtRange === 'all' && a.includeNullRt && a.condition === 'all' && a.responseType === 'all'
}
