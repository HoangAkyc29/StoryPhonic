<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>Story Phonic</h2>
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
        <div class="project-meta">
          <span class="last-edit">Last edit: {{ project.lastEdit }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
defineProps<{ projects: any[], selectedProjectId: string }>()
defineEmits(['selectProject', 'newProject'])
</script>

<style scoped>
.sidebar {
  width: 270px;
  background: #18181b;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 0;
  border-right: 1px solid #222;
  min-height: 100vh;
}
.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1.5rem 1.2rem 1rem 1.2rem;
  border-bottom: 1px solid #222;
}
.sidebar-header h2 {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 0.7rem;
  color: #38bdf8;
}
.new-project-btn {
  background: #38bdf8;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 1.2rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.new-project-btn:hover {
  background: #0ea5e9;
}
.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0.5rem;
}
.project-item {
  background: #23232b;
  border-radius: 0.7rem;
  margin-bottom: 1rem;
  padding: 1rem 1rem 0.7rem 1rem;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}
.project-item.selected {
  border: 2px solid #38bdf8;
  background: #1e293b;
}
.project-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}
.project-title {
  font-weight: 600;
  font-size: 1.1rem;
}
.project-progress {
  font-size: 0.95rem;
  color: #38bdf8;
}
.progress-bar {
  background: #2d2d3a;
  border-radius: 0.5rem;
  height: 7px;
  margin-bottom: 0.3rem;
  width: 100%;
}
.progress {
  background: #38bdf8;
  height: 100%;
  border-radius: 0.5rem;
  transition: width 0.3s;
}
.project-meta {
  font-size: 0.85rem;
  color: #bdbdbd;
}
.last-edit {
  font-style: italic;
}
</style> 