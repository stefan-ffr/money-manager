import { test, expect } from '@playwright/test'
import { enableVirtualAuthenticator, uniqueUser, registerPasskey } from './helpers'

test('passkey registration, then logout and re-login', async ({ page }) => {
  await enableVirtualAuthenticator(page)
  const user = uniqueUser()

  // Register with a passkey -> lands on the dashboard
  await registerPasskey(page, user)
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()

  // Logout
  await page.getByRole('button', { name: 'Abmelden' }).click()
  await page.waitForURL((u) => new URL(u).pathname === '/login', { timeout: 15_000 })

  // Login again with the same passkey (resident credential on the authenticator)
  await page.fill('#username', user.username)
  await page.getByRole('button', { name: 'Mit Passkey anmelden' }).click()
  await page.waitForURL((u) => new URL(u).pathname === '/', { timeout: 25_000 })
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
})
