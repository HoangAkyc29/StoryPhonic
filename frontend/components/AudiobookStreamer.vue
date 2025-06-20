<template>
  <div class="streamer-row">
    <div class="profile-box character-profile">
      <h4>Character Profile</h4>
      <template v-if="currentMeta && currentMeta.true_identity !== 'Narrator' && currentCharacterProfile">
        <JsonPretty :data="currentCharacterProfile" />
      </template>
      <div v-else style="color:#aaa">No character info</div>
    </div>
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
      <!-- Sentence display -->
      <div v-if="currentSentenceObj" class="sentence-highlight-box">
        <span class="sentence-highlight">
          <span class="read-part">{{ highlightedSentence.read }}</span><span class="unread-part">{{ highlightedSentence.unread }}</span>
        </span>
      </div>
      <div v-if="currentMeta" class="current-meta-box">
        <h4>
          <span class="meta-icon">ℹ️</span>
          Metadata Information
        </h4>
        <ul class="meta-list">
          <li><span class="meta-icon">👤</span> <b>Character:</b> {{ currentMeta.character_name }}</li>
          <li><span class="meta-icon">🎤</span> <b>Voice Actor:</b> {{ currentMeta.voice_actor }}</li>
          <li><span class="meta-icon">🕵️‍♂️</span> <b>Identity:</b> {{ currentMeta.true_identity }}</li>
          <li><span class="meta-icon">⏱️</span> <b>Time Start:</b> {{ currentMeta.time_start }}</li>
          <li><span class="meta-icon">⏱️</span> <b>Time End:</b> {{ currentMeta.time_end }}</li>
          <li v-if="currentSentenceObj"><span class="meta-icon">😊</span> <b>Emotion:</b> {{ displayEmotion }}</li>
        </ul>
      </div>
    </div>
    <div class="profile-box voice-profile">
      <h4>Voice Actor Profile</h4>
      <template v-if="currentMeta && currentMeta.voice_actor !== 'Narrator' && currentVoiceProfile">
        <JsonPretty :data="currentVoiceProfile" />
      </template>
      <div v-else style="color:#aaa">No voice actor info</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import JsonPretty from './JsonPretty.vue'

interface MetadataItem {
  index_x: number;
  index_y: number;
  voice_actor: string;
  character_name: string;
  true_identity: string;
  time_start: number;
  time_end: number;
}

interface SentenceObj {
  sentence: string;
  type: string;
  character: string;
  emotion: string;
  index: number;
  identity: string;
  voice_actor: string;
  gender?: string;
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
  parsed_clean?: SentenceObj[];
}

interface Novel {
  id: string;
  name: string;
  created_at: string;
  s3_audio_file_url?: string;
  s3_audio_metadata_url?: string;
  // ... add more fields as needed
}

interface CharacterProfile {
  [key: string]: any;
}
interface VoiceProfile {
  [key: string]: any;
}
interface CharacterItem {
  id: string;
  name: string;
  character_info: string;
  // ... các trường khác nếu cần
}
interface VoiceItem {
  id: string;
  voice_actor_name: string;
  voice_actor_info: string;
  // ... các trường khác nếu cần
}

const props = defineProps<{ novel: Novel }>()

const chunkAnnotations = ref<ChunkAnnotation[]>([])
const metadata = ref<MetadataItem[]>([])
const audioRef = ref<HTMLAudioElement|null>(null)
const currentTime = ref(0)
const characters = ref<CharacterItem[]>([])
const voices = ref<VoiceItem[]>([])
const lastCharacterProfile = ref<CharacterProfile|null>(null)
const lastVoiceProfile = ref<VoiceProfile|null>(null)

const currentMeta = computed(() => {
  if (!metadata.value.length) return null
  // Lọc các đoạn có time_start <= currentTime, lấy đoạn cuối cùng
  return [...metadata.value]
    .filter(m => m.time_start <= currentTime.value)
    .sort((a, b) => b.time_start - a.time_start)[0] || null
})

const currentSentenceObj = computed(() => {
  if (!currentMeta.value) return null
  const { index_x, index_y } = currentMeta.value
  const chunk = chunkAnnotations.value.find(c => c.index === index_x)
  if (!chunk || !chunk.parsed_clean) return null
  return chunk.parsed_clean.find((item: SentenceObj) => item.index === index_y) || null
})

const sentenceProgress = computed(() => {
  if (!currentMeta.value || !audioRef.value) return 0
  const { time_start, time_end } = currentMeta.value
  const duration = time_end - time_start
  if (duration <= 0) return 1
  const progress = (currentTime.value - time_start) / duration
  return Math.max(0, Math.min(1, progress))
})

const highlightedSentence = computed(() => {
  if (!currentSentenceObj.value) return { read: '', unread: '' }
  const sentence = currentSentenceObj.value.sentence || ''
  const len = sentence.length
  const numRead = Math.round(len * sentenceProgress.value)
  return {
    read: sentence.slice(0, numRead),
    unread: sentence.slice(numRead)
  }
})

const displayEmotion = computed(() => {
  if (!currentMeta.value || !currentSentenceObj.value) return ''
  if (currentMeta.value.voice_actor === 'Narrator') return 'neutral'
  return currentSentenceObj.value.emotion
})

const currentCharacterProfile = computed(() => {
  if (!currentMeta.value) return lastCharacterProfile.value
  const identity = (currentMeta.value.true_identity || '').trim()
  const found = characters.value.find((c) => (c.name || '').trim() === identity)
  if (found) {
    try {
      const parsed = JSON.parse(found.character_info)
      if (parsed && typeof parsed === 'object' && 'bfi_responses' in parsed) {
        const { bfi_responses, ...rest } = parsed
        return rest
      }
      return parsed
    } catch {
      return lastCharacterProfile.value
    }
  }
  return lastCharacterProfile.value
})

