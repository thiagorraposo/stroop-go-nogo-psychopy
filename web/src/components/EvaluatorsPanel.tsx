import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import type { ProfessionalProfile } from '../api/client'
import type { Project } from '../api/assessments'
import { relinkAssessment } from '../api/assessments'
import {
  createEvaluator,
  getEvaluator,
  listEvaluators,
  updateEvaluator,
} from '../api/evaluators'
import type {
  EvaluatorDetail,
  EvaluatorRecord,
} from '../api/evaluators'
import { deriveInitials } from '../api/patients'

type FilterStatus = 'all' | 'true' | 'false'

export function EvaluatorsPanel({
  profile,
  project: _project,
}: {
  profile: ProfessionalProfile
  project?: Project | null
}) {
  const [evaluators, setEvaluators] = useState<EvaluatorRecord[]>([])
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
  const [selectedEvaluatorId, setSelectedEvaluatorId] = useState<string | null>(null)
  const [detail, setDetail] = useState<EvaluatorDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [updatingStatus, setUpdatingStatus] = useState(false)

  // Formulário de novo avaliador
  const [showCreate, setShowCreate] = useState(false)
  const [fullName, setFullName] = useState('')
  const [initials, setInitials] = useState('')
  const [initialsCustom, setInitialsCustom] = useState(false)
  const [confirmHomonym, setConfirmHomonym] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  // Edição cadastral
  const [isEditing, setIsEditing] = useState(false)
  const [editFullName, setEditFullName] = useState('')
  const [editInitials, setEditInitials] = useState('')
  const [editReasonCode, setEditReasonCode] = useState('correcao_cadastral')
  const [editSubmitting, setEditSubmitting] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)

  // Correção auditada de vínculo (relink)
  const [relinkingAssessment, setRelinkingAssessment] = useState<{
    assessment_id: string
    project_id: string
  } | null>(null)
  const [relinkNewEvaluatorId, setRelinkNewEvaluatorId] = useState('')
  const [relinkNewPatientId, setRelinkNewPatientId] = useState('')
  const [relinkReasonCode, setRelinkReasonCode] = useState('correcao_erro_humano_vinculo')
  const [relinkSubmitting, setRelinkSubmitting] = useState(false)
  const [relinkError, setRelinkError] = useState<string | null>(null)

  const detailPanelRef = useRef<HTMLElement>(null)

  // Carrega listagem de avaliadores
  useEffect(() => {
    const io = new AbortController()
    setLoading(true)
    setError(null)
    void listEvaluators(
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
          setEvaluators(res.items)
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

  // Carrega detalhe do avaliador selecionado
  useEffect(() => {
    if (!selectedEvaluatorId) {
      setDetail(null)
      return
    }
    const io = new AbortController()
    setDetailLoading(true)
    setDetailError(null)
    void getEvaluator(selectedEvaluatorId, io.signal).then(
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
  }, [selectedEvaluatorId, revision])

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
  }

  async function handleCreateEvaluator(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setCreateError(null)
    try {
      const created = await createEvaluator(
        {
          full_name: fullName,
          initials: initials || null,
          confirm_homonym: confirmHomonym,
        },
        profile.csrf_token,
      )
      setNotice(`Avaliador cadastrado com sucesso! Código gerado: ${created.evaluator_code}`)
      setShowCreate(false)
      setFullName('')
      setInitials('')
      setInitialsCustom(false)
      setConfirmHomonym(false)
      setRevision(v => v + 1)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setCreateError(
          'Foi encontrado um avaliador com nome coincidente. Se confirmar tratar-se de profissional diferente, marque a opção de homônimo para prosseguir.',
        )
      } else {
        setCreateError(apiErrorMessage(err))
      }
    } finally {
      setSubmitting(false)
    }
  }

  async function handleToggleActive(target: EvaluatorRecord) {
    const action = target.active ? 'inativação' : 'reativação'
    const confirmMessage = target.active
      ? `Confirma a inativação lógica do avaliador ${target.evaluator_code} (${target.full_name})? Avaliações históricas conduzidas permanecerão preservadas.`
      : `Confirma a reativação do avaliador ${target.evaluator_code} (${target.full_name})?`
    if (!window.confirm(confirmMessage)) return

    setUpdatingStatus(true)
    try {
      await updateEvaluator(
        target.id,
        {
          active: !target.active,
          reason_code: target.active ? 'inativacao_cadastral' : 'reativacao_cadastral',
        },
        profile.csrf_token,
      )
      setNotice(`Avaliador ${target.evaluator_code} atualizado (${action} concluída).`)
      setRevision(v => v + 1)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setUpdatingStatus(false)
    }
  }

  function startEditing(target: EvaluatorRecord | EvaluatorDetail) {
    setEditFullName(target.full_name)
    setEditInitials(target.initials ?? '')
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
      await updateEvaluator(
        detail.id,
        {
          full_name: editFullName.trim(),
          initials: editInitials.trim() || null,
          reason_code: reason,
        },
        profile.csrf_token,
      )
      setNotice(`Cadastro de ${editFullName.trim()} atualizado com sucesso (evento auditado).`)
      setIsEditing(false)
      setRevision(v => v + 1)
      const refreshed = await getEvaluator(detail.id)
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
    if (!relinkNewEvaluatorId.trim() && !relinkNewPatientId.trim()) {
      setRelinkError('Informe pelo menos um novo ID de avaliador ou paciente.')
      return
    }
    setRelinkSubmitting(true)
    setRelinkError(null)
    try {
      await relinkAssessment(
        relinkingAssessment.project_id,
        relinkingAssessment.assessment_id,
        {
          evaluator_id: relinkNewEvaluatorId.trim() || undefined,
          patient_id: relinkNewPatientId.trim() || undefined,
          reason_code: reason,
        },
        profile.csrf_token,
      )
      setNotice(
        `Vínculo da avaliação ${relinkingAssessment.assessment_id} corrigido com sucesso (evento auditado).`,
      )
      setRelinkingAssessment(null)
      setRelinkNewEvaluatorId('')
      setRelinkNewPatientId('')
      setRelinkReasonCode('correcao_erro_humano_vinculo')
      setRevision(v => v + 1)
      const refreshed = await getEvaluator(detail.id)
      setDetail(refreshed)
    } catch (err) {
      setRelinkError(apiErrorMessage(err))
    } finally {
      setRelinkSubmitting(false)
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="evaluators-panel registry-panel" aria-label="Módulo Avaliadores">
      <div className="panel-header">
        <div>
          <h2>Avaliadores</h2>
          <p className="quiet">
            Cadastro centralizado de avaliadores responsáveis pela condução das sessões (ADR-007 / WEB-047).
            Código estável EVA-... gerado automaticamente.
          </p>
        </div>
        {profile.role !== 'consulta' && (
          <button
            type="button"
            className="button primary"
            onClick={() => setShowCreate(prev => !prev)}
            aria-expanded={showCreate}
          >
            {showCreate ? 'Cancelar cadastro' : '+ Cadastrar novo avaliador'}
          </button>
        )}
      </div>

      <div className="notice" role="region" aria-label="Distinção de contas">
        <strong>Aviso arquitetural (ADR-006 / ADR-007):</strong> Este cadastro identifica nominalmente os
        profissionais que conduzem as avaliações e sessões. Não cria nem altera contas de acesso ao sistema;
        a equipe utiliza a conta compartilhada para autenticação local e segurança operacional.
      </div>

      {notice && (
        <p role="status" className="notice">
          {notice}
        </p>
      )}

      {/* Formulário de criação de avaliador */}
      {showCreate && (
        <section className="content-card evaluator-form-card" aria-label="Cadastro de novo avaliador">
          <h3>Novo cadastro de avaliador responsável</h3>
          <p className="quiet">
            Informe o nome do profissional. O código estável EVA-... será gerado automaticamente.
          </p>
          <form onSubmit={e => void handleCreateEvaluator(e)}>
            <div className="form-field">
              <label htmlFor="evaluator-fullname">
                Nome completo <strong>*</strong>
              </label>
              <input
                id="evaluator-fullname"
                type="text"
                required
                minLength={2}
                maxLength={120}
                value={fullName}
                onChange={e => handleNameChange(e.target.value)}
                placeholder="Ex.: Dra. Beatriz Sintética Ribeiro"
                autoComplete="off"
              />
            </div>

            <div className="form-field">
              <label htmlFor="evaluator-initials">
                Iniciais (auxílio visual de conferência)
              </label>
              <input
                id="evaluator-initials"
                type="text"
                maxLength={16}
                value={initials}
                onChange={e => {
                  setInitialsCustom(true)
                  setInitials(e.target.value.toUpperCase())
                }}
                placeholder="Ex.: BSR"
                autoComplete="off"
              />
            </div>

            {createError && (
              <div role="region" aria-label="Erro de cadastro" className="homonym-alert notice">
                <p role="alert">{createError}</p>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={confirmHomonym}
                    onChange={e => setConfirmHomonym(e.target.checked)}
                  />
                  <span>Confirmar cadastro de homônimo (profissional diferente)</span>
                </label>
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="button primary" disabled={submitting}>
                {submitting ? 'Salvando avaliador…' : 'Confirmar e salvar avaliador'}
              </button>
              <button
                type="button"
                className="button secondary"
                onClick={() => {
                  setShowCreate(false)
                  setCreateError(null)
                  setConfirmHomonym(false)
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
          Buscar avaliadores
          <input
            type="search"
            value={search}
            onChange={e => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Nome, código EVA-... ou iniciais"
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
      {loading && !evaluators.length ? (
        <p role="status">Carregando lista de avaliadores…</p>
      ) : evaluators.length === 0 ? (
        <p role="status">Nenhum avaliador encontrado para os filtros selecionados.</p>
      ) : (
        <div className="table-scroll">
          <table aria-label="Lista de avaliadores cadastrados">
            <caption>
              Avaliadores cadastrados ({total} no total) — Página {page} de {totalPages}
            </caption>
            <thead>
              <tr>
                <th scope="col">Código</th>
                <th scope="col">Nome completo</th>
                <th scope="col">Iniciais</th>
                <th scope="col">Avaliações conduzidas</th>
                <th scope="col">Última avaliação</th>
                <th scope="col">Status</th>
                <th scope="col">Ações</th>
              </tr>
            </thead>
            <tbody>
              {evaluators.map(ev => (
                <tr key={ev.id}>
                  <td className="tabular-nums">
                    <strong>{ev.evaluator_code}</strong>
                  </td>
                  <td>{ev.full_name}</td>
                  <td>{ev.initials ?? '—'}</td>
                  <td className="tabular-nums">{ev.assessment_count}</td>
                  <td className="tabular-nums">{ev.last_assessment_at ?? '—'}</td>
                  <td>
                    <span className={`status-badge ${ev.active ? 'status-active' : 'status-inactive'}`}>
                      {ev.active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="button secondary"
                      onClick={() => setSelectedEvaluatorId(ev.id)}
                      aria-label={`Ver ficha de ${ev.full_name} (${ev.evaluator_code})`}
                    >
                      Ver ficha
                    </button>
                    {profile.role !== 'consulta' && (
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => void handleToggleActive(ev)}
                        disabled={updatingStatus}
                        aria-label={`${ev.active ? 'Inativar' : 'Reativar'} avaliador ${ev.evaluator_code}`}
                        style={{ marginLeft: 6 }}
                      >
                        {ev.active ? 'Inativar' : 'Reativar'}
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
        <nav aria-label="Paginação de avaliadores" className="pagination-bar">
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

      {/* Ficha detalhada do avaliador */}
      {selectedEvaluatorId && (
        <section
          ref={detailPanelRef}
          tabIndex={-1}
          className="assessment-detail evaluator-detail"
          aria-label="Ficha detalhada do avaliador"
        >
          <div className="panel-header">
            <h3>Ficha cadastral do avaliador</h3>
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
                  setSelectedEvaluatorId(null)
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
              {/* Formulário de edição cadastral do avaliador */}
              {isEditing && (
                <section
                  className="content-card evaluator-edit-card"
                  aria-label="Edição de cadastro do avaliador"
                  style={{ marginBottom: 16 }}
                >
                  <h4>Editar dados cadastrais do avaliador</h4>
                  <p className="quiet">
                    Alterações de nome ou iniciais são registradas com trilha de auditoria em{' '}
                    <code>web_registry_audit_events</code>, mantendo o histórico de avaliações conduzidas.
                  </p>
                  <form onSubmit={e => void handleSaveEdit(e)}>
                    <div className="form-field">
                      <label htmlFor="edit-evaluator-fullname">
                        Nome completo <strong>*</strong>
                      </label>
                      <input
                        id="edit-evaluator-fullname"
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
                      <label htmlFor="edit-evaluator-initials">Iniciais</label>
                      <input
                        id="edit-evaluator-initials"
                        type="text"
                        maxLength={16}
                        value={editInitials}
                        onChange={e => setEditInitials(e.target.value.toUpperCase())}
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="edit-evaluator-reason">
                        Motivo da alteração cadastral <strong>*</strong>
                      </label>
                      <input
                        id="edit-evaluator-reason"
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
                    Procedimento administrativo auditado para retificar erro humano na vinculação do
                    avaliador responsável ou paciente, sem apagar resultados experimentais ou tentativas.
                  </p>
                  <form onSubmit={e => void handleConfirmRelink(e)}>
                    <div className="form-field">
                      <label htmlFor="relink-evaluator-new-eval">
                        ID UUID do novo avaliador responsável (opcional)
                      </label>
                      <input
                        id="relink-evaluator-new-eval"
                        type="text"
                        value={relinkNewEvaluatorId}
                        onChange={e => setRelinkNewEvaluatorId(e.target.value.trim())}
                        placeholder="Ex.: 00000000-0000-4000-8000-000000000101"
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="relink-evaluator-new-pat">
                        ID UUID do novo paciente vinculado (opcional)
                      </label>
                      <input
                        id="relink-evaluator-new-pat"
                        type="text"
                        value={relinkNewPatientId}
                        onChange={e => setRelinkNewPatientId(e.target.value.trim())}
                        placeholder="Ex.: 00000000-0000-4000-8000-000000000001"
                        autoComplete="off"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="relink-evaluator-reason">
                        Motivo da retificação de vínculo <strong>*</strong>
                      </label>
                      <input
                        id="relink-evaluator-reason"
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
                  <dt>Código do avaliador</dt>
                  <dd className="tabular-nums"><strong>{detail.evaluator_code}</strong></dd>
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
                  <dt>Avaliações conduzidas</dt>
                  <dd className="tabular-nums">{detail.assessment_count}</dd>
                </div>
                <div>
                  <dt>Última avaliação</dt>
                  <dd className="tabular-nums">{detail.last_assessment_at ?? 'Nenhuma conduzida'}</dd>
                </div>
              </dl>

              {/* Instrumentos utilizados */}
              <h4>Instrumentos utilizados ({detail.instruments?.length ?? 0})</h4>
              {!detail.instruments || detail.instruments.length === 0 ? (
                <p className="quiet">Nenhum instrumento registrado para este avaliador.</p>
              ) : (
                <ul className="instruments-list" aria-label="Lista de instrumentos do avaliador">
                  {detail.instruments.map(inst => (
                    <li key={inst}>
                      <span className="badge">{inst}</span>
                    </li>
                  ))}
                </ul>
              )}

              {/* Histórico de avaliações conduzidas */}
              <h4>Histórico de avaliações conduzidas ({detail.assessments.length})</h4>
              {detail.assessments.length === 0 ? (
                <p className="quiet">Nenhuma avaliação experimental registrada sob este avaliador.</p>
              ) : (
                <div className="table-scroll">
                  <table aria-label="Histórico de avaliações conduzidas pelo avaliador">
                    <caption>Avaliações conduzidas por este avaliador</caption>
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
                  <table aria-label="Trilha de auditoria cadastral do avaliador">
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
