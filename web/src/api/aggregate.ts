/** Exportacao explicita da visao confirmada, com snapshots somente em RAM. */
import { ApiError, record, request } from './client'
import { assessmentFilterParams } from './assessments'
import type { AssessmentOptions } from './assessments'
export type ExportProject = { project_id: string; snapshot: string }
export type ExportContext = { projects: ExportProject[]; filters: AssessmentOptions }
export type ExportView = { test_code: string; platform?: 'web' | 'psychopy' }
const multi = ['participant_id', 'visit', 'evaluator_id', 'test_version', 'platform', 'test_code'] as const
const singles = ['start_date', 'end_date'] as const
const instruments = ['stroop_go_nogo_ptbr', 'instrumento_sintetico_demo']
export function exportAssessmentView(context: ExportContext, view: ExportView, csrf: string, signal?: AbortSignal): Promise<{ filename: string; blob: Blob }> {
  const fail = (): never => { throw new ApiError('invalid_request', 422) }
  if (!record(context) || !Array.isArray(context.projects) || !context.projects.length || context.projects.length > 20
    || !record(context.filters) || Object.keys(context.filters).some(key => ![...multi, ...singles].includes(key as typeof multi[number]))
    || !record(view) || Object.keys(view).some(key => key !== 'test_code' && key !== 'platform')
    || !instruments.includes(view.test_code) || view.platform !== undefined && !['web', 'psychopy'].includes(view.platform)
    || !/^[A-Za-z0-9_-]{43}$/.test(csrf)) return fail()
  const projects = context.projects.map(project => {
    if (!record(project) || Object.keys(project).length !== 2 || typeof project.project_id !== 'string'
      || !/^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i.test(project.project_id)
      || typeof project.snapshot !== 'string' || !/^[A-Za-z0-9_-]{1,1024}$/.test(project.snapshot)) return fail()
    return { project_id: project.project_id, snapshot: project.snapshot }
  })
  if (new Set(projects.map(project => project.project_id.toLowerCase())).size !== projects.length) return fail()
  const params = assessmentFilterParams(context.filters)
  const filters: Record<string, string | string[]> = {}
  for (const key of multi) if (params.has(key)) filters[key] = params.getAll(key)
  for (const key of singles) if (params.has(key)) filters[key] = params.get(key)!
  const body = JSON.stringify({ projects, filters, view: { test_code: view.test_code, ...(view.platform ? { platform: view.platform } : {}) } })
  if (new TextEncoder().encode(body).length > 65_536) return fail()
  return request('/api/v1/assessments/export', { method: 'POST',
    headers: { Accept: 'text/csv', 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body }, async response => {
    if (response.status !== 200 || !/^text\/csv(?:\s*;\s*charset=utf-8)?$/i.test(response.headers.get('Content-Type') ?? '')
      || response.headers.get('Content-Disposition') !== `attachment; filename="${view.test_code}_avaliacoes.csv"`) throw new ApiError('invalid_response', response.status)
    const blob = await response.blob()
    if (!blob.size) throw new ApiError('invalid_response', response.status)
    return { filename: `${view.test_code}_avaliacoes.csv`, blob }
  }, signal)
}
