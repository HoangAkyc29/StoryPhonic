import { ref } from 'vue'
import type { Novel } from '~/types/novel'

export const useStories = () => {
  const stories = ref<Novel[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchStories = async () => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch('http://localhost:8000/api/audiobook/novels/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch stories')
      }

      const data = await response.json()
      stories.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchStoryById = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`http://localhost:8000/api/audiobook/novels/${id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch story')
      }

      const data = await response.json()
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    stories,
    loading,
    error,
    fetchStories,
    fetchStoryById
  }
} 