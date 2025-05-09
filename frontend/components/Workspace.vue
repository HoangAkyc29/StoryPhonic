<template>
  <div class="workspace">
    <div v-if="isNew" class="new-project">
      <h2>Welcome to Story Phonic!</h2>
      <p class="intro">Turn your book into a multicast AI audiobook in minutes. Start by entering your story or uploading a file.</p>
      <div class="input-options">
        <textarea v-model="storyText" placeholder="Type or paste your story here..." class="story-input"></textarea>
        <div class="or">OR</div>
        <input type="file" accept=".txt,.docx,.pdf" @change="onFileChange" />
      </div>
      <button class="start-btn" @click="$emit('startProcess')">Start Processing</button>
    </div>
    <div v-else-if="project" class="project-workspace">
      <h2>{{ project.name }}</h2>
      <div class="progress-section">
        <div class="progress-label">Progress: {{ project.progress }}%</div>
        <div class="progress-bar">
          <div class="progress" :style="{ width: project.progress + '%' }"></div>
        </div>
      </div>
      <div class="pipeline">
        <div v-for="(step, idx) in project.steps" :key="idx" class="pipeline-step" :class="{ active: idx + 1 === project.currentStep, done: idx + 1 < project.currentStep }">
          <span class="step-index">{{ idx + 1 }}</span>
          <span class="step-label">{{ step }}</span>
        </div>
      </div>
      <div v-if="project.status === 'done'" class="audio-section">
        <h3>Output Audio</h3>
        <audio controls :src="audioUrl" class="audio-player"></audio>
        <div class="audio-actions">
          <button class="edit-btn">Edit Audio</button>
          <button class="download-btn">Download</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const props = defineProps<{ project: any, isNew: boolean }>()
const emit = defineEmits(['uploadFile', 'startProcess'])
const storyText = ref('')
const audioUrl = ref('') // Mock, sẽ thay bằng url thực tế sau
function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emit('uploadFile', file)
}
</script>

<style scoped>
.workspace {
  flex: 1;
  padding: 2.5rem 2rem 1rem 2rem;
  background: #f8fafc;
  min-height: 100vh;
}
.new-project {
  max-width: 600px;
  margin: 0 auto;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 16px rgba(56,189,248,0.10);
  padding: 2.5rem 2rem 2rem 2rem;
  text-align: center;
}
.intro {
  color: #0ea5e9;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}
.input-options {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  margin-bottom: 2rem;
}
.story-input {
  width: 100%;
  min-height: 120px;
  border: 1px solid #e0f2fe;
  border-radius: 0.5rem;
  padding: 1rem;
  font-size: 1rem;
  resize: vertical;
}
.or {
  color: #888;
  font-size: 1rem;
  margin: 0.5rem 0;
}
.start-btn {
  background: #38bdf8;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.8rem 2rem;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.start-btn:hover {
  background: #0ea5e9;
}
.project-workspace {
  max-width: 700px;
  margin: 0 auto;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 16px rgba(56,189,248,0.10);
  padding: 2.5rem 2rem 2rem 2rem;
}
.progress-section {
  margin-bottom: 1.5rem;
}
.progress-label {
  font-size: 1rem;
  color: #0ea5e9;
  margin-bottom: 0.3rem;
}
.progress-bar {
  background: #e0f2fe;
  border-radius: 0.5rem;
  height: 10px;
  width: 100%;
  margin-bottom: 1rem;
}
.progress {
  background: #38bdf8;
  height: 100%;
  border-radius: 0.5rem;
  transition: width 0.3s;
}
.pipeline {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  margin-bottom: 2rem;
}
.pipeline-step {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.7rem 1rem;
  border-radius: 0.5rem;
  background: #f1f5f9;
  color: #333;
  font-size: 1rem;
  transition: background 0.2s;
}
.pipeline-step.active {
  background: #38bdf8;
  color: #fff;
  font-weight: bold;
}
.pipeline-step.done {
  background: #a7f3d0;
  color: #065f46;
}
.step-index {
  font-weight: bold;
  font-size: 1.1rem;
  width: 2rem;
  text-align: center;
}
.audio-section {
  margin-top: 2rem;
  text-align: center;
}
.audio-player {
  width: 100%;
  margin-bottom: 1rem;
}
.audio-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
.edit-btn, .download-btn {
  background: #0ea5e9;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.6rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.edit-btn:hover, .download-btn:hover {
  background: #0369a1;
}
</style> 