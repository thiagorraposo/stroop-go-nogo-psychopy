import { useId, useState } from 'react'

/** Busca apenas opções; a seleção continua sendo um listbox nativo com teclado. */
export function SearchableMultiSelect({ label, options, value, onChange }: {
  label: string
  options: { value: string; label: string }[]
  value: string[]
  onChange(values: string[]): void
}) {
  const id = useId()
  const [search, setSearch] = useState('')
  const needle = search.toLocaleLowerCase('pt-BR')
  const matches = options.filter(option => value.includes(option.value)
    || option.label.toLocaleLowerCase('pt-BR').includes(needle))
  return <div>
    <label htmlFor={`${id}-search`}>Buscar opções de {label.toLocaleLowerCase('pt-BR')}</label>
    <input id={`${id}-search`} type="search" value={search} maxLength={120}
      onChange={event => setSearch(event.target.value)} aria-controls={`${id}-list`} />
    <label htmlFor={`${id}-list`}>{label}</label>
    <select id={`${id}-list`} multiple value={value}
      onChange={event => onChange([...event.target.selectedOptions].map(option => option.value))}>
      {matches.map(option => <option key={option.value} value={option.value} title={option.label}>{option.label}</option>)}
    </select>
    {!matches.length && <p role="status">Nenhuma opção corresponde à busca.</p>}
  </div>
}
