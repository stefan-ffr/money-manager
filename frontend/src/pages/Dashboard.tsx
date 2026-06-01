import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid,
} from 'recharts'
import { formatCurrency } from '../lib/currencies'

const API_URL = import.meta.env.VITE_API_URL || ''

interface Account {
  id: number
  name: string
  type: string
  balance: string
  currency: string
}

interface Transaction {
  id: number
  account_id: number
  date: string
  amount: number
  category: string | null
  description: string | null
  status: string
  requires_confirmation: boolean
}

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  checking: 'Girokonto',
  savings: 'Sparkonto',
  credit_card: 'Kreditkarte',
  cash: 'Bargeld',
}

const MONTH_LABELS = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

function Dashboard() {
  const { data: accounts } = useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts`)
      return res.data
    },
  })

  const { data: transactions } = useQuery<Transaction[]>({
    queryKey: ['transactions', {}],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/transactions/?limit=500`)
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

  const currencyByAccount: Record<number, string> = {}
  ;(accounts || []).forEach((a) => { currencyByAccount[a.id] = a.currency || 'CHF' })

  // Häufigste Kontowährung als Anzeigewährung für das Diagramm (vermeidet Mischen).
  const currencyCounts = (accounts || []).reduce<Record<string, number>>((acc, a) => {
    acc[a.currency] = (acc[a.currency] || 0) + 1
    return acc
  }, {})
  const displayCurrency = Object.entries(currencyCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'CHF'

  const pendingCount = (transactions || []).filter((t) => t.requires_confirmation).length

  const recentTransactions = [...(transactions || [])]
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 5)

  // Letzte 6 Monate Einnahmen/Ausgaben für die Anzeigewährung
  const monthBuckets: { key: string; label: string; Einnahmen: number; Ausgaben: number }[] = []
  const now = new Date()
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    monthBuckets.push({
      key: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      label: MONTH_LABELS[d.getMonth()],
      Einnahmen: 0,
      Ausgaben: 0,
    })
  }
  const bucketByKey = Object.fromEntries(monthBuckets.map((b) => [b.key, b]))
  ;(transactions || []).forEach((t) => {
    if (currencyByAccount[t.account_id] !== displayCurrency) return
    const key = t.date.slice(0, 7)
    const bucket = bucketByKey[key]
    if (!bucket) return
    if (t.amount >= 0) bucket.Einnahmen += t.amount
    else bucket.Ausgaben += Math.abs(t.amount)
  })

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

        <Link to="/transactions" className="bg-white overflow-hidden shadow rounded-lg hover:bg-gray-50">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Offene Bestätigungen
            </dt>
            <dd className={`mt-1 text-3xl font-semibold ${pendingCount > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {pendingCount}
            </dd>
          </div>
        </Link>
      </div>

      {/* Einnahmen/Ausgaben Chart */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Einnahmen & Ausgaben (6 Monate)</h2>
          <span className="text-sm text-gray-500">in {displayCurrency}</span>
        </div>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <BarChart data={monthBuckets}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip formatter={(value: number) => formatCurrency(value, displayCurrency)} />
              <Legend />
              <Bar dataKey="Einnahmen" fill="#16a34a" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Ausgaben" fill="#dc2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Kontoübersicht */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Kontoübersicht</h2>
          <div className="bg-white shadow rounded-lg overflow-hidden">
            {!accounts || accounts.length === 0 ? (
              <p className="text-gray-600 p-6">
                Noch keine Konten vorhanden. Lege unter „Konten" dein erstes Konto an.
              </p>
            ) : (
              <ul className="divide-y divide-gray-200">
                {accounts.map((account) => (
                  <li key={account.id} className="flex items-center justify-between px-4 py-4 sm:px-6">
                    <div>
                      <p className="font-medium text-gray-900">{account.name}</p>
                      <p className="text-sm text-gray-500">
                        {ACCOUNT_TYPE_LABELS[account.type] || account.type} · {account.currency}
                      </p>
                    </div>
                    <div className={`text-lg font-semibold ${parseFloat(account.balance) < 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      {formatCurrency(parseFloat(account.balance), account.currency)}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Letzte Transaktionen */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Letzte Transaktionen</h2>
            <Link to="/transactions" className="text-sm text-primary-600 hover:text-primary-700">
              Alle anzeigen
            </Link>
          </div>
          <div className="bg-white shadow rounded-lg overflow-hidden">
            {recentTransactions.length === 0 ? (
              <p className="text-gray-600 p-6">Noch keine Transaktionen.</p>
            ) : (
              <ul className="divide-y divide-gray-200">
                {recentTransactions.map((tx) => (
                  <li key={tx.id} className="flex items-center justify-between px-4 py-3 sm:px-6">
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {tx.description || tx.category || 'Transaktion'}
                      </p>
                      <p className="text-sm text-gray-500">{tx.date}</p>
                    </div>
                    <div className={`text-sm font-semibold whitespace-nowrap ${tx.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {formatCurrency(tx.amount, currencyByAccount[tx.account_id] || 'CHF')}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
