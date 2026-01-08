import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  PlusCircle,
  Users,
  UserPlus,
  Receipt,
  TrendingUp,
  ArrowRight,
  X,
  DollarSign,
  Percent,
  Equal
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || ''

interface SharedAccount {
  id: number
  name: string
  description: string | null
  currency: string
}

interface Balance {
  user: string
  amount: number
  status: 'owes' | 'owed' | 'settled'
}

interface Settlement {
  from: string
  to: string
  amount: number
}

function SharedAccounts() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: sharedAccounts, isLoading } = useQuery({
    queryKey: ['shared-accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/shared-accounts/`)
      return res.data as SharedAccount[]
    },
  })

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Lade Gemeinschaftskonten...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gemeinschaftskonten</h1>
          <p className="text-gray-600 mt-1">
            WG-Konten, Vereinskassen oder geteilte Ausgaben verwalten
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2"
        >
          <PlusCircle className="w-5 h-5" />
          Neues Konto
        </button>
      </div>

      {sharedAccounts && sharedAccounts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sharedAccounts.map((account) => (
            <div
              key={account.id}
              onClick={() => setSelectedAccount(account.id)}
              className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-100 p-2 rounded-lg">
                    <Users className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900">{account.name}</h3>
                    <p className="text-sm text-gray-500">{account.currency}</p>
                  </div>
                </div>
              </div>

              {account.description && (
                <p className="text-sm text-gray-600 mb-4">{account.description}</p>
              )}

              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedAccount(account.id)
                }}
                className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Details anzeigen →
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Keine Gemeinschaftskonten vorhanden
          </h2>
          <p className="text-gray-600 mb-6">
            Erstellen Sie Ihr erstes Gemeinschaftskonto für WG, Verein oder Familie.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 inline-flex items-center gap-2"
          >
            <PlusCircle className="w-5 h-5" />
            Erstes Konto erstellen
          </button>
        </div>
      )}

      {showCreateModal && (
        <CreateSharedAccountModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['shared-accounts'] })
          }}
        />
      )}

      {selectedAccount && (
        <SharedAccountDetails
          accountId={selectedAccount}
          onClose={() => setSelectedAccount(null)}
        />
      )}
    </div>
  )
}

interface CreateSharedAccountModalProps {
  onClose: () => void
  onSuccess: () => void
}

