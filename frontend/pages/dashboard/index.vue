<template>
  <div class="dashboard-workspace">
    <template v-if="selectedProjectId === 'new'">
      <div class="workspace-intro">
        <h2>Welcome to Story Phonic!</h2>
        <p>Start your new audiobook project by entering your story text or uploading a document file (docx, txt, pdf).</p>
      </div>
      <div class="workspace-box">
        <div class="input-options">
          <textarea class="story-input" placeholder="Type or paste your story here..."></textarea>
          <div class="divider">or</div>
          <label class="file-upload">
            <input type="file" accept=".docx,.txt,.pdf" style="display:none" />
            <span>Upload a file (.docx, .txt, .pdf)</span>
          </label>
        </div>
        <button class="start-btn">Start Processing</button>
      </div>
    </template>
    <template v-else>
      <div class="workspace-pipeline">
        <PipelineSteps :currentStep="currentProject?.currentStep || 1" :status="currentProject?.status || ''" />
      </div>
      <div v-if="currentProject?.status === 'done'" class="workspace-audio">
        <h3>Listen & Fine-tune Your Audiobook</h3>
        <div class="audio-player-demo">
          <span>Audio player & tuning UI coming soon...</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PipelineSteps from '~/components/PipelineSteps.vue'
import { useDashboardProjects } from '~/composables/useDashboardProjects'

const { projects, selectedProjectId } = useDashboardProjects()
const currentProject = computed(() => projects.value.find(p => p.id === selectedProjectId.value))
</script>

<style scoped>
.dashboard-workspace {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 0;
}
.workspace-intro {
  text-align: center;
  margin-bottom: 2rem;
}
.workspace-intro h2 {
  font-size: 2rem;
  color: #0ea5e9;
  margin-bottom: 0.5rem;
}
.workspace-intro p {
  color: #555;
  font-size: 1.1rem;
}
.workspace-box {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}
.input-options {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
}
.story-input {
  width: 100%;
  min-height: 120px;
  border: 1px solid #e0e7ef;
  border-radius: 8px;
  padding: 1rem;
  font-size: 1.1rem;
  resize: vertical;
}
.divider {
  color: #aaa;
  font-size: 1rem;
  margin: 0.5rem 0;
}
.file-upload {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.7rem 1.5rem;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid #bae6fd;
  transition: background 0.2s;
}
.file-upload:hover {
  background: #bae6fd;
}
.start-btn {
  background: #0ea5e9;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.7rem 2.2rem;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  margin-top: 1rem;
  transition: background 0.2s;
}
.start-btn:hover {
  background: #0369a1;
}
.workspace-pipeline {
  margin-bottom: 2.5rem;
}
.workspace-audio {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 2rem;
  margin-top: 2rem;
  text-align: center;
}
.audio-player-demo {
  margin-top: 1rem;
  color: #888;
  font-size: 1.1rem;
}
</style> 