import { ref } from 'vue'
import type { Character } from '~/types/novel'

export const useCharacters = () => {
  const characters = ref<Character[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCharacters = async (novelId: string) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/characters/?novel=${novelId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch characters')
      }

      const data = await response.json()
      characters.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createCharacter = async (novelId: string, data: Omit<Character, 'id' | 'novel' | 'created_at' | 'updated_at' | 'is_deleted'>) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/characters/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...data,
          novel: novelId,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create character')
      }

      const responseData = await response.json()
      characters.value.push(responseData)
      return responseData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateCharacter = async (characterId: string, data: Partial<Omit<Character, 'id' | 'novel' | 'created_at' | 'updated_at' | 'is_deleted'>>) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/characters/${characterId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update character')
      }

      const responseData = await response.json()
      const index = characters.value.findIndex(c => c.id === characterId)
      if (index !== -1) {
        characters.value[index] = responseData
      }
      return responseData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const deleteCharacter = async (characterId: string) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/characters/${characterId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete character')
      }

      characters.value = characters.value.filter(c => c.id !== characterId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    characters,
    loading,
    error,
    fetchCharacters,
    createCharacter,
    updateCharacter,
    deleteCharacter,
  }
} 