watch(currentCharacterProfile, (val) => {
  if (val) lastCharacterProfile.value = val
})

const currentVoiceProfile = computed(() => {
  if (!currentMeta.value) return lastVoiceProfile.value
  const actor = (currentMeta.value.voice_actor || '').trim().toLowerCase()
  const found = voices.value.find((v) => ((v.voice_actor_name || '').trim().toLowerCase() === actor))
  if (found) {
    try {
      return JSON.parse(found.voice_actor_info)
    } catch {
      return lastVoiceProfile.value
    }
  }
  return lastVoiceProfile.value
})

watch(currentVoiceProfile, (val) => {
  if (val) lastVoiceProfile.value = val
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
    const res = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/audiobook/chunk-annotations/?novel=${novelId}`, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'ngrok-skip-browser-warning': 'true'
      }
    })
    if (!res.ok) throw new Error('Failed to fetch chunk annotations')
    const data = await res.json()
    // Parse clean_text cho từng annotation
    data.forEach((item: ChunkAnnotation) => {
      try {
        item.parsed_clean = JSON.parse(item.clean_text)
      } catch (e) {
        console.error('Failed to parse clean_text', e)
        item.parsed_clean = []
      }
    })
    chunkAnnotations.value = data
    console.log('Chunk annotations:', data)
  } catch (e) {
    console.error(e)
  }
}

async function fetchMetadata(url: string) {
  try {
    const res = await fetch(url, {
      headers: {
      }
    })
    if (!res.ok) throw new Error('Failed to fetch metadata')
    const data = await res.json()
    metadata.value = data
    console.log('Metadata:', data)
  } catch (e) {
    console.error(e)
  }
}

// Lấy danh sách character theo novel_id (API mới backend)
async function fetchCharactersByNovelId(novelId: string) {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/audiobook/characters/?novel_id=${novelId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'ngrok-skip-browser-warning': 'true'
      }
    })
    if (!res.ok) throw new Error('Failed to fetch characters')
    const data = await res.json()
    console.log('Characters:', data)
    return data
  } catch (e) {
    console.error(e)
    return []
  }
}

// Lấy danh sách voice (API mới backend)
async function fetchVoices() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/api/audiobook/voices/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'ngrok-skip-browser-warning': 'true'
      }
    })
    if (!res.ok) throw new Error('Failed to fetch voices')
    const data = await res.json()
    console.log('Voices:', data)
    return data
  } catch (e) {
    console.error(e)
    return []
  }
}

onMounted(() => {
  if (props.novel?.id) {
    fetchChunkAnnotations(props.novel.id)
    fetchCharactersByNovelId(props.novel.id).then(data => { characters.value = data })
  }
  if (props.novel?.s3_audio_metadata_url) fetchMetadata(props.novel.s3_audio_metadata_url)
  fetchVoices().then(data => { voices.value = data })
})

watch(() => props.novel, (n, o) => {
  if (n?.id && n?.id !== o?.id) {
    fetchChunkAnnotations(n.id)
    fetchCharactersByNovelId(n.id).then(data => { characters.value = data })
  }
  if (n?.s3_audio_metadata_url && n?.s3_audio_metadata_url !== o?.s3_audio_metadata_url) fetchMetadata(n.s3_audio_metadata_url)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

.streamer-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-start;
  margin-top: 2.5rem;
  gap: 2.5rem;
}
.profile-box {
  background: #f1f5f9;
  border-radius: 1rem;
  padding: 1.2rem 1.5rem;
  min-width: 286px;
  max-width: 416px;
  box-shadow: 0 2px 8px rgba(14,165,233,0.06);
  font-size: 1.05rem;
  word-break: break-word;
  height: fit-content;
}
.character-profile {
}
.voice-profile {
}
.audiobook-streamer {
  font-family: 'Inter', Arial, sans-serif;
  background: #f8fafc;
  border-radius: 1.5rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 3.5rem 3rem 3rem 3rem;
  margin-top: 0;
  text-align: center;
  max-width: 1120px;
  margin-left: auto;
  margin-right: auto;
  transition: box-shadow 0.2s;
}
.audiobook-streamer:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
}
.audio-missing {
  color: #ef4444;
  margin: 1.5rem 0;
}
.sentence-highlight-box {
  margin: 2.2rem 0 1.2rem 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}
.sentence-highlight {
  font-size: 1.2rem;
  font-weight: 700;
  text-align: justify;
  line-height: 1.6;
  min-height: 2.5rem;
  display: inline-block;
  max-width: 90%;
  margin-left: auto;
  margin-right: auto;
}
.read-part {
  color: #0ea5e9;
  transition: color 0.2s;
}
.unread-part {
  color: #b6c2d1;
  transition: color 0.2s;
}
.current-meta-box {
  margin-top: 2rem;
  background: #e0f2fe;
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  display: inline-block;
  text-align: left;
  box-shadow: 0 2px 8px rgba(14,165,233,0.08);
  min-width: 270px;
  animation: fadeIn 0.7s;
}
.current-meta-box h4 {
  margin-bottom: 1.1rem;
  color: #0ea5e9;
  font-weight: 700;
  font-size: 1.15rem;
  display: flex;
  align-items: center;
}
.meta-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.meta-list li {
  margin-bottom: 0.5rem;
  font-size: 1.08rem;
  color: #334155;
  display: flex;
  align-items: center;
}
.meta-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
  opacity: 0.8;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px);}
  to { opacity: 1; transform: translateY(0);}
}
pre {
  background: #e0e7ef;
  border-radius: 0.5rem;
  padding: 0.7rem 1rem;
  font-size: 0.98rem;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}
</style> 