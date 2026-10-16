/** Agregacoes descritivas sobre o conjunto autorizado filtrado, sem normas. */
import { formatHalfEven } from '../experiment/summary'
import type { Assessment } from '../api/assessments'
export function median(values: readonly number[]): number | null {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[middle]! : (sorted[middle - 1]! + sorted[middle]!) / 2
}
export function summarize(rows: readonly Assessment[]) {
  const accuracies: number[] = [], times: number[] = []
  let omissions = 0, commissions = 0
  for (const row of rows) {
    if ('metrics' in row.summary) continue
    if (row.summary.accuracy !== null) accuracies.push(row.summary.accuracy)
    if (row.summary.response_time_seconds !== null) times.push(row.summary.response_time_seconds)
    omissions += row.summary.omission_errors
    commissions += row.summary.commission_errors
  }
  return { assessments: rows.length, participants: new Set(rows.map(row => row.participant_id)).size,
    meanAccuracy: accuracies.length ? accuracies.reduce((a, b) => a + b, 0) / accuracies.length : null,
    medianAccuracy: median(accuracies), medianResponseSeconds: median(times), omissions, commissions }
}
export function countByDate(rows: readonly Assessment[]): [string, number][] {
  const dates = new Map<string, number>()
  for (const row of rows) {
    const day = row.started_at.slice(0, 10)
    dates.set(day, (dates.get(day) ?? 0) + 1)
  }
  return [...dates].sort(([a], [b]) => a.localeCompare(b))
}
export function accuracyByVisit(rows: readonly Assessment[]): [string, number][] {
  const values = new Map<string, number[]>()
  for (const row of rows) {
    if (!('accuracy' in row.summary) || row.summary.accuracy === null) continue
    const group = values.get(row.visit) ?? []; group.push(row.summary.accuracy); values.set(row.visit, group)
  }
  return [...values].sort(([a], [b]) => a.localeCompare(b)).map(([visit, scores]) => [visit, scores.reduce((a, b) => a + b, 0) / scores.length])
}
export function responseDistribution(rows: readonly Assessment[]): [string, number][] {
  const groups: [string, number][] = [['< 0,5 s', 0], ['0,5 a < 1 s', 0], ['1 a < 1,5 s', 0], ['1,5 a < 2 s', 0], ['≥ 2 s', 0]]
  for (const row of rows) {
    if (!('response_time_seconds' in row.summary) || row.summary.response_time_seconds === null) continue
    const index = Math.min(4, Math.max(0, Math.floor(row.summary.response_time_seconds / 0.5)))
    groups[index]![1] += 1
  }
  return groups
}

/** Exibicao igual ao formatador Python do Streamlit, com separador pt-BR. */
export function formatMetric(value: number | null, digits = 0): string {
  if (value === null) return '—'
  const sign = value < 0 || Object.is(value, -0) ? '-' : ''
  return sign + formatHalfEven(Math.abs(value), digits).replace('.', ',')
}
