import { ref } from 'vue'

export interface Project {
  id: string
  name: string
  progress: number
  lastEdit: string
  status: string
  currentStep: number
}

const projects = ref<Project[]>([
  {
    id: '1',
    name: 'The Little Prince',
    progress: 80,
    lastEdit: '2 ngày trước',
    status: 'processing',
    currentStep: 4
  },
  {
    id: '2',
    name: 'Alice in Wonderland',
    progress: 100,
    lastEdit: '7 ngày trước',
    status: 'done',
    currentStep: 8
  }
])

const selectedProjectId = ref<string>('new')

export function useDashboardProjects() {
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
    createNewProject
  }
} 