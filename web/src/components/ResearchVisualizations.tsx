import { useState } from 'react'
import type { Assessment, Project, StroopSummary } from '../api/assessments'
import { formatMetric } from '../dashboard/analysis'

type Row = Assessment & { project_id: string }
type Props = { rows: readonly Row[]; projects: readonly Project[] }
const projectName = (id: string, projects: readonly Project[]) => projects.find(project => project.id === id)?.code ?? id
const identity = (row: Row) => JSON.stringify([row.project_id, row.participant_id])
const rowKey = (row: Row) => JSON.stringify([row.project_id, row.assessment_id])
const order = (a: Row, b: Row) => a.started_at.localeCompare(b.started_at) || a.assessment_id.localeCompare(b.assessment_id)
const stroop = (row: Row): row is Row & { summary: StroopSummary } => !('metrics' in row.summary)
const value = (number: number | null) => number === null ? 'Ausente' : formatMetric(number, 3)

/** Visuais exclusivamente descritivos do conjunto recebido; nenhuma consulta adicional. */
export function ResearchVisualizations({ rows, projects }: Props) {
  const [chosen, setChosen] = useState('')
  const eligible = rows.filter(stroop)
  const participants = [...new Map(eligible.map(row => [identity(row), row])).entries()]
    .sort(([a], [b]) => a.localeCompare(b))
  const selected = participants.some(([key]) => key === chosen) ? chosen : participants[0]?.[0] ?? ''
  const longitudinal = eligible.filter(row => identity(row) === selected).sort(order)
  const projectTotals = [...new Set(eligible.map(row => row.project_id))].sort().map(id => ({
    id, omissions: eligible.filter(row => row.project_id === id).reduce((sum, row) => sum + row.summary.omission_errors, 0),
    commissions: eligible.filter(row => row.project_id === id).reduce((sum, row) => sum + row.summary.commission_errors, 0),
  }))
  const peak = Math.max(1, ...projectTotals.flatMap(project => [project.omissions, project.commissions]))
  const timePeak = Math.max(0.001, ...longitudinal.map(row => row.summary.response_time_seconds ?? 0))
  if (!eligible.length) return null
  return <section aria-label="Comparações descritivas">
    <figure><figcaption>Omissões e comissões por projeto (contagem)</figcaption>
      <ul>{projectTotals.map(project => <li key={project.id}>{projectName(project.id, projects)}:
        <meter min={0} max={peak} value={project.omissions} aria-label={`${projectName(project.id, projects)}: ${project.omissions} omissões`} /> Omissões: {project.omissions};
        <meter min={0} max={peak} value={project.commissions} aria-label={`${projectName(project.id, projects)}: ${project.commissions} comissões`} /> Comissões: {project.commissions}
      </li>)}</ul>
      <div className="table-scroll"><table><caption>Contagens de erros por projeto</caption><thead><tr><th>Projeto</th><th>Omissões</th><th>Comissões</th></tr></thead>
        <tbody>{projectTotals.map(project => <tr key={project.id}><td>{projectName(project.id, projects)}</td><td>{project.omissions}</td><td>{project.commissions}</td></tr>)}</tbody></table></div>
    </figure>
    <label>Participante para evolução<select value={selected} onChange={event => setChosen(event.target.value)}>
      {participants.map(([key, row]) => <option key={key} value={key}>{projectName(row.project_id, projects)} · {row.participant_id}</option>)}
    </select></label>
    <p>Visitas repetidas representam avaliações distintas, ordenadas pelo início registrado e identificador. Datas legadas conservam a referência civil; não se atribui fuso.</p>
    <figure><figcaption>Precisão por avaliação (%)</figcaption><ul>{longitudinal.map(row => <li key={rowKey(row)}>{row.visit} · {row.started_at} · {row.assessment_id}: {value(row.summary.accuracy)}{row.summary.accuracy === null ? '' : '%'}
      {row.summary.accuracy !== null && <meter min={0} max={100} value={row.summary.accuracy} aria-label={`${row.assessment_id}: precisão ${row.summary.accuracy}%`} />}
    </li>)}</ul></figure>
    <figure><figcaption>Tempo mediano de resposta por avaliação (s)</figcaption><ul>{longitudinal.map(row => <li key={rowKey(row)}>{row.visit} · {row.started_at} · {row.assessment_id}: {value(row.summary.response_time_seconds)}{row.summary.response_time_seconds === null ? '' : ' s'}
      {row.summary.response_time_seconds !== null && <meter min={0} max={timePeak} value={row.summary.response_time_seconds} aria-label={`${row.assessment_id}: tempo mediano ${row.summary.response_time_seconds} s`} />}
    </li>)}</ul></figure>
    <div className="table-scroll"><table><caption>Evolução do participante por avaliação</caption><thead><tr><th>Projeto</th><th>Participante</th><th>Visita</th><th>Início</th><th>Avaliação</th><th>Precisão (%)</th><th>Tempo mediano (s)</th></tr></thead>
      <tbody>{longitudinal.map(row => <tr key={rowKey(row)}><td>{projectName(row.project_id, projects)}</td><td>{row.participant_id}</td><td>{row.visit}</td><td>{row.started_at}</td><td>{row.assessment_id}</td><td>{value(row.summary.accuracy)}</td><td>{value(row.summary.response_time_seconds)}</td></tr>)}</tbody></table></div>
  </section>
}

