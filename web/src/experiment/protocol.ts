import snapshot from '../../../condicoes/web_protocol.json'
import practiceSource from '../../../condicoes/pratica_stroop_go_nogo_ptbr.csv?raw'

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
export function parsePracticeSource(raw: string): Condition[] {
  const [header, ...lines] = raw.trim().split(/\r?\n/)
  if (header !== 'trial_number,word,ink_color,ink_color_display,condition,correct_response') {
    throw new Error('Fonte de prática incompatível.')
  }
  const conditions = lines.map(line => {
    const parts = line.split(',')
    const [id, word, color, , kind, response] = parts
    if (parts.length !== 6 || !id || !/^[1-4]$/.test(id) || !word || word.includes('"') ||
      !color || !Object.hasOwn(PROTOCOL.colors, color) ||
      (kind !== 'congruent' && kind !== 'incongruent') ||
      response !== (kind === 'congruent' ? 'space' : '')) throw new Error('Condição de prática incompatível.')
    return {
      condition_id: Number(id), word, ink_color: color as InkColor,
      ink_color_display: PROTOCOL.colors[color as InkColor], condition: kind,
      correct_response: response === 'space' ? 'space' : null,
    } as Condition
  })
  if (conditions.length !== PROTOCOL.practice.trials || new Set(conditions.map(row => row.condition_id)).size !== 4 ||
    conditions.filter(row => row.condition === 'congruent').length !== 2) throw new Error('Pool de prática incompatível.')
  return conditions
}

export const PRACTICE_CONDITIONS = parsePracticeSource(practiceSource)
