import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import type { ProfessionalProfile } from '../api/client'
import type { Project } from '../api/assessments'
import { relinkAssessment } from '../api/assessments'
import {
  checkDuplicatePatients,
  createPatient,
  deriveInitials,
  getPatient,
  listPatients,
  updatePatient,
} from '../api/patients'
import type {
  DuplicatePatientCandidate,
  PatientDetail,
  PatientRecord,
} from '../api/patients'

type FilterStatus = 'all' | 'true' | 'false'

export function PatientsPanel({
  profile,
  project: _project,
}: {
  profile: ProfessionalProfile
  project?: Project | null
}) {
  const [patients, setPatients] = useState<PatientRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)

  // Filtros
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all')

  // Ficha de detalhe
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [detail, setDetail] = useState<PatientDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [updatingStatus, setUpdatingStatus] = useState(false)

  // Formulário de novo paciente
  const [showCreate, setShowCreate] = useState(false)
  const [fullName, setFullName] = useState('')
  const [initials, setInitials] = useState('')
  const [initialsCustom, setInitialsCustom] = useState(false)
  const [disambiguationNote, setDisambiguationNote] = useState('')
  const [confirmHomonym, setConfirmHomonym] = useState(false)
  const [homonymCandidates, setHomonymCandidates] = useState<DuplicatePatientCandidate[] | null>(null)
  const [checkingDuplicates, setCheckingDuplicates] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  // Edição cadastral
  const [isEditing, setIsEditing] = useState(false)
  const [editFullName, setEditFullName] = useState('')
  const [editInitials, setEditInitials] = useState('')
  const [editDisambiguationNote, setEditDisambiguationNote] = useState('')
  const [editReasonCode, setEditReasonCode] = useState('correcao_cadastral')
  const [editSubmitting, setEditSubmitting] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)

  // Correção auditada de vínculo (relink)
  const [relinkingAssessment, setRelinkingAssessment] = useState<{
    assessment_id: string
    project_id: string
  } | null>(null)
  const [relinkNewPatientId, setRelinkNewPatientId] = useState('')
  const [relinkNewEvaluatorId, setRelinkNewEvaluatorId] = useState('')
  const [relinkReasonCode, setRelinkReasonCode] = useState('correcao_erro_humano_vinculo')
  const [relinkSubmitting, setRelinkSubmitting] = useState(false)
  const [relinkError, setRelinkError] = useState<string | null>(null)

  const detailPanelRef = useRef<HTMLElement>(null)

  // Carrega listagem de pacientes
  useEffect(() => {
    const io = new AbortController()
    setLoading(true)
    setError(null)
    void listPatients(
      {
        search: search.trim() || undefined,
        active: statusFilter,
        page,
        page_size: pageSize,
      },
      io.signal,
    ).then(
      res => {
        if (!io.signal.aborted) {
          setPatients(res.items)
          setTotal(res.total)
        }
      },
      err => {
        if (!io.signal.aborted) {
          setError(apiErrorMessage(err))
        }
      },
    ).finally(() => {
      if (!io.signal.aborted) setLoading(false)
    })
    return () => io.abort()
  }, [search, statusFilter, page, pageSize, revision])

  // Carrega detalhe do paciente selecionado
  useEffect(() => {
    if (!selectedPatientId) {
      setDetail(null)
      return
    }
    const io = new AbortController()
    setDetailLoading(true)
    setDetailError(null)
    void getPatient(selectedPatientId, io.signal).then(
      res => {
        if (!io.signal.aborted) {
          setDetail(res)
        }
      },
      err => {
        if (!io.signal.aborted) {
          setDetailError(apiErrorMessage(err))
        }
      },
    ).finally(() => {
      if (!io.signal.aborted) setDetailLoading(false)
    })
    return () => io.abort()
  }, [selectedPatientId, revision])

  useEffect(() => {
    if (detail) {
      detailPanelRef.current?.focus()
    }
  }, [detail])

  function handleNameChange(value: string) {
    setFullName(value)
    if (!initialsCustom) {
      setInitials(deriveInitials(value))
    }
    setHomonymCandidates(null)
    setConfirmHomonym(false)
  }

  async function checkHomonyms(name: string) {
    const trimmed = name.trim()
    if (trimmed.length < 2 || trimmed.length > 120) return
    setCheckingDuplicates(true)
    try {
      const res = await checkDuplicatePatients(trimmed)
      if (res.candidates.length > 0) {
        setHomonymCandidates(res.candidates)
      } else {
        setHomonymCandidates(null)
      }
    } catch {
      // Ignora falhas de prefetch
    } finally {
      setCheckingDuplicates(false)
    }
  }

  async function handleCreatePatient(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setCreateError(null)
    try {
      const created = await createPatient(
        {
          full_name: fullName,
          initials: initials || null,
          disambiguation_note: disambiguationNote || null,
          confirm_homonym: confirmHomonym,
        },
        profile.csrf_token,
      )
      setNotice(`Paciente cadastrado com sucesso! Código gerado: ${created.participant_code}`)
      setShowCreate(false)
      setFullName('')
      setInitials('')
      setInitialsCustom(false)
      setDisambiguationNote('')
      setHomonymCandidates(null)
      setConfirmHomonym(false)
      setRevision(v => v + 1)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setCreateError(
          'Foram identificados possíveis homônimos já cadastrados. Confira a lista abaixo e selecione a confirmação consciente para prosseguir.',
        )
        void checkHomonyms(fullName)
      } else {
        setCreateError(apiErrorMessage(err))
      }
    } finally {
      setSubmitting(false)
    }
  }

  async function handleToggleActive(target: PatientRecord) {
    const action = target.active ? 'inativação' : 'reativação'
    const confirmMessage = target.active
      ? `Confirma a inativação lógica do paciente ${target.participant_code} (${target.full_name})? Avaliações históricas permanecerão preservadas.`
      : `Confirma a reativação do paciente ${target.participant_code} (${target.full_name})?`
    if (!window.confirm(confirmMessage)) return

    setUpdatingStatus(true)
    try {
      await updatePatient(
        target.id,
        {
          active: !target.active,
          reason_code: target.active ? 'inativacao_cadastral' : 'reativacao_cadastral',
        },
        profile.csrf_token,
      )
      setNotice(`Paciente ${target.participant_code} atualizado (${action} concluída).`)
      setRevision(v => v + 1)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setUpdatingStatus(false)
    }
  }

  function startEditing(target: PatientRecord | PatientDetail) {
    setEditFullName(target.full_name)
    setEditInitials(target.initials ?? '')
    setEditDisambiguationNote(target.disambiguation_note ?? '')
    setEditReasonCode('correcao_cadastral')
    setEditError(null)
    setIsEditing(true)
  }

  async function handleSaveEdit(e: FormEvent) {
    e.preventDefault()
    if (!detail) return
    const reason = editReasonCode.trim()
    if (!reason) {
      setEditError('Informe o motivo da alteração cadastral.')
      return
    }
    setEditSubmitting(true)
    setEditError(null)
    try {
      await updatePatient(
        detail.id,
        {
          full_name: editFullName.trim(),
          initials: editInitials.trim() || null,
          disambiguation_note: editDisambiguationNote.trim() || null,
          reason_code: reason,
        },
        profile.csrf_token,
      )
      setNotice(`Cadastro de ${editFullName.trim()} atualizado com sucesso (evento auditado).`)
      setIsEditing(false)
      setRevision(v => v + 1)
      const refreshed = await getPatient(detail.id)
      setDetail(refreshed)
    } catch (err) {
      setEditError(apiErrorMessage(err))
    } finally {
      setEditSubmitting(false)
    }
  }

  async function handleConfirmRelink(e: FormEvent) {
    e.preventDefault()
    if (!relinkingAssessment || !detail) return
    const reason = relinkReasonCode.trim()
    if (!reason) {
      setRelinkError('Informe o motivo da correção de vínculo.')
      return
    }
    if (!relinkNewPatientId.trim() && !relinkNewEvaluatorId.trim()) {
      setRelinkError('Informe pelo menos um novo ID de paciente ou avaliador.')
      return
    }
    setRelinkSubmitting(true)
    setRelinkError(null)
    try {
      await relinkAssessment(
        relinkingAssessment.project_id,
        relinkingAssessment.assessment_id,
        {
          patient_id: relinkNewPatientId.trim() || undefined,
          evaluator_id: relinkNewEvaluatorId.trim() || undefined,
          reason_code: reason,
        },
        profile.csrf_token,
      )
      setNotice(
        `Vínculo da avaliação ${relinkingAssessment.assessment_id} corrigido com sucesso (evento auditado).`,
      )
      setRelinkingAssessment(null)
      setRelinkNewPatientId('')
      setRelinkNewEvaluatorId('')
      setRelinkReasonCode('correcao_erro_humano_vinculo')
      setRevision(v => v + 1)
      const refreshed = await getPatient(detail.id)
      setDetail(refreshed)
    } catch (err) {
      setRelinkError(apiErrorMessage(err))
    } finally {
      setRelinkSubmitting(false)
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="patients-panel registry-panel" aria-label="Módulo Pacientes">
      <div className="panel-header">
        <div>
          <h2>Pacientes</h2>
          <p className="quiet">
            Cadastro centralizado de participantes/pacientes (ADR-007). Código estável PAT-... gerado
            automaticamente e reutilizável entre projetos, visitas e avaliações.
          </p>
        </div>
        {profile.role !== 'consulta' && (
          <button
            type="button"
            className="button primary"
            onClick={() => setShowCreate(prev => !prev)}
            aria-expanded={showCreate}
          >
            {showCreate ? 'Cancelar cadastro' : '+ Cadastrar novo paciente'}
          </button>
        )}
      </div>

      {notice && (
        <p role="status" className="notice">
          {notice}
        </p>
      )}

      {/* Formulário de criação de paciente */}
      {showCreate && (
        <section className="content-card patient-form-card" aria-label="Cadastro de novo paciente">
          <h3>Novo cadastro de paciente</h3>
          <p className="quiet">
            Informe os dados nominais. O código PAT-... será atribuído pelo sistema de forma sequencial e
            estável. Homônimos são aceitos mediante confirmação consciente.
          </p>
          <form onSubmit={e => void handleCreatePatient(e)}>
            <div className="form-field">
              <label htmlFor="patient-fullname">
                Nome completo <strong>*</strong>
              </label>
              <input
                id="patient-fullname"
                type="text"
                required
                minLength={2}
                maxLength={120}
                value={fullName}
                onChange={e => handleNameChange(e.target.value)}
                onBlur={e => void checkHomonyms(e.target.value)}
                placeholder="Ex.: Maria de Souza Oliveira"
                autoComplete="off"
              />
            </div>

            <div className="form-field">
              <label htmlFor="patient-initials">
                Iniciais (auxílio visual de conferência)
              </label>
              <input
                id="patient-initials"
                type="text"
                maxLength={16}
                value={initials}
                onChange={e => {
                  setInitialsCustom(true)
                  setInitials(e.target.value.toUpperCase())
                }}
                placeholder="Ex.: MSO"
                autoComplete="off"
              />
              <span className="quiet">
                {initialsCustom
                  ? 'Iniciais personalizadas manualmente.'
                  : 'Iniciais derivadas automaticamente a partir do nome.'}
              </span>
            </div>

            <div className="form-field">
              <label htmlFor="patient-disambiguation">
                Anotação de desambiguação / metadados autorizados (opcional)
              </label>
              <input
                id="patient-disambiguation"
                type="text"
                maxLength={160}
                value={disambiguationNote}
                onChange={e => setDisambiguationNote(e.target.value)}
                placeholder="Ex.: Grupo A - Ambulatório Central"
                autoComplete="off"
              />
            </div>

            {checkingDuplicates && <p role="status" className="quiet">Verificando correspondências existentes…</p>}

            {homonymCandidates && homonymCandidates.length > 0 && (
              <div role="region" aria-label="Aviso de homônimos" className="homonym-alert notice">
                <h4>Atenção: foram encontrados pacientes com nome semelhante já cadastrados</h4>
                <ul className="homonym-list">
                  {homonymCandidates.map(c => (
                    <li key={c.id}>
                      <strong className="tabular-nums">{c.participant_code}</strong>: {c.full_name}{' '}
                      {c.initials && `(${c.initials})`} —{' '}
                      <span>{c.active ? 'Ativo' : 'Inativo'}</span>{' '}
                      {c.disambiguation_note && <em>[{c.disambiguation_note}]</em>}
                    </li>
                  ))}
                </ul>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={confirmHomonym}
                    onChange={e => setConfirmHomonym(e.target.checked)}
                  />
                  <span>
                    Confirmo conscientemente que este é um <strong>novo paciente homônimo</strong> diferente
                    dos listados acima.
                  </span>
                </label>
              </div>
            )}

            {createError && (
              <p role="alert" className="notice error">
                {createError}
              </p>
            )}

            <div className="form-actions">
              <button
                type="submit"
                className="button primary"
                disabled={submitting || (homonymCandidates !== null && homonymCandidates.length > 0 && !confirmHomonym)}
              >
                {submitting ? 'Salvando cadastro…' : 'Confirmar e salvar paciente'}
              </button>
              <button
                type="button"
                className="button secondary"
                onClick={() => {
                  setShowCreate(false)
                  setCreateError(null)
                  setHomonymCandidates(null)
                }}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Barra de busca e filtros */}
      <div className="filter-bar">
        <label>
          Buscar pacientes
          <input
            type="search"
            value={search}
            onChange={e => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Nome, código PAT-... ou iniciais"
          />
        </label>

        <label>
          Status
          <select
            value={statusFilter}
            onChange={e => {
              setStatusFilter(e.target.value as FilterStatus)
              setPage(1)
            }}
          >
            <option value="all">Todos</option>
            <option value="true">Apenas ativos</option>
            <option value="false">Apenas inativos</option>
          </select>
        </label>

        <button
          type="button"
          className="button secondary"
          onClick={() => setRevision(v => v + 1)}
          disabled={loading}
        >
          {loading ? 'Atualizando…' : 'Atualizar lista'}
        </button>
      </div>

      {error && (
        <p role="alert" className="notice error">
          {error}
        </p>
      )}

      {/* Tabela de listagem */}
      {loading && !patients.length ? (
        <p role="status">Carregando lista de pacientes…</p>
      ) : patients.length === 0 ? (
        <p role="status">Nenhum paciente encontrado para os filtros selecionados.</p>
      ) : (
        <div className="table-scroll">
          <table aria-label="Lista de pacientes cadastrados">
            <caption>
              Pacientes cadastrados ({total} no total) — Página {page} de {totalPages}
            </caption>
            <thead>
              <tr>
                <th scope="col">Código</th>
                <th scope="col">Nome completo</th>
                <th scope="col">Iniciais</th>
                <th scope="col">Desambiguação</th>
                <th scope="col">Projetos</th>
                <th scope="col">Avaliações</th>
                <th scope="col">Status</th>
                <th scope="col">Ações</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id}>
                  <td className="tabular-nums">
                    <strong>{p.participant_code}</strong>
                  </td>
                  <td>{p.full_name}</td>
                  <td>{p.initials ?? '—'}</td>
                  <td>{p.disambiguation_note ?? '—'}</td>
                  <td className="tabular-nums">{p.project_count}</td>
                  <td className="tabular-nums">{p.assessment_count}</td>
                  <td>
                    <span className={`status-badge ${p.active ? 'status-active' : 'status-inactive'}`}>
                      {p.active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="button secondary"
                      onClick={() => setSelectedPatientId(p.id)}
                      aria-label={`Ver ficha de ${p.full_name} (${p.participant_code})`}
                    >
                      Ver ficha
                    </button>
                    {profile.role !== 'consulta' && (
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => void handleToggleActive(p)}
                        disabled={updatingStatus}
                        aria-label={`${p.active ? 'Inativar' : 'Reativar'} paciente ${p.participant_code}`}
                        style={{ marginLeft: 6 }}
                      >
                        {p.active ? 'Inativar' : 'Reativar'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Paginação */}
      {totalPages > 1 && (
        <nav aria-label="Paginação de pacientes" className="pagination-bar">
          <button
            type="button"
            className="button secondary"
            disabled={page <= 1 || loading}
            onClick={() => setPage(p => Math.max(1, p - 1))}
          >
            ← Anterior
          </button>
          <span className="quiet tabular-nums">
            Página {page} de {totalPages}
          </span>
          <button
            type="button"
            className="button secondary"
            disabled={page >= totalPages || loading}
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          >
            Próxima →
          </button>
        </nav>
      )}

      {/* Ficha detalhada do paciente */}
      {selectedPatientId && (
        <section
          ref={detailPanelRef}
          tabIndex={-1}
          className="assessment-detail patient-detail"
          aria-label="Ficha detalhada do paciente"
        >
          <div className="panel-header">
            <h3>Ficha cadastral do paciente</h3>
            <div className="panel-actions">
              {profile.role !== 'consulta' && (
                <button
                  type="button"
                  className="button secondary"
                  onClick={() => (isEditing ? setIsEditing(false) : startEditing(detail!))}
                  disabled={!detail}
                  aria-expanded={isEditing}
                >
                  {isEditing ? 'Cancelar edição' : 'Editar cadastro'}
                </button>
              )}
              <button
                type="button"
                className="button secondary"
                onClick={() => {
                  setSelectedPatientId(null)
                  setIsEditing(false)
                  setRelinkingAssessment(null)
                }}
              >
                Fechar ficha
              </button>
            </div>
          </div>

          {detailLoading && <p role="status">Carregando dados da ficha…</p>}
          {detailError && <p role="alert" className="notice error">{detailError}</p>}

          {detail && (
            <>
              {/* Formulário de edição cadastral */}
              {isEditing && (
                <section
                  className="content-card patient-edit-card"
                  aria-label="Edição de cadastro do paciente"
                  style={{ marginBottom: 16 }}
                >
                  <h4>Editar dados cadastrais do paciente</h4>
                  <p className="quiet">
                    As alterações cadastrais são registradas com trilha auditável em{' '}
                    <code>web_registry_audit_events</code> preservando todos os vínculos históricos.
                  </p>
                  <form onSubmit={e => void handleSaveEdit(e)}>
                    <div className="form-field">
                      <label htmlFor="edit-patient-fullname">
                        Nome completo <strong>*</strong>
                      </label>
                      <input
                        id="edit-patient-fullname"
                        type="text"
                        required
                        minLength={2}
                        maxLength={120}
                        value={editFullName}
                        onChange={e => setEditFullName(e.target.value)}
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="edit-patient-initials">Iniciais</label>
                      <input
                        id="edit-patient-initials"
                        type="text"
                        maxLength={16}
                        value={editInitials}
                        onChange={e => setEditInitials(e.target.value.toUpperCase())}
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="edit-patient-disambiguation">
                        Desambiguação / Anotação de coorte
                      </label>
                      <input
                        id="edit-patient-disambiguation"
                        type="text"
                        maxLength={160}
                        value={editDisambiguationNote}
                        onChange={e => setEditDisambiguationNote(e.target.value)}
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="edit-patient-reason">
                        Motivo da alteração cadastral <strong>*</strong>
                      </label>
                      <input
                        id="edit-patient-reason"
                        type="text"
                        required
                        maxLength={120}
                        value={editReasonCode}
                        onChange={e => setEditReasonCode(e.target.value)}
                        placeholder="Ex.: correcao_ortografica, ajuste_cadastral"
                        autoComplete="off"
                      />
                    </div>

                    {editError && (
                      <p role="alert" className="notice error">
                        {editError}
                      </p>
                    )}

                    <div className="form-actions">
                      <button type="submit" className="button primary" disabled={editSubmitting}>
                        {editSubmitting ? 'Salvando alterações…' : 'Salvar alterações'}
                      </button>
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => setIsEditing(false)}
                      >
                        Cancelar
                      </button>
                    </div>
                  </form>
                </section>
              )}

              {/* Formulário de correção auditada de vínculo */}
              {relinkingAssessment && (
                <section
                  className="content-card relink-card notice"
                  aria-label="Correção auditada de vínculo de avaliação"
                  style={{ marginBottom: 16 }}
                >
                  <h4>
                    Correção auditada de vínculo — Avaliação <code>{relinkingAssessment.assessment_id}</code>
                  </h4>
                  <p className="quiet">
                    Procedimento administrativo auditado para retificar erro humano na vinculação de
                    paciente ou avaliador, sem apagar resultados científicos ou tentativas.
                  </p>
                  <form onSubmit={e => void handleConfirmRelink(e)}>
                    <div className="form-field">
                      <label htmlFor="relink-new-patient">
                        ID UUID do novo paciente (deixe em branco se mantiver o paciente atual)
                      </label>
                      <input
                        id="relink-new-patient"
                        type="text"
                        value={relinkNewPatientId}
                        onChange={e => setRelinkNewPatientId(e.target.value.trim())}
                        placeholder="Ex.: 00000000-0000-4000-8000-000000000001"
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="relink-new-evaluator">
                        ID UUID do novo avaliador responsável (opcional)
                      </label>
                      <input
                        id="relink-new-evaluator"
                        type="text"
                        value={relinkNewEvaluatorId}
                        onChange={e => setRelinkNewEvaluatorId(e.target.value.trim())}
                        placeholder="Ex.: 00000000-0000-4000-8000-000000000101"
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="relink-reason">
                        Motivo da retificação de vínculo <strong>*</strong>
                      </label>
                      <input
                        id="relink-reason"
                        type="text"
                        required
                        maxLength={120}
                        value={relinkReasonCode}
                        onChange={e => setRelinkReasonCode(e.target.value)}
                        placeholder="Ex.: correcao_erro_humano_vinculo"
                        autoComplete="off"
                      />
                    </div>

                    {relinkError && (
                      <p role="alert" className="notice error">
                        {relinkError}
                      </p>
                    )}

                    <div className="form-actions">
                      <button type="submit" className="button primary" disabled={relinkSubmitting}>
                        {relinkSubmitting ? 'Processando revinculação…' : 'Confirmar revinculação auditada'}
                      </button>
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => setRelinkingAssessment(null)}
                      >
                        Cancelar
                      </button>
                    </div>
                  </form>
                </section>
              )}

              <dl className="assessment-metadata">
                <div>
                  <dt>Código do paciente</dt>
                  <dd className="tabular-nums"><strong>{detail.participant_code}</strong></dd>
                </div>
                <div>
                  <dt>Nome completo</dt>
                  <dd>{detail.full_name}</dd>
                </div>
                <div>
                  <dt>Iniciais</dt>
                  <dd>{detail.initials ?? 'Não informadas'}</dd>
                </div>
                <div>
                  <dt>Desambiguação / Anotação</dt>
                  <dd>{detail.disambiguation_note ?? 'Nenhuma anotação'}</dd>
                </div>
                <div>
                  <dt>Status cadastral</dt>
                  <dd>
                    <span className={`status-badge ${detail.active ? 'status-active' : 'status-inactive'}`}>
                      {detail.active ? 'Ativo' : 'Inativo (lógico)'}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Data de cadastro</dt>
                  <dd className="tabular-nums">{detail.created_at}</dd>
                </div>
                <div>
                  <dt>Última atualização</dt>
                  <dd className="tabular-nums">{detail.updated_at}</dd>
                </div>
                <div>
                  <dt>Última avaliação</dt>
                  <dd className="tabular-nums">{detail.last_assessment_at ?? 'Nenhuma avaliação realizada'}</dd>
                </div>
              </dl>

              {/* Projetos vinculados */}
              <h4>Projetos vinculados ({detail.projects.length})</h4>
              {detail.projects.length === 0 ? (
                <p className="quiet">Este paciente ainda não possui vínculos com projetos ativos.</p>
              ) : (
                <div className="table-scroll">
                  <table>
                    <caption>Vínculos do paciente com projetos</caption>
                    <thead>
                      <tr>
                        <th scope="col">Projeto</th>
                        <th scope="col">Código</th>
                        <th scope="col">Código no projeto</th>
                        <th scope="col">Data do vínculo</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.projects.map(proj => (
                        <tr key={proj.project_id}>
                          <td>{proj.project_name}</td>
                          <td className="tabular-nums">{proj.project_code}</td>
                          <td className="tabular-nums">{proj.participant_code ?? '—'}</td>
                          <td className="tabular-nums">{proj.created_at ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Visitas registradas */}
              <h4>Visitas registradas ({detail.visits.length})</h4>
              {detail.visits.length === 0 ? (
                <p className="quiet">Nenhuma visita registrada para este paciente.</p>
              ) : (
                <div className="table-scroll">
                  <table>
                    <caption>Visitas do paciente</caption>
                    <thead>
                      <tr>
                        <th scope="col">Projeto</th>
                        <th scope="col">Rótulo da visita</th>
                        <th scope="col">Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.visits.map(v => (
                        <tr key={v.visit_uuid}>
                          <td className="tabular-nums">{v.project_code}</td>
                          <td>{v.visit}</td>
                          <td className="tabular-nums">{v.created_at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Sessões e convites preparados */}
              <h4>Sessões e convites preparados ({detail.sessions?.length ?? 0})</h4>
              {!detail.sessions || detail.sessions.length === 0 ? (
                <p className="quiet">Nenhuma sessão preparada ou convite registrado para este paciente.</p>
              ) : (
                <div className="table-scroll">
                  <table aria-label="Sessões e convites preparados para o paciente">
                    <caption>Sessões preparadas para o paciente</caption>
                    <thead>
                      <tr>
                        <th scope="col">Projeto</th>
                        <th scope="col">Visita</th>
                        <th scope="col">Avaliador</th>
                        <th scope="col">Instrumento</th>
                        <th scope="col">Estado convite</th>
                        <th scope="col">Estado sessão</th>
                        <th scope="col">Criado em</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.sessions.map(s => (
                        <tr key={s.invitation_id}>
                          <td className="tabular-nums">{s.project_code}</td>
                          <td>{s.visit}</td>
                          <td className="tabular-nums">{s.evaluator_code ?? '—'}</td>
                          <td>{s.test_code}</td>
                          <td>
                            <span className="badge">{s.invitation_state}</span>
                          </td>
                          <td>
                            <span className="badge">{s.session_state ?? '—'}</span>
                          </td>
                          <td className="tabular-nums">{s.created_at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Histórico longitudinal de avaliações */}
              <h4>Histórico longitudinal de avaliações ({detail.assessments.length})</h4>
              {detail.assessments.length === 0 ? (
                <p className="quiet">Nenhuma avaliação experimental associada até o momento.</p>
              ) : (
                <div className="table-scroll">
                  <table aria-label="Histórico longitudinal de avaliações do paciente">
                    <caption>Avaliações realizadas pelo paciente</caption>
                    <thead>
                      <tr>
                        <th scope="col">ID da avaliação</th>
                        <th scope="col">Projeto</th>
                        <th scope="col">Instrumento</th>
                        <th scope="col">Versão</th>
                        <th scope="col">Visita</th>
                        <th scope="col">Data</th>
                        {profile.role !== 'consulta' && <th scope="col">Ações</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {detail.assessments.map(a => (
                        <tr key={a.assessment_id}>
                          <td className="tabular-nums">{a.assessment_id}</td>
                          <td className="tabular-nums">{a.project_code}</td>
                          <td>{a.test_code}</td>
                          <td className="tabular-nums">{a.test_version}</td>
                          <td>{a.visit}</td>
                          <td className="tabular-nums">{a.created_at}</td>
                          {profile.role !== 'consulta' && (
                            <td>
                              <button
                                type="button"
                                className="button secondary"
                                onClick={() => {
                                  setRelinkingAssessment({
                                    assessment_id: a.assessment_id,
                                    project_id: a.project_id,
                                  })
                                  setRelinkReasonCode('correcao_erro_humano_vinculo')
                                  setRelinkError(null)
                                }}
                                aria-label={`Corrigir vínculo da avaliação ${a.assessment_id}`}
                              >
                                Corrigir vínculo
                              </button>
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Trilha de auditoria cadastral */}
              <h4>Trilha de auditoria cadastral ({detail.audit_history?.length ?? 0})</h4>
              {!detail.audit_history || detail.audit_history.length === 0 ? (
                <p className="quiet">Nenhum evento de auditoria cadastral registrado.</p>
              ) : (
                <div className="table-scroll">
                  <table aria-label="Trilha de auditoria cadastral do paciente">
                    <caption>Eventos auditados em web_registry_audit_events</caption>
                    <thead>
                      <tr>
                        <th scope="col">Ação</th>
                        <th scope="col">Motivo</th>
                        <th scope="col">Entidade</th>
                        <th scope="col">Data / Hora</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.audit_history.map(ev => (
                        <tr key={ev.event_id}>
                          <td>
                            <strong>{ev.action}</strong>
                          </td>
                          <td>{ev.reason_code || '—'}</td>
                          <td>{ev.entity_type}</td>
                          <td className="tabular-nums">{ev.occurred_at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </section>
      )}
    </div>
  )
}
