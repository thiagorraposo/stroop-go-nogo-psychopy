import { defineConfig, devices } from '@playwright/test'

const portText = process.env.WEB_TEST_PORT ?? '4173'
if (!/^\d{4,5}$/.test(portText) || Number(portText) < 1024 || Number(portText) > 65535) {
  throw new Error('WEB_TEST_PORT deve ser uma porta local entre 1024 e 65535.')
}
const origin = `http://127.0.0.1:${portText}`

export default defineConfig({
  testDir: './e2e',
  testIgnore: ['**/integrated/**'],
  fullyParallel: true,
  forbidOnly: true,
  retries: 0,
  workers: 2,
  reporter: 'list',
  use: { baseURL: origin, trace: 'retain-on-failure' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: `npm run dev -- --port ${portText} --strictPort`,
    url: origin,
    reuseExistingServer: false,
    timeout: 30_000,
  },
})
