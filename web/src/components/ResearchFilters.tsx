import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { apiErrorMessage } from '../api/client'
import { getAssessmentOptions } from '../api/assessments'
import type { AssessmentFacets, AssessmentOptions, Project } from '../api/assessments'

export type AdvancedFilterValues = {
  searchText: string
  status: 'valid' | 'all' | 'invalid'
  accuracyRange: 'all' | 'under50' | '50to80' | '80plus'
  rtRange: 'all' | 'under500ms' | '500to1000ms' | '1000to1500ms' | '1500msPlus'
  includeNullRt: boolean
  condition: 'all' | 'congruent' | 'incongruent' | 'go' | 'nogo'
  responseType: 'all' | 'hits' | 'omissions' | 'commissions' | 'correct_rejections'
  sortBy: 'date' | 'participant' | 'accuracy' | 'response_time'
  sortOrder: 'asc' | 'desc'
}

export type ResearchQuery = {
  projects: string[]
  filters: AssessmentOptions
  advanced?: AdvancedFilterValues
}

const empty: AssessmentFacets = {
  participant_id: [],
  visit: [],
  evaluator_id: [],
  test_version: [],
  platform: [],
  test_code: [],
}

const labels = {
  participant_id: 'Participantes (códigos)',
  visit: 'Visitas',
  evaluator_id: 'Avaliadores (identificação técnica)',
  test_version: 'Versões',
  platform: 'Plataformas',
} as const

