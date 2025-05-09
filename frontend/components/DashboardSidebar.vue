<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <button class="new-project-btn" @click="$emit('newProject')">+ New Project</button>
    </div>
    <div class="project-list">
      <div
        v-for="project in projects"
        :key="project.id"
        :class="['project-item', { selected: project.id === selectedProjectId }]"
        @click="$emit('selectProject', project.id)"
      >
        <div class="project-title-row">
          <span class="project-title">{{ project.name }}</span>
          <span class="project-progress">{{ project.progress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress" :style="{ width: project.progress + '%' }"></div>
        </div>
        <div class="project-meta">Last edit: {{ project.lastEdit }}</div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
interface Project {
  id: string;
  name: string;
  progress: number;
  lastEdit: string;
  status: string;
  currentStep: number;
}
defineProps<{ projects: Project[]; selectedProjectId: string }>()
defineEmits(['selectProject', 'newProject'])
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #18181b;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 1rem 0.5rem 1rem 1rem;
  border-right: 1px solid #23232a;
  min-height: 100vh;
}
.sidebar-header {
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #23232a;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}
.new-project-btn {
  background: #0ea5e9;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.5rem 1.2rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.new-project-btn:hover {
  background: #0369a1;
}
.project-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 0.5rem;
}
.project-item {
  background: transparent;
  border-radius: 8px;
  padding: 0.7rem 1rem 0.7rem 0.7rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid transparent;
}
.project-item.selected {
  background: #23232a;
  border: 1px solid #0ea5e9;
}
.project-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.2rem;
}
.project-title {
  font-weight: 600;
  font-size: 1.05rem;
  color: #fff;
}
.project-progress {
  font-size: 0.95rem;
  color: #38bdf8;
  font-weight: 500;
}
.progress-bar {
  width: 100%;
  height: 6px;
  background: #23232a;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.3rem;
}
.progress {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9 60%, #38bdf8 100%);
  border-radius: 4px;
  transition: width 0.3s;
}
.project-meta {
  font-size: 0.85rem;
  color: #a1a1aa;
}
</style> 