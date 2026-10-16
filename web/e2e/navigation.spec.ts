import { expect, test } from '@playwright/test'

const profile = {
  user_id: 'c3ludGhldGljLXVzZXI', role: 'consulta',
  expires_at: '2026-10-16T18:02:01.123456Z', csrf_token: 's'.repeat(43),
}

test('navega pelas orientacoes e respeita o historico e o foco', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Tarefa de Correspondência de Cores' })).toBeVisible()
  await page.getByRole('link', { name: 'Entender a tarefa' }).click()
  await expect(page).toHaveURL('/instrucoes')
  await expect(page.getByRole('main')).toBeFocused()
  await expect(page.getByRole('heading', { name: 'Observe a palavra e a cor das letras.' })).toBeVisible()
  await expect(page.getByLabel('Exemplos da regra')).toContainText('Palavra e cor iguais')
  await expect(page.getByLabel('Exemplos da regra')).toContainText('Palavra e cor diferentes')
  await page.goBack()
  await expect(page).toHaveURL('/')
  await expect(page.getByRole('heading', { name: 'Tarefa de Correspondência de Cores' })).toBeVisible()
  await page.goForward()
  await expect(page).toHaveURL('/instrucoes')
  await page.getByRole('link', { name: 'Voltar ao início' }).click()
  await expect(page).toHaveURL('/')
})

test('mostra carregamento e direciona o acesso profissional ao Google', async ({ page }) => {
  let release!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  await page.route('**/api/v1/auth/me', async route => {
    await gate
    await route.fulfill({ status: 401, json: { error: { code: 'authentication_required' } } })
  })
  await page.goto('/equipe')
  await expect(page.getByRole('status')).toHaveText('Verificando seu acesso…')
  release()
  const login = page.getByRole('link', { name: 'Entrar com Google' })
  await expect(login).toBeVisible()
  await expect(login).toHaveAttribute('href', '/api/v1/auth/login')
  await expect(page.getByRole('heading', { name: 'Área da equipe' })).toBeVisible()
})

test('recupera erro seguro, revalida perfil e encerra com CSRF em RAM', async ({ page }) => {
  let available = false
  await page.route('**/api/v1/auth/me', route => route.fulfill(available
    ? { status: 200, json: profile }
    : { status: 503, json: { error: { code: 'service_unavailable', message: 'SYNTHETIC_SECRET' } } }))
  await page.route('**/api/v1/auth/logout', async route => {
    expect(route.request().method()).toBe('POST')
    expect(route.request().headers()['origin']).toBe(new URL(page.url()).origin)
    expect(route.request().headers()['x-csrf-token']).toBe(profile.csrf_token)
    expect(route.request().postData()).toBe('{}')
    await route.fulfill({ status: 204 })
  })
  await page.goto('/equipe')
  await expect(page.getByRole('alert')).toContainText('temporariamente indisponível')
  await expect(page.getByRole('main')).not.toContainText('SYNTHETIC_SECRET')
  available = true
  await page.getByRole('button', { name: 'Tentar novamente' }).click()
  await expect(page.getByText('Sua sessão está ativa.')).toBeVisible()
  await expect(page.getByText('Consulta', { exact: true })).toBeVisible()
  await expect(page.getByRole('main')).not.toContainText(profile.csrf_token)
  await expect(page.getByRole('main')).not.toContainText(profile.user_id)
  await page.getByRole('button', { name: 'Encerrar sessão' }).click()
  await expect(page.getByRole('link', { name: 'Entrar com Google' })).toBeVisible()
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })))
    .toEqual({ local: 0, session: 0 })
})

test('acesso bloqueado e resposta inesperada nao expoem dados do servidor', async ({ page }) => {
  await page.route('**/api/v1/auth/me', route => route.fulfill({ status: 403,
    json: { error: { code: 'account_blocked', message: '<script>SYNTHETIC_SECRET</script>' } } }))
  await page.goto('/equipe')
  await expect(page.getByRole('alert')).toContainText('bloqueada')
  await expect(page.getByRole('main')).not.toContainText('SYNTHETIC_SECRET')
  await page.route('**/api/v1/auth/me', route => route.fulfill({ status: 200, json: { unexpected: 'SYNTHETIC_SECRET' } }))
  await page.getByRole('button', { name: 'Tentar novamente' }).click()
  await expect(page.getByRole('alert')).toContainText('resposta inválida')
})

test('rotas desconhecidas possuem retorno acessivel ao inicio', async ({ page }) => {
  await page.goto('/rota-sintetica-inexistente')
  await expect(page.getByRole('heading', { name: 'Vamos voltar ao início?' })).toBeVisible()
  await page.getByRole('link', { name: 'Ir para o início', exact: true }).click()
  await expect(page).toHaveURL('/')
  await page.getByRole('link', { name: 'Área da equipe' }).focus()
  await expect(page.getByRole('link', { name: 'Área da equipe' })).toBeFocused()
})
