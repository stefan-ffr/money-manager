import { test, expect } from '@playwright/test'
import { enableVirtualAuthenticator, uniqueUser, registerPasskey } from './helpers'

test('dashboard widgets, navigation and transaction filter', async ({ page }) => {
  await enableVirtualAuthenticator(page)
  await registerPasskey(page, uniqueUser())

  // Dashboard widgets (per-currency totals, account overview, chart)
  await expect(page.getByText('Gesamtsaldo je Währung')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Kontoübersicht' })).toBeVisible()
  await expect(page.getByText('Einnahmen & Ausgaben (6 Monate)')).toBeVisible()
  await expect(page.getByText('Offene Bestätigungen')).toBeVisible()

  // Transactions: filter bar wired up (search with no data -> "Keine Treffer")
  await page.getByRole('link', { name: 'Transaktionen' }).click()
  await expect(page.getByRole('heading', { name: 'Transaktionen', exact: true })).toBeVisible()
  const search = page.getByPlaceholder('Beschreibung…')
  await expect(search).toBeVisible()
  await search.fill('zzz-kein-treffer')
  await expect(page.getByText('Keine Treffer')).toBeVisible()

  // Recurring page renders
  await page.getByRole('link', { name: 'Dauerbuchungen' }).click()
  await expect(page.getByRole('heading', { name: 'Dauerbuchungen' })).toBeVisible()

  // Settings page renders with the Integrationen tab
  await page.getByRole('link', { name: 'Einstellungen' }).click()
  await expect(page.getByRole('heading', { name: 'Einstellungen', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Integrationen' }).click()
  await expect(page.getByText('Quittungsabrechnungsbot')).toBeVisible()
})

test('create a category via the settings UI', async ({ page }) => {
  await enableVirtualAuthenticator(page)
  await registerPasskey(page, uniqueUser())

  await page.getByRole('link', { name: 'Einstellungen' }).click()
  await page.getByRole('button', { name: 'Kategorien' }).click()
  await page.getByRole('button', { name: /Kategorie hinzufügen/ }).click()

  await page.getByPlaceholder('Name').fill('E2E-Kategorie')
  await page.getByPlaceholder('z. B. 3100').fill('3100')
  await page.getByTitle('Speichern').click()

  await expect(page.getByRole('cell', { name: 'E2E-Kategorie' })).toBeVisible()
})
