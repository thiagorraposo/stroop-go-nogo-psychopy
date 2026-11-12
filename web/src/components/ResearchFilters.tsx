import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, apiErrorMessage } from '../api/client'
import { SearchableMultiSelect } from './SearchableMultiSelect'
import { getAssessmentOptions } from '../api/assessments'
import type { AssessmentFacets, Project } from '../api/assessments'

import { defaultQuery, normalizeQuery, queryKey } from '../dashboard/query'
import type { AdvancedFilterValues, ResearchQuery } from '../dashboard/query'
export type { AdvancedFilterValues, ResearchQuery } from '../dashboard/query'

const toArray = (v: string | readonly string[] | undefined): string[] => typeof v === 'string' ? [v] : [...v ?? []]

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
  value, applied, onChange, refreshKey = 0,
}: {
  projects: Project[]
  initialProject: string
  loading: boolean
  onApply(query: ResearchQuery): void
  refreshKey?: number
  value?: ResearchQuery
  applied?: ResearchQuery
  onChange?(query: ResearchQuery): void
}) {
  const [localDraft, setLocalDraft] = useState(() => defaultQuery(initialProject))
  const [localApplied, setLocalApplied] = useState(() => defaultQuery(initialProject))
  const draft = value ?? localDraft
  const appliedQuery = applied ?? localApplied
  const update = (next: ResearchQuery) => { setLocalDraft(next); onChange?.(next) }
  const selected = draft.projects
  const start = draft.filters.start_date ?? ''
  const end = draft.filters.end_date ?? ''
  const instrument = draft.filters.test_code ?? ''
  const values = {
    participant_id: toArray(draft.filters.participant_id),
    visit: toArray(draft.filters.visit),
    evaluator_id: toArray(draft.filters.evaluator_id),
    test_version: toArray(draft.filters.test_version),
    platform: toArray(draft.filters.platform),
  }
  const advanced = { ...defaultQuery(initialProject).advanced!, ...draft.advanced }
  const { searchText, status, accuracyRange, rtRange, includeNullRt, condition, responseType, sortBy, sortOrder } = advanced
  const setSelected = (projects: string[]) => update({ ...draft, projects })
  const setStart = (start_date: string) => update({ ...draft, filters: { ...draft.filters, start_date: start_date || undefined } })
  const setEnd = (end_date: string) => update({ ...draft, filters: { ...draft.filters, end_date: end_date || undefined } })
  const setInstrument = (test_code: string) => update({ ...draft, filters: { ...draft.filters, test_code: test_code || undefined } })
  const setValues = (next: typeof values) => update({ ...draft, filters: { ...draft.filters, ...next,
    platform: next.platform.filter((v): v is 'web' | 'psychopy' => v === 'web' || v === 'psychopy') } })
  const setAdvanced = <K extends keyof AdvancedFilterValues>(key: K, next: AdvancedFilterValues[K]) =>
    update({ ...draft, advanced: { ...advanced, [key]: next } })
  const dirty = queryKey(draft) !== queryKey(appliedQuery)

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
            signal: io.signal,
          })
          for (const key of Object.keys(empty) as (keyof AssessmentFacets)[]) {
            Object.assign(merged, { [key]: [...new Set([...merged[key], ...page[key]])].sort() })
          }
        }
        if (!io.signal.aborted) setFacets(merged)
      } catch (cause) {
        if (!io.signal.aborted) {
          setError(apiErrorMessage(cause))
          if (cause instanceof ApiError && [401, 403].includes(cause.status)) window.dispatchEvent(new Event('stroop-professional-session-ended'))
        }
      } finally {
        if (!io.signal.aborted) setPending(false)
      }
    })()
    return () => io.abort()
  }, [selected, start, end, revision, refreshKey])

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
    const next = normalizeQuery(draft)
    setLocalApplied(next)
    onApply(next)
  }

  function clear() {
    setValidation(null)
    update(defaultQuery(initialProject))
  }

  const activeChips: { label: string; onRemove: () => void }[] = []
  if (searchText) {
    activeChips.push({ label: `Busca: "${searchText}"`, onRemove: () => setAdvanced('searchText', '') })
  }
  if (start || end) {
    activeChips.push({ label: `Período: ${start || '…'} a ${end || '…'}`, onRemove: () => update({ ...draft, filters: { ...draft.filters, start_date: undefined, end_date: undefined } }) })
  }
  if (instrument) {
    activeChips.push({ label: `Instrumento: ${instrument}`, onRemove: () => setInstrument('') })
  }
  if (status !== 'valid') {
    activeChips.push({ label: `Status: ${status === 'all' ? 'Todas' : 'Inválidas'}`, onRemove: () => setAdvanced('status', 'valid') })
  }
  if (accuracyRange !== 'all') {
    activeChips.push({ label: `Precisão: ${accuracyRange}`, onRemove: () => setAdvanced('accuracyRange', 'all') })
  }
  if (rtRange !== 'all') {
    activeChips.push({ label: `RT: ${rtRange}`, onRemove: () => setAdvanced('rtRange', 'all') })
  }
  if (condition !== 'all') {
    activeChips.push({ label: `Condição: ${condition}`, onRemove: () => setAdvanced('condition', 'all') })
  }
  if (responseType !== 'all') {
    activeChips.push({ label: `Resposta: ${responseType}`, onRemove: () => setAdvanced('responseType', 'all') })
  }
  for (const key of Object.keys(labels) as (keyof typeof labels)[]) {
    if (values[key].length > 0) {
      activeChips.push({
        label: `${labels[key]}: ${values[key].length} sel.`,
        onRemove: () => setValues({ ...values, [key]: [] }),
      })
    }
  }

  return (
    <form aria-busy={loading} onSubmit={apply} className="research-filters filter-catalog-card" aria-label="Filtros da consulta">
      <div className="panel-header-section" style={{ borderBottom: 'none', paddingBottom: 0, marginBottom: '0.75rem' }}>
        <h3>Filtrar resultados</h3>
        <p className="panel-subtitle">Catálogo unificado de filtros por projeto, dimensões experimentais e métricas.</p>
      </div>

      <details className="context-help-details">
        <summary className="context-help-summary">
          <span>ℹ️ Orientações e regras de combinação dos filtros</span>
        </summary>
        <div className="context-help-content">
          <p className="quiet">
            Seleções do mesmo campo são alternativas; os campos são combinados. Sem seleção, todas as opções desse campo.
            Use Ctrl/Cmd ou Shift e as setas para selecionar várias opções.
          </p>
          <p className="quiet">
            Período inclusivo pela data da avaliação: WEB usa o dia UTC do início; legado conserva a data civil registrada,
            sem atribuir fuso. Máximo de 20 projetos e 5.000 avaliações completas por consulta; restrinja os filtros para
            volumes maiores.
          </p>
        </div>
      </details>

      {activeChips.length > 0 && (
        <div className="active-filters-bar" aria-label="Filtros do rascunho">
          <span className="active-filters-label">Filtros do rascunho ({activeChips.length}):</span>
          {activeChips.map((chip, idx) => (
            <span key={idx} className="filter-chip">
              {chip.label}
              <button
                type="button"
                className="filter-chip-remove"
                aria-label={`Remover filtro ${chip.label}`}
                onClick={chip.onRemove}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Catálogo de filtros combinados básicos e avançados em 4 grupos (REQ-REL-004) */}
      <div className="filter-groups-grid">
        {/* GRUPO 1: ESCOPO E PERÍODO */}
        <div className="filter-group-box">
          <div className="filter-group-legend">
            <span>📅</span>
            <span>1. Escopo e Período</span>
          </div>
          <SearchableMultiSelect label="Projetos da consulta" value={selected} onChange={setSelected}
            options={projects.map(project => ({ value: project.id, label: `${project.code}${project.active ? '' : ' (inativo)'}` }))} />
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
              <option value="">Todos</option>
              {[...new Set([...facets.test_code, ...(instrument ? [instrument] : [])])].map(code => (
                <option key={code}>{code}</option>
              ))}
            </select>
          </label>
        </div>

        <details className="advanced-query-filters">
          <summary>Filtros avançados e ordenação</summary>
        {/* GRUPO 2: DIMENSÕES EXPERIMENTAIS */}
        <div className="filter-group-box">
          <div className="filter-group-legend">
            <span>🔬</span>
            <span>2. Dimensões Experimentais</span>
          </div>
          {(Object.keys(labels) as (keyof typeof labels)[]).map(key => (
            <SearchableMultiSelect key={key} label={labels[key]} value={values[key]}
              onChange={items => setValues({ ...values, [key]: items })}
              options={[...new Set([...facets[key], ...values[key]])].sort().map(value => ({ value,
                label: value === 'LEGADO_NAO_MAPEADO' && key === 'evaluator_id' ? 'Legado sem identificação técnica' : value }))} />
          ))}
        </div>

        {/* GRUPO 3: CRITÉRIOS DE PESQUISA & MÉTRICAS */}
        <div className="filter-group-box">
          <div className="filter-group-legend">
            <span>📊</span>
            <span>3. Critérios & Métricas</span>
          </div>
          <label>
            Busca textual (paciente/código)
            <input
              type="search"
              maxLength={120}
              placeholder="Ex: PAT-, V1, EVA-..."
              value={searchText}
              onChange={event => setAdvanced('searchText', event.target.value)}
            />
          </label>
          <label>
            Status da avaliação
            <select value={status} onChange={event => setAdvanced('status', event.target.value as AdvancedFilterValues['status'])}>
              <option value="valid">Oficiais válidas (padrão)</option>
              <option value="all">Todas as avaliações</option>
              <option value="invalid">Interrompidas / Invalidadas</option>
            </select>
          </label>
          <label>
            Faixa de precisão
            <select
              value={accuracyRange}
              onChange={event => setAdvanced('accuracyRange', event.target.value as AdvancedFilterValues['accuracyRange'])}
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
              onChange={event => setAdvanced('rtRange', event.target.value as AdvancedFilterValues['rtRange'])}
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
              onChange={event => setAdvanced('responseType', event.target.value as AdvancedFilterValues['responseType'])}
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
              onChange={event => setAdvanced('condition', event.target.value as AdvancedFilterValues['condition'])}
            >
              <option value="all">Todas as condições</option>
              <option value="go">Apenas blocos com Go</option>
              <option value="nogo">Apenas blocos com No-Go</option>
            </select>
          </label>
        </div>

        {/* GRUPO 4: ORDENAÇÃO E TRATAMENTO */}
        <div className="filter-group-box">
          <div className="filter-group-legend">
            <span>⚙️</span>
            <span>4. Ordenação & Tratamento</span>
          </div>
          <label>
            Critério de ordenação
            <select
              value={sortBy}
              onChange={event => setAdvanced('sortBy', event.target.value as AdvancedFilterValues['sortBy'])}
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
              onChange={event => setAdvanced('sortOrder', event.target.value as AdvancedFilterValues['sortOrder'])}
            >
              <option value="desc">Decrescente (mais recente / maior)</option>
              <option value="asc">Crescente (mais antigo / menor)</option>
            </select>
          </label>
          <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
            <label style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', cursor: 'pointer', fontSize: '12px' }}>
              <input
                type="checkbox"
                checked={includeNullRt}
                onChange={event => setAdvanced('includeNullRt', event.target.checked)}
                style={{ width: 'auto', marginTop: '2px' }}
              />
              <span>Tratamento explícito de RT ausente: incluir avaliações sem acertos (RT mediano ausente)</span>
            </label>
          </div>
        </div>
        </details>
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
      {dirty && <p role="status">Alterações não aplicadas. Aplique ou descarte para habilitar downloads.</p>}
      <div className="filter-form-actions" style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '1.25rem', flexWrap: 'wrap' }}>
        <button className="button primary" type="submit">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
          Aplicar filtros
        </button>
        <button className="button secondary" type="button" onClick={clear}>
          Limpar filtros
        </button>
        {dirty && <button className="button secondary" type="button" onClick={() => update(appliedQuery)}>Descartar alterações</button>}
      </div>
    </form>
  )
}
