import { useEffect, useRef, useState } from 'react'
import type { ProfessionalProfile } from '../api/client'
import { SessionInvitation } from './SessionInvitation'
import { ResearchFilters } from './ResearchFilters'
import { ResultsTable } from './ResultsTable'
import { ResearchVisualizations, GenericInstrumentResults } from './ResearchVisualizations'
import type { ScopedAssessment } from './ResultsTable'
import type { ResearchQuery } from './ResearchFilters'
import { ApiError, apiErrorMessage } from '../api/client'
import { listProjects, listAssessments, getAssessment, exportAssessment } from '../api/assessments'
import type { AssessmentDetail, Project } from '../api/assessments'
import { accuracyByVisit, countByDate, formatMetric as number, responseDistribution, summarize } from '../dashboard/analysis'

const filterLabels: Record<string, string> = { start_date: 'Data inicial', end_date: 'Data final', participant_id: 'Participantes', visit: 'Visitas', evaluator_id: 'Avaliadores', test_version: 'Versões', platform: 'Plataformas', test_code: 'Instrumento' }

export function ProfessionalDashboard({ profile }: { profile: ProfessionalProfile }) {
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
  const detailPanel = useRef<HTMLElement>(null)
  const downloadIO = useRef<AbortController | null>(null)

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
        if (!io.signal.aborted) { setProjects(items); setProject(items[0]?.id ?? '') }
      } catch (cause) { if (!io.signal.aborted) setError(apiErrorMessage(cause)) }
      finally { if (!io.signal.aborted) setProjectsLoading(false) }
    })()
    return () => io.abort()
  }, [revision])

  useEffect(() => {
    const io = new AbortController()
    setRows([]); setDetail(null); setDetailId(''); setDetailError(null); setDownloadMessage(null)
    setInstrument(''); setPlatform(''); setLoaded(0)
    downloadIO.current?.abort(); setExporting(false)
    const selected = query?.projects ?? (project ? [project] : [])
    if (!selected.length) { setLoading(false); return () => io.abort() }
    setLoading(true); setError(null)
    void (async () => {
      try {
        const items: ScopedAssessment[] = []
        if (selected.length > 20) throw new ApiError('invalid_request', 422)
        for (const projectId of selected) {
          const cursors = new Set<string>(), ids = new Set<string>()
          let cursor: string | undefined
          do {
            const page = await listAssessments(projectId, { ...query?.filters, cursor, limit: 100, signal: io.signal })
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
        }
        if (!io.signal.aborted) setRows(items)
      } catch (cause) { if (!io.signal.aborted) { setRows([]); setError(cause instanceof ApiError && cause.status === 422 ? 'A consulta não pôde ser concluída com estes filtros. Restrinja o período ou os projetos (até 5.000 avaliações); nenhum total parcial foi exibido.' : cause instanceof ApiError && cause.code === 'state_conflict' ? 'O conjunto mudou durante a consulta. Atualize para carregar todas as páginas novamente; nenhum total parcial foi exibido.' : apiErrorMessage(cause)) } }
      finally { if (!io.signal.aborted) setLoading(false) }
    })()
    return () => { io.abort(); downloadIO.current?.abort() }
  }, [project, query, revision])

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

  async function download() {
    if (!detail || exporting) return
    const io = new AbortController(); downloadIO.current = io
    setExporting(true); setDownloadMessage(null)
    try {
      const result = await exportAssessment(detail.project_id, detail.assessment_id, io.signal)
      if (io.signal.aborted) return
      const url = URL.createObjectURL(result.blob)
      try {
        const link = document.createElement('a'); link.href = url; link.download = result.filename
        document.body.append(link); link.click(); link.remove()
      } finally { setTimeout(() => URL.revokeObjectURL(url), 1000) }
      setDownloadMessage('Arquivo preparado para download.')
    } catch (cause) { if (!io.signal.aborted) setDownloadMessage(apiErrorMessage(cause)) }
    finally { if (!io.signal.aborted) setExporting(false) }
  }

  const instruments = [...new Set(rows.map(row => row.test_code))].sort()
  const selectedInstrument = instrument || instruments[0] || ''
  const visible = rows.filter(row => row.test_code === selectedInstrument && (!platform || row.platform === platform))
  const totals = summarize(visible)
  const dates = countByDate(visible)
  const peak = Math.max(1, ...dates.map(([, count]) => count))
  return <div className="professional-dashboard">
    <h2>Resultados da pesquisa</h2>
    <p className="notice">Resultados descritivos. Este painel não representa avaliação clínica ou diagnóstico.</p>
    {projectsLoading && <p role="status">Carregando projetos…</p>}
    {error && <><p role="alert">{error}</p><button className="button secondary" onClick={() => setRevision(value => value + 1)}>Atualizar consultas</button></>}
    {!projectsLoading && !projects.length && !error && <p role="status">Nenhum projeto disponível para sua conta.</p>}
    {projects.length > 0 && <>
      <label htmlFor="research-project">Projeto</label>
      <select id="research-project" value={project} onChange={event => { if (event.target.value !== project) { setRows([]); setDetail(null); setProject(event.target.value); setQuery(null) } }}>
        {projects.map(item => <option key={item.id} value={item.id}>{item.code} — {item.name}{item.active ? '' : ' (inativo)'}</option>)}
      </select>
      {projects.find(item => item.id === project)?.active && profile.role !== 'consulta' && <SessionInvitation key={`invitation:${project}`} project={projects.find(item => item.id === project)!} profile={profile} />}
      <ResearchFilters key={`filters:${project}`} projects={projects} initialProject={project} loading={loading} onApply={value => { setRows([]); setQuery(value) }} />
      {query && <p className="quiet" role="status">Filtros aplicados: {query.projects.length} projeto(s); {Object.entries(query.filters).filter(([, value]) => Array.isArray(value) ? value.length : !!value).map(([key, value]) => `${filterLabels[key] ?? key}: ${Array.isArray(value) ? value.join(', ') : value}`).join(' · ') || 'sem restrições adicionais'}.</p>}
      {loading && <p role="status">Carregando avaliações… {loaded} recebidas.</p>}
      {!loading && !error && <>
        {!rows.length ? <p role="status">Nenhuma avaliação corresponde aos filtros.</p> : <>
          <div className="dashboard-filters">
            <label>Instrumento<select value={selectedInstrument} onChange={event => { setInstrument(event.target.value); setDetailId('') }}>{instruments.map(code => <option key={code}>{code}</option>)}</select></label>
            <label>Plataforma<select value={platform} onChange={event => { setPlatform(event.target.value); setDetailId('') }}><option value="">Todas</option><option value="web">WEB</option><option value="psychopy">PsychoPy local</option></select></label>
          </div>
          <p className="quiet">Os totais consideram todas as páginas do projeto e os filtros aplicados. Um instrumento por vez. Datas seguem o início registrado; horários legados sem fuso conservam sua referência original.</p>
          <dl className="dashboard-cards">
            <div><dt>Avaliações</dt><dd>{totals.assessments}</dd></div><div><dt>Participantes únicos</dt><dd>{totals.participants}</dd></div>
            {selectedInstrument === 'stroop_go_nogo_ptbr' && <>
              <div><dt>Precisão média</dt><dd>{number(totals.meanAccuracy, 1)}%</dd></div><div><dt>Precisão mediana</dt><dd>{number(totals.medianAccuracy, 1)}%</dd></div>
              <div><dt>Mediana dos tempos por avaliação</dt><dd>{number(totals.medianResponseSeconds, 3)} s</dd></div>
              <div><dt>Omissões</dt><dd>{totals.omissions}</dd></div><div><dt>Comissões</dt><dd>{totals.commissions}</dd></div>
            </>}
          </dl>
          <figure className="dashboard-chart"><figcaption>Avaliações por data de início</figcaption>
            <ul>{dates.map(([day, count]) => <li key={day}><span>{day}</span><meter min={0} max={peak} value={count} aria-label={`${day}: ${count} avaliações`} /><strong>{count}</strong></li>)}</ul>
          </figure>
          {selectedInstrument === 'stroop_go_nogo_ptbr' && <>
            <figure className="dashboard-chart"><figcaption>Precisão média por visita (%)</figcaption><ul>{accuracyByVisit(visible).map(([visit, accuracy]) => <li key={visit}><span>{visit}</span><meter min={0} max={100} value={accuracy} aria-label={`${visit}: ${number(accuracy, 1)}%`} /><strong>{number(accuracy, 1)}</strong></li>)}</ul></figure>
            <figure className="dashboard-chart"><figcaption>Distribuição dos tempos medianos por avaliação</figcaption><ul>{responseDistribution(visible).map(([range, count]) => <li key={range}><span>{range}</span><meter min={0} max={Math.max(1, visible.length)} value={count} aria-label={`${range}: ${count} avaliações`} /><strong>{count}</strong></li>)}</ul><p className="quiet">Avaliações sem acertos não possuem tempo mediano e ficam fora desta distribuição.</p></figure>
            <ResearchVisualizations rows={visible} projects={projects} />
          </>}
          {selectedInstrument !== 'stroop_go_nogo_ptbr' && <GenericInstrumentResults rows={visible} projects={projects} />}
          <ResultsTable rows={visible} projects={projects} onDetail={row => { setDetailProject(row.project_id); setDetailId(row.assessment_id) }} />
        </>}
      </>}
    </>}
    {detailId && !detail && !detailError && <p role="status">Carregando detalhe…</p>}
    {detailError && <p role="alert">{detailError}</p>}
    {detail && <section ref={detailPanel} tabIndex={-1} className="assessment-detail" aria-label="Detalhe da avaliação">
      <h3>Detalhe da avaliação</h3>
      <dl className="assessment-metadata">
        <div><dt>Avaliação</dt><dd>{detail.assessment_id}</dd></div>
        <div><dt>Sessão</dt><dd>{detail.session_id ?? 'Legado sem sessão WEB'}</dd></div>
        <div><dt>Projeto</dt><dd>{projects.find(item => item.id === detail.project_id)?.code ?? detail.project_id} ({detail.project_id})</dd></div>
        <div><dt>Participante</dt><dd>{detail.participant_id}</dd></div><div><dt>Visita</dt><dd>{detail.visit}</dd></div>
        <div><dt>Avaliador</dt><dd>{detail.evaluator_id ?? 'Legado sem identificação técnica'}</dd></div>
        <div><dt>Início</dt><dd>{detail.started_at}</dd></div><div><dt>Conclusão</dt><dd>{detail.completed_at ?? 'Não registrada no legado'}</dd></div>
        <div><dt>Plataforma</dt><dd>{detail.platform === 'web' ? 'WEB' : 'PsychoPy local (importado)'}</dd></div>
        <div><dt>Instrumento</dt><dd>{detail.test_code}</dd></div><div><dt>Versão</dt><dd>{detail.test_version}</dd></div>
        <div><dt>Protocolo</dt><dd>{detail.protocol_id ?? 'Legado sem protocolo WEB'}</dd></div>
        <div><dt>Aplicativo</dt><dd>{detail.app_version ?? 'Não registrado'}</dd></div>
        <div><dt>Período de quadro observado (ms)</dt><dd>{number(detail.frame_period_ms, 3)}</dd></div>
      </dl>
      {'accuracy' in detail.summary && <section aria-label="Contagens das respostas">
        <h4>Contagens das respostas principais</h4>
        <dl className="dashboard-cards">
          <div><dt>Acertos (hit)</dt><dd>{detail.summary.hits}</dd></div>
          <div><dt>Omissões (omission)</dt><dd>{detail.summary.omission_errors}</dd></div>
          <div><dt>Rejeições corretas (correct_rejection)</dt><dd>{detail.summary.correct_rejections}</dd></div>
          <div><dt>Comissões (commission)</dt><dd>{detail.summary.commission_errors}</dd></div>
        </dl>
      </section>}
      <dl>{detail.metrics.map(metric => <div key={metric.metric_code}><dt>{metric.metric_label}</dt><dd>{number(metric.metric_value, 3)} {metric.unit}</dd></div>)}</dl>
      {detail.trials.length > 0 && <div className="table-scroll"><table><caption>Tentativas registradas</caption><thead><tr><th>Tentativa</th><th>Palavra</th><th>Cor</th><th>Condição</th><th>Resposta</th><th>Classificação</th><th>RT (s)</th></tr></thead><tbody>{detail.trials.map(trial => <tr key={trial.trial_number}><td>{trial.trial_number}</td><td>{trial.word}</td><td>{trial.ink_color}</td><td>{trial.condition}</td><td>{trial.key_pressed ?? '—'}</td><td>{trial.error_type}</td><td>{number(trial.reaction_time_seconds, 3)}</td></tr>)}</tbody></table></div>}
      {detail.test_code === 'stroop_go_nogo_ptbr' && <button className="button primary" disabled={exporting} onClick={() => void download()}>{exporting ? 'Preparando arquivo…' : 'Exportar CSV oficial'}</button>}
      {downloadMessage && <p role="status">{downloadMessage}</p>}
      <button className="button secondary" onClick={() => setDetailId('')}>Fechar detalhe</button>
    </section>}
  </div>
}
