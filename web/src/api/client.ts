/** Fronteira HTTP: cookies HttpOnly, CSRF em RAM e erros publicos fechados. */

export type ProfessionalProfile = {
  user_id: string;
  role: 'consulta' | 'importacao' | 'administracao';
  expires_at: string;
  csrf_token: string;
};

const backendErrors = {
  invalid_json: [400, 'Não foi possível enviar a solicitação.'],
  invalid_oidc_state: [400, 'O acesso expirou. Entre novamente com o Google.'],
  authentication_required: [401, 'Entre com o Google para continuar.'],
  permission_denied: [403, 'Seu perfil não permite esta operação.'],
  account_blocked: [403, 'Sua conta está bloqueada. Contate o responsável pela pesquisa.'],
  csrf_failed: [403, 'A verificação de segurança falhou. Atualize a página e tente novamente.'],
  not_found: [404, 'O recurso solicitado não está disponível.'],
  method_not_allowed: [405, 'Esta operação não está disponível.'],
  state_conflict: [409, 'A operação não pode ser realizada no estado atual.'],
  invitation_used: [409, 'Este convite já foi utilizado.'],
  result_conflict: [409, 'Esta sessão já possui um resultado diferente.'],
  duplicate_project: [409, 'Este projeto já está cadastrado.'],
  invitation_expired: [410, 'Este convite expirou. Solicite um novo convite.'],
  session_expired: [410, 'Sua sessão expirou. Inicie uma nova sessão.'],
  body_too_large: [413, 'A solicitação excede o tamanho permitido.'],
  unsupported_media_type: [415, 'O formato da solicitação não é aceito.'],
  invalid_request: [422, 'Não foi possível validar os dados enviados.'],
  invalid_result: [422, 'O resultado não atende ao protocolo da pesquisa.'],
  rate_limited: [429, 'Muitas solicitações. Aguarde antes de tentar novamente.'],
  internal_error: [500, 'Não foi possível concluir a operação. Tente novamente.'],
  service_unavailable: [503, 'O serviço está temporariamente indisponível. Tente novamente.'],
} as const;

const localErrors = {
  network_error: 'Não foi possível conectar ao serviço. Verifique sua conexão.',
  request_timeout: 'O serviço demorou a responder. Tente novamente.',
  request_cancelled: 'A solicitação foi cancelada.',
  invalid_response: 'O serviço enviou uma resposta inválida. Tente novamente.',
} as const;

const fallbackByStatus: Readonly<Record<number, string>> = {
  400: 'invalid_json', 401: 'authentication_required', 403: 'permission_denied',
  404: 'not_found', 405: 'method_not_allowed', 409: 'state_conflict',
  410: 'session_expired', 413: 'body_too_large', 415: 'unsupported_media_type',
  422: 'invalid_request', 429: 'rate_limited', 500: 'internal_error',
  503: 'service_unavailable',
};

function isBackendCode(code: string): code is keyof typeof backendErrors {
  return Object.hasOwn(backendErrors, code);
}

function safeCode(code: string): string {
  return isBackendCode(code) || Object.hasOwn(localErrors, code) ? code : 'invalid_response';
}

function messageFor(code: string): string {
  if (isBackendCode(code)) return backendErrors[code][1];
  if (Object.hasOwn(localErrors, code)) return localErrors[code as keyof typeof localErrors];
  return localErrors.invalid_response;
}

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly retryAfter: number | null;

  constructor(code: string, status: number, retryAfter: number | null = null) {
    const publicCode = safeCode(code);
    super(messageFor(publicCode));
    this.name = 'ApiError';
    this.code = publicCode;
    this.status = Number.isInteger(status) && status >= 0 && status <= 599 ? status : 0;
    this.retryAfter = retryAfter !== null && Number.isSafeInteger(retryAfter) && retryAfter >= 0
      ? retryAfter : null;
  }
}

/** Nunca usar mensagens de excecoes, HTML ou texto livre fornecidos pelo servidor. */
export function apiErrorMessage(error: unknown): string {
  return error instanceof ApiError ? messageFor(error.code) : localErrors.invalid_response;
}

