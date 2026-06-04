import { test, expect, type Page } from '@playwright/test'
import { enableVirtualAuthenticator, uniqueUser, registerPasskey } from './helpers'

/**
 * Responsive regression suite. Runs the same set of routes across every
 * viewport defined in `playwright.config.ts` under `responsive-*` projects.
 *
 * For each route we assert:
 *   - the page actually loaded (the Layout's nav rendered → not 404 / spinner)
 *   - there is NO unintended horizontal scroll (the #1 mobile regression)
 *   - on viewports ≥ 1024 the sidebar is visible; on < 1024 it must be
 *     collapsed/hidden behind a toggle (hamburger)
 *
 * Pixel-diff screenshots are NOT asserted (we don't lock in the current
 * possibly-broken layout as truth). Instead, every page+viewport pair
 * uploads a full-page PNG as a CI artifact for visual review in PRs.
 */

const ROUTES = [
  '/',
  '/accounts',
  '/transactions',
  '/shared-accounts',
  '/bank-import',
  '/reconciliation',
  '/recurring',
  '/settings',
]

async function hasHorizontalScroll(page: Page): Promise<boolean> {
  return await page.evaluate(() => {
    const html = document.documentElement
    const body = document.body
    return (
      html.scrollWidth > html.clientWidth + 1 ||
      body.scrollWidth > body.clientWidth + 1
    )
  })
}

/**
 * Wait for the protected Layout to be rendered. The Layout always exposes a
 * top-level <main> region — when we see it, the route resolved (no 404 /
 * auth-redirect / loading spinner).
 */
async function waitForRoute(page: Page) {
  // <main> from the Layout component — always present on every protected page.
  await page.waitForSelector('main', { state: 'attached', timeout: 15_000 })
  // Settle network so React-Query / lazy chunks finish.
  await page
    .waitForLoadState('networkidle', { timeout: 5_000 })
    .catch(() => undefined)
}

test.describe('responsive layout per viewport', () => {
  test.beforeEach(async ({ page }) => {
    await enableVirtualAuthenticator(page)
    await registerPasskey(page, uniqueUser())
  })

  for (const path of ROUTES) {
    test(`route ${path} fits viewport without horizontal scroll`, async ({
      page,
    }, testInfo) => {
      await page.goto(path)
      await waitForRoute(page)

      // Capture the full page as an artifact for visual review.
      const safeName = path.replace(/[^a-zA-Z0-9]/g, '_') || 'root'
      await testInfo.attach(`${testInfo.project.name}-${safeName}.png`, {
        body: await page.screenshot({ fullPage: true }),
        contentType: 'image/png',
      })

      // Horizontal scroll = layout overflow = mobile bug.
      expect(
        await hasHorizontalScroll(page),
        `route ${path} produced horizontal scroll on viewport ${testInfo.project.name}`,
      ).toBe(false)
    })
  }

  test('sidebar collapses on narrow viewports', async ({ page }, testInfo) => {
    await page.goto('/')
    await waitForRoute(page)

    const viewport = page.viewportSize()
    if (!viewport) test.skip()
    const isNarrow = viewport!.width < 1024

    const nav = page.getByRole('navigation').first()
    const navVisible = await nav.isVisible().catch(() => false)
    if (isNarrow) {
      // Mobile: nav hidden OR a toggle button exposed.
      const toggleCount = await page
        .getByRole('button', { name: /menu|menü|toggle|öffnen|schließen|navigation/i })
        .count()
      expect(
        navVisible === false || toggleCount > 0,
        `viewport ${viewport!.width}px should hide nav or expose a toggle button`,
      ).toBe(true)
    } else {
      expect(navVisible, `viewport ${viewport!.width}px should show the nav inline`).toBe(true)
    }
  })
})
