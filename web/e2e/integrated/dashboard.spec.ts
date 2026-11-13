/** HTTPS + API + SELECT PostgreSQL reais; perfis/dados exclusivamente sinteticos. */
import { execFileSync } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'
const python = fileURLToPath(new URL('../../../.venv/bin/python', import.meta.url))
const script = fileURLToPath(new URL('./dashboard-manage.py', import.meta.url))
type Prepared = { cookie_name: string; token: string; project_id: string; subject: string; assessment_id: string }
function manage(value: Record<string, unknown>): Prepared {
  return JSON.parse(execFileSync(python, [script], { input: JSON.stringify(value), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }))
}
for (const [role, label] of [['consulta', 'Consulta'], ['importacao', 'Coleta e importação'], ['administracao', 'Administração']]) {
  test(`painel HTTPS real por perfil ${role}: paridade, detalhe, exportacao e revogacao`, async ({ page, context }) => {
    const prepared = manage({ role })
    await context.addCookies([{ name: prepared.cookie_name, value: prepared.token, domain: '127.0.0.1', path: '/',
      secure: true, httpOnly: true, sameSite: 'Lax' }])
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.name))
    await page.goto('/equipe')
    await expect(page.locator('.role-badge')).toHaveText(label!)
    await page.getByRole('listbox', { name: 'Projetos da consulta', exact: true }).selectOption(prepared.project_id)
    await page.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
    await expect(page.locator('.dashboard-cards').getByText('1', { exact: true })).toHaveCount(2)
    await expect(page.locator('.dashboard-cards')).toContainText('56,2%')
    await expect(page.locator('.dashboard-cards')).toContainText('0,512 s')
    const table = page.getByRole('table', { name: 'Avaliações filtradas' })
    await expect(table).toContainText('P_SINTETICO_W15')
    await expect(table).toContainText('PsychoPy local')
    await page.getByRole('button', { name: 'Ver avaliação P_SINTETICO_W15, visita V_SINTETICA' }).focus()
    await page.keyboard.press('Enter')
    const panel = page.getByRole('region', { name: 'Detalhe da avaliação' })
    await expect(panel).toBeFocused()
    await expect(panel.getByRole('table', { name: 'Tentativas registradas' }).locator('tbody tr')).toHaveCount(16)
    const downloaded = page.waitForEvent('download')
    await panel.getByRole('button', { name: 'Exportar CSV oficial' }).click()
    const download = await downloaded
    expect(download.suggestedFilename()).toMatch(/^stroop_go_nogo_ptbr_\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m\d{2}s_trials.csv$/)
    const path = await download.path()
    expect(path).not.toBeNull()
    const content = await readFile(path!, 'utf8')
    expect(content.trim().split(/\r?\n/)).toHaveLength(17)
    expect(content).toContain('NAO_COLETADO')
    expect(content).not.toContain('NOME_SINTETICO_RESTRITO')
    await expect(panel.getByRole('status')).toHaveText('Arquivo preparado para download.')
    await expect(page.getByRole('main')).not.toContainText('NOME_SINTETICO_RESTRITO')
    expect((await page.getByRole('main').innerText()).includes(prepared.token)).toBe(false)
    expect(await page.evaluate(() => [document.cookie, localStorage.length, sessionStorage.length])).toEqual(['', 0, 0])
    manage({ action: 'revoke', project_id: prepared.project_id, subject: prepared.subject })
    await panel.getByRole('button', { name: 'Exportar CSV oficial' }).click()
    await expect(panel.getByRole('status')).toHaveText('O recurso solicitado não está disponível.')
    await page.reload()
    if (role === 'administracao') {
      await page.getByRole('listbox', { name: 'Projetos da consulta', exact: true }).selectOption(prepared.project_id)
      await page.getByRole('button', { name: 'Aplicar filtros', exact: true }).click()
      await expect(page.locator('.professional-dashboard > p[role=alert]')).toHaveText('O recurso solicitado não está disponível.')
    } else await expect(page.getByRole('status')).toHaveText('Nenhum projeto disponível para sua conta.')
    await expect(page.getByRole('table')).toHaveCount(0)
    expect(errors).toEqual([])
  })
}
