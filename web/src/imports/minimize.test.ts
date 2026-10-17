import { describe, expect, it } from 'vitest'
import { CsvMinimizationError, MAX_IMPORT_BYTES, STROOP_COLUMNS, minimizeCsv } from './minimize'

function csv(name = 'NOME SINTETICO RESTRITO', initials = 'NS') {
  const row = STROOP_COLUMNS.map(column => ({
    project: 'SYNTHETIC_PROJECT', participant_id: 'P_SYNTHETIC', participant_name: name,
    initials, visit: 'V1', evaluator: 'E_SYNTHETIC', assessment_id: '00000000-0000-4000-8000-000000000001',
    assessment_date: '2026-01-01', started_at: '2026-01-01T10:00:00-03:00',
    test_code: 'stroop_go_nogo_ptbr', test_version: '0.2.2', block: 'main', trial_number: '1',
    word: 'VERDE', ink_color: 'green', condition: 'congruent', correct_response: 'space',
    key_pressed: 'space', reaction_time: '0.512', correct: '1', error_type: 'hit',
  } as Record<string, string>)[column]).join(',')
  return `${STROOP_COLUMNS.join(',')}\r\n${row}\r\n`
}

describe('minimizacao local de CSV', () => {
  it('redige nome/iniciais antes do envio e preserva o arquivo original', async () => {
    const original = csv()
    const file = new File([original], 'SYNTHETIC_PRIVATE.csv', { type: 'text/csv' })
    const output = await minimizeCsv(file)
    const result = await output.text()
    expect(result).toContain('NAO_COLETADO,,V1')
    expect(result).not.toContain('NOME SINTETICO RESTRITO')
    expect(result).not.toContain('NS')
    expect(await file.text()).toBe(original)
  })

  it('escapa delimitadores e aspas sem alterar os demais campos', async () => {
    const source = csv('NOME SINTETICO RESTRITO')
      .replace('SYNTHETIC_PROJECT,P_SYNTHETIC', '"SYNTHETIC, PROJECT",P_SYNTHETIC')
    const result = await (await minimizeCsv(new File([source], 'x.csv'))).text()
    expect(result).toContain('"SYNTHETIC, PROJECT",P_SYNTHETIC,NAO_COLETADO,,V1')
  })

  it('recusa cabecalho, codificacao, NUL, tamanho e limite de registros invalidos', async () => {
    const invalid = [
      new File(['a,b\r\n1,2\r\n'], 'x.csv'),
      new File([new Uint8Array([0xff])], 'x.csv'),
      new File([csv() + '\u0000'], 'x.csv'),
      new File(['x'.repeat(MAX_IMPORT_BYTES + 1)], 'x.csv'),
      new File([`${STROOP_COLUMNS.join(',')}\r\n${'x'.repeat(10_001).split('').map(x => x).join('\r\n')}`], 'x.csv'),
    ]
    for (const file of invalid) await expect(minimizeCsv(file)).rejects.toBeInstanceOf(CsvMinimizationError)
  })
})
