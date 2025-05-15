import { ref } from 'vue'
import { useAuth } from './useAuth'

interface UpdateProfileData {
  first_name: string
  last_name: string
  email: string
}

interface ChangePasswordData {
  current_password: string
  new_password: string
  confirm_password: string
}

export const useProfile = () => {
  const { user } = useAuth()
  const loading = ref(false)
  const error = ref<string | null>(null)

  const updateProfile = async (data: UpdateProfileData) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch('http://localhost:8000/api/oauth/profile/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update profile')
      }

      const responseData = await response.json()
      if (user.value) {
        user.value = { ...user.value, ...responseData }
      }
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

      const response = await fetch('http://localhost:8000/api/oauth/change-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: data.current_password,
          new_password: data.new_password,
          confirm_password: data.confirm_password
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to change password')
      }
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

      const response = await fetch('http://localhost:8000/api/oauth/avatar/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to update avatar')
      }

      const responseData = await response.json()
      if (user.value) {
        user.value.avatar = responseData.avatar
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    updateProfile,
    changePassword,
    updateAvatar,
  }
} 