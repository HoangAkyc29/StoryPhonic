<template>
  <div>
    <AppHeader />
    <div class="main-area">
      <Sidebar v-if="showSidebar" :projects="projects" :selectedProjectId="selectedProjectId" @selectProject="selectProject" @newProject="createNewProject" />
      <main>
        <slot />
      </main>
    </div>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '~/components/AppHeader.vue'
import Sidebar from '~/components/Sidebar.vue'
import AppFooter from '~/components/AppFooter.vue'

const route = useRoute()
const showSidebar = computed(() => route.path.startsWith('/dashboard'))

// Mock data cho sidebar
const projects = ref([
  {
    id: '1',
    name: 'The Little Prince',
    progress: 80,
    lastEdit: '2 ngày trước',
    status: 'processing',
    currentStep: 4,
    steps: [
      'Document Chunking',
      'Context Memory Management',
      'Annotation Generation',
      'Character Trait Assessment',
      'Voice Assignment',
      'Text To Speech',
      'Audio Post-processing',
      'Output Audio'
    ]
  },
  {
    id: '2',
    name: 'Alice in Wonderland',
    progress: 100,
    lastEdit: '7 ngày trước',
    status: 'done',
    currentStep: 8,
    steps: [
      'Document Chunking',
      'Context Memory Management',
      'Annotation Generation',
      'Character Trait Assessment',
      'Voice Assignment',
      'Text To Speech',
      'Audio Post-processing',
      'Output Audio'
    ]
  }
])
const selectedProjectId = ref('new')
const selectedProject = computed(() => {
  if (selectedProjectId.value === 'new') return null
  return projects.value.find(p => p.id === selectedProjectId.value) || null
})
function selectProject(id) {
  selectedProjectId.value = id
}
function createNewProject() {
  selectedProjectId.value = 'new'
}
</script>

<style scoped>
.main-area {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(120deg, #e0f7fa 0%, #e0f2fe 100%);
}
main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(120deg, #f8fbff 0%, #e0f2fe 100%);
}

.header {
  background: #fff;
  border-bottom: 1px solid #e0f2fe;
  padding: 0.5rem 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
}

.logo-title {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo {
  width: 36px;
  height: 36px;
}

.brand {
  font-size: 1.4rem;
  font-weight: bold;
  color: #0ea5e9;
  letter-spacing: 1px;
}

.menu {
  display: flex;
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu li a {
  color: #222;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.2s;
}

.menu li a:hover {
  color: #0ea5e9;
}

.auth {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.login {
  color: #222;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.2s;
}

.login:hover {
  color: #0ea5e9;
}

.signup {
  background: #0ea5e9;
  color: #fff;
  padding: 0.5rem 1.2rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  transition: background 0.2s;
}

.signup:hover {
  background: #0369a1;
}

.footer {
  background: #f8fafc;
  border-top: 1px solid #e0f2fe;
  padding: 1.5rem 0 1rem 0;
  margin-top: 2rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
  color: #666;
  padding: 0 2rem;
}

.footer-links a {
  color: #0ea5e9;
  text-decoration: none;
  margin: 0 0.3rem;
}

.footer-links a:hover {
  text-decoration: underline;
}
</style> 