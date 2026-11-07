import { defineConfig } from '@playwright/test'
import base from './playwright.w16.config'

// Matriz local DEC-04 aprovada em 2026-11-05. Sem retries de testes.
export default defineConfig({
  ...base,
  testMatch: 'web011.spec.ts',
  outputDir: './test-results/web011/artifacts',
  reporter: [['list'], ['json', { outputFile: './test-results/web011/results.json' }]],
  use: { ...base.use, viewport: { width: 1280, height: 720 } },
  projects: [
    { name: 'chromium-local', use: { browserName: 'chromium' } },
    { name: 'firefox-local', use: { browserName: 'firefox' } },
  ],
})
