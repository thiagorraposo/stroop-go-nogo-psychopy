/** Emissao e revogacao profissional; codigos permanecem somente na memoria do consumidor. */
import { ApiError, record, request } from './client';

export type InvitationInput = { participant_id: string; visit: string };
export type CreatedInvitation = {
  invitation_id: string; session_id: string; code: string; expires_at: string; state: 'issued';
};
const uuid = /^[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}$/i;
const label = /^[A-Za-z0-9_.-]{1,64}$/;
function input(valid: boolean): void {
  if (!valid) throw new ApiError('invalid_request', 422);
}
function validId(value: unknown): value is string { return typeof value === 'string' && uuid.test(value); }
function validDate(value: unknown): value is string {
  return typeof value === 'string'
    && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/.test(value)
    && Number.isFinite(Date.parse(value))
    && new Date(value).toISOString().slice(0, 19) === value.slice(0, 19);
}
function headers(csrfToken: string): Record<string, string> {
  input(typeof csrfToken === 'string' && /^[A-Za-z0-9_-]{43}$/.test(csrfToken));
  return { Accept: 'application/json', 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken };
}

export function createInvitation(projectId: string, values: InvitationInput,
  csrfToken: string, signal?: AbortSignal): Promise<CreatedInvitation> {
  input(validId(projectId));
  input(record(values) && Object.keys(values).length === 2
    && typeof values.participant_id === 'string' && typeof values.visit === 'string');
  const participant_id = values.participant_id.trim();
  const visit = values.visit.trim();
  input(label.test(participant_id) && label.test(visit));
  return request(`/api/v1/projects/${projectId}/invitations`, {
    method: 'POST', headers: headers(csrfToken), body: JSON.stringify({ participant_id, visit }),
  }, async response => {
    if (response.status !== 201) throw new ApiError('invalid_response', response.status);
    let body: unknown;
    try { body = await response.json(); }
    catch { throw new ApiError('invalid_response', response.status); }
    if (!record(body) || Object.keys(body).length !== 5
      || !validId(body.invitation_id) || !validId(body.session_id)
      || typeof body.code !== 'string' || !/^[A-Za-z0-9_-]{22,128}$/.test(body.code)
      || !validDate(body.expires_at) || body.state !== 'issued') {
      throw new ApiError('invalid_response', response.status);
    }
    return { invitation_id: body.invitation_id, session_id: body.session_id,
      code: body.code, expires_at: body.expires_at, state: 'issued' };
  }, signal);
}

export function revokeInvitation(projectId: string, invitationId: string,
  csrfToken: string, signal?: AbortSignal): Promise<void> {
  input(validId(projectId) && validId(invitationId));
  return request(`/api/v1/projects/${projectId}/invitations/${invitationId}/revoke`, {
    method: 'POST', headers: headers(csrfToken), body: '{}',
  }, async response => {
    if (response.status !== 204 || await response.text() !== '') {
      throw new ApiError('invalid_response', response.status);
    }
  }, signal);
}