export function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function retryAfter(response: Response): number | null {
  if (response.status !== 429) return null;
  const value = response.headers.get('Retry-After');
  if (value === null || !/^\d+$/.test(value)) return null;
  const number = Number(value);
  return Number.isSafeInteger(number) && number >= 0 ? number : null;
}

async function responseError(response: Response): Promise<ApiError> {
  let code = fallbackByStatus[response.status] ?? 'invalid_response';
  try {
    const body: unknown = await response.json();
    if (record(body) && record(body.error) && typeof body.error.code === 'string'
      && isBackendCode(body.error.code) && backendErrors[body.error.code][0] === response.status) {
      code = body.error.code;
    }
  } catch {
    // Respostas de proxy ou JSON malformado usam somente o status publico.
  }
  return new ApiError(code, response.status, retryAfter(response));
}

type ApiPath = '/api/v1/auth/me' | '/api/v1/auth/logout' |
  '/api/v1/participant/redeem' | '/api/v1/participant/session' |
  '/api/v1/participant/start' | '/api/v1/participant/complete' | '/api/v1/participant/abort' |
  '/api/v1/participant/logout';

export async function request<T>(path: ApiPath,
  init: RequestInit, decode: (response: Response) => Promise<T>, signal?: AbortSignal): Promise<T> {
  if (signal?.aborted) throw new ApiError('request_cancelled', 0);
  const controller = new AbortController();
  let interrupted: ApiError | undefined;
  let rejectInterrupted: (reason: ApiError) => void = () => undefined;
  const interruption = new Promise<never>((_, reject) => { rejectInterrupted = reject; });
  const cancel = (code: 'request_timeout' | 'request_cancelled') => {
    if (interrupted) return;
    interrupted = new ApiError(code, 0);
    controller.abort();
    rejectInterrupted(interrupted);
  };
  const onAbort = () => cancel('request_cancelled');
  signal?.addEventListener('abort', onAbort, { once: true });
  const timer = globalThis.setTimeout(() => cancel('request_timeout'), 10_000);
  try {
    const operation = (async () => {
      const response = await fetch(path, {
        ...init, credentials: 'same-origin', cache: 'no-store', redirect: 'error',
        signal: controller.signal,
      });
      if (!response.ok) throw await responseError(response);
      return decode(response);
    })();
    return await Promise.race([operation, interruption]);
  } catch (error: unknown) {
    if (interrupted) throw interrupted;
    if (error instanceof ApiError) throw error;
    throw new ApiError('network_error', 0);
  } finally {
    globalThis.clearTimeout(timer);
    signal?.removeEventListener('abort', onAbort);
  }
}

function professionalProfile(body: unknown): ProfessionalProfile {
  if (!record(body) || Object.keys(body).length !== 4
    || typeof body.user_id !== 'string' || !/^[A-Za-z0-9_-]{1,512}$/.test(body.user_id)
    || typeof body.role !== 'string'
    || !['consulta', 'importacao', 'administracao'].includes(body.role)
    || typeof body.expires_at !== 'string'
    || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/.test(body.expires_at)
    || !Number.isFinite(Date.parse(body.expires_at))
    || new Date(body.expires_at).toISOString().slice(0, 19) !== body.expires_at.slice(0, 19)
    || typeof body.csrf_token !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(body.csrf_token)) {
    throw new ApiError('invalid_response', 200);
  }
  return {
    user_id: body.user_id, role: body.role as ProfessionalProfile['role'],
    expires_at: body.expires_at, csrf_token: body.csrf_token,
  };
}

export function getProfessionalProfile(signal?: AbortSignal): Promise<ProfessionalProfile> {
  return request('/api/v1/auth/me', { method: 'GET', headers: { Accept: 'application/json' } },
    async (response) => {
      if (response.status !== 200) throw new ApiError('invalid_response', response.status);
      let body: unknown;
      try { body = await response.json(); }
      catch { throw new ApiError('invalid_response', response.status); }
      return professionalProfile(body);
    }, signal);
}

export function logoutProfessional(csrfToken: string, signal?: AbortSignal): Promise<void> {
  return request('/api/v1/auth/logout', {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken }, body: '{}',
  }, async (response) => {
    if (response.status !== 204) throw new ApiError('invalid_response', response.status);
  }, signal);
}
