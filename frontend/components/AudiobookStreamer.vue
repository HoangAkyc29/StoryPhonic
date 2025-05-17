<template>
  <div class="audiobook-streamer">
    <h3>{{ novel.name }}</h3>
    <p>Created: {{ formatDate(novel.created_at) }}</p>
    <audio
      ref="audioRef"
      v-if="novel.s3_audio_file_url"
      :src="novel.s3_audio_file_url"
      controls
      preload="none"
      style="width: 100%; margin: 1.5rem 0;"
      @timeupdate="onTimeUpdate"
    >
      Your browser does not support the audio element.
    </audio>
    <div v-else class="audio-missing">No audio file available.</div>
    <div class="meta-info">
      <p><strong>Metadata:</strong> <span v-if="metadata">Loaded</span><span v-else>Loading...</span></p>
      <p><strong>Chunk annotations:</strong> <span v-if="chunkAnnotations.length">Loaded ({{ chunkAnnotations.length }})</span><span v-else>Loading...</span></p>
    </div>
    <div v-if="currentMeta" class="current-meta-box">
      <h4>Current Metadata</h4>
      <p><b>Character:</b> {{ currentMeta.character_name }}</p>
      <p><b>Voice Actor:</b> {{ currentMeta.voice_actor }}</p>
      <p><b>True Identity:</b> {{ currentMeta.true_identity }}</p>
      <p><b>Time Start:</b> {{ currentMeta.time_start }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'

interface MetadataItem {
  index_x: number;
  index_y: number;
  voice_actor: string;
  character_name: string;
  true_identity: string;
  time_start: number;
  time_end: number;
}

interface ChunkAnnotation {
  id: string;
  novel: string;
  raw_text: string;
  clean_text: string;
  index: number;
  status: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

interface Novel {
  id: string;
  name: string;
  created_at: string;
  s3_audio_file_url?: string;
  s3_audio_metadata_url?: string;
  // ... add more fields as needed
}

const props = defineProps<{ novel: Novel }>()

const chunkAnnotations = ref<ChunkAnnotation[]>([])
const metadata = ref<MetadataItem[]>([])
const audioRef = ref<HTMLAudioElement|null>(null)
const currentTime = ref(0)

const currentMeta = computed(() => {
  if (!metadata.value.length) return null
  // Lọc các đoạn có time_start <= currentTime, lấy đoạn cuối cùng
  return [...metadata.value]
    .filter(m => m.time_start <= currentTime.value)
    .sort((a, b) => b.time_start - a.time_start)[0] || null
})

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function onTimeUpdate() {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
  }
}

async function fetchChunkAnnotations(novelId: string) {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`http://localhost:8000/api/audiobook/chunk-annotations/?novel=${novelId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch chunk annotations')
    const data = await res.json()
    chunkAnnotations.value = data
    console.log('Chunk annotations:', data)
  } catch (e) {
    console.error(e)
  }
}

async function fetchMetadata(url: string) {
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error('Failed to fetch metadata')
    const data = await res.json()
    metadata.value = data
    console.log('Metadata:', data)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  if (props.novel?.id) fetchChunkAnnotations(props.novel.id)
  if (props.novel?.s3_audio_metadata_url) fetchMetadata(props.novel.s3_audio_metadata_url)
})

watch(() => props.novel, (n, o) => {
  if (n?.id && n?.id !== o?.id) fetchChunkAnnotations(n.id)
  if (n?.s3_audio_metadata_url && n?.s3_audio_metadata_url !== o?.s3_audio_metadata_url) fetchMetadata(n.s3_audio_metadata_url)
})
</script>

<style scoped>
.audiobook-streamer {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 2rem;
  margin-top: 2rem;
  text-align: center;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}
.audio-missing {
  color: #ef4444;
  margin: 1.5rem 0;
}
.meta-info {
  margin-top: 1.5rem;
  color: #888;
  font-size: 1.05rem;
}
.current-meta-box {
  margin-top: 2rem;
  background: #f0f9ff;
  border-radius: 0.7rem;
  padding: 1.2rem 1.5rem;
  display: inline-block;
  text-align: left;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.current-meta-box h4 {
  margin-bottom: 0.7rem;
  color: #0ea5e9;
}
</style> 