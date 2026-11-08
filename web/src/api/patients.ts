/** Fronteira HTTP para o cadastro central de pacientes (/api/v1/patients). */
import { ApiError, record, request } from './client';

export type PatientRecord = {
  id: string;
  participant_code: string;
  full_name: string;
  normalized_name?: string;
  initials: string | null;
  disambiguation_note: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
  project_count: number;
  assessment_count: number;
  last_assessment_at: string | null;
};

export type PatientListResponse = {
  items: PatientRecord[];
  total: number;
  page: number;
  page_size: number;
};

export type CreatePatientInput = {
  full_name: string;
  initials?: string | null;
  disambiguation_note?: string | null;
  confirm_homonym?: boolean;
};

export type DuplicatePatientCandidate = {
  id: string;
  participant_code: string;
  full_name: string;
  initials: string | null;
  disambiguation_note: string | null;
  active: boolean;
  created_at: string;
};

export type DuplicatePatientsResponse = {
  normalized_name: string;
  candidates: DuplicatePatientCandidate[];
};

const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i;
const stopWords = new Set(['DA', 'DE', 'DO', 'DAS', 'DOS', 'E']);

function validId(value: unknown): value is string {
  return typeof value === 'string' && uuid.test(value);
}

function headers(csrfToken: string): Record<string, string> {
  if (typeof csrfToken !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(csrfToken)) {
    throw new ApiError('invalid_request', 422);
  }
  return { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken };
}

export function deriveInitials(fullName: string): string {
  const folded = fullName
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
    .trim();
  if (!folded) return '';
  const tokens = folded.split(/\s+/).filter(Boolean);
  const filtered = tokens.filter(token => !stopWords.has(token));
  const chosen = filtered.length > 0 ? filtered : tokens;
  const letters: string[] = [];
  for (const token of chosen) {
    const match = token.match(/[A-Z0-9]/);
    if (match) letters.push(match[0]);
  }
  return letters.join('').slice(0, 16);
}

function decodePatient(raw: unknown, status: number): PatientRecord {
  if (
    !record(raw) ||
    !validId(raw.id) ||
    typeof raw.participant_code !== 'string' ||
    !/^PAT-(?:\d{4,}|\d{8}-\d{6})$/.test(raw.participant_code) ||
    typeof raw.full_name !== 'string' ||
    (raw.initials !== null && typeof raw.initials !== 'string') ||
    (raw.disambiguation_note !== null && typeof raw.disambiguation_note !== 'string') ||
    typeof raw.active !== 'boolean' ||
    typeof raw.created_at !== 'string' ||
    typeof raw.updated_at !== 'string'
  ) {
    throw new ApiError('invalid_response', status);
  }
  return {
    id: raw.id,
    participant_code: raw.participant_code,
    full_name: raw.full_name,
    normalized_name: typeof raw.normalized_name === 'string' ? raw.normalized_name : undefined,
    initials: raw.initials,
    disambiguation_note: raw.disambiguation_note,
    active: raw.active,
    created_at: raw.created_at,
    updated_at: raw.updated_at,
    project_count:
      typeof raw.project_count === 'number'
        ? raw.project_count
        : Array.isArray(raw.project_codes)
          ? raw.project_codes.length
          : 0,
    assessment_count: typeof raw.assessment_count === 'number' ? raw.assessment_count : 0,
    last_assessment_at:
      typeof raw.last_assessment_at === 'string'
        ? raw.last_assessment_at
        : typeof raw.last_visit_at === 'string'
          ? raw.last_visit_at
          : null,
  };
}

export function listPatients(
  options: { search?: string; active?: 'true' | 'false' | 'all'; page?: number; page_size?: number } = {},
  signal?: AbortSignal,
): Promise<PatientListResponse> {
  const params = new URLSearchParams();
  if (options.search && options.search.trim()) params.set('search', options.search.trim());
  if (options.active) params.set('active', options.active);
  if (options.page !== undefined) params.set('page', String(options.page));
  if (options.page_size !== undefined) params.set('page_size', String(options.page_size));
  const query = params.toString();
  const path = query ? (`/api/v1/patients?${query}` as const) : ('/api/v1/patients' as const);
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
        items: body.items.map(item => decodePatient(item, response.status)),
        total: body.total,
        page: body.page,
        page_size: body.page_size,
      };
    },
    signal,
  );
}

