import { Page } from '@playwright/test'

/**
 * Attach a CTAP2 virtual authenticator via the Chrome DevTools Protocol so the
 * passkey (WebAuthn) flows can run headlessly in CI. Must be called before any
 * page triggers a WebAuthn ceremony.
 */
export async function enableVirtualAuthenticator(page: Page) {
  const client = await page.context().newCDPSession(page)
  await client.send('WebAuthn.enable')
  await client.send('WebAuthn.addVirtualAuthenticator', {
    options: {
      protocol: 'ctap2',
      transport: 'internal',
      hasResidentKey: true,
      hasUserVerification: true,
      isUserVerified: true,
      automaticPresenceSimulation: true,
    },
  })
  return client
}

export function uniqueUser() {
  const id = Math.random().toString(36).slice(2, 8)
  return {
    email: `e2e_${id}@example.com`,
    username: `e2e_${id}`,
    device: 'CI Authenticator',
  }
}

/** Register a new user with a passkey and land on the dashboard. */
export async function registerPasskey(
  page: Page,
  user: { email: string; username: string; device: string },
) {
  await page.goto('/register')
  await page.fill('#email', user.email)
  await page.fill('#username', user.username)
  await page.fill('#deviceName', user.device)
  await page.locator('form button[type="submit"]').click()
  await page.waitForURL((url) => new URL(url).pathname === '/', { timeout: 25_000 })
}
