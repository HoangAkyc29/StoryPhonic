import { ref } from 'vue'
import type { User, Profile, LoginCredentials, RegisterData, ChangePasswordData } from '~/types/auth'
import { useRouter } from 'vue-router'

declare global {
  interface Window {
    google: {
      accounts: {
        oauth2: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            callback: (response: { access_token: string; error?: string }) => void;
          }) => {
            requestAccessToken: () => void;
          };
        };
      };
    };
  }
}

export const useAuth = () => {
  const router = useRouter()
  const user = ref<User | null>(null)
  const profile = ref<Profile | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isAuthenticated = ref(false)

  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      localStorage.setItem('token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      
      await checkAuth()
      return user.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      const responseData = await response.json()
      user.value = responseData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    profile.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false

    // Always redirect to homepage after logout using navigateTo
    return navigateTo('/')
  }

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/me/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (!response.ok) {
          throw new Error('Auth check failed')
        }

        const data = await response.json()
        user.value = data
        isAuthenticated.value = true
      } catch (error) {
        console.error('Auth check failed:', error)
        logout()
      }
    } else {
      isAuthenticated.value = false
      user.value = null
    }
  }

  const fetchProfile = async () => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch profile')
      }

      const data = await response.json()
      profile.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (data: Partial<Profile>) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/profile/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Failed to update profile')
      }

      const responseData = await response.json()
      profile.value = responseData
      return responseData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (data: ChangePasswordData) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/change-password/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to change password')
      }

      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateAvatar = async (file: File) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const formData = new FormData()
      formData.append('avatar', file)

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/avatar/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to update avatar')
      }

      const data = await response.json()
      if (profile.value) {
        profile.value.avatar = data.avatar
      }
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const loginWithGoogle = async () => {
    try {
      loading.value = true
      error.value = null

      // Load Google API
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://accounts.google.com/gsi/client'
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })

      // Initialize Google Sign-In
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: useRuntimeConfig().public.googleClientId as string,
        scope: 'email profile',
        callback: async (response) => {
          if (response.error) {
            error.value = response.error
            return
          }

          try {
            // Get user info from Google
            const userInfo = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
              headers: { Authorization: `Bearer ${response.access_token}` }
            }).then(res => res.json())

            // Send to backend
            const result = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/oauth/google/callback/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ user_info: userInfo }),
            }).then(res => res.json())

            if (result.tokens) {
              // Store tokens
              localStorage.setItem('token', result.tokens.access)
              localStorage.setItem('refresh_token', result.tokens.refresh)
              user.value = result.user
              router.push('/dashboard')
            }
          } catch (e) {
            error.value = e instanceof Error ? e.message : 'An error occurred'
          }
        },
      })

      client.requestAccessToken()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    profile,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
    fetchProfile,
    updateProfile,
    changePassword,
    updateAvatar,
    loginWithGoogle,
  }
}

export const auth = useAuth() 