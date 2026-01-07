import axios from 'axios'
import { startRegistration, startAuthentication } from '@simplewebauthn/browser'
import type {
  PublicKeyCredentialCreationOptionsJSON,
  PublicKeyCredentialRequestOptionsJSON,
} from '@simplewebauthn/browser'

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
    const parsedOptions: PublicKeyCredentialCreationOptionsJSON = JSON.parse(options)

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
    const parsedOptions: PublicKeyCredentialRequestOptionsJSON = JSON.parse(options)

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
