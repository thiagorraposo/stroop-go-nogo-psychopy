import { useState } from 'react'
import type { Assessment, Project, StroopSummary } from '../api/assessments'
import { formatMetric, median, responseDistribution } from '../dashboard/analysis'

type Row = Assessment & { project_id: string }
type Props = { rows: readonly Row[]; projects: readonly Project[] }
const projectName = (id: string, projects: readonly Project[]) => projects.find(project => project.id === id)?.code ?? id
const identity = (row: Row) => JSON.stringify([row.project_id, row.participant_id])
const rowKey = (row: Row) => JSON.stringify([row.project_id, row.assessment_id])
const order = (a: Row, b: Row) => a.started_at.localeCompare(b.started_at) || a.assessment_id.localeCompare(b.assessment_id)
const stroop = (row: Row): row is Row & { summary: StroopSummary } => !('metrics' in row.summary)
const value = (number: number | null) => number === null ? 'Ausente' : formatMetric(number, 3)

/** Visuais exclusivamente descritivos do conjunto recebido; nenhuma inferência clínica (REQ-REL-005). */
export function ResearchVisualizations({ rows, projects }: Props) {
  const [chosen, setChosen] = useState('')
  const eligible = rows.filter(stroop)
  const participants = [...new Map(eligible.map(row => [identity(row), row])).entries()]
    .sort(([a], [b]) => a.localeCompare(b))
  const selected = participants.some(([key]) => key === chosen) ? chosen : participants[0]?.[0] ?? ''
  const longitudinal = eligible.filter(row => identity(row) === selected).sort(order)

  // 1. Totais por Projeto
  const projectTotals = [...new Set(eligible.map(row => row.project_id))].sort().map(id => ({
    id,
    omissions: eligible.filter(row => row.project_id === id).reduce((sum, row) => sum + row.summary.omission_errors, 0),
    commissions: eligible.filter(row => row.project_id === id).reduce((sum, row) => sum + row.summary.commission_errors, 0),
  }))
  const peak = Math.max(1, ...projectTotals.flatMap(project => [project.omissions, project.commissions]))
  const timePeak = Math.max(0.001, ...longitudinal.map(row => row.summary.response_time_seconds ?? 0))

  // 2. Distribuição de Tempos de Reação (RTs)
  const rtDist = responseDistribution(eligible)
  const missingRtCount = eligible.filter(row => row.summary.response_time_seconds === null).length
  const rtDistPeak = Math.max(1, ...rtDist.map(([, count]) => count), missingRtCount)

  // 3. Precisão e Erros por Condição Experimental (Go vs No-Go)
  const totalGoTrials = eligible.reduce((acc, r) => acc + r.summary.total_go_trials, 0)
  const totalGoHits = eligible.reduce((acc, r) => acc + r.summary.hits, 0)
  const totalGoOmissions = eligible.reduce((acc, r) => acc + r.summary.omission_errors, 0)
  const meanGoAccuracy = totalGoTrials > 0 ? (totalGoHits / totalGoTrials) * 100 : null

  const totalNoGoTrials = eligible.reduce((acc, r) => acc + r.summary.total_no_go_trials, 0)
  const totalNoGoCorrectRejections = eligible.reduce((acc, r) => acc + r.summary.correct_rejections, 0)
  const totalNoGoCommissions = eligible.reduce((acc, r) => acc + r.summary.commission_errors, 0)
  const meanNoGoAccuracy = totalNoGoTrials > 0 ? (totalNoGoCorrectRejections / totalNoGoTrials) * 100 : null

  // 4. Totais por Visita
  const visitKeys = [...new Set(eligible.map(r => r.visit))].sort()
  const visitTotals = visitKeys.map(visit => {
    const group = eligible.filter(r => r.visit === visit)
    const accList = group.map(r => r.summary.accuracy).filter((x): x is number => x !== null)
    const rtList = group.map(r => r.summary.response_time_seconds).filter((x): x is number => x !== null)
    return {
      visit,
      count: group.length,
      omissions: group.reduce((sum, r) => sum + r.summary.omission_errors, 0),
      commissions: group.reduce((sum, r) => sum + r.summary.commission_errors, 0),
      meanAccuracy: accList.length ? accList.reduce((a, b) => a + b, 0) / accList.length : null,
      medianRt: median(rtList),
    }
  })

  // 5. Totais por Avaliador
  const evaluatorKeys = [...new Set(eligible.map(r => r.evaluator_id ?? 'Não identificado'))].sort()
  const evaluatorTotals = evaluatorKeys.map(evaluator => {
    const group = eligible.filter(r => (r.evaluator_id ?? 'Não identificado') === evaluator)
    const accList = group.map(r => r.summary.accuracy).filter((x): x is number => x !== null)
    return {
      evaluator,
      count: group.length,
      omissions: group.reduce((sum, r) => sum + r.summary.omission_errors, 0),
      commissions: group.reduce((sum, r) => sum + r.summary.commission_errors, 0),
      meanAccuracy: accList.length ? accList.reduce((a, b) => a + b, 0) / accList.length : null,
    }
  })

  if (!eligible.length) return null

  return (
    <section aria-label="Comparações descritivas" className="research-visualizations-panel">
      {/* 1. Comparações de erros por projeto */}
      <figure>
        <figcaption>Omissões e comissões por projeto (contagem)</figcaption>
        <ul>
          {projectTotals.map(project => (
            <li key={project.id}>
              {projectName(project.id, projects)}:
              <meter
                min={0}
                max={peak}
                value={project.omissions}
                aria-label={`${projectName(project.id, projects)}: ${project.omissions} omissões`}
              />{' '}
              Omissões: {project.omissions};
              <meter
                min={0}
                max={peak}
                value={project.commissions}
                aria-label={`${projectName(project.id, projects)}: ${project.commissions} comissões`}
              />{' '}
              Comissões: {project.commissions}
            </li>
          ))}
        </ul>
        <div className="table-scroll">
          <table>
            <caption>Contagens de erros por projeto</caption>
            <thead>
              <tr>
                <th>Projeto</th>
                <th>Omissões</th>
                <th>Comissões</th>
              </tr>
            </thead>
            <tbody>
              {projectTotals.map(project => (
                <tr key={project.id}>
                  <td>{projectName(project.id, projects)}</td>
                  <td>{project.omissions}</td>
                  <td>{project.commissions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </figure>

      {/* 2. Evolução longitudinal do participante */}
      <div className="longitudinal-section">
        <h3>Evolução longitudinal do participante (REQ-REL-005)</h3>
        <label>
          Participante para evolução
          <select value={selected} onChange={event => setChosen(event.target.value)}>
            {participants.map(([key, row]) => (
              <option key={key} value={key}>
                {projectName(row.project_id, projects)} · {row.participant_id}
              </option>
            ))}
          </select>
        </label>
        <p className="quiet">
          Visitas repetidas representam avaliações distintas, ordenadas pelo início registrado e identificador.
          Datas legadas conservam a referência civil; não se atribui fuso.
        </p>
        <figure>
          <figcaption>Precisão por avaliação (%)</figcaption>
          <ul>
            {longitudinal.map(row => (
              <li key={rowKey(row)}>
                {row.visit} · {row.started_at} · {row.assessment_id}: {value(row.summary.accuracy)}
                {row.summary.accuracy === null ? '' : '%'}
                {row.summary.accuracy !== null && (
                  <meter
                    min={0}
                    max={100}
                    value={row.summary.accuracy}
                    aria-label={`${row.assessment_id}: precisão ${row.summary.accuracy}%`}
                  />
                )}
              </li>
            ))}
          </ul>
        </figure>
        <figure>
          <figcaption>Tempo mediano de resposta por avaliação (s)</figcaption>
          <ul>
            {longitudinal.map(row => (
              <li key={rowKey(row)}>
                {row.visit} · {row.started_at} · {row.assessment_id}:{' '}
                {value(row.summary.response_time_seconds)}
                {row.summary.response_time_seconds === null ? '' : ' s'}
                {row.summary.response_time_seconds !== null && (
                  <meter
                    min={0}
                    max={timePeak}
                    value={row.summary.response_time_seconds}
                    aria-label={`${row.assessment_id}: tempo mediano ${row.summary.response_time_seconds} s`}
                  />
                )}
              </li>
            ))}
          </ul>
        </figure>
        <div className="table-scroll">
          <table>
            <caption>Evolução do participante por avaliação</caption>
            <thead>
              <tr>
                <th>Projeto</th>
                <th>Participante</th>
                <th>Visita</th>
                <th>Início</th>
                <th>Avaliação</th>
                <th>Precisão (%)</th>
                <th>Tempo mediano (s)</th>
              </tr>
            </thead>
            <tbody>
              {longitudinal.map(row => (
                <tr key={rowKey(row)}>
                  <td>{projectName(row.project_id, projects)}</td>
                  <td>{row.participant_id}</td>
                  <td>{row.visit}</td>
                  <td>{row.started_at}</td>
                  <td>{row.assessment_id}</td>
                  <td>{value(row.summary.accuracy)}</td>
                  <td>{value(row.summary.response_time_seconds)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. Distribuição de Tempos de Reação (RTs) */}
      <div className="rt-distribution-section">
        <h3>Distribuição de tempos de reação (RT mediano)</h3>
        <p className="quiet">
          Distribuição dos tempos medianos de reação em estímulos Go com resposta correta (hits).
          Ausências são registradas explicitamente sem substituição arbitrária por zero.
        </p>
        <figure>
          <figcaption>Distribuição de tempos de reação (contagem de avaliações)</figcaption>
          <ul>
            {rtDist.map(([range, count]) => (
              <li key={range}>
                {range}: {count} avaliações
                <meter
                  min={0}
                  max={rtDistPeak}
                  value={count}
                  aria-label={`Faixa ${range}: ${count} avaliações`}
                />
              </li>
            ))}
            {missingRtCount > 0 && (
              <li>
                Ausente (sem acertos em Go): {missingRtCount} avaliações
                <meter
                  min={0}
                  max={rtDistPeak}
                  value={missingRtCount}
                  aria-label={`RT ausente: ${missingRtCount} avaliações`}
                />
              </li>
            )}
          </ul>
        </figure>
        <div className="table-scroll">
          <table>
            <caption>Distribuição de tempos de reação</caption>
            <thead>
              <tr>
                <th>Faixa de RT</th>
                <th>Avaliações</th>
                <th>Proporção sobre o total (%)</th>
              </tr>
            </thead>
            <tbody>
              {rtDist.map(([range, count]) => (
                <tr key={range}>
                  <td>{range}</td>
                  <td className="tabular-nums">{count}</td>
                  <td className="tabular-nums">
                    {formatMetric((count / eligible.length) * 100, 1)}%
                  </td>
                </tr>
              ))}
              {missingRtCount > 0 && (
                <tr>
                  <td>Ausente (sem acertos em Go)</td>
                  <td className="tabular-nums">{missingRtCount}</td>
                  <td className="tabular-nums">
                    {formatMetric((missingRtCount / eligible.length) * 100, 1)}%
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Precisão e Erros por Condição Experimental (Go vs No-Go) */}
      <div className="experimental-conditions-section">
        <h3>Precisão e respostas por condição experimental</h3>
        <p className="quiet">
          Desempenho comparativo entre estímulos Go (resposta motora requerida) e No-Go (inibição de resposta).
        </p>
        <figure>
          <figcaption>Precisão média por condição (%)</figcaption>
          <ul>
            <li>
              Condição Go: {value(meanGoAccuracy)}%
              {meanGoAccuracy !== null && (
                <meter
                  min={0}
                  max={100}
                  value={meanGoAccuracy}
                  aria-label={`Condição Go: precisão média ${formatMetric(meanGoAccuracy, 1)}%`}
                />
              )}
            </li>
            <li>
              Condição No-Go: {value(meanNoGoAccuracy)}%
              {meanNoGoAccuracy !== null && (
                <meter
                  min={0}
                  max={100}
                  value={meanNoGoAccuracy}
                  aria-label={`Condição No-Go: precisão média ${formatMetric(meanNoGoAccuracy, 1)}%`}
                />
              )}
            </li>
          </ul>
        </figure>
        <div className="table-scroll">
          <table>
            <caption>Desempenho por condição experimental (Go / No-Go)</caption>
            <thead>
              <tr>
                <th>Condição</th>
                <th>Tentativas</th>
                <th>Acertos / Inibições corretas</th>
                <th>Erros (Omissões / Comissões)</th>
                <th>Precisão média (%)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Go (resposta com barra de espaço)</td>
                <td className="tabular-nums">{totalGoTrials}</td>
                <td className="tabular-nums">{totalGoHits} (acertos)</td>
                <td className="tabular-nums">{totalGoOmissions} (omissões)</td>
                <td className="tabular-nums">{value(meanGoAccuracy)}%</td>
              </tr>
              <tr>
                <td>No-Go (inibição de resposta motora)</td>
                <td className="tabular-nums">{totalNoGoTrials}</td>
                <td className="tabular-nums">{totalNoGoCorrectRejections} (rejeições corretas)</td>
                <td className="tabular-nums">{totalNoGoCommissions} (comissões)</td>
                <td className="tabular-nums">{value(meanNoGoAccuracy)}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Comparações por Visita e Avaliador */}
      <div className="visit-evaluator-section">
        <h3>Comparações por visita e avaliador</h3>
        <div className="table-scroll">
          <table>
            <caption>Desempenho e contagens de erros por visita</caption>
            <thead>
              <tr>
                <th>Visita</th>
                <th>Avaliações</th>
                <th>Omissões</th>
                <th>Comissões</th>
                <th>Precisão média (%)</th>
                <th>RT mediano (s)</th>
              </tr>
            </thead>
            <tbody>
              {visitTotals.map(item => (
                <tr key={item.visit}>
                  <td>{item.visit}</td>
                  <td className="tabular-nums">{item.count}</td>
                  <td className="tabular-nums">{item.omissions}</td>
                  <td className="tabular-nums">{item.commissions}</td>
                  <td className="tabular-nums">{value(item.meanAccuracy)}%</td>
                  <td className="tabular-nums">{value(item.medianRt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="table-scroll">
          <table>
            <caption>Desempenho e contagens de erros por avaliador</caption>
            <thead>
              <tr>
                <th>Avaliador responsável</th>
                <th>Avaliações</th>
                <th>Omissões</th>
                <th>Comissões</th>
                <th>Precisão média (%)</th>
              </tr>
            </thead>
            <tbody>
              {evaluatorTotals.map(item => (
                <tr key={item.evaluator}>
                  <td>{item.evaluator}</td>
                  <td className="tabular-nums">{item.count}</td>
                  <td className="tabular-nums">{item.omissions}</td>
                  <td className="tabular-nums">{item.commissions}</td>
                  <td className="tabular-nums">{value(item.meanAccuracy)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}

/** Metricas demonstrativas registradas preservam unidades; demais instrumentos recebem tabela neutra. */
export function GenericInstrumentResults({ rows, projects }: Props) {
  const generic = rows.filter(row => 'metrics' in row.summary).sort(order)
  if (!generic.length) return null
  const demo = generic.filter(row => row.test_code === 'instrumento_sintetico_demo')
  const registered = [
    { code: 'demo_total', label: 'Total demonstrativo', unit: 'count' },
    { code: 'demo_mean', label: 'Média demonstrativa', unit: 'unit' },
  ]
  return (
    <section aria-label="Resultados por instrumento">
      {!!demo.length && (
        <>
          <h3>Demonstração sintética</h3>
          <p>Métricas demonstrativas descritivas; não constituem avaliação clínica.</p>
          {registered.map(metric => {
            const numbers = demo.flatMap(row =>
              'metrics' in row.summary && row.summary.metrics[metric.code] !== undefined
                ? [row.summary.metrics[metric.code]!]
                : []
            )
            const maximum = Math.max(1, ...numbers)
            const minimum = Math.min(0, ...numbers)
            return (
              <figure key={metric.code}>
                <figcaption>
                  {metric.label} ({metric.unit}) por avaliação
                </figcaption>
                <dl className="dashboard-cards">
                  {demo.map(row => {
                    const number =
                      'metrics' in row.summary ? row.summary.metrics[metric.code] ?? null : null
                    return (
                      <div key={rowKey(row)}>
                        <dt>
                          {projectName(row.project_id, projects)} · {row.participant_id} · {row.visit} ·{' '}
                          {row.assessment_id}
                        </dt>
                        <dd>
                          {value(number)} {number === null ? '' : metric.unit}
                        </dd>
                      </div>
                    )
                  })}
                </dl>
                <ul>
                  {demo.map(row => {
                    const number =
                      'metrics' in row.summary ? row.summary.metrics[metric.code] ?? null : null
                    return (
                      <li key={rowKey(row)}>
                        {projectName(row.project_id, projects)} · {row.assessment_id}: {value(number)}{' '}
                        {number === null ? '' : metric.unit}
                        {number !== null && (
                          <meter
                            min={minimum}
                            max={maximum}
                            value={number}
                            aria-label={`${row.assessment_id}: ${metric.label} ${number} ${metric.unit}`}
                          />
                        )}
                      </li>
                    )
                  })}
                </ul>
              </figure>
            )
          })}
        </>
      )}
      <div className="table-scroll">
        <table>
          <caption>Métricas por instrumento e avaliação</caption>
          <thead>
            <tr>
              <th>Projeto</th>
              <th>Instrumento</th>
              <th>Participante</th>
              <th>Visita</th>
              <th>Início</th>
              <th>Avaliação</th>
              <th>Métrica</th>
              <th>Valor</th>
              <th>Unidade</th>
            </tr>
          </thead>
          <tbody>
            {generic.flatMap(row =>
              'metrics' in row.summary
                ? Object.entries(row.summary.metrics)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([code, number]) => {
                      const metric =
                        row.test_code === 'instrumento_sintetico_demo'
                          ? registered.find(m => m.code === code)
                          : undefined
                      return (
                        <tr key={JSON.stringify([row.project_id, row.assessment_id, code])}>
                          <td>{projectName(row.project_id, projects)}</td>
                          <td>{row.test_code}</td>
                          <td>{row.participant_id}</td>
                          <td>{row.visit}</td>
                          <td>{row.started_at}</td>
                          <td>{row.assessment_id}</td>
                          <td>{metric?.label ?? code}</td>
                          <td>{value(number)}</td>
                          <td>{metric?.unit ?? 'Não informada'}</td>
                        </tr>
                      )
                    })
                : []
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
