/** Fronteira HTTP para exportação CSV multi-granularidade (/api/v1/exports). */
import { ApiError, record, request } from './client';
import type { ApiPath } from './client';

export type ExportGranularity =
  | 'pacientes'
  | 'avaliacoes'
  | 'tentativas'
  | 'metricas'
  | 'stroop_21_colunas';

export type IdentificationMode = 'deidentified' | 'nominal';

export type ExportPreviewInput = {
  project_id: string;
  granularity: ExportGranularity;
  columns?: string[];
  identification_mode?: IdentificationMode;
  filters?: Record<string, unknown>;
};

export type ExportPreviewResponse = {
  total_rows: number;
  columns: string[];
  applied_criteria: {
    project_id: string;
    granularity: ExportGranularity;
    identification_mode: IdentificationMode;
  };
  sample_rows: Record<string, unknown>[];
  export_token: string;
};

export type ExportDownloadInput = {
  project_id: string;
  granularity: ExportGranularity;
  columns?: string[];
  identification_mode?: IdentificationMode;
  export_token: string;
  filters?: Record<string, unknown>;
};

const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i;

function headers(csrfToken: string): Record<string, string> {
  if (typeof csrfToken !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(csrfToken)) {
    throw new ApiError('invalid_request', 422);
  }
  return {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken,
  };
}

export function previewExport(
  input: ExportPreviewInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<ExportPreviewResponse> {
  if (!uuid.test(input.project_id)) {
    throw new ApiError('invalid_request', 422);
  }
  return request(
    '/api/v1/exports/preview' as ApiPath,
    {
      method: 'POST',
      headers: headers(csrfToken),
      body: JSON.stringify({
        project_id: input.project_id,
        granularity: input.granularity,
        columns: input.columns,
        identification_mode: input.identification_mode ?? 'deidentified',
        filters: input.filters,
      }),
    },
    async response => {
      if (response.status !== 200) {
        throw new ApiError('invalid_response', response.status);
      }
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new ApiError('invalid_response', response.status);
      }
      if (
        !record(body) ||
        typeof body.total_rows !== 'number' ||
        !Array.isArray(body.columns) ||
        !Array.isArray(body.sample_rows) ||
        typeof body.export_token !== 'string'
      ) {
        throw new ApiError('invalid_response', response.status);
      }
      return body as ExportPreviewResponse;
    },
    signal,
  );
}

export function downloadExport(
  input: ExportDownloadInput,
  csrfToken: string,
  signal?: AbortSignal,
): Promise<{ filename: string; blob: Blob }> {
  if (!uuid.test(input.project_id) || !input.export_token) {
    throw new ApiError('invalid_request', 422);
  }
  return request(
    '/api/v1/exports/download' as ApiPath,
    {
      method: 'POST',
      headers: {
        ...headers(csrfToken),
        Accept: 'text/csv',
      },
      body: JSON.stringify({
        project_id: input.project_id,
        granularity: input.granularity,
        columns: input.columns,
        identification_mode: input.identification_mode ?? 'deidentified',
        export_token: input.export_token,
        filters: input.filters,
      }),
    },
    async response => {
      if (response.status !== 200) {
        throw new ApiError('invalid_response', response.status);
      }
      const cd = response.headers.get('Content-Disposition') ?? '';
      const match = /filename="([^"]+)"/.exec(cd);
      const filename = match?.[1] ?? `${input.granularity}.csv`;
      const blob = await response.blob();
      return { filename, blob };
    },
    signal,
  );
}
