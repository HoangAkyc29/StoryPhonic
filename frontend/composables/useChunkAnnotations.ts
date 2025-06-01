import { ref } from 'vue'
import type { ChunkAnnotation } from '~/types/novel'

export const useChunkAnnotations = () => {
  const chunkAnnotations = ref<ChunkAnnotation[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchChunkAnnotations = async (novelId: string) => {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/chunk-annotations/?novel=${novelId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch chunk annotations')
      }

      const data = await response.json()
      chunkAnnotations.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    chunkAnnotations,
    loading,
    error,
    fetchChunkAnnotations,
  }
} 