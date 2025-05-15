import { ref } from 'vue'
import { useNovels } from './useNovels'
import type { Novel } from '~/types/novel'

export interface Project {
  id: string
  name: string
  status: string
}

const projects = ref<Project[]>([])
const selectedProjectId = ref<string>('new')

export function useDashboardProjects() {
  const { novels, fetchNovels } = useNovels()

  const loadProjects = async () => {
    try {
      await fetchNovels()
      projects.value = novels.value.map(novel => ({
        id: novel.id,
        name: novel.name,
        status: novel.status
      }))
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  function selectProject(id: string) {
    selectedProjectId.value = id
  }

  function createNewProject() {
    selectedProjectId.value = 'new'
  }

  return {
    projects,
    selectedProjectId,
    selectProject,
    createNewProject,
    loadProjects
  }
} 