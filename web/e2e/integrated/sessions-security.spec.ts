import { expect, request, test } from '@playwright/test'
import { invitation, manage, redeem } from './fixtures'

test('HTTPS separa credenciais e CSRF; logout revoga replay sem encerrar participante', async ({ page, context }) => {
  // Sessao local injetada pelo operador de fixtures; login real tem suite propria.
  const professional = manage('professional') as unknown as {
    cookie_name: string; token: string; csrf: string
  }
  await context.addCookies([{ name: professional.cookie_name, value: professional.token,
    domain: '127.0.0.1', path: '/', secure: true, httpOnly: true, sameSite: 'Lax' }])
  const issued = await invitation()
  const origin = 'https://127.0.0.1:4373'
  try {
    await redeem(page, issued.code)
    const bootstrap = await (await page.request.get('/api/v1/participant/session')).json()
    const cookies = await context.cookies()
    const participant = cookies.find(cookie => cookie.name === '__Host-stroop_participant')!
    expect(participant).toMatchObject({ secure: true, httpOnly: true, sameSite: 'Lax', path: '/' })
    expect(await page.evaluate(() => [document.cookie, localStorage.length, sessionStorage.length])).toEqual(['', 0, 0])

    for (const headers of <Record<string, string>[]>[
      {}, { Origin: origin }, { Origin: 'https://attacker.invalid', 'X-CSRF-Token': bootstrap.csrf_token },
      { Origin: origin, 'X-CSRF-Token': professional.csrf },
    ]) {
      expect((await page.request.post('/api/v1/participant/start', {
        data: { app_version: 'synthetic-session-security' }, headers,
      })).status()).toBe(403)
    }
    for (const headers of <Record<string, string>[]>[
      {}, { Origin: origin }, { Origin: 'https://attacker.invalid', 'X-CSRF-Token': professional.csrf },
      { Origin: origin, 'X-CSRF-Token': bootstrap.csrf_token },
    ]) {
      expect((await page.request.post('/api/v1/auth/logout', { data: {}, headers })).status()).toBe(403)
    }

    const replay = await request.newContext({ baseURL: origin, ignoreHTTPSErrors: true })
    try {
      // O nome de cookie faz parte da credencial: tokens trocados nao autenticam.
      expect((await replay.get('/api/v1/auth/me', {
        headers: { Cookie: `${professional.cookie_name}=${participant.value}` },
      })).status()).toBe(401)
      expect((await replay.get('/api/v1/participant/session', {
        headers: { Cookie: `${participant.name}=${professional.token}` },
      })).status()).toBe(401)
      expect((await page.request.post('/api/v1/auth/logout', {
        data: {}, headers: { Origin: origin, 'X-CSRF-Token': professional.csrf },
      })).status()).toBe(204)
      expect((await context.cookies()).some(cookie => cookie.name === professional.cookie_name)).toBe(false)
      expect((await replay.get('/api/v1/auth/me', {
        headers: { Cookie: `${professional.cookie_name}=${professional.token}` },
      })).status()).toBe(401)
      expect((await page.request.get('/api/v1/participant/session')).status()).toBe(200)
      expect((await page.request.post('/api/v1/participant/logout', {
        data: {}, headers: { Origin: origin, 'X-CSRF-Token': bootstrap.csrf_token },
      })).status()).toBe(204)
      expect((await context.cookies()).some(cookie => cookie.name === participant.name)).toBe(false)
      expect((await replay.get('/api/v1/participant/session', {
        headers: { Cookie: `${participant.name}=${participant.value}` },
      })).status()).toBe(401)
      expect(manage('state', { session_id: issued.session_id }).assessments).toBe(0)
    } finally { await replay.dispose() }
  } finally { await issued.close() }
})
