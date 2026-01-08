import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { AlertCircle, CheckCircle, Clock, PlusCircle, X } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || ''

interface Transaction {
  id: number
  account_id: number
  date: string
  amount: number
  category: string | null
  description: string | null
  status: string
  source: string
  requires_confirmation: boolean
  receipt_path: string | null
}

interface Account {
  id: number
  name: string
  type: string
  balance: string
  currency: string
}

function TransactionList() {
  const [showAddModal, setShowAddModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: transactions, isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: async () => {
      const res = await axios.get<Transaction[]>(`${API_URL}/api/v1/transactions`)
      return res.data
    },
  })

  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get<Account[]>(`${API_URL}/api/v1/accounts/`)
      return res.data
    },
  })

  const confirmMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.put(`${API_URL}/api/v1/transactions/${id}`, {
        status: 'confirmed',
        requires_confirmation: false
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`${API_URL}/api/v1/transactions/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const getSourceBadge = (source: string) => {
    const badges = {
      manual: { color: 'bg-gray-100 text-gray-800', label: 'Manuell' },
      telegram: { color: 'bg-blue-100 text-blue-800', label: 'Telegram' },
      federation: { color: 'bg-purple-100 text-purple-800', label: 'Federation' },
      csv_import: { color: 'bg-green-100 text-green-800', label: 'CSV Import' },
    }
    const badge = badges[source as keyof typeof badges] || badges.manual
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badge.color}`}>
        {badge.label}
      </span>
    )
  }

  const getStatusIcon = (status: string, requiresConfirmation: boolean) => {
    if (requiresConfirmation) {
      return <AlertCircle className="w-5 h-5 text-red-500" />
    }
    if (status === 'confirmed') {
      return <CheckCircle className="w-5 h-5 text-green-500" />
    }
    return <Clock className="w-5 h-5 text-yellow-500" />
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Transaktionen</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2"
        >
          <PlusCircle className="w-5 h-5" />
          Neue Transaktion
        </button>
      </div>

      {transactions && transactions.length > 0 ? (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Datum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Beschreibung
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kategorie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quelle
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Betrag
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transactions.map((tx) => (
                <tr
                  key={tx.id}
                  className={tx.requires_confirmation ? 'bg-red-50 border-l-4 border-red-500' : ''}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(tx.status, tx.requires_confirmation)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(tx.date).toLocaleDateString('de-CH')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="flex flex-col">
                      <span>{tx.description || 'Keine Beschreibung'}</span>
                      {tx.requires_confirmation && (
                        <span className="text-xs text-red-600 font-medium mt-1">
                          ⚠️ Bestätigung erforderlich
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tx.category || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getSourceBadge(tx.source)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <span className={tx.amount < 0 ? 'text-red-600' : 'text-green-600'}>
                      CHF {Math.abs(tx.amount).toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    {tx.requires_confirmation && (
                      <button
                        onClick={() => confirmMutation.mutate(tx.id)}
                        className="text-green-600 hover:text-green-900 font-medium"
                      >
                        ✓ Bestätigen
                      </button>
                    )}
                    <button
                      onClick={() => deleteMutation.mutate(tx.id)}
                      className="text-red-600 hover:text-red-900 font-medium"
                    >
                      Löschen
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Keine Transaktionen vorhanden
          </h2>
          <p className="text-gray-600 mb-6">
            Erstellen Sie Ihre erste Transaktion, um mit der Verwaltung zu beginnen.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 inline-flex items-center gap-2"
          >
            <PlusCircle className="w-5 h-5" />
            Erste Transaktion erstellen
          </button>
        </div>
      )}

      {showAddModal && (
        <TransactionModal
          accounts={accounts || []}
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false)
            queryClient.invalidateQueries({ queryKey: ['transactions'] })
            queryClient.invalidateQueries({ queryKey: ['accounts'] })
          }}
        />
      )}
    </div>
  )
}

interface TransactionModalProps {
  accounts: Account[]
  onClose: () => void
  onSuccess: () => void
}

function TransactionModal({ accounts, onClose, onSuccess }: TransactionModalProps) {
  const today = new Date().toISOString().split('T')[0]
  const [formData, setFormData] = useState({
    account_id: accounts[0]?.id || '',
    date: today,
    amount: '',
    category: '',
    description: '',
    status: 'confirmed',
  })

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      await axios.post(`${API_URL}/api/v1/transactions/`, {
        ...data,
        account_id: Number(data.account_id),
        amount: parseFloat(data.amount),
      })
    },
    onSuccess: () => {
      onSuccess()
    },
    onError: (error: any) => {
      alert(`Fehler: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.amount || parseFloat(formData.amount) === 0) {
      alert('Bitte geben Sie einen Betrag ein')
      return
    }
    createMutation.mutate(formData)
  }

  const categories = [
    'Miete & Nebenkosten',
    'Verpflegung',
    'Transport & Mobilität',
    'Gesundheit',
    'Versicherungen',
    'Kleidung',
    'Freizeit & Unterhaltung',
    'Bildung & Weiterbildung',
    'Spenden & Geschenke',
    'Einkommen',
    'Sonstiges',
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Neue Transaktion</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Konto *
            </label>
            <select
              value={formData.account_id}
              onChange={(e) =>
                setFormData({ ...formData, account_id: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            >
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name} ({account.currency})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Datum *
            </label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) =>
                setFormData({ ...formData, date: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Betrag * (negativ für Ausgaben, positiv für Einnahmen)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) =>
                setFormData({ ...formData, amount: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="z.B. -45.50 oder +1000.00"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Tipp: -45.50 für Ausgabe, +1000.00 für Einnahme
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kategorie (optional)
            </label>
            <select
              value={formData.category}
              onChange={(e) =>
                setFormData({ ...formData, category: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="">-- Keine Kategorie --</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Beschreibung (optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              rows={3}
              placeholder="z.B. Migros Einkauf"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending ? 'Speichern...' : 'Erstellen'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
            >
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TransactionList