function CreateSharedAccountModal({ onClose, onSuccess }: CreateSharedAccountModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    currency: 'CHF',
  })

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      await axios.post(`${API_URL}/api/v1/shared-accounts/`, data)
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
          <h2 className="text-2xl font-bold text-gray-900">Neues Gemeinschaftskonto</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="z.B. WG Binningen, Feuerwehr Raura"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Beschreibung (optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              rows={3}
              placeholder="z.B. Gemeinsame Haushaltskasse für Miete und Nebenkosten"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Währung *</label>
            <select
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            >
              <option value="CHF">CHF</option>
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Erstellen...' : 'Erstellen'}
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

interface SharedAccountDetailsProps {
  accountId: number
  onClose: () => void
}

function SharedAccountDetails({ accountId, onClose }: SharedAccountDetailsProps) {
  const [activeTab, setActiveTab] = useState<'members' | 'transactions' | 'balance'>('members')
  const [showAddMemberModal, setShowAddMemberModal] = useState(false)
  const [showAddTransactionModal, setShowAddTransactionModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: account } = useQuery({
    queryKey: ['shared-account', accountId],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/shared-accounts/`)
      const accounts = res.data as SharedAccount[]
      return accounts.find((a) => a.id === accountId)
    },
  })

  const { data: balance } = useQuery({
    queryKey: ['shared-account-balance', accountId],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/shared-accounts/${accountId}/balance`)
      return res.data as Balance[]
    },
    enabled: activeTab === 'balance',
  })

  const { data: settlements } = useQuery({
    queryKey: ['shared-account-settlements', accountId],
    queryFn: async () => {
      const res = await axios.post(`${API_URL}/api/v1/shared-accounts/${accountId}/settle`)
      return res.data as Settlement[]
    },
    enabled: activeTab === 'balance',
  })

  if (!account) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{account.name}</h2>
            {account.description && (
              <p className="text-sm text-gray-600 mt-1">{account.description}</p>
            )}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('members')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'members'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Mitglieder
            </button>
            <button
              onClick={() => setActiveTab('transactions')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'transactions'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Receipt className="w-4 h-4 inline mr-2" />
              Transaktionen
            </button>
            <button
              onClick={() => setActiveTab('balance')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'balance'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <TrendingUp className="w-4 h-4 inline mr-2" />
              Abrechnung
            </button>
          </nav>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'members' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Mitglieder</h3>
                <button
                  onClick={() => setShowAddMemberModal(true)}
                  className="bg-primary-600 text-white px-3 py-1.5 rounded text-sm hover:bg-primary-700 flex items-center gap-1"
                >
                  <UserPlus className="w-4 h-4" />
                  Hinzufügen
                </button>
              </div>
              <div className="bg-gray-50 rounded-lg p-6 text-center">
                <p className="text-gray-600">
                  Noch keine Mitglieder. Klicken Sie auf "Hinzufügen" um Mitglieder einzuladen.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'transactions' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Split Transaktionen</h3>
                <button
                  onClick={() => setShowAddTransactionModal(true)}
                  className="bg-primary-600 text-white px-3 py-1.5 rounded text-sm hover:bg-primary-700 flex items-center gap-1"
                >
                  <PlusCircle className="w-4 h-4" />
                  Neue Ausgabe
                </button>
              </div>
              <div className="bg-gray-50 rounded-lg p-6 text-center">
                <p className="text-gray-600">Noch keine Transaktionen vorhanden</p>
              </div>
            </div>
          )}

          {activeTab === 'balance' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Aktuelle Bilanz</h3>
                {balance && balance.length > 0 ? (
                  <div className="space-y-2">
                    {balance.map((item, index) => (
                      <div
                        key={index}
                        className={`flex justify-between items-center p-4 rounded-lg ${
                          item.status === 'owed'
                            ? 'bg-green-50 border border-green-200'
                            : item.status === 'owes'
                            ? 'bg-red-50 border border-red-200'
                            : 'bg-gray-50 border border-gray-200'
                        }`}
                      >
                        <span className="font-medium">{item.user}</span>
                        <span
                          className={`font-bold ${
                            item.status === 'owed'
                              ? 'text-green-600'
                              : item.status === 'owes'
                              ? 'text-red-600'
                              : 'text-gray-600'
                          }`}
                        >
                          {item.status === 'owed' ? '+' : item.status === 'owes' ? '-' : ''}
                          {account.currency} {Math.abs(item.amount).toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-6 text-center">
                    <p className="text-gray-600">Noch keine Transaktionen für Bilanz</p>
                  </div>
                )}
              </div>

              {settlements && settlements.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Optimale Abrechnung</h3>
                  <div className="space-y-3">
                    {settlements.map((settlement, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg"
                      >
                        <span className="font-medium text-blue-900">{settlement.from}</span>
                        <ArrowRight className="w-5 h-5 text-blue-600" />
                        <span className="font-medium text-blue-900">{settlement.to}</span>
                        <span className="ml-auto font-bold text-blue-700">
                          {account.currency} {settlement.amount.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-4">
                    Diese Zahlungen gleichen alle Schulden optimal aus (minimale Anzahl Transaktionen)
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {showAddMemberModal && (
          <AddMemberModal
            accountId={accountId}
            onClose={() => setShowAddMemberModal(false)}
            onSuccess={() => {
              setShowAddMemberModal(false)
              queryClient.invalidateQueries({ queryKey: ['shared-account', accountId] })
            }}
          />
        )}

        {showAddTransactionModal && (
          <AddSplitTransactionModal
            accountId={accountId}
            currency={account.currency}
            onClose={() => setShowAddTransactionModal(false)}
            onSuccess={() => {
              setShowAddTransactionModal(false)
              queryClient.invalidateQueries({ queryKey: ['shared-account', accountId] })
              queryClient.invalidateQueries({ queryKey: ['shared-account-balance', accountId] })
            }}
          />
        )}
      </div>
    </div>
  )
}

interface AddMemberModalProps {
  accountId: number
  onClose: () => void
  onSuccess: () => void
}

function AddMemberModal({ accountId, onClose, onSuccess }: AddMemberModalProps) {
  const [formData, setFormData] = useState({
    user_identifier: '',
    instance_url: '',
    role: 'member',
  })

  const addMemberMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      await axios.post(`${API_URL}/api/v1/shared-accounts/${accountId}/members`, {
        ...data,
        instance_url: data.instance_url || null,
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
    addMemberMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Mitglied hinzufügen</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              User Identifier *
            </label>
            <input
              type="text"
              value={formData.user_identifier}
              onChange={(e) => setFormData({ ...formData, user_identifier: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="z.B. stefan@juroct.ch oder stefan"
              required
            />
            <p className="text-xs text-gray-500 mt-1">Email oder Benutzername</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Instanz URL (optional)
            </label>
            <input
              type="url"
              value={formData.instance_url}
              onChange={(e) => setFormData({ ...formData, instance_url: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="https://money.example.com"
            />
            <p className="text-xs text-gray-500 mt-1">
              Für Federation: URL der anderen Money Manager Instanz
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Rolle *</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            >
              <option value="member">Mitglied</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={addMemberMutation.isPending}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {addMemberMutation.isPending ? 'Hinzufügen...' : 'Hinzufügen'}
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

interface AddSplitTransactionModalProps {
  accountId: number
  currency: string
  onClose: () => void
  onSuccess: () => void
}

function AddSplitTransactionModal({
  accountId,
  currency,
  onClose,
  onSuccess,
}: AddSplitTransactionModalProps) {
  const today = new Date().toISOString().split('T')[0]
  const [formData, setFormData] = useState({
    paid_by: '',
    total_amount: '',
    date: today,
    description: '',
    category: '',
    split_type: 'equal',
  })

  const addTransactionMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      await axios.post(`${API_URL}/api/v1/shared-accounts/${accountId}/split-transaction`, {
        shared_account_id: accountId,
        paid_by: data.paid_by,
        total_amount: parseFloat(data.total_amount),
        date: data.date,
        description: data.description || null,
        category: data.category || null,
        split_type: data.split_type,
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
    addTransactionMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Neue Ausgabe teilen</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bezahlt von *
            </label>
            <input
              type="text"
              value={formData.paid_by}
              onChange={(e) => setFormData({ ...formData, paid_by: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="User Identifier (z.B. stefan@juroct.ch)"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Gesamtbetrag * ({currency})
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.total_amount}
              onChange={(e) => setFormData({ ...formData, total_amount: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="0.00"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Datum *</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aufteilung *
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, split_type: 'equal' })}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-colors ${
                  formData.split_type === 'equal'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Equal className="w-5 h-5" />
                <span className="text-xs font-medium">Gleich</span>
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, split_type: 'percentage' })}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-colors ${
                  formData.split_type === 'percentage'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled
              >
                <Percent className="w-5 h-5" />
                <span className="text-xs font-medium">Prozent</span>
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, split_type: 'custom' })}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-colors ${
                  formData.split_type === 'custom'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled
              >
                <DollarSign className="w-5 h-5" />
                <span className="text-xs font-medium">Custom</span>
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Derzeit nur gleiche Aufteilung verfügbar
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Beschreibung (optional)
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="z.B. Miete Januar, Einkauf"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={addTransactionMutation.isPending}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {addTransactionMutation.isPending ? 'Erstellen...' : 'Erstellen'}
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

export default SharedAccounts
