import { ref } from 'vue'

interface Story {
  id: number
  title: string
  content: string
  level: number
  points: number
  created_at: string
  updated_at: string
}

export const useStories = () => {
  const stories = ref<Story[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchStories = async () => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch('/api/stories/', {
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

  const fetchStoryById = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`/api/stories/${id}/`, {
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