/** Parser RFC 4180 restrito aos formatos oficiais ja suportados pelo nucleo. */
export const MAX_IMPORT_BYTES = 5 * 1024 * 1024
export const MAX_IMPORT_RECORDS = 10_000
export const REDACTED_PARTICIPANT_NAME = 'NAO_COLETADO'

export const STROOP_COLUMNS = [
  'project', 'participant_id', 'participant_name', 'initials', 'visit', 'evaluator',
  'assessment_id', 'assessment_date', 'started_at', 'test_code', 'test_version',
  'block', 'trial_number', 'word', 'ink_color', 'condition', 'correct_response',
  'key_pressed', 'reaction_time', 'correct', 'error_type',
] as const

export const SYNTHETIC_COLUMNS = [
  'project', 'participant_id', 'participant_name', 'initials', 'visit', 'evaluator',
  'assessment_id', 'assessment_date', 'started_at', 'test_code', 'test_version',
  'metric_code', 'metric_label', 'metric_value', 'unit',
] as const

export class CsvMinimizationError extends Error {
  constructor() { super('Não foi possível validar e minimizar este CSV.'); this.name = 'CsvMinimizationError' }
}

function parseCsv(text: string): string[][] {
  const rows: string[][] = []
  let row: string[] = [], field = '', quoted = false, afterQuote = false
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    if (quoted) {
      if (char === '"') {
        if (text[index + 1] === '"') { field += '"'; index += 1 }
        else { quoted = false; afterQuote = true }
      } else field += char
      continue
    }
    if (afterQuote && char !== ',' && char !== '\r' && char !== '\n') throw new CsvMinimizationError()
    if (char === '"') {
      if (field || afterQuote) throw new CsvMinimizationError()
      quoted = true
    } else if (char === ',') {
      row.push(field); field = ''; afterQuote = false
    } else if (char === '\r' || char === '\n') {
      if (char === '\r' && text[index + 1] === '\n') index += 1
      row.push(field); field = ''; afterQuote = false
      if (row.some(value => value !== '') || rows.length > 0 || index < text.length - 1) {
        rows.push(row); row = []
        if (rows.length > MAX_IMPORT_RECORDS + 1) throw new CsvMinimizationError()
      }
    } else field += char
  }
  if (quoted) throw new CsvMinimizationError()
  if (row.length || field || afterQuote) {
    row.push(field); rows.push(row)
  }
  if (!rows.length || rows.length > MAX_IMPORT_RECORDS + 1) throw new CsvMinimizationError()
  return rows
}

function quote(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value
}

/** Retorna bytes novos; jamais modifica o File original nem seu buffer. */
export async function minimizeCsv(file: File): Promise<Blob> {
  if (file.size <= 0 || file.size > MAX_IMPORT_BYTES) throw new CsvMinimizationError()
  let text: string
  try { text = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer()) }
  catch { throw new CsvMinimizationError() }
  if (text.includes('\u0000')) throw new CsvMinimizationError()
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1)
  const records = parseCsv(text)
  const header = records[0]
  if (!header) throw new CsvMinimizationError()
  const allowed = [STROOP_COLUMNS, SYNTHETIC_COLUMNS].find(columns =>
    columns.length === header.length && columns.every((column, index) => header[index] === column))
  if (!allowed || records.length < 2 || records.slice(1).some(row => row.length !== header.length)) {
    throw new CsvMinimizationError()
  }
  const nameIndex = header.indexOf('participant_name'), initialsIndex = header.indexOf('initials')
  if (nameIndex < 0 || initialsIndex < 0) throw new CsvMinimizationError()
  const minimized = records.map((record, rowIndex) => {
    if (rowIndex === 0) return record.map(quote).join(',')
    const copy = [...record]
    copy[nameIndex] = REDACTED_PARTICIPANT_NAME
    copy[initialsIndex] = ''
    return copy.map(quote).join(',')
  }).join('\r\n') + '\r\n'
  const blob = new Blob([minimized], { type: 'text/csv;charset=utf-8' })
  if (blob.size > MAX_IMPORT_BYTES) throw new CsvMinimizationError()
  return blob
}
