/** Consulta aplicada em RAM, sem fallback GET ou filtros locais de resultados. */
import { ApiError, record, request } from './client'
import { decodeAssessment } from './assessments'
import type { Assessment } from './assessments'
import type { ExportContext } from './aggregate'

export type AnalysisBody = {
  query: { projects: string[]; filters: Record<string, unknown> }
  grouping: { level: 'assessment'; dimension: 'project' }
  page: { size: number; sort: string; cursor?: string }
}
export type AnalysisPage = {
  query_id: string; normalized_query: AnalysisBody['query']; query_fingerprint: string; content_fingerprint: string
  expires_at: string; completeness: 'complete'
  counts: { participants: number; visits: number; assessments: number; trials: number }
  aggregates: { project_id: string; assessments: number; trials: number }[]
  items: (Assessment & { project_id: string })[]; next_cursor: string | null
  legacy_export_context: ExportContext | null
}
const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/
const fingerprint = /^[a-f\d]{64}$/
const token = /^[A-Za-z0-9_-]{1,1024}$/
const count = (x: unknown): x is number => Number.isSafeInteger(x) && Number(x) >= 0
const closed = (x: unknown, keys: string): x is Record<string, unknown> => record(x)
  && Object.keys(x).length === keys.split(' ').length && keys.split(' ').every(key => Object.hasOwn(x, key))
