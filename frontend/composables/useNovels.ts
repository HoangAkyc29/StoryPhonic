import { ref } from 'vue'
import type { Novel, CreateNovelData } from '~/types/novel'

function getToken() {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null;
}

export const useNovels = () => {
  const novels = ref<Novel[]>([])
  const currentNovel = ref<Novel | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchNovels = async () => {
    loading.value = true
    error.value = null
    try {
      const token = getToken()
      if (!token) throw new Error('Not authenticated')

      const response = await fetch('http://localhost:8000/api/audiobook/novels/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch novels')
      }

      const data = await response.json()
      novels.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchNovelById = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const token = getToken()
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`http://localhost:8000/api/audiobook/novels/${id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch novel')
      }

      const data = await response.json()
      currentNovel.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createNovel = async (data: CreateNovelData) => {
    loading.value = true
    error.value = null
    try {
      const token = getToken()
      if (!token) throw new Error('Not authenticated')

      const formData = new FormData()
      formData.append('name', data.name)
      if (data.content) {
        formData.append('content', data.content)
      }
      if (data.content_file) {
        formData.append('content_file', data.content_file)
      }

      const response = await fetch('http://localhost:8000/api/audiobook/novels/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create novel')
      }

      const responseData = await response.json()
      novels.value.push(responseData)
      return responseData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createAudiobook = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const token = getToken()
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`http://localhost:8000/api/audiobook/novels/${id}/create_audiobook/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create audiobook')
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

  const softDeleteNovel = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const token = getToken()
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`http://localhost:8000/api/audiobook/novels/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete novel')
      }

      novels.value = novels.value.filter(novel => novel.id !== id)
      if (currentNovel.value?.id === id) {
        currentNovel.value = null
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    novels,
    currentNovel,
    loading,
    error,
    fetchNovels,
    fetchNovelById,
    createNovel,
    createAudiobook,
    softDeleteNovel,
  }
} 