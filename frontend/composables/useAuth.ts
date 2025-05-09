import { ref } from 'vue'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  avatar?: string
  roles: string[]
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  username: string
  email: string
  password: string
  confirmPassword: string
  first_name?: string
  last_name?: string
}

export const useAuth = () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('http://localhost:8000/api/oauth/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.email,
          password: credentials.password,
          email: credentials.email
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      // Store token in localStorage
      localStorage.setItem('token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      
      // Get user info
      await checkAuth()
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
      const response = await fetch('/api/oauth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: data.username,
          email: data.email,
          password: data.password,
          password2: data.confirmPassword,
          first_name: data.first_name,
          last_name: data.last_name
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      const responseData = await response.json()
      user.value = responseData.user
      // Store token in localStorage
      localStorage.setItem('token', responseData.token)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    if (!token) return false

    try {
      const response = await fetch('/api/oauth/me/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Authentication failed')
      }

      const data = await response.json()
      user.value = data
      return true
    } catch (e) {
      logout()
      return false
    }
  }

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    checkAuth,
  }
} 