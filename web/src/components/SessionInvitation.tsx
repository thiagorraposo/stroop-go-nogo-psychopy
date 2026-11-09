import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import type { ProfessionalProfile } from '../api/client'
import type { Project } from '../api/assessments'
import { createEvaluator, listEvaluators } from '../api/evaluators'
import type { EvaluatorRecord } from '../api/evaluators'
import { createPatient, deriveInitials, listPatients } from '../api/patients'
import type { PatientRecord } from '../api/patients'
import { createInvitation, revokeInvitation } from '../api/sessions'
import type { CreatedInvitation, InvitationSummary } from '../api/sessions'

type Saved = {
  invitation: CreatedInvitation
  participant: string
  visit: string
  summary?: InvitationSummary
}

type HomonymCandidate = {
  id: string
  code: string
  full_name: string
  initials: string | null
  disambiguation_note: string | null
}

const labelPattern = /^[A-Za-z0-9_.-]{1,64}$/
const initialsPattern = /^[A-Z0-9.-]{1,16}$/
const uncertain = (cause: unknown) =>
  !(cause instanceof ApiError) ||
  cause.status === 0 ||
  cause.status >= 500 ||
  cause.code === 'invalid_response'

export function SessionInvitation({
  project,
  profile,
}: {
  project: Project
  profile: ProfessionalProfile
}) {
  const [patients, setPatients] = useState<PatientRecord[]>([])
  const [evaluators, setEvaluators] = useState<EvaluatorRecord[]>([])
  const [patientSearch, setPatientSearch] = useState('')
  const [evaluatorSearch, setEvaluatorSearch] = useState('')
  const [selectedPatient, setSelectedPatient] = useState<PatientRecord | null>(null)
  const [selectedEvaluator, setSelectedEvaluator] = useState<EvaluatorRecord | null>(null)

  const [showNewPatient, setShowNewPatient] = useState(false)
  const [newPatientName, setNewPatientName] = useState('')
  const [newPatientInitials, setNewPatientInitials] = useState('')
  const [newPatientInitialsTouched, setNewPatientInitialsTouched] = useState(false)
  const [newPatientNote, setNewPatientNote] = useState('')
  const [patientHomonyms, setPatientHomonyms] = useState<HomonymCandidate[] | null>(null)

  const [showNewEvaluator, setShowNewEvaluator] = useState(false)
  const [newEvaluatorName, setNewEvaluatorName] = useState('')
  const [newEvaluatorInitials, setNewEvaluatorInitials] = useState('')
  const [newEvaluatorInitialsTouched, setNewEvaluatorInitialsTouched] = useState(false)
  const [evaluatorHomonyms, setEvaluatorHomonyms] = useState<HomonymCandidate[] | null>(null)

  const [participant, setParticipant] = useState('')
  const [initials, setInitials] = useState('')
  const [visit, setVisit] = useState('')
  const [testCode, setTestCode] = useState('stroop_go_nogo_ptbr')
  const [reviewing, setReviewing] = useState(false)

  const [errors, setErrors] = useState({
    participant: '',
    evaluator: '',
    initials: '',
    visit: '',
  })
  const [saved, setSaved] = useState<Saved | null>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [unknownCreation, setUnknownCreation] = useState(false)
  const [revoked, setRevoked] = useState(false)

  const operation = useRef<AbortController | null>(null)
  const catalogOperation = useRef<AbortController | null>(null)
  const panel = useRef<HTMLElement>(null)
  const participantInput = useRef<HTMLInputElement>(null)
  const visitInput = useRef<HTMLInputElement>(null)
  const focusForm = useRef(false)

  useEffect(
    () => () => {
      operation.current?.abort()
      catalogOperation.current?.abort()
    },
    [],
  )

  useEffect(() => {
    const controller = new AbortController()
    catalogOperation.current?.abort()
    catalogOperation.current = controller
    void Promise.allSettled([
      listPatients({ search: patientSearch, active: 'true', page_size: 50 }, controller.signal).then(
        res => {
          if (!controller.signal.aborted) setPatients(res.items)
        },
      ),
      listEvaluators(
        { search: evaluatorSearch, active: 'true', page_size: 50 },
        controller.signal,
      ).then(res => {
        if (!controller.signal.aborted) setEvaluators(res.items)
      }),
    ])
    return () => controller.abort()
  }, [patientSearch, evaluatorSearch])

  useEffect(() => {
    if (!saved && !revoked && !unknownCreation && focusForm.current) {
      focusForm.current = false
      participantInput.current?.focus()
    }
  }, [saved, revoked, unknownCreation])

  useEffect(() => {
    if (saved || revoked || unknownCreation) panel.current?.focus()
  }, [saved, revoked, unknownCreation])

  function selectPatientRecord(record: PatientRecord | null) {
    setSelectedPatient(record)
    setReviewing(false)
    if (record) {
      setParticipant(record.participant_code)
      setInitials(record.initials ?? deriveInitials(record.full_name))
      setErrors(prev => ({ ...prev, participant: '' }))
    } else {
      setParticipant('')
      setInitials('')
    }
  }

  function selectEvaluatorRecord(record: EvaluatorRecord | null) {
    setSelectedEvaluator(record)
    setReviewing(false)
    if (record) {
      setErrors(prev => ({ ...prev, evaluator: '' }))
    }
  }

  async function handleCreatePatient(confirmHomonym = false) {
    if (operation.current || busy) return
    const trimmedName = newPatientName.trim()
    if (trimmedName.length < 2 || trimmedName.length > 120) {
      setMessage('Informe o nome completo do paciente (2 a 120 caracteres).')
      return
    }
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    setMessage(null)
    try {
      const created = await createPatient(
        {
          full_name: trimmedName,
          initials: (newPatientInitials || deriveInitials(trimmedName)).trim() || null,
          disambiguation_note: newPatientNote.trim() || null,
          confirm_homonym: confirmHomonym,
        },
        profile.csrf_token,
        io.signal,
      )
      if (!io.signal.aborted) {
        setPatients(prev => [created, ...prev.filter(item => item.id !== created.id)])
        selectPatientRecord(created)
        setShowNewPatient(false)
        setNewPatientName('')
        setNewPatientInitials('')
        setNewPatientInitialsTouched(false)
        setNewPatientNote('')
        setPatientHomonyms(null)
      }
    } catch (cause) {
      if (!io.signal.aborted) {
        if (cause instanceof ApiError && cause.code === 'duplicate_candidate_found') {
          const candidates: HomonymCandidate[] = (cause.candidates ?? []).map(item => ({
            id: String(item.id ?? ''),
            code: String(item.participant_code ?? ''),
            full_name: String(item.full_name ?? ''),
            initials: typeof item.initials === 'string' ? item.initials : null,
            disambiguation_note:
              typeof item.disambiguation_note === 'string' ? item.disambiguation_note : null,
          }))
          setPatientHomonyms(candidates)
          setMessage(apiErrorMessage(cause))
        } else {
          setMessage(apiErrorMessage(cause))
        }
      }
    } finally {
      if (!io.signal.aborted) {
        operation.current = null
        setBusy(false)
      }
    }
  }

  async function handleCreateEvaluator(confirmHomonym = false) {
    if (operation.current || busy) return
    const trimmedName = newEvaluatorName.trim()
    if (trimmedName.length < 2 || trimmedName.length > 120) {
      setMessage('Informe o nome completo do avaliador (2 a 120 caracteres).')
      return
    }
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    setMessage(null)
    try {
      const created = await createEvaluator(
        {
          full_name: trimmedName,
          initials: (newEvaluatorInitials || deriveInitials(trimmedName)).trim() || null,
          confirm_homonym: confirmHomonym,
        },
        profile.csrf_token,
        io.signal,
      )
      if (!io.signal.aborted) {
        setEvaluators(prev => [created, ...prev.filter(item => item.id !== created.id)])
        selectEvaluatorRecord(created)
        setShowNewEvaluator(false)
        setNewEvaluatorName('')
        setNewEvaluatorInitials('')
        setNewEvaluatorInitialsTouched(false)
        setEvaluatorHomonyms(null)
      }
    } catch (cause) {
      if (!io.signal.aborted) {
        if (cause instanceof ApiError && cause.code === 'duplicate_candidate_found') {
          const candidates: HomonymCandidate[] = (cause.candidates ?? []).map(item => ({
            id: String(item.id ?? ''),
            code: String(item.evaluator_code ?? ''),
            full_name: String(item.full_name ?? ''),
            initials: typeof item.initials === 'string' ? item.initials : null,
            disambiguation_note: null,
          }))
          setEvaluatorHomonyms(candidates)
          setMessage(apiErrorMessage(cause))
        } else {
          setMessage(apiErrorMessage(cause))
        }
      }
    } finally {
      if (!io.signal.aborted) {
        operation.current = null
        setBusy(false)
      }
    }
  }

  function validatePreparation() {
    const p = (selectedPatient ? selectedPatient.participant_code : participant).trim()
    const v = visit.trim()
    const ini = initials.trim().toUpperCase()
    const hasCadastral = selectedPatient !== null || selectedEvaluator !== null
    const next = {
      participant: hasCadastral
        ? selectedPatient
          ? ''
          : 'Selecione ou cadastre o paciente da sessão.'
        : labelPattern.test(p)
          ? ''
          : 'Use de 1 a 64 letras, números, ponto, hífen ou sublinhado.',
      evaluator: hasCadastral && !selectedEvaluator
        ? 'Selecione ou cadastre o avaliador responsável pela sessão.'
        : '',
      initials:
        ini && !initialsPattern.test(ini)
          ? 'Use até 16 letras, números, ponto ou hífen nas iniciais.'
          : '',
      visit: labelPattern.test(v)
        ? ''
        : 'Use de 1 a 64 letras, números, ponto, hífen ou sublinhado.',
    }
    setErrors(next)
    setMessage(null)
    if (next.participant || next.evaluator || next.initials || next.visit) {
      if (next.participant) participantInput.current?.focus()
      else if (next.visit) visitInput.current?.focus()
      return null
    }
    setParticipant(p)
    setVisit(v)
    if (ini) setInitials(ini)
    return { p, v, ini, hasCadastral }
  }

  function handleReview() {
    if (operation.current || saved || unknownCreation) return
    const valid = validatePreparation()
    if (!valid) return
    setReviewing(true)
  }

  async function issueInvitation() {
    if (operation.current || saved || unknownCreation) return
    const valid = validatePreparation()
    if (!valid) return
    const { p, v, ini } = valid
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    try {
      const invitation =
        selectedPatient && selectedEvaluator
          ? await createInvitation(
              project.id,
              {
                patient_id: selectedPatient.id,
                evaluator_id: selectedEvaluator.id,
                visit: v,
                test_code: testCode,
                initials: ini || null,
              },
              profile.csrf_token,
              io.signal,
            )
          : await createInvitation(
              project.id,
              { participant_id: p, visit: v },
              profile.csrf_token,
              io.signal,
            )
      if (!io.signal.aborted) {
        const summary = invitation.summary
        setSaved({
          invitation,
          participant: summary ? summary.participant_code : p,
          visit: v,
          summary,
        })
        setReviewing(false)
      }
    } catch (cause) {
      if (!io.signal.aborted) {
        if (uncertain(cause)) {
          setUnknownCreation(true)
          setMessage(
            'Não foi possível confirmar a criação. A sessão pode ter sido criada, mas o código não pode ser recuperado. Nenhuma nova emissão será feita automaticamente. Sem identificador confirmado, não é possível revogar este convite por esta tela. Informe o responsável antes de preparar outra sessão.',
          )
        } else {
          setMessage(apiErrorMessage(cause))
        }
      }
    } finally {
      if (!io.signal.aborted) {
        operation.current = null
        setBusy(false)
      }
    }
  }

  async function create(event: FormEvent) {
    event.preventDefault()
    await issueInvitation()
  }

  async function revoke() {
    if (!saved || operation.current || revoked) return
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    setMessage(null)
    try {
      await revokeInvitation(
        project.id,
        saved.invitation.invitation_id,
        profile.csrf_token,
        io.signal,
      )
      if (!io.signal.aborted) {
        setRevoked(true)
        setSaved(null)
        setSelectedPatient(null)
        setSelectedEvaluator(null)
        setParticipant('')
        setInitials('')
        setVisit('')
        setReviewing(false)
      }
    } catch (cause) {
      if (!io.signal.aborted)
        setMessage(
          uncertain(cause)
            ? 'A revogação ainda não foi confirmada. Não entregue o código; confirme novamente a revogação.'
            : apiErrorMessage(cause),
        )
    } finally {
      if (!io.signal.aborted) {
        operation.current = null
        setBusy(false)
      }
    }
  }

  function reset() {
    if (operation.current) return
    focusForm.current = true
    setSaved(null)
    setRevoked(false)
    setUnknownCreation(false)
    setSelectedPatient(null)
    setSelectedEvaluator(null)
    setParticipant('')
    setInitials('')
    setVisit('')
    setReviewing(false)
    setShowNewPatient(false)
    setShowNewEvaluator(false)
    setPatientHomonyms(null)
    setEvaluatorHomonyms(null)
    setMessage(null)
    setErrors({ participant: '', evaluator: '', initials: '', visit: '' })
  }

  return (
    <section
      className="assessment-detail session-invitation"
      aria-label="Preparar sessão"
      ref={panel}
      tabIndex={-1}
      aria-busy={busy}
    >
      <h3>Preparar sessão</h3>
      <p>
        Projeto: {project.code} — {project.name}
      </p>
      <p>
        Conta autenticada: {profile.user_id}.{' '}
        {selectedEvaluator
          ? `Avaliador responsável selecionado: ${selectedEvaluator.full_name} (${selectedEvaluator.evaluator_code}).`
          : `Avaliador responsável: selecione no cadastro central ou utilize sua conta autenticada (${profile.user_id}).`}
      </p>
      <p className="quiet">
        Selecione ou cadastre o paciente e o avaliador responsável para gerar os códigos
        automaticamente sem digitação manual de IDs. Metadados técnicos (assessment_id,
        session_id, invitation_id, assessment_date, started_at, test_version: 0.2.2-web.1) são
        preenchidos automaticamente pelo servidor.
      </p>

      {!saved && !unknownCreation && !revoked && (
        <form onSubmit={event => void create(event)} noValidate className="dashboard-filters invitation-stepper-grid">
          {/* ETAPA 1: VÍNCULO CADASTRAL */}
          <div className="step-card">
            <div className="step-card-header">
              <span className="step-number-badge">1</span>
              <h4 className="step-card-title">Vínculo Cadastral</h4>
            </div>

            <div className="registry-selector">
              <label htmlFor="session-patient-search">
                Buscar paciente cadastrado
                <input
                  id="session-patient-search"
                  aria-label="Buscar paciente cadastrado"
                  type="search"
                  value={patientSearch}
                  disabled={busy}
                  autoComplete="off"
                  placeholder="Nome ou código PAT-..."
                  onChange={event => setPatientSearch(event.target.value)}
                />
              </label>
              <label htmlFor="session-patient-select">
                Paciente cadastrado
                <select
                  id="session-patient-select"
                  aria-label="Paciente cadastrado"
                  value={selectedPatient?.id ?? ''}
                  disabled={busy}
                  onChange={event => {
                    const found = patients.find(item => item.id === event.target.value) ?? null
                    selectPatientRecord(found)
                  }}
                >
                  <option value="">Selecione um paciente ou cadastre novo…</option>
                  {patients.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.full_name} ({item.participant_code})
                      {item.disambiguation_note ? ` — ${item.disambiguation_note}` : ''}
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className="button secondary button-sm"
                disabled={busy}
                onClick={() => {
                  setShowNewPatient(prev => !prev)
                  setPatientHomonyms(null)
                }}
              >
                {showNewPatient ? 'Cancelar novo paciente' : 'Cadastrar novo paciente'}
              </button>
            </div>

            {showNewPatient && (
              <div role="group" aria-label="Novo cadastro de paciente" className="inline-registry-box">
                <label htmlFor="new-patient-full-name">
                  Nome completo do paciente
                  <input
                    id="new-patient-full-name"
                    maxLength={120}
                    value={newPatientName}
                    disabled={busy}
                    autoComplete="off"
                    onChange={event => {
                      const value = event.target.value
                      setNewPatientName(value)
                      if (!newPatientInitialsTouched) {
                        setNewPatientInitials(deriveInitials(value))
                      }
                    }}
                  />
                </label>
                <label htmlFor="new-patient-initials">
                  Iniciais do paciente
                  <input
                    id="new-patient-initials"
                    maxLength={16}
                    value={newPatientInitials}
                    disabled={busy}
                    autoComplete="off"
                    onChange={event => {
                      setNewPatientInitialsTouched(true)
                      setNewPatientInitials(event.target.value.toUpperCase())
                    }}
                  />
                </label>
                <label htmlFor="new-patient-note">
                  Nota de desambiguação (opcional)
                  <input
                    id="new-patient-note"
                    maxLength={160}
                    value={newPatientNote}
                    disabled={busy}
                    autoComplete="off"
                    onChange={event => setNewPatientNote(event.target.value)}
                  />
                </label>
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => void handleCreatePatient(false)}
                >
                  Salvar paciente
                </button>
                {patientHomonyms && patientHomonyms.length > 0 && (
                  <div role="alert" aria-label="Alerta de homônimo de paciente" className="homonym-alert">
                    <p>
                      Possível homônimo encontrado para este paciente. Selecione o cadastro existente
                      ou confirme que se trata de outra pessoa:
                    </p>
                    <ul className="homonym-list">
                      {patientHomonyms.map(candidate => (
                        <li key={candidate.id}>
                          {candidate.full_name} ({candidate.code})
                          {candidate.disambiguation_note
                            ? ` — ${candidate.disambiguation_note}`
                            : ''}{' '}
                          <button
                            type="button"
                            className="button secondary button-sm"
                            disabled={busy}
                            onClick={() => {
                              const existing = patients.find(p => p.id === candidate.id)
                              if (existing) {
                                selectPatientRecord(existing)
                                setShowNewPatient(false)
                                setPatientHomonyms(null)
                              }
                            }}
                          >
                            Usar {candidate.code}
                          </button>
                        </li>
                      ))}
                    </ul>
                    <button
                      type="button"
                      className="button secondary"
                      disabled={busy}
                      onClick={() => void handleCreatePatient(true)}
                    >
                      Confirmar homônimo e cadastrar paciente
                    </button>
                  </div>
                )}
              </div>
            )}

            <div className="registry-selector" style={{ marginTop: '12px' }}>
              <label htmlFor="session-evaluator-search">
                Buscar avaliador responsável
                <input
                  id="session-evaluator-search"
                  aria-label="Buscar avaliador responsável"
                  type="search"
                  value={evaluatorSearch}
                  disabled={busy}
                  autoComplete="off"
                  placeholder="Nome ou código EVA-..."
                  onChange={event => setEvaluatorSearch(event.target.value)}
                />
              </label>
              <label htmlFor="session-evaluator-select">
                Avaliador responsável
                <select
                  id="session-evaluator-select"
                  aria-label="Avaliador responsável"
                  value={selectedEvaluator?.id ?? ''}
                  disabled={busy}
                  aria-invalid={!!errors.evaluator}
                  aria-describedby={errors.evaluator ? 'session-evaluator-error' : undefined}
                  onChange={event => {
                    const found = evaluators.find(item => item.id === event.target.value) ?? null
                    selectEvaluatorRecord(found)
                  }}
                >
                  <option value="">Selecione um avaliador ou cadastre novo…</option>
                  {evaluators.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.full_name} ({item.evaluator_code})
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className="button secondary button-sm"
                disabled={busy}
                onClick={() => {
                  setShowNewEvaluator(prev => !prev)
                  setEvaluatorHomonyms(null)
                }}
              >
                {showNewEvaluator ? 'Cancelar novo avaliador' : 'Cadastrar novo avaliador'}
              </button>
            </div>
            {errors.evaluator && (
              <p id="session-evaluator-error" role="alert" className="notice" style={{ margin: '8px 0' }}>
                {errors.evaluator}
              </p>
            )}

            {showNewEvaluator && (
              <div
                role="group"
                aria-label="Novo cadastro de avaliador"
                className="inline-registry-box"
              >
                <label htmlFor="new-evaluator-full-name">
                  Nome completo do avaliador
                  <input
                    id="new-evaluator-full-name"
                    maxLength={120}
                    value={newEvaluatorName}
                    disabled={busy}
                    autoComplete="off"
                    onChange={event => {
                      const value = event.target.value
                      setNewEvaluatorName(value)
                      if (!newEvaluatorInitialsTouched) {
                        setNewEvaluatorInitials(deriveInitials(value))
                      }
                    }}
                  />
                </label>
                <label htmlFor="new-evaluator-initials">
                  Iniciais do avaliador
                  <input
                    id="new-evaluator-initials"
                    maxLength={16}
                    value={newEvaluatorInitials}
                    disabled={busy}
                    autoComplete="off"
                    onChange={event => {
                      setNewEvaluatorInitialsTouched(true)
                      setNewEvaluatorInitials(event.target.value.toUpperCase())
                    }}
                  />
                </label>
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => void handleCreateEvaluator(false)}
                >
                  Salvar avaliador
                </button>
                {evaluatorHomonyms && evaluatorHomonyms.length > 0 && (
                  <div role="alert" aria-label="Alerta de homônimo de avaliador" className="homonym-alert">
                    <p>
                      Possível homônimo encontrado para este avaliador. Confirme se deseja criar novo
                      registro:
                    </p>
                    <button
                      type="button"
                      className="button secondary"
                      disabled={busy}
                      onClick={() => void handleCreateEvaluator(true)}
                    >
                      Confirmar homônimo e cadastrar avaliador
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ETAPA 2: PARÂMETROS DA SESSÃO */}
          <div className="step-card">
            <div className="step-card-header">
              <span className="step-number-badge">2</span>
              <h4 className="step-card-title">Parâmetros da Sessão</h4>
            </div>

            <label htmlFor="session-test-code">
              Instrumento
              <select
                id="session-test-code"
                value={testCode}
                disabled={busy}
                onChange={event => {
                  setTestCode(event.target.value)
                  setReviewing(false)
                }}
              >
                <option value="stroop_go_nogo_ptbr">
                  Stroop Go/No-Go (stroop_go_nogo_ptbr · v0.2.2-web.1)
                </option>
              </select>
            </label>

            <label htmlFor="session-participant">
              Código do participante
              <input
                ref={participantInput}
                id="session-participant"
                required
                maxLength={64}
                value={selectedPatient ? selectedPatient.participant_code : participant}
                readOnly={!!selectedPatient}
                disabled={busy}
                autoComplete="off"
                aria-invalid={!!errors.participant}
                aria-describedby={errors.participant ? 'session-participant-error' : undefined}
                onChange={event => {
                  if (!selectedPatient) {
                    setParticipant(event.target.value)
                    setReviewing(false)
                  }
                }}
              />
            </label>
            {errors.participant && (
              <p id="session-participant-error" role="alert" className="notice" style={{ margin: '8px 0' }}>
                {errors.participant}
              </p>
            )}

            <label htmlFor="session-initials">
              Iniciais na sessão
              <input
                id="session-initials"
                maxLength={16}
                value={initials}
                disabled={busy}
                autoComplete="off"
                aria-invalid={!!errors.initials}
                aria-describedby={errors.initials ? 'session-initials-error' : undefined}
                onChange={event => {
                  setInitials(event.target.value.toUpperCase())
                  setReviewing(false)
                }}
              />
            </label>
            {errors.initials && (
              <p id="session-initials-error" role="alert" className="notice" style={{ margin: '8px 0' }}>
                {errors.initials}
              </p>
            )}

            <label htmlFor="session-visit">
              Visita da sessão
              <input
                ref={visitInput}
                id="session-visit"
                required
                maxLength={64}
                value={visit}
                disabled={busy}
                autoComplete="off"
                aria-invalid={!!errors.visit}
                aria-describedby={errors.visit ? 'session-visit-error' : undefined}
                onChange={event => {
                  setVisit(event.target.value)
                  setReviewing(false)
                }}
              />
            </label>
            {errors.visit && (
              <p id="session-visit-error" role="alert" className="notice" style={{ margin: '8px 0' }}>
                {errors.visit}
              </p>
            )}
          </div>

          {/* ETAPA 3: CONFERÊNCIA E EMISSÃO */}
          <div className="step-card">
            <div className="step-card-header">
              <span className="step-number-badge">3</span>
              <h4 className="step-card-title">Emissão e Conferência</h4>
            </div>

            <p className="quiet" style={{ margin: '0 0 12px 0' }}>
              Confira os parâmetros antes de emitir o convite único. O código gerado terá validade limitada e uso único.
            </p>

            <div className="session-actions" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="button secondary"
                disabled={busy}
                onClick={handleReview}
              >
                Revisar preparação
              </button>
              <button className="button primary" disabled={busy} type="submit">
                {busy ? 'Gerando convite…' : 'Gerar convite'}
              </button>
            </div>

            {reviewing && (
              <div
                role="region"
                aria-label="Resumo para conferência"
                className="preparation-review-card"
              >
                <h4>Resumo para conferência</h4>
                <dl>
                  <div>
                    <dt>Projeto</dt>
                    <dd>
                      {project.code} — {project.name}
                    </dd>
                  </div>
                  <div>
                    <dt>Paciente</dt>
                    <dd>
                      {selectedPatient
                        ? `${selectedPatient.full_name} (${selectedPatient.participant_code})`
                        : participant}
                    </dd>
                  </div>
                  <div>
                    <dt>Iniciais</dt>
                    <dd>{initials || '—'}</dd>
                  </div>
                  <div>
                    <dt>Avaliador responsável</dt>
                    <dd>
                      {selectedEvaluator
                        ? `${selectedEvaluator.full_name} (${selectedEvaluator.evaluator_code})`
                        : profile.user_id}
                    </dd>
                  </div>
                  <div>
                    <dt>Visita</dt>
                    <dd>{visit}</dd>
                  </div>
                  <div>
                    <dt>Instrumento e versão</dt>
                    <dd>{testCode} · 0.2.2-web.1</dd>
                  </div>
                </dl>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    className="button primary"
                    disabled={busy}
                    onClick={() => void issueInvitation()}
                  >
                    {busy ? 'Confirmando…' : 'Confirmar e emitir convite'}
                  </button>
                  <button
                    type="button"
                    className="button secondary"
                    disabled={busy}
                    onClick={() => setReviewing(false)}
                  >
                    Voltar e editar
                  </button>
                </div>
              </div>
            )}
          </div>
        </form>
      )}

      {saved && (
        <div className="preparation-review-card" style={{ background: '#f8fafc', borderColor: '#cbd5e1' }}>
          <h4>Convite criado com sucesso</h4>
          <p>
            Participante: {saved.participant} · Visita: {saved.visit}
          </p>
          {saved.summary && (
            <p>
              Paciente: {saved.summary.participant_name} ({saved.summary.participant_code}) ·
              Iniciais: {saved.summary.initials ?? '—'} · Avaliador: {saved.summary.evaluator_name}{' '}
              ({saved.summary.evaluator_code}) · Instrumento: {saved.summary.test_code} (
              {saved.summary.test_version})
            </p>
          )}
          <p>Sessão: {saved.invitation.session_id}</p>
          <p>
            Código de uso único:{' '}
            <output aria-label="Código do convite" className="invitation-code-display">{saved.invitation.code}</output>
          </p>
          <p>Expira em: {saved.invitation.expires_at} (UTC). Após o prazo, solicite uma nova sessão.</p>
          <p className="quiet">
            Entregue o código ao participante por canal apropriado. Ele só aparece agora e será
            apagado ao trocar de projeto, sair ou recarregar. Abrir a prática exige informar o
            convite; o código não é incluído no endereço.
          </p>
          <div style={{ display: 'flex', gap: '10px', marginTop: '16px', flexWrap: 'wrap' }}>
            <a className="button primary" href="/pratica" target="_blank" rel="noopener noreferrer">
              Abrir prática em outra aba ↗
            </a>
            <button className="button secondary button-danger" disabled={busy} onClick={() => void revoke()}>
              {busy ? 'Revogando…' : 'Revogar convite'}
            </button>
          </div>
        </div>
      )}

      {revoked && (
        <p role="status">
          Revogação confirmada. O convite não permite iniciar ou continuar a sessão.
        </p>
      )}
      {message && <p role="alert">{message}</p>}
      {(saved || unknownCreation || revoked) && (
        <>
          <p className="quiet">
            Preparar outra sessão apaga os dados desta tela e cria uma sessão distinta somente após
            nova confirmação. Não revoga convites anteriores.
          </p>
          <button className="button secondary" disabled={busy} onClick={reset}>
            Preparar outra sessão
          </button>
        </>
      )}
    </section>
  )
}
