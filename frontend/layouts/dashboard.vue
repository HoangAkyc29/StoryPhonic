<template>
  <div class="dashboard-layout">
    <AppHeader />
    <div class="dashboard-body">
      <DashboardSidebar :projects="projects" :selectedProjectId="selectedProjectId" @selectProject="selectProject" @newProject="createNewProject" />
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
import { useDashboardProjects } from '~/composables/useDashboardProjects'

const { projects, selectedProjectId, selectProject, createNewProject } = useDashboardProjects()
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