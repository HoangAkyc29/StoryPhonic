<template>
  <div class="dashboard-layout">
    <AppHeader />
    <ProjectModal
      :visible="showDeleteModal"
      type="delete"
      :projectName="deleteProjectName"
      @confirm="handleDeleteConfirm"
      @cancel="showDeleteModal = false"
    />
    <div class="dashboard-body">
      <DashboardSidebar
        :projects="projects"
        :selectedProjectId="selectedProjectId"
        @selectProject="selectProject"
        @newProject="createNewProject"
        @delete="openDeleteModal"
      />
      <main class="dashboard-main">
        <slot />
      </main>
    </div>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/AppHeader.vue'
import AppFooter from '~/components/AppFooter.vue'
import DashboardSidebar from '~/components/DashboardSidebar.vue'
import ProjectModal from '~/components/ProjectModal.vue'
import { useDashboardProjects } from '~/composables/useDashboardProjects'
import { ref } from 'vue'

const { projects, selectedProjectId, selectProject, createNewProject } = useDashboardProjects()

const showDeleteModal = ref(false)
const deleteProjectId = ref('')
const deleteProjectName = ref('')

function openDeleteModal(project: { id: string, name: string }) {
  deleteProjectId.value = project.id
  deleteProjectName.value = project.name
  showDeleteModal.value = true
}
function handleDeleteConfirm() {
  const idx = projects.value.findIndex(p => p.id === deleteProjectId.value)
  if (idx !== -1) {
    projects.value.splice(idx, 1)
    // If deleted project is selected, select 'new'
    if (selectedProjectId.value === deleteProjectId.value) {
      createNewProject()
    }
  }
  showDeleteModal.value = false
}
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.dashboard-body {
  display: flex;
  flex: 1;
  min-height: 0;
  background: linear-gradient(120deg, #e0f7fa 0%, #e0f2fe 100%);
}
.dashboard-main {
  flex: 1;
  padding: 2rem 2.5rem;
  min-height: 100vh;
  background: linear-gradient(120deg, #f8fbff 0%, #e0f2fe 100%);
  overflow-y: auto;
}
</style> 