import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Upload,
  ArrowRight,
  Edit,
  Trash,
  Plus,
  Link as LinkIcon
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type MatchStatus = 'matched' | 'unmatched_bank' | 'unmatched_app' | 'pending'

interface Match {
  id: number
  bank_date: string
  bank_amount: number
  bank_description: string
  bank_reference: string
  match_status: MatchStatus
  match_confidence: number
  match_type: string | null
  action: string | null
  user_notes: string | null
  transaction: {
    id: number
    date: string
    amount: number
    description: string
    category: string | null
  } | null
}

interface Reconciliation {
  id: number
  account_id: number
  period_start: string
  period_end: string
  bank_balance: number | null
  app_balance: number | null
  difference: number | null
  status: string
  total_bank_transactions: number
  matched_count: number
  unmatched_bank_count: number
  unmatched_app_count: number
  created_at: string
  matches: Match[]
}

function Reconciliation() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadForm, setUploadForm] = useState({
    account_id: '',
    period_start: '',
    period_end: '',
    bank_balance: ''
  })
  const [selectedReconciliation, setSelectedReconciliation] = useState<number | null>(null)
  const [editingMatch, setEditingMatch] = useState<number | null>(null)

  const queryClient = useQueryClient()

  // Fetch accounts
  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts`)
      return res.data
    }
  })

  // Fetch reconciliations
  const { data: reconciliations } = useQuery({
    queryKey: ['reconciliations'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/reconciliation`)
      return res.data
    }
  })

  // Fetch selected reconciliation details
  const { data: reconciliationDetail } = useQuery({
    queryKey: ['reconciliation', selectedReconciliation],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/reconciliation/${selectedReconciliation}`)
      return res.data
    },
    enabled: !!selectedReconciliation
  })

  // Upload CSV mutation
  const uploadMutation = useMutation({
    mutationFn: async () => {
      const formData = new FormData()
      formData.append('file', selectedFile!)
      formData.append('account_id', uploadForm.account_id)
      formData.append('period_start', uploadForm.period_start)
      formData.append('period_end', uploadForm.period_end)
      if (uploadForm.bank_balance) {
        formData.append('bank_balance', uploadForm.bank_balance)
      }

      const res = await axios.post(`${API_URL}/api/v1/reconciliation`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return res.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['reconciliations'] })
      setSelectedReconciliation(data.id)
      setSelectedFile(null)
      setUploadForm({ account_id: '', period_start: '', period_end: '', bank_balance: '' })
      alert(`Reconciliation erstellt: ${data.matched_count} matched, ${data.unmatched_bank_count} unmatched`)
    },
    onError: (error: any) => {
      alert(`Fehler: ${error.response?.data?.detail || error.message}`)
    }
  })

  // Resolve match mutation
  const resolveMutation = useMutation({
    mutationFn: async ({ reconciliationId, matchId, action, transactionData, notes }: any) => {
      const res = await axios.post(
        `${API_URL}/api/v1/reconciliation/${reconciliationId}/resolve/${matchId}`,
        { action, transaction_data: transactionData, notes }
      )
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reconciliation', selectedReconciliation] })
      setEditingMatch(null)
    },
    onError: (error: any) => {
      alert(`Fehler: ${error.response?.data?.detail || error.message}`)
    }
  })

  const handleUpload = () => {
    if (!selectedFile || !uploadForm.account_id || !uploadForm.period_start || !uploadForm.period_end) {
      alert('Bitte alle Pflichtfelder ausfüllen')
      return
    }
    uploadMutation.mutate()
  }

  const handleResolve = (matchId: number, action: string, transactionData?: any, notes?: string) => {
    resolveMutation.mutate({
      reconciliationId: selectedReconciliation,
      matchId,
      action,
      transactionData,
      notes
    })
  }

  const getMatchColor = (match: Match) => {
    if (match.match_status === 'matched' && match.match_confidence >= 90) {
      return 'bg-green-50 border-green-200'
    } else if (match.match_status === 'matched' && match.match_confidence >= 70) {
      return 'bg-yellow-50 border-yellow-200'
    } else {
      return 'bg-red-50 border-red-200'
    }
  }

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 90) return <CheckCircle className="w-5 h-5 text-green-600" />
    if (confidence >= 70) return <AlertCircle className="w-5 h-5 text-yellow-600" />
    return <XCircle className="w-5 h-5 text-red-600" />
  }

  if (!selectedReconciliation) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Kontenabstimmung</h1>

        {/* Upload Form */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Neue Abstimmung starten</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Konto *</label>
              <select
                value={uploadForm.account_id}
                onChange={(e) => setUploadForm({ ...uploadForm, account_id: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="">Konto wählen...</option>
                {accounts?.map((account: any) => (
                  <option key={account.id} value={account.id}>
                    {account.name} ({account.type})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Zeitraum von *</label>
              <input
                type="date"
                value={uploadForm.period_start}
                onChange={(e) => setUploadForm({ ...uploadForm, period_start: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Zeitraum bis *</label>
              <input
                type="date"
                value={uploadForm.period_end}
                onChange={(e) => setUploadForm({ ...uploadForm, period_end: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Bank Saldo (optional)</label>
              <input
                type="number"
                step="0.01"
                value={uploadForm.bank_balance}
                onChange={(e) => setUploadForm({ ...uploadForm, bank_balance: e.target.value })}
                placeholder="z.B. 1234.56"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Bank CSV Datei *</label>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            />
            {selectedFile && (
              <p className="text-sm text-gray-600 mt-2">📄 {selectedFile.name}</p>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={uploadMutation.isPending}
            className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700 flex items-center gap-2 disabled:opacity-50"
          >
            <Upload className="w-4 h-4" />
            {uploadMutation.isPending ? 'Verarbeite...' : 'Abstimmung starten'}
          </button>
        </div>

        {/* Previous Reconciliations */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Bisherige Abstimmungen</h2>

          {reconciliations && reconciliations.length > 0 ? (
            <div className="space-y-2">
              {reconciliations.map((rec: any) => (
                <div
                  key={rec.id}
                  onClick={() => setSelectedReconciliation(rec.id)}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium">
                        {new Date(rec.period_start).toLocaleDateString('de-DE')} - {new Date(rec.period_end).toLocaleDateString('de-DE')}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Account ID: {rec.account_id} • Status: {rec.status}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="flex gap-2">
                        <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">
                          {rec.matched_count} ✓
                        </span>
                        <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-800">
                          {rec.unmatched_bank_count + rec.unmatched_app_count} ✗
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(rec.created_at).toLocaleDateString('de-DE')}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">Noch keine Abstimmungen vorhanden</p>
          )}
        </div>
      </div>
    )
  }

  // Reconciliation Detail View
  const rec: Reconciliation = reconciliationDetail

  if (!rec) {
    return <div>Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Abstimmung: {new Date(rec.period_start).toLocaleDateString('de-DE')} - {new Date(rec.period_end).toLocaleDateString('de-DE')}
        </h1>
        <button
          onClick={() => setSelectedReconciliation(null)}
          className="text-gray-600 hover:text-gray-800"
        >
          ← Zurück
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600">Total Bank</div>
          <div className="text-2xl font-bold">{rec.total_bank_transactions}</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-sm text-green-700">Gematched</div>
          <div className="text-2xl font-bold text-green-700">{rec.matched_count}</div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-sm text-red-700">Nur in Bank</div>
          <div className="text-2xl font-bold text-red-700">{rec.unmatched_bank_count}</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-sm text-yellow-700">Nur in App</div>
          <div className="text-2xl font-bold text-yellow-700">{rec.unmatched_app_count}</div>
        </div>
      </div>

      {rec.bank_balance !== null && rec.app_balance !== null && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-medium text-blue-900 mb-2">Saldo-Vergleich</h3>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-blue-700">Bank Saldo</div>
              <div className="font-bold">{rec.bank_balance.toFixed(2)} CHF</div>
            </div>
            <div>
              <div className="text-blue-700">App Saldo</div>
              <div className="font-bold">{rec.app_balance.toFixed(2)} CHF</div>
            </div>
            <div>
              <div className="text-blue-700">Differenz</div>
              <div className={`font-bold ${Math.abs(rec.difference || 0) < 0.01 ? 'text-green-600' : 'text-red-600'}`}>
                {rec.difference?.toFixed(2)} CHF
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Matches */}
      <div className="space-y-4">
        {rec.matches.map((match) => (
          <div
            key={match.id}
            className={`border rounded-lg p-4 ${getMatchColor(match)}`}
          >
            <div className="flex items-start gap-4">
              {/* Confidence Indicator */}
              <div className="flex-shrink-0 pt-1">
                {getConfidenceIcon(match.match_confidence)}
              </div>

              {/* Bank Transaction */}
              <div className="flex-1">
                <div className="font-medium text-gray-900">Bank Transaktion</div>
                <div className="text-sm text-gray-600">
                  {new Date(match.bank_date).toLocaleDateString('de-DE')}
                </div>
                <div className="text-lg font-semibold mt-1">
                  {match.bank_amount.toFixed(2)} CHF
                </div>
                <div className="text-sm text-gray-700 mt-1">{match.bank_description}</div>
                {match.bank_reference && (
                  <div className="text-xs text-gray-500 mt-1">Ref: {match.bank_reference}</div>
                )}
              </div>

              {/* Match Indicator */}
              {match.transaction && (
                <>
                  <div className="flex-shrink-0 flex items-center text-gray-400">
                    <ArrowRight className="w-6 h-6" />
                  </div>

                  {/* App Transaction */}
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">App Transaktion</div>
                    <div className="text-sm text-gray-600">
                      {new Date(match.transaction.date).toLocaleDateString('de-DE')}
                    </div>
                    <div className="text-lg font-semibold mt-1">
                      {match.transaction.amount.toFixed(2)} CHF
                    </div>
                    <div className="text-sm text-gray-700 mt-1">{match.transaction.description}</div>
                    {match.transaction.category && (
                      <div className="text-xs text-gray-500 mt-1">Kategorie: {match.transaction.category}</div>
                    )}
                    {match.match_type && (
                      <div className="text-xs text-blue-600 mt-1">
                        Match: {match.match_type} ({match.match_confidence}% Confidence)
                      </div>
                    )}
                  </div>
                </>
              )}

              {/* Actions */}
              <div className="flex-shrink-0">
                {match.action ? (
                  <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-700">
                    {match.action === 'accept' && '✓ Akzeptiert'}
                    {match.action === 'ignore' && '⊗ Ignoriert'}
                    {match.action === 'create_transaction' && '+ Erstellt'}
                  </span>
                ) : (
                  <div className="flex flex-col gap-2">
                    {match.transaction && (
                      <button
                        onClick={() => handleResolve(match.id, 'accept')}
                        className="text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                      >
                        ✓ Akzeptieren
                      </button>
                    )}
                    {!match.transaction && (
                      <>
                        <button
                          onClick={() => setEditingMatch(match.id)}
                          className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 flex items-center gap-1"
                        >
                          <Plus className="w-3 h-3" /> Erstellen
                        </button>
                        <button
                          onClick={() => handleResolve(match.id, 'ignore')}
                          className="text-xs bg-gray-400 text-white px-3 py-1 rounded hover:bg-gray-500"
                        >
                          ⊗ Ignorieren
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Create Transaction Form */}
            {editingMatch === match.id && (
              <div className="mt-4 pt-4 border-t border-gray-300">
                <h4 className="font-medium mb-3">Neue Transaktion erstellen</h4>
                <CreateTransactionForm
                  initialData={{
                    date: match.bank_date,
                    amount: match.bank_amount,
                    description: match.bank_description
                  }}
                  onSubmit={(data) => handleResolve(match.id, 'create_transaction', data)}
                  onCancel={() => setEditingMatch(null)}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function CreateTransactionForm({
  initialData,
  onSubmit,
  onCancel
}: {
  initialData: { date: string; amount: number; description: string }
  onSubmit: (data: any) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState({
    description: initialData.description,
    category: '',
    notes: ''
  })

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Beschreibung</label>
        <input
          type="text"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Kategorie</label>
        <input
          type="text"
          value={formData.category}
          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Notizen</label>
        <input
          type="text"
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>
      <div className="md:col-span-3 flex gap-2">
        <button
          onClick={() => onSubmit(formData)}
          className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700"
        >
          Erstellen
        </button>
        <button
          onClick={onCancel}
          className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        >
          Abbrechen
        </button>
      </div>
    </div>
  )
}

export default Reconciliation
