import { expect, test } from '@playwright/test'
import { invitation, redeem, finishPractice } from './fixtures'

test('pagina real bloqueia script inline e conexao fora da origem', async ({ page }) => {
  const response = await page.goto('/')
  expect(response?.headers()['content-security-policy']).toContain("script-src 'self'")
  expect(response?.headers()['x-content-type-options']).toBe('nosniff')
  const blocked = await page.evaluate(async () => {
    const policies: string[] = []
    document.addEventListener('securitypolicyviolation', event => policies.push(event.effectiveDirective))
    const script = document.createElement('script')
    script.textContent = 'window.__synthetic_inline_executed = true'
    document.body.append(script)
    let connection = false
    try { await fetch('https://127.0.0.1:9/synthetic-csp-probe'); connection = true } catch { /* Esperado pelo CSP. */ }
    await new Promise(resolve => setTimeout(resolve, 50))
    return { executed: Object.hasOwn(window, '__synthetic_inline_executed'), connection, policies }
  })
  expect(blocked.executed).toBe(false)
  expect(blocked.connection).toBe(false)
  expect(blocked.policies.some(value => value.startsWith('script-src'))).toBe(true)
  expect(blocked.policies).toContain('connect-src')
  await expect(page.getByRole('heading', { name: 'Tarefa de Correspondência de Cores' })).toBeVisible()
})

test('CSP real preserva estilo dinamico do motor sem permissoes inline', async ({ page }) => {
  const issued = await invitation()
  try {
    await page.addInitScript(() => {
      const violations: string[] = []
      Object.assign(window, { __synthetic_policy_violations: violations })
      document.addEventListener('securitypolicyviolation', event => violations.push(event.effectiveDirective))
    })
    await redeem(page, issued.code)
    await finishPractice(page)
    expect(await page.evaluate(() => (window as unknown as { __synthetic_policy_violations: string[] }).__synthetic_policy_violations)).toEqual([])
    await page.getByRole('button', { name: 'Começar tarefa' }).click()
    await expect(page.locator('[data-phase="stimulus"]')).toBeVisible({ timeout: 8_000 })
    await page.keyboard.press('Escape')
    await expect(page.getByRole('alert')).toContainText('A execução foi interrompida')
    expect(await page.evaluate(() => (window as unknown as { __synthetic_policy_violations: string[] }).__synthetic_policy_violations)).toEqual([])
  } finally { await issued.close() }
})
