import { flushSync } from 'react-dom'
import { useCallback, useEffect, useRef, useState } from 'react'
import type { MouseEvent, ReactNode } from 'react'
import { ApiError, apiErrorMessage, getProfessionalProfile, logoutProfessional } from './api/client'
import type { ProfessionalProfile } from './api/client'
import { ParticipantFlow } from './components/ParticipantFlow'
import { ProfessionalDashboard } from './components/ProfessionalDashboard'
import { ProfessionalLogin, ProfessionalPassword } from './components/ProfessionalCredentials'
import { JourneyIndicator } from './components/JourneyIndicator'

type Navigate = (path: string) => void

function LocalLink({ href, navigate, children, className }: {
  href: string; navigate: Navigate; children: ReactNode; className?: string
}) {
  function follow(event: MouseEvent<HTMLAnchorElement>) {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
    event.preventDefault()
    navigate(href)
  }
  return <a href={href} onClick={follow} className={className}>{children}</a>
}

function Welcome({ navigate }: { navigate: Navigate }) {
  return <section className="welcome-grid">
    <div className="hero-card">
      <JourneyIndicator current={1} />
      <p className="eyebrow">Participação em pesquisa</p>
      <h1>Tarefa de Correspondência de Cores</h1>
      <p className="lead">Uma tarefa breve de correspondência entre palavras e cores. Primeiro, conheça a regra e faça uma prática.</p>
      <LocalLink href="/instrucoes" navigate={navigate} className="button primary">Iniciar tutorial <span aria-hidden="true">→</span></LocalLink>
      <p className="quiet">O bloco principal dura cerca de um minuto. Para participar, você precisará do convite fornecido pela equipe de pesquisa.</p>
    </div>
    <aside className="rule-card" aria-labelledby="rule-title">
      <p className="eyebrow">A regra em um olhar</p>
      <h2 id="rule-title">Compare palavra e cor.</h2>
      <div className="rule-examples" aria-label="Exemplos da regra">
        <article className="rule-example"><span className="rule-tag">Iguais</span><strong className="rule-word rule-word-match">VERDE</strong><p>Pressione <kbd>Espaço</kbd></p></article>
        <article className="rule-example"><span className="rule-tag">Diferentes</span><strong className="rule-word rule-word-mismatch">VERDE</strong><p>Aguarde sem pressionar</p></article>
      </div>
      <p className="equipment-note">Use um computador com teclado físico e reserve um momento sem interrupções.</p>
    </aside>
  </section>
}

function Instructions({ navigate }: { navigate: Navigate }) {
  return <section className="content-card instruction-card">
    <JourneyIndicator current={1} />
    <p className="eyebrow">Tutorial · conheça a regra</p>
    <h1>Observe a palavra e compare a cor das letras.</h1>
    <ol className="instruction-steps" aria-label="Como responder">
      <li><span className="instruction-number">01</span><div><h2>Observe</h2><p>Leia o nome da cor.</p></div></li>
      <li><span className="instruction-number">02</span><div><h2>Compare</h2><p>Confira a cor em que as letras aparecem.</p></div></li>
      <li><span className="instruction-number">03</span><div><h2>Responda ou aguarde</h2><p>Use Espaço quando forem iguais; quando forem diferentes, não pressione.</p></div></li>
    </ol>
    <div className="examples" aria-label="Exemplos da regra">
      <article className="example"><p className="example-label">Palavra e cor iguais</p><strong className="word go">VERDE</strong><p>Pressione <kbd>Espaço</kbd>.</p></article>
      <article className="example"><p className="example-label">Palavra e cor diferentes</p><strong className="word no-go">VERMELHO</strong><p>Aguarde, sem pressionar.</p></article>
    </div>
    <p>Durante a prática, você receberá feedback após cada tentativa.</p>
    <LocalLink href="/pratica" navigate={navigate} className="button primary">Ir para a prática <span aria-hidden="true">→</span></LocalLink>{' '}
    <LocalLink href="/" navigate={navigate} className="button secondary">Voltar ao início</LocalLink>
  </section>
}

type AccessState = { phase: 'loading' | 'login' } |
  { phase: 'ready'; profile: ProfessionalProfile } | { phase: 'error'; error: unknown }

