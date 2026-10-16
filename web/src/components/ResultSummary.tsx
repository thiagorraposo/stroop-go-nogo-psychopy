import { useEffect, useRef } from 'react'
import { formatHalfEven } from '../experiment/summary'
import type { ResultSummary } from '../experiment/summary'

export function ResultSummaryPanel({ summary, onFinish }: { summary: ResultSummary; onFinish: () => void }) {
  const panel = useRef<HTMLElement>(null)
  useEffect(() => { panel.current?.focus({ preventScroll: true }) }, [])
  return <section ref={panel} className="content-card result-summary" tabIndex={-1} aria-labelledby="result-title">
    <p className="eyebrow">Bloco principal concluído</p>
    <h1 id="result-title">Resumo da execução</h1>
    <p className="lead">Dados descritivos das {summary.total_trials} tentativas principais. O treino não faz parte deste resultado.</p>
    <dl className="result-highlights">
      <div><dt>Precisão total</dt><dd>{formatHalfEven(summary.accuracy, 0)}%</dd></div>
      <div><dt>Tempo de reação</dt><dd>{summary.response_time === null ? '—' : `${formatHalfEven(summary.response_time, 3)} s`}</dd></div>
    </dl>
    <p className="quiet">O tempo de reação é a mediana das respostas corretas nas tentativas em que era necessário responder.</p>
    <dl className="result-counts">
      <div><dt>Acertos Go</dt><dd>{summary.hits}</dd></div>
      <div><dt>Omissões</dt><dd>{summary.omission_errors}</dd></div>
      <div><dt>Rejeições corretas</dt><dd>{summary.correct_rejections}</dd></div>
      <div><dt>Respostas indevidas</dt><dd>{summary.commission_errors}</dd></div>
    </dl>
    <p>Este resumo descreve apenas esta execução e não representa diagnóstico ou avaliação clínica.</p>
    <p role="status" className="notice">Esta execução local ainda não possui confirmação de recebimento pela equipe.</p>
    <button className="button primary" onClick={onFinish}>Finalizar</button>
  </section>
}
