import { expect, test } from '@playwright/test'

const profile = {
  user_id: 'c3ludGhldGljLXVzZXI', role: 'consulta',
  expires_at: new Date(Date.now() + 1_800_000).toISOString(), csrf_token: 's'.repeat(43),
}

test('navega pelas orientacoes e respeita o historico e o foco', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Tarefa de Correspondência de Cores' })).toBeVisible()
  await expect(page.getByLabel('Exemplos da regra')).toContainText('Iguais')
  await page.getByRole('link', { name: 'Iniciar tutorial' }).click()
  await expect(page).toHaveURL('/instrucoes')
  await expect(page.getByRole('main')).toBeFocused()
  await expect(page.getByRole('heading', { name: 'Observe a palavra e compare a cor das letras.' })).toBeVisible()
  await expect(page.getByLabel('Exemplos da regra')).toContainText('Palavra e cor iguais')
  await expect(page.getByLabel('Exemplos da regra')).toContainText('Palavra e cor diferentes')
  await expect(page.getByRole('list', { name: 'Como responder' }).getByRole('listitem')).toHaveCount(3)
  await page.goBack()
  await expect(page).toHaveURL('/')
  await expect(page.getByRole('heading', { name: 'Tarefa de Correspondência de Cores' })).toBeVisible()
  await page.goForward()
  await expect(page).toHaveURL('/instrucoes')
  await page.getByRole('link', { name: 'Voltar ao início' }).click()
  await expect(page).toHaveURL('/')
})

test('percurso preparatorio e exemplos permanecem legiveis sem rolagem horizontal', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.route('**/api/v1/participant/session', route => route.fulfill({ status: 401,
    json: { error: { code: 'authentication_required' }, request_id: 'synthetic-journey' } }))
  await page.goto('/')
  await expect(page.getByLabel('Exemplos da regra')).toBeVisible()
  await expect(page.getByRole('list', { name: 'Etapas da participação' }).locator('[aria-current="step"]')).toContainText('Orientações')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.getByRole('link', { name: 'Iniciar tutorial' }).click()
  await expect(page.getByRole('list', { name: 'Como responder' }).getByRole('listitem')).toHaveCount(3)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.getByRole('link', { name: 'Ir para a prática' }).click()
  await expect(page.getByRole('list', { name: 'Etapas da participação' }).locator('[aria-current="step"]')).toContainText('Convite')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.setViewportSize({ width: 1280, height: 800 })
  await page.evaluate(() => { document.documentElement.style.zoom = '2' })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
})

test('mostra carregamento e formulario profissional local', async ({ page }) => {
  let release!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  await page.route('**/api/v1/auth/me', async route => {
    await gate
    await route.fulfill({ status: 401, json: { error: { code: 'authentication_required' } } })
  })
  await page.goto('/equipe')
  await expect(page.getByRole('status')).toHaveText('Verificando seu acesso…')
  release()
  await expect(page.getByLabel('Usuário', { exact: true })).toBeVisible()
  await expect(page.getByLabel('Senha', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Entrar', exact: true })).toBeVisible()
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
  await expect(page.getByRole('button', { name: 'Entrar', exact: true })).toBeVisible()
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

test('perda de foco cancela avancar por tecla iniciada antes da interrupcao', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('main').focus()
  await page.keyboard.down('Space')
  await page.evaluate(() => window.dispatchEvent(new Event('blur')))
  await page.keyboard.up('Space')
  await expect(page).toHaveURL('/')
  await page.keyboard.press('Space')
  await expect(page).toHaveURL('/instrucoes')
})

test('expiracao profissional limpa painel e exige novo login sem persistir dados', async ({ page }) => {
  await page.clock.install()
  let expired = false
  await page.route('**/api/v1/auth/me', route => route.fulfill(!expired
    ? { status: 200, json: profile }
    : { status: 401, json: { error: { code: 'authentication_required' } } }))
  await page.route('**/api/v1/projects?*', route => route.fulfill({ status: 200, json: { items: [], next_cursor: null } }))
  await page.goto('/equipe')
  await expect(page.getByRole('heading', { name: 'Resultados da pesquisa' })).toBeVisible()
  expired = true
  await page.clock.fastForward(1_800_001)
  await expect(page.getByRole('button', { name: 'Entrar', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Resultados da pesquisa' })).toHaveCount(0)
  expect(await page.evaluate(() => localStorage.length + sessionStorage.length)).toBe(0)
})
