import { useEffect, useRef } from 'react'
import { formatHalfEven } from '../experiment/summary'
import type { DisplaySummary } from '../experiment/summary'
import { JourneyIndicator } from './JourneyIndicator'

export function ResultSummaryPanel({ summary, onFinish, delivery = 'local', message, canRetry = false,
  busy = false, onRetry, onNewInvitation }: {
  summary: DisplaySummary; onFinish: () => void; delivery?: 'local' | 'sending' | 'pending' | 'saved';
  message?: string | null; canRetry?: boolean; busy?: boolean; onRetry?: () => void; onNewInvitation?: () => void
}) {
  const panel = useRef<HTMLElement>(null)
  useEffect(() => { panel.current?.focus({ preventScroll: true }) }, [])
  return <section ref={panel} className="content-card result-summary" tabIndex={-1} aria-labelledby="result-title">
    <JourneyIndicator current={4} />
    <p className="eyebrow">Tarefa principal concluída</p>
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
    {delivery === 'saved' && <p className="participant-thanks">Tarefa concluída. Obrigado por participar.</p>}
    <p role="status" className={`delivery-status delivery-${delivery}`}>
      {delivery === 'saved' ? 'Resultado recebido pela equipe.' : delivery === 'sending'
        ? 'Enviando o resultado. Aguarde a confirmação de recebimento.' : delivery === 'pending'
          ? 'O recebimento ainda não foi confirmado. Você pode reenviar o mesmo resultado sem repetir a tarefa.'
          : 'Esta execução local ainda não possui confirmação de recebimento pela equipe.'}
    </p>
    {message && <p role="alert" className="notice">{message}</p>}
    {delivery === 'pending' && <>
      <p>Ao sair sem confirmação, este navegador não conservará o resultado.</p>
      <button className="button primary" onClick={onRetry} disabled={!canRetry || busy}>Reenviar resultado</button>{' '}
    </>}
    <button className={delivery === 'pending' ? 'button secondary' : 'button primary'} onClick={onFinish}
      disabled={busy || delivery === 'sending'}>{busy ? 'Encerrando acesso…' : delivery === 'pending' ? 'Sair sem confirmação' : 'Finalizar'}</button>
    {delivery === 'saved' && onNewInvitation && <>{' '}<button className="button secondary" disabled={busy} onClick={onNewInvitation}>Utilizar outro convite</button></>}
  </section>
}