function invalid(): never { throw new ApiError('invalid_response', 200) }
/** Ordena chaves sem alterar a ordem dos arrays canônicos. */
export function contextKey(x: unknown): string {
  return JSON.stringify(x, (_key, value) => record(value)
    ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0)) : value)
}
export function decodeAnalysisPage(value: unknown, body: AnalysisBody): AnalysisPage {
  if (!closed(value, 'query_id normalized_query query_fingerprint content_fingerprint expires_at completeness counts indicator_definitions aggregates items next_cursor capabilities legacy_export_context')
    || typeof value.query_id !== 'string' || !uuid.test(value.query_id)
    || ![value.query_fingerprint, value.content_fingerprint].every(x => typeof x === 'string' && fingerprint.test(x))
    || typeof value.expires_at !== 'string' || !/^\d{4}-\d{2}-\d{2}T.*Z$/.test(value.expires_at)
    || !Number.isFinite(Date.parse(value.expires_at)) || Date.parse(value.expires_at) <= Date.now()
    || value.completeness !== 'complete' || contextKey(value.normalized_query) !== contextKey(body.query)
    || !closed(value.counts, 'participants visits assessments trials') || !Object.values(value.counts).every(count)
    || Number(value.counts.assessments) > 5000 || Number(value.counts.participants) > Number(value.counts.assessments)
    || Number(value.counts.visits) > Number(value.counts.assessments)
    || !Array.isArray(value.items) || value.items.length > body.page.size
    || !(value.next_cursor === null || typeof value.next_cursor === 'string' && token.test(value.next_cursor))
    || !Array.isArray(value.aggregates) || value.aggregates.length !== body.query.projects.length) return invalid()
  const expectedDefinitions = {
    counts: { kind: 'operational_count', population: 'official_assessments_and_main_trials', timezone: 'UTC',
      participant_identity: ['project_id', 'participant_code'], visit_identity: ['project_id', 'participant_code', 'visit'] },
    summary: { source: 'stroop.domain.stroop.calculate_metrics', population: 'complete_assessment', rt_unit: 'seconds' },
  }
  if (contextKey(value.indicator_definitions) !== contextKey(expectedDefinitions)
    || !closed(value.capabilities, 'filters status trial_filters grouping sort platform max_assessments max_projects exports nominal_search')
    || value.capabilities.exports !== false || value.capabilities.nominal_search !== false
    || value.capabilities.max_assessments !== 5000 || value.capabilities.max_projects !== 20
    || contextKey(value.capabilities.status) !== '["valid"]'
    || contextKey(value.capabilities.platform) !== '["web","psychopy_local"]'
    || contextKey(value.capabilities.grouping) !== contextKey([body.grouping])
    || contextKey(value.capabilities.trial_filters) !== contextKey({ stroop_go_nogo_ptbr: ['condition', 'response_type'] })
    || !Array.isArray(value.capabilities.filters) || !value.capabilities.filters.every(x => typeof x === 'string')
    || !Object.keys(body.query.filters).every(key => key === 'condition' || key === 'response_type' || (value.capabilities as Record<string, unknown[]>).filters!.includes(key))
    || !Array.isArray(value.capabilities.sort) || !value.capabilities.sort.every(x => typeof x === 'string')
    || !value.capabilities.sort.includes(body.page.sort)) return invalid()
  const items = value.items.map(item => {
    if (!record(item) || typeof item.project_id !== 'string' || !body.query.projects.includes(item.project_id)) return invalid()
    const { project_id, ...assessment } = item
    return { ...decodeAssessment(assessment), project_id }
  })
  if (new Set(items.map(item => item.assessment_id)).size !== items.length) return invalid()
  const aggregates = value.aggregates.map((entry, index) => {
    if (!closed(entry, 'project_id assessments trials') || entry.project_id !== body.query.projects[index]
      || !count(entry.assessments) || !count(entry.trials)) return invalid()
    return entry as AnalysisPage['aggregates'][number]
  })
  if (aggregates.reduce((n, item) => n + item.assessments, 0) !== value.counts.assessments
    || aggregates.reduce((n, item) => n + item.trials, 0) !== value.counts.trials) return invalid()
  if (value.legacy_export_context !== null) {
    const context = value.legacy_export_context
    if (!closed(context, 'projects filters') || !Array.isArray(context.projects)
      || context.projects.length !== body.query.projects.length || !record(context.filters)) return invalid()
    const filters: Record<string, unknown> = {}
    const aliases: Record<string, string> = { date_from: 'start_date', date_to: 'end_date', participant_code: 'participant_id' }
    for (const [key, input] of Object.entries(body.query.filters)) {
      if (key === 'status' && input === 'valid' || key === 'include_null_rt' && input === true) continue
      if (!['date_from', 'date_to', 'participant_code', 'visit', 'evaluator_id', 'test_code', 'test_version', 'platform'].includes(key)) return invalid()
      filters[aliases[key] ?? key] = key === 'platform' ? (input as string[]).map(x => x === 'psychopy_local' ? 'psychopy' : x) : input
    }
    // GET canoniza instrumento único como string; demais dimensões são arrays.
    if (Array.isArray(filters.test_code) && filters.test_code.length === 1) filters.test_code = filters.test_code[0]
    if (contextKey(context.filters) !== contextKey(filters)) return invalid()
    context.projects.forEach((entry, index) => {
      if (!closed(entry, 'project_id snapshot') || entry.project_id !== body.query.projects[index]
        || typeof entry.snapshot !== 'string' || !token.test(entry.snapshot)) return invalid()
    })
  }
  return { ...value, items, aggregates } as unknown as AnalysisPage
}

export function queryAnalysis(body: AnalysisBody, csrf: string, signal?: AbortSignal): Promise<AnalysisPage> {
  if (!/^[A-Za-z0-9_-]{43}$/.test(csrf) || !body.query.projects.length || body.query.projects.length > 20
    || !body.query.projects.every(id => uuid.test(id)) || new TextEncoder().encode(JSON.stringify(body)).length > 65_536) {
    return Promise.reject(new ApiError('invalid_request', 422))
  }
  return request('/api/v1/analysis/query', { method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify(body) },
  async response => {
    if (response.status !== 200) return invalid()
    let value: unknown
    try { value = await response.json() } catch { return invalid() }
    return decodeAnalysisPage(value, body)
  }, signal)
}
