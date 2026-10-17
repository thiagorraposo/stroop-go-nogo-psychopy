// @vitest-environment jsdom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, expect, test } from 'vitest'
import { GenericInstrumentResults, ResearchVisualizations } from './ResearchVisualizations'
import type { Assessment, Project } from '../api/assessments'
Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
const projects: Project[] = ['A', 'B'].map(id => ({ id, code: `PROJETO_${id}`, name: 'Sintético', active: true, created_at: '2026-10-17T00:00:00Z' }))
const row = (assessment_id: string, project_id = 'A'): Assessment & { project_id: string } => ({ project_id, assessment_id,
  participant_id: 'P_SINTETICO', visit: 'V1', evaluator_id: null, created_at: '2026-10-17T00:00:00Z', started_at: '2026-10-17T10:00:00Z',
  platform: 'web', test_code: 'stroop_go_nogo_ptbr', test_version: '1.0.0', protocol_id: 'synthetic', app_version: 'web-0.1.0',
  summary: { accuracy_go_trials: 75, accuracy_no_go_trials: 75, total_go_trials: 8, total_no_go_trials: 8, accuracy: 75, response_time_seconds: 0.625, total_trials: 16, hits: 6, correct_rejections: 6, omission_errors: 2, commission_errors: 2 } })
const container = document.createElement('div')
document.body.append(container)
let root = createRoot(container)
afterEach(async () => { await act(async () => root.unmount()); container.replaceChildren(); root = createRoot(container) })
const table = (caption: string) => [...container.querySelectorAll('table')].find(table => table.caption?.textContent === caption)!

test('separa pessoas por projeto, preserva visitas repetidas e ordena inicio/id sem mutar fonte', async () => {
  const rows = [row('Z'), row('OUTRO', 'B'), row('A')]
  await act(async () => root.render(<ResearchVisualizations rows={rows} projects={projects} />))
  const select = container.querySelector('select')!
  expect([...select.options].map(option => [option.value, option.textContent])).toEqual([
    ['["A","P_SINTETICO"]', 'PROJETO_A · P_SINTETICO'], ['["B","P_SINTETICO"]', 'PROJETO_B · P_SINTETICO'],
  ])
  const longitudinal = table('Evolução do participante por avaliação')
  expect([...longitudinal.tBodies[0]!.rows].map(row => row.cells[4]!.textContent)).toEqual(['A', 'Z'])
  expect([...longitudinal.tBodies[0]!.rows].map(row => row.cells[2]!.textContent)).toEqual(['V1', 'V1'])
  expect(rows.map(row => row.assessment_id)).toEqual(['Z', 'OUTRO', 'A'])
  await act(async () => { select.value = '["B","P_SINTETICO"]'; select.dispatchEvent(new Event('change', { bubbles: true })) })
  expect(longitudinal.tBodies[0]!.rows).toHaveLength(1)
  expect(longitudinal.textContent).toContain('OUTRO'); expect(longitudinal.textContent).not.toContain('PROJETO_A')
})

test('contagens por projeto e escalas separadas, ausencias nao viram zero', async () => {
  const missing = row('SEM_ACERTOS')
  if ('accuracy' in missing.summary) missing.summary = { ...missing.summary, accuracy: null, response_time_seconds: null, omission_errors: 8 }
  await act(async () => root.render(<ResearchVisualizations rows={[row('A'), missing, row('B', 'B')]} projects={projects} />))
  const totals = table('Contagens de erros por projeto')
  expect([...totals.tBodies[0]!.rows].map(row => [...row.cells].map(cell => cell.textContent))).toEqual([
    ['PROJETO_A', '10', '4'], ['PROJETO_B', '2', '2'],
  ])
  const figures = [...container.querySelectorAll('figure')]
  const precision = figures.find(figure => figure.querySelector('figcaption')?.textContent === 'Precisão por avaliação (%)')!
  const time = figures.find(figure => figure.querySelector('figcaption')?.textContent === 'Tempo mediano de resposta por avaliação (s)')!
  expect(precision.querySelector('meter')?.max).toBe(100)
  expect(time.querySelector('meter')?.max).toBe(0.625)
  expect(time.querySelectorAll('meter')).toHaveLength(1)
  expect(time.textContent).toContain('SEM_ACERTOS: Ausente')
  const missingCells = [...table('Evolução do participante por avaliação').tBodies[0]!.rows].find(row => row.cells[4]!.textContent === 'SEM_ACERTOS')!.cells
  expect(missingCells[5]?.textContent).toBe('Ausente'); expect(missingCells[6]?.textContent).toBe('Ausente')
})

