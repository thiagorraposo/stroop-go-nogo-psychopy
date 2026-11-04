import { defineConfig } from '@playwright/test'

// Campanha local explicita: navegador visivel, teclado sintetico e API double.
// Nao integra a suite padrao nem representa medicao fisica de latencia.
export default defineConfig({
  testDir: './pilots',
  fullyParallel: false,
  forbidOnly: true,
  retries: 0,
  workers: 1,
  timeout: 110_000,
  outputDir: './test-results/w16/artifacts',
  reporter: [['list'], ['json', { outputFile: './test-results/w16/results.json' }]],
  use: {
    baseURL: 'http://127.0.0.1:4186',
    headless: false,
    viewport: { width: 1440, height: 900 },
    trace: 'off',
    screenshot: 'off',
    video: 'off',
  },
  projects: [
    { name: 'chrome-local', use: { browserName: 'chromium', channel: 'chrome' } },
    { name: 'firefox-playwright', use: { browserName: 'firefox' } },
  ],
  webServer: {
    command: 'npm run dev -- --port 4186 --strictPort',
    env: { VITE_W16_TIMING_CAPTURE: 'synthetic-only' },
    url: 'http://127.0.0.1:4186',
    reuseExistingServer: false,
    timeout: 30_000,
  },
})
