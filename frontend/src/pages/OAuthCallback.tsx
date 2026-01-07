import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { handleOAuthCallback } from '../services/auth'
import { AlertCircle, Loader2 } from 'lucide-react'

function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')

      if (!code || !state) {
        setError('Ungültige OAuth-Antwort. Code oder State fehlt.')
        return
      }

      try {
        await handleOAuthCallback(code, state)
        // Successfully authenticated, redirect to dashboard
        navigate('/')
      } catch (err: any) {
        setError(err.message || 'OAuth-Authentifizierung fehlgeschlagen')
      }
    }

    processCallback()
  }, [searchParams, navigate])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
            <AlertCircle className="h-6 w-6 text-red-600" />
          </div>
          <h2 className="mt-4 text-center text-xl font-semibold text-gray-900">
            Authentifizierung fehlgeschlagen
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">{error}</p>
          <div className="mt-6">
            <button
              onClick={() => navigate('/login')}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Zurück zum Login
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto" />
        <h2 className="mt-4 text-xl font-semibold text-gray-900">
          Authentifizierung läuft...
        </h2>
        <p className="mt-2 text-sm text-gray-600">
          Bitte warten Sie, während wir Ihre Anmeldung verarbeiten.
        </p>
      </div>
    </div>
  )
}

export default OAuthCallback
