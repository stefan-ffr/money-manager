import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { AlertCircle, CheckCircle, Clock } from 'lucide-react'

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

function TransactionList() {
  const queryClient = useQueryClient()

  const { data: transactions, isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: async () => {
      const res = await axios.get<Transaction[]>(`${API_URL}/api/v1/transactions`)
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
      <h2 className="text-2xl font-bold text-gray-900">Transaktionen</h2>
      
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
            {transactions?.map((tx) => (
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
    </div>
  )
}

export default TransactionList
