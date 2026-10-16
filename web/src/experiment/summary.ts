import { validMainResult } from './main-engine'
import type { MainResult } from './main-engine'

export type ResultSummary = {
  accuracy: number
  accuracy_go_trials: number
  accuracy_no_go_trials: number
  omission_errors: number
  omission_errors_percentage: number
  commission_errors: number
  response_time: number | null
  total_trials: number
  total_go_trials: number
  total_no_go_trials: number
  hits: number
  correct_rejections: number
}

/** Mesmas formulas do nucleo Python; ausencia de hits permanece ausencia. */
export function summarizeMain(result: MainResult): ResultSummary {
  if (!validMainResult(result)) throw new Error('Resultado principal inválido.')
  let hits = 0
  let omissions = 0
  let rejections = 0
  let commissions = 0
  const hitSeconds: number[] = []
  for (const [index, trial] of result.trials.entries()) {
    const go = result.order[index]!.condition === 'congruent'
    if (go && trial.key_pressed === 'space') {
      hits += 1
      hitSeconds.push(trial.reaction_time_ms! / 1000)
    } else if (go) omissions += 1
    else if (trial.key_pressed === 'space') commissions += 1
    else rejections += 1
  }
  hitSeconds.sort((a, b) => a - b)
  const midpoint = Math.floor(hitSeconds.length / 2)
  const rt = hitSeconds.length === 0 ? null : hitSeconds.length % 2
    ? hitSeconds[midpoint]! : (hitSeconds[midpoint - 1]! + hitSeconds[midpoint]!) / 2
  const goCount = hits + omissions
  const noGoCount = rejections + commissions
  return {
    accuracy: (hits + rejections) / result.trials.length * 100,
    accuracy_go_trials: hits / goCount * 100,
    accuracy_no_go_trials: rejections / noGoCount * 100,
    omission_errors: omissions, omission_errors_percentage: omissions / goCount * 100,
    commission_errors: commissions, response_time: rt, total_trials: result.trials.length,
    total_go_trials: goCount, total_no_go_trials: noGoCount, hits, correct_rejections: rejections,
  }
}

/** Arredondamento para par, incluindo representacao binaria como Python format. */
export function formatHalfEven(value: number, digits: number): string {
  if (!Number.isFinite(value) || value < 0 || !Number.isInteger(digits) || digits < 0 || digits > 6) {
    throw new Error('Valor de exibição inválido.')
  }
  // Decompor o float evita quantizar antes do arredondamento de exibicao.
  const buffer = new ArrayBuffer(8)
  const view = new DataView(buffer)
  view.setFloat64(0, value)
  const bits = view.getBigUint64(0)
  const exponent = Number((bits >> 52n) & 0x7ffn)
  let numerator = bits & ((1n << 52n) - 1n)
  let power = -1074
  if (exponent !== 0) { numerator |= 1n << 52n; power = exponent - 1023 - 52 }
  numerator *= 10n ** BigInt(digits)
  const denominator = power < 0 ? 1n << BigInt(-power) : 1n
  if (power >= 0) numerator <<= BigInt(power)
  let rounded = numerator / denominator
  const remainder = numerator % denominator
  if (remainder * 2n > denominator || remainder * 2n === denominator && rounded % 2n !== 0n) rounded += 1n
  const text = rounded.toString().padStart(digits + 1, '0')
  return digits === 0 ? text : `${text.slice(0, -digits)}.${text.slice(-digits)}`
}
