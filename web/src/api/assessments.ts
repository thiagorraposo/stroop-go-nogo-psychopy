/** Consulta profissional fechada; somente rotas relativas e dados pseudonimizados. */
import { ApiError, record, request } from './client';
import type { ApiPath } from './client';

export type Project = { id: string; code: string; name: string; active: boolean; created_at: string };
export type Page<T> = { items: T[]; next_cursor: string | null };
export type StroopSummary = { accuracy: number | null; response_time_seconds: number | null;
  total_trials: number; hits: number; omission_errors: number; commission_errors: number;
  correct_rejections: number };
export type Assessment = { assessment_id: string; participant_id: string; visit: string;
  evaluator_id: string | null; created_at: string; started_at: string; platform: 'web' | 'psychopy';
  test_code: string; test_version: string; protocol_id: string | null; app_version: string | null;
  summary: StroopSummary | { metrics: Record<string, number> } };
export type Metric = { metric_code: string; metric_label: string; metric_value: number | null; unit: string };
export type Trial = { trial_number: number; condition_id: number | null; word: string; ink_color: string;
  condition: string; correct_response: string | null; key_pressed: string | null; correct: boolean;
  error_type: string; trial_start_ms: number | null; stimulus_onset_ms: number | null;
  stimulus_offset_ms: number | null; trial_end_ms: number | null; key_at_ms: number | null;
  reaction_time_ms: number | null; reaction_time_seconds: number | null };
export type AssessmentDetail = Assessment & { project_id: string; session_id: string | null;
  completed_at: string | null; metrics: Metric[]; frame_period_ms: number | null; trials: Trial[] };
export type PageOptions = { cursor?: string; limit?: number; signal?: AbortSignal };
export type AssessmentOptions = PageOptions & { participant_id?: string; visit?: string };

