import { useEffect, useRef, useState } from 'react'
import type { ProfessionalProfile } from '../api/client'
import { SessionInvitation } from './SessionInvitation'
import { CsvImportPanel } from './CsvImportPanel'
import { ResearchFilters } from './ResearchFilters'
import { ResultsTable } from './ResultsTable'
import { ResearchVisualizations, GenericInstrumentResults } from './ResearchVisualizations'
import { PatientsPanel } from './PatientsPanel'
import { EvaluatorsPanel } from './EvaluatorsPanel'
import { AdministrationPanel } from './AdministrationPanel'
import { ExportHubPanel } from './ExportHubPanel'
import type { ScopedAssessment } from './ResultsTable'
import type { ResearchQuery } from './ResearchFilters'
import { ApiError, apiErrorMessage } from '../api/client'
import { listProjects, listAssessments, getAssessment, exportAssessment } from '../api/assessments'
import type { AssessmentDetail, AssessmentOptions, Project } from '../api/assessments'
import { exportAssessmentView } from '../api/aggregate'
import type { ExportContext } from '../api/aggregate'
import {
  accuracyByVisit,
  computeOverviewKPIs,
  countByDate,
  filterAssessments,
  formatMetric as number,
  OFFICIAL_METRICS_DICTIONARY,
  responseDistribution,
  sortAssessments,
  summarize,
} from '../dashboard/analysis'
import { listPatients } from '../api/patients'

export type AdministrativeModule =
  | 'dashboard'
  | 'pacientes'
  | 'avaliadores'
  | 'preparar'
  | 'historico'
  | 'resultados'
  | 'exportacoes'
  | 'administracao'

const filterLabels: Record<string, string> = {
  start_date: 'Data inicial',
  end_date: 'Data final',
  participant_id: 'Participantes',
  visit: 'Visitas',
  evaluator_id: 'Avaliadores',
  test_version: 'Versões',
  platform: 'Plataformas',
  test_code: 'Instrumento',
}

const navIcons = {
  dashboard: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="3" width="7" height="9" />
      <rect x="14" y="3" width="7" height="5" />
      <rect x="14" y="12" width="7" height="9" />
      <rect x="3" y="16" width="7" height="5" />
    </svg>
  ),
  pacientes: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
  avaliadores: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
      <path d="m9 14 2 2 4-4" />
    </svg>
  ),
  preparar: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m22 2-7 20-4-9-9-4Z" />
      <path d="M22 2 11 13" />
    </svg>
  ),
  historico: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  ),
  resultados: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  exportacoes: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  ),
  administracao: (
    <svg className="nav-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ),
}

