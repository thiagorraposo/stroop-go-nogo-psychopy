import { useEffect, useRef, useState } from 'react'
import type { ProfessionalProfile } from '../api/client'
import { SessionInvitation } from './SessionInvitation'
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
import { listProjects, getAssessment, exportAssessment } from '../api/assessments'
import type { AssessmentDetail, Project } from '../api/assessments'
import { exportAssessmentView } from '../api/aggregate'
import type { ExportContext } from '../api/aggregate'
import {
  accuracyByVisit,
  computeOverviewKPIs,
  countByDate,
  formatMetric as number,
  OFFICIAL_METRICS_DICTIONARY,
  responseDistribution,
  summarize,
} from '../dashboard/analysis'
import { listPatients } from '../api/patients'
import { queryAnalysis, contextKey } from '../api/analysis'
import type { AnalysisPage } from '../api/analysis'
import { defaultQuery, normalizeQuery, queryKey, supportsLegacyExport, analysisQueryBody } from '../dashboard/query'

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
  const [analyticsTab, setAnalyticsTab] = useState<'geral' | 'visitas' | 'condicoes' | 'operacional' | 'tabela'>('geral')
  const [projects, setProjects] = useState<Project[]>([])
  const [project, setProject] = useState('')
  const [projectsLoading, setProjectsLoading] = useState(true)
  const [query, setQuery] = useState<ResearchQuery | null>(null)
  const [rows, setRows] = useState<ScopedAssessment[]>([])
  const [analysisContext, setAnalysisContext] = useState<AnalysisPage | null>(null)
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)
  const [draft, setDraft] = useState<ResearchQuery | null>(null)
  const [generation, setGeneration] = useState(0)
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

  const queryIO = useRef<AbortController | null>(null)
  const detailIO = useRef<AbortController | null>(null)
  const dirty = !!draft && !!query && queryKey(draft) !== queryKey(query)
  const analyticModule = ['dashboard', 'historico', 'resultados', 'exportacoes'].includes(activeModule)

  function editQuery(next: ResearchQuery) {
    downloadIO.current?.abort(); aggregateIO.current?.abort()
    setExporting(false); setAggregateBusy(false)
    setDownloadMessage(null); setAggregateMessage(null)
    setDraft(next)
  }

  function applyQuery(next: ResearchQuery) {
    queryIO.current?.abort(); detailIO.current?.abort()
    downloadIO.current?.abort(); aggregateIO.current?.abort()
    setRows([]); setAnalysisContext(null); setAggregateContext(null); setAggregateMessage(null)
    setDetail(null); setDetailId(''); setDetailError(null); setDownloadMessage(null)
    setExporting(false); setAggregateBusy(false); setError(null)
    const normalized = normalizeQuery(next)
    setDraft(normalized); setQuery(normalized); setGeneration(n => n + 1)
  }

  function expireContext(cause: unknown) {
    if (!(cause instanceof ApiError) || ![401, 403, 409].includes(cause.status)) return
    queryIO.current?.abort(); detailIO.current?.abort()
    downloadIO.current?.abort(); aggregateIO.current?.abort()
    setRows([]); setAnalysisContext(null); setLoaded(0); setAggregateContext(null); setDetail(null); setDetailId('')
    setLoading(false); setExporting(false); setAggregateBusy(false)
    setError('O conjunto não está mais disponível. Atualize a consulta antes de continuar.')
    if ([401, 403].includes(cause.status)) window.dispatchEvent(new Event('stroop-professional-session-ended'))
  }

  const detailPanel = useRef<HTMLElement>(null)
  const downloadIO = useRef<AbortController | null>(null)
  const aggregateIO = useRef<AbortController | null>(null)

  // Contagem cadastral autorizada, distinta dos pacientes presentes no recorte.
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
          setProject(current => current && items.some(item => item.id === current) ? current : items[0]?.id ?? '')
          if (!query && items[0]) applyQuery(defaultQuery(items[0].id))
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
    setRows([]); setAnalysisContext(null); setAggregateContext(null); setAggregateMessage(null); setDetail(null); setDetailId(''); setDetailError(null); setDownloadMessage(null)
    setLoaded(0)
    downloadIO.current?.abort(); setExporting(false)
    aggregateIO.current?.abort(); setAggregateBusy(false)
    queryIO.current = io
    const selected = query?.projects ?? []
    if (!selected.length) { setLoading(false); return () => io.abort() }
    setLoading(true); setError(null)
    void (async () => {
      try {
        const items: ScopedAssessment[] = []
        const cursors = new Set<string>(), ids = new Set<string>()
        let cursor: string | undefined, first: AnalysisPage | undefined
        do {
          const body = analysisQueryBody(query!, cursor)
          const page = await queryAnalysis(body, profile.csrf_token, io.signal)
          if (io.signal.aborted) return
          if (first && (page.query_id !== first.query_id || page.query_fingerprint !== first.query_fingerprint
            || page.content_fingerprint !== first.content_fingerprint || page.expires_at !== first.expires_at
            || contextKey(page.counts) !== contextKey(first.counts)
            || contextKey(page.aggregates) !== contextKey(first.aggregates)
            || contextKey(page.legacy_export_context) !== contextKey(first.legacy_export_context))) throw new ApiError('state_conflict', 409)
          first ??= page
          for (const item of page.items) {
            if (ids.has(item.assessment_id)) throw new ApiError('invalid_response', 200)
            ids.add(item.assessment_id); items.push(item)
            if (items.length > 5000 || items.length > page.counts.assessments) throw new ApiError('invalid_response', 200)
          }
          cursor = page.next_cursor ?? undefined
          if (cursor && (!page.items.length || cursors.has(cursor))) throw new ApiError('invalid_response', 200)
          if (cursor) cursors.add(cursor)
          setLoaded(items.length)
        } while (cursor)
        if (items.length !== first!.counts.assessments) throw new ApiError('invalid_response', 200)
        if (!io.signal.aborted) {
          setRows(items); setAnalysisContext(first!)
          setAggregateContext(first!.legacy_export_context)
        }
      } catch (cause) {
        if (!io.signal.aborted) {
          setRows([]); setAnalysisContext(null); setLoaded(0); setAggregateContext(null)
          if (cause instanceof ApiError && [401, 403].includes(cause.status)) {
            window.dispatchEvent(new Event('stroop-professional-session-ended'))
          }
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
  }, [query, revision])

  useEffect(() => {
    if (!analysisContext) return
    const expire = () => expireContext(new ApiError('state_conflict', 409))
    const remaining = Date.parse(analysisContext.expires_at) - Date.now()
    if (remaining <= 0) { expire(); return }
    const timer = window.setTimeout(expire, remaining)
    return () => window.clearTimeout(timer)
  }, [analysisContext])

  // Detalhe individual de avaliação
  useEffect(() => {
    const io = new AbortController()
    detailIO.current = io
    setDetail(null); setDetailError(null); setDownloadMessage(null)
    downloadIO.current?.abort(); setExporting(false)
    if (detailId && rows.some(row => row.project_id === detailProject && row.assessment_id === detailId)) void getAssessment(detailProject, detailId, io.signal).then(value => {
      if (!io.signal.aborted) setDetail(value)
    }, cause => { if (!io.signal.aborted) { setDetailError(apiErrorMessage(cause)); expireContext(cause) } })
    return () => io.abort()
  }, [detailProject, detailId, rows])

  useEffect(() => { if (detail) detailPanel.current?.focus() }, [detail])
  useEffect(() => () => downloadIO.current?.abort(), [])
  useEffect(() => () => aggregateIO.current?.abort(), [])

  async function downloadAggregate() {
    if (dirty || !query || !supportsLegacyExport(query) || !aggregateContext || aggregateBusy || !['stroop_go_nogo_ptbr', 'instrumento_sintetico_demo'].includes(selectedInstrument)) return
    const io = new AbortController(); aggregateIO.current = io
    setAggregateBusy(true); setAggregateMessage(null)
    try {
      const result = await exportAssessmentView(
        aggregateContext,
        { test_code: selectedInstrument },
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
        expireContext(cause)
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
    if (!detail || exporting || dirty || loading || error) return
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
      if (!io.signal.aborted) {
        setDownloadMessage(apiErrorMessage(cause))
        expireContext(cause)
      }
    } finally {
      if (!io.signal.aborted) setExporting(false)
    }
  }

  const currentProject = projects.find(item => item.id === project) ?? null

  // O servidor seleciona e ordena o conjunto completo. Consumidores compartilham
  // a geração publicada somente após validar todas as páginas do mesmo contexto.
  const sortedRows = rows

  const instruments = [...new Set(sortedRows.map(row => row.test_code))].sort()
  const selectedInstrument = instruments.length === 1 ? instruments[0]! : ''
  const visible = sortedRows
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
          <button className="button primary" disabled={exporting || dirty || loading || !!error} onClick={() => void download()}>
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

      {projects.length > 0 && query && draft && <div hidden={!analyticModule}>
        <ResearchFilters projects={projects} initialProject={project} loading={loading}
          value={draft} applied={query} refreshKey={revision} onChange={editQuery} onApply={applyQuery} />
        <p className="quiet" role="status">Consulta aplicada {generation}. {loading ? 'Carregando conjunto completo…' : error ? 'Conjunto indisponível; atualize a consulta.' : 'Consulta carregada.'}</p>
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
                  {query.advanced?.condition.length ? ` · condições: ${query.advanced.condition.join(', ')}` : ''}
                  {query.advanced?.responseType.length ? ` · respostas: ${query.advanced.responseType.join(', ')}` : ''}
                  .
                </p>
              )}


        {instruments.length > 1 && <p role="status">Há instrumentos diferentes no recorte. Aplique um instrumento para comparar métricas ou exportar a visão filtrada.</p>}
        {query && !supportsLegacyExport(query) && <p role="status">A exportação deste recorte ainda não está disponível. Os filtros avançados foram preservados; nenhum arquivo sem esses filtros será gerado.</p>}
      </div>}

      {analyticModule && error && <>
        <p role="alert">{error}</p>
        <button className="button secondary" onClick={() => setRevision(value => value + 1)}>Atualizar consultas</button>
      </>}
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

          {!projectsLoading && !projects.length && !error && (
            <p role="status">Nenhum projeto disponível para sua conta.</p>
          )}

          {projects.length > 0 && (
            <>


              {<>
                <p className="quiet">Projeto de preparação: este contexto não altera a consulta aplicada.</p>
                {renderProjectSelector()}
              </>}
              {/* Preparação rápida de convite integrada na visão geral */}
              {currentProject?.active && profile.role !== 'consulta' && (
                <SessionInvitation
                  key={`invitation:${project}`}
                  project={currentProject}
                  profile={profile}
                />
              )}



              {loading && <p role="status">Carregando avaliações… {loaded} recebidas.</p>}

              {!loading && !error && (
                <>
                  {!rows.length ? (
                    <p role="status">Nenhuma avaliação corresponde aos filtros.</p>
                  ) : (
                    <>
                      {/* KPIs Executivos da Visão Geral */}
                      {/* KPIs da Visão Geral (CHG-005 / REQ-REL-004) */}
                      <section className="overview-summary-kpis" aria-label="KPIs da Visão Geral">
                        <div className="kpi-grid">
                          <div className="kpi-box">
                            <span className="kpi-label">Pacientes cadastrados acessíveis</span>
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

                      {/* Sub-navegação em Abas Temáticas de Análise */}
                      <div className="analytics-tabs-container">
                        <nav className="analytics-subnav" aria-label="Visualizações analíticas">
                          <button
                            type="button"
                            className={`button secondary analytics-subnav-btn ${analyticsTab === 'geral' ? 'active' : ''}`}
                            onClick={() => setAnalyticsTab('geral')}
                            aria-pressed={analyticsTab === 'geral'}
                          >
                            📊 Desempenho Geral
                          </button>
                          <button
                            type="button"
                            className={`button secondary analytics-subnav-btn ${analyticsTab === 'visitas' ? 'active' : ''}`}
                            onClick={() => setAnalyticsTab('visitas')}
                            aria-pressed={analyticsTab === 'visitas'}
                          >
                            🔄 Análises por Visita
                          </button>
                          <button
                            type="button"
                            className={`button secondary analytics-subnav-btn ${analyticsTab === 'condicoes' ? 'active' : ''}`}
                            onClick={() => setAnalyticsTab('condicoes')}
                            aria-pressed={analyticsTab === 'condicoes'}
                          >
                            🎯 Condições (Go / No-Go)
                          </button>
                          <button
                            type="button"
                            className={`button secondary analytics-subnav-btn ${analyticsTab === 'operacional' ? 'active' : ''}`}
                            onClick={() => setAnalyticsTab('operacional')}
                            aria-pressed={analyticsTab === 'operacional'}
                          >
                            📈 Volume & Operação
                          </button>
                          <button
                            type="button"
                            className={`button secondary analytics-subnav-btn ${analyticsTab === 'tabela' ? 'active' : ''}`}
                            onClick={() => setAnalyticsTab('tabela')}
                            aria-pressed={analyticsTab === 'tabela'}
                          >
                            📋 Registros & Métricas
                          </button>
                        </nav>
                      </div>

                      {/* CONTEÚDO DA ABA 1: DESEMPENHO GERAL */}
                      {analyticsTab === 'geral' && (
                        <div className="analytics-tab-panel" role="region" aria-label="Painel Desempenho Geral">


                      <button
                        type="button"
                        className="button secondary"
                        disabled={
                          dirty || loading || !!error || !query || !supportsLegacyExport(query) || aggregateBusy ||
                          !aggregateContext ||
                          !['stroop_go_nogo_ptbr', 'instrumento_sintetico_demo'].includes(
                            selectedInstrument,
                          )
                        }
                        onClick={() => void downloadAggregate()}
                      >
                        {aggregateBusy ? 'Preparando arquivo agregado…' : 'Exportar visão filtrada'}
                      </button>

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

                          <figure className="dashboard-chart analytics-card" style={{ margin: '1rem 0' }}>
                            <figcaption>Avaliações por data de início</figcaption>
                            <ul className="chart-meter-list">
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
                              <div className="comparison-tables-grid">
                              <figure className="dashboard-chart analytics-card">
                                <figcaption>Precisão média por visita (%)</figcaption>
                                <ul className="chart-meter-list">
                                  {accuracyByVisit(visible).map(([v, accuracy]) => (
                                    <li key={v}>
                                      <span>Visita {v}</span>
                                      <meter
                                        min={0}
                                        max={100}
                                        value={accuracy}
                                        aria-label={`${v}: ${number(accuracy, 1)}%`}
                                      />
                                      <strong className="tabular-nums">{number(accuracy, 1)}%</strong>
                                    </li>
                                  ))}
                                </ul>
                              </figure>

                              <figure className="dashboard-chart analytics-card">
                                <figcaption>Distribuição dos tempos medianos por avaliação</figcaption>
                                <ul className="chart-meter-list">
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
                                <p className="quiet" style={{ marginTop: '8px' }}>
                                  Avaliações sem acertos não possuem tempo mediano e ficam fora desta distribuição.
                                </p>
                              </figure>
                              </div>

                              <ResearchVisualizations rows={visible} projects={projects} />
                            </>
                          )}

                          {selectedInstrument !== 'stroop_go_nogo_ptbr' && (
                            <GenericInstrumentResults rows={visible} projects={projects} />
                          )}
                        </div>
                      )}

                      {/* CONTEÚDO DA ABA 2: ANÁLISES POR VISITA */}
                      {analyticsTab === 'visitas' && (
                        <div className="analytics-tab-panel" role="region" aria-label="Painel Análises por Visita">
                          {selectedInstrument === 'stroop_go_nogo_ptbr' ? (
                            <ResearchVisualizations rows={visible} projects={projects} viewMode="visitas" />
                          ) : (
                            <GenericInstrumentResults rows={visible} projects={projects} />
                          )}
                        </div>
                      )}

                      {/* CONTEÚDO DA ABA 3: CONDIÇÕES (GO / NO-GO) */}
                      {analyticsTab === 'condicoes' && (
                        <div className="analytics-tab-panel" role="region" aria-label="Painel Condições">
                          {selectedInstrument === 'stroop_go_nogo_ptbr' ? (
                            <ResearchVisualizations rows={visible} projects={projects} viewMode="condicoes" />
                          ) : (
                            <GenericInstrumentResults rows={visible} projects={projects} />
                          )}
                        </div>
                      )}

                      {/* CONTEÚDO DA ABA 4: VOLUME & OPERAÇÃO */}
                      {analyticsTab === 'operacional' && (
                        <div className="analytics-tab-panel" role="region" aria-label="Painel Volume e Operação">
                          <figure className="dashboard-chart analytics-card">
                            <div className="analytics-card-header">
                              <h4 className="analytics-card-title">Volume de coletas ao longo do tempo</h4>
                            </div>
                            <figcaption>Avaliações por data de início</figcaption>
                            <ul className="chart-meter-list">
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
                            <ResearchVisualizations rows={visible} projects={projects} viewMode="operacional" />
                          )}
                        </div>
                      )}

                      {/* CONTEÚDO DA ABA 5: REGISTROS E MÉTRICAS */}
                      {analyticsTab === 'tabela' && (
                        <div className="analytics-tab-panel" role="region" aria-label="Painel Registros e Métricas">
                          <p className="quiet" style={{ margin: '0 0 1rem 0' }}>
                            Visualização detalhada dos registros filtrados e definições conceituais das métricas oficiais.
                          </p>
                        </div>
                      )}

                      {/* TABELA DE REGISTROS FILTRADOS E DICIONÁRIO DE MÉTRICAS */}
                      <div className="analytics-results-section" style={{ marginTop: '2rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '10px' }}>
                          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Tabela de Registros Filtrados ({visible.length})</h3>
                          <button
                            type="button"
                            className="button secondary button-sm"
                            disabled={
                              dirty || loading || !!error || !query || !supportsLegacyExport(query) || aggregateBusy ||
                              !aggregateContext ||
                              !['stroop_go_nogo_ptbr', 'instrumento_sintetico_demo'].includes(
                                selectedInstrument,
                              )
                            }
                            onClick={() => void downloadAggregate()}
                          >
                            {aggregateBusy ? 'Preparando arquivo…' : 'Exportar CSV dos registros'}
                          </button>
                        </div>

                        {aggregateMessage && <p role="status">{aggregateMessage}</p>}

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

                        {/* Resumo e Dicionário Descritivo das Métricas Oficiais (em acordeão recolhível) */}
                        <details className="metrics-dictionary-details analytics-card" style={{ marginTop: '1.5rem' }} open={analyticsTab === 'tabela'}>
                          <summary style={{ cursor: 'pointer', fontWeight: 600, padding: '4px 0' }}>
                            <span>📖 Resumo Descritivo das Métricas Oficiais (Clique para expandir)</span>
                          </summary>
                          <div style={{ marginTop: '1rem' }}>
                            <h3 id="metrics-dictionary-title" style={{ fontSize: '1rem', margin: '0 0 8px 0' }}>
                              Resumo Descritivo das Métricas Oficiais
                            </h3>
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
                          </div>
                        </details>
                      </div>
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





          {loading && <p role="status">Carregando histórico de avaliações…</p>}

          {!loading && !error && !rows.length && (
            <p role="status">Nenhuma avaliação encontrada para este projeto.</p>
          )}

          {!loading && !error && rows.length > 0 && (
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
      {activeModule === 'resultados' && !loading && !error && (
        <section aria-label="Módulo Resultados e análises">
          <div className="panel-header-section">
            <h2>Resultados e análises</h2>
            <p className="panel-subtitle">Análises descritivas aprofundadas, distribuições e visualizações dos instrumentos de pesquisa.</p>
          </div>
          <div className="notice notice-disclaimer">
            <span aria-hidden="true">ℹ️</span>
            <span>Visualizações descritivas e análises de pesquisa (REQ-REL-005). Não constitui avaliação clínica.</span>
          </div>





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

          <p role="status">A exportação avançada do recorte aplicado ainda não está disponível. Use a visão filtrada na Visão geral quando habilitada.</p>
          <fieldset disabled><legend>Exportação avançada indisponível para este recorte</legend>
            <ExportHubPanel profile={profile} project={currentProject} />
          </fieldset>
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
