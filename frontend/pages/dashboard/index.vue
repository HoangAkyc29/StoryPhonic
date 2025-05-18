<template>
  <div class="dashboard-workspace">
    <ProjectModal
      :visible="showNameModal"
      type="name"
      @confirm="handleNameConfirm"
      @cancel="showNameModal = false"
    />
    <template v-if="selectedNovelId === 'new'">
      <div class="workspace-intro">
        <h2>Welcome to Story Phonic!</h2>
        <p>Start your new audiobook project by entering your story text or uploading a document file (docx, txt, pdf).</p>
      </div>
      <div class="workspace-box">
        <div class="input-options">
          <textarea 
            v-model="newProjectText" 
            class="story-input" 
            :disabled="!!uploadedFile" 
            :class="{ disabled: !!uploadedFile }" 
            placeholder="Type or paste your story here..."
          ></textarea>
          <div class="divider">or</div>
          <label v-if="!uploadedFile" class="file-upload">
            <input type="file" accept=".docx,.txt,.pdf" style="display:none" @change="handleFileUpload" />
            <span>Upload a file (.docx, .txt, .pdf)</span>
          </label>
          <div v-else class="uploaded-file-box">
            <span class="file-icon">📄</span>
            <span class="file-name">{{ uploadedFile.name }}</span>
            <button class="remove-file-btn" @click="removeFile" title="Remove file">&times;</button>
          </div>
        </div>
        <button class="start-btn" @click="showNameModal = true" :disabled="!canStart">Start Processing</button>
        <div v-if="fileError" class="file-error">{{ fileError }}</div>
      </div>
    </template>
    <template v-else>
      <div class="workspace-pipeline">
        <PipelineSteps :currentStep="currentProject?.currentStep || 1" :status="currentProject?.status || ''" :novel="currentProject" />
      </div>
      <AudiobookStreamer v-if="currentProject?.status === 'completed' || currentProject?.status === 'done'" :novel="currentProject" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { useNovels } from '~/composables/useNovels'
import type { Novel } from '~/types/novel'
import ProjectModal from '~/components/ProjectModal.vue'
import PipelineSteps from '~/components/PipelineSteps.vue'
import AudiobookStreamer from '~/components/AudiobookStreamer.vue'

const { createNovel } = useNovels()
const novels = inject('novels', ref<Novel[]>([]))
const selectedNovelId = inject('selectedNovelId', ref(''))
const selectNovel = inject('selectNovel', () => {})
const currentProject = computed(() => {
  if (!novels?.value || !selectedNovelId?.value) return null
  return novels.value.find(p => p.id === selectedNovelId.value) || null
})

const showNameModal = ref(false)
const newProjectText = ref('')
const uploadedFile = ref<File|null>(null)
const fileError = ref('')

const canStart = computed(() => {
  return (!!newProjectText.value.trim() && !uploadedFile.value) || (!!uploadedFile.value && !newProjectText.value.trim())
})

function handleFileUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['pdf','txt','docx'].includes(ext || '')) {
    fileError.value = 'Only .docx, .txt, or .pdf files are allowed.'
    return
  }
  
  fileError.value = ''
  uploadedFile.value = file
  newProjectText.value = '' // Clear text when file is uploaded
}

function removeFile() {
  uploadedFile.value = null
}

function handleNameConfirm(name: string) {
  // Only allow letters, numbers, spaces, dash, underscore
  const valid = /^[a-zA-Z0-9 _-]+$/.test(name)
  if (!valid) {
    alert('Project name can only contain letters, numbers, spaces, dash (-), and underscore (_).')
    return
  }

  const novelData = {
    name,
    ...(uploadedFile.value ? { content_file: uploadedFile.value } : { content: newProjectText.value.trim() })
  }

  createNovel(novelData)
    .then(_responseData => {
      showNameModal.value = false
      newProjectText.value = ''
      uploadedFile.value = null
      window.location.reload() // Reload page to update sidebar
    })
    .catch(error => {
      alert('Failed to create project: ' + error.message)
    })
}

// Add dashboard layout for Nuxt 3
definePageMeta({
  layout: 'dashboard'
})
</script>

<style scoped>
.dashboard-workspace {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 0;
  /* background: transparent; */
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
  transition: background 0.2s, color 0.2s;
}
.story-input.disabled {
  background: #f3f4f6;
  color: #aaa;
  cursor: not-allowed;
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
.uploaded-file-box {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.7rem 1.5rem;
  border-radius: 999px;
  font-weight: 600;
  border: 1px solid #bae6fd;
}
.file-icon {
  font-size: 1.2rem;
}
.file-name {
  font-size: 1rem;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.remove-file-btn {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 1.2rem;
  cursor: pointer;
  margin-left: 0.2rem;
  padding: 0 0.2rem;
  border-radius: 50%;
  transition: background 0.2s;
}
.remove-file-btn:hover {
  background: #fee2e2;
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
.start-btn:disabled {
  background: #b6e0fa;
  cursor: not-allowed;
}
.start-btn:hover:not(:disabled) {
  background: #0369a1;
}
.file-error {
  color: #ef4444;
  font-size: 0.98rem;
  margin-top: 0.5rem;
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