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
  const canManage = profile.role === 'importacao' || profile.role === 'administracao'

  // Estados de Pacientes
  const [patients, setPatients] = useState<PatientRecord[]>([])
  const [patientSearch, setPatientSearch] = useState('')
  const [selectedPatient, setSelectedPatient] = useState<PatientRecord | null>(null)
  const [patientLoading, setPatientLoading] = useState(false)
  const [patientSearchError, setPatientSearchError] = useState<string | null>(null)

  // Cadastro de Novo Paciente
  const [showNewPatient, setShowNewPatient] = useState(false)
  const [newPatientName, setNewPatientName] = useState('')
  const [newPatientInitials, setNewPatientInitials] = useState('')
  const [newPatientInitialsTouched, setNewPatientInitialsTouched] = useState(false)
  const [newPatientNote, setNewPatientNote] = useState('')
  const [patientHomonyms, setPatientHomonyms] = useState<HomonymCandidate[] | null>(null)
  const [newPatientError, setNewPatientError] = useState<string | null>(null)

  // Estados de Avaliadores
  const [evaluators, setEvaluators] = useState<EvaluatorRecord[]>([])
  const [evaluatorSearch, setEvaluatorSearch] = useState('')
  const [selectedEvaluator, setSelectedEvaluator] = useState<EvaluatorRecord | null>(null)
  const [evaluatorLoading, setEvaluatorLoading] = useState(false)
  const [evaluatorSearchError, setEvaluatorSearchError] = useState<string | null>(null)

  // Cadastro de Novo Avaliador
  const [showNewEvaluator, setShowNewEvaluator] = useState(false)
  const [newEvaluatorName, setNewEvaluatorName] = useState('')
  const [newEvaluatorInitials, setNewEvaluatorInitials] = useState('')
  const [newEvaluatorInitialsTouched, setNewEvaluatorInitialsTouched] = useState(false)
  const [evaluatorHomonyms, setEvaluatorHomonyms] = useState<HomonymCandidate[] | null>(null)
  const [newEvaluatorError, setNewEvaluatorError] = useState<string | null>(null)

  // Parâmetros da Sessão
  const [participant, setParticipant] = useState('')
  const [initials, setInitials] = useState('')
  const [visit, setVisit] = useState('')
  const [testCode, setTestCode] = useState('stroop_go_nogo_ptbr')
  const [applicationMode, setApplicationMode] = useState<'presencial' | 'remota'>('remota')
  const [reviewing, setReviewing] = useState(false)

  // Mensagens e Estados Operacionais
  const [errors, setErrors] = useState({
    participant: '',
    evaluator: '',
    initials: '',
    visit: '',
  })
  const [saved, setSaved] = useState<Saved | null>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [successNotice, setSuccessNotice] = useState<string | null>(null)
  const [unknownCreation, setUnknownCreation] = useState(false)
  const [revoked, setRevoked] = useState(false)

  // AbortControllers e Refs
  const operation = useRef<AbortController | null>(null)
  const patientController = useRef<AbortController | null>(null)
  const evaluatorController = useRef<AbortController | null>(null)
  const panel = useRef<HTMLElement>(null)
  const participantInput = useRef<HTMLInputElement>(null)
  const visitInput = useRef<HTMLInputElement>(null)
  const focusForm = useRef(false)

  useEffect(
    () => () => {
      operation.current?.abort()
      patientController.current?.abort()
      evaluatorController.current?.abort()
    },
    [],
  )

  // Busca de pacientes independente
  useEffect(() => {
    patientController.current?.abort()
    const controller = new AbortController()
    patientController.current = controller
    setPatientLoading(true)
    setPatientSearchError(null)

    listPatients(
      { search: patientSearch.trim() || undefined, active: 'true', page_size: 50 },
      controller.signal,
    )
      .then(res => {
        if (!controller.signal.aborted) {
          setPatients(res.items)
        }
      })
      .catch(err => {
        if (!controller.signal.aborted) {
          if (err instanceof ApiError && err.code === 'permission_denied') {
            setPatientSearchError('Seu perfil não possui permissão para listar pacientes.')
          } else if (err?.name !== 'AbortError' && !(err instanceof ApiError && err.code === 'request_cancelled')) {
            setPatientSearchError('Erro ao consultar pacientes no banco de dados.')
          }
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setPatientLoading(false)
        }
      })

    return () => controller.abort()
  }, [patientSearch])

  // Busca de avaliadores independente
  useEffect(() => {
    evaluatorController.current?.abort()
    const controller = new AbortController()
    evaluatorController.current = controller
    setEvaluatorLoading(true)
    setEvaluatorSearchError(null)

    listEvaluators(
      { search: evaluatorSearch.trim() || undefined, active: 'true', page_size: 50 },
      controller.signal,
    )
      .then(res => {
        if (!controller.signal.aborted) {
          setEvaluators(res.items)
        }
      })
      .catch(err => {
        if (!controller.signal.aborted) {
          if (err instanceof ApiError && err.code === 'permission_denied') {
            setEvaluatorSearchError('Seu perfil não possui permissão para listar avaliadores.')
          } else if (err?.name !== 'AbortError' && !(err instanceof ApiError && err.code === 'request_cancelled')) {
            setEvaluatorSearchError('Erro ao consultar avaliadores no banco de dados.')
          }
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setEvaluatorLoading(false)
        }
      })

    return () => controller.abort()
  }, [evaluatorSearch])

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
    if (!canManage) {
      setMessage('Seu perfil não permite esta operação. O cadastro de pacientes exige perfil de importação ou administração.')
      return
    }
    const trimmedName = newPatientName.trim()
    if (trimmedName.length < 2 || trimmedName.length > 120) {
      setNewPatientError('Informe o nome completo do paciente (2 a 120 caracteres).')
      return
    }
    setNewPatientError(null)
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    setMessage(null)
    setSuccessNotice(null)
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
        setSuccessNotice(`Paciente ${created.full_name} (${created.participant_code}) cadastrado e selecionado!`)
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
        } else if (cause instanceof ApiError && cause.code === 'permission_denied') {
          setMessage('Seu perfil não permite esta operação. O cadastro de pacientes exige perfil de importação ou administração.')
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
    if (!canManage) {
      setMessage('Seu perfil não permite esta operação. O cadastro de avaliadores exige perfil de importação ou administração.')
      return
    }
    const trimmedName = newEvaluatorName.trim()
    if (trimmedName.length < 2 || trimmedName.length > 120) {
      setNewEvaluatorError('Informe o nome completo do avaliador (2 a 120 caracteres).')
      return
    }
    setNewEvaluatorError(null)
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    setMessage(null)
    setSuccessNotice(null)
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
        setSuccessNotice(`Avaliador ${created.full_name} (${created.evaluator_code}) cadastrado e selecionado!`)
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
        } else if (cause instanceof ApiError && cause.code === 'permission_denied') {
          setMessage('Seu perfil não permite esta operação. O cadastro de avaliadores exige perfil de importação ou administração.')
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
    if (!canManage) {
      setMessage('Seu perfil não permite esta operação. A emissão de convites exige perfil de importação ou administração.')
      return
    }
    const valid = validatePreparation()
    if (!valid) return
    const { p, v, ini } = valid
    const io = new AbortController()
    operation.current = io
    setBusy(true)
    setMessage(null)
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
        } else if (cause instanceof ApiError && cause.code === 'permission_denied') {
          setMessage('Seu perfil não permite esta operação. A emissão de convites exige permissão de importação ou administração vinculada a este projeto.')
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
    setSuccessNotice(null)
    setErrors({ participant: '', evaluator: '', initials: '', visit: '' })
  }

  // Lista de pacientes exibida no dropdown sempre garante a inclusão do selecionado
  const displayedPatients =
    selectedPatient && !patients.some(item => item.id === selectedPatient.id)
      ? [selectedPatient, ...patients]
      : patients

  // Lista de avaliadores exibida no dropdown sempre garante a inclusão do selecionado
  const displayedEvaluators =
    selectedEvaluator && !evaluators.some(item => item.id === selectedEvaluator.id)
      ? [selectedEvaluator, ...evaluators]
      : evaluators

  return (
    <section
      className="session-prep-container assessment-detail session-invitation"
      aria-label="Preparar sessão"
      ref={panel}
      tabIndex={-1}
      aria-busy={busy}
    >
      {/* CABEÇALHO RECONSTRUÍDO */}
      <header className="session-prep-header">
        <div className="session-prep-header-main">
          <div className="session-prep-title-row">
            <h3 className="session-prep-title">Preparar sessão</h3>
            <span className="session-prep-status-badge">
              Projeto ativo: <strong>{project.code}</strong>
            </span>
          </div>
          <p className="session-prep-subtitle">
            Configure o participante, o avaliador e os parâmetros da sessão para iniciar a avaliação ou emitir um convite seguro.
          </p>
          <div className="session-prep-project-banner">
            <div className="session-prep-project-info">
              <span className="session-prep-label-tag">Projeto</span>
              <strong className="session-prep-project-name">{project.name}</strong>
              <span className="session-prep-project-code">({project.code})</span>
            </div>
            <div className="session-prep-user-badge">
              <span className="session-prep-label-tag">Operador autenticado</span>
              <strong>{profile.user_id}</strong>
              <span className="session-role-pill" data-role={profile.role}>
                {profile.role}
              </span>
            </div>
          </div>
        </div>

        {/* Banner de permissão quando usuário for consulta */}
        {!canManage && (
          <div className="session-permission-notice" role="status">
            <span className="session-permission-icon" aria-hidden="true">ℹ</span>
            <div>
              <strong>Modo de Consulta (leitura):</strong> Seu perfil permite buscar e consultar registros.
              O cadastro de novos pacientes ou avaliadores e a emissão de convites exigem perfil de <em>importação</em> ou <em>administração</em>.
            </div>
          </div>
        )}

        {/* Informações técnicas em seção recolhível */}
        <details className="session-prep-tech-details">
          <summary className="session-prep-tech-summary">
            Informações técnicas do protocolo e auditoria (clique para expandir)
          </summary>
          <div className="session-prep-tech-content">
            <div className="session-prep-meta-row">
              <span className="session-prep-chip">
                Instrumento: <strong>Stroop Go/No-Go (stroop_go_nogo_ptbr)</strong>
              </span>
              <span className="session-prep-chip">
                Versão do teste: <strong>0.2.2-web.1</strong>
              </span>
              <span className="session-prep-chip">
                Protocolo: <strong>stroop_go_nogo_ptbr/0.2.2-web.1</strong>
              </span>
              <span className="session-prep-chip">
                Conta: <strong>{profile.user_id}</strong>
              </span>
            </div>
            <p className="session-prep-tech-description">
              Metadados técnicos de auditoria (<em>assessment_id</em>, <em>session_id</em>, <em>invitation_id</em>, <em>assessment_date</em> e <em>started_at</em>) são gerenciados e preenchidos automaticamente pelo servidor com integridade criptográfica. Tokens e credenciais operacionais nunca são expostos na URL.
            </p>
          </div>
        </details>
      </header>

      {/* Notificações contextuais globais */}
      {successNotice && (
        <div role="status" className="session-prep-toast success">
          <span aria-hidden="true">✓</span> {successNotice}
        </div>
      )}
      {message && (
        <div role="alert" className="session-prep-toast error">
          <span aria-hidden="true">⚠</span> {message}
        </div>
      )}

      {/* FORMULÁRIO PRINCIPAL */}
      {!saved && !unknownCreation && !revoked && (
        <form onSubmit={event => void create(event)} noValidate className="session-prep-form">
          {/* SEÇÃO 1: PARTICIPANTE */}
          <fieldset className="prep-section-card">
            <legend className="prep-section-header">
              <span className="step-number-badge">1</span>
              <div>
                <h4 className="prep-section-title">Participante</h4>
                <p className="prep-section-subtitle">
                  Busque no banco de dados ou cadastre um novo paciente para associar à sessão.
                </p>
              </div>
            </legend>

            <div className="prep-section-content">
              {/* Linha de busca e seleção */}
              <div className="prep-lookup-grid">
                <div className="prep-field-block">
                  <label htmlFor="session-patient-search" className="prep-field-label">
                    Buscar paciente cadastrado
                  </label>
                  <div className="prep-input-search-wrapper">
                    <input
                      id="session-patient-search"
                      aria-label="Buscar paciente cadastrado"
                      type="search"
                      value={patientSearch}
                      disabled={busy}
                      autoComplete="off"
                      placeholder="Buscar por nome ou código PAT-..."
                      className="prep-search-input"
                      onChange={event => setPatientSearch(event.target.value)}
                    />
                    {patientLoading && <span className="prep-search-spinner" aria-hidden="true">⏳</span>}
                  </div>
                </div>

                <div className="prep-field-block">
                  <label htmlFor="session-patient-select" className="prep-field-label">
                    Selecionar paciente dos resultados
                  </label>
                  <select
                    id="session-patient-select"
                    aria-label="Paciente cadastrado"
                    value={selectedPatient?.id ?? ''}
                    disabled={busy}
                    className="prep-select"
                    aria-invalid={!!errors.participant}
                    aria-describedby={errors.participant ? 'session-patient-error' : undefined}
                    onChange={event => {
                      const found = displayedPatients.find(item => item.id === event.target.value) ?? null
                      selectPatientRecord(found)
                    }}
                  >
                    <option value="">Selecione um paciente ou cadastre novo…</option>
                    {displayedPatients.map(item => (
                      <option key={item.id} value={item.id}>
                        {item.full_name} ({item.participant_code})
                        {item.disambiguation_note ? ` — ${item.disambiguation_note}` : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="prep-action-cell">
                  <button
                    type="button"
                    aria-label={showNewPatient ? 'Cancelar novo paciente' : 'Cadastrar novo paciente'}
                    className={`button ${showNewPatient ? 'secondary' : 'primary'} button-toggle-registry`}
                    disabled={busy || !canManage}
                    title={!canManage ? 'Seu perfil de consulta não permite cadastrar novos pacientes.' : undefined}
                    onClick={() => {
                      setShowNewPatient(prev => !prev)
                      setPatientHomonyms(null)
                      setNewPatientError(null)
                    }}
                  >
                    {showNewPatient ? 'Cancelar novo paciente' : 'Cadastrar novo paciente'}
                  </button>
                </div>
              </div>

              {/* Feedbacks de busca */}
              {patientSearchError && (
                <p role="alert" className="prep-inline-feedback error">
                  {patientSearchError}
                </p>
              )}
              {patientSearch.trim().length > 0 && !patientLoading && patients.length === 0 && !patientSearchError && (
                <p className="prep-inline-feedback quiet">
                  Nenhum paciente cadastrado encontrado para "{patientSearch.trim()}". Verifique o termo ou cadastre um novo paciente.
                </p>
              )}

              {/* Resumo compacto do paciente selecionado */}
              {selectedPatient && (
                <div className="session-selected-card" role="region" aria-label="Paciente selecionado">
                  <div className="session-selected-info">
                    <span className="session-selected-icon" aria-hidden="true">👤</span>
                    <div>
                      <div className="session-selected-name-row">
                        <strong className="session-selected-name">{selectedPatient.full_name}</strong>
                        <span className="session-selected-code">{selectedPatient.participant_code}</span>
                      </div>
                      <div className="session-selected-meta-row">
                        <span>Iniciais: <strong>{selectedPatient.initials ?? '—'}</strong></span>
                        {selectedPatient.disambiguation_note && (
                          <span>Nota: <em>{selectedPatient.disambiguation_note}</em></span>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="button secondary button-sm"
                    disabled={busy}
                    onClick={() => selectPatientRecord(null)}
                    title="Remover seleção atual para buscar ou selecionar outro paciente"
                  >
                    Desmarcar paciente
                  </button>
                </div>
              )}

              {/* Formulário contextual de Novo Paciente */}
              {showNewPatient && (
                <div role="group" aria-label="Novo cadastro de paciente" className="inline-registry-box prep-expand-form">
                  <div className="prep-expand-form-header">
                    <h5 className="prep-expand-form-title">Novo cadastro de paciente</h5>
                    <p className="prep-expand-form-sub">
                      Preencha o nome completo para gerar o código estável PAT-... e desambiguar na pesquisa.
                    </p>
                  </div>

                  <div className="prep-form-grid-2">
                    <label htmlFor="new-patient-full-name" className="prep-field-label">
                      Nome completo do paciente
                      <input
                        id="new-patient-full-name"
                        maxLength={120}
                        required
                        value={newPatientName}
                        disabled={busy || !canManage}
                        autoComplete="off"
                        placeholder="Nome completo (2 a 120 caracteres)"
                        className="prep-text-input"
                        onChange={event => {
                          const value = event.target.value
                          setNewPatientName(value)
                          if (!newPatientInitialsTouched) {
                            setNewPatientInitials(deriveInitials(value))
                          }
                        }}
                      />
                    </label>

                    <label htmlFor="new-patient-initials" className="prep-field-label">
                      Iniciais do paciente
                      <input
                        id="new-patient-initials"
                        maxLength={16}
                        value={newPatientInitials}
                        disabled={busy || !canManage}
                        autoComplete="off"
                        placeholder="Iniciais (até 16 caracteres)"
                        className="prep-text-input"
                        onChange={event => {
                          setNewPatientInitialsTouched(true)
                          setNewPatientInitials(event.target.value.toUpperCase())
                        }}
                      />
                    </label>
                  </div>

                  <label htmlFor="new-patient-note" className="prep-field-label">
                    Nota de desambiguação (opcional)
                    <input
                      id="new-patient-note"
                      maxLength={160}
                      value={newPatientNote}
                      disabled={busy || !canManage}
                      autoComplete="off"
                      placeholder="Ex.: Turma A, Grupo Intervenção, Coorte 2026..."
                      className="prep-text-input"
                      onChange={event => setNewPatientNote(event.target.value)}
                    />
                  </label>

                  {newPatientError && (
                    <p role="alert" className="notice prep-field-error">
                      {newPatientError}
                    </p>
                  )}

                  <div className="prep-form-actions">
                    <button
                      type="button"
                      className="button primary"
                      disabled={busy || !canManage}
                      onClick={() => void handleCreatePatient(false)}
                    >
                      {busy ? 'Salvando…' : 'Salvar paciente'}
                    </button>
                    <button
                      type="button"
                      className="button secondary"
                      disabled={busy}
                      onClick={() => {
                        setShowNewPatient(false)
                        setPatientHomonyms(null)
                        setNewPatientError(null)
                      }}
                    >
                      Cancelar
                    </button>
                  </div>

                  {/* Resolução consciente de homônimo */}
                  {patientHomonyms && patientHomonyms.length > 0 && (
                    <div role="alert" aria-label="Alerta de homônimo de paciente" className="homonym-alert prep-homonym-box">
                      <h6>Possível homônimo encontrado no banco de dados</h6>
                      <p>
                        Já existe cadastro com nome semelhante. Selecione o paciente existente para evitar duplicidade ou confirme se é uma pessoa distinta:
                      </p>
                      <ul className="homonym-list">
                        {patientHomonyms.map(candidate => (
                          <li key={candidate.id} className="homonym-item">
                            <div>
                              <strong>{candidate.full_name}</strong> ({candidate.code})
                              {candidate.disambiguation_note ? ` — ${candidate.disambiguation_note}` : ''}
                            </div>
                            <button
                              type="button"
                              className="button secondary button-sm"
                              disabled={busy}
                              onClick={() => {
                                const existing = displayedPatients.find(p => p.id === candidate.id) ?? {
                                  id: candidate.id,
                                  participant_code: candidate.code,
                                  full_name: candidate.full_name,
                                  initials: candidate.initials,
                                  disambiguation_note: candidate.disambiguation_note,
                                  active: true,
                                  created_at: new Date().toISOString(),
                                  updated_at: new Date().toISOString(),
                                  project_count: 1,
                                  assessment_count: 0,
                                  last_assessment_at: null,
                                }
                                selectPatientRecord(existing)
                                setShowNewPatient(false)
                                setPatientHomonyms(null)
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
                        disabled={busy || !canManage}
                        onClick={() => void handleCreatePatient(true)}
                      >
                        Confirmar homônimo e cadastrar paciente
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </fieldset>

          {/* SEÇÃO 2: AVALIADOR */}
          <fieldset className="prep-section-card">
            <legend className="prep-section-header">
              <span className="step-number-badge">2</span>
              <div>
                <h4 className="prep-section-title">Avaliador Responsável</h4>
                <p className="prep-section-subtitle">
                  Indique o profissional responsável pela aplicação da avaliação (cadastro central EVA-...).
                </p>
              </div>
            </legend>

            <div className="prep-section-content">
              {/* Linha de busca e seleção */}
              <div className="prep-lookup-grid">
                <div className="prep-field-block">
                  <label htmlFor="session-evaluator-search" className="prep-field-label">
                    Buscar avaliador responsável
                  </label>
                  <div className="prep-input-search-wrapper">
                    <input
                      id="session-evaluator-search"
                      aria-label="Buscar avaliador responsável"
                      type="search"
                      value={evaluatorSearch}
                      disabled={busy}
                      autoComplete="off"
                      placeholder="Buscar por nome ou código EVA-..."
                      className="prep-search-input"
                      onChange={event => setEvaluatorSearch(event.target.value)}
                    />
                    {evaluatorLoading && <span className="prep-search-spinner" aria-hidden="true">⏳</span>}
                  </div>
                </div>

                <div className="prep-field-block">
                  <label htmlFor="session-evaluator-select" className="prep-field-label">
                    Selecionar avaliador responsável
                  </label>
                  <select
                    id="session-evaluator-select"
                    aria-label="Avaliador responsável"
                    value={selectedEvaluator?.id ?? ''}
                    disabled={busy}
                    className="prep-select"
                    aria-invalid={!!errors.evaluator}
                    aria-describedby={errors.evaluator ? 'session-evaluator-error' : undefined}
                    onChange={event => {
                      const found = displayedEvaluators.find(item => item.id === event.target.value) ?? null
                      selectEvaluatorRecord(found)
                    }}
                  >
                    <option value="">Selecione um avaliador ou cadastre novo…</option>
                    {displayedEvaluators.map(item => (
                      <option key={item.id} value={item.id}>
                        {item.full_name} ({item.evaluator_code})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="prep-action-cell">
                  <button
                    type="button"
                    aria-label={showNewEvaluator ? 'Cancelar novo avaliador' : 'Cadastrar novo avaliador'}
                    className={`button ${showNewEvaluator ? 'secondary' : 'primary'} button-toggle-registry`}
                    disabled={busy || !canManage}
                    title={!canManage ? 'Seu perfil de consulta não permite cadastrar novos avaliadores.' : undefined}
                    onClick={() => {
                      setShowNewEvaluator(prev => !prev)
                      setEvaluatorHomonyms(null)
                      setNewEvaluatorError(null)
                    }}
                  >
                    {showNewEvaluator ? 'Cancelar novo avaliador' : 'Cadastrar novo avaliador'}
                  </button>
                </div>
              </div>

              {/* Feedbacks de busca de avaliador */}
              {evaluatorSearchError && (
                <p role="alert" className="prep-inline-feedback error">
                  {evaluatorSearchError}
                </p>
              )}
              {evaluatorSearch.trim().length > 0 && !evaluatorLoading && evaluators.length === 0 && !evaluatorSearchError && (
                <p className="prep-inline-feedback quiet">
                  Nenhum avaliador encontrado para "{evaluatorSearch.trim()}". Verifique o termo ou cadastre um novo profissional.
                </p>
              )}
              {errors.evaluator && (
                <p id="session-evaluator-error" role="alert" className="notice prep-field-error">
                  {errors.evaluator}
                </p>
              )}

              {/* Resumo compacto do avaliador selecionado */}
              {selectedEvaluator && (
                <div className="session-selected-card" role="region" aria-label="Avaliador selecionado">
                  <div className="session-selected-info">
                    <span className="session-selected-icon" aria-hidden="true">🩺</span>
                    <div>
                      <div className="session-selected-name-row">
                        <strong className="session-selected-name">{selectedEvaluator.full_name}</strong>
                        <span className="session-selected-code">{selectedEvaluator.evaluator_code}</span>
                      </div>
                      <div className="session-selected-meta-row">
                        <span>Iniciais: <strong>{selectedEvaluator.initials ?? '—'}</strong></span>
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="button secondary button-sm"
                    disabled={busy}
                    onClick={() => selectEvaluatorRecord(null)}
                    title="Remover seleção atual para buscar ou selecionar outro avaliador"
                  >
                    Desmarcar avaliador
                  </button>
                </div>
              )}

              {/* Formulário contextual de Novo Avaliador */}
              {showNewEvaluator && (
                <div role="group" aria-label="Novo cadastro de avaliador" className="inline-registry-box prep-expand-form">
                  <div className="prep-expand-form-header">
                    <h5 className="prep-expand-form-title">Novo cadastro de avaliador</h5>
                    <p className="prep-expand-form-sub">
                      Informe o nome completo do pesquisador ou profissional para gerar o código estável EVA-...
                    </p>
                  </div>

                  <div className="prep-form-grid-2">
                    <label htmlFor="new-evaluator-full-name" className="prep-field-label">
                      Nome completo do avaliador
                      <input
                        id="new-evaluator-full-name"
                        maxLength={120}
                        required
                        value={newEvaluatorName}
                        disabled={busy || !canManage}
                        autoComplete="off"
                        placeholder="Nome completo (2 a 120 caracteres)"
                        className="prep-text-input"
                        onChange={event => {
                          const value = event.target.value
                          setNewEvaluatorName(value)
                          if (!newEvaluatorInitialsTouched) {
                            setNewEvaluatorInitials(deriveInitials(value))
                          }
                        }}
                      />
                    </label>

                    <label htmlFor="new-evaluator-initials" className="prep-field-label">
                      Iniciais do avaliador
                      <input
                        id="new-evaluator-initials"
                        maxLength={16}
                        value={newEvaluatorInitials}
                        disabled={busy || !canManage}
                        autoComplete="off"
                        placeholder="Iniciais (até 16 caracteres)"
                        className="prep-text-input"
                        onChange={event => {
                          setNewEvaluatorInitialsTouched(true)
                          setNewEvaluatorInitials(event.target.value.toUpperCase())
                        }}
                      />
                    </label>
                  </div>

                  {newEvaluatorError && (
                    <p role="alert" className="notice prep-field-error">
                      {newEvaluatorError}
                    </p>
                  )}

                  <div className="prep-form-actions">
                    <button
                      type="button"
                      className="button primary"
                      disabled={busy || !canManage}
                      onClick={() => void handleCreateEvaluator(false)}
                    >
                      {busy ? 'Salvando…' : 'Salvar avaliador'}
                    </button>
                    <button
                      type="button"
                      className="button secondary"
                      disabled={busy}
                      onClick={() => {
                        setShowNewEvaluator(false)
                        setEvaluatorHomonyms(null)
                        setNewEvaluatorError(null)
                      }}
                    >
                      Cancelar
                    </button>
                  </div>

                  {evaluatorHomonyms && evaluatorHomonyms.length > 0 && (
                    <div role="alert" aria-label="Alerta de homônimo de avaliador" className="homonym-alert prep-homonym-box">
                      <h6>Possível homônimo de avaliador identificado</h6>
                      <p>
                        Já existe avaliador cadastrado com grafia similar. Confirme se deseja criar um registro adicional:
                      </p>
                      <button
                        type="button"
                        className="button secondary"
                        disabled={busy || !canManage}
                        onClick={() => void handleCreateEvaluator(true)}
                      >
                        Confirmar homônimo e cadastrar avaliador
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </fieldset>

          {/* SEÇÃO 3: DADOS DA SESSÃO */}
          <fieldset className="prep-section-card">
            <legend className="prep-section-header">
              <span className="step-number-badge">3</span>
              <div>
                <h4 className="prep-section-title">Dados da Sessão</h4>
                <p className="prep-section-subtitle">
                  Parâmetros de execução da tarefa cognitiva e identificador da visita.
                </p>
              </div>
            </legend>

            <div className="prep-section-content">
              <div className="prep-session-grid">
                {/* Instrumento */}
                <div className="prep-field-block">
                  <label htmlFor="session-test-code" className="prep-field-label">
                    Instrumento
                  </label>
                  <select
                    id="session-test-code"
                    value={testCode}
                    disabled={busy}
                    className="prep-select"
                    onChange={event => {
                      setTestCode(event.target.value)
                      setReviewing(false)
                    }}
                  >
                    <option value="stroop_go_nogo_ptbr">
                      Stroop Go/No-Go (stroop_go_nogo_ptbr · v0.2.2-web.1)
                    </option>
                  </select>
                  <span className="prep-field-hint">Tarefa oficial de correspondência e inibição.</span>
                </div>

                {/* Código do Participante */}
                <div className="prep-field-block">
                  <label htmlFor="session-participant" className="prep-field-label">
                    Código do participante
                  </label>
                  <div className="prep-participant-code-wrap">
                    <input
                      ref={participantInput}
                      id="session-participant"
                      required
                      maxLength={64}
                      value={selectedPatient ? selectedPatient.participant_code : participant}
                      readOnly={!!selectedPatient}
                      disabled={busy}
                      autoComplete="off"
                      className={`prep-text-input ${selectedPatient ? 'readonly-field' : ''}`}
                      aria-invalid={!!errors.participant}
                      aria-describedby={errors.participant ? 'session-participant-error' : undefined}
                      onChange={event => {
                        if (!selectedPatient) {
                          setParticipant(event.target.value)
                          setReviewing(false)
                        }
                      }}
                    />
                    {selectedPatient && (
                      <span className="prep-field-badge success" title="Código vinculado ao cadastro central">
                        Vínculo PAT ativo
                      </span>
                    )}
                  </div>
                  {errors.participant && (
                    <p id="session-participant-error" role="alert" className="notice prep-field-error">
                      {errors.participant}
                    </p>
                  )}
                  <span className="prep-field-hint">
                    {selectedPatient
                      ? 'Preenchido automaticamente pelo paciente selecionado.'
                      : 'Identificador alfanumérico para controle no projeto.'}
                  </span>
                </div>

                {/* Iniciais na Sessão */}
                <div className="prep-field-block">
                  <label htmlFor="session-initials" className="prep-field-label">
                    Iniciais na sessão
                  </label>
                  <input
                    id="session-initials"
                    maxLength={16}
                    value={initials}
                    disabled={busy}
                    autoComplete="off"
                    placeholder="Ex.: ACS"
                    className="prep-text-input"
                    aria-invalid={!!errors.initials}
                    aria-describedby={errors.initials ? 'session-initials-error' : undefined}
                    onChange={event => {
                      setInitials(event.target.value.toUpperCase())
                      setReviewing(false)
                    }}
                  />
                  {errors.initials && (
                    <p id="session-initials-error" role="alert" className="notice prep-field-error">
                      {errors.initials}
                    </p>
                  )}
                  <span className="prep-field-hint">Até 16 letras para conferência (sem acentos).</span>
                </div>

                {/* Visita da Sessão */}
                <div className="prep-field-block">
                  <label htmlFor="session-visit" className="prep-field-label">
                    Visita da sessão
                  </label>
                  <input
                    ref={visitInput}
                    id="session-visit"
                    required
                    maxLength={64}
                    value={visit}
                    disabled={busy}
                    autoComplete="off"
                    placeholder="Ex.: V1, V2, T1, T2..."
                    className="prep-text-input"
                    aria-invalid={!!errors.visit}
                    aria-describedby={errors.visit ? 'session-visit-error' : undefined}
                    onChange={event => {
                      setVisit(event.target.value)
                      setReviewing(false)
                    }}
                  />
                  {errors.visit && (
                    <p id="session-visit-error" role="alert" className="notice prep-field-error">
                      {errors.visit}
                    </p>
                  )}
                  <span className="prep-field-hint">Identificação do momento longitudinal ou coleta.</span>
                </div>
              </div>
            </div>
          </fieldset>

          {/* SEÇÃO 4: MODALIDADE */}
          <fieldset className="prep-section-card">
            <legend className="prep-section-header">
              <span className="step-number-badge">4</span>
              <div>
                <h4 className="prep-section-title">Modalidade de Aplicação</h4>
                <p className="prep-section-subtitle">
                  Selecione como a avaliação será executada pelo participante.
                </p>
              </div>
            </legend>

            <div className="prep-section-content">
              <div className="mode-selection-grid prep-mode-grid">
                <button
                  type="button"
                  className={`mode-card ${applicationMode === 'presencial' ? 'active' : ''}`}
                  onClick={() => setApplicationMode('presencial')}
                  aria-pressed={applicationMode === 'presencial'}
                >
                  <div className="mode-card-header">
                    <span className="mode-card-title">🏢 Presencial (Iniciar Agora)</span>
                    <span className="mode-card-badge">Local</span>
                  </div>
                  <p className="mode-card-desc">
                    Aplicação direta neste computador/navegador. Ideal para consultório, laboratório ou aplicação assistida.
                  </p>
                </button>

                <button
                  type="button"
                  className={`mode-card ${applicationMode === 'remota' ? 'active' : ''}`}
                  onClick={() => setApplicationMode('remota')}
                  aria-pressed={applicationMode === 'remota'}
                >
                  <div className="mode-card-header">
                    <span className="mode-card-title">🌐 Remota (Link Único)</span>
                    <span className="mode-card-badge">À Distância</span>
                  </div>
                  <p className="mode-card-desc">
                    Emite convite com código criptográfico de uso único para envio ao participante realizar no seu próprio dispositivo.
                  </p>
                </button>
              </div>
            </div>
          </fieldset>

          {/* SEÇÃO 5: REVISAR E CONFIRMAR */}
          <fieldset className="prep-section-card prep-section-confirm">
            <legend className="prep-section-header">
              <span className="step-number-badge">5</span>
              <div>
                <h4 className="prep-section-title">Revisar e Confirmar</h4>
                <p className="prep-section-subtitle">
                  Confira os parâmetros informados antes de gerar a sessão ou emitir o convite seguro.
                </p>
              </div>
            </legend>

            <div className="prep-section-content">
              <div className="prep-confirm-bar">
                <div className="prep-confirm-summary-pill">
                  <span>Modalidade: <strong>{applicationMode === 'presencial' ? '🏢 Presencial' : '🌐 Remota'}</strong></span>
                  <span>Paciente: <strong>{selectedPatient ? selectedPatient.full_name : participant || 'Não definido'}</strong></span>
                  <span>Visita: <strong>{visit || 'Não informada'}</strong></span>
                </div>

                <div className="prep-confirm-buttons">
                  <button
                    type="button"
                    className="button secondary"
                    disabled={busy}
                    onClick={handleReview}
                  >
                    Revisar preparação
                  </button>
                  <button
                    className="button primary"
                    disabled={busy || !canManage}
                    type="submit"
                    title={!canManage ? 'Seu perfil de consulta não permite gerar convites.' : undefined}
                  >
                    {busy
                      ? (applicationMode === 'presencial' ? 'Iniciando avaliação…' : 'Gerando convite…')
                      : applicationMode === 'presencial'
                        ? 'Iniciar avaliação'
                        : 'Gerar convite'}
                  </button>
                </div>
              </div>

              {/* Painel detalhado de conferência */}
              {reviewing && (
                <div
                  role="region"
                  aria-label="Resumo para conferência"
                  className="preparation-review-card prep-review-box"
                >
                  <div className="prep-review-header">
                    <h4 className="prep-review-title">Conferência dos dados da sessão</h4>
                    <span className="prep-review-tag">Pronto para emissão</span>
                  </div>

                  <dl className="prep-review-dl">
                    <div className="prep-review-item">
                      <dt>Projeto de Pesquisa</dt>
                      <dd>{project.code} — {project.name}</dd>
                    </div>
                    <div className="prep-review-item">
                      <dt>Modalidade</dt>
                      <dd>
                        {applicationMode === 'presencial'
                          ? '🏢 Presencial (Iniciar Agora)'
                          : '🌐 Remota (Código de uso único)'}
                      </dd>
                    </div>
                    <div className="prep-review-item">
                      <dt>Paciente</dt>
                      <dd>
                        {selectedPatient
                          ? `${selectedPatient.full_name} (${selectedPatient.participant_code})`
                          : participant}
                      </dd>
                    </div>
                    <div className="prep-review-item">
                      <dt>Iniciais na Sessão</dt>
                      <dd>{initials || '—'}</dd>
                    </div>
                    <div className="prep-review-item">
                      <dt>Avaliador Responsável</dt>
                      <dd>
                        {selectedEvaluator
                          ? `${selectedEvaluator.full_name} (${selectedEvaluator.evaluator_code})`
                          : profile.user_id}
                      </dd>
                    </div>
                    <div className="prep-review-item">
                      <dt>Visita / Momento</dt>
                      <dd>{visit}</dd>
                    </div>
                    <div className="prep-review-item">
                      <dt>Instrumento e Versão</dt>
                      <dd>{testCode} · 0.2.2-web.1</dd>
                    </div>
                  </dl>

                  <div className="prep-review-actions">
                    <button
                      type="button"
                      className="button primary"
                      disabled={busy || !canManage}
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
          </fieldset>
        </form>
      )}

      {/* TELA DE SUCESSO APÓS EMISSÃO */}
      {saved && (
        <div className="invitation-success-card prep-success-view" role="region" aria-label="Convite criado com sucesso">
          <div className="prep-success-header">
            <span className="prep-success-icon" aria-hidden="true">✓</span>
            <div>
              <h4 className="prep-success-title">Convite criado com sucesso</h4>
              <p className="prep-success-meta">
                Participante: <strong>{saved.participant}</strong> · Visita: <strong>{saved.visit}</strong>
              </p>
            </div>
          </div>

          {saved.summary && (
            <div className="prep-success-summary-box">
              <p>
                <strong>Paciente:</strong> {saved.summary.participant_name} ({saved.summary.participant_code})
                {' · '}
                <strong>Iniciais:</strong> {saved.summary.initials ?? '—'}
                {' · '}
                <strong>Avaliador:</strong> {saved.summary.evaluator_name} ({saved.summary.evaluator_code})
              </p>
              <p>
                <strong>Instrumento:</strong> {saved.summary.test_code} ({saved.summary.test_version})
                {' · '}
                <strong>Sessão ID:</strong> {saved.invitation.session_id}
              </p>
            </div>
          )}

          <div className="prep-code-box">
            <span className="prep-code-label">Código de uso único:</span>
            <output aria-label="Código do convite" className="invitation-code-display prep-code-text">
              {saved.invitation.code}
            </output>
            <span className="prep-code-expiry">Expira em: {saved.invitation.expires_at} (UTC)</span>
          </div>

          <p className="quiet prep-success-notice">
            Entregue este código ao participante pelo canal seguro apropriado. O código de acesso só é exibido nesta confirmação e não fica gravado na URL da prática.
          </p>

          <div className="invitation-actions-row prep-success-actions">
            <a
              className="button primary"
              href="/pratica"
              target="_blank"
              rel="noopener noreferrer"
            >
              Abrir prática em outra aba ↗
            </a>
            <button
              type="button"
              className="button secondary"
              onClick={() => {
                void navigator.clipboard.writeText(saved.invitation.code)
              }}
            >
              📋 Copiar código
            </button>
            <button
              className="button secondary button-danger"
              disabled={busy || !canManage}
              onClick={() => void revoke()}
            >
              {busy ? 'Revogando…' : 'Revogar convite'}
            </button>
          </div>
        </div>
      )}

      {revoked && (
        <div className="prep-status-banner info">
          <p role="status">
            Revogação confirmada. O convite foi cancelado e não permite iniciar ou continuar a sessão.
          </p>
        </div>
      )}

      {(saved || unknownCreation || revoked) && (
        <div className="prep-reset-row">
          <p className="quiet">
            Preparar outra sessão limpa a tela para configurar um novo participante e visita sem afetar convites emitidos anteriormente.
          </p>
          <button className="button secondary" disabled={busy} onClick={reset}>
            Preparar outra sessão
          </button>
        </div>
      )}
    </section>
  )
}
