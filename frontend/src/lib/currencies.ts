// Zentrale Währungsliste – gespiegelt von backend/app/core/currencies.py
// Quelle der Wahrheit für alle Währungs-Dropdowns und die Betragsformatierung im Frontend.

export interface Currency {
  code: string
  name: string
  symbol: string
  decimalPlaces: number
  symbolPosition: 'before' | 'after'
  thousandsSeparator: string
  decimalSeparator: string
}

// Reihenfolge bestimmt die Anzeige in den Dropdowns.
export const CURRENCIES: Record<string, Currency> = {
  CHF: { code: 'CHF', name: 'Schweizer Franken', symbol: 'CHF', decimalPlaces: 2, symbolPosition: 'after', thousandsSeparator: "'", decimalSeparator: '.' },
  EUR: { code: 'EUR', name: 'Euro', symbol: '€', decimalPlaces: 2, symbolPosition: 'after', thousandsSeparator: '.', decimalSeparator: ',' },
  USD: { code: 'USD', name: 'US Dollar', symbol: '$', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  THB: { code: 'THB', name: 'Thai Baht', symbol: '฿', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  GBP: { code: 'GBP', name: 'British Pound', symbol: '£', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  JPY: { code: 'JPY', name: 'Japanese Yen', symbol: '¥', decimalPlaces: 0, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '' },
  CNY: { code: 'CNY', name: 'Chinese Yuan', symbol: '¥', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  AUD: { code: 'AUD', name: 'Australian Dollar', symbol: 'A$', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  CAD: { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  SGD: { code: 'SGD', name: 'Singapore Dollar', symbol: 'S$', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  INR: { code: 'INR', name: 'Indian Rupee', symbol: '₹', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
  BRL: { code: 'BRL', name: 'Brazilian Real', symbol: 'R$', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: '.', decimalSeparator: ',' },
  ZAR: { code: 'ZAR', name: 'South African Rand', symbol: 'R', decimalPlaces: 2, symbolPosition: 'before', thousandsSeparator: ',', decimalSeparator: '.' },
}

// Liste für Dropdowns (stabile Reihenfolge wie oben definiert).
export const CURRENCY_LIST: Currency[] = Object.values(CURRENCIES)

// Formatiert einen Betrag analog zur Backend-Logik (currencies.py).
export function formatCurrency(amount: number, code: string): string {
  const currency = CURRENCIES[code?.toUpperCase()]
  if (!currency) {
    return `${amount.toFixed(2)} ${code}`
  }

  const fixed = Math.abs(amount).toFixed(currency.decimalPlaces)
  const [intPart, decPart] = fixed.split('.')
  const withThousands = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, currency.thousandsSeparator)
  let amountStr = decPart ? `${withThousands}${currency.decimalSeparator}${decPart}` : withThousands
  if (amount < 0) amountStr = `-${amountStr}`

  return currency.symbolPosition === 'before'
    ? `${currency.symbol}${amountStr}`
    : `${amountStr} ${currency.symbol}`
}
