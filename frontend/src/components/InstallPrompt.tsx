import { useState, useEffect } from 'react'
import { X, Download, Smartphone } from 'lucide-react'
import {
  setupInstallPrompt,
  showInstallPrompt,
  isAppInstalled,
  isIOS,
  getInstallInstructions,
  type BeforeInstallPromptEvent,
} from '../services/pwa'

function InstallPrompt() {
  const [showBanner, setShowBanner] = useState(false)
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    // Don't show if already installed or dismissed
    if (isAppInstalled() || sessionStorage.getItem('installPromptDismissed')) {
      return
    }

    // Setup install prompt listener
    setupInstallPrompt((prompt) => {
      setDeferredPrompt(prompt)
      setShowBanner(true)
    })

    // For iOS, show manual instructions after a delay
    if (isIOS() && !isAppInstalled()) {
      const timer = setTimeout(() => {
        if (!sessionStorage.getItem('installPromptDismissed')) {
          setShowBanner(true)
        }
      }, 3000) // Show after 3 seconds

      return () => clearTimeout(timer)
    }
  }, [])

  const handleInstall = async () => {
    if (deferredPrompt) {
      const outcome = await showInstallPrompt()

      if (outcome === 'accepted') {
        setShowBanner(false)
      }
    }
  }

  const handleDismiss = () => {
    setShowBanner(false)
    setDismissed(true)
    sessionStorage.setItem('installPromptDismissed', 'true')
  }

  if (!showBanner || dismissed) {
    return null
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6 pointer-events-none">
      <div className="max-w-md mx-auto pointer-events-auto">
        <div className="bg-white rounded-lg shadow-2xl border border-gray-200 overflow-hidden">
          <div className="p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                  {isIOS() ? (
                    <Smartphone className="h-6 w-6 text-blue-600" />
                  ) : (
                    <Download className="h-6 w-6 text-blue-600" />
                  )}
                </div>
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-sm font-semibold text-gray-900">
                  Money Manager installieren
                </h3>
                <p className="mt-1 text-sm text-gray-600">
                  {isIOS()
                    ? getInstallInstructions()
                    : 'Installiere die App für schnellen Zugriff und Offline-Nutzung'}
                </p>
              </div>
              <button
                onClick={handleDismiss}
                className="ml-4 flex-shrink-0 inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {!isIOS() && deferredPrompt && (
              <div className="mt-4 flex space-x-3">
                <button
                  onClick={handleInstall}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Jetzt installieren
                </button>
                <button
                  onClick={handleDismiss}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  Später
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default InstallPrompt
