import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  PlusCircle,
  CreditCard,
  Wallet,
  Building2,
  Banknote,
  Pencil,
  Trash2,
  X
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || ''

interface Account {
  id: number
  name: string
  type: string
  iban: string | null
  balance: string
  currency: string
}

const accountTypes = [
  { value: 'checking', label: 'Privatkonto', icon: Building2 },
  { value: 'savings', label: 'Sparkonto', icon: Banknote },
  { value: 'pillar3a', label: 'Säule 3a', icon: Banknote },
  { value: 'credit_card', label: 'Kreditkarte', icon: CreditCard },
  { value: 'cash', label: 'Bargeld', icon: Wallet },
]

function Accounts() {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const queryClient = useQueryClient()

  const { data: accounts, isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts/`)
      return res.data as Account[]
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (accountId: number) => {
      await axios.delete(`${API_URL}/api/v1/accounts/${accountId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
    },
  })

  const handleDelete = (account: Account) => {
    if (confirm(`Möchten Sie das Konto "${account.name}" wirklich löschen?`)) {
      deleteMutation.mutate(account.id)
    }
  }

  const getAccountTypeInfo = (type: string) => {
    return accountTypes.find(t => t.value === type) || accountTypes[0]
  }

  const formatBalance = (balance: string, currency: string) => {
    const num = parseFloat(balance)
    return new Intl.NumberFormat('de-CH', {
      style: 'currency',
      currency: currency || 'CHF',
    }).format(num)
  }

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Lade Konten...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Konten</h1>
        <button
          onClick={() => {
            setEditingAccount(null)
            setShowAddModal(true)
          }}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2"
        >
          <PlusCircle className="w-5 h-5" />
          Neues Konto
        </button>
      </div>

      {accounts && accounts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts.map((account) => {
            const typeInfo = getAccountTypeInfo(account.type)
            const Icon = typeInfo.icon
            const balance = parseFloat(account.balance)
            const isNegative = balance < 0

            return (
              <div
                key={account.id}
                className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="bg-primary-100 p-2 rounded-lg">
                      <Icon className="w-6 h-6 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900">
                        {account.name}
                      </h3>
                      <p className="text-sm text-gray-500">{typeInfo.label}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => {
                        setEditingAccount(account)
                        setShowAddModal(true)
                      }}
                      className="p-1 text-gray-400 hover:text-primary-600"
                      title="Bearbeiten"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(account)}
                      className="p-1 text-gray-400 hover:text-red-600"
                      title="Löschen"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-baseline">
                    <span className="text-sm text-gray-500">Saldo:</span>
                    <span
                      className={`text-2xl font-bold ${
                        isNegative ? 'text-red-600' : 'text-green-600'
                      }`}
                    >
                      {formatBalance(account.balance, account.currency)}
                    </span>
                  </div>

                  {account.iban && (
                    <div className="pt-2 border-t border-gray-100">
                      <p className="text-xs text-gray-500">IBAN</p>
                      <p className="text-sm text-gray-700 font-mono">
                        {account.iban}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <Wallet className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Keine Konten vorhanden
          </h2>
          <p className="text-gray-600 mb-6">
            Legen Sie Ihr erstes Konto an, um mit der Verwaltung Ihrer Finanzen zu beginnen.
          </p>
          <button
            onClick={() => {
              setEditingAccount(null)
              setShowAddModal(true)
            }}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 inline-flex items-center gap-2"
          >
            <PlusCircle className="w-5 h-5" />
            Erstes Konto erstellen
          </button>
        </div>
      )}

      {showAddModal && (
        <AccountModal
          account={editingAccount}
          onClose={() => {
            setShowAddModal(false)
            setEditingAccount(null)
          }}
          onSuccess={() => {
            setShowAddModal(false)
            setEditingAccount(null)
            queryClient.invalidateQueries({ queryKey: ['accounts'] })
          }}
        />
      )}
    </div>
  )
}

interface AccountModalProps {
  account: Account | null
  onClose: () => void
  onSuccess: () => void
}

function AccountModal({ account, onClose, onSuccess }: AccountModalProps) {
  const [formData, setFormData] = useState({
    name: account?.name || '',
    type: account?.type || 'checking',
    iban: account?.iban || '',
    balance: account?.balance || '0.00',
    currency: account?.currency || 'CHF',
  })

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      if (account) {
        await axios.put(`${API_URL}/api/v1/accounts/${account.id}`, data)
      } else {
        await axios.post(`${API_URL}/api/v1/accounts/`, data)
      }
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
    createMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {account ? 'Konto bearbeiten' : 'Neues Konto'}
          </h2>
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
              Kontoname *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="z.B. PostFinance Privatkonto"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kontotyp *
            </label>
            <div className="grid grid-cols-2 gap-2">
              {accountTypes.map((type) => {
                const Icon = type.icon
                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() =>
                      setFormData({ ...formData, type: type.value })
                    }
                    className={`flex items-center gap-2 p-3 rounded-lg border-2 transition-colors ${
                      formData.type === type.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm font-medium">{type.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              IBAN (optional)
            </label>
            <input
              type="text"
              value={formData.iban}
              onChange={(e) =>
                setFormData({ ...formData, iban: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 font-mono"
              placeholder="CH93 0076 2011 6238 5295 7"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Anfangssaldo *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.balance}
                onChange={(e) =>
                  setFormData({ ...formData, balance: e.target.value })
                }
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Währung *
              </label>
              <select
                value={formData.currency}
                onChange={(e) =>
                  setFormData({ ...formData, currency: e.target.value })
                }
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                required
              >
                <option value="CHF">CHF</option>
                <option value="EUR">EUR</option>
                <option value="USD">USD</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending
                ? 'Speichern...'
                : account
                ? 'Aktualisieren'
                : 'Erstellen'}
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

export default Accounts
