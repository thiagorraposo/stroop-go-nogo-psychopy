import { analysisFixture } from '../src/test/analysis-fixture'
/** Doubles sinteticos; nao substituem o aceite HTTPS/PostgreSQL real. */
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
const id = '11111111-1111-4111-8111-111111111111', other = '22222222-2222-4222-8222-222222222222'
const invitation = { invitation_id: '33333333-3333-4333-8333-333333333333', session_id: '44444444-4444-4444-8444-444444444444',
  code: 'SINTETICO_NAO_UTILIZAVEL_123456789', expires_at: '2026-10-18T13:00:00Z', state: 'issued' }
const endpoint = `**/api/v1/projects/${id}/invitations`
const panel = (p: Page) => p.getByRole('region', { name: 'Preparar sessão' })
const code = (p: Page) => p.getByRole('status', { name: 'Código do convite' })
async function access(page: Page, role = 'importacao', active = true) {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ json: { user_id: 'avaliador_sintetico', role,
    expires_at: new Date(Date.now() + 3600000).toISOString(), csrf_token: 's'.repeat(43) } }))
  const project = { id, code: 'PROJETO_SINTETICO', name: 'Pesquisa sintetica', active, created_at: '2026-10-16T12:00:00Z' }
  await page.route('**/api/v1/projects?*', route => route.fulfill({ json: { items: [project,
    { ...project, id: other, code: 'OUTRO_SINTETICO', active: true }], next_cursor: null } }))
  await page.route('**/api/v1/analysis/query', route => route.fulfill({ json: analysisFixture(route.request().postDataJSON(), []) }))
  await page.route('**/api/v1/patients*', route => route.fulfill({ json: { items: [], total: 0, page: 1, page_size: 50 } }))
  await page.route('**/api/v1/evaluators*', route => route.fulfill({ json: { items: [], total: 0, page: 1, page_size: 50 } }))
  await page.goto('/equipe'); await expect(page.getByLabel('Projeto', { exact: true })).toBeVisible()
}
async function fill(page: Page) {
  await page.getByLabel('Código do participante', { exact: true }).fill(' P_SINTETICO ')
  await page.getByLabel('Visita da sessão').fill(' V_2 ')
}
for (const [role, active] of [['consulta', true], ['importacao', false], ['administracao', false]] as const) {
  test(`${role} ativo=${active} sem controles`, async ({ page }) => {
    await access(page, role, active); await expect(panel(page)).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Gerar convite' })).toHaveCount(0)
  })
}
for (const role of ['importacao', 'administracao']) {
  test(`${role} valida, normaliza, cria e revoga`, async ({ page }, testInfo) => {
    let created = 0, revoked = 0
    await page.route(endpoint, route => {
      created++; expect(route.request().postDataJSON()).toEqual({ participant_id: 'P_SINTETICO', visit: 'V_2' })
      expect(route.request().headers()['x-csrf-token']).toBe('s'.repeat(43))
      return route.fulfill({ status: 201, json: invitation })
    })
    await page.route(`${endpoint}/${invitation.invitation_id}/revoke`, route => {
      revoked++; expect(route.request().postDataJSON()).toEqual({}); return route.fulfill({ status: 204 })
    })
    await access(page, role); await page.getByRole('button', { name: 'Gerar convite' }).click()
    await expect(panel(page).getByRole('alert')).toHaveCount(2)
    await page.getByLabel('Código do participante', { exact: true }).fill('codigo invalido')
    await page.getByLabel('Visita da sessão').fill('V_2')
    await page.getByRole('button', { name: 'Gerar convite' }).click()
    await expect(page.getByLabel('Código do participante', { exact: true })).toHaveAttribute('aria-invalid', 'true')
    expect(created).toBe(0); await fill(page); await page.getByLabel('Visita da sessão').press('Enter')
    await expect(code(page)).toHaveText(invitation.code); await expect(panel(page)).toBeFocused()
    await expect(panel(page)).toContainText('Participante: P_SINTETICO · Visita: V_2')
    await expect(panel(page)).toContainText('avaliador_sintetico')
    if (role === 'importacao' && testInfo.project.name === 'chromium') await page.screenshot({ path: '/tmp/stroop-w13a-invite.png', fullPage: true })
    await expect(page.getByRole('link', { name: 'Abrir prática em outra aba' })).toHaveAttribute('href', '/pratica')
    expect(page.url()).not.toContain(invitation.code)
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
    await page.getByRole('button', { name: 'Revogar convite', exact: true }).click()
    await expect(panel(page).getByRole('status')).toContainText('Revogação confirmada')
    await expect(code(page)).toHaveCount(0); expect(created).toBe(1); expect(revoked).toBe(1)
    await page.getByRole('button', { name: 'Preparar outra sessão' }).click()
    await expect(page.getByLabel('Código do participante', { exact: true })).toBeFocused()
  })
}
test('duplo envio em espera faz apenas um POST', async ({ page }) => {
  let calls = 0, release!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  await page.route(endpoint, async route => { calls++; await gate; await route.fulfill({ status: 201, json: invitation }) })
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click()
  await expect(page.getByRole('button', { name: 'Gerando convite…' })).toBeDisabled()
  await panel(page).locator('form').evaluate(form => {
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  })
  release(); await expect(code(page)).toHaveText(invitation.code); expect(calls).toBe(1)
})
test('falha de rede mostra resultado desconhecido sem repetir', async ({ page }) => {
  let calls = 0
  await page.route(endpoint, route => { calls++; return route.abort('failed') })
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click()
  await expect(panel(page).getByRole('alert')).toContainText('A sessão pode ter sido criada')
  await expect(panel(page).getByRole('alert')).toContainText('Sem identificador confirmado')
  await expect(page.getByRole('button', { name: 'Gerar convite', exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Revogar convite', exact: true })).toHaveCount(0); expect(calls).toBe(1)
})
test('troca projeto descarta resposta pendente e limpa codigo confirmado', async ({ page }) => {
  let release!: () => void, started!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  const received = new Promise<void>(resolve => { started = resolve })
  await page.route(endpoint, async route => { started(); await gate; await route.fulfill({ status: 201, json: invitation }).catch(() => undefined) })
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click(); await received
  await page.getByLabel('Projeto', { exact: true }).selectOption(other)
  await expect(page.getByLabel('Código do participante', { exact: true })).toHaveValue('')
  release(); await expect(panel(page)).not.toContainText(invitation.code)
  await page.getByLabel('Projeto', { exact: true }).selectOption(id)
  await page.unroute(endpoint); await page.route(endpoint, route => route.fulfill({ status: 201, json: invitation }))
  await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click(); await expect(code(page)).toHaveText(invitation.code)
  await page.getByLabel('Projeto', { exact: true }).selectOption(other)
  await expect(panel(page)).not.toContainText(invitation.code); await expect(page.getByLabel('Visita da sessão')).toHaveValue('')
})
test('logout apaga codigo confirmado', async ({ page }) => {
  await page.route(endpoint, route => route.fulfill({ status: 201, json: invitation }))
  await page.route('**/api/v1/auth/logout', route => route.fulfill({ status: 204 }))
  await access(page); await fill(page); await page.getByRole('button', { name: 'Gerar convite' }).click()
  await expect(code(page)).toHaveText(invitation.code)
  await page.getByRole('button', { name: 'Encerrar sessão', exact: true }).click()
  await expect(panel(page)).toHaveCount(0); await expect(page.locator('body')).not.toContainText(invitation.code)
})
test('PREP-01: seleciona paciente e avaliador, revisa resumo para conferencia e emite convite cadastral', async ({ page }) => {
  const patient = { id: '55555555-5555-4555-8555-555555555555', participant_code: 'PAT-0001',
    full_name: 'Paciente Sintetico Prep', normalized_name: 'PACIENTE SINTETICO PREP', initials: 'PSP',
    disambiguation_note: 'Coorte 1', active: true, created_at: '2026-11-07T10:00:00Z',
    updated_at: '2026-11-07T10:00:00Z', project_count: 1, assessment_count: 0, last_assessment_at: null }
  const evaluator = { id: '66666666-6666-4666-8666-666666666666', evaluator_code: 'EVA-0001',
    full_name: 'Avaliadora Sintetica Prep', normalized_name: 'AVALIADORA SINTETICA PREP', initials: 'ASP',
    active: true, created_at: '2026-11-07T10:00:00Z', updated_at: '2026-11-07T10:00:00Z',
    assessment_count: 0, last_assessment_at: null }
  const summary = { project_id: id, project_code: 'PROJETO_SINTETICO', project_name: 'Pesquisa sintetica',
    patient_id: patient.id, participant_code: 'PAT-0001', participant_name: patient.full_name,
    initials: 'PSP', evaluator_id: evaluator.id, evaluator_code: 'EVA-0001', evaluator_name: evaluator.full_name,
    test_code: 'stroop_go_nogo_ptbr', test_version: '0.2.2-web.1', protocol_id: 'stroop_go_nogo_ptbr/0.2.2-web.1',
    visit: 'T1' }
  await access(page)
  await page.unroute('**/api/v1/patients*')
  await page.unroute('**/api/v1/evaluators*')
  await page.route('**/api/v1/patients*', route => route.fulfill({ json: { items: [patient], total: 1, page: 1, page_size: 50 } }))
  await page.route('**/api/v1/evaluators*', route => route.fulfill({ json: { items: [evaluator], total: 1, page: 1, page_size: 50 } }))
  await page.route(endpoint, route => {
    expect(route.request().postDataJSON()).toEqual({
      patient_id: patient.id, evaluator_id: evaluator.id, visit: 'T1',
      test_code: 'stroop_go_nogo_ptbr', initials: 'PSP',
    })
    return route.fulfill({ status: 201, json: { ...invitation, summary } })
  })
  await page.getByLabel('Buscar paciente cadastrado', { exact: true }).fill('Paciente')
  await page.getByLabel('Paciente cadastrado', { exact: true }).selectOption(patient.id)
  await expect(page.getByLabel('Código do participante', { exact: true })).toHaveValue('PAT-0001')
  await expect(page.getByLabel('Iniciais na sessão')).toHaveValue('PSP')
  await page.getByLabel('Buscar avaliador responsável', { exact: true }).fill('Avaliadora')
  await page.getByLabel('Avaliador responsável', { exact: true }).selectOption(evaluator.id)
  await page.getByLabel('Visita da sessão').fill('T1')
  await page.getByRole('button', { name: 'Revisar preparação', exact: true }).click()
  const review = page.getByRole('region', { name: 'Resumo para conferência' })
  await expect(review).toContainText('Paciente Sintetico Prep (PAT-0001)')
  await expect(review).toContainText('Avaliadora Sintetica Prep (EVA-0001)')
  await expect(review).toContainText('stroop_go_nogo_ptbr · 0.2.2-web.1')
  await review.getByRole('button', { name: 'Confirmar e emitir convite', exact: true }).click()
  await expect(code(page)).toHaveText(invitation.code)
  await expect(panel(page)).toContainText('Participante: PAT-0001 · Visita: T1')
  await expect(panel(page)).toContainText('Paciente: Paciente Sintetico Prep (PAT-0001)')
  await expect(panel(page)).toContainText('Avaliador: Avaliadora Sintetica Prep (EVA-0001)')
})