const uuidPattern = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i;
const labelPattern = /^[A-Za-z0-9_.-]{1,64}$/;
const idPattern = /^[A-Za-z0-9_.-]{1,128}$/;
const cursorPattern = /^[A-Za-z0-9_-]{1,512}$/;
const finite = (x: unknown): x is number => typeof x === 'number' && Number.isFinite(x);
const nullableNumber = (x: unknown): x is number | null => x === null || finite(x);
const text = (x: unknown): x is string => typeof x === 'string' && x.length <= 512 && !/[\x00-\x1f\x7f]/.test(x);
const nonempty = (x: unknown): x is string => text(x) && x.length > 0;
const nullableText = (x: unknown): x is string | null => x === null || nonempty(x);
function closed(x: unknown, keys: string): x is Record<string, unknown> {
  const expected = keys.split(' ');
  return record(x) && Object.keys(x).length === expected.length && expected.every((k) => Object.hasOwn(x, k));
}
function date(x: unknown): x is string {
  return typeof x === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)?$/.test(x)
    && Number.isFinite(Date.parse(x.endsWith('Z') || x.endsWith('+00:00') ? x : `${x}Z`))
    && new Date(x.endsWith('Z') || x.endsWith('+00:00') ? x : `${x}Z`).toISOString().slice(0, 19) === x.slice(0, 19);
}
function invalid(): never { throw new ApiError('invalid_response', 200); }
function input(valid: boolean): void { if (!valid) throw new ApiError('invalid_request', 422); }
function project(x: unknown): Project {
  if (!closed(x, 'id code name active created_at') || typeof x.id !== 'string' || !uuidPattern.test(x.id)
    || typeof x.code !== 'string' || !labelPattern.test(x.code) || !nonempty(x.name) || x.name.length > 120
    || typeof x.active !== 'boolean' || !date(x.created_at)) return invalid();
  return x as Project;
}
function stroopSummary(x: unknown): x is StroopSummary {
  if (!closed(x, 'accuracy response_time_seconds total_trials hits omission_errors commission_errors correct_rejections')) return false;
  const counts = ['total_trials', 'hits', 'omission_errors', 'commission_errors', 'correct_rejections'];
  return counts.every((k) => Number.isSafeInteger(x[k]) && Number(x[k]) >= 0)
    && nullableNumber(x.accuracy) && (x.accuracy === null || x.accuracy >= 0 && x.accuracy <= 100)
    && nullableNumber(x.response_time_seconds) && (x.response_time_seconds === null || x.response_time_seconds > 0)
    && Number(x.total_trials) > 0
    && Number(x.hits) + Number(x.omission_errors) + Number(x.commission_errors) + Number(x.correct_rejections) === x.total_trials
    && (Number(x.hits) > 0 ? x.response_time_seconds !== null : x.response_time_seconds === null)
    && x.accuracy !== null
    && Math.abs(x.accuracy - 100 * (Number(x.hits) + Number(x.correct_rejections)) / Number(x.total_trials)) < 1e-8;
}
const baseKeys = 'assessment_id participant_id visit evaluator_id created_at started_at platform test_code test_version protocol_id app_version summary';
function assessment(x: unknown, detail = false): Assessment {
  const keys = detail ? `${baseKeys} project_id session_id completed_at metrics frame_period_ms trials` : baseKeys;
  if (!closed(x, keys) || typeof x.assessment_id !== 'string' || !idPattern.test(x.assessment_id)
    || !nonempty(x.participant_id) || !nonempty(x.visit) || !nullableText(x.evaluator_id)
    || !date(x.created_at) || !date(x.started_at) || !['web', 'psychopy'].includes(String(x.platform))
    || !nonempty(x.test_code) || !nonempty(x.test_version) || !nullableText(x.protocol_id) || !nullableText(x.app_version)) return invalid();
  if (x.test_code === 'stroop_go_nogo_ptbr') {
    if (!stroopSummary(x.summary)) return invalid();
  } else if (!closed(x.summary, 'metrics') || !record(x.summary.metrics)
    || !Object.entries(x.summary.metrics).every(([k, v]) => nonempty(k) && finite(v))) return invalid();
  return x as unknown as Assessment;
}
function metric(x: unknown): Metric {
  if (!closed(x, 'metric_code metric_label metric_value unit') || !nonempty(x.metric_code)
    || !nonempty(x.metric_label) || !text(x.unit) || !nullableNumber(x.metric_value)) return invalid();
  return x as Metric;
}
const timingKeys = ['trial_start_ms', 'stimulus_onset_ms', 'stimulus_offset_ms', 'trial_end_ms', 'key_at_ms', 'reaction_time_ms', 'reaction_time_seconds'];
function trial(x: unknown): Trial {
  if (!closed(x, `trial_number condition_id word ink_color condition correct_response key_pressed correct error_type ${timingKeys.join(' ')}`)
    || !Number.isSafeInteger(x.trial_number) || Number(x.trial_number) < 1
    || !(x.condition_id === null || Number.isSafeInteger(x.condition_id) && Number(x.condition_id) >= 1)
    || !nonempty(x.word) || !nonempty(x.ink_color) || !nonempty(x.condition)
    || !(x.correct_response === null || text(x.correct_response)) || !(x.key_pressed === null || text(x.key_pressed))
    || typeof x.correct !== 'boolean' || !text(x.error_type) || !timingKeys.every((k) => nullableNumber(x[k]))) return invalid();
  return x as Trial;
}
function detail(x: unknown, projectId: string, assessmentId: string): AssessmentDetail {
  assessment(x, true);
  if (!record(x) || x.project_id !== projectId || x.assessment_id !== assessmentId
    || !(x.session_id === null || typeof x.session_id === 'string' && uuidPattern.test(x.session_id))
    || !(x.completed_at === null || date(x.completed_at)) || !nullableNumber(x.frame_period_ms)
    || !Array.isArray(x.metrics) || !Array.isArray(x.trials)) return invalid();
  const metrics = x.metrics.map(metric); const trials = x.trials.map(trial);
  if (new Set(metrics.map((m) => m.metric_code)).size !== metrics.length
    || trials.some((t, i) => t.trial_number !== i + 1)) return invalid();
  return { ...x, metrics, trials } as AssessmentDetail;
}
function page<T>(x: unknown, decode: (x: unknown) => T): Page<T> {
  if (!closed(x, 'items next_cursor') || !Array.isArray(x.items) || x.items.length > 100
    || !(x.next_cursor === null || typeof x.next_cursor === 'string' && cursorPattern.test(x.next_cursor))) return invalid();
  return { items: x.items.map(decode), next_cursor: x.next_cursor };
}
function query(options: PageOptions): URLSearchParams {
  const params = new URLSearchParams();
  if (options.limit !== undefined) { input(Number.isInteger(options.limit) && options.limit >= 1 && options.limit <= 100); params.set('limit', String(options.limit)); }
  if (options.cursor !== undefined) { input(cursorPattern.test(options.cursor)); params.set('cursor', options.cursor); }
  return params;
}
function path(base: string, params: URLSearchParams): ApiPath {
  return (base + (params.size ? `?${params}` : '')) as ApiPath;
}
async function json<T>(url: ApiPath, decode: (x: unknown) => T, signal?: AbortSignal): Promise<T> {
  return request(url, { method: 'GET', headers: { Accept: 'application/json' } }, async (response) => {
    if (response.status !== 200) throw new ApiError('invalid_response', response.status);
    let value: unknown;
    try { value = await response.json(); } catch { return invalid(); }
    return decode(value);
  }, signal);
}
function assessmentPath(projectId: string, assessmentId?: string): string {
  input(uuidPattern.test(projectId));
  if (assessmentId !== undefined) input(idPattern.test(assessmentId) && assessmentId !== '.' && assessmentId !== '..');
  return `/api/v1/projects/${projectId}/assessments${assessmentId === undefined ? '' : `/${assessmentId}`}`;
}
export function listProjects(options: PageOptions = {}): Promise<Page<Project>> {
  return json(path('/api/v1/projects', query(options)), (x) => page(x, project), options.signal);
}
export function listAssessments(projectId: string, options: AssessmentOptions = {}): Promise<Page<Assessment>> {
  const params = query(options);
  for (const key of ['participant_id', 'visit'] as const) if (options[key] !== undefined) {
    input(labelPattern.test(options[key])); params.set(key, options[key]);
  }
  return json(path(assessmentPath(projectId), params), (x) => page(x, (item) => assessment(item)), options.signal);
}
export function getAssessment(projectId: string, assessmentId: string, signal?: AbortSignal): Promise<AssessmentDetail> {
  return json(assessmentPath(projectId, assessmentId) as ApiPath, (x) => detail(x, projectId, assessmentId), signal);
}
export function exportAssessment(projectId: string, assessmentId: string, signal?: AbortSignal): Promise<{ filename: string; blob: Blob }> {
  return request(`${assessmentPath(projectId, assessmentId)}/export` as ApiPath,
    { method: 'GET', headers: { Accept: 'text/csv' } }, async (response) => {
      if (response.status !== 200 || !/^text\/csv(?:\s*;\s*charset=utf-8)?$/i.test(response.headers.get('Content-Type') ?? '')) return invalid();
      const match = /^attachment; filename="(stroop_go_nogo_ptbr_\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m\d{2}s_trials\.csv)"$/.exec(response.headers.get('Content-Disposition') ?? '');
      if (!match?.[1]) return invalid();
      const blob = await response.blob();
      if (!blob.size) return invalid();
      return { filename: match[1], blob };
    }, signal);
}
