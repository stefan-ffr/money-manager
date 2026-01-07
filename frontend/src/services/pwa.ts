/**
 * PWA Service Worker Registration and Management
 */

export interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

let deferredPrompt: BeforeInstallPromptEvent | null = null

/**
 * Register service worker for PWA functionality
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | undefined> {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      })

      console.log('[PWA] Service Worker registered:', registration.scope)

      // Check for updates periodically
      setInterval(() => {
        registration.update()
      }, 60 * 60 * 1000) // Check every hour

      return registration
    } catch (error) {
      console.error('[PWA] Service Worker registration failed:', error)
    }
  } else {
    console.log('[PWA] Service Workers not supported in this browser')
  }
}

/**
 * Unregister service worker
 */
export async function unregisterServiceWorker(): Promise<boolean> {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.ready
    return registration.unregister()
  }
  return false
}

/**
 * Setup install prompt listener
 */
export function setupInstallPrompt(
  onPromptAvailable: (prompt: BeforeInstallPromptEvent) => void
): void {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt = e as BeforeInstallPromptEvent
    onPromptAvailable(deferredPrompt)
  })

  // Listen for successful install
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed successfully')
    deferredPrompt = null
  })
}

/**
 * Show install prompt
 */
export async function showInstallPrompt(): Promise<'accepted' | 'dismissed' | 'unavailable'> {
  if (!deferredPrompt) {
    return 'unavailable'
  }

  deferredPrompt.prompt()
  const { outcome } = await deferredPrompt.userChoice
  deferredPrompt = null

  return outcome
}

/**
 * Check if app is installed
 */
export function isAppInstalled(): boolean {
  // Check if running in standalone mode
  if (window.matchMedia('(display-mode: standalone)').matches) {
    return true
  }

  // Check iOS standalone mode
  if ((window.navigator as any).standalone === true) {
    return true
  }

  return false
}

/**
 * Check if device is iOS
 */
export function isIOS(): boolean {
  return (
    /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  )
}

/**
 * Check if PWA installation is supported
 */
export function isPWASupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window
}

/**
 * Get install instructions for current platform
 */
export function getInstallInstructions(): string {
  if (isIOS()) {
    return 'Tippe auf das Teilen-Symbol und wähle "Zum Home-Bildschirm"'
  }

  return 'Klicke auf das Installieren-Icon in der Adressleiste oder nutze das Menü deines Browsers'
}
