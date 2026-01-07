import axios from 'axios'
import { startRegistration, startAuthentication } from '@simplewebauthn/browser'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
}

/**
 * Register a new user with Passkey authentication
 */
export async function registerWithPasskey(
  email: string,
  username: string,
  deviceName?: string
): Promise<AuthTokens> {
  try {
    // 1. Start registration - get options from server
    const beginResponse = await axios.post(`${API_URL}/api/v1/auth/register/begin`, {
      email,
      username,
    })

    const { user_id, options } = beginResponse.data
    const parsedOptions = JSON.parse(options)

    // 2. Trigger browser Passkey registration
    const credential = await startRegistration(parsedOptions)

    // 3. Complete registration - send credential to server
    const completeResponse = await axios.post(`${API_URL}/api/v1/auth/register/complete`, {
      user_id,
      credential,
      device_name: deviceName,
    })

    const tokens: AuthTokens = {
      access_token: completeResponse.data.access_token,
      token_type: completeResponse.data.token_type,
    }

    // Store token in localStorage
    localStorage.setItem('access_token', tokens.access_token)

    return tokens
  } catch (error: any) {
    console.error('Registration failed:', error)
    throw new Error(
      error.response?.data?.detail || 'Registration failed. Please try again.'
    )
  }
}

/**
 * Login with Passkey authentication
 */
export async function loginWithPasskey(username: string): Promise<AuthTokens> {
  try {
    // 1. Start authentication - get challenge from server
    const beginResponse = await axios.post(`${API_URL}/api/v1/auth/login/begin`, {
      username,
    })

    const { options } = beginResponse.data
    const parsedOptions = JSON.parse(options)

    // 2. Authenticate with Passkey (browser prompts for biometric/PIN)
    const credential = await startAuthentication(parsedOptions)

    // 3. Complete authentication - verify and get token
    const completeResponse = await axios.post(`${API_URL}/api/v1/auth/login/complete`, {
      username,
      credential,
    })

    const tokens: AuthTokens = {
      access_token: completeResponse.data.access_token,
      token_type: completeResponse.data.token_type,
    }

    // Store token in localStorage
    localStorage.setItem('access_token', tokens.access_token)

    return tokens
  } catch (error: any) {
    console.error('Login failed:', error)
    throw new Error(
      error.response?.data?.detail || 'Login failed. Please try again.'
    )
  }
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  const token = localStorage.getItem('access_token')

  if (!token) {
    throw new Error('No authentication token found')
  }

  try {
    const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    return response.data
  } catch (error: any) {
    console.error('Failed to get current user:', error)

    // If token is invalid, clear it
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
    }

    throw new Error(
      error.response?.data?.detail || 'Failed to get user information'
    )
  }
}

/**
 * Logout - clear stored token
 */
export function logout(): void {
  localStorage.removeItem('access_token')
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token')
}

/**
 * Get stored access token
 */
export function getAccessToken(): string | null {
  return localStorage.getItem('access_token')
}

/**
 * Axios interceptor to add auth token to all requests
 */
export function setupAxiosInterceptor(): void {
  axios.interceptors.request.use(
    (config) => {
      const token = getAccessToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      // Auto-logout on 401
      if (error.response?.status === 401) {
        logout()
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )
}

// ============================================================================
// OAuth2/OIDC Functions (Authentik, Keycloak, etc.)
// ============================================================================

export interface OAuthConfig {
  enabled: boolean
  authorization_url: string | null
  client_id: string | null
  redirect_uri: string | null
  scopes: string | null
}

/**
 * Get OAuth configuration from backend
 */
export async function getOAuthConfig(): Promise<OAuthConfig> {
  try {
    const response = await axios.get(`${API_URL}/api/v1/auth/oauth/config`)
    return response.data
  } catch (error) {
    console.error('Failed to get OAuth config:', error)
    return {
      enabled: false,
      authorization_url: null,
      client_id: null,
      redirect_uri: null,
      scopes: null,
    }
  }
}

/**
 * Start OAuth login flow
 * Redirects user to OAuth provider (Authentik, Keycloak, etc.)
 */
export async function loginWithOAuth(): Promise<void> {
  try {
    const response = await axios.get(`${API_URL}/api/v1/auth/oauth/login`)
    const { authorization_url, state } = response.data

    // Store state for verification after redirect
    sessionStorage.setItem('oauth_state', state)

    // Redirect to OAuth provider
    window.location.href = authorization_url
  } catch (error: any) {
    console.error('OAuth login failed:', error)
    throw new Error(
      error.response?.data?.detail || 'OAuth login failed. Please try again.'
    )
  }
}

/**
 * Handle OAuth callback after redirect from provider
 */
export async function handleOAuthCallback(
  code: string,
  state: string
): Promise<AuthTokens> {
  try {
    // Verify state matches what we stored
    const storedState = sessionStorage.getItem('oauth_state')
    if (!storedState || storedState !== state) {
      throw new Error('Invalid OAuth state. Possible CSRF attack.')
    }

    // Exchange code for token
    const response = await axios.post(`${API_URL}/api/v1/auth/oauth/callback`, {
      code,
      state,
    })

    const tokens: AuthTokens = {
      access_token: response.data.access_token,
      token_type: response.data.token_type,
    }

    // Store token
    localStorage.setItem('access_token', tokens.access_token)

    // Clean up state
    sessionStorage.removeItem('oauth_state')

    return tokens
  } catch (error: any) {
    console.error('OAuth callback failed:', error)
    sessionStorage.removeItem('oauth_state')
    throw new Error(
      error.response?.data?.detail || 'OAuth authentication failed. Please try again.'
    )
  }
}
