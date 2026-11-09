import { flushSync } from 'react-dom'
import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import type { FormEvent } from 'react'
import { ParticipantRun } from '../participant/ParticipantRun'
import { PracticePreparation } from './PracticePreparation'
import { ResultSummaryPanel } from './ResultSummary'
import { JourneyIndicator } from './JourneyIndicator'
import { W16TimingCapturePanel } from './W16TimingCapturePanel'
import { w16CaptureEnabled } from '../experiment/w16-capture'
import type { MainTimingTrace } from '../experiment/main-engine'

// Coordena montagens consecutivas/StrictMode na mesma pagina. A trava nativa
// coordena abas diferentes sem gravar credenciais ou resultados em storage.
let reservation: Promise<void> = Promise.resolve()

export function ParticipantFlow({ onBack }: { onBack: () => void }) {
  const [run] = useState(() => new ParticipantRun())
  const view = useSyncExternalStore(run.subscribe, run.getSnapshot)
  const [revision, setRevision] = useState(0)
  const [code, setCode] = useState('')
  const [codeError, setCodeError] = useState<string | null>(null)
  const [closed, setClosed] = useState(false)
  const [timingTraces, setTimingTraces] = useState<MainTimingTrace[]>([])
  const captureTiming = w16CaptureEnabled(import.meta.env.VITE_W16_TIMING_CAPTURE, window.location.search)
  const panel = useRef<HTMLElement>(null)
  const codeInput = useRef<HTMLInputElement>(null)

  useEffect(() => {
    let active = true
    let release: () => void = () => undefined
    const held = new Promise<void>(resolve => { release = resolve })
    const close = () => {
      active = false
      flushSync(() => { run.dispose('page_closed', true); setCode(''); setCodeError(null) })
      release()
    }
    const restore = (event: PageTransitionEvent) => { if (event.persisted) window.location.reload() }
    window.addEventListener('pagehide', close)
    window.addEventListener('pageshow', restore)
    const cleanup = () => {
      active = false; run.dispose(); release()
      window.removeEventListener('pagehide', close)
      window.removeEventListener('pageshow', restore)
    }
    if (!navigator.locks?.request) {
      run.blocked('Não foi possível reservar a sessão neste navegador. Use Chrome, Edge ou Firefox atualizados.')
      return cleanup
    }
    reservation = reservation.then(async () => {
      if (!active) return
      await navigator.locks.request('stroop-participant-session', { ifAvailable: true }, async lock => {
        if (!active) return
        if (!lock) {
          run.blocked('Uma sessão já está aberta em outra aba. Feche a outra aba para continuar.')
          return
        }
        void run.activate()
        await held
      })
    }).catch(() => {
      if (active) { run.dispose(); run.blocked('Não foi possível reservar a sessão. Verifique o navegador e tente novamente.') }
    })
    return cleanup
  }, [run, revision])

  const busy = view.phase === 'invite' && view.busy
  useEffect(() => {
    if (view.phase === 'invite' && !busy) {
      const params = new URLSearchParams(window.location.search)
      const urlCode = params.get('convite')
      if (urlCode && /^[A-Za-z0-9_-]{32,128}$/.test(urlCode)) {
        void run.redeem(urlCode)
      } else {
        codeInput.current?.focus({ preventScroll: true })
      }
    } else if (closed || view.phase !== 'preparing' && view.phase !== 'result') {
      panel.current?.focus({ preventScroll: true })
    }
  }, [view.phase, busy, closed, run])

  function redeem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const value = code.trim()
    if (!/^[A-Za-z0-9_-]{32,128}$/.test(value)) { setCodeError('Confira o código informado pela equipe.'); return }
    setCode(''); setCodeError(null)
    void run.redeem(value)
  }
  async function finish(leave: boolean) {
    if (await run.finish()) {
      setCode(''); setCodeError(null)
      if (leave) setClosed(true)
    }
  }
  const capturePanel = captureTiming
    ? <W16TimingCapturePanel traces={timingTraces} onClear={() => setTimingTraces([])} /> : null

  if (closed) return <><section className="content-card closing-card" ref={panel} tabIndex={-1} aria-labelledby="closed-title">
    <JourneyIndicator current={4} />
    <p className="eyebrow">Acesso encerrado</p>
    <h1 id="closed-title">Participação encerrada.</h1>
    <p className="lead">O acesso desta sessão foi finalizado. Você pode fechar esta página.</p>
    <button className="button primary" onClick={onBack}>Voltar às orientações</button>{' '}
    <button className="button secondary" onClick={() => setClosed(false)}>Usar outro convite</button>
  </section>{capturePanel}</>

  if (view.phase === 'preparing') return <><PracticePreparation key={view.session.session_id}
    onBack={onBack} mainOrder={view.session.main_conditions} onMainStart={() => run.start()}
    onMainTrialComplete={(trial, framePeriod) => run.recordTrial(trial, framePeriod)}
    onMainComplete={result => run.complete(result)} onMainInterrupted={reason => run.interrupt(reason)}
    captureTiming={captureTiming} onMainTimingTrace={trace => setTimingTraces(rows => [...rows, trace])} />{capturePanel}</>
  if (view.phase === 'result') return <><ResultSummaryPanel summary={view.summary}
    delivery={view.delivery} message={view.message} canRetry={view.canRetry}
    busy={view.finishing} onRetry={() => void run.send()} onFinish={() => void finish(true)}
    onNewInvitation={() => void finish(false)} />{capturePanel}</>
  return <><section className="content-card" ref={panel} tabIndex={-1}>
    <JourneyIndicator current={2} />
    <p className="eyebrow">Participação em pesquisa</p>
    {view.phase === 'loading' ? <>
      <h1>Verificando seu acesso.</h1><p role="status">Aguarde um instante…</p>
    </> : view.phase === 'blocked' ? <>
      <h1>Vamos usar uma única aba.</h1><p role="alert" className="notice">{view.message}</p>
      <button className="button primary" onClick={() => setRevision(value => value + 1)}>Verificar novamente</button>
    </> : <>
      <h1>Informe o convite da equipe.</h1>
      <p className="lead">Use o código enviado pela equipe para iniciar esta sessão.</p>
      {view.message && <p role="alert" className="notice">{view.message}</p>}
      <form className="invitation-form" onSubmit={redeem} noValidate autoComplete="off" aria-busy={busy}>
        <label htmlFor="invitation-code">Código do convite</label>
        <input id="invitation-code" ref={codeInput} type="password" name="invitation-code"
          autoComplete="off" autoCapitalize="none" spellCheck={false} maxLength={128}
          value={code} onChange={event => { setCode(event.target.value); setCodeError(null) }}
          disabled={busy} aria-invalid={codeError !== null} aria-describedby="invitation-note" />
        <p id="invitation-note" className="quiet">Utilize o código fornecido pela equipe responsável pela pesquisa.</p>
        {codeError && <p role="alert" className="notice">{codeError}</p>}
        <button className="button primary" type="submit" disabled={busy}>{busy ? 'Verificando convite…' : 'Validar convite'}</button>{' '}
        <button className="button secondary" type="button" disabled={busy} onClick={() => void run.load()}>Verificar acesso</button>
      </form>
    </>}
    <div className="preparation-back"><button className="button secondary" disabled={busy} onClick={onBack}>Voltar às orientações</button></div>
  </section>{capturePanel}</>
}
