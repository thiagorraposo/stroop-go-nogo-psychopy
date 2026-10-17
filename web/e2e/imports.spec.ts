import { expect, test } from '@playwright/test'

const projectId = '11111111-1111-4111-8111-111111111111'
const operationId = '22222222-2222-4222-8222-222222222222'
const assessmentId = '33333333-3333-4333-8333-333333333333'
const project = { id: projectId, code: 'SYNTHETIC_IMPORT', name: 'Pesquisa sintetica', active: true,
  created_at: '2026-10-16T12:00:00Z' }
const profile = { user_id: 'c3ludGhldGljLXVzZXI', role: 'importacao',
  expires_at: new Date(Date.now() + 3_600_000).toISOString(), csrf_token: 's'.repeat(43) }
const columns = ['project','participant_id','participant_name','initials','visit','evaluator','assessment_id',
  'assessment_date','started_at','test_code','test_version','block','trial_number','word','ink_color',
  'condition','correct_response','key_pressed','reaction_time','correct','error_type']
const source = [columns.join(','), [
  'SYNTHETIC_SOURCE','P_SYNTHETIC','SYNTHETIC_NAME_DO_NOT_TRANSMIT','SN','V1','E_SYNTHETIC',assessmentId,
  '2026-10-16','2026-10-16T12:00:00Z','stroop_go_nogo_ptbr','0.2.2','main','1','VERDE','green',
  'congruent','space','space','0.512','1','hit',
].join(',')].join('\r\n') + '\r\n'

async function access(page: import('@playwright/test').Page) {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: profile }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [project], next_cursor: null } }))
  await page.route('**/api/v1/projects/*/assessments/options*', route => route.fulfill({ json: {
    participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: ['psychopy'],
    test_code: ['stroop_go_nogo_ptbr'],
  } }))
  await page.route('**/api/v1/projects/*/assessments?*', route => route.fulfill({ json: { items: [], next_cursor: null } }))
}

test('redige a copia no navegador e envia somente para o projeto escolhido', async ({ page }) => {
  await access(page)
  let sent = ''
  let sentUrl = ''
  await page.route('**/api/v1/projects/*/imports/*', async route => {
    if (route.request().method() !== 'POST') return route.fulfill({ status: 404 })
    sent = route.request().postDataBuffer()?.toString('utf8') ?? ''
    sentUrl = route.request().url()
    return route.fulfill({ json: {
      operation_id: operationId, status: 'importado', error_code: null,
      assessment_id: assessmentId, created_at: '2026-10-16T12:00:00Z', updated_at: '2026-10-16T12:00:01Z',
    } })
  })
  await page.goto('/equipe')
  const input = page.getByLabel('Arquivo CSV (até 5 MiB)')
  await input.setInputFiles({ name: 'synthetic.csv', mimeType: 'text/csv', buffer: Buffer.from(source) })
  await page.getByRole('button', { name: 'Minimizar e importar CSV' }).click()
  await expect(page.locator('.csv-import-panel').getByRole('status')).toContainText('Importação concluída')
  expect(sentUrl).toContain(`/projects/${projectId}/imports/`)
  expect(sentUrl).not.toContain('synthetic.csv')
  expect(sent).toContain('NAO_COLETADO,,V1')
  expect(sent).not.toContain('SYNTHETIC_NAME_DO_NOT_TRANSMIT')
  expect(sent).not.toContain(',SN,')
  await expect(input).toHaveValue('')
  await expect(page.getByRole('main')).not.toContainText('SYNTHETIC_NAME_DO_NOT_TRANSMIT')
})

test('timeout preserva a mesma operacao e consulta sem repetir POST automaticamente', async ({ page }) => {
  await access(page)
  let posts = 0
  let postedId = ''
  await page.route('**/api/v1/projects/*/imports/*', async route => {
    const url = new URL(route.request().url())
    postedId = url.pathname.split('/').at(-1) ?? ''
    if (route.request().method() === 'POST') {
      posts += 1
      return route.fulfill({ status: 503, json: { error: { code: 'service_unavailable' } } })
    }
    return route.fulfill({ json: {
      operation_id: postedId, status: 'importado', error_code: null,
      assessment_id: assessmentId, created_at: '2026-10-16T12:00:00Z', updated_at: '2026-10-16T12:00:01Z',
    } })
  })
  await page.goto('/equipe')
  await page.getByLabel('Arquivo CSV (até 5 MiB)').setInputFiles({
    name: 'synthetic.csv', mimeType: 'text/csv', buffer: Buffer.from(source),
  })
  await page.getByRole('button', { name: 'Minimizar e importar CSV' }).click()
  await expect(page.getByRole('alert')).toContainText('O envio não foi confirmado')
  expect(posts).toBe(1)
  await page.getByRole('button', { name: 'Consultar estado' }).click()
  await expect(page.locator('.csv-import-panel').getByRole('status')).toContainText('Importação concluída')
  expect(posts).toBe(1)
  expect(postedId).toMatch(/^[a-f\d-]{36}$/i)
})
