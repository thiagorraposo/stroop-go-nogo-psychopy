/** Resposta exclusivamente sintética para doubles QUERY7, sem acesso externo. */
import type { AnalysisBody } from '../api/analysis'
import type { Assessment } from '../api/assessments'
const expires = new Date(Date.now() + 900_000).toISOString()

export function analysisFixture(body: AnalysisBody, rows: (Assessment & { project_id?: string })[], overrides: Record<string, unknown> = {}, snapshot = 'synthetic') {
  const items = rows.map(row => ({ ...row, project_id: row.project_id ?? body.query.projects[0]! }))
  const trialCount = (row: Assessment) => 'total_trials' in row.summary ? row.summary.total_trials : 0
  const filters: Record<string, unknown> = {}
  const aliases: Record<string, string> = { date_from: 'start_date', date_to: 'end_date', participant_code: 'participant_id' }
  const basic = ['date_from', 'date_to', 'participant_code', 'visit', 'evaluator_id', 'test_code', 'test_version', 'platform']
  const legacy = Object.entries(body.query.filters).every(([key, value]) => {
    if (key === 'status') return value === 'valid'
    if (key === 'include_null_rt') return value === true
    if (!basic.includes(key)) return false
    filters[aliases[key] ?? key] = key === 'platform' ? (value as string[]).map(x => x === 'psychopy_local' ? 'psychopy' : x) : value
    return true
  })
  if (Array.isArray(filters.test_code) && filters.test_code.length === 1) filters.test_code = filters.test_code[0]
  return {
    query_id: '33333333-3333-4333-8333-333333333333', normalized_query: body.query,
    query_fingerprint: 'a'.repeat(64), content_fingerprint: 'b'.repeat(64), expires_at: expires,
    completeness: 'complete' as const,
    counts: { participants: new Set(items.map(x => `${x.project_id}/${x.participant_id}`)).size,
      visits: new Set(items.map(x => `${x.project_id}/${x.participant_id}/${x.visit}`)).size,
      assessments: items.length, trials: items.reduce((n, row) => n + trialCount(row), 0) },
    aggregates: body.query.projects.map(id => ({ project_id: id, assessments: items.filter(x => x.project_id === id).length,
      trials: items.filter(x => x.project_id === id).reduce((n, row) => n + trialCount(row), 0) })),
    items, next_cursor: null,
    indicator_definitions: { counts: { kind: 'operational_count', population: 'official_assessments_and_main_trials', timezone: 'UTC',
      participant_identity: ['project_id', 'participant_code'], visit_identity: ['project_id', 'participant_code', 'visit'] },
    summary: { source: 'stroop.domain.stroop.calculate_metrics', population: 'complete_assessment', rt_unit: 'seconds' } },
    capabilities: { filters: [...basic, 'status', 'patient_search', 'accuracy_min', 'accuracy_max', 'rt_median_min_ms', 'rt_median_max_ms', 'include_null_rt'],
      status: ['valid'], trial_filters: { stroop_go_nogo_ptbr: ['condition', 'response_type'] },
      grouping: [{ level: 'assessment', dimension: 'project' }],
      sort: ['started_at_desc', 'started_at_asc', 'participant_code_asc', 'participant_code_desc', 'visit_asc', 'accuracy_asc', 'accuracy_desc', 'response_time_asc', 'response_time_desc'],
      platform: ['web', 'psychopy_local'], max_assessments: 5000, max_projects: 20, exports: false, nominal_search: false },
    legacy_export_context: legacy ? { filters, projects: body.query.projects.map(id => ({ project_id: id, snapshot })) } : null,
    ...overrides,
  }
}
