import { defineConfig, devices } from '@playwright/test'

/**
 * E2E + responsive against a running stack (docker-compose). The frontend
 * serves the SPA and proxies /api to the backend on the same origin, so
 * WebAuthn works on the localhost secure context with a virtual authenticator.
 *
 * Two project groups:
 *   - `chromium` runs the full functional suite on Desktop Chrome.
 *   - `responsive-*` runs only `responsive.spec.ts` on a matrix of viewports
 *     that cluster the popular Android (Galaxy A / Pixel / Fairphone),
 *     iPhone, iPad, laptop and desktop sizes — one project per *CSS viewport*,
 *     since identical viewport ≡ identical layout.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:8080',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      testIgnore: /responsive\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
    },

    // Responsive matrix — one project per CSS-viewport cluster.
    // Real device names listed for clarity; identical viewport ≡ identical layout.
    {
      name: 'responsive-android-360x640',
      testMatch: /responsive\.spec\.ts/,
      use: {
        ...devices['Galaxy S5'],
        viewport: { width: 360, height: 640 },
      },
    },
    {
      name: 'responsive-android-360x800', // Galaxy A13/A14/A24
      testMatch: /responsive\.spec\.ts/,
      use: {
        ...devices['Galaxy S9+'],
        viewport: { width: 360, height: 800 },
        userAgent:
          'Mozilla/5.0 (Linux; Android 13; SM-A146P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
      },
    },
    {
      name: 'responsive-iphone-se',
      testMatch: /responsive\.spec\.ts/,
      use: { ...devices['iPhone SE'] }, // 375×667
    },
    {
      name: 'responsive-iphone-14',
      testMatch: /responsive\.spec\.ts/,
      use: { ...devices['iPhone 14'] }, // 390×844
    },
    {
      name: 'responsive-android-411x891', // Galaxy A54/A55, Pixel 7, Fairphone 4/5
      testMatch: /responsive\.spec\.ts/,
      use: {
        ...devices['Pixel 7'],
        viewport: { width: 411, height: 891 },
        userAgent:
          'Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
      },
    },
    {
      name: 'responsive-ipad-portrait',
      testMatch: /responsive\.spec\.ts/,
      use: {
        ...devices['iPad (gen 7)'],
        viewport: { width: 768, height: 1024 },
      },
    },
    {
      name: 'responsive-ipad-landscape',
      testMatch: /responsive\.spec\.ts/,
      use: {
        ...devices['iPad (gen 7) landscape'],
        viewport: { width: 1024, height: 768 },
      },
    },
    {
      name: 'responsive-laptop-1280',
      testMatch: /responsive\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
    {
      name: 'responsive-desktop-1920',
      testMatch: /responsive\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport: { width: 1920, height: 1080 } },
    },
  ],
})