test('mudanca de conjunto abandona participante ausente e conserva somente novos dados', async () => {
  await act(async () => root.render(<ResearchVisualizations rows={[row('A')]} projects={projects} />))
  await act(async () => root.render(<ResearchVisualizations rows={[row('B', 'B')]} projects={projects} />))
  expect(container.querySelector('select')?.value).toBe('["B","P_SINTETICO"]')
  expect(table('Evolução do participante por avaliação').textContent).not.toContain('PROJETO_A')
  await act(async () => root.render(<ResearchVisualizations rows={[]} projects={projects} />))
  expect(container.textContent).toBe('')
})

test('demo tem cards e graficos por avaliacao/unidade sem somar medias', async () => {
  const a = { ...row('DEMO_A'), test_code: 'instrumento_sintetico_demo', summary: { metrics: { demo_total: 4, demo_mean: 2.5 } } }
  const b = { ...row('DEMO_B', 'B'), test_code: 'instrumento_sintetico_demo', summary: { metrics: { demo_total: 8, demo_mean: 4.5 } } }
  await act(async () => root.render(<GenericInstrumentResults rows={[a, b]} projects={projects} />))
  const captions = [...container.querySelectorAll('figcaption')].map(node => node.textContent)
  expect(captions).toEqual(['Total demonstrativo (count) por avaliação', 'Média demonstrativa (unit) por avaliação'])
  expect([...container.querySelectorAll('dd')].map(node => node.textContent)).toEqual(['4,000 count', '8,000 count', '2,500 unit', '4,500 unit'])
  expect(table('Métricas por instrumento e avaliação').tBodies[0]!.rows).toHaveLength(4)
  expect(container.querySelectorAll('meter')).toHaveLength(4)
  expect(container.textContent).not.toContain('Precisão')
})

test('instrumento desconhecido preserva codigos e valor em tabela sem unidade inventada', async () => {
  const unknown = { ...row('GENERICO'), test_code: 'outro_instrumento', summary: { metrics: { score_sintetico: -2 } } }
  await act(async () => root.render(<GenericInstrumentResults rows={[unknown]} projects={projects} />))
  expect(container.querySelectorAll('figure')).toHaveLength(0)
  expect(container.querySelectorAll('meter')).toHaveLength(0)
  expect(table('Métricas por instrumento e avaliação').textContent).toContain('score_sintetico-2,000Não informada')
  expect(container.textContent).not.toContain('Demonstração sintética')
})

test('demo conserva negativos e metrica ausente sem preencher com zero', async () => {
  const negative = { ...row('DEMO_NEGATIVO'), test_code: 'instrumento_sintetico_demo', summary: { metrics: { demo_total: -4, demo_mean: -2.5 } } }
  const absent = { ...row('DEMO_AUSENTE'), test_code: 'instrumento_sintetico_demo', summary: { metrics: {} } }
  await act(async () => root.render(<GenericInstrumentResults rows={[negative, absent]} projects={projects} />))
  const meters = [...container.querySelectorAll('meter')]
  expect(meters.map(meter => [meter.value, meter.min])).toEqual([[-4, -4], [-2.5, -2.5]])
  const values = [...container.querySelectorAll('dd')].map(node => node.textContent?.trim())
  expect(values).toEqual(['Ausente', '-4,000 count', 'Ausente', '-2,500 unit'])
  expect(container.textContent).not.toContain('0,000')
})
