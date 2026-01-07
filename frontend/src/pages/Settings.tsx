import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  Settings as SettingsIcon,
  Globe,
  Server,
  MessageSquare,
  Tag,
  Shield,
  Download,
  Key
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type Tab = 'general' | 'federation' | 'mirrors' | 'telegram' | 'categories' | 'security'

function Settings() {
  const [activeTab, setActiveTab] = useState<Tab>('general')

  const tabs = [
    { id: 'general', label: 'Allgemein', icon: SettingsIcon },
    { id: 'federation', label: 'Federation', icon: Globe },
    { id: 'mirrors', label: 'Mirror Instanzen', icon: Server },
    { id: 'telegram', label: 'Telegram Bot', icon: MessageSquare },
    { id: 'categories', label: 'Kategorien', icon: Tag },
    { id: 'security', label: 'Sicherheit', icon: Shield },
  ]

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Einstellungen</h1>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as Tab)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5 mr-2" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white shadow rounded-lg p-6">
        {activeTab === 'general' && <GeneralSettings />}
        {activeTab === 'federation' && <FederationSettings />}
        {activeTab === 'mirrors' && <MirrorSettings />}
        {activeTab === 'telegram' && <TelegramSettings />}
        {activeTab === 'categories' && <CategorySettings />}
        {activeTab === 'security' && <SecuritySettings />}
      </div>
    </div>
  )
}