export function checkDuplicatePatients(
  fullName: string,
  signal?: AbortSignal,
): Promise<DuplicatePatientsResponse> {
  const trimmed = fullName.trim();
  if (trimmed.length < 2 || trimmed.length > 120) {
    throw new ApiError('invalid_request', 422);
  }
  const params = new URLSearchParams({ full_name: trimmed });
  return request(
    `/api/v1/patients/duplicates?${params.toString()}`,
    { method: 'GET', headers: { Accept: 'application/json' } },
    async response => {
      if (response.status !== 200) throw new ApiError('invalid_response', response.status);
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new ApiError('invalid_response', response.status);
      }
      if (!record(body) || typeof body.normalized_name !== 'string' || !Array.isArray(body.candidates)) {
        throw new ApiError('invalid_response', response.status);
      }
      const candidates: DuplicatePatientCandidate[] = body.candidates.map(item => {
        if (
          !record(item) ||
          !validId(item.id) ||
          typeof item.participant_code !== 'string' ||
          typeof item.full_name !== 'string' ||
          typeof item.active !== 'boolean' ||
          typeof item.created_at !== 'string'
        ) {
          throw new ApiError('invalid_response', response.status);
        }
        return {
          id: item.id,
          participant_code: item.participant_code,
          full_name: item.full_name,
          initials: typeof item.initials === 'string' ? item.initials : null,
          disambiguation_note: typeof item.disambiguation_note === 'string' ? item.disambiguation_note : null,
          active: item.active,
          created_at: item.created_at,
        };
      });
      return { normalized_name: body.normalized_name, candidates };
    },
    signal,
  );
}