/** Metricas demonstrativas registradas preservam unidades; demais instrumentos recebem tabela neutra. */
export function GenericInstrumentResults({ rows, projects }: Props) {
  const generic = rows.filter(row => 'metrics' in row.summary).sort(order)
  if (!generic.length) return null
  const demo = generic.filter(row => row.test_code === 'instrumento_sintetico_demo')
  const registered = [{ code: 'demo_total', label: 'Total demonstrativo', unit: 'count' }, { code: 'demo_mean', label: 'Média demonstrativa', unit: 'unit' }]
  return <section aria-label="Resultados por instrumento">
    {!!demo.length && <><h3>Demonstração sintética</h3><p>Métricas demonstrativas descritivas; não constituem avaliação clínica.</p>
      {registered.map(metric => {
        const numbers = demo.flatMap(row => 'metrics' in row.summary && row.summary.metrics[metric.code] !== undefined ? [row.summary.metrics[metric.code]!] : [])
        const maximum = Math.max(1, ...numbers)
        const minimum = Math.min(0, ...numbers)
        return <figure key={metric.code}><figcaption>{metric.label} ({metric.unit}) por avaliação</figcaption>
          <dl className="dashboard-cards">{demo.map(row => {
            const number = 'metrics' in row.summary ? row.summary.metrics[metric.code] ?? null : null
            return <div key={rowKey(row)}><dt>{projectName(row.project_id, projects)} · {row.participant_id} · {row.visit} · {row.assessment_id}</dt><dd>{value(number)} {number === null ? '' : metric.unit}</dd></div>
          })}</dl>
          <ul>{demo.map(row => {
            const number = 'metrics' in row.summary ? row.summary.metrics[metric.code] ?? null : null
            return <li key={rowKey(row)}>{projectName(row.project_id, projects)} · {row.assessment_id}: {value(number)} {number === null ? '' : metric.unit}
              {number !== null && <meter min={minimum} max={maximum} value={number} aria-label={`${row.assessment_id}: ${metric.label} ${number} ${metric.unit}`} />}</li>
          })}</ul></figure>
      })}</>}
    <div className="table-scroll"><table><caption>Métricas por instrumento e avaliação</caption><thead><tr><th>Projeto</th><th>Instrumento</th><th>Participante</th><th>Visita</th><th>Início</th><th>Avaliação</th><th>Métrica</th><th>Valor</th><th>Unidade</th></tr></thead>
      <tbody>{generic.flatMap(row => 'metrics' in row.summary ? Object.entries(row.summary.metrics).sort(([a], [b]) => a.localeCompare(b)).map(([code, number]) => {
        const metric = row.test_code === 'instrumento_sintetico_demo' ? registered.find(metric => metric.code === code) : undefined
        return <tr key={JSON.stringify([row.project_id, row.assessment_id, code])}><td>{projectName(row.project_id, projects)}</td><td>{row.test_code}</td><td>{row.participant_id}</td><td>{row.visit}</td><td>{row.started_at}</td><td>{row.assessment_id}</td><td>{metric?.label ?? code}</td><td>{value(number)}</td><td>{metric?.unit ?? 'Não informada'}</td></tr>
      }) : [])}</tbody></table></div>
  </section>
}
