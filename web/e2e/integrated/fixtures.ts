/** Preparacao por processos locais e HTTP real; nunca intercepta respostas API. */
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { randomUUID } from 'node:crypto'
import { expect, request } from '@playwright/test'
import type { APIRequestContext, Page } from '@playwright/test'

const origin = 'https://127.0.0.1:4373'
const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const management = fileURLToPath(new URL('./manage.py', import.meta.url))
export type StoredState = { state: string; reason: string | null; assessment_id: string | null;
  assessments: number; trials: number; metrics: number; receipt: { summary: Record<string, number | null> } | null }
export function manage(action: string, input: Record<string, unknown> = {}): StoredState {
  const output = execFileSync(python, [management, action], { input: JSON.stringify(input), encoding: 'utf8',
    stdio: ['pipe', 'pipe', 'pipe'] })
  return JSON.parse(output)
}
export type Invitation = { code: string; session_id: string; invitation_id: string; project_id: string;
  professional: APIRequestContext; close(): Promise<void> }
export async function invitation(): Promise<Invitation> {
  const credentials = JSON.parse(execFileSync(python, [management, 'professional'], {
    input: '{}', encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'],
  }))
  const professional = await request.newContext({ baseURL: origin, ignoreHTTPSErrors: true,
    extraHTTPHeaders: { Cookie: `${credentials.cookie_name}=${credentials.token}`, Origin: origin,
      'X-CSRF-Token': credentials.csrf } })
  try {
    const project = await professional.post('/api/v1/projects', { data: {
      code: `SYNTHETIC_${randomUUID().replaceAll('-', '')}`, name: 'Projeto sintetico integrado' } })
    expect(project.status()).toBe(201)
    const projectId = (await project.json()).id
    const member = await professional.put(`/api/v1/projects/${projectId}/members/${credentials.user_id}`, { data: { active: true } })
    expect(member.status()).toBe(200)
    const issued = await professional.post(`/api/v1/projects/${projectId}/invitations`, {
      data: { participant_id: 'P_SINTETICO_INTEGRADO', visit: 'V_SINTETICA' } })
    expect(issued.status()).toBe(201)
    const value = await issued.json()
    return { ...value, project_id: projectId, professional, close: () => professional.dispose() }
  } catch {
    await professional.dispose()
    throw new Error('Nao foi possivel preparar convite sintetico pela API real.')
  }
}
export async function redeem(page: Page, code: string) {
  await page.goto('/pratica')
  await expect(page.getByRole('heading', { name: 'Informe o convite da equipe.' })).toBeVisible()
  await page.getByLabel('Código do convite').fill(code)
  await page.getByRole('button', { name: 'Validar convite' }).click()
  await expect(page.getByRole('heading', { name: 'Primeiro, vamos praticar.' })).toBeVisible()
}
export async function finishPractice(page: Page) {
  await page.getByLabel('Estou usando um computador ou notebook com teclado físico.').check()
  await page.getByRole('main').focus()
  await page.keyboard.press('Space')
  await page.getByRole('button', { name: 'Começar prática', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Prática concluída.' })).toBeVisible({ timeout: 22_000 })
}