export function createPatient(
  input: CreatePatientInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<PatientRecord> {
  const fullName = input.full_name.trim().replace(/\s+/g, ' ');
  if (fullName.length < 2 || fullName.length > 120) {
    throw new ApiError('invalid_request', 422);
  }
  const initials = input.initials ? input.initials.trim().toUpperCase() : null;
  if (initials !== null && initials.length > 16) {
    throw new ApiError('invalid_request', 422);
  }
  const note = input.disambiguation_note ? input.disambiguation_note.trim() : null;
  if (note !== null && note.length > 160) {
    throw new ApiError('invalid_request', 422);
  }
  return request(
    '/api/v1/patients',
    {
      method: 'POST',
      headers: headers(csrfToken),
      body: JSON.stringify({
        full_name: fullName,
        initials: initials || null,
        disambiguation_note: note || null,
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
      return decodePatient(body, response.status);
    },
    signal,
  );
}

export type PatientProjectLink = {
  project_id: string;
  project_code: string;
  project_name: string;
  participant_uuid?: string;
  participant_code?: string;
  created_at?: string;
};

export type PatientVisitLink = {
  visit_uuid: string;
  project_id: string;
  project_code: string;
  visit: string;
  created_at: string;
};

export type PatientAssessmentLink = {
  assessment_id: string;
  project_id: string;
  project_code: string;
  test_code: string;
  test_version: string;
  visit: string;
  created_at: string;
};

export type PatientSessionLink = {
  invitation_id: string;
  session_id: string;
  project_id: string;
  project_code: string;
  visit: string;
  evaluator_code?: string;
  evaluator_id?: string | null;
  test_code: string;
  test_version: string;
  invitation_state: string;
  session_state?: string | null;
  created_at: string;
  expires_at?: string | null;
  redeemed_at?: string | null;
  revoked_at?: string | null;
};

export type RegistryAuditEvent = {
  event_id: string;
  entity_type: string;
  action: string;
  reason_code: string;
  occurred_at: string;
};

export type PatientDetail = PatientRecord & {
  projects: PatientProjectLink[];
  visits: PatientVisitLink[];
  assessments: PatientAssessmentLink[];
  sessions: PatientSessionLink[];
  audit_history: RegistryAuditEvent[];
};

export type UpdatePatientInput = {
  full_name?: string;
  initials?: string | null;
  disambiguation_note?: string | null;
  active?: boolean;
  reason_code: string;
};

export function getPatient(
  patientId: string,
  signal?: AbortSignal,
): Promise<PatientDetail> {
  if (!validId(patientId)) {
    throw new ApiError('invalid_request', 422);
  }
  return request(
    `/api/v1/patients/${patientId}`,
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
      const base = decodePatient(body, response.status);
      const projects: PatientProjectLink[] = Array.isArray(body.projects)
        ? body.projects.filter(record).map(p => ({
            project_id: String(p.project_id),
            project_code: String(p.project_code),
            project_name: String(p.project_name),
            participant_uuid: typeof p.participant_uuid === 'string' ? p.participant_uuid : undefined,
            participant_code: typeof p.participant_code === 'string' ? p.participant_code : undefined,
            created_at: typeof p.created_at === 'string' ? p.created_at : undefined,
          }))
        : [];
      const visits: PatientVisitLink[] = Array.isArray(body.visits)
        ? body.visits.filter(record).map(v => ({
            visit_uuid: String(v.visit_uuid),
            project_id: String(v.project_id),
            project_code: String(v.project_code),
            visit: String(v.visit),
            created_at: String(v.created_at),
          }))
        : [];
      const assessments: PatientAssessmentLink[] = Array.isArray(body.assessments)
        ? body.assessments.filter(record).map(a => ({
            assessment_id: String(a.assessment_id),
            project_id: String(a.project_id),
            project_code: String(a.project_code),
            test_code: String(a.test_code),
            test_version: String(a.test_version),
            visit: String(a.visit),
            created_at: String(a.created_at ?? a.completed_at ?? ''),
          }))
        : [];
      const sessions: PatientSessionLink[] = Array.isArray(body.sessions)
        ? body.sessions.filter(record).map(s => ({
            invitation_id: String(s.invitation_id),
            session_id: String(s.session_id),
            project_id: String(s.project_id),
            project_code: String(s.project_code),
            visit: String(s.visit),
            evaluator_code: typeof s.evaluator_code === 'string' ? s.evaluator_code : undefined,
            evaluator_id: typeof s.evaluator_id === 'string' ? s.evaluator_id : null,
            test_code: String(s.test_code),
            test_version: String(s.test_version),
            invitation_state: String(s.invitation_state),
            session_state: typeof s.session_state === 'string' ? s.session_state : null,
            created_at: String(s.created_at),
            expires_at: typeof s.expires_at === 'string' ? s.expires_at : null,
            redeemed_at: typeof s.redeemed_at === 'string' ? s.redeemed_at : null,
            revoked_at: typeof s.revoked_at === 'string' ? s.revoked_at : null,
          }))
        : [];
      const audit_history: RegistryAuditEvent[] = Array.isArray(body.audit_history)
        ? body.audit_history.filter(record).map(h => ({
            event_id: String(h.event_id),
            entity_type: String(h.entity_type),
            action: String(h.action),
            reason_code: String(h.reason_code),
            occurred_at: String(h.occurred_at),
          }))
        : [];
      return { ...base, projects, visits, assessments, sessions, audit_history };
    },
    signal,
  );
}

export function updatePatient(
  patientId: string,
  input: UpdatePatientInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<PatientRecord> {
  if (!validId(patientId)) {
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
  if (input.disambiguation_note !== undefined) {
    payload.disambiguation_note = input.disambiguation_note ? input.disambiguation_note.trim() : null;
  }
  if (input.active !== undefined) {
    payload.active = Boolean(input.active);
  }
  return request(
    `/api/v1/patients/${patientId}`,
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
      return decodePatient(body, response.status);
    },
    signal,
  );
}
