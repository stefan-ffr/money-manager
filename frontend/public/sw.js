// Money Manager - Service Worker
// Provides offline support and caching for PWA

const CACHE_NAME = 'money-manager-v1.0.0'
const API_CACHE_NAME = 'money-manager-api-v1.0.0'

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...')
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Caching static assets')
      return cache.addAll(STATIC_ASSETS)
    }).then(() => {
      console.log('[ServiceWorker] Skip waiting')
      return self.skipWaiting()
    })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...')
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => {
            return name !== CACHE_NAME && name !== API_CACHE_NAME
          })
          .map((name) => {
            console.log('[ServiceWorker] Deleting old cache:', name)
            return caches.delete(name)
          })
      )
    }).then(() => {
      console.log('[ServiceWorker] Claiming clients')
      return self.clients.claim()
    })
  )
})

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return
  }

  // API requests - network first with cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Clone response and cache it
          const responseClone = response.clone()
          caches.open(API_CACHE_NAME).then((cache) => {
            cache.put(request, responseClone)
          })
          return response
        })
        .catch(() => {
          // Network failed, try cache
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse
            }
            // Return offline page or error
            return new Response(
              JSON.stringify({ error: 'Offline - keine Verbindung möglich' }),
              {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
              }
            )
          })
        })
    )
    return
  }

  // Static assets - cache first with network fallback
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        // Return cached version and update cache in background
        fetch(request).then((response) => {
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, response)
          })
        }).catch(() => {
          // Ignore network errors in background update
        })
        return cachedResponse
      }

      // Not in cache, fetch from network
      return fetch(request)
        .then((response) => {
          // Cache the new resource
          const responseClone = response.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone)
          })
          return response
        })
        .catch((error) => {
          console.log('[ServiceWorker] Fetch failed:', error)
          // Return offline page if navigation request
          if (request.mode === 'navigate') {
            return caches.match('/index.html')
          }
          throw error
        })
    })
  )
})

// Background sync for offline actions (future enhancement)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncTransactions())
  }
})

async function syncTransactions() {
  // TODO: Implement background sync for offline-created transactions
  console.log('[ServiceWorker] Background sync triggered')
}

// Push notifications support (future enhancement)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Neue Benachrichtigung',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    vibrate: [200, 100, 200]
  }

  event.waitUntil(
    self.registration.showNotification('Money Manager', options)
  )
})
