<template>
  <aside class="sidebar-glass">
    <div class="sidebar-header">
      <span class="sidebar-title">
        <svg width="28" height="28" viewBox="0 0 32 32" fill="none" style="vertical-align:middle;margin-right:0.5rem;"><circle cx="16" cy="16" r="16" fill="#0ea5e9"/><text x="50%" y="55%" text-anchor="middle" fill="#fff" font-size="18" font-family="Inter, Arial, sans-serif" dy=".3em">D</text></svg>
        Story Phonic
      </span>
      <button class="new-project-btn" @click="$emit('newProject')">
        <svg width="18" height="18" viewBox="0 0 20 20" fill="none" style="margin-right:0.5rem;"><path d="M10 4V16M4 10H16" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>
        New Project
      </button>
    </div>
    <div class="sidebar-project-list">
      <div
        v-for="novel in novels"
        :key="novel.id"
        :class="['sidebar-project-item', { selected: novel.id === selectedNovelId }]"
        @click="$emit('selectNovel', novel.id)"
      >
        <div class="project-title-row">
          <span class="project-title" :title="novel.name">{{ novel.name }}</span>
          <span class="project-status-badge" :class="statusClass(novel.status)">
            {{ statusText(novel.status) }}
          </span>
          <button class="delete-btn-glass" title="Delete project" @click.stop="$emit('delete', novel)">
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M7.5 8.75V14.25M10 8.75V14.25M12.5 8.75V14.25M3.75 5.75H16.25M5.833 5.75L6.25 15.25C6.25 15.6642 6.58579 16 7 16H13C13.4142 16 13.75 15.6642 13.75 15.25L14.167 5.75M8.75 5.75V4.75C8.75 4.33579 9.08579 4 9.5 4H10.5C10.9142 4 11.25 4.33579 11.25 4.75V5.75" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
        <div class="project-meta">
          Created: {{ formatDate(novel.created_at) }}
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { Novel } from '~/types/novel'

defineProps<{ novels: Novel[]; selectedNovelId: string }>()
defineEmits(['selectNovel', 'newProject', 'delete'])

function statusText(status: string) {
  if (status === 'pending') return 'Pending'
  if (status === 'processing') return 'Processing'
  if (status === 'done') return 'Completed'
  if (status === 'error') return 'Error'
  return status
}
function statusClass(status: string) {
  if (status === 'pending') return 'badge-pending'
  if (status === 'processing') return 'badge-processing'
  if (status === 'done') return 'badge-done'
  if (status === 'error') return 'badge-error'
  return ''
}
function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.sidebar-glass {
  width: 270px;
  background: rgba(255,255,255,0.55);
  backdrop-filter: blur(16px);
  border-right: 1.5px solid #e0e7ef;
  color: #222;
  display: flex;
  flex-direction: column;
  padding: 2rem 1rem 1.5rem 1.2rem;
  min-height: 100vh;
  font-family: 'Inter', Arial, sans-serif;
  box-sizing: border-box;
}
.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1.2rem;
  margin-bottom: 2.2rem;
}
.sidebar-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0ea5e9;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
}
.new-project-btn {
  background: linear-gradient(90deg, #0ea5e9 60%, #38bdf8 100%);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.55rem 1.5rem;
  font-weight: 600;
  font-size: 1.05rem;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(14,165,233,0.10);
  display: flex;
  align-items: center;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}
.new-project-btn:hover {
  background: linear-gradient(90deg, #38bdf8 0%, #0ea5e9 100%);
  color: #0ea5e9;
  box-shadow: 0 4px 24px rgba(14,165,233,0.18);
}
.sidebar-project-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.sidebar-project-item {
  background: #fff;
  border-radius: 1rem;
  padding: 1.1rem 1.1rem 0.9rem 1rem;
  cursor: pointer;
  border: 2px solid transparent;
  transition: box-shadow 0.18s, border 0.18s, background 0.18s;
  box-shadow: 0 2px 12px rgba(14,165,233,0.06);
}
.sidebar-project-item.selected {
  border: 2px solid #0ea5e9;
  background: #e0f7fa;
}
.sidebar-project-item:hover {
  box-shadow: 0 8px 32px rgba(14,165,233,0.18);
  border: 2px solid #38bdf8;
  background: #f0faff;
}
.project-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
  gap: 0.3rem;
}
.project-title {
  font-weight: 600;
  font-size: 1.08rem;
  color: #222;
  letter-spacing: 0.2px;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.project-status-badge {
  font-size: 0.97rem;
  font-weight: 500;
  padding: 0.1rem 0.7rem;
  border-radius: 999px;
  margin-left: 0.3rem;
  text-transform: none;
}
.badge-pending {
  background: #f3f4f6;
  color: #6b7280;
}
.badge-processing {
  background: #e0f2fe;
  color: #0369a1;
}
.badge-done {
  background: #d1fae5;
  color: #059669;
}
.badge-error {
  background: #fee2e2;
  color: #ef4444;
}
.project-meta {
  font-size: 0.87rem;
  color: #0369a1;
  font-style: italic;
  margin-top: 0.2rem;
}
.delete-btn-glass {
  background: none;
  border: none;
  padding: 0 0 0 0.3rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s, background 0.2s;
  vertical-align: middle;
  color: #0ea5e9;
  border-radius: 50%;
  margin-left: 0.2rem;
  outline: none;
}
.sidebar-project-item:hover .delete-btn-glass {
  opacity: 1;
}
.delete-btn-glass:hover {
  color: #ef4444;
  background: #e0e7ef;
}
.project-list::-webkit-scrollbar {
  width: 7px;
}
.project-list::-webkit-scrollbar-thumb {
  background: #e0e7ef;
  border-radius: 6px;
}
.project-list::-webkit-scrollbar-track {
  background: transparent;
}
</style> 