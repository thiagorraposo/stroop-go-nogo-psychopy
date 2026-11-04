import snapshot from '../../../condicoes/web_protocol.json'
import practiceSource from '../../../condicoes/pratica_stroop_go_nogo_ptbr.csv?raw'
import mainSource from '../../../condicoes/bloco_principal_stroop_go_nogo_ptbr.csv?raw'

export const PROTOCOL = snapshot
export type InkColor = keyof typeof PROTOCOL.colors
export type Condition = {
  condition_id: number
  word: string
  ink_color: InkColor
  ink_color_display: string
  condition: 'congruent' | 'incongruent'
  correct_response: 'space' | null
}
export type PracticeSummary = { correct: number; total: number }
export type InterruptionReason = 'focus_lost' | 'visibility_hidden' | 'escape' | 'page_closed' | 'timing_invalid'

/** CSVs versionados simples; recusar qualquer mudanca de formato em vez de reinterpretar. */
function parseConditions(raw: string, kind: 'practice' | 'main'): Condition[] {
  const count = PROTOCOL[kind].trials
  const [header, ...lines] = raw.trim().split(/\r?\n/)
  if (header !== 'trial_number,word,ink_color,ink_color_display,condition,correct_response') {
    throw new Error('Fonte de condições incompatível.')
  }
  const conditions = lines.map(line => {
    const parts = line.split(',')
    const [id, word, color, , kind, response] = parts
    if (parts.length !== 6 || !id || !/^[1-9][0-9]*$/.test(id) || Number(id) > count || !word || word.includes('"') ||
      !color || !Object.hasOwn(PROTOCOL.colors, color) ||
      (kind !== 'congruent' && kind !== 'incongruent') ||
      response !== (kind === 'congruent' ? 'space' : '')) throw new Error('Condição incompatível.')
    return {
      condition_id: Number(id), word, ink_color: color as InkColor,
      ink_color_display: PROTOCOL.colors[color as InkColor], condition: kind,
      correct_response: response === 'space' ? 'space' : null,
    } as Condition
  })
  if (conditions.length !== count || new Set(conditions.map(row => row.condition_id)).size !== count ||
    conditions.filter(row => row.condition === 'congruent').length !== count / 2) throw new Error('Pool de condições incompatível.')
  return conditions
}

export const parsePracticeSource = (raw: string): Condition[] => parseConditions(raw, 'practice')
export const parseMainSource = (raw: string): Condition[] => parseConditions(raw, 'main')
export const PRACTICE_CONDITIONS = parsePracticeSource(practiceSource)
export const MAIN_CONDITIONS = parseMainSource(mainSource)

/** Ordem local antes de W13; o motor aceita a ordem persistida sem reembaralhar. */
export function createMainOrder(): Condition[] {
  const order = [...MAIN_CONDITIONS]
  for (let index = order.length - 1; index > 0; index -= 1) {
    const other = Math.floor(Math.random() * (index + 1))
    ;[order[index], order[other]] = [order[other]!, order[index]!]
  }
  return order
}
