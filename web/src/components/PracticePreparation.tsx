import { useCallback, useEffect, useRef, useState } from 'react'
import { participantErrorMessage } from '../api/participant'
import { ExperimentHost } from '../experiment/ExperimentHost'
import type { MountExperiment } from '../experiment/ExperimentHost'
import { checkEnvironment } from '../experiment/environment'
import { mountPractice } from '../experiment/practice'
import { mountMain } from '../experiment/main'
import { JourneyIndicator } from './JourneyIndicator'
import type { MainResult, MainTimingTrace, MainTrial } from '../experiment/main-engine'
import type { Condition, InterruptionReason, PracticeSummary } from '../experiment/protocol'

type Phase = 'preparing' | 'practice' | 'summary' | 'interrupted' | 'starting' | 'start-error' | 'main'
type Props = {
  onBack: () => void
  mainOrder: readonly Condition[]
  onMainStart: () => Promise<void>
  onMainTrialComplete?: (trial: Readonly<MainTrial>, framePeriod: number) => void
  onMainComplete: (result: MainResult) => void
  onMainInterrupted: (reason: InterruptionReason) => void
  captureTiming?: boolean
  onMainTimingTrace?: (trace: MainTimingTrace) => void
}

export function PracticePreparation(props: Props) {
  const { onBack } = props
  const integration = useRef(props)
  integration.current = props
  const environment = checkEnvironment(navigator.userAgent)
  const [confirmedKeyboard, setConfirmedKeyboard] = useState(false)
  const [verifiedKeyboard, setVerifiedKeyboard] = useState(false)
  const [focused, setFocused] = useState(document.hasFocus() && document.visibilityState === 'visible')
  const [phase, setPhase] = useState<Phase>('preparing')
  const [summary, setSummary] = useState<PracticeSummary | null>(null)
  const [startError, setStartError] = useState<unknown>(null)
  const held = useRef(new Set<string>())
  const pendingNavigation = useRef<string | null>(null)
  const panel = useRef<HTMLElement>(null)
  const mounted = useRef(true)
  const starting = useRef(false)
  const canStart = environment.supported && confirmedKeyboard && verifiedKeyboard && focused

  useEffect(() => { mounted.current = true; return () => { mounted.current = false } }, [])
  const begin = useCallback(() => {
    if (!canStart || !document.hasFocus() || document.visibilityState !== 'visible' || starting.current) return
    setSummary(null)
    setPhase('practice')
  }, [canStart])
  const beginMain = useCallback(async () => {
    if (!canStart || !['summary', 'start-error'].includes(phase) || starting.current
      || !document.hasFocus() || document.visibilityState !== 'visible') return
    starting.current = true
    setStartError(null)
    setPhase('starting')
    try {
      await integration.current.onMainStart()
      if (!mounted.current) return
      if (!document.hasFocus() || document.visibilityState !== 'visible') {
        integration.current.onMainInterrupted(document.visibilityState === 'visible' ? 'focus_lost' : 'visibility_hidden')
        return
      }
      setPhase('main')
    } catch (error) {
      if (mounted.current) { setStartError(error); setPhase('start-error') }
    } finally { starting.current = false }
  }, [canStart, phase])
  const mountMainBlock = useCallback<MountExperiment>(container => mountMain(container, {
    order: integration.current.mainOrder, initiallyHeldKeys: [...held.current],
    onTrialComplete: (trial, framePeriod) => integration.current.onMainTrialComplete?.(trial, framePeriod),
    onComplete: result => integration.current.onMainComplete(result),
    onInterrupted: reason => integration.current.onMainInterrupted(reason),
    onTimingTrace: integration.current.captureTiming
      ? trace => integration.current.onMainTimingTrace?.(trace) : undefined,
  }), [])
  const mount = useCallback<MountExperiment>(container => mountPractice(container, {
    initiallyHeldKeys: [...held.current],
    onComplete: result => { setSummary(result); setPhase('summary') },
    onInterrupted: () => { setSummary(null); setPhase('interrupted') },
  }), [])

  useEffect(() => {
    const update = () => {
      pendingNavigation.current = null
      setFocused(document.hasFocus() && document.visibilityState === 'visible')
    }
    window.addEventListener('focus', update)
    window.addEventListener('blur', update)
    document.addEventListener('visibilitychange', update)
    return () => {
      window.removeEventListener('focus', update)
      window.removeEventListener('blur', update)
      document.removeEventListener('visibilitychange', update)
    }
  }, [])
  useEffect(() => {
    if (phase !== 'practice' && phase !== 'main') panel.current?.focus({ preventScroll: true })
    document.body.classList.toggle('task-active', phase === 'practice' || phase === 'main')
    return () => { document.body.classList.remove('task-active') }
  }, [phase])
  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      const alreadyHeld = held.current.has(event.code)
      held.current.add(event.code)
      if (event.repeat || alreadyHeld || phase === 'practice' || phase === 'main' || phase === 'starting') return
      const target = event.target instanceof HTMLElement ? event.target : null
      if (target?.closest('input, textarea, select, [contenteditable="true"]')) return
      if (phase === 'summary' && event.code === 'KeyR' && canStart) {
        pendingNavigation.current = event.code
        event.preventDefault()
      } else if (!target?.closest('button, a') && ['Space', 'Enter'].includes(event.code)) {
        if (canStart) pendingNavigation.current = event.code
        event.preventDefault()
      }
    }
    const up = (event: KeyboardEvent) => {
      const wasHeld = held.current.delete(event.code)
      if (event.code === 'Space' && wasHeld && phase !== 'practice' && phase !== 'main') setVerifiedKeyboard(true)
      if (pendingNavigation.current === event.code && wasHeld) {
        pendingNavigation.current = null
        if (['summary', 'start-error'].includes(phase) && event.code !== 'KeyR') void beginMain()
        else begin()
      }
    }
    document.addEventListener('keydown', down)
    document.addEventListener('keyup', up)
    return () => {
      document.removeEventListener('keydown', down)
      document.removeEventListener('keyup', up)
      pendingNavigation.current = null
    }
  }, [phase, canStart, begin, beginMain])

  if (phase === 'practice') return <ExperimentHost mount={mount} />
  if (phase === 'main') return <ExperimentHost mount={mountMainBlock} />
  if (phase === 'starting' || phase === 'start-error') return <section className="content-card" ref={panel} tabIndex={-1}>
    <JourneyIndicator current={4} />
    <p className="eyebrow">Etapa 4 · tarefa principal</p><h1>Preparando a execução.</h1>
    {phase === 'starting' ? <p role="status">Confirmando seu acesso antes de começar…</p> : <>
      <p role="alert" className="notice">{participantErrorMessage(startError)}</p>
      <p>A tarefa principal ainda não começou. Você pode tentar confirmar o início novamente.</p>
      <button className="button primary" onClick={() => void beginMain()} disabled={!canStart}>Tentar iniciar novamente</button>{' '}
      <button className="button secondary" onClick={onBack}>Voltar às orientações</button>
    </>}
  </section>
  return <section className="content-card practice-preparation" ref={panel} tabIndex={-1}>
    <JourneyIndicator current={3} />
    <p className="eyebrow">Etapa 3 · prática</p>
    {phase === 'summary' && summary ? <>
      <h1>Prática concluída.</h1>
      <p className="lead">Você concluiu as {summary.total} tentativas de treino. Quando estiver pronto, comece a tarefa principal.</p>
      <p>Se quiser, você pode repetir a prática. O treino não faz parte do resultado.</p>
      <button className="button primary" onClick={() => void beginMain()} disabled={!canStart}>Começar tarefa</button>{' '}
      <button className="button secondary" onClick={begin} disabled={!canStart}>Repetir prática</button>
      <p className="quiet">Pressione Espaço ou Enter para começar a tarefa, ou R para repetir a prática.</p>
    </> : <>
      <h1>Primeiro, vamos praticar.</h1>
      <p className="lead">Faça quatro tentativas. Durante a prática, você receberá feedback após cada uma.</p>
      <ol className="preparation-sequence" aria-label="Preparação para a prática">
        <li><span className="instruction-number">01</span><div><h2>Confirme o teclado</h2><p>Use um computador com teclado físico e mantenha esta aba em foco.</p></div></li>
        <li><span className="instruction-number">02</span><div><h2>Pratique a regra</h2><p>Pressione <kbd>Espaço</kbd> quando a palavra e a cor das letras forem iguais; nas diferentes, aguarde.</p></div></li>
      </ol>
      {phase === 'interrupted' && <p className="notice" role="alert">O treino foi interrompido. Recomece uma rodada completa para continuar.</p>}
      {!environment.supported ? <p className="notice" role="alert">Use um computador Windows ou Linux com teclado físico e Chrome, Edge ou Firefox. Este ambiente ainda não foi validado para a tarefa.</p> : <div className="preparation-checks">
        <label className="keyboard-confirm"><input type="checkbox" checked={confirmedKeyboard} onChange={event => setConfirmedKeyboard(event.target.checked)} /> Estou usando um computador ou notebook com teclado físico.</label>
        <p role="status">{verifiedKeyboard ? 'Teclado verificado.' : 'Pressione e solte Espaço para verificar o teclado.'}</p>
        <button className="button primary" disabled={!canStart} onClick={begin}>{phase === 'interrupted' ? 'Recomeçar prática' : 'Começar prática'}</button>
        <p className="quiet">Com o teclado verificado, você também pode pressionar e soltar Espaço ou Enter para começar.</p>
      </div>}
    </>}
    {!focused && environment.supported && <p className="notice" role="status">Mantenha esta aba visível e em foco para começar.</p>}
    <div className="preparation-back"><button className="button secondary" onClick={onBack}>Voltar às orientações</button></div>
  </section>
}
