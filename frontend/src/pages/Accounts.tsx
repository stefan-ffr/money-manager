import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  PlusCircle,
  CreditCard,
  Wallet,
  Building2,
  Banknote,
  X,
  Save,
  ArrowRightLeft,
  Eye,
  Upload,
  Plus,
  Trash2
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

const accountTypes = [
  { value: 'checking', label: 'Privatkonto', icon: Building2 },
  { value: 'savings', label: 'Sparkonto', icon: Banknote },
  { value: 'pillar3a', label: 'Säule 3a', icon: Banknote },
  { value: 'credit_card', label: 'Kreditkarte', icon: CreditCard },
  { value: 'cash', label: 'Bargeld', icon: Wallet },
]

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

function Accounts() {
  const [showAccountModal, setShowAccountModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null)
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [showMoveModal, setShowMoveModal] = useState(false)
  const [receiptPreview, setReceiptPreview] = useState<{ transactionId: number; path: string } | null>(null)

  const [formData, setFormData] = useState({
    type: 'expense',
    date: new Date().toISOString().split('T')[0],
    amount: '',
    description: '',
    category: '',
  })

  const queryClient = useQueryClient()

  const { data: accounts, isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts/`)
      return res.data as Account[]
    },
  })

  const { data: transactions } = useQuery({
    queryKey: ['transactions', selectedAccountId],
    queryFn: async () => {
      if (!selectedAccountId) return []
      const res = await axios.get<Transaction[]>(
        `${API_URL}/api/v1/transactions/?account_id=${selectedAccountId}`
      )
      return res.data
    },
    enabled: !!selectedAccountId,
  })

  // Auto-select first account
  useEffect(() => {
    if (accounts && accounts.length > 0 && !selectedAccountId) {
      setSelectedAccountId(accounts[0].id)
    }
  }, [accounts, selectedAccountId])

  const createTransactionMutation = useMutation({
    mutationFn: async (data: any) => {
      if (selectedTransaction) {
        await axios.put(`${API_URL}/api/v1/transactions/${selectedTransaction.id}`, data)
      } else {
        await axios.post(`${API_URL}/api/v1/transactions/`, {
          ...data,
          account_id: selectedAccountId,
        })
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      handleNewTransaction()
    },
  })

  const deleteTransactionMutation = useMutation({
    mutationFn: async (transactionId: number) => {
      await axios.delete(`${API_URL}/api/v1/transactions/${transactionId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      handleNewTransaction()
    },
  })

  const moveTransactionMutation = useMutation({
    mutationFn: async ({ transactionId, targetAccountId }: { transactionId: number; targetAccountId: number }) => {
      await axios.put(`${API_URL}/api/v1/transactions/${transactionId}`, {
        account_id: targetAccountId
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      setShowMoveModal(false)
      handleNewTransaction()
    },
  })

  const uploadReceiptMutation = useMutation({
    mutationFn: async ({ transactionId, file }: { transactionId: number; file: File }) => {
      const formData = new FormData()
      formData.append('file', file)
      await axios.post(`${API_URL}/api/v1/transactions/${transactionId}/receipt`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
    },
  })

  const handleTransactionClick = (tx: Transaction) => {
    setSelectedTransaction(tx)
    setFormData({
      type: tx.amount < 0 ? 'expense' : 'income',
      date: tx.date,
      amount: Math.abs(tx.amount).toString(),
      description: tx.description || '',
      category: tx.category || '',
    })
  }

  const handleNewTransaction = () => {
    setSelectedTransaction(null)
    setFormData({
      type: 'expense',
      date: new Date().toISOString().split('T')[0],
      amount: '',
      description: '',
      category: '',
    })
  }

  const handleSaveTransaction = () => {
    if (!formData.amount || parseFloat(formData.amount) === 0) {
      alert('Bitte geben Sie einen Betrag ein')
      return
    }

    const amount = formData.type === 'expense'
      ? -Math.abs(parseFloat(formData.amount))
      : Math.abs(parseFloat(formData.amount))

    createTransactionMutation.mutate({
      date: formData.date,
      amount: amount,
      description: formData.description,
      category: formData.category,
      status: 'confirmed',
    })
  }

  const handleDeleteTransaction = () => {
    if (selectedTransaction && confirm('Transaktion wirklich löschen?')) {
      deleteTransactionMutation.mutate(selectedTransaction.id)
    }
  }

  const handleReceiptUpload = () => {
    if (!selectedTransaction) return
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*,application/pdf'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file && selectedTransaction) {
        uploadReceiptMutation.mutate({ transactionId: selectedTransaction.id, file })
      }
    }
    input.click()
  }

  const handleReceiptPreview = (transactionId: number) => {
    setReceiptPreview({ transactionId, path: `${API_URL}/api/v1/transactions/${transactionId}/receipt` })
  }

  const selectedAccount = accounts?.find(a => a.id === selectedAccountId)

  // Calculate running balance
  let runningBalance = parseFloat(selectedAccount?.balance || '0')
  const transactionsWithBalance = transactions?.map(tx => {
    const txWithBalance = { ...tx, runningBalance }
    runningBalance -= tx.amount
    return txWithBalance
  }) || []

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!accounts || accounts.length === 0) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <Wallet className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Keine Konten vorhanden
          </h2>
          <p className="text-gray-600 mb-6">
            Legen Sie Ihr erstes Konto an, um mit der Verwaltung zu beginnen.
          </p>
          <button
            onClick={() => {
              setEditingAccount(null)
              setShowAccountModal(true)
            }}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 inline-flex items-center gap-2"
          >
            <PlusCircle className="w-5 h-5" />
            Erstes Konto erstellen
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header with Account Selector */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Konto:</label>
            <select
              value={selectedAccountId || ''}
              onChange={(e) => {
                setSelectedAccountId(Number(e.target.value))
                handleNewTransaction()
              }}
              className="text-lg font-semibold border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name} - {parseFloat(account.balance).toFixed(2)} {account.currency}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setEditingAccount(selectedAccount || null)
                setShowAccountModal(true)
              }}
              className="text-primary-600 hover:text-primary-700 px-3 py-1 border border-primary-600 rounded-md text-sm"
            >
              Konto bearbeiten
            </button>
            <button
              onClick={() => {
                setEditingAccount(null)
                setShowAccountModal(true)
              }}
              className="bg-primary-600 text-white px-3 py-1 rounded-md hover:bg-primary-700 flex items-center gap-1 text-sm"
            >
              <PlusCircle className="w-4 h-4" />
              Neues Konto
            </button>
          </div>
        </div>
      </div>

      {/* Top Section: Transaction List (2/3) */}
      <div className="flex-[2] overflow-auto bg-white">
        {transactionsWithBalance.length > 0 ? (
          <table className="min-w-full">
            <thead className="bg-gray-50 border-b-2 border-gray-200 sticky top-0">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 w-28">Datum</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Beschreibung</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Kategorie</th>
                <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600 w-28">Einnahme</th>
                <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600 w-28">Ausgabe</th>
                <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600 w-32">Saldo</th>
                <th className="px-4 py-2 text-center text-xs font-semibold text-gray-600 w-16">Beleg</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {transactionsWithBalance.map((tx) => (
                <tr
                  key={tx.id}
                  onClick={() => handleTransactionClick(tx)}
                  className={`cursor-pointer hover:bg-blue-50 ${
                    selectedTransaction?.id === tx.id ? 'bg-blue-100' : ''
                  } ${tx.requires_confirmation ? 'bg-red-50' : ''}`}
                >
                  <td className="px-4 py-2 text-sm text-gray-900">
                    {new Date(tx.date).toLocaleDateString('de-CH')}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-900">
                    {tx.description || '-'}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-600">
                    {tx.category || '-'}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">
                    {tx.amount > 0 && (
                      <span className="text-green-600 font-medium">
                        {tx.amount.toFixed(2)}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">
                    {tx.amount < 0 && (
                      <span className="text-red-600 font-medium">
                        {Math.abs(tx.amount).toFixed(2)}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-sm text-right font-semibold text-gray-900">
                    {tx.runningBalance.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-center">
                    {tx.receipt_path && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleReceiptPreview(tx.id)
                        }}
                        className="text-blue-600 hover:text-blue-900"
                        title="Beleg anzeigen"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Keine Transaktionen vorhanden</p>
          </div>
        )}
      </div>

      {/* Bottom Section: Transaction Form (1/3) */}
      <div className="flex-[1] bg-gray-50 border-t-4 border-gray-300 p-4 overflow-auto">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Left Column */}
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Typ
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="expense">Ausgabe</option>
                  <option value="income">Einnahme</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Datum
                </label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Betrag
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  placeholder="0.00"
                />
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Beschreibung
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  placeholder="z.B. Migros Einkauf"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Kategorie
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">-- Keine Kategorie --</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {selectedTransaction && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Beleg
                  </label>
                  <div className="flex gap-2">
                    {selectedTransaction.receipt_path ? (
                      <button
                        onClick={() => handleReceiptPreview(selectedTransaction.id)}
                        className="flex-1 text-sm text-blue-600 hover:text-blue-700 px-3 py-1.5 border border-blue-600 rounded-md flex items-center justify-center gap-1"
                      >
                        <Eye className="w-4 h-4" />
                        Anzeigen
                      </button>
                    ) : (
                      <button
                        onClick={handleReceiptUpload}
                        className="flex-1 text-sm text-gray-700 hover:text-gray-900 px-3 py-1.5 border border-gray-300 rounded-md flex items-center justify-center gap-1"
                      >
                        <Upload className="w-4 h-4" />
                        Hochladen
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={handleNewTransaction}
              className="px-4 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              Neu
            </button>
            <button
              onClick={handleSaveTransaction}
              disabled={createTransactionMutation.isPending}
              className="px-4 py-1.5 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 flex items-center gap-1"
            >
              <Save className="w-4 h-4" />
              {selectedTransaction ? 'Speichern' : 'Erstellen'}
            </button>
            {selectedTransaction && (
              <>
                <button
                  onClick={() => setShowMoveModal(true)}
                  className="px-4 py-1.5 text-sm border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 flex items-center gap-1"
                >
                  <ArrowRightLeft className="w-4 h-4" />
                  Verschieben
                </button>
                <button
                  onClick={handleDeleteTransaction}
                  className="px-4 py-1.5 text-sm border border-red-600 text-red-600 rounded-md hover:bg-red-50 flex items-center gap-1"
                >
                  <Trash2 className="w-4 h-4" />
                  Löschen
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showAccountModal && (
        <AccountModal
          account={editingAccount}
          onClose={() => {
            setShowAccountModal(false)
            setEditingAccount(null)
          }}
          onSuccess={() => {
            setShowAccountModal(false)
            setEditingAccount(null)
            queryClient.invalidateQueries({ queryKey: ['accounts'] })
          }}
        />
      )}

      {showMoveModal && selectedTransaction && (
        <MoveTransactionModal
          transaction={selectedTransaction}
          accounts={accounts || []}
          onClose={() => setShowMoveModal(false)}
          onMove={(targetAccountId) => {
            moveTransactionMutation.mutate({
              transactionId: selectedTransaction.id,
              targetAccountId,
            })
          }}
        />
      )}

      {receiptPreview && (
        <ReceiptPreviewModal
          transactionId={receiptPreview.transactionId}
          receiptUrl={receiptPreview.path}
          onClose={() => setReceiptPreview(null)}
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

interface MoveTransactionModalProps {
  transaction: Transaction
  accounts: Account[]
  onClose: () => void
  onMove: (targetAccountId: number) => void
}

function MoveTransactionModal({ transaction, accounts, onClose, onMove }: MoveTransactionModalProps) {
  const [targetAccountId, setTargetAccountId] = useState<number>(
    accounts.filter(a => a.id !== transaction.account_id)[0]?.id || 0
  )

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Transaktion verschieben</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          <p className="text-sm text-gray-600 mb-4">
            Transaktion: <strong>{transaction.description || 'Ohne Beschreibung'}</strong>
          </p>
          <p className="text-sm text-gray-600 mb-4">
            Betrag: <strong>{transaction.amount.toFixed(2)}</strong>
          </p>

          <label className="block text-sm font-medium text-gray-700 mb-2">
            Zielkonto auswählen:
          </label>
          <select
            value={targetAccountId}
            onChange={(e) => setTargetAccountId(Number(e.target.value))}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            {accounts
              .filter(a => a.id !== transaction.account_id)
              .map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
          </select>

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => onMove(targetAccountId)}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
            >
              Verschieben
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
            >
              Abbrechen
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

interface ReceiptPreviewModalProps {
  transactionId: number
  receiptUrl: string
  onClose: () => void
}

function ReceiptPreviewModal({ transactionId, receiptUrl, onClose }: ReceiptPreviewModalProps) {
  const isPDF = receiptUrl.toLowerCase().includes('.pdf')

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Beleg Vorschau</h2>
          <div className="flex gap-2">
            <a
              href={receiptUrl}
              download
              className="text-primary-600 hover:text-primary-700 px-4 py-2 border border-primary-600 rounded-lg"
            >
              Download
            </a>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {isPDF ? (
            <iframe
              src={receiptUrl}
              className="w-full h-full min-h-[600px] border border-gray-200 rounded"
              title={`Receipt for transaction ${transactionId}`}
            />
          ) : (
            <img
              src={receiptUrl}
              alt={`Receipt for transaction ${transactionId}`}
              className="max-w-full h-auto mx-auto"
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default Accounts
