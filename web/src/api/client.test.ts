import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError, apiErrorMessage, getProfessionalProfile, logoutProfessional } from './client';

const profile = {
  user_id: 'c3ludGhldGljLXVzZXI', role: 'consulta',
  expires_at: '2026-10-16T18:02:01.123456Z', csrf_token: 'a'.repeat(43),
} as const;

function json(body: unknown, status = 200, headers: HeadersInit = {}): Response {
  const responseHeaders = new Headers(headers);
  responseHeaders.set('Content-Type', 'application/json');
  return new Response(JSON.stringify(body), {
    status, headers: responseHeaders,
  });
}

let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>;

beforeEach(() => {
  fetchMock = vi.fn<typeof fetch>();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('cliente profissional', () => {
  it('consulta apenas o endpoint relativo fixo com cookie same-origin e sem cache', async () => {
    fetchMock.mockResolvedValue(json(profile));
    await expect(getProfessionalProfile()).resolves.toEqual(profile);
    expect(fetchMock).toHaveBeenCalledExactlyOnceWith('/api/v1/auth/me', {
      method: 'GET', headers: { Accept: 'application/json' },
      credentials: 'same-origin', cache: 'no-store', redirect: 'error',
      signal: expect.any(AbortSignal),
    });
  });

  it.each(['consulta', 'importacao', 'administracao'] as const)('aceita o perfil %s', async (role) => {
    fetchMock.mockResolvedValue(json({ ...profile, role }));
    await expect(getProfessionalProfile()).resolves.toEqual({ ...profile, role });
  });

  it('envia CSRF no header e JSON vazio no logout, aceitando somente 204', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));
    await expect(logoutProfessional(profile.csrf_token)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledExactlyOnceWith('/api/v1/auth/logout', {
      method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json',
        'X-CSRF-Token': profile.csrf_token }, body: '{}',
      credentials: 'same-origin', cache: 'no-store', redirect: 'error',
      signal: expect.any(AbortSignal),
    });
    fetchMock.mockResolvedValue(json({}));
    await expect(logoutProfessional(profile.csrf_token)).rejects.toMatchObject({
      code: 'invalid_response', status: 200,
    });
  });

  it.each([
    null, [], {}, { ...profile, role: 'admin' }, { ...profile, role: ['consulta'] },
    { ...profile, role: true }, { ...profile, user_id: '' }, { ...profile, user_id: 'x'.repeat(513) },
    { ...profile, user_id: '<script>secret</script>' }, { ...profile, csrf_token: null },
    { ...profile, csrf_token: 'too-short' }, { ...profile, csrf_token: 'x'.repeat(44) },
    { ...profile, expires_at: 'not-a-date' }, { ...profile, expires_at: '2026-02-31T18:02:01Z' },
    { ...profile, expires_at: '2026-10-16' }, { ...profile, email: 'synthetic-secret@example.test' },
  ])('rejeita schema de perfil invalido sem refletir dados: %#', async (body) => {
    fetchMock.mockResolvedValue(json(body));
    await expect(getProfessionalProfile()).rejects.toMatchObject({ code: 'invalid_response', status: 200 });
  });

  it('rejeita JSON/HTML invalido e status de sucesso inesperado', async () => {
    for (const response of [new Response('<html>SYNTHETIC_SECRET</html>'),
      json(profile, 201), new Response(null, { status: 204 })]) {
      fetchMock.mockResolvedValue(response);
      const error = await getProfessionalProfile().catch((value: unknown) => value);
      expect(error).toBeInstanceOf(ApiError);
      expect(error).toMatchObject({ code: 'invalid_response' });
      expect(String(error)).not.toContain('SYNTHETIC_SECRET');
    }
  });

  it.each([
    [401, 'authentication_required'], [403, 'account_blocked'],
    [403, 'csrf_failed'], [503, 'service_unavailable'],
  ] as const)('mapeia erro HTTP %s pelo catalogo fechado', async (status, code) => {
    fetchMock.mockResolvedValue(json({ error: { code, message: 'SYNTHETIC_SECRET' }, request_id: 'synthetic' }, status));
    const error = await getProfessionalProfile().catch((value: unknown) => value);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code, status, retryAfter: null });
    expect(apiErrorMessage(error)).not.toContain('SYNTHETIC_SECRET');
    expect(String(error)).not.toContain('SYNTHETIC_SECRET');
  });

  it('aceita Retry-After numerico em 429 e rejeita headers malformados', async () => {
    for (const [header, expected] of [
      ['60', 60], ['0', 0], ['-1', null], ['1.5', null], ['Infinity', null],
      ['999999999999999999999999', null], ['SYNTHETIC_SECRET', null],
      ['Fri, 16 Oct 2026 18:02:01 GMT', null],
    ] as const) {
      fetchMock.mockResolvedValue(json({ error: { code: 'rate_limited' } }, 429, { 'Retry-After': header }));
      await expect(getProfessionalProfile()).rejects.toMatchObject({ code: 'rate_limited', status: 429, retryAfter: expected });
    }
    fetchMock.mockResolvedValue(json({ error: { code: 'service_unavailable' } }, 503, { 'Retry-After': '60' }));
    await expect(getProfessionalProfile()).rejects.toMatchObject({ retryAfter: null });
  });

  it('ignora codigos desconhecidos e mensagens HTML, inclusive codigo conhecido no status errado', async () => {
    for (const body of [
      { error: { code: 'SYNTHETIC_SECRET', message: '<script>secret</script>' } },
      { error: { code: 'authentication_required', message: 'SYNTHETIC_SECRET' } },
      { error: { code: '__proto__', message: 'SYNTHETIC_SECRET' } },
      { error: null },
    ]) {
      fetchMock.mockResolvedValue(json(body, 503));
      const error = await getProfessionalProfile().catch((value: unknown) => value);
      expect(error).toMatchObject({ code: 'service_unavailable', status: 503 });
      expect(apiErrorMessage(error)).not.toMatch(/SYNTHETIC_SECRET|<script>|secret/);
    }
    fetchMock.mockResolvedValue(new Response('<html>SYNTHETIC_SECRET</html>', { status: 502 }));
    await expect(getProfessionalProfile()).rejects.toMatchObject({ code: 'invalid_response', status: 502 });
  });

  it('converte falha de rede para mensagem segura sem propagar stack ou detalhes', async () => {
    fetchMock.mockRejectedValue(new Error('SYNTHETIC_SECRET <html>upstream</html>'));
    const error = await getProfessionalProfile().catch((value: unknown) => value);
    expect(error).toMatchObject({ code: 'network_error', status: 0 });
    expect(apiErrorMessage(error)).not.toMatch(/SYNTHETIC_SECRET|upstream|<html>/);
    expect(String(error)).not.toContain('SYNTHETIC_SECRET');
  });

  it('encerra em dez segundos mesmo se fetch nao cumprir cancelamento e limpa timer/listener', async () => {
    vi.useFakeTimers();
    const external = new AbortController();
    const remove = vi.spyOn(external.signal, 'removeEventListener');
    fetchMock.mockImplementation(() => new Promise<Response>(() => undefined));
    const pending = getProfessionalProfile(external.signal);
    const rejected = expect(pending).rejects.toMatchObject({ code: 'request_timeout', status: 0 });
    await vi.advanceTimersByTimeAsync(10_000);
    await rejected;
    expect(fetchMock.mock.calls[0]?.[1]?.signal?.aborted).toBe(true);
    expect(remove).toHaveBeenCalledWith('abort', expect.any(Function));
    expect(vi.getTimerCount()).toBe(0);
  });

  it('aplica timeout tambem enquanto le corpo da resposta', async () => {
    vi.useFakeTimers();
    fetchMock.mockResolvedValue({ ok: true, status: 200,
      json: () => new Promise<unknown>(() => undefined) } as Response);
    const pending = getProfessionalProfile();
    const rejected = expect(pending).rejects.toMatchObject({ code: 'request_timeout' });
    await vi.advanceTimersByTimeAsync(10_000);
    await rejected;
    expect(vi.getTimerCount()).toBe(0);
  });

  it('cancela imediatamente, propaga abort ao fetch e remove recursos', async () => {
    vi.useFakeTimers();
    const external = new AbortController();
    const remove = vi.spyOn(external.signal, 'removeEventListener');
    fetchMock.mockImplementation(() => new Promise<Response>(() => undefined));
    const pending = getProfessionalProfile(external.signal);
    const rejected = expect(pending).rejects.toMatchObject({ code: 'request_cancelled', status: 0 });
    external.abort('SYNTHETIC_SECRET');
    await rejected;
    expect(fetchMock.mock.calls[0]?.[1]?.signal?.aborted).toBe(true);
    expect(remove).toHaveBeenCalledWith('abort', expect.any(Function));
    expect(vi.getTimerCount()).toBe(0);
  });

  it('nao inicia fetch quando o sinal ja esta cancelado', async () => {
    const external = new AbortController();
    external.abort();
    await expect(getProfessionalProfile(external.signal)).rejects.toMatchObject({ code: 'request_cancelled' });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('remove timeout e listener depois de sucesso ou erro sem cancelar trabalho concluido', async () => {
    vi.useFakeTimers();
    const external = new AbortController();
    const remove = vi.spyOn(external.signal, 'removeEventListener');
    fetchMock.mockResolvedValueOnce(json(profile)).mockRejectedValueOnce(new Error('synthetic'));
    await getProfessionalProfile(external.signal);
    expect(vi.getTimerCount()).toBe(0);
    await expect(getProfessionalProfile(external.signal)).rejects.toMatchObject({ code: 'network_error' });
    expect(remove).toHaveBeenCalledTimes(2);
    expect(vi.getTimerCount()).toBe(0);
    external.abort();
    expect(fetchMock.mock.calls[0]?.[1]?.signal?.aborted).toBe(false);
  });

  it('mantem mensagens seguras mesmo com erros externos ou ApiError adulterado', () => {
    expect(apiErrorMessage(new Error('SYNTHETIC_SECRET'))).not.toContain('SYNTHETIC_SECRET');
    const error = new ApiError('SYNTHETIC_SECRET', 503);
    expect(error.code).toBe('invalid_response');
    error.message = 'SYNTHETIC_SECRET';
    expect(apiErrorMessage(error)).not.toContain('SYNTHETIC_SECRET');
  });
});
