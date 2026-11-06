import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import type { ProfessionalProfile } from '../api/client'
import { listProjects } from '../api/assessments'
import type { Project } from '../api/assessments'
import { revokeAdminSessions, createProject, listAdminUsers, listProjectMembers, setProjectMember, updateAdminUser } from '../api/administration'
import type { AdminUser, ProjectMember } from '../api/administration'

export function AdministrationPanel({ profile }: { profile: ProfessionalProfile }) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [userCursor, setUserCursor] = useState<string | null>(null)
  const [usersBusy, setUsersBusy] = useState(false)
  const [projects, setProjects] = useState<Project[]>([])
  const [projectCursor, setProjectCursor] = useState<string | null>(null)
  const [project, setProject] = useState('')
  const [members, setMembers] = useState<ProjectMember[]>([])
  const [memberCursor, setMemberCursor] = useState<string | null>(null)
  const [membersBusy, setMembersBusy] = useState(false)
  const [selectedUser, setSelectedUser] = useState('')
  const [editUser, setEditUser] = useState('')
  const [role, setRole] = useState<AdminUser['role']>('consulta')
  const [active, setActive] = useState(true)
  const [projectCode, setProjectCode] = useState('')
  const [projectName, setProjectName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    const io = new AbortController()
    void (async () => {
      try {
        const page = await listProjects({ limit: 100, signal: io.signal })
        if (!io.signal.aborted) { setProjects(page.items); setProjectCursor(page.next_cursor); setProject(page.items[0]?.id ?? '') }
      } catch (cause) { if (!io.signal.aborted) setError(apiErrorMessage(cause)) }
    })()
    return () => io.abort()
  }, [])

  useEffect(() => {
    const io = new AbortController()
    setMembers([]); setMemberCursor(null)
    if (!project) return () => io.abort()
    void listProjectMembers(project, { limit: 100, signal: io.signal }).then(page => {
      if (!io.signal.aborted) { setMembers(page.items); setMemberCursor(page.next_cursor) }
    }, cause => { if (!io.signal.aborted) setError(apiErrorMessage(cause)) })
    return () => io.abort()
  }, [project])

  async function loadUsers(cursor?: string | null) {
    if (usersBusy) return
    const io = new AbortController()
    setUsersBusy(true); setError(null)
    try {
      const page = await listAdminUsers({ limit: 100, ...(cursor ? { cursor } : {}), signal: io.signal })
      setUsers(current => cursor ? [...current, ...page.items.filter(item => !current.some(existing => existing.user_id === item.user_id))] : page.items)
      setUserCursor(page.next_cursor)
    } catch (cause) { setError(apiErrorMessage(cause)) }
    finally { setUsersBusy(false) }
  }
  useEffect(() => { void loadUsers() }, [])

  async function loadMoreProjects() {
    if (!projectCursor || busy) return
    setBusy(true); setError(null)
    try {
      const page = await listProjects({ limit: 100, cursor: projectCursor })
      setProjects(current => [...current, ...page.items]); setProjectCursor(page.next_cursor)
    } catch (cause) { setError(apiErrorMessage(cause)) }
    finally { setBusy(false) }
  }
  async function loadMoreMembers() {
    if (!memberCursor || membersBusy) return
    const io = new AbortController(); setMembersBusy(true); setError(null)
    try {
      const page = await listProjectMembers(project, { limit: 100, cursor: memberCursor, signal: io.signal })
      setMembers(current => [...current, ...page.items.filter(item => !current.some(existing => existing.user_id === item.user_id))])
      setMemberCursor(page.next_cursor)
    } catch (cause) { setError(apiErrorMessage(cause)) }
    finally { setMembersBusy(false) }
  }

  async function revokeSessions(userId: string) {
    if (busy || !window.confirm('Encerrar todas as sessões da conta selecionada?')) return
    setBusy(true); setError(null); setMessage(null)
    try {
      await revokeAdminSessions(userId, profile.csrf_token)
      if (userId === profile.user_id) window.dispatchEvent(new Event('stroop-professional-session-ended'))
      else setMessage('Sessões encerradas.')
    } catch (cause) { setError(apiErrorMessage(cause)) }
    finally { setBusy(false) }
  }
  async function saveUser(event: FormEvent) {
    event.preventDefault()
    const selected = users.find(item => item.user_id === editUser)
    if (!selected || busy) return
    setBusy(true); setError(null); setMessage(null)
    const action = active ? 'reativar' : 'bloquear'
    if (!window.confirm(`${action} ${selected.user_id}; aplicar perfil ${role}?`)) { setBusy(false); return }
    try {
      await updateAdminUser(selected.user_id, { role, active }, profile.csrf_token)
      setUsers(current => current.map(item => item.user_id === selected.user_id ? { ...item, role, active } : item))
      setMessage('Alterações aplicadas. Sessões são revalidadas pelo servidor.')
    } catch (cause) { setError(cause instanceof ApiError && cause.status === 409 ? 'A operação preservou a última conta administrativa ativa.' : apiErrorMessage(cause)) }
    finally { setBusy(false) }
  }
  async function addProject(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(null); setMessage(null)
    try {
      const created = await createProject({ code: projectCode.trim(), name: projectName.trim() }, profile.csrf_token)
      setProjects(current => [created, ...current]); setProject(created.id); setProjectCode(''); setProjectName('')
      setMessage('Projeto criado. Vincule explicitamente as contas que devem consultar os resultados.')
    } catch (cause) { setError(apiErrorMessage(cause)) }
    finally { setBusy(false) }
  }
  async function changeMember(userId: string, next: boolean) {
    const selected = users.find(item => item.user_id === userId)
    if (!project || busy) return
    setError(null); setMessage(null)
    if (!window.confirm(`${next ? 'Vincular' : 'Revogar vínculo de'} ${selected?.user_id || userId} ao projeto selecionado?`)) return
    setBusy(true)
    try {
      const result = await setProjectMember(project, userId, next, profile.csrf_token)
      setMembers(current => current.some(item => item.user_id === userId)
        ? current.map(item => item.user_id === userId ? result : item) : [...current, result])
      setMessage(next ? 'Vínculo ativado. O acesso a resultados exige este vínculo.' : 'Vínculo revogado.')
    } catch (cause) { setError(apiErrorMessage(cause)) }
    finally { setBusy(false) }
  }
  const selected = users.find(item => item.user_id === editUser)
  return <section className="administration-panel" aria-labelledby="admin-title">
    <h2 id="admin-title">Administração</h2>
    <p className="quiet">Somente a administração pode gerir contas, projetos e vínculos. Bloqueios e revogações são revalidados pelo servidor.</p>
    {error && <p role="alert">{error}</p>}{message && <p role="status">{message}</p>}
    <section aria-labelledby="accounts-title">
      <h3 id="accounts-title">Contas e permissões</h3>
      <p>A conta é provisionada pelo responsável. O identificador técnico representa a conta compartilhada e não identifica a pessoa que a utiliza.</p>
      <label htmlFor="admin-user-select">Conta para alterar</label>
      <select id="admin-user-select" value={editUser} onChange={event => { setEditUser(event.target.value); const item = users.find(user => user.user_id === event.target.value); if (item) { setRole(item.role); setActive(item.active) } }}>
        <option value="">Selecione uma conta</option>{users.map(item => <option key={item.user_id} value={item.user_id}>{item.user_id} — {item.role}{item.active ? '' : ' (bloqueada)'}</option>)}
      </select>
      <div className="table-scroll"><table><caption>Contas cadastradas</caption><thead><tr><th>Identificador da conta</th><th>Perfil</th><th>Estado</th><th>Ação</th></tr></thead><tbody>
        {users.map(item => <tr key={item.user_id}><td>{item.user_id}</td><td>{item.role}</td><td>{item.active ? 'Ativa' : 'Bloqueada'}</td>
          <td><button className="button secondary" onClick={() => { setEditUser(item.user_id); setRole(item.role); setActive(item.active) }}>Editar</button>{' '}
            <button className="button secondary" disabled={busy} onClick={() => void revokeSessions(item.user_id)}>Encerrar sessões</button></td></tr>)}
      </tbody></table></div>
      {selected && <form onSubmit={event => void saveUser(event)}>
        <p className="quiet">Conta: {selected.user_id}</p>
        <label>Perfil<select value={role} onChange={event => setRole(event.target.value as AdminUser['role'])}><option value="consulta">Consulta</option><option value="importacao">Coleta e importação</option><option value="administracao">Administração</option></select></label>
        <label><input type="checkbox" checked={active} onChange={event => setActive(event.target.checked)} /> Conta ativa</label>
        <button className="button secondary" disabled={busy}>Confirmar alterações</button>
      </form>}
      {userCursor && <button className="button secondary" disabled={usersBusy} onClick={() => void loadUsers(userCursor)}>{usersBusy ? 'Carregando contas…' : 'Mais contas'}</button>}
    </section>
    <section aria-labelledby="projects-title">
      <h3 id="projects-title">Projetos e vínculos</h3>
      <form onSubmit={event => void addProject(event)}>
        <label>Código do projeto<input value={projectCode} onChange={event => setProjectCode(event.target.value)} required maxLength={64} pattern="[A-Za-z0-9_.-]+" /></label>
        <label>Nome do projeto<input value={projectName} onChange={event => setProjectName(event.target.value)} required maxLength={120} /></label>
        <button className="button primary" disabled={busy}>Criar projeto</button>
      </form>
      <label htmlFor="admin-project">Projeto para vínculos</label>
      <select id="admin-project" value={project} onChange={event => setProject(event.target.value)}>
        {projects.map(item => <option key={item.id} value={item.id}>{item.code} — {item.name}{item.active ? '' : ' (inativo)'}</option>)}
      </select>
      {projectCursor && <button className="button secondary" disabled={busy} onClick={() => void loadMoreProjects()}>Mais projetos</button>}
      <label htmlFor="member-user">Conta para vincular</label>
      <select id="member-user" value={selectedUser} onChange={event => setSelectedUser(event.target.value)}>
        <option value="">Selecione uma conta</option>{users.map(item => <option key={item.user_id} value={item.user_id}>{item.user_id} — {item.role}</option>)}
      </select>
      <button className="button secondary" disabled={busy || !selectedUser || !project} onClick={() => void changeMember(selectedUser, true)}>Ativar vínculo</button>
      <table><caption>Vínculos do projeto selecionado</caption><thead><tr><th>Conta</th><th>Estado</th><th>Ação</th></tr></thead><tbody>
        {members.map(item => { const user = users.find(candidate => candidate.user_id === item.user_id); return <tr key={item.user_id}>
          <td>{user?.user_id || item.user_id}</td><td>{item.active ? 'Ativo' : 'Revogado'}</td>
          <td><button className="button secondary" disabled={busy || !user || item.active} onClick={() => void changeMember(item.user_id, true)}>Ativar</button>{' '}
            <button className="button secondary" disabled={busy || !user || !item.active} onClick={() => void changeMember(item.user_id, false)}>Revogar</button></td>
        </tr>})}
      </tbody></table>
      {memberCursor && <button className="button secondary" disabled={membersBusy} onClick={() => void loadMoreMembers()}>{membersBusy ? 'Carregando vínculos…' : 'Mais vínculos'}</button>}
    </section>
  </section>
}
