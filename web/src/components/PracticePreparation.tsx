import { useCallback, useEffect, useRef, useState } from 'react'
import { ExperimentHost } from '../experiment/ExperimentHost'
import type { MountExperiment } from '../experiment/ExperimentHost'
import { checkEnvironment } from '../experiment/environment'
import { mountPractice } from '../experiment/practice'
import type { PracticeSummary } from '../experiment/protocol'

type Phase = 'preparing' | 'practice' | 'summary' | 'interrupted'

export function PracticePreparation({ onBack }: { onBack: () => void }) {
  const environment = checkEnvironment(navigator.userAgent)
  const [confirmedKeyboard, setConfirmedKeyboard] = useState(false)
  const [verifiedKeyboard, setVerifiedKeyboard] = useState(false)
  const [focused, setFocused] = useState(document.hasFocus() && document.visibilityState === 'visible')
  const [phase, setPhase] = useState<Phase>('preparing')
  const [summary, setSummary] = useState<PracticeSummary | null>(null)
  const held = useRef(new Set<string>())
  const pendingNavigation = useRef<string | null>(null)
  const panel = useRef<HTMLElement>(null)
  const canStart = environment.supported && confirmedKeyboard && verifiedKeyboard && focused

  const begin = useCallback(() => {
    if (!canStart || !document.hasFocus() || document.visibilityState !== 'visible') return
    setSummary(null)
    setPhase('practice')
  }, [canStart])

  const mount = useCallback<MountExperiment>(container => mountPractice(container, {
    initiallyHeldKeys: [...held.current],
    onComplete: result => { setSummary(result); setPhase('summary') },
    onInterrupted: () => { setSummary(null); setPhase('interrupted') },
  }), [])

  useEffect(() => {
    const update = () => setFocused(document.hasFocus() && document.visibilityState === 'visible')
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
    if (phase !== 'practice') panel.current?.focus({ preventScroll: true })
    document.body.classList.toggle('task-active', phase === 'practice')
    return () => { document.body.classList.remove('task-active') }
  }, [phase])
  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      const alreadyHeld = held.current.has(event.code)
      held.current.add(event.code)
      if (event.repeat || alreadyHeld || phase === 'practice') return
      const target = event.target instanceof HTMLElement ? event.target : null
      const editable = !!target?.closest('input, textarea, select, [contenteditable="true"]')
      if (editable) return
      if (phase === 'summary' && event.code === 'KeyR' && canStart) {
        pendingNavigation.current = event.code
        event.preventDefault()
      } else if (!target?.closest('button, a') && ['Space', 'Enter'].includes(event.code)) {
        if (canStart && phase !== 'summary') pendingNavigation.current = event.code
        event.preventDefault()
      }
    }
    const up = (event: KeyboardEvent) => {
      const wasHeld = held.current.delete(event.code)
      if (event.code === 'Space' && wasHeld && phase !== 'practice') setVerifiedKeyboard(true)
      if (pendingNavigation.current === event.code && wasHeld) {
        pendingNavigation.current = null
        begin()
      }
    }
    document.addEventListener('keydown', down)
    document.addEventListener('keyup', up)
    return () => {
      document.removeEventListener('keydown', down)
      document.removeEventListener('keyup', up)
      pendingNavigation.current = null
    }
  }, [phase, canStart, begin])

  if (phase === 'practice') return <ExperimentHost mount={mount} />
  return <section className="content-card practice-preparation" ref={panel} tabIndex={-1}>
    <p className="eyebrow">Preparação e prática</p>
    {phase === 'summary' && summary ? <>
      <h1>Prática concluída.</h1>
      <p className="lead">Você concluiu as {summary.total} tentativas de treino. Se quiser, pode repetir a prática antes de continuar.</p>
      <p>O treino não faz parte do resultado oficial.</p>
      <button className="button primary" onClick={begin} disabled={!canStart}>Repetir prática</button>
      <p className="quiet">Pressione R para repetir ou volte às orientações.</p>
    </> : <>
      <h1>Vamos praticar primeiro.</h1>
      <p className="lead">Serão quatro tentativas, com feedback após cada uma. Pressione <kbd>Espaço</kbd> apenas quando a palavra e a cor das letras forem iguais.</p>
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
