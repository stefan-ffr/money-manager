import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Repeat, Plus, Trash2, Play, X } from 'lucide-react'
import { formatCurrency } from '../lib/currencies'

const API_URL = import.meta.env.VITE_API_URL || ''

interface Account {
  id: number
  name: string
  currency: string
}

interface Recurring {
  id: number
  account_id: number
  amount: number
  category: string | null
  description: string | null
  interval: string
  next_run: string
  last_run: string | null
  active: boolean
}

const INTERVAL_LABELS: Record<string, string> = {
  daily: 'Täglich',
  weekly: 'Wöchentlich',
  monthly: 'Monatlich',
  yearly: 'Jährlich',
}

function Recurring() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const today = new Date().toISOString().split('T')[0]
  const [form, setForm] = useState({
    account_id: '',
    type: 'expense',
    amount: '',
    description: '',
    category: '',
    interval: 'monthly',
    next_run: today,
  })

  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts/`)
      return res.data as Account[]
    },
  })

  const { data: rules } = useQuery({
    queryKey: ['recurring'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/recurring/`)
      return res.data as Recurring[]
    },
  })

  const currencyByAccount: Record<number, string> = {}
  accounts?.forEach((a) => { currencyByAccount[a.id] = a.currency })
  const accountName: Record<number, string> = {}
  accounts?.forEach((a) => { accountName[a.id] = a.name })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['recurring'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
  }

  const createMutation = useMutation({
    mutationFn: async () => {
      const amount = form.type === 'expense'
        ? -Math.abs(parseFloat(form.amount))
        : Math.abs(parseFloat(form.amount))
      await axios.post(`${API_URL}/api/v1/recurring/`, {
        account_id: Number(form.account_id),
        amount,
        description: form.description || null,
        category: form.category || null,
        interval: form.interval,
        next_run: form.next_run,
        active: true,
      })
    },
    onSuccess: () => {
      invalidate()
      setShowForm(false)
      setForm({ account_id: '', type: 'expense', amount: '', description: '', category: '', interval: 'monthly', next_run: today })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => { await axios.delete(`${API_URL}/api/v1/recurring/${id}`) },
    onSuccess: invalidate,
  })

  const toggleMutation = useMutation({
    mutationFn: async (rule: Recurring) => {
      await axios.put(`${API_URL}/api/v1/recurring/${rule.id}`, { active: !rule.active })
    },
    onSuccess: invalidate,
  })

  const processMutation = useMutation({
    mutationFn: async () => {
      const res = await axios.post(`${API_URL}/api/v1/recurring/process`)
      return res.data as { created: number }
    },
    onSuccess: invalidate,
  })

  const canSubmit = form.account_id && parseFloat(form.amount) > 0

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Repeat className="w-7 h-7" /> Dauerbuchungen
        </h1>
        <div className="flex gap-2">
          <button
            onClick={() => processMutation.mutate()}
            disabled={processMutation.isPending}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-1 disabled:opacity-50"
            title="Fällige Dauerbuchungen jetzt erzeugen"
          >
            <Play className="w-4 h-4" />
            Fällige jetzt buchen
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 flex items-center gap-1"
          >
            <Plus className="w-4 h-4" /> Neue Dauerbuchung
          </button>
        </div>
      </div>

      {processMutation.data && (
        <div className="mb-4 text-sm bg-green-50 border border-green-200 text-green-800 rounded-md px-4 py-2">
          {processMutation.data.created} fällige Buchung(en) erstellt.
        </div>
      )}

      {showForm && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Neue Dauerbuchung</h2>
            <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Konto *</label>
              <select
                value={form.account_id}
                onChange={(e) => setForm({ ...form, account_id: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="">Bitte wählen…</option>
                {accounts?.map((a) => <option key={a.id} value={a.id}>{a.name} ({a.currency})</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Typ</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="expense">Ausgabe</option>
                <option value="income">Einnahme</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Betrag *</label>
              <input
                type="number" step="0.01" min="0"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Intervall</label>
              <select
                value={form.interval}
                onChange={(e) => setForm({ ...form, interval: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                {Object.entries(INTERVAL_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nächste Ausführung *</label>
              <input
                type="date"
                value={form.next_run}
                onChange={(e) => setForm({ ...form, next_run: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kategorie</label>
              <input
                type="text"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Beschreibung</label>
              <input
                type="text"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="z. B. Miete, Abo, Gehalt"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-4">
            <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
              Abbrechen
            </button>
            <button
              onClick={() => createMutation.mutate()}
              disabled={!canSubmit || createMutation.isPending}
              className="px-4 py-2 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              Speichern
            </button>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg overflow-hidden">
        {!rules || rules.length === 0 ? (
          <p className="text-gray-600 p-8 text-center">
            Noch keine Dauerbuchungen. Lege z. B. Miete, Abos oder das Gehalt als wiederkehrende Buchung an.
          </p>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-500">Beschreibung</th>
                <th className="px-4 py-2 text-left font-medium text-gray-500">Konto</th>
                <th className="px-4 py-2 text-left font-medium text-gray-500">Intervall</th>
                <th className="px-4 py-2 text-left font-medium text-gray-500">Nächste</th>
                <th className="px-4 py-2 text-right font-medium text-gray-500">Betrag</th>
                <th className="px-4 py-2 text-center font-medium text-gray-500">Aktiv</th>
                <th className="px-4 py-2 text-right font-medium text-gray-500 w-16"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rules.map((r) => (
                <tr key={r.id} className={r.active ? '' : 'opacity-50'}>
                  <td className="px-4 py-2 text-gray-900">{r.description || r.category || 'Dauerbuchung'}</td>
                  <td className="px-4 py-2 text-gray-600">{accountName[r.account_id] || r.account_id}</td>
                  <td className="px-4 py-2 text-gray-600">{INTERVAL_LABELS[r.interval] || r.interval}</td>
                  <td className="px-4 py-2 text-gray-600">{r.next_run}</td>
                  <td className={`px-4 py-2 text-right font-semibold ${r.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {formatCurrency(r.amount, currencyByAccount[r.account_id] || 'CHF')}
                  </td>
                  <td className="px-4 py-2 text-center">
                    <input
                      type="checkbox"
                      checked={r.active}
                      onChange={() => toggleMutation.mutate(r)}
                      className="h-4 w-4 text-primary-600 border-gray-300 rounded"
                    />
                  </td>
                  <td className="px-4 py-2 text-right">
                    <button
                      onClick={() => { if (confirm('Dauerbuchung löschen?')) deleteMutation.mutate(r.id) }}
                      className="text-red-600 hover:text-red-800"
                      title="Löschen"
                    >
                      <Trash2 className="w-4 h-4 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Recurring
