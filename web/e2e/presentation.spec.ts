import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'

// Fixture exclusivamente sintética: motor real, relógio controlado, sem HTTP/PG.
async function mount(page: Page, block: 'main' | 'practice') {
  await page.goto('/')
  await expect(page.getByRole('main')).toBeFocused()
  await page.evaluate(async block => {
    const mainPath = '/src/experiment/main-engine.ts'
    const practicePath = '/src/experiment/practice-engine.ts'
    const protocolPath = '/src/experiment/protocol.ts'
    const main = await import(/* @vite-ignore */ mainPath) as typeof import('../src/experiment/main-engine')
    const practice = await import(/* @vite-ignore */ practicePath) as typeof import('../src/experiment/practice-engine')
    const { MAIN_CONDITIONS, PRACTICE_CONDITIONS } = await import(/* @vite-ignore */ protocolPath) as typeof import('../src/experiment/protocol')
    const host = document.createElement('div')
    Object.assign(host.style, { position: 'fixed', inset: '0', zIndex: '9999' })
    document.body.replaceChildren(host)
    let time = 0
    let pending: FrameRequestCallback | undefined
    const clock = { now: () => time,
      requestFrame: (callback: FrameRequestCallback) => { pending = callback; return 1 },
      cancelFrame: () => { pending = undefined } }
    const onInterrupted = (reason: string) => {
      if (reason !== 'page_closed') throw new Error(`Fixture visual interrompida: ${reason}`)
    }
    const onComplete = () => undefined
    const cleanup = block === 'main'
      ? main.createMainRuntime(host, { order: MAIN_CONDITIONS, onInterrupted, onComplete }, clock)
      : practice.createPracticeRuntime(host, PRACTICE_CONDITIONS, { onInterrupted, onComplete }, clock)
    ;(window as unknown as { presentationCleanup(): void }).presentationCleanup = cleanup
    ;(window as unknown as { presentationStep(ms: number): void }).presentationStep = (ms: number) => {
      const end = time + ms
      while (time < end) {
        time = Math.min(end, time + 10)
        const callback = pending
        pending = undefined
        callback?.(time)
      }
    }
  }, block)
}
async function step(page: Page, ms: number) {
  await page.evaluate(ms => (window as unknown as { presentationStep(ms: number): void }).presentationStep(ms), ms)
}
async function noAccuracy(page: Page, block: 'main' | 'practice') {
  const surface = page.locator(`.${block}-runtime`)
  await expect(surface.locator('[data-hud="accuracy"], [data-hud="accuracy-bar"], meter')).toHaveCount(0)
  expect(await surface.textContent()).not.toMatch(/Precisão|accuracy|%|ranking|taxa de erros/i)
  expect(await surface.ariaSnapshot()).not.toMatch(/Precisão|accuracy|%|ranking|taxa de erros/i)
}

test.afterEach(async ({ page }) => {
  if (!page.isClosed()) await page.evaluate(() =>
    (window as unknown as { presentationCleanup?: () => void }).presentationCleanup?.())
})

for (const size of [{ width: 1280, height: 720 }, { width: 1920, height: 1080 }]) {
  test.describe(`${size.width}x${size.height}`, () => {
  test.use({ viewport: size })
  test('dez cores sem caixa, contorno uniforme e centro estável', async ({ page }, testInfo) => {
    await mount(page, 'main')
    await step(page, 3050) // contagem e primeira fixação, sem alterar tempos do motor
    const colors = new Set<string>()
    const outlineWidths = new Set<string>()
    const timerWidths = new Set<number>()
    for (let index = 0; index < 16; index++) {
      const word = page.locator('.main-stimulus-card')
      await expect(page.locator('[data-phase="stimulus"]')).toHaveAttribute('data-trial-number', String(index + 1))
      const style = await word.evaluate(element => {
        const css = getComputedStyle(element)
        const box = element.getBoundingClientRect()
        return { color: css.color, background: css.backgroundColor, outline: css.getPropertyValue('-webkit-text-stroke-color'),
          width: css.getPropertyValue('-webkit-text-stroke-width'), paint: css.getPropertyValue('paint-order'),
          shadow: css.textShadow, font: css.fontFamily, weight: css.fontWeight,
          x: box.x + box.width / 2, y: box.y + box.height / 2,
          supports: CSS.supports('-webkit-text-stroke', '1px white') && CSS.supports('paint-order', 'stroke fill') }
      })
      expect(style.supports).toBe(true)
      expect(style.background).toBe('rgba(0, 0, 0, 0)')
      expect(style.outline).toBe('rgb(255, 255, 255)')
      expect(parseFloat(style.width)).toBeGreaterThan(0)
      expect(parseFloat(style.width)).toBeLessThan(3)
      expect(style.paint).toContain('stroke')
      expect(style.shadow).toBe('none')
      expect(style.font).toContain('system-ui')
      expect(style.weight).toBe('700')
      expect(style.x).toBeCloseTo(size.width / 2, 0)
      expect(style.y).toBeCloseTo(size.height / 2, 0)
      outlineWidths.add(style.width)
      const timer = await page.locator('[data-hud="time"]').evaluate(element => ({
        width: element.getBoundingClientRect().width, numeric: getComputedStyle(element).fontVariantNumeric,
      }))
      expect(timer.numeric).toBe('tabular-nums')
      timerWidths.add(timer.width)
      expect(await page.locator('.experiment-progress-track > span').evaluate(element => ({
        animation: getComputedStyle(element).animationName, transition: getComputedStyle(element).transitionDuration,
      }))).toEqual({ animation: 'none', transition: '0s' })
      await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow', String(index))
      await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuemax', '16')
      await noAccuracy(page, 'main')
      if (!colors.has(style.color)) {
        colors.add(style.color)
        // Screenshots sintéticos no diretório ignorado do Playwright, sem coletas.
        await page.screenshot({ path: testInfo.outputPath(`color-${colors.size}.png`) })
      }
      if (index < 15) await step(page, 3750)
    }
    expect(colors.size).toBe(10)
    expect(outlineWidths.size).toBe(1)
    expect(timerWidths.size).toBe(1)
    console.log(`Visual sintético: ${testInfo.project.name} ${page.context().browser()?.version()} ${size.width}x${size.height}`)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth
      && document.documentElement.scrollHeight <= innerHeight)).toBe(true)
    await testInfo.attach('browser', { body: `${testInfo.project.name} ${page.context().browser()?.version()}`, contentType: 'text/plain' })
  })
  })
}

test('prática sem precisão, com progresso concluído e feedback individual preservado', async ({ page }) => {
  await mount(page, 'practice')
  await noAccuracy(page, 'practice')
  await step(page, 4550)
  await expect(page.locator('[data-phase="stimulus"]')).toBeVisible()
  await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')
  await expect(page.locator('[data-hud="time"]')).toHaveCount(0)
  await noAccuracy(page, 'practice')
  await step(page, 2500)
  await expect(page.locator('[data-phase="feedback"]')).toBeVisible()
  await expect(page.getByText('Pressione ESPAÇO quando a cor combina', { exact: true })).toBeVisible()
  await noAccuracy(page, 'practice')
  await step(page, 500)
  await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '1')
})
