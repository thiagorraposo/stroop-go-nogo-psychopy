import { defineConfig, devices } from '@playwright/test'
export default defineConfig({
  testDir: './e2e/local-auth', fullyParallel: false, forbidOnly: true, retries: 0, workers: 1,
  timeout: 110_000, reporter: 'list', outputDir: './test-results/local-auth',
  use: { baseURL: 'https://127.0.0.1:4473', ignoreHTTPSErrors: true, trace: 'off', video: 'off' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: { command: '../.venv/bin/python e2e/local-auth/server.py',
    url: 'https://127.0.0.1:4473/health/live', ignoreHTTPSErrors: true,
    reuseExistingServer: false, timeout: 30_000,
    gracefulShutdown: { signal: 'SIGTERM', timeout: 10_000 } },
})
