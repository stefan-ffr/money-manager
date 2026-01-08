import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  Upload,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Building2,
  Settings
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || ''

interface Bank {
  id: string
  name: string
  format: string
  encoding: string
  date_format: string
  decimal_separator: string
}

interface Account {
  id: number
  name: string
  type: string
  balance: string
  currency: string
  bank_name?: string
  bank_identifier?: string
  bank_import_enabled?: boolean
}

interface ImportResult {
  success: boolean
  bank?: string
  account_id?: number
  account_name?: string
  transactions_created?: number
  duplicates_skipped?: number
  total_parsed?: number
  error?: string
}

function BankImport() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedAccount, setSelectedAccount] = useState<string>('auto')
  const [showSetupModal, setShowSetupModal] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)
  const queryClient = useQueryClient()

  const { data: banks } = useQuery({
    queryKey: ['supported-banks'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/import/bank/supported`)
      return res.data.banks as Bank[]
    },
  })

  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts/`)
      return res.data as Account[]
    },
  })

  const importMutation = useMutation({
    mutationFn: async (data: { file: File; accountId?: number }) => {
      const formData = new FormData()
      formData.append('file', data.file)
      if (data.accountId) {
        formData.append('account_id', data.accountId.toString())
      }
      formData.append('auto_match', 'true')

      const res = await axios.post(`${API_URL}/api/v1/import/bank/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return res.data as ImportResult
    },
    onSuccess: (result) => {
      setImportResult(result)
      setSelectedFile(null)
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
    },
    onError: (error: any) => {
      setImportResult({
        success: false,
        error: error.response?.data?.detail || error.message,
      })
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
      setImportResult(null)
    }
  }

  const handleImport = () => {
    if (!selectedFile) return

    const accountId = selectedAccount === 'auto' ? undefined : Number(selectedAccount)
    importMutation.mutate({ file: selectedFile, accountId })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bank CSV Import</h1>
          <p className="text-gray-600 mt-1">
            Importieren Sie Bankauszüge von Schweizer Banken
          </p>
        </div>
        <button
          onClick={() => setShowSetupModal(true)}
          className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 flex items-center gap-2"
        >
          <Settings className="w-5 h-5" />
          Konto konfigurieren
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* File Upload */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">1. CSV Datei hochladen</h2>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="csv-upload"
              />
              <label
                htmlFor="csv-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="w-12 h-12 text-gray-400 mb-4" />
                <span className="text-lg font-medium text-gray-900 mb-1">
                  {selectedFile ? selectedFile.name : 'CSV Datei auswählen'}
                </span>
                <span className="text-sm text-gray-500">
                  oder Datei hierher ziehen
                </span>
              </label>
            </div>

            {selectedFile && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-900">{selectedFile.name}</p>
                    <p className="text-xs text-blue-600">
                      {(selectedFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <XCircle className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Account Selection */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">2. Konto auswählen</h2>

            <div className="space-y-4">
              <label className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary-500">
                <input
                  type="radio"
                  name="account"
                  value="auto"
                  checked={selectedAccount === 'auto'}
                  onChange={(e) => setSelectedAccount(e.target.value)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500"
                />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Automatisch erkennen</p>
                  <p className="text-sm text-gray-500">
                    System erkennt Konto anhand IBAN im CSV (empfohlen)
                  </p>
                </div>
              </label>

              {accounts?.map((account) => (
                <label
                  key={account.id}
                  className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary-500"
                >
                  <input
                    type="radio"
                    name="account"
                    value={account.id.toString()}
                    checked={selectedAccount === account.id.toString()}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{account.name}</p>
                    <p className="text-sm text-gray-500">
                      {account.bank_name ? (
                        <>
                          {account.bank_name}
                          {account.bank_identifier && ` - ${account.bank_identifier}`}
                          {account.bank_import_enabled && (
                            <span className="ml-2 text-green-600">✓ Konfiguriert</span>
                          )}
                        </>
                      ) : (
                        <span className="text-orange-600">Nicht konfiguriert</span>
                      )}
                    </p>
                  </div>
                </label>
              ))}
            </div>

            <button
              onClick={handleImport}
              disabled={!selectedFile || importMutation.isPending}
              className="w-full mt-6 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Upload className="w-5 h-5" />
              {importMutation.isPending ? 'Importiere...' : 'CSV Importieren'}
            </button>
          </div>

          {/* Import Result */}
          {importResult && (
            <div
              className={`shadow rounded-lg p-6 ${
                importResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
              }`}
            >
              <div className="flex items-start gap-3">
                {importResult.success ? (
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <h3
                    className={`text-lg font-semibold ${
                      importResult.success ? 'text-green-900' : 'text-red-900'
                    }`}
                  >
                    {importResult.success ? 'Import erfolgreich!' : 'Import fehlgeschlagen'}
                  </h3>
                  {importResult.success ? (
                    <div className="mt-2 space-y-1 text-sm text-green-700">
                      <p>Bank: {importResult.bank}</p>
                      <p>Konto: {importResult.account_name}</p>
                      <p>
                        <strong>{importResult.transactions_created}</strong> Transaktionen erstellt
                      </p>
                      {importResult.duplicates_skipped! > 0 && (
                        <p className="text-orange-600">
                          {importResult.duplicates_skipped} Duplikate übersprungen
                        </p>
                      )}
                      <p className="text-xs mt-2">
                        Alle importierten Transaktionen sind rot markiert und müssen bestätigt werden.
                      </p>
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-red-700">{importResult.error}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Info Sidebar */}
        <div className="space-y-6">
          {/* Supported Banks */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Unterstützte Banken</h2>
            <div className="space-y-3">
              {banks?.map((bank) => (
                <div key={bank.id} className="flex items-start gap-3">
                  <Building2 className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-900">{bank.name}</p>
                    <p className="text-xs text-gray-500">{bank.format}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start gap-2 mb-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <h3 className="font-semibold text-blue-900">Anleitung</h3>
            </div>
            <ol className="space-y-2 text-sm text-blue-800 list-decimal list-inside">
              <li>Bankauszug als CSV exportieren</li>
              <li>CSV-Datei hier hochladen</li>
              <li>Konto auswählen (oder Auto-Erkennung)</li>
              <li>Import starten</li>
              <li>Transaktionen in der Liste bestätigen</li>
            </ol>
            <div className="mt-4 pt-4 border-t border-blue-200">
              <p className="text-xs text-blue-700">
                <strong>Tipp:</strong> Konfigurieren Sie Ihre Konten mit IBAN für automatische
                Erkennung.
              </p>
            </div>
          </div>
        </div>
      </div>

      {showSetupModal && (
        <BankSetupModal
          accounts={accounts || []}
          banks={banks || []}
          onClose={() => setShowSetupModal(false)}
          onSuccess={() => {
            setShowSetupModal(false)
            queryClient.invalidateQueries({ queryKey: ['accounts'] })
          }}
        />
      )}
    </div>
  )
}

interface BankSetupModalProps {
  accounts: Account[]
  banks: Bank[]
  onClose: () => void
  onSuccess: () => void
}

function BankSetupModal({ accounts, banks, onClose, onSuccess }: BankSetupModalProps) {
  const [formData, setFormData] = useState({
    account_id: accounts[0]?.id || '',
    bank_name: '',
    bank_identifier: '',
    enable_auto_import: true,
  })

  const setupMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      await axios.post(`${API_URL}/api/v1/import/bank/setup`, {
        account_id: Number(data.account_id),
        bank_name: data.bank_name,
        bank_identifier: data.bank_identifier,
        enable_auto_import: data.enable_auto_import,
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
    setupMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Konto für Import konfigurieren</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Konto *</label>
            <select
              value={formData.account_id}
              onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            >
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bank *</label>
            <select
              value={formData.bank_name}
              onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            >
              <option value="">-- Bank auswählen --</option>
              {banks.map((bank) => (
                <option key={bank.id} value={bank.name}>
                  {bank.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              IBAN oder Kontonummer *
            </label>
            <input
              type="text"
              value={formData.bank_identifier}
              onChange={(e) => setFormData({ ...formData, bank_identifier: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 font-mono"
              placeholder="CH93 0076 2011 6238 5295 7"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Wird verwendet, um das Konto beim CSV Import automatisch zu erkennen
            </p>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.enable_auto_import}
              onChange={(e) =>
                setFormData({ ...formData, enable_auto_import: e.target.checked })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-900">
              Auto-Import aktivieren
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={setupMutation.isPending}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {setupMutation.isPending ? 'Speichern...' : 'Speichern'}
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

export default BankImport
