import type { Assessment, Project } from '../api/assessments'
import { formatMetric as number } from '../dashboard/analysis'

export type ScopedAssessment = Assessment & { project_id: string }
export function ResultsTable({ rows, projects, onDetail }: {
  rows: ScopedAssessment[]; projects: Project[]; onDetail(row: ScopedAssessment): void
}) {
  const stroop = rows[0]?.test_code === 'stroop_go_nogo_ptbr'
  return <div className="table-scroll"><table className={stroop ? 'results-table stroop-results' : 'results-table'}>
    <caption>Avaliações filtradas</caption>
    <thead><tr><th>Projeto</th><th>Participante</th><th>Visita</th><th>Início</th><th>Plataforma</th><th>Avaliador</th><th>Versão</th>
      {stroop && <><th>Precisão (%)</th><th>Precisão Go (%)</th><th>Precisão No-Go (%)</th><th>Omissões</th><th>Comissões</th><th>Acertos</th><th>Rejeições corretas</th><th>RT mediano (s)</th></>}
      <th>Detalhe</th></tr></thead>
    <tbody>{rows.map(row => <tr key={`${row.project_id}:${row.assessment_id}`}>
      <td>{projects.find(item => item.id === row.project_id)?.code ?? row.project_id}</td>
      <td className="tabular-nums"><strong>{row.participant_id}</strong></td>
      <td>{row.visit}</td>
      <td className="tabular-nums">{row.started_at}</td>
      <td>
        <span className={`badge-platform ${row.platform === 'web' ? 'badge-web' : 'badge-legacy'}`}>
          {row.platform === 'web' ? 'WEB' : 'PsychoPy local'}
        </span>
      </td>
      <td>{row.evaluator_id ?? 'Legado sem identificação técnica'}</td>
      <td className="tabular-nums">{row.test_version}</td>
      {stroop && 'accuracy' in row.summary && <>
        <td className="tabular-nums">{number(row.summary.accuracy, 1)}</td>
        <td className="tabular-nums">{number(row.summary.accuracy_go_trials, 1)}</td>
        <td className="tabular-nums">{number(row.summary.accuracy_no_go_trials, 1)}</td>
        <td className="tabular-nums">{row.summary.omission_errors}</td>
        <td className="tabular-nums">{row.summary.commission_errors}</td>
        <td className="tabular-nums">{row.summary.hits}</td>
        <td className="tabular-nums">{row.summary.correct_rejections}</td>
        <td className="tabular-nums">{number(row.summary.response_time_seconds, 3)}</td>
      </>}
      <td>
        <button
          className="button secondary button-sm"
          onClick={() => onDetail(row)}
          aria-label={`Ver avaliação ${row.participant_id}, visita ${row.visit}, projeto ${projects.find(item => item.id === row.project_id)?.code ?? row.project_id}`}
          title={projects.find(item => item.id === row.project_id)?.code}
        >
          Ver
        </button>
      </td>
    </tr>)}</tbody>
  </table></div>
}
