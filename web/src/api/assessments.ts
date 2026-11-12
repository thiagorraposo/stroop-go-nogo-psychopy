/** Consulta profissional fechada; somente rotas relativas e dados pseudonimizados. */
import { ApiError, record, request } from './client';
import type { ApiPath } from './client';

export type Project = { id: string; code: string; name: string; active: boolean; created_at: string };
export type Page<T> = { items: T[]; next_cursor: string | null; snapshot?: string };
export type StroopSummary = { accuracy: number | null; response_time_seconds: number | null;
  accuracy_go_trials: number | null; accuracy_no_go_trials: number | null; total_go_trials: number; total_no_go_trials: number;
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
export type AssessmentFacetOptions = { start_date?: string; end_date?: string; test_code?: string; signal?: AbortSignal };
export type AssessmentOptions = PageOptions & Omit<AssessmentFacetOptions, 'test_code'> & {
  condition?: readonly ('congruent' | 'incongruent')[];
  response_type?: readonly ('hit' | 'omission' | 'commission' | 'correct_rejection')[];
  test_code?: string | readonly string[];
  participant_id?: string | readonly string[]; visit?: string | readonly string[];
  evaluator_id?: readonly string[]; test_version?: readonly string[]; platform?: readonly ('web' | 'psychopy')[];
};
export type AssessmentFacets = { participant_id: string[]; visit: string[]; evaluator_id: string[];
  test_version: string[]; platform: ('web' | 'psychopy')[]; test_code: string[] };

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
/** Confere a projecao recebida; nao calcula metricas para apresentar resultados. */
function consistentPercentage(value: unknown, correct: number, total: number): boolean {
  return total === 0 ? value === null
    : finite(value) && value >= 0 && value <= 100 && Math.abs(value - 100 * correct / total) < 1e-8;
}
function stroopSummary(x: unknown): x is StroopSummary {
  if (!closed(x, 'accuracy accuracy_go_trials accuracy_no_go_trials total_go_trials total_no_go_trials response_time_seconds total_trials hits omission_errors commission_errors correct_rejections')) return false;
  const counts = ['total_trials', 'total_go_trials', 'total_no_go_trials', 'hits', 'omission_errors', 'commission_errors', 'correct_rejections'];
  return counts.every((k) => Number.isSafeInteger(x[k]) && Number(x[k]) >= 0)
    && nullableNumber(x.accuracy) && (x.accuracy === null || x.accuracy >= 0 && x.accuracy <= 100)
    && Number(x.total_go_trials) + Number(x.total_no_go_trials) === x.total_trials
    && Number(x.hits) + Number(x.omission_errors) === x.total_go_trials
    && Number(x.correct_rejections) + Number(x.commission_errors) === x.total_no_go_trials
    && consistentPercentage(x.accuracy_go_trials, Number(x.hits), Number(x.total_go_trials))
    && consistentPercentage(x.accuracy_no_go_trials, Number(x.correct_rejections), Number(x.total_no_go_trials))
    && nullableNumber(x.response_time_seconds) && (x.response_time_seconds === null || x.response_time_seconds > 0)
    && Number(x.total_trials) > 0
    && Number(x.hits) + Number(x.omission_errors) + Number(x.commission_errors) + Number(x.correct_rejections) === x.total_trials
    && (Number(x.hits) > 0 ? x.response_time_seconds !== null : x.response_time_seconds === null)
    && x.accuracy !== null
    && Math.abs(x.accuracy - 100 * (Number(x.hits) + Number(x.correct_rejections)) / Number(x.total_trials)) < 1e-8;
}
const baseKeys = 'assessment_id participant_id visit evaluator_id created_at started_at platform test_code test_version protocol_id app_version summary';
function validity(x: unknown): unknown {
  if (!record(x) || !Object.hasOwn(x, 'valid_for_result')) return x;
  if (x.valid_for_result === false) throw new ApiError('state_conflict', 409);
  if (x.valid_for_result !== true || x.invalidation_reason !== null) return invalid();
  const { valid_for_result: _validity, invalidation_reason: _reason, ...body } = x;
  return body;
}
function assessment(x: unknown, detail = false): Assessment {
  x = validity(x);
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
  x = validity(x);
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
async function json<T>(url: ApiPath, decode: (x: unknown, response: Response) => T, signal?: AbortSignal): Promise<T> {
  return request(url, { method: 'GET', headers: { Accept: 'application/json' } }, async (response) => {
    if (response.status !== 200) throw new ApiError('invalid_response', response.status);
    let value: unknown;
    try { value = await response.json(); } catch { return invalid(); }
    return decode(value, response);
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
const filterPatterns = {
  condition: /^(?:congruent|incongruent)$/,
  response_type: /^(?:hit|omission|commission|correct_rejection)$/,
  test_code: labelPattern,
  participant_id: /^[^\x00-\x1f\x7f]{1,512}$/, visit: /^[^\x00-\x1f\x7f]{1,512}$/,  evaluator_id: /^[A-Za-z0-9_-]{1,512}$/,
  test_version: /^[A-Za-z0-9_.+-]{1,64}$/, platform: /^(?:web|psychopy)$/,
};
function civilDate(value: unknown): value is string {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)
    && Number.isFinite(Date.parse(`${value}T00:00:00Z`))
    && new Date(`${value}T00:00:00Z`).toISOString().slice(0, 10) === value;
}
function contextQuery(options: Omit<AssessmentFacetOptions, 'test_code'>, params = new URLSearchParams()): URLSearchParams {
  for (const key of ['start_date', 'end_date'] as const) if (options[key] !== undefined) {
    input(civilDate(options[key])); params.set(key, options[key]);
  }
  input(!options.start_date || !options.end_date || options.start_date <= options.end_date);
  return params;
}
export function assessmentFilterParams(options: AssessmentOptions = {}): URLSearchParams {
  const params = contextQuery(options, query(options));
  for (const key of Object.keys(filterPatterns) as (keyof typeof filterPatterns)[]) {
    const value = options[key];
    if (value === undefined) continue;
    const values = typeof value === 'string' ? [value] : value;
    input(Array.isArray(values) && values.length <= 100
      && values.every(item => typeof item === 'string' && filterPatterns[key].test(item)
        && (!(key === 'participant_id' || key === 'visit') || item.trim().length > 0))
      && new Set(values).size === values.length);
    for (const item of values) params.append(key, item);
  }
  return params;
}
export function listAssessments(projectId: string, options: AssessmentOptions = {}): Promise<Page<Assessment>> {
  const params = assessmentFilterParams(options);
  return json(path(assessmentPath(projectId), params), (x, response) => {
    const result = page(x, (item) => assessment(item));
    const snapshot = response.headers.get('X-Assessment-Snapshot');
    if (snapshot === null) return result;
    if (!/^[A-Za-z0-9_-]{1,1024}$/.test(snapshot)) return invalid();
    return { ...result, snapshot };
  }, options.signal);
}
export function getAssessmentOptions(projectId: string, options: AssessmentFacetOptions = {}): Promise<AssessmentFacets> {
  const params = contextQuery(options);
  if (options.test_code !== undefined) { input(labelPattern.test(options.test_code)); params.set('test_code', options.test_code); }
  return json(path(`${assessmentPath(projectId)}/options`, params), x => {
    if (!closed(x, 'participant_id visit evaluator_id test_version platform test_code')) return invalid();
    for (const key of ['participant_id', 'visit', 'evaluator_id', 'test_version', 'platform', 'test_code'] as const) {
      const values = x[key];
      const pattern = key === 'test_code' ? labelPattern : filterPatterns[key];
      if (!Array.isArray(values) || values.length > 200
        || !values.every(value => typeof value === 'string' && pattern.test(value)
          && (!(key === 'participant_id' || key === 'visit') || value.trim().length > 0))
        || new Set(values).size !== values.length) return invalid();
    }
    return x as AssessmentFacets;
  }, options.signal);
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

export type RelinkAssessmentInput = {
  patient_id?: string;
  evaluator_id?: string;
  reason_code: string;
};

export type RelinkAssessmentResponse = {
  assessment_id: string;
  project_id: string;
  patient_id: string | null;
  evaluator_id: string | null;
  relinked: boolean;
};

export function relinkAssessment(
  projectId: string,
  assessmentId: string,
  input: RelinkAssessmentInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<RelinkAssessmentResponse> {
  const reason = input.reason_code.trim();
  if (!reason || reason.length > 120) throw new ApiError('invalid_request', 422);
  const payload: Record<string, unknown> = { reason_code: reason };
  if (input.patient_id) {
    if (!uuidPattern.test(input.patient_id)) throw new ApiError('invalid_request', 422);
    payload.patient_id = input.patient_id;
  }
  if (input.evaluator_id) {
    if (!uuidPattern.test(input.evaluator_id)) throw new ApiError('invalid_request', 422);
    payload.evaluator_id = input.evaluator_id;
  }
  return request(
    `${assessmentPath(projectId, assessmentId)}/relink` as ApiPath,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-Token': csrfToken,
      },
      body: JSON.stringify(payload),
    },
    async response => {
      if (response.status !== 200) throw new ApiError('invalid_response', response.status);
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new ApiError('invalid_response', response.status);
      }
      if (!record(body) || typeof body.assessment_id !== 'string') {
        throw new ApiError('invalid_response', response.status);
      }
      return {
        assessment_id: String(body.assessment_id),
        project_id: String(body.project_id),
        patient_id: typeof body.patient_id === 'string' ? body.patient_id : null,
        evaluator_id: typeof body.evaluator_id === 'string' ? body.evaluator_id : null,
        relinked: Boolean(body.relinked),
      };
    },
    signal,
  );
}