export function ResearchFilters({
  projects,
  initialProject,
  loading,
  onApply,
}: {
  projects: Project[]
  initialProject: string
  loading: boolean
  onApply(query: ResearchQuery): void
}) {
  const [selected, setSelected] = useState([initialProject])
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [instrument, setInstrument] = useState('')
  const [values, setValues] = useState<Record<keyof typeof labels, string[]>>({
    participant_id: [],
    visit: [],
    evaluator_id: [],
    test_version: [],
    platform: [],
  })

  // Catálogo avançado de filtros combinados (REQ-REL-004)
  const [searchText, setSearchText] = useState('')
  const [status, setStatus] = useState<AdvancedFilterValues['status']>('valid')
  const [accuracyRange, setAccuracyRange] = useState<AdvancedFilterValues['accuracyRange']>('all')
  const [rtRange, setRtRange] = useState<AdvancedFilterValues['rtRange']>('all')
  const [includeNullRt, setIncludeNullRt] = useState(true)
  const [condition, setCondition] = useState<AdvancedFilterValues['condition']>('all')
  const [responseType, setResponseType] = useState<AdvancedFilterValues['responseType']>('all')
  const [sortBy, setSortBy] = useState<AdvancedFilterValues['sortBy']>('date')
  const [sortOrder, setSortOrder] = useState<AdvancedFilterValues['sortOrder']>('desc')

  const [facets, setFacets] = useState(empty)
  const [error, setError] = useState<string | null>(null)
  const [validation, setValidation] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    const io = new AbortController()
    setFacets(empty)
    setError(null)
    if (!selected.length || selected.length > 20 || (start && end && start > end)) {
      setPending(false)
      return () => io.abort()
    }
    setPending(true)
    void (async () => {
      try {
        const merged: AssessmentFacets = { ...empty }
        for (const id of selected) {
          const page = await getAssessmentOptions(id, {
            start_date: start || undefined,
            end_date: end || undefined,
            test_code: instrument || undefined,
            signal: io.signal,
          })
          for (const key of Object.keys(empty) as (keyof AssessmentFacets)[]) {
            Object.assign(merged, { [key]: [...new Set([...merged[key], ...page[key]])].sort() })
          }
        }
        if (!io.signal.aborted) setFacets(merged)
      } catch (cause) {
        if (!io.signal.aborted) setError(apiErrorMessage(cause))
      } finally {
        if (!io.signal.aborted) setPending(false)
      }
    })()
    return () => io.abort()
  }, [selected, start, end, instrument, revision])

  function apply(event?: FormEvent) {
    event?.preventDefault()
    setValidation(null)
    if (!selected.length || selected.length > 20) {
      setValidation('Selecione de 1 a 20 projetos para consultar.')
      return
    }
    if (start && end && start > end) {
      setValidation('A data inicial deve ser anterior ou igual à final.')
      return
    }
    if (Object.values(values).some(items => items.length > 100)) {
      setValidation('Selecione no máximo 100 opções por campo.')
      return
    }
    onApply({
      projects: [...selected],
      filters: {
        ...values,
        platform: values.platform.filter((value): value is 'web' | 'psychopy' => value === 'web' || value === 'psychopy'),
        start_date: start || undefined,
        end_date: end || undefined,
        test_code: instrument || undefined,
      },
      advanced: {
        searchText,
        status,
        accuracyRange,
        rtRange,
        includeNullRt,
        condition,
        responseType,
        sortBy,
        sortOrder,
      },
    })
  }

  function clear() {
    setValidation(null)
    setSelected([initialProject])
    setStart('')
    setEnd('')
    setInstrument('')
    setValues({ participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: [] })
    setSearchText('')
    setStatus('valid')
    setAccuracyRange('all')
    setRtRange('all')
    setIncludeNullRt(true)
    setCondition('all')
    setResponseType('all')
    setSortBy('date')
    setSortOrder('desc')
    onApply({ projects: [initialProject], filters: {} })
  }

  return (
    <form onSubmit={apply} className="research-filters" aria-label="Filtros da consulta">
      <h3>Filtrar resultados</h3>
      <p className="quiet">
        Seleções do mesmo campo são alternativas; os campos são combinados. Sem seleção, todas as opções desse campo.
        Use Ctrl/Cmd ou Shift e as setas para selecionar várias opções.
      </p>

      {/* Catálogo de filtros combinados básicos e avançados (REQ-REL-004) */}
      <div className="dashboard-filters">
        <label className="project-filter">
          Projetos da consulta
          <select
            multiple
            value={selected}
            onChange={event => setSelected([...event.target.selectedOptions].map(option => option.value))}
          >
            {projects.map(project => (
              <option key={project.id} value={project.id} title={`${project.code} — ${project.name}`}>
                {project.code}
                {project.active ? '' : ' (inativo)'}
              </option>
            ))}
          </select>
        </label>
        <label>
          Data inicial
          <input type="date" value={start} onChange={event => setStart(event.target.value)} />
        </label>
        <label>
          Data final
          <input type="date" value={end} onChange={event => setEnd(event.target.value)} />
        </label>
        <label>
          Instrumento da consulta
          <select value={instrument} onChange={event => setInstrument(event.target.value)}>
            <option value="">Todos (exibir um por vez)</option>
            {[...new Set([...facets.test_code, ...(instrument ? [instrument] : [])])].map(code => (
              <option key={code}>{code}</option>
            ))}
          </select>
        </label>
        {(Object.keys(labels) as (keyof typeof labels)[]).map(key => (
          <label key={key}>
            {labels[key]}
            <select
              multiple
              value={values[key]}
              onChange={event => setValues({ ...values, [key]: [...event.target.selectedOptions].map(option => option.value) })}
            >
              {[...new Set([...facets[key], ...values[key]])].sort().map(value => (
                <option key={value} value={value} title={value}>
                  {value === 'LEGADO_NAO_MAPEADO' && key === 'evaluator_id'
                    ? 'Legado sem identificação técnica'
                    : value}
                </option>
              ))}
            </select>
          </label>
        ))}

        {/* Filtros avançados do catálogo analítico (REQ-REL-004) */}
        <label>
          Busca textual (paciente/código)
          <input
            type="search"
            placeholder="Ex: PAT-, V1, EVA-..."
            value={searchText}
            onChange={event => setSearchText(event.target.value)}
          />
        </label>
        <label>
          Status da avaliação
          <select value={status} onChange={event => setStatus(event.target.value as AdvancedFilterValues['status'])}>
            <option value="valid">Oficiais válidas (padrão)</option>
            <option value="all">Todas as avaliações</option>
            <option value="invalid">Interrompidas / Invalidadas</option>
          </select>
        </label>
        <label>
          Faixa de precisão
          <select
            value={accuracyRange}
            onChange={event => setAccuracyRange(event.target.value as AdvancedFilterValues['accuracyRange'])}
          >
            <option value="all">Todas as precisões</option>
            <option value="under50">&lt; 50%</option>
            <option value="50to80">50% a 79%</option>
            <option value="80plus">≥ 80%</option>
          </select>
        </label>
        <label>
          Faixa de tempo de reação (RT)
          <select
            value={rtRange}
            onChange={event => setRtRange(event.target.value as AdvancedFilterValues['rtRange'])}
          >
            <option value="all">Todos os tempos</option>
            <option value="under500ms">&lt; 0,5 s</option>
            <option value="500to1000ms">0,5 a &lt; 1,0 s</option>
            <option value="1000to1500ms">1,0 a &lt; 1,5 s</option>
            <option value="1500msPlus">≥ 1,5 s</option>
          </select>
        </label>
        <label>
          Tipo de resposta / erro
          <select
            value={responseType}
            onChange={event => setResponseType(event.target.value as AdvancedFilterValues['responseType'])}
          >
            <option value="all">Todos os tipos</option>
            <option value="hits">Com acertos (Hits &gt; 0)</option>
            <option value="omissions">Com erros de omissão (&gt; 0)</option>
            <option value="commissions">Com erros de comissão (&gt; 0)</option>
            <option value="correct_rejections">Com rejeições corretas (&gt; 0)</option>
          </select>
        </label>
        <label>
          Condição experimental
          <select
            value={condition}
            onChange={event => setCondition(event.target.value as AdvancedFilterValues['condition'])}
          >
            <option value="all">Todas as condições</option>
            <option value="go">Apenas blocos com Go</option>
            <option value="nogo">Apenas blocos com No-Go</option>
          </select>
        </label>
        <label>
          Critério de ordenação
          <select
            value={sortBy}
            onChange={event => setSortBy(event.target.value as AdvancedFilterValues['sortBy'])}
          >
            <option value="date">Data de início</option>
            <option value="participant">Participante (código)</option>
            <option value="accuracy">Precisão</option>
            <option value="response_time">Tempo de reação mediano</option>
          </select>
        </label>
        <label>
          Direção da ordenação
          <select
            value={sortOrder}
            onChange={event => setSortOrder(event.target.value as AdvancedFilterValues['sortOrder'])}
          >
            <option value="desc">Decrescente (mais recente / maior)</option>
            <option value="asc">Crescente (mais antigo / menor)</option>
          </select>
        </label>
      </div>

      <div style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={includeNullRt}
            onChange={event => setIncludeNullRt(event.target.checked)}
          />
          <span>Tratamento explícito de RT ausente: incluir avaliações sem acertos (RT mediano ausente)</span>
        </label>
      </div>

      <p className="quiet">
        Período inclusivo pela data da avaliação: WEB usa o dia UTC do início; legado conserva a data civil registrada,
        sem atribuir fuso. Máximo de 20 projetos e 5.000 avaliações completas por consulta; restrinja os filtros para
        volumes maiores.
      </p>
      {validation && <p role="alert">{validation}</p>}
      {pending && <p role="status">Carregando opções autorizadas…</p>}
      {error && (
        <>
          <p role="alert">Opções de filtro: {error}</p>
          <button type="button" className="button secondary" onClick={() => setRevision(n => n + 1)}>
            Atualizar opções
          </button>
        </>
      )}
      <button className="button primary" type="submit" disabled={loading || pending || !!error}>
        Aplicar filtros
      </button>
      <button className="button secondary" type="button" onClick={clear}>
        Limpar filtros
      </button>
    </form>
  )
}
