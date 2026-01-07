import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'
import { AuthProvider } from './hooks/useAuth'
import { setupAxiosInterceptor } from './services/auth'
import { registerServiceWorker } from './services/pwa'
import InstallPrompt from './components/InstallPrompt'

// Setup axios interceptor for automatic token injection
setupAxiosInterceptor()

// Register service worker for PWA functionality
if (import.meta.env.PROD) {
  registerServiceWorker()
}

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <App />
          <InstallPrompt />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
