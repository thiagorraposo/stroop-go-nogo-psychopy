import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import type { ProfessionalProfile } from '../api/client'
import type { Project } from '../api/assessments'
import { createInvitation, revokeInvitation } from '../api/sessions'
import type { CreatedInvitation } from '../api/sessions'

type Saved = { invitation: CreatedInvitation; participant: string; visit: string }
const labelPattern = /^[A-Za-z0-9_.-]{1,64}$/
const uncertain = (cause: unknown) => !(cause instanceof ApiError) || cause.status === 0 || cause.status >= 500 || cause.code === 'invalid_response'

export function SessionInvitation({ project, profile }: { project: Project; profile: ProfessionalProfile }) {
  const [participant, setParticipant] = useState('')
  const [visit, setVisit] = useState('')
  const [errors, setErrors] = useState({ participant: '', visit: '' })
  const [saved, setSaved] = useState<Saved | null>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [unknownCreation, setUnknownCreation] = useState(false)
  const [revoked, setRevoked] = useState(false)
  const operation = useRef<AbortController | null>(null)
  const panel = useRef<HTMLElement>(null)
  const participantInput = useRef<HTMLInputElement>(null)
  const visitInput = useRef<HTMLInputElement>(null)
  const focusForm = useRef(false)
  useEffect(() => () => operation.current?.abort(), [])
  useEffect(() => {
    if (!saved && !revoked && !unknownCreation && focusForm.current) {
      focusForm.current = false; participantInput.current?.focus()
    }
  }, [saved, revoked, unknownCreation])
  useEffect(() => { if (saved || revoked || unknownCreation) panel.current?.focus() }, [saved, revoked, unknownCreation])

  async function create(event: FormEvent) {
    event.preventDefault()
    if (operation.current || saved || unknownCreation) return
    const p = participant.trim(), v = visit.trim()
    const next = { participant: labelPattern.test(p) ? '' : 'Use de 1 a 64 letras, números, ponto, hífen ou sublinhado.',
      visit: labelPattern.test(v) ? '' : 'Use de 1 a 64 letras, números, ponto, hífen ou sublinhado.' }
    setErrors(next); setMessage(null)
    if (next.participant || next.visit) {
      (next.participant ? participantInput : visitInput).current?.focus(); return
    }
    setParticipant(p); setVisit(v)
    const io = new AbortController(); operation.current = io; setBusy(true)
    try {
      const invitation = await createInvitation(project.id, { participant_id: p, visit: v }, profile.csrf_token, io.signal)
      if (!io.signal.aborted) setSaved({ invitation, participant: p, visit: v })
    } catch (cause) {
      if (!io.signal.aborted) {
        if (uncertain(cause)) { setUnknownCreation(true); setMessage('Não foi possível confirmar a criação. A sessão pode ter sido criada, mas o código não pode ser recuperado. Nenhuma nova emissão será feita automaticamente. Sem identificador confirmado, não é possível revogar este convite por esta tela. Informe o responsável antes de preparar outra sessão.') }
        else setMessage(apiErrorMessage(cause))
      }
    } finally { if (!io.signal.aborted) { operation.current = null; setBusy(false) } }
  }
  async function revoke() {
    if (!saved || operation.current || revoked) return
    const io = new AbortController(); operation.current = io; setBusy(true); setMessage(null)
    try {
      await revokeInvitation(project.id, saved.invitation.invitation_id, profile.csrf_token, io.signal)
      if (!io.signal.aborted) { setRevoked(true); setSaved(null); setParticipant(''); setVisit('') }
    } catch (cause) {
      if (!io.signal.aborted) setMessage(uncertain(cause)
        ? 'A revogação ainda não foi confirmada. Não entregue o código; confirme novamente a revogação.' : apiErrorMessage(cause))
    } finally { if (!io.signal.aborted) { operation.current = null; setBusy(false) } }
  }
  function reset() {
    if (operation.current) return
    focusForm.current = true
    setSaved(null); setRevoked(false); setUnknownCreation(false); setParticipant(''); setVisit(''); setMessage(null); setErrors({ participant: '', visit: '' })
  }
  return <section className="assessment-detail session-invitation" aria-label="Preparar sessão" ref={panel} tabIndex={-1} aria-busy={busy}>
    <h3>Preparar sessão</h3>
    <p>Projeto: {project.code} — {project.name}</p>
    <p>Avaliador responsável: sua conta autenticada ({profile.user_id}). O servidor vincula esta identidade à sessão.</p>
    <p className="quiet">Use somente códigos pseudonimizados. Nesta versão, prepare apenas sessões sintéticas de teste.</p>
    {!saved && !unknownCreation && !revoked && <form onSubmit={event => void create(event)} noValidate className="dashboard-filters">
      <label htmlFor="session-participant">Código do participante<input ref={participantInput} id="session-participant" required maxLength={64} value={participant} disabled={busy} autoComplete="off" aria-invalid={!!errors.participant} aria-describedby={errors.participant ? 'session-participant-error' : undefined} onChange={event => setParticipant(event.target.value)} /></label>
      {errors.participant && <p id="session-participant-error" role="alert">{errors.participant}</p>}
      <label htmlFor="session-visit">Visita da sessão<input ref={visitInput} id="session-visit" required maxLength={64} value={visit} disabled={busy} autoComplete="off" aria-invalid={!!errors.visit} aria-describedby={errors.visit ? 'session-visit-error' : undefined} onChange={event => setVisit(event.target.value)} /></label>
      {errors.visit && <p id="session-visit-error" role="alert">{errors.visit}</p>}
      <button className="button primary" disabled={busy} type="submit">{busy ? 'Gerando convite…' : 'Gerar convite'}</button>
    </form>}
    {saved && <>
      <h4>Convite criado</h4>
      <p>Participante: {saved.participant} · Visita: {saved.visit}</p>
      <p>Sessão: {saved.invitation.session_id}</p>
      <p>Código de uso único: <output aria-label="Código do convite">{saved.invitation.code}</output></p>
      <p>Expira em: {saved.invitation.expires_at} (UTC). Após o prazo, solicite uma nova sessão.</p>
      <p>Entregue o código ao participante por canal apropriado. Ele só aparece agora e será apagado ao trocar de projeto, sair ou recarregar. Abrir a prática exige informar o convite; o código não é incluído no endereço.</p>
      <a className="button secondary" href="/pratica" target="_blank" rel="noopener noreferrer">Abrir prática em outra aba</a>
      <button className="button secondary" disabled={busy} onClick={() => void revoke()}>{busy ? 'Revogando…' : 'Revogar convite'}</button>
    </>}
    {revoked && <p role="status">Revogação confirmada. O convite não permite iniciar ou continuar a sessão.</p>}
    {message && <p role="alert">{message}</p>}
    {(saved || unknownCreation || revoked) && <><p className="quiet">Preparar outra sessão apaga os dados desta tela e cria uma sessão distinta somente após nova confirmação. Não revoga convites anteriores.</p><button className="button secondary" disabled={busy} onClick={reset}>Preparar outra sessão</button></>}
  </section>
}
