/** Fronteira HTTP para o cadastro central de avaliadores (/api/v1/evaluators). */
import { ApiError, record, request } from './client';

export type EvaluatorRecord = {
  id: string;
  evaluator_code: string;
  full_name: string;
  normalized_name?: string;
  initials: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
  assessment_count: number;
  last_assessment_at: string | null;
};

export type EvaluatorListResponse = {
  items: EvaluatorRecord[];
  total: number;
  page: number;
  page_size: number;
};

export type CreateEvaluatorInput = {
  full_name: string;
  initials?: string | null;
  confirm_homonym?: boolean;
};

const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i;

function validId(value: unknown): value is string {
  return typeof value === 'string' && uuid.test(value);
}

function headers(csrfToken: string): Record<string, string> {
  if (typeof csrfToken !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(csrfToken)) {
    throw new ApiError('invalid_request', 422);
  }
  return { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken };
}

function decodeEvaluator(raw: unknown, status: number): EvaluatorRecord {
  if (
    !record(raw) ||
    !validId(raw.id) ||
    typeof raw.evaluator_code !== 'string' ||
    !/^EVA-(?:\d{4,}|\d{8}-\d{6})$/.test(raw.evaluator_code) ||
    typeof raw.full_name !== 'string' ||
    (raw.initials !== null && typeof raw.initials !== 'string') ||
    typeof raw.active !== 'boolean' ||
    typeof raw.created_at !== 'string' ||
    typeof raw.updated_at !== 'string'
  ) {
    throw new ApiError('invalid_response', status);
  }
  return {
    id: raw.id,
    evaluator_code: raw.evaluator_code,
    full_name: raw.full_name,
    normalized_name: typeof raw.normalized_name === 'string' ? raw.normalized_name : undefined,
    initials: raw.initials,
    active: raw.active,
    created_at: raw.created_at,
    updated_at: raw.updated_at,
    assessment_count: typeof raw.assessment_count === 'number' ? raw.assessment_count : 0,
    last_assessment_at: typeof raw.last_assessment_at === 'string' ? raw.last_assessment_at : null,
  };
}

export function listEvaluators(
  options: { search?: string; active?: 'true' | 'false' | 'all'; page?: number; page_size?: number } = {},
  signal?: AbortSignal,
): Promise<EvaluatorListResponse> {
  const params = new URLSearchParams();
  if (options.search && options.search.trim()) params.set('search', options.search.trim());
  if (options.active) params.set('active', options.active);
  if (options.page !== undefined) params.set('page', String(options.page));
  if (options.page_size !== undefined) params.set('page_size', String(options.page_size));
  const query = params.toString();
  const path = query ? (`/api/v1/evaluators?${query}` as const) : ('/api/v1/evaluators' as const);
  return request(
    path,
    { method: 'GET', headers: { Accept: 'application/json' } },
    async response => {
      if (response.status !== 200) throw new ApiError('invalid_response', response.status);
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new ApiError('invalid_response', response.status);
      }
      if (
        !record(body) ||
        !Array.isArray(body.items) ||
        typeof body.total !== 'number' ||
        typeof body.page !== 'number' ||
        typeof body.page_size !== 'number'
      ) {
        throw new ApiError('invalid_response', response.status);
      }
      return {
        items: body.items.map(item => decodeEvaluator(item, response.status)),
        total: body.total,
        page: body.page,
        page_size: body.page_size,
      };
    },
    signal,
  );
}

export function createEvaluator(
  input: CreateEvaluatorInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<EvaluatorRecord> {
  const fullName = input.full_name.trim().replace(/\s+/g, ' ');
  if (fullName.length < 2 || fullName.length > 120) {
    throw new ApiError('invalid_request', 422);
  }
  const initials = input.initials ? input.initials.trim().toUpperCase() : null;
  if (initials !== null && initials.length > 16) {
    throw new ApiError('invalid_request', 422);
  }
  return request(
    '/api/v1/evaluators',
    {
      method: 'POST',
      headers: headers(csrfToken),
      body: JSON.stringify({
        full_name: fullName,
        initials: initials || null,
        confirm_homonym: Boolean(input.confirm_homonym),
      }),
    },
    async response => {
      if (response.status !== 201) throw new ApiError('invalid_response', response.status);
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new ApiError('invalid_response', response.status);
      }
      return decodeEvaluator(body, response.status);
    },
    signal,
  );
}

export type EvaluatorAssessmentLink = {
  assessment_id: string;
  project_id: string;
  project_code: string;
  test_code: string;
  test_version: string;
  visit: string;
  created_at: string;
};

export type EvaluatorDetail = EvaluatorRecord & {
  assessments: EvaluatorAssessmentLink[];
};

export type UpdateEvaluatorInput = {
  full_name?: string;
  initials?: string | null;
  active?: boolean;
  reason_code: string;
};

export function getEvaluator(
  evaluatorId: string,
  signal?: AbortSignal,
): Promise<EvaluatorDetail> {
  if (!validId(evaluatorId)) {
    throw new ApiError('invalid_request', 422);
  }
  return request(
    `/api/v1/evaluators/${evaluatorId}`,
    { method: 'GET', headers: { Accept: 'application/json' } },
    async response => {
      if (response.status !== 200) throw new ApiError('invalid_response', response.status);
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new ApiError('invalid_response', response.status);
      }
      if (!record(body)) throw new ApiError('invalid_response', response.status);
      const base = decodeEvaluator(body, response.status);
      const assessments: EvaluatorAssessmentLink[] = Array.isArray(body.assessments)
        ? body.assessments.filter(record).map(a => ({
            assessment_id: String(a.assessment_id),
            project_id: String(a.project_id),
            project_code: String(a.project_code),
            test_code: String(a.test_code),
            test_version: String(a.test_version),
            visit: String(a.visit),
            created_at: String(a.created_at),
          }))
        : [];
      return { ...base, assessments };
    },
    signal,
  );
}

export function updateEvaluator(
  evaluatorId: string,
  input: UpdateEvaluatorInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<EvaluatorRecord> {
  if (!validId(evaluatorId)) {
    throw new ApiError('invalid_request', 422);
  }
  const payload: Record<string, unknown> = {
    reason_code: input.reason_code.trim() || 'correcao_cadastral',
  };
  if (input.full_name !== undefined) {
    const trimmed = input.full_name.trim().replace(/\s+/g, ' ');
    if (trimmed.length < 2 || trimmed.length > 120) throw new ApiError('invalid_request', 422);
    payload.full_name = trimmed;
  }
  if (input.initials !== undefined) {
    payload.initials = input.initials ? input.initials.trim().toUpperCase() : null;
  }
  if (input.active !== undefined) {
    payload.active = Boolean(input.active);
  }
  return request(
    `/api/v1/evaluators/${evaluatorId}`,
    {
      method: 'PATCH',
      headers: headers(csrfToken),
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
      return decodeEvaluator(body, response.status);
    },
    signal,
  );
}
