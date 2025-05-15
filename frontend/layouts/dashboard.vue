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
        :novels="novels"
        :selectedNovelId="selectedNovelId"
        @selectNovel="selectNovel"
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
import { useNovels } from '~/composables/useNovels'
import { ref, onMounted, provide } from 'vue'

const { novels, fetchNovels } = useNovels()
const selectedNovelId = ref<string>('')
const showDeleteModal = ref(false)
const deleteProjectName = ref('')

onMounted(async () => {
  try {
    await fetchNovels()
    selectedNovelId.value = 'new'
  } catch (error) {
    console.error('Failed to fetch novels:', error)
  }
})

function selectNovel(id: string) {
  selectedNovelId.value = id
}

function createNewProject() {
  selectedNovelId.value = 'new'
  // TODO: Implement new project creation
}

function openDeleteModal(novel: { id: string, name: string }) {
  deleteProjectName.value = novel.name
  showDeleteModal.value = true
}

function handleDeleteConfirm() {
  // TODO: Implement delete confirmation
  showDeleteModal.value = false
}

provide('novels', novels)
provide('selectedNovelId', selectedNovelId)
provide('selectNovel', selectNovel)
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