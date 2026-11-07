import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import { createInvitation, revokeInvitation } from './sessions';

const projectId = '00000000-0000-4000-8000-000000000001';
const csrf = 'c'.repeat(43);
const values = { participant_id: 'P_SINTETICO', visit: 'V_SINTETICA' };
const invitation = { invitation_id: '00000000-0000-4000-8000-000000000010',
  session_id: '00000000-0000-4000-8000-000000000020', code: 'SINTETICO_NAO_UTILIZAVEL_123456789',
  expires_at: '2026-10-17T13:00:00Z', state: 'issued' };
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>;
const json = (body: unknown, status = 201) => new Response(JSON.stringify(body), { status });
beforeEach(() => { fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

test('cria com dados normalizados, CSRF e transporte seguro; codigo apenas no corpo', async () => {
  fetchMock.mockResolvedValue(json(invitation));
  await expect(createInvitation(projectId, { participant_id: ' P_SINTETICO ', visit: ' V_SINTETICA ' }, csrf))
    .resolves.toEqual(invitation);
  expect(fetchMock).toHaveBeenCalledExactlyOnceWith(`/api/v1/projects/${projectId}/invitations`,
    expect.objectContaining({ method: 'POST', body: JSON.stringify(values),
      credentials: 'same-origin', cache: 'no-store', redirect: 'error',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': csrf } }));
});

test('valida ids, campos, limites e CSRF antes da rede', () => {
  for (const invoke of [
    () => createInvitation('../x', values, csrf),
    () => createInvitation(projectId, { ...values, participant_id: '' }, csrf),
    () => createInvitation(projectId, { ...values, visit: 'pessoa sintética' }, csrf),
    () => createInvitation(projectId, { ...values, visit: 'V'.repeat(65) }, csrf),
    () => createInvitation(projectId, { ...values, participant_name: 'SINTETICO' } as typeof values, csrf),
    () => createInvitation(projectId, values, 'csrf-invalido'),
    () => revokeInvitation(projectId, '../x', csrf),
  ]) expect(invoke).toThrowError(expect.objectContaining({ code: 'invalid_request' }));
  expect(fetchMock).not.toHaveBeenCalled();
});

test.each([
  { ...invitation, invitation_id: 'invalido' }, { ...invitation, session_id: null },
  { ...invitation, code: 'curto' }, { ...invitation, code: 'https://externo.invalid/segredo' },
  { ...invitation, expires_at: '2026-02-30T13:00:00Z' },
  { ...invitation, expires_at: '2026-10-17T13:00:00' },
  { ...invitation, state: 'redeemed' }, { ...invitation, participant_name: 'SINTETICO' },
  { invitation_id: invitation.invitation_id }, null,
])('recusa resposta de criacao fora do contrato %#', async body => {
  fetchMock.mockResolvedValue(json(body));
  await expect(createInvitation(projectId, values, csrf)).rejects.toMatchObject({ code: 'invalid_response' });
});

test('recusa JSON malformado e status de sucesso inesperado', async () => {
  for (const response of [new Response('{', { status: 201 }), json(invitation, 200), new Response(null, { status: 204 })]) {
    fetchMock.mockResolvedValue(response);
    await expect(createInvitation(projectId, values, csrf)).rejects.toMatchObject({ code: 'invalid_response' });
  }
});

test('revoga somente com confirmacao 204 e corpo vazio', async () => {
  fetchMock.mockResolvedValue(new Response(null, { status: 204 }));
  await expect(revokeInvitation(projectId, invitation.invitation_id, csrf)).resolves.toBeUndefined();
  expect(fetchMock).toHaveBeenCalledExactlyOnceWith(
    `/api/v1/projects/${projectId}/invitations/${invitation.invitation_id}/revoke`,
    expect.objectContaining({ method: 'POST', body: '{}', headers: expect.objectContaining({ 'X-CSRF-Token': csrf }) }));
  fetchMock.mockResolvedValue(json({}, 200));
  await expect(revokeInvitation(projectId, invitation.invitation_id, csrf)).rejects.toMatchObject({ code: 'invalid_response' });
});

test.each([401, 403, 404, 409, 410, 429, 503])('preserva erro publico %i sem repetir POST', async status => {
  fetchMock.mockResolvedValue(new Response('texto privado', { status }));
  await expect(createInvitation(projectId, values, csrf)).rejects.toMatchObject({ status });
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

test('falha de rede e timeout nao repetem criacao', async () => {
  fetchMock.mockRejectedValue(new Error('privado'));
  await expect(createInvitation(projectId, values, csrf)).rejects.toMatchObject({ code: 'network_error' });
  expect(fetchMock).toHaveBeenCalledTimes(1);
  fetchMock.mockClear(); vi.useFakeTimers();
  fetchMock.mockImplementation(() => new Promise(() => undefined));
  const pending = createInvitation(projectId, values, csrf);
  const assertion = expect(pending).rejects.toMatchObject({ code: 'request_timeout' });
  await vi.advanceTimersByTimeAsync(10_000); await assertion;
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

test('cancelamento antes e durante escrita nao declara sucesso nem repete', async () => {
  const already = new AbortController(); already.abort();
  await expect(createInvitation(projectId, values, csrf, already.signal)).rejects.toMatchObject({ code: 'request_cancelled' });
  expect(fetchMock).not.toHaveBeenCalled();
  const controller = new AbortController();
  let resolve: (response: Response) => void = () => undefined;
  fetchMock.mockImplementation(() => new Promise<Response>(done => { resolve = done; }));
  const pending = revokeInvitation(projectId, invitation.invitation_id, csrf, controller.signal);
  controller.abort();
  await expect(pending).rejects.toMatchObject({ code: 'request_cancelled' });
  resolve(new Response(null, { status: 204 }));
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

test('cria convite cadastral com patient_id, evaluator_id, test_code, iniciais e resumo para conferencia', async () => {
  const patientId = '00000000-0000-4000-8000-000000000101';
  const evaluatorId = '00000000-0000-4000-8000-000000000202';
  const summary = {
    project_id: projectId,
    project_code: 'PROJETO_SINTETICO',
    project_name: 'Projeto sintetico',
    patient_id: patientId,
    participant_code: 'PAT-0001',
    participant_name: 'Paciente Sintetico',
    initials: 'P.S.',
    evaluator_id: evaluatorId,
    evaluator_code: 'EVA-0001',
    evaluator_name: 'Avaliador Sintetico',
    test_code: 'stroop_go_nogo_ptbr',
    test_version: '0.2.2-web.1',
    protocol_id: 'stroop_go_nogo_ptbr/0.2.2-web.1',
    visit: 'T1',
  };
  fetchMock.mockResolvedValue(json({ ...invitation, summary }));
  await expect(
    createInvitation(
      projectId,
      {
        patient_id: patientId,
        evaluator_id: evaluatorId,
        visit: ' T1 ',
        test_code: 'stroop_go_nogo_ptbr',
        initials: ' p.s. ',
      },
      csrf,
    ),
  ).resolves.toEqual({ ...invitation, summary });
  expect(fetchMock).toHaveBeenCalledExactlyOnceWith(
    `/api/v1/projects/${projectId}/invitations`,
    expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({
        patient_id: patientId,
        evaluator_id: evaluatorId,
        visit: 'T1',
        test_code: 'stroop_go_nogo_ptbr',
        initials: 'P.S.',
      }),
    }),
  );
});
