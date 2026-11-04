import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { apiErrorMessage } from '../api/client'
import { getAssessmentOptions } from '../api/assessments'
import type { AssessmentFacets, AssessmentOptions, Project } from '../api/assessments'

export type ResearchQuery = { projects: string[]; filters: AssessmentOptions }
const empty: AssessmentFacets = { participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: [], test_code: [] }
const labels = { participant_id: 'Participantes (códigos)', visit: 'Visitas', evaluator_id: 'Avaliadores (identificação técnica)', test_version: 'Versões', platform: 'Plataformas' } as const
export function ResearchFilters({ projects, initialProject, loading, onApply }: {
  projects: Project[]; initialProject: string; loading: boolean; onApply(query: ResearchQuery): void
}) {
  const [selected, setSelected] = useState([initialProject])
  const [start, setStart] = useState(''), [end, setEnd] = useState('')
  const [instrument, setInstrument] = useState('')
  const [values, setValues] = useState<Record<keyof typeof labels, string[]>>({ participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: [] })
  const [facets, setFacets] = useState(empty)
  const [error, setError] = useState<string | null>(null)
  const [validation, setValidation] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const io = new AbortController()
    setFacets(empty); setError(null)
    if (!selected.length || selected.length > 20 || start && end && start > end) { setPending(false); return () => io.abort() }
    setPending(true)
    void (async () => {
      try {
        const merged: AssessmentFacets = { ...empty }
        for (const id of selected) {
          const page = await getAssessmentOptions(id, { start_date: start || undefined, end_date: end || undefined, test_code: instrument || undefined, signal: io.signal })
          for (const key of Object.keys(empty) as (keyof AssessmentFacets)[]) Object.assign(merged, { [key]: [...new Set([...merged[key], ...page[key]])].sort() })
        }
        if (!io.signal.aborted) setFacets(merged)
      } catch (cause) { if (!io.signal.aborted) setError(apiErrorMessage(cause)) }
      finally { if (!io.signal.aborted) setPending(false) }
    })()
    return () => io.abort()
  }, [selected, start, end, instrument, revision])
  function apply(event?: FormEvent) {
    event?.preventDefault()
    setValidation(null)
    if (!selected.length || selected.length > 20) { setValidation('Selecione de 1 a 20 projetos para consultar.'); return }
    if (start && end && start > end) { setValidation('A data inicial deve ser anterior ou igual à final.'); return }
    if (Object.values(values).some(items => items.length > 100)) { setValidation('Selecione no máximo 100 opções por campo.'); return }
    onApply({ projects: [...selected], filters: { ...values, platform: values.platform.filter((value): value is 'web' | 'psychopy' => value === 'web' || value === 'psychopy'), start_date: start || undefined, end_date: end || undefined, test_code: instrument || undefined } })
  }
  function clear() {
    setValidation(null); setSelected([initialProject]); setStart(''); setEnd(''); setInstrument(''); setValues({ participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: [] })
    onApply({ projects: [initialProject], filters: {} })
  }
  return <form onSubmit={apply} className="research-filters" aria-label="Filtros da consulta">
    <h3>Filtrar resultados</h3>
    <p className="quiet">Seleções do mesmo campo são alternativas; os campos são combinados. Sem seleção, todas as opções desse campo. Use Ctrl/Cmd ou Shift e as setas para selecionar várias opções.</p>
    <div className="dashboard-filters">
      <label className="project-filter">Projetos da consulta<select multiple value={selected} onChange={event => setSelected([...event.target.selectedOptions].map(option => option.value))}>
        {projects.map(project => <option key={project.id} value={project.id} title={`${project.code} — ${project.name}`}>{project.code}{project.active ? '' : ' (inativo)'}</option>)}
      </select></label>
      <label>Data inicial<input type="date" value={start} onChange={event => setStart(event.target.value)} /></label>
      <label>Data final<input type="date" value={end} onChange={event => setEnd(event.target.value)} /></label>
      <label>Instrumento da consulta<select value={instrument} onChange={event => setInstrument(event.target.value)}><option value="">Todos (exibir um por vez)</option>{[...new Set([...facets.test_code, ...(instrument ? [instrument] : [])])].map(code => <option key={code}>{code}</option>)}</select></label>
      {(Object.keys(labels) as (keyof typeof labels)[]).map(key => <label key={key}>{labels[key]}<select multiple value={values[key]} onChange={event => setValues({ ...values, [key]: [...event.target.selectedOptions].map(option => option.value) })}>
        {[...new Set([...facets[key], ...values[key]])].sort().map(value => <option key={value} value={value} title={value}>{value === 'LEGADO_NAO_MAPEADO' && key === 'evaluator_id' ? 'Legado sem identificação técnica' : value}</option>)}
      </select></label>)}
    </div>
    <p className="quiet">Período inclusivo pela data da avaliação: WEB usa o dia UTC do início; legado conserva a data civil registrada, sem atribuir fuso. Máximo de 20 projetos e 5.000 avaliações completas por consulta; restrinja os filtros para volumes maiores.</p>
    {validation && <p role="alert">{validation}</p>}
    {pending && <p role="status">Carregando opções autorizadas…</p>}
    {error && <><p role="alert">Opções de filtro: {error}</p><button type="button" className="button secondary" onClick={() => setRevision(n => n + 1)}>Atualizar opções</button></>}
    <button className="button primary" type="submit" disabled={loading || pending || !!error}>Aplicar filtros</button>
    <button className="button secondary" type="button" onClick={clear}>Limpar filtros</button>
  </form>
}