// General Settings Component
function GeneralSettings() {
  const { data: currencies } = useQuery({
    queryKey: ['currencies'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/settings/currencies`)
      return res.data
    },
  })

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Allgemeine Einstellungen</h2>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">Standardwährung</label>
          <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500">
            {currencies && Object.entries(currencies.currencies).map(([code, curr]: [string, any]) => (
              <option key={code} value={code}>
                {curr.symbol} {code} - {curr.name}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">
            {currencies && Object.keys(currencies.currencies).length} Währungen verfügbar
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Datumsformat</label>
          <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500">
            <option value="DD.MM.YYYY">DD.MM.YYYY (07.12.2024)</option>
            <option value="MM/DD/YYYY">MM/DD/YYYY (12/07/2024)</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD (2024-12-07)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Sprache</label>
          <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
            <option value="de">Deutsch</option>
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="it">Italiano</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Theme</label>
          <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
            <option value="light">Hell</option>
            <option value="dark">Dunkel</option>
            <option value="auto">System</option>
          </select>
        </div>
      </div>

      <div className="flex items-center">
        <input type="checkbox" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
        <label className="ml-2 block text-sm text-gray-900">Email-Benachrichtigungen aktivieren</label>
      </div>

      <button className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700">
        Speichern
      </button>
    </div>
  )
}

// Federation Settings Component
function FederationSettings() {
  const [testUrl, setTestUrl] = useState('')

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Federation Einstellungen</h2>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">🔐 Deine Instanz</h3>
        <p className="text-sm text-blue-700 mb-2">
          Domain: <code className="bg-blue-100 px-2 py-1 rounded">money.babsyit.ch</code>
        </p>
        <p className="text-sm text-blue-700">Status: ✅ Aktiviert</p>
      </div>

      <div>
        <h3 className="font-medium mb-2">RSA Key-Pair</h3>
        <p className="text-sm text-gray-600 mb-4">
          Dein Public Key wird über <code>/.well-known/money-instance</code> veröffentlicht
        </p>
        <button className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700">
          <Key className="inline w-4 h-4 mr-2" />
          Neue Keys generieren
        </button>
        <p className="text-xs text-gray-500 mt-2">⚠️ Achtung: Alte Signaturen werden ungültig!</p>
      </div>

      <div>
        <h3 className="font-medium mb-2">Verbindung testen</h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={testUrl}
            onChange={(e) => setTestUrl(e.target.value)}
            placeholder="https://money.example.com"
            className="flex-1 rounded-md border-gray-300 shadow-sm"
          />
          <button className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700">
            Testen
          </button>
        </div>
      </div>
    </div>
  )
}

// Mirror Settings Component
function MirrorSettings() {
  const [showAddForm, setShowAddForm] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Mirror Instanzen</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700"
        >
          + Mirror hinzufügen
        </button>
      </div>

      {showAddForm && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h3 className="font-medium">Neue Mirror Instanz</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700">URL</label>
            <input
              type="text"
              placeholder="https://mirror.example.com"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Priorität</label>
              <input type="number" defaultValue={2} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
              <p className="text-xs text-gray-500 mt-1">1 = Primary, 2+ = Secondary</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Sync Richtung</label>
              <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                <option value="bidirectional">↔️ Bidirektional</option>
                <option value="push">→ Push Only</option>
                <option value="pull">← Pull Only</option>
              </select>
            </div>
          </div>
          <button className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700">
            Hinzufügen
          </button>
        </div>
      )}

      <div className="text-center py-12 text-gray-500">
        <Server className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p>Keine Mirror Instanzen konfiguriert</p>
        <p className="text-sm mt-2">Füge eine Mirror Instanz für automatisches Backup hinzu</p>
      </div>
    </div>
  )
}

// Telegram Settings Component
function TelegramSettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Telegram Bot Einstellungen</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700">Bot Token</label>
        <input
          type="password"
          value="***************"
          readOnly
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-50"
        />
        <p className="text-xs text-gray-500 mt-1">Token wird in Environment Variables gespeichert</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Erlaubte User IDs</label>
        <p className="text-gray-500 italic">Keine User IDs konfiguriert (alle erlaubt)</p>
      </div>

      <div className="flex items-center">
        <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
        <label className="ml-2 block text-sm text-gray-900">OCR für Rechnungen aktivieren (Tesseract)</label>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-medium text-yellow-900 mb-2">⚠️ Setup Anleitung</h3>
        <ol className="text-sm text-yellow-800 space-y-2 list-decimal list-inside">
          <li>Erstelle Bot mit <a href="https://t.me/botfather" target="_blank" className="underline">@BotFather</a></li>
          <li>Kopiere Token in <code className="bg-yellow-100 px-1">.env</code> als <code className="bg-yellow-100 px-1">TELEGRAM_BOT_TOKEN</code></li>
          <li>Hole deine User ID von <a href="https://t.me/userinfobot" target="_blank" className="underline">@userinfobot</a></li>
          <li>Füge User ID zu <code className="bg-yellow-100 px-1">TELEGRAM_ALLOWED_USERS</code> hinzu</li>
          <li>Restart: <code className="bg-yellow-100 px-1">docker compose restart telegram-bot</code></li>
        </ol>
      </div>
    </div>
  )
}

// Category Settings Component
function CategorySettings() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Kategorie EasyTax Mapping</h2>
        <button className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700">
          + Kategorie hinzufügen
        </button>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">📊 EasyTax Export</h3>
        <p className="text-sm text-blue-700 mb-2">
          Mappe deine Kategorien zu EasyTax-Codes für automatischen Steuer-Export
        </p>
        <button className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
          <Download className="inline w-4 h-4 mr-1" />
          CSV Exportieren
        </button>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-medium mb-2">Standard Kategorien</h3>
        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
          <div>• Miete & Nebenkosten</div>
          <div>• Versicherungen</div>
          <div>• Verpflegung</div>
          <div>• Transport & Mobilität</div>
          <div>• Gesundheit</div>
          <div>• Bildung & Weiterbildung</div>
        </div>
      </div>
    </div>
  )
}

// Security Settings Component
function SecuritySettings() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Sicherheitseinstellungen</h2>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="font-medium text-green-900 mb-2">🔐 Passkey Authentication (WebAuthn)</h3>
        <p className="text-sm text-green-700 mb-4">
          Sichere biometrische Anmeldung mit Face ID, Touch ID oder Hardware Keys
        </p>
        <div className="flex items-center mb-4">
          <input type="checkbox" className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded" />
          <label className="ml-2 block text-sm text-green-900 font-medium">
            Passkey Authentication aktivieren
          </label>
        </div>
        <p className="text-xs text-green-600">Aktiviere Passkeys für höhere Sicherheit</p>
      </div>

      <div>
        <h3 className="font-medium mb-2">Bestätigung erforderlich für</h3>
        <div className="space-y-2">
          <div className="flex items-center">
            <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
            <label className="ml-2 block text-sm text-gray-900">📲 Telegram Bot Einträge</label>
          </div>
          <div className="flex items-center">
            <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
            <label className="ml-2 block text-sm text-gray-900">🌐 Federation Rechnungen</label>
          </div>
          <div className="flex items-center">
            <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
            <label className="ml-2 block text-sm text-gray-900">📄 CSV Import Einträge</label>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Session Timeout</label>
        <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
          <option value="30">30 Minuten</option>
          <option value="60">1 Stunde</option>
          <option value="240">4 Stunden</option>
          <option value="1440">24 Stunden</option>
        </select>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-medium text-yellow-900 mb-2">⚠️ Sicherheitshinweise</h3>
        <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
          <li>Verwende HTTPS in Production (Traefik + Let's Encrypt)</li>
          <li>Sichere Private Keys in <code className="bg-yellow-100 px-1">/app/secrets</code></li>
          <li>Aktiviere Firewall (nur Port 80/443)</li>
          <li>Regelmäßige Database Backups</li>
          <li>Rate Limiting für API aktivieren</li>
        </ul>
      </div>
    </div>
  )
}

export default Settings
