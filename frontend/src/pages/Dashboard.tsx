import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { formatCurrency } from '../lib/currencies'

const API_URL = import.meta.env.VITE_API_URL || ''

interface Account {
  id: number
  name: string
  type: string
  balance: string
  currency: string
}

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  checking: 'Girokonto',
  savings: 'Sparkonto',
  credit_card: 'Kreditkarte',
  cash: 'Bargeld',
}

function Dashboard() {
  const { data: accounts } = useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts`)
      return res.data
    },
  })

  // Salden je Währung getrennt summieren (kein Mischen verschiedener Währungen).
  const totalsByCurrency = (accounts || []).reduce<Record<string, number>>((acc, a) => {
    const code = a.currency || 'CHF'
    acc[code] = (acc[code] || 0) + parseFloat(a.balance)
    return acc
  }, {})
  const currencyTotals = Object.entries(totalsByCurrency)

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Gesamtsaldo je Währung
            </dt>
            <dd className="mt-1 space-y-1">
              {currencyTotals.length === 0 ? (
                <span className="text-3xl font-semibold text-gray-900">–</span>
              ) : (
                currencyTotals.map(([code, total]) => (
                  <div key={code} className="text-2xl font-semibold text-gray-900">
                    {formatCurrency(total, code)}
                  </div>
                ))
              )}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Anzahl Konten
            </dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {accounts?.length || 0}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Status
            </dt>
            <dd className="mt-1 text-3xl font-semibold text-green-600">
              ✓ Aktiv
            </dd>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Kontoübersicht</h2>
        <div className="bg-white shadow rounded-lg overflow-hidden">
          {!accounts || accounts.length === 0 ? (
            <p className="text-gray-600 p-6">
              Noch keine Konten vorhanden. Lege unter „Konten" dein erstes Konto an.
            </p>
          ) : (
            <ul className="divide-y divide-gray-200">
              {accounts.map((account) => (
                <li
                  key={account.id}
                  className="flex items-center justify-between px-4 py-4 sm:px-6"
                >
                  <div>
                    <p className="font-medium text-gray-900">{account.name}</p>
                    <p className="text-sm text-gray-500">
                      {ACCOUNT_TYPE_LABELS[account.type] || account.type} · {account.currency}
                    </p>
                  </div>
                  <div
                    className={`text-lg font-semibold ${
                      parseFloat(account.balance) < 0 ? 'text-red-600' : 'text-gray-900'
                    }`}
                  >
                    {formatCurrency(parseFloat(account.balance), account.currency)}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
