import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import { listProjects, listAssessments, getAssessment, exportAssessment } from '../api/assessments'
import type { Assessment, AssessmentDetail, Project } from '../api/assessments'
import { accuracyByVisit, countByDate, responseDistribution, summarize } from '../dashboard/analysis'

type Filters = { participant_id: string; visit: string }
const emptyFilters: Filters = { participant_id: '', visit: '' }
const number = (value: number | null, digits = 0) => value === null ? '—' : value.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits })

export function ProfessionalDashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [project, setProject] = useState('')
  const [projectsLoading, setProjectsLoading] = useState(true)
  const [draft, setDraft] = useState(emptyFilters)
  const [filters, setFilters] = useState(emptyFilters)
  const [rows, setRows] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)
  const [instrument, setInstrument] = useState('')
  const [platform, setPlatform] = useState('')
  const [detail, setDetail] = useState<AssessmentDetail | null>(null)
  const [detailId, setDetailId] = useState('')
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
    if (!project) { setLoading(false); return () => io.abort() }
    setLoading(true); setError(null)
    void (async () => {
      try {
        const items: Assessment[] = []
        const cursors = new Set<string>(), ids = new Set<string>()
        let cursor: string | undefined
        do {
          const page = await listAssessments(project, { participant_id: filters.participant_id || undefined,
            visit: filters.visit || undefined, cursor, limit: 100, signal: io.signal })
          for (const item of page.items) {
            if (ids.has(item.assessment_id)) throw new ApiError('invalid_response', 200)
            ids.add(item.assessment_id); items.push(item)
          }
          cursor = page.next_cursor ?? undefined
          if (cursor && cursors.has(cursor)) throw new ApiError('invalid_response', 200)
          if (cursor) cursors.add(cursor)
          if (io.signal.aborted) return
          setLoaded(items.length)
        } while (cursor)
        if (!io.signal.aborted) setRows(items)
      } catch (cause) { if (!io.signal.aborted) { setRows([]); setError(apiErrorMessage(cause)) } }
      finally { if (!io.signal.aborted) setLoading(false) }
    })()
    return () => { io.abort(); downloadIO.current?.abort() }
  }, [project, filters, revision])

  useEffect(() => {
    const io = new AbortController()
    setDetail(null); setDetailError(null); setDownloadMessage(null)
    downloadIO.current?.abort(); setExporting(false)
    if (detailId) void getAssessment(project, detailId, io.signal).then(value => {
      if (!io.signal.aborted) setDetail(value)
    }, cause => { if (!io.signal.aborted) setDetailError(apiErrorMessage(cause)) })
    return () => io.abort()
  }, [project, detailId])
  useEffect(() => { if (detail) detailPanel.current?.focus() }, [detail])
  useEffect(() => () => downloadIO.current?.abort(), [])

  function apply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setFilters({ participant_id: draft.participant_id.trim(), visit: draft.visit.trim() })
  }
  async function download() {
    if (!detail || exporting) return
    const io = new AbortController(); downloadIO.current = io
    setExporting(true); setDownloadMessage(null)
    try {
      const result = await exportAssessment(project, detail.assessment_id, io.signal)
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
      <select id="research-project" value={project} onChange={event => { setRows([]); setDetail(null); setProject(event.target.value) }}>
        {projects.map(item => <option key={item.id} value={item.id}>{item.code} — {item.name}{item.active ? '' : ' (inativo)'}</option>)}
      </select>
      <form className="dashboard-filters" onSubmit={apply}>
        <label>Participante (código)<input value={draft.participant_id} pattern="[A-Za-z0-9_.-]{1,64}" maxLength={64} onChange={event => setDraft({ ...draft, participant_id: event.target.value })} /></label>
        <label>Visita<input value={draft.visit} pattern="[A-Za-z0-9_.-]{1,64}" maxLength={64} onChange={event => setDraft({ ...draft, visit: event.target.value })} /></label>
        <button className="button primary" type="submit" disabled={loading}>Aplicar filtros</button>
      </form>
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
            <figure className="dashboard-chart"><figcaption>Erros no projeto filtrado</figcaption><ul>{([['Omissões', totals.omissions], ['Comissões', totals.commissions]] as const).map(([kind, count]) => <li key={kind}><span>{kind}</span><meter min={0} max={Math.max(1, totals.omissions, totals.commissions)} value={count} aria-label={`${kind}: ${count}`} /><strong>{count}</strong></li>)}</ul></figure>
            {filters.participant_id && <div className="table-scroll"><table><caption>Evolução descritiva do participante por visita</caption><thead><tr><th>Visita</th><th>Início</th><th>Precisão (%)</th><th>RT mediano (s)</th></tr></thead><tbody>{[...visible].sort((a, b) => a.started_at.localeCompare(b.started_at)).map(row => <tr key={row.assessment_id}><td>{row.visit}</td><td>{row.started_at}</td><td>{'accuracy' in row.summary ? number(row.summary.accuracy, 1) : '—'}</td><td>{'response_time_seconds' in row.summary ? number(row.summary.response_time_seconds, 3) : '—'}</td></tr>)}</tbody></table></div>}
          </>}
          <div className="table-scroll"><table><caption>Avaliações filtradas</caption><thead><tr><th>Participante</th><th>Visita</th><th>Início</th><th>Plataforma</th><th>Versão</th><th>Precisão</th><th>RT mediano (s)</th><th>Detalhe</th></tr></thead>
            <tbody>{visible.map(row => <tr key={row.assessment_id}><td>{row.participant_id}</td><td>{row.visit}</td><td>{row.started_at}</td><td>{row.platform}</td><td>{row.test_version}</td><td>{'accuracy' in row.summary ? number(row.summary.accuracy, 1) : '—'}</td><td>{'response_time_seconds' in row.summary ? number(row.summary.response_time_seconds, 3) : '—'}</td><td><button className="button secondary" onClick={() => setDetailId(row.assessment_id)} aria-label={`Ver avaliação ${row.participant_id}, visita ${row.visit}`}>Ver</button></td></tr>)}</tbody>
          </table></div>
        </>}
      </>}
    </>}
    {detailId && !detail && !detailError && <p role="status">Carregando detalhe…</p>}
    {detailError && <p role="alert">{detailError}</p>}
    {detail && <section ref={detailPanel} tabIndex={-1} className="assessment-detail" aria-label="Detalhe da avaliação">
      <h3>Detalhe da avaliação</h3><p>{detail.participant_id} · {detail.visit} · {detail.platform} · {detail.test_code} · {detail.test_version}</p>
      <p>Início: {detail.started_at}. Protocolo: {detail.protocol_id ?? 'Legado sem protocolo WEB'}. Aplicativo: {detail.app_version ?? 'Não registrado'}.</p>
      <dl>{detail.metrics.map(metric => <div key={metric.metric_code}><dt>{metric.metric_label}</dt><dd>{number(metric.metric_value, 3)} {metric.unit}</dd></div>)}</dl>
      {detail.trials.length > 0 && <div className="table-scroll"><table><caption>Tentativas registradas</caption><thead><tr><th>Tentativa</th><th>Palavra</th><th>Cor</th><th>Condição</th><th>Resposta</th><th>Classificação</th><th>RT (s)</th></tr></thead><tbody>{detail.trials.map(trial => <tr key={trial.trial_number}><td>{trial.trial_number}</td><td>{trial.word}</td><td>{trial.ink_color}</td><td>{trial.condition}</td><td>{trial.key_pressed ?? '—'}</td><td>{trial.error_type}</td><td>{number(trial.reaction_time_seconds, 3)}</td></tr>)}</tbody></table></div>}
      {detail.test_code === 'stroop_go_nogo_ptbr' && <button className="button primary" disabled={exporting} onClick={() => void download()}>{exporting ? 'Preparando arquivo…' : 'Exportar CSV oficial'}</button>}
      {downloadMessage && <p role="status">{downloadMessage}</p>}
      <button className="button secondary" onClick={() => setDetailId('')}>Fechar detalhe</button>
    </section>}
  </div>
}