function ProfessionalAccess() {
  const [state, setState] = useState<AccessState>({ phase: 'loading' })
  const [revision, setRevision] = useState(0)
  const [ending, setEnding] = useState(false)
  const [logoutError, setLogoutError] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    setState({ phase: 'loading' })
    getProfessionalProfile(controller.signal).then(
      profile => { if (!controller.signal.aborted) setState({ phase: 'ready', profile }) },
      error => {
        if (controller.signal.aborted) return
        setState(error instanceof ApiError && error.status === 401 ? { phase: 'login' } : { phase: 'error', error })
      },
    )
    return () => controller.abort()
  }, [revision])

  useEffect(() => {
    if (state.phase !== 'ready') return
    const remaining = Math.max(0, Date.parse(state.profile.expires_at) - Date.now())
    const timer = setTimeout(() => setRevision(value => value + 1), remaining)
    return () => clearTimeout(timer)
  }, [state])
  useEffect(() => {
    const clear = () => flushSync(() => setState({ phase: 'login' }))
    const restore = (event: PageTransitionEvent) => { if (event.persisted) window.location.reload() }
    window.addEventListener('pagehide', clear)
    window.addEventListener('stroop-professional-session-ended', clear)
    window.addEventListener('pageshow', restore)
    return () => { window.removeEventListener('pagehide', clear); window.removeEventListener('stroop-professional-session-ended', clear); window.removeEventListener('pageshow', restore) }
  }, [])

  async function endSession(profile: ProfessionalProfile) {
    setEnding(true)
    setLogoutError(false)
    try {
      await logoutProfessional(profile.csrf_token)
      setState({ phase: 'login' })
    } catch {
      setLogoutError(true)
    } finally {
      setEnding(false)
    }
  }
  const roleNames = { consulta: 'Consulta', importacao: 'Coleta e importação', administracao: 'Administração' }
  return <section className="content-card access-card" aria-busy={state.phase === 'loading' || ending}>
    <p className="eyebrow">Acesso profissional</p>
    <h1>Área da equipe</h1>
    {state.phase === 'loading' && <p role="status" className="status-line"><span className="spinner" aria-hidden="true" />Verificando seu acesso…</p>}
    {state.phase === 'login' && <ProfessionalLogin onAuthenticated={profile => setState({ phase: 'ready', profile })} />}
    {state.phase === 'error' && <>
      <p role="alert" className="notice">{apiErrorMessage(state.error)}</p>
      <button className="button secondary" onClick={() => setRevision(value => value + 1)}>Tentar novamente</button>
    </>}
    {state.phase === 'ready' && <>
      <p className="lead">Sua sessão está ativa.</p>
      <p className="role-badge">{roleNames[state.profile.role]}</p>
      {logoutError && <p role="alert" className="notice">Não foi possível confirmar o encerramento. Tente novamente.</p>}
      <button className="button secondary" disabled={ending} onClick={() => void endSession(state.profile)}>{ending ? 'Encerrando…' : 'Encerrar sessão'}</button>
      {!ending && <>
        <ProfessionalPassword profile={state.profile} onEnded={() => setState({ phase: 'login' })} />
        <ProfessionalDashboard profile={state.profile} />
      </>}
    </>}
  </section>
}

export function App() {
  const [path, setPath] = useState(window.location.pathname)
  const main = useRef<HTMLElement>(null)
  const navigate = useCallback<Navigate>(next => {
    if (window.location.pathname === next) return
    window.history.pushState(null, '', next)
    setPath(next)
  }, [])
  useEffect(() => {
    const followHistory = () => setPath(window.location.pathname)
    window.addEventListener('popstate', followHistory)
    return () => window.removeEventListener('popstate', followHistory)
  }, [])
  useEffect(() => {
    if (path !== '/' && path !== '/instrucoes') return
    let pressed: string | null = null
    const down = (event: KeyboardEvent) => {
      if (event.repeat || !['Space', 'Enter'].includes(event.code)) return
      if (event.target instanceof HTMLElement && event.target.closest('a, button, input, textarea, select, [contenteditable="true"]')) return
      pressed = event.code
      event.preventDefault()
    }
    const up = (event: KeyboardEvent) => {
      if (pressed !== event.code) return
      pressed = null
      event.preventDefault()
      navigate(path === '/' ? '/instrucoes' : '/pratica')
    }
    const cancelNavigation = () => { pressed = null }
    window.addEventListener('blur', cancelNavigation)
    document.addEventListener('keydown', down)
    document.addEventListener('keyup', up)
    return () => {
      window.removeEventListener('blur', cancelNavigation)
      document.removeEventListener('keydown', down)
      document.removeEventListener('keyup', up)
    }
  }, [path, navigate])
  useEffect(() => {
    document.title = `${path === '/equipe' ? 'Área da equipe' : path === '/instrucoes' ? 'Orientações' : path === '/pratica' ? 'Prática' : 'Participação'} · Tarefa de Correspondência de Cores`
    main.current?.focus({ preventScroll: true })
    window.scrollTo(0, 0)
  }, [path])

  return <>
    <a className="skip-link" href="#conteudo">Ir para o conteúdo</a>
    <div className="page-shell">
      <header className="site-header">
        <LocalLink href="/" navigate={navigate} className="brand"><span className="brand-mark" aria-hidden="true"><i /><i /><i /></span><span>Cores<span className="brand-subtitle">Tarefa experimental</span></span></LocalLink>
        <nav aria-label="Navegação principal">
          <LocalLink href="/" navigate={navigate}>Participação</LocalLink>
          <LocalLink href="/equipe" navigate={navigate} className="team-link">Área da equipe <span aria-hidden="true">↗</span></LocalLink>
        </nav>
      </header>
      <main id="conteudo" ref={main} tabIndex={-1}>
        {path === '/' ? <Welcome navigate={navigate} /> : path === '/instrucoes' ? <Instructions navigate={navigate} /> : path === '/pratica' ? <ParticipantFlow onBack={() => navigate('/instrucoes')} /> : path === '/equipe' ? <ProfessionalAccess /> : <section className="content-card"><p className="eyebrow">Página não encontrada</p><h1>Vamos voltar ao início?</h1><LocalLink href="/" navigate={navigate} className="button primary">Ir para o início</LocalLink></section>}
      </main>
      <footer className="site-footer"><span>Pesquisa · Atenção às cores</span><span>Siga as orientações da equipe responsável.</span></footer>
    </div>
  </>
}
