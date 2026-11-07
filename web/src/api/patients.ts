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
