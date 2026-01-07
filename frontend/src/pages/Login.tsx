import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { loginWithPasskey, loginWithOAuth, getOAuthConfig, type OAuthConfig } from '../services/auth'
import { KeyRound, AlertCircle, Shield } from 'lucide-react'

function Login() {
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [oauthConfig, setOauthConfig] = useState<OAuthConfig | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    // Load OAuth config on mount
    getOAuthConfig().then(setOauthConfig)
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await loginWithPasskey(username)
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Login fehlgeschlagen')
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthLogin = async () => {
    setError('')
    setLoading(true)
    try {
      await loginWithOAuth()
      // Will redirect to OAuth provider
    } catch (err: any) {
      setError(err.message || 'OAuth Login fehlgeschlagen')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Money Manager
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Mit Passkey anmelden
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
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

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                Benutzername
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Benutzername"
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !username}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                <KeyRound className="h-5 w-5 text-blue-500 group-hover:text-blue-400" />
              </span>
              {loading ? 'Anmeldung läuft...' : 'Mit Passkey anmelden'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Noch kein Konto?{' '}
              <Link
                to="/register"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Jetzt registrieren
              </Link>
            </p>
          </div>
        </form>

        {/* OAuth Login Option */}
        {oauthConfig?.enabled && (
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">Oder</span>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleOAuthLogin}
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Shield className="h-5 w-5 mr-2 text-green-600" />
                Mit SSO anmelden (Authentik/Keycloak)
              </button>
            </div>
          </div>
        )}

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">
                Was sind Passkeys?
              </span>
            </div>
          </div>

          <div className="mt-6 text-sm text-gray-600 space-y-2">
            <p>
              Passkeys sind eine sichere und einfache Möglichkeit, sich anzumelden:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Keine Passwörter zum Merken</li>
              <li>Biometrische Authentifizierung (Face ID, Touch ID, Fingerprint)</li>
              <li>Phishing-resistent und sicher</li>
              <li>Funktioniert auf allen deinen Geräten</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
