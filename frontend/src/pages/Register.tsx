import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerWithPasskey } from '../services/auth'
import { KeyRound, AlertCircle, CheckCircle } from 'lucide-react'

function Register() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [deviceName, setDeviceName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await registerWithPasskey(email, username, deviceName || undefined)
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Registrierung fehlgeschlagen')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Konto erstellen
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Mit Passkey registrieren
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleRegister}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                E-Mail-Adresse
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="deine@email.com"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Benutzername
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="benutzername"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="deviceName" className="block text-sm font-medium text-gray-700">
                Gerätename (optional)
              </label>
              <input
                id="deviceName"
                name="deviceName"
                type="text"
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="z.B. iPhone 15 Pro"
                disabled={loading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Hilft dir, deine Passkeys später zu identifizieren
              </p>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !email || !username}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                <KeyRound className="h-5 w-5 text-blue-500 group-hover:text-blue-400" />
              </span>
              {loading ? 'Registrierung läuft...' : 'Mit Passkey registrieren'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Bereits registriert?{' '}
              <Link
                to="/login"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Jetzt anmelden
              </Link>
            </p>
          </div>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">
                Vorteile von Passkeys
              </span>
            </div>
          </div>

          <div className="mt-6 text-sm text-gray-600 space-y-3">
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
              <div>
                <strong>Keine Passwörter:</strong> Nichts zu merken, nichts zu hacken
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
              <div>
                <strong>Biometrisch:</strong> Face ID, Touch ID oder Fingerabdruck
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
              <div>
                <strong>Sicher:</strong> Phishing-resistent und Hardware-gebunden
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
              <div>
                <strong>Multi-Device:</strong> Sync über iCloud/Google
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
