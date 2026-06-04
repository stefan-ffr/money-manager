import { test, expect, type Page } from '@playwright/test'
import { enableVirtualAuthenticator, uniqueUser, registerPasskey } from './helpers'

/**
 * Responsive regression suite. Runs the same set of routes across every
 * viewport defined in `playwright.config.ts` under `responsive-*` projects.
 *
 * For each route we assert:
 *   - the page actually rendered (key heading visible)
 *   - there is NO unintended horizontal scroll (the #1 mobile regression)
 *   - on viewports ≥ 1024 the sidebar is visible; on < 1024 it must be
 *     collapsed/hidden behind a hamburger toggle
 *
 * Pixel-diff screenshots are NOT asserted (we don't lock in the current
 * possibly-broken layout as truth). Instead, every page+viewport pair
 * uploads a full-page PNG as a CI artifact for visual review in PRs.
 */

const ROUTES: { path: string; heading: RegExp }[] = [
  { path: '/', heading: /Dashboard|Gesamtsaldo/ },
  { path: '/accounts', heading: /Konten|Kontoübersicht/ },
  { path: '/transactions', heading: /Transaktionen/ },
  { path: '/shared-accounts', heading: /Geteilte Konten|Shared/ },
  { path: '/bank-import', heading: /Bank.?Import|Import/ },
  { path: '/reconciliation', heading: /Abstimmung|Reconciliation|Bestätigungen/ },
  { path: '/recurring', heading: /Dauerbuchungen|Recurring/ },
  { path: '/settings', heading: /Einstellungen|Settings/ },
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

test.describe('responsive layout per viewport', () => {
  test.beforeEach(async ({ page }) => {
    await enableVirtualAuthenticator(page)
    await registerPasskey(page, uniqueUser())
  })

  for (const route of ROUTES) {
    test(`route ${route.path} fits viewport without horizontal scroll`, async ({
      page,
    }, testInfo) => {
      await page.goto(route.path)
      // Wait for the route to render — heading is the most stable signal.
      await expect(
        page.getByRole('heading', { name: route.heading }).first(),
      ).toBeVisible({ timeout: 15_000 })

      // Capture the full page as an artifact for visual review.
      const safeName = route.path.replace(/[^a-zA-Z0-9]/g, '_') || 'root'
      await testInfo.attach(`${testInfo.project.name}-${safeName}.png`, {
        body: await page.screenshot({ fullPage: true }),
        contentType: 'image/png',
      })

      // Horizontal scroll = layout overflow = mobile bug.
      expect(
        await hasHorizontalScroll(page),
        `route ${route.path} produced horizontal scroll on viewport ${testInfo.project.name}`,
      ).toBe(false)
    })
  }

  test('sidebar collapses on narrow viewports', async ({ page }, testInfo) => {
    await page.goto('/')
    await expect(
      page.getByRole('heading', { name: /Dashboard|Gesamtsaldo/ }).first(),
    ).toBeVisible({ timeout: 15_000 })

    const viewport = page.viewportSize()
    if (!viewport) test.skip()
    const isNarrow = viewport!.width < 1024

    // The Layout component renders a nav with the main routes; on desktop it
    // is always visible, on mobile it should sit behind a toggle (hamburger).
    const nav = page.getByRole('navigation').first()
    const navVisible = await nav.isVisible().catch(() => false)
    if (isNarrow) {
      // On mobile: either nav is hidden, or a toggle button is present.
      const toggle = page
        .getByRole('button', { name: /menu|menü|toggle|öffnen|schließen/i })
        .first()
      const toggleExists = await toggle.count()
      expect(
        navVisible === false || toggleExists > 0,
        `viewport ${viewport!.width}px should hide nav or expose a toggle button`,
      ).toBe(true)
    } else {
      // On wide screens nav must be visible.
      expect(navVisible, `viewport ${viewport!.width}px should show the nav inline`).toBe(true)
    }
  })
})