export function ProfessionalDashboard({
  profile,
  initialModule = 'dashboard',
}: {
  profile: ProfessionalProfile
  initialModule?: AdministrativeModule
}) {
  const [activeModule, setActiveModule] = useState<AdministrativeModule>(initialModule)
  const [projects, setProjects] = useState<Project[]>([])
  const [project, setProject] = useState('')
  const [projectsLoading, setProjectsLoading] = useState(true)
  const [query, setQuery] = useState<ResearchQuery | null>(null)
  const [rows, setRows] = useState<ScopedAssessment[]>([])
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)
  const [instrument, setInstrument] = useState('')
  const [platform, setPlatform] = useState('')
  const [detail, setDetail] = useState<AssessmentDetail | null>(null)
  const [detailId, setDetailId] = useState('')
  const [detailProject, setDetailProject] = useState('')
  const [detailError, setDetailError] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)
  const [downloadMessage, setDownloadMessage] = useState<string | null>(null)
  const [aggregateContext, setAggregateContext] = useState<ExportContext | null>(null)
  const [aggregateBusy, setAggregateBusy] = useState(false)
  const [aggregateMessage, setAggregateMessage] = useState<string | null>(null)
  const [registeredPatientsCount, setRegisteredPatientsCount] = useState<number | null>(null)

  const detailPanel = useRef<HTMLElement>(null)
  const downloadIO = useRef<AbortController | null>(null)
  const aggregateIO = useRef<AbortController | null>(null)

  // Carrega contagem de pacientes cadastrados no projeto atual para os KPIs
  useEffect(() => {
    if (!project) {
      setRegisteredPatientsCount(null)
      return
    }
    const io = new AbortController()
    void listPatients({ page_size: 1 }, io.signal)
      .then(res => {
        if (!io.signal.aborted) setRegisteredPatientsCount(res.total)
      })
      .catch(() => {
        if (!io.signal.aborted) setRegisteredPatientsCount(null)
      })
    return () => io.abort()
  }, [project, revision])

  // Carrega lista de projetos autorizados
  useEffect(() => {
    const io = new AbortController()
    void (async () => {
      try {
        const items: Project[] = []
        const cursors = new Set<string>(), ids = new Set<string>()
        let cursor: string | undefined
        do {
          const page = await listProjects({ cursor, limit: 100, signal: io.signal })
          for (const item of page.items) {
            if (ids.has(item.id)) throw new ApiError('invalid_response', 200)
            ids.add(item.id); items.push(item)
          }
          cursor = page.next_cursor ?? undefined
          if (cursor && cursors.has(cursor)) throw new ApiError('invalid_response', 200)
          if (cursor) cursors.add(cursor)
        } while (cursor)
        if (!io.signal.aborted) {
          setProjects(items)
          setProject(items[0]?.id ?? '')
        }
      } catch (cause) {
        if (!io.signal.aborted) setError(apiErrorMessage(cause))
      } finally {
        if (!io.signal.aborted) setProjectsLoading(false)
      }
    })()
    return () => io.abort()
  }, [revision])

  // Carrega avaliações conforme projeto e filtros
  useEffect(() => {
    const io = new AbortController()
    setRows([]); setAggregateContext(null); setAggregateMessage(null); setDetail(null); setDetailId(''); setDetailError(null); setDownloadMessage(null)
    setInstrument(''); setPlatform(''); setLoaded(0)
    downloadIO.current?.abort(); setExporting(false)
    aggregateIO.current?.abort(); setAggregateBusy(false)
    const selected = query?.projects ?? (project ? [project] : [])
    if (!selected.length) { setLoading(false); return () => io.abort() }
    setLoading(true); setError(null)
    void (async () => {
      try {
        const items: ScopedAssessment[] = []
        const snapshots: ExportContext['projects'] = []
        const appliedFilters = { ...(query?.filters ?? {}) } as AssessmentOptions
        delete appliedFilters.cursor; delete appliedFilters.limit; delete appliedFilters.signal
        if (selected.length > 20) throw new ApiError('invalid_request', 422)
        for (const projectId of selected) {
          const cursors = new Set<string>(), ids = new Set<string>()
          let cursor: string | undefined, projectSnapshot: string | undefined
          let snapshotsComplete = true
          do {
            const page = await listAssessments(projectId, { ...query?.filters, cursor, limit: 100, signal: io.signal })
            if (page.snapshot) {
              if (projectSnapshot && projectSnapshot !== page.snapshot) throw new ApiError('invalid_response', 200)
              projectSnapshot = page.snapshot
            } else snapshotsComplete = false
            for (const item of page.items) {
              if (ids.has(item.assessment_id)) throw new ApiError('invalid_response', 200)
              ids.add(item.assessment_id); items.push({ ...item, project_id: projectId })
              if (items.length > 5000) throw new ApiError('invalid_request', 422)
            }
            cursor = page.next_cursor ?? undefined
            if (cursor && cursors.has(cursor)) throw new ApiError('invalid_response', 200)
            if (cursor) cursors.add(cursor)
            if (io.signal.aborted) return
            setLoaded(items.length)
          } while (cursor)
          if (projectSnapshot && snapshotsComplete) snapshots.push({ project_id: projectId, snapshot: projectSnapshot })
        }
        if (!io.signal.aborted) {
          setRows(items)
          setAggregateContext(snapshots.length === selected.length ? { projects: snapshots, filters: appliedFilters } : null)
        }
      } catch (cause) {
        if (!io.signal.aborted) {
          setRows([])
          setError(
            cause instanceof ApiError && cause.status === 422
              ? 'A consulta não pôde ser concluída com estes filtros. Restrinja o período ou os projetos (até 5.000 avaliações); nenhum total parcial foi exibido.'
              : cause instanceof ApiError && cause.code === 'state_conflict'
                ? 'O conjunto mudou durante a consulta. Atualize para carregar todas as páginas novamente; nenhum total parcial foi exibido.'
                : apiErrorMessage(cause),
          )
        }
      } finally {
        if (!io.signal.aborted) setLoading(false)
      }
    })()
    return () => { io.abort(); downloadIO.current?.abort(); aggregateIO.current?.abort() }
  }, [project, query, revision])

  // Detalhe individual de avaliação
  useEffect(() => {
    const io = new AbortController()
    setDetail(null); setDetailError(null); setDownloadMessage(null)
    downloadIO.current?.abort(); setExporting(false)
    if (detailId) void getAssessment(detailProject, detailId, io.signal).then(value => {
      if (!io.signal.aborted) setDetail(value)
    }, cause => { if (!io.signal.aborted) setDetailError(apiErrorMessage(cause)) })
    return () => io.abort()
  }, [detailProject, detailId])

  useEffect(() => { if (detail) detailPanel.current?.focus() }, [detail])
  useEffect(() => () => downloadIO.current?.abort(), [])
  useEffect(() => () => aggregateIO.current?.abort(), [])

  async function downloadAggregate() {
    if (!aggregateContext || aggregateBusy || !['stroop_go_nogo_ptbr', 'instrumento_sintetico_demo'].includes(selectedInstrument)) return
    const io = new AbortController(); aggregateIO.current = io
    setAggregateBusy(true); setAggregateMessage(null)
    try {
      const result = await exportAssessmentView(
        aggregateContext,
        { test_code: selectedInstrument, ...(platform ? { platform: platform as 'web' | 'psychopy' } : {}) },
        profile.csrf_token,
        io.signal,
      )
      if (io.signal.aborted) return
      const url = URL.createObjectURL(result.blob)
      try {
        const link = document.createElement('a')
        link.href = url
        link.download = result.filename
        document.body.append(link)
        link.click()
        link.remove()
      } finally {
        setTimeout(() => URL.revokeObjectURL(url), 1000)
      }
      setAggregateMessage('Arquivo agregado preparado para download.')
    } catch (cause) {
      if (!io.signal.aborted) {
        setAggregateMessage(
          cause instanceof ApiError && cause.status === 409
            ? 'Os dados mudaram desde a consulta. Atualize os filtros para recarregar todas as páginas antes de exportar.'
            : apiErrorMessage(cause),
        )
      }
    } finally {
      if (!io.signal.aborted) setAggregateBusy(false)
    }
  }

  async function download() {
    if (!detail || exporting) return
    const io = new AbortController(); downloadIO.current = io
    setExporting(true); setDownloadMessage(null)
    try {
      const result = await exportAssessment(detail.project_id, detail.assessment_id, io.signal)
      if (io.signal.aborted) return
      const url = URL.createObjectURL(result.blob)
      try {
        const link = document.createElement('a')
        link.href = url
        link.download = result.filename
        document.body.append(link)
        link.click()
        link.remove()
      } finally {
        setTimeout(() => URL.revokeObjectURL(url), 1000)
      }
      setDownloadMessage('Arquivo preparado para download.')
    } catch (cause) {
      if (!io.signal.aborted) setDownloadMessage(apiErrorMessage(cause))
    } finally {
      if (!io.signal.aborted) setExporting(false)
    }
  }

  const currentProject = projects.find(item => item.id === project) ?? null

  // Aplicação do catálogo avançado de filtros e ordenação determinística (REQ-REL-004)
  const filteredRows = filterAssessments(rows, query?.advanced)
  const sortedRows = sortAssessments(
    filteredRows,
    query?.advanced?.sortBy ?? 'date',
    query?.advanced?.sortOrder ?? 'desc',
  )

  const instruments = [...new Set(sortedRows.map(row => row.test_code))].sort()
  const selectedInstrument = instrument || instruments[0] || ''
  const visible = sortedRows.filter(
    row => row.test_code === selectedInstrument && (!platform || row.platform === platform),
  )
  const totals = summarize(visible)
  const dates = countByDate(visible)
  const peak = Math.max(1, ...dates.map(([, count]) => count))
  const overviewKpis = computeOverviewKPIs(sortedRows, registeredPatientsCount)

  // Renderizador do seletor de projeto compartilhado
  const renderProjectSelector = () => (
    <div className="project-selector-wrapper">
      <label htmlFor="research-project">Projeto</label>
      <select
        id="research-project"
        value={project}
        onChange={event => {
          if (event.target.value !== project) {
            aggregateIO.current?.abort()
            setAggregateContext(null)
            setAggregateBusy(false)
            setRows([])
            setDetail(null)
            setProject(event.target.value)
            setQuery(null)
          }
        }}
      >
        {projects.map(item => (
          <option key={item.id} value={item.id}>
            {item.code} — {item.name}
            {item.active ? '' : ' (inativo)'}
          </option>
        ))}
      </select>
    </div>
  )

  // Renderizador do painel de detalhe de avaliação
  const renderAssessmentDetail = () =>
    detail ? (
      <section ref={detailPanel} tabIndex={-1} className="assessment-detail" aria-label="Detalhe da avaliação">
        <h3>Detalhe da avaliação</h3>
        <dl className="assessment-metadata">
          <div><dt>Avaliação</dt><dd className="tabular-nums">{detail.assessment_id}</dd></div>
          <div><dt>Sessão</dt><dd className="tabular-nums">{detail.session_id ?? 'Legado sem sessão WEB'}</dd></div>
          <div><dt>Projeto</dt><dd>{projects.find(item => item.id === detail.project_id)?.code ?? detail.project_id} ({detail.project_id})</dd></div>
          <div><dt>Participante</dt><dd className="tabular-nums">{detail.participant_id}</dd></div>
          <div><dt>Visita</dt><dd>{detail.visit}</dd></div>
          <div><dt>Avaliador</dt><dd>{detail.evaluator_id ?? 'Legado sem identificação técnica'}</dd></div>
          <div><dt>Início</dt><dd className="tabular-nums">{detail.started_at}</dd></div>
          <div><dt>Conclusão</dt><dd className="tabular-nums">{detail.completed_at ?? 'Não registrada no legado'}</dd></div>
          <div><dt>Plataforma</dt><dd>{detail.platform === 'web' ? 'WEB' : 'PsychoPy local (importado)'}</dd></div>
          <div><dt>Instrumento</dt><dd>{detail.test_code}</dd></div>
          <div><dt>Versão</dt><dd className="tabular-nums">{detail.test_version}</dd></div>
          <div><dt>Protocolo</dt><dd>{detail.protocol_id ?? 'Legado sem protocolo WEB'}</dd></div>
          <div><dt>Aplicativo</dt><dd>{detail.app_version ?? 'Não registrado'}</dd></div>
          <div><dt>Período de quadro observado (ms)</dt><dd className="tabular-nums">{number(detail.frame_period_ms, 3)}</dd></div>
        </dl>
        {'accuracy' in detail.summary && (
          <section aria-label="Contagens das respostas">
            <h4>Contagens das respostas principais</h4>
            <dl className="dashboard-cards">
              <div><dt>Acertos (hit)</dt><dd className="tabular-nums">{detail.summary.hits}</dd></div>
              <div><dt>Omissões (omission)</dt><dd className="tabular-nums">{detail.summary.omission_errors}</dd></div>
              <div><dt>Rejeições corretas (correct_rejection)</dt><dd className="tabular-nums">{detail.summary.correct_rejections}</dd></div>
              <div><dt>Comissões (commission)</dt><dd className="tabular-nums">{detail.summary.commission_errors}</dd></div>
            </dl>
          </section>
        )}
        <dl>
          {detail.metrics.map(metric => (
            <div key={metric.metric_code}>
              <dt>{metric.metric_label}</dt>
              <dd className="tabular-nums">
                {number(metric.metric_value, 3)} {metric.unit}
              </dd>
            </div>
          ))}
        </dl>
        {detail.trials.length > 0 && (
          <div className="table-scroll">
            <table>
              <caption>Tentativas registradas</caption>
              <thead>
                <tr>
                  <th>Tentativa</th>
                  <th>Palavra</th>
                  <th>Cor</th>
                  <th>Condição</th>
                  <th>Resposta</th>
                  <th>Classificação</th>
                  <th>RT (s)</th>
                </tr>
              </thead>
              <tbody>
                {detail.trials.map(trial => (
                  <tr key={trial.trial_number}>
                    <td className="tabular-nums">{trial.trial_number}</td>
                    <td>{trial.word}</td>
                    <td>{trial.ink_color}</td>
                    <td>{trial.condition}</td>
                    <td>{trial.key_pressed ?? '—'}</td>
                    <td>{trial.error_type}</td>
                    <td className="tabular-nums">{number(trial.reaction_time_seconds, 3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {detail.test_code === 'stroop_go_nogo_ptbr' && (
          <button className="button primary" disabled={exporting} onClick={() => void download()}>
            {exporting ? 'Preparando arquivo…' : 'Exportar CSV oficial'}
          </button>
        )}
        {downloadMessage && <p role="status">{downloadMessage}</p>}
        <button className="button secondary" onClick={() => setDetailId('')}>
          Fechar detalhe
        </button>
      </section>
    ) : null

  return (
    <div className="professional-dashboard" aria-label="Painel administrativo da pesquisa">
      {/* Barra de Navegação Modular em 8 Módulos (ADR-007 / CHG-005) */}
      <nav aria-label="Módulos administrativos" className="professional-areas professional-modules">
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'dashboard' ? 'active' : ''}`}
          aria-pressed={activeModule === 'dashboard'}
          onClick={() => {
            setActiveModule('dashboard')
            setDetailId('')
          }}
        >
          {navIcons.dashboard}
          Visão geral (Dashboard)
        </button>
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'pacientes' ? 'active' : ''}`}
          aria-pressed={activeModule === 'pacientes'}
          onClick={() => {
            setActiveModule('pacientes')
            setDetailId('')
          }}
        >
          {navIcons.pacientes}
          Pacientes
        </button>
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'avaliadores' ? 'active' : ''}`}
          aria-pressed={activeModule === 'avaliadores'}
          onClick={() => {
            setActiveModule('avaliadores')
            setDetailId('')
          }}
        >
          {navIcons.avaliadores}
          Avaliadores
        </button>
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'preparar' ? 'active' : ''}`}
          aria-pressed={activeModule === 'preparar'}
          onClick={() => {
            setActiveModule('preparar')
            setDetailId('')
          }}
        >
          {navIcons.preparar}
          Preparar avaliação
        </button>
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'historico' ? 'active' : ''}`}
          aria-pressed={activeModule === 'historico'}
          onClick={() => {
            setActiveModule('historico')
            setDetailId('')
          }}
        >
          {navIcons.historico}
          Avaliações e histórico
        </button>
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'resultados' ? 'active' : ''}`}
          aria-pressed={activeModule === 'resultados'}
          onClick={() => {
            setActiveModule('resultados')
            setDetailId('')
          }}
        >
          {navIcons.resultados}
          Resultados e análises
        </button>
        <button
          type="button"
          className={`button secondary modular-nav-btn ${activeModule === 'exportacoes' ? 'active' : ''}`}
          aria-pressed={activeModule === 'exportacoes'}
          onClick={() => {
            setActiveModule('exportacoes')
            setDetailId('')
          }}
        >
          {navIcons.exportacoes}
          Exportações
        </button>
        {profile.role === 'administracao' && (
          <button
            type="button"
            className={`button secondary modular-nav-btn ${activeModule === 'administracao' ? 'active' : ''}`}
            aria-pressed={activeModule === 'administracao'}
            onClick={() => {
              setActiveModule('administracao')
              setDetailId('')
            }}
          >
            {navIcons.administracao}
            Administração
          </button>
        )}
      </nav>

      {/* MÓDULO 1: VISÃO GERAL (DASHBOARD) */}
      {activeModule === 'dashboard' && (
        <>
          <div className="panel-header-section">
            <h2>Resultados da pesquisa</h2>
            <p className="panel-subtitle">Visão consolidada de avaliações, métricas psicométricas e tendências operacionais.</p>
          </div>
          <div className="notice notice-disclaimer">
            <span aria-hidden="true">ℹ️</span>
            <span>Resultados descritivos. Este painel não representa avaliação clínica ou diagnóstico.</span>
          </div>

          {projectsLoading && <p role="status">Carregando projetos…</p>}
          {error && (
            <>
              <p role="alert">{error}</p>
              <button className="button secondary" onClick={() => setRevision(value => value + 1)}>
                Atualizar consultas
              </button>
            </>
          )}
          {!projectsLoading && !projects.length && !error && (
            <p role="status">Nenhum projeto disponível para sua conta.</p>
          )}

          {projects.length > 0 && (
            <>
              {renderProjectSelector()}

              {/* Importação CSV mantida durante a transição M5 até M7 */}
              {currentProject?.active && profile.role !== 'consulta' && (
                <CsvImportPanel
                  project={currentProject}
                  profile={profile}
                  onImported={() => setRevision(value => value + 1)}
                />
              )}

              {/* Preparação rápida de convite integrada na visão geral */}
              {currentProject?.active && profile.role !== 'consulta' && (
                <SessionInvitation
                  key={`invitation:${project}`}
                  project={currentProject}
                  profile={profile}
                />
              )}

              <ResearchFilters
                key={`filters:${project}`}
                projects={projects}
                initialProject={project}
                loading={loading}
                onApply={value => {
                  aggregateIO.current?.abort()
                  setAggregateContext(null)
                  setAggregateBusy(false)
                  setRows([])
                  setQuery(value)
                }}
              />

              {query && (
                <p className="quiet active-filters-bar" role="status">
                  Filtros aplicados: {query.projects.length} projeto(s);{' '}
                  {Object.entries(query.filters)
                    .filter(([, value]) => (Array.isArray(value) ? value.length : !!value))
                    .map(
                      ([key, value]) =>
                        `${filterLabels[key] ?? key}: ${Array.isArray(value) ? value.join(', ') : value}`,
                    )
                    .join(' · ') || 'sem restrições adicionais'}
                  {query.advanced?.searchText ? ` · busca: "${query.advanced.searchText}"` : ''}
                  {query.advanced?.status && query.advanced.status !== 'valid' ? ` · status: ${query.advanced.status}` : ''}
                  {query.advanced?.accuracyRange && query.advanced.accuracyRange !== 'all' ? ` · precisão: ${query.advanced.accuracyRange}` : ''}
                  {query.advanced?.rtRange && query.advanced.rtRange !== 'all' ? ` · RT: ${query.advanced.rtRange}` : ''}
                  .
                </p>
              )}

              {loading && <p role="status">Carregando avaliações… {loaded} recebidas.</p>}

              {!loading && !error && (
                <>
                  {!rows.length ? (
                    <p role="status">Nenhuma avaliação corresponde aos filtros.</p>
                  ) : (
                    <>
                      {/* KPIs da Visão Geral (CHG-005 / REQ-REL-004) */}
                      <section className="overview-summary-kpis" aria-label="KPIs da Visão Geral">
                        <div className="kpi-grid">
                          <div className="kpi-box">
                            <span className="kpi-label">Pacientes cadastrados no projeto</span>
                            <strong className="kpi-value tabular-nums">
                              {registeredPatientsCount !== null ? registeredPatientsCount : '—'}
                            </strong>
                          </div>
                          <div className="kpi-box">
                            <span className="kpi-label">Avaliações válidas</span>
                            <strong className="kpi-value tabular-nums">{overviewKpis.byStatus.valid}</strong>
                          </div>
                          <div className="kpi-box">
                            <span className="kpi-label">Avaliações interrompidas / inválidas</span>
                            <strong className="kpi-value tabular-nums">{overviewKpis.byStatus.invalid}</strong>
                          </div>
                          <div className="kpi-box">
                            <span className="kpi-label">Avaliadores no recorte</span>
                            <strong className="kpi-value tabular-nums">
                              {Object.keys(overviewKpis.byEvaluator).length}
                            </strong>
                          </div>
                        </div>
                      </section>

                      <div className="dashboard-filters">
                        <label>
                          Instrumento
                          <select
                            value={selectedInstrument}
                            onChange={event => {
                              aggregateIO.current?.abort()
                              setAggregateBusy(false)
                              setAggregateMessage(null)
                              setInstrument(event.target.value)
                              setDetailId('')
                            }}
                          >
                            {instruments.map(code => (
                              <option key={code}>{code}</option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Plataforma
                          <select
                            value={platform}
                            onChange={event => {
                              aggregateIO.current?.abort()
                              setAggregateBusy(false)
                              setAggregateMessage(null)
                              setPlatform(event.target.value)
                              setDetailId('')
                            }}
                          >
                            <option value="">Todas</option>
                            <option value="web">WEB</option>
                            <option value="psychopy">PsychoPy local</option>
                          </select>
                        </label>
                      </div>

                      <button
                        type="button"
                        className="button secondary"
                        disabled={
                          aggregateBusy ||
                          !aggregateContext ||
                          !['stroop_go_nogo_ptbr', 'instrumento_sintetico_demo'].includes(
                            selectedInstrument,
                          )
                        }
                        onClick={() => void downloadAggregate()}
                      >
                        {aggregateBusy ? 'Preparando arquivo agregado…' : 'Exportar visão filtrada'}
                      </button>

                      {aggregateMessage && <p role="status">{aggregateMessage}</p>}

                      <p className="quiet">
                        Os totais consideram todas as páginas do projeto e os filtros aplicados. Um instrumento
                        por vez. Datas seguem o início registrado; horários legados sem fuso conservam sua
                        referência original.
                      </p>

                      <dl className="dashboard-cards">
                        <div>
                          <dt>Avaliações</dt>
                          <dd className="tabular-nums">{totals.assessments}</dd>
                        </div>
                        <div>
                          <dt>Participantes únicos</dt>
                          <dd className="tabular-nums">{totals.participants}</dd>
                        </div>
                        {selectedInstrument === 'stroop_go_nogo_ptbr' && (
                          <>
                            <div>
                              <dt>Precisão média</dt>
                              <dd className="tabular-nums">{number(totals.meanAccuracy, 1)}%</dd>
                            </div>
                            <div>
                              <dt>Precisão mediana</dt>
                              <dd className="tabular-nums">{number(totals.medianAccuracy, 1)}%</dd>
                            </div>
                            <div>
                              <dt>Mediana dos tempos por avaliação</dt>
                              <dd className="tabular-nums">{number(totals.medianResponseSeconds, 3)} s</dd>
                            </div>
                            <div>
                              <dt>Omissões</dt>
                              <dd className="tabular-nums">{totals.omissions}</dd>
                            </div>
                            <div>
                              <dt>Comissões</dt>
                              <dd className="tabular-nums">{totals.commissions}</dd>
                            </div>
                          </>
                        )}
                      </dl>

                      <figure className="dashboard-chart">
                        <figcaption>Avaliações por data de início</figcaption>
                        <ul>
                          {dates.map(([day, count]) => (
                            <li key={day}>
                              <span>{day}</span>
                              <meter
                                min={0}
                                max={peak}
                                value={count}
                                aria-label={`${day}: ${count} avaliações`}
                              />
                              <strong className="tabular-nums">{count}</strong>
                            </li>
                          ))}
                        </ul>
                      </figure>

                      {selectedInstrument === 'stroop_go_nogo_ptbr' && (
                        <>
                          <figure className="dashboard-chart">
                            <figcaption>Precisão média por visita (%)</figcaption>
                            <ul>
                              {accuracyByVisit(visible).map(([v, accuracy]) => (
                                <li key={v}>
                                  <span>{v}</span>
                                  <meter
                                    min={0}
                                    max={100}
                                    value={accuracy}
                                    aria-label={`${v}: ${number(accuracy, 1)}%`}
                                  />
                                  <strong className="tabular-nums">{number(accuracy, 1)}</strong>
                                </li>
                              ))}
                            </ul>
                          </figure>
                          <figure className="dashboard-chart">
                            <figcaption>Distribuição dos tempos medianos por avaliação</figcaption>
                            <ul>
                              {responseDistribution(visible).map(([range, count]) => (
                                <li key={range}>
                                  <span>{range}</span>
                                  <meter
                                    min={0}
                                    max={Math.max(1, visible.length)}
                                    value={count}
                                    aria-label={`${range}: ${count} avaliações`}
                                  />
                                  <strong className="tabular-nums">{count}</strong>
                                </li>
                              ))}
                            </ul>
                            <p className="quiet">
                              Avaliações sem acertos não possuem tempo mediano e ficam fora desta distribuição.
                            </p>
                          </figure>
                          <ResearchVisualizations rows={visible} projects={projects} />
                        </>
                      )}

                      {selectedInstrument !== 'stroop_go_nogo_ptbr' && (
                        <GenericInstrumentResults rows={visible} projects={projects} />
                      )}

                      <ResultsTable
                        rows={visible}
                        projects={projects}
                        onDetail={row => {
                          aggregateIO.current?.abort()
                          setAggregateBusy(false)
                          setDetailProject(row.project_id)
                          setDetailId(row.assessment_id)
                        }}
                      />

                      {/* Resumo e Dicionário Descritivo das Métricas Oficiais (CHG-005) */}
                      <section className="metrics-dictionary" aria-labelledby="metrics-dictionary-title">
                        <h3 id="metrics-dictionary-title">Resumo Descritivo das Métricas Oficiais</h3>
                        <p className="quiet">
                          Definições conceituais, origens de cálculo e convenção de tratamento de valores nulos
                          das métricas oficiais Stroop Go/No-Go.
                        </p>
                        <div className="table-scroll">
                          <table aria-label="Definições conceituais e tratamento de nulos">
                            <thead>
                              <tr>
                                <th>Métrica oficial</th>
                                <th>Origem da fórmula</th>
                                <th>Definição conceitual</th>
                                <th>Unidade</th>
                                <th>Tratamento de nulos</th>
                              </tr>
                            </thead>
                            <tbody>
                              {OFFICIAL_METRICS_DICTIONARY.map(m => (
                                <tr key={m.code}>
                                  <td>
                                    <strong>{m.label}</strong> (<code>{m.code}</code>)
                                  </td>
                                  <td>{m.origin}</td>
                                  <td>{m.definition}</td>
                                  <td>
                                    <span className="badge">{m.unit}</span>
                                  </td>
                                  <td>{m.nullTreatment}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </section>
                    </>
                  )}
                </>
              )}

              {detailId && !detail && !detailError && <p role="status">Carregando detalhe…</p>}
              {detailError && <p role="alert">{detailError}</p>}
              {renderAssessmentDetail()}
            </>
          )}
        </>
      )}

      {/* MÓDULO 2: PACIENTES (WEB-047) */}
      {activeModule === 'pacientes' && (
        <PatientsPanel profile={profile} project={currentProject} />
      )}

      {/* MÓDULO 3: AVALIADORES (WEB-047) */}
      {activeModule === 'avaliadores' && (
        <EvaluatorsPanel profile={profile} project={currentProject} />
      )}

      {/* MÓDULO 4: PREPARAR AVALIAÇÃO */}
      {activeModule === 'preparar' && (
        <section aria-label="Módulo Preparar avaliação">
          <div className="panel-header-section">
            <h2>Preparar avaliação</h2>
            <p className="panel-subtitle">
              Emissão de convites de uso único para aplicação da Tarefa de Correspondência de Cores.
              Selecione o paciente e o avaliador cadastrados, informe a visita e confira o resumo.
            </p>
          </div>

          {renderProjectSelector()}

          {currentProject?.active && profile.role !== 'consulta' ? (
            <SessionInvitation
              key={`invitation-mod:${project}`}
              project={currentProject}
              profile={profile}
            />
          ) : profile.role === 'consulta' ? (
            <p className="notice" role="status">
              Seu perfil é de consulta e não tem permissão para gerar novos convites de avaliação.
            </p>
          ) : (
            <p className="notice" role="status">
              O projeto selecionado está inativo. Selecione um projeto ativo para preparar novas sessões.
            </p>
          )}
        </section>
      )}

      {/* MÓDULO 5: AVALIAÇÕES E HISTÓRICO */}
      {activeModule === 'historico' && (
        <section aria-label="Módulo Avaliações e histórico">
          <div className="panel-header-section">
            <h2>Avaliações e histórico</h2>
            <p className="panel-subtitle">
              Acompanhamento operacional de sessões, tentativas registradas e conferência detalhada de resultados.
            </p>
          </div>

          {renderProjectSelector()}

          <div className="dashboard-filters">
            <label>
              Instrumento
              <select
                value={selectedInstrument}
                onChange={event => {
                  setInstrument(event.target.value)
                  setDetailId('')
                }}
              >
                {instruments.map(code => (
                  <option key={code}>{code}</option>
                ))}
              </select>
            </label>
            <label>
              Plataforma
              <select
                value={platform}
                onChange={event => {
                  setPlatform(event.target.value)
                  setDetailId('')
                }}
              >
                <option value="">Todas</option>
                <option value="web">WEB</option>
                <option value="psychopy">PsychoPy local</option>
              </select>
            </label>
          </div>

          {loading && <p role="status">Carregando histórico de avaliações…</p>}

          {!loading && !rows.length && (
            <p role="status">Nenhuma avaliação encontrada para este projeto.</p>
          )}

          {!loading && rows.length > 0 && (
            <ResultsTable
              rows={visible}
              projects={projects}
              onDetail={row => {
                setDetailProject(row.project_id)
                setDetailId(row.assessment_id)
              }}
            />
          )}

          {detailId && !detail && !detailError && <p role="status">Carregando detalhe…</p>}
          {detailError && <p role="alert">{detailError}</p>}
          {renderAssessmentDetail()}
        </section>
      )}

      {/* MÓDULO 6: RESULTADOS E ANÁLISES (WEB-019) */}
      {activeModule === 'resultados' && (
        <section aria-label="Módulo Resultados e análises">
          <div className="panel-header-section">
            <h2>Resultados e análises</h2>
            <p className="panel-subtitle">Análises descritivas aprofundadas, distribuições e visualizações dos instrumentos de pesquisa.</p>
          </div>
          <div className="notice notice-disclaimer">
            <span aria-hidden="true">ℹ️</span>
            <span>Visualizações descritivas e análises de pesquisa (REQ-REL-005). Não constitui avaliação clínica.</span>
          </div>

          {renderProjectSelector()}

          <ResearchFilters
            key={`analytics-filters:${project}`}
            projects={projects}
            initialProject={project}
            loading={loading}
            onApply={value => {
              setRows([])
              setQuery(value)
            }}
          />

          <dl className="dashboard-cards">
            <div>
              <dt>Avaliações analisadas</dt>
              <dd className="tabular-nums">{totals.assessments}</dd>
            </div>
            <div>
              <dt>Participantes únicos</dt>
              <dd className="tabular-nums">{totals.participants}</dd>
            </div>
            {selectedInstrument === 'stroop_go_nogo_ptbr' && (
              <>
                <div>
                  <dt>Precisão média</dt>
                  <dd className="tabular-nums">{number(totals.meanAccuracy, 1)}%</dd>
                </div>
                <div>
                  <dt>Precisão mediana</dt>
                  <dd className="tabular-nums">{number(totals.medianAccuracy, 1)}%</dd>
                </div>
                <div>
                  <dt>Tempo mediano de resposta</dt>
                  <dd className="tabular-nums">{number(totals.medianResponseSeconds, 3)} s</dd>
                </div>
              </>
            )}
          </dl>

          {selectedInstrument === 'stroop_go_nogo_ptbr' && (
            <ResearchVisualizations rows={visible} projects={projects} />
          )}

          {selectedInstrument !== 'stroop_go_nogo_ptbr' && (
            <GenericInstrumentResults rows={visible} projects={projects} />
          )}
        </section>
      )}

      {/* MÓDULO 7: EXPORTAÇÕES (WEB-020) */}
      {activeModule === 'exportacoes' && (
        <section aria-label="Módulo Exportações" className="export-hub-panel">
          {renderProjectSelector()}
          <ExportHubPanel profile={profile} project={currentProject} />
        </section>
      )}

      {/* MÓDULO 8: ADMINISTRAÇÃO (AdministrationPanel.tsx) */}
      {activeModule === 'administracao' && profile.role === 'administracao' && (
        <AdministrationPanel
          profile={profile}
          onNavigateToEvaluators={() => setActiveModule('avaliadores')}
        />
      )}
    </div>
  )
}
