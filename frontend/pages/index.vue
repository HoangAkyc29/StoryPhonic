<template>
  <div class="landing">
    <!-- Hero Section -->
    <header class="hero">
      <div class="logo-title">
        <img src="/logo-storyphonic.svg" alt="Story Phonic Logo" class="logo" />
        <h1>Story Phonic</h1>
      </div>
      <h2 class="slogan">Turn your book into a multicast AI audiobook in minutes</h2>
      <p class="desc">Create professional audiobooks with multiple natural AI voices. Fast, easy, and ready to share.</p>
      <button class="cta-btn" @click="handleStart">Start for free</button>
    </header>

    <!-- Features Section -->
    <section class="features" id="features">
      <h3>Key Features</h3>
      <div class="feature-list">
        <div class="feature-item">
          <div class="icon">🔊</div>
          <h4>Multicast Voiceover</h4>
          <p>Assign different AI voices to each character for a vivid listening experience.</p>
        </div>
        <div class="feature-item">
          <div class="icon">⚡</div>
          <h4>Fast & Easy</h4>
          <p>Just a few steps to publish a professional audiobook. No technical skills required.</p>
        </div>
        <div class="feature-item">
          <div class="icon">🎧</div>
          <h4>High-Quality Audio</h4>
          <p>Export studio-quality audio files ready for any platform.</p>
        </div>
        <div class="feature-item">
          <div class="icon">📚</div>
          <h4>Flexible Text Input</h4>
          <p>Paste, upload, or write your story directly in the app.</p>
        </div>
      </div>
    </section>

    <!-- Demo Section -->
    <section class="demo-section">
      <h3>Live Demo</h3>
      <div class="demo-box">
        <div class="demo-text">
          <span
            class="highlight-gradient"
            :style="{
              background: `linear-gradient(90deg, #0ea5e9 ${highlightPercent}%, #111 ${highlightPercent}%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              color: 'transparent',
              transition: 'background 0.05s linear'
            }"
          >{{ demoText }}</span>
        </div>
        <audio ref="audioRef" :src="demoAudio" @play="onPlay" @pause="onPause" @ended="onEnded" @timeupdate="onTimeUpdate" @loadedmetadata="onLoadedMetadata"></audio>
        <button class="audio-btn" @click="toggleAudio">
          <span v-if="!isPlaying">▶ Play Demo</span>
          <span v-else>⏸ Pause</span>
        </button>
      </div>
      <p class="demo-caption">Try it yourself with your own text after signing up!</p>
    </section>

    <!-- Pricing Section (summary) -->
    <section class="pricing-summary">
      <h3>Pricing</h3>
      <div class="pricing-cards">
        <div class="pricing-card">
          <h4>Free</h4>
          <div class="price">$0<span>/mo</span></div>
          <ul>
            <li>1 hour audio/month</li>
            <li>Basic AI voices</li>
          </ul>
        </div>
        <div class="pricing-card pro">
          <h4>Pro</h4>
          <div class="price">$19<span>/mo</span></div>
          <ul>
            <li>20 hours audio/month</li>
            <li>Premium voices</li>
            <li>Multicast voiceover</li>
          </ul>
        </div>
        <div class="pricing-card enterprise">
          <h4>Enterprise</h4>
          <div class="price">Custom</div>
          <ul>
            <li>Unlimited audio</li>
            <li>Custom voices</li>
          </ul>
        </div>
      </div>
      <NuxtLink to="/pricing" class="cta-btn pricing-btn">See all plans</NuxtLink>
    </section>

    <section class="illustration">
      <img src="/audiobook-illustration.svg" alt="Audiobook Illustration" />
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '~/composables/useAuth'

const { user } = auth
const router = useRouter()

const handleStart = () => {
  if (user.value) {
    router.push('/dashboard')
  } else {
    router.push('/signup')
  }
}

const demoText = `If you do anything to her I'll curse you and all of your off- spring, you know?`
const demoAudio = '/sample-audio.wav' // Placeholder, replace with real audio
const audioRef = ref(null)
const isPlaying = ref(false)
const audioDuration = ref(1)
const currentTime = ref(0)

const highlightPercent = computed(() => {
  // Bỏ qua 0.2s đầu
  const t = Math.max(0, currentTime.value)
  const d = Math.max(0.1, audioDuration.value)
  const percent = Math.min(1, t / d)
  return (percent * 100).toFixed(2)
})

function toggleAudio() {
  if (!audioRef.value) return
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play()
  }
}
function onPlay() {
  isPlaying.value = true
}
function onPause() {
  isPlaying.value = false
}
function onEnded() {
  isPlaying.value = false
  currentTime.value = 0
}
function onLoadedMetadata(e) {
  audioDuration.value = e.target.duration || 1
}
function onTimeUpdate(e) {
  currentTime.value = e.target.currentTime
}
</script>

<style scoped>
.landing {
  background: #fff;
  color: #111;
  min-height: 100vh;
  font-family: 'Inter', Arial, sans-serif;
}
.hero {
  text-align: center;
  padding: 3rem 1rem 2rem 1rem;
  background: linear-gradient(90deg, #e0f2fe 0%, #38bdf8 100%);
}
.logo-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}
.logo {
  width: 48px;
  height: 48px;
}
.slogan {
  font-size: 2rem;
  margin: 1.5rem 0 0.5rem 0;
  color: #0ea5e9;
}
.desc {
  font-size: 1.1rem;
  color: #222;
  margin-bottom: 1.5rem;
}
.cta-btn {
  display: inline-block;
  background: #0ea5e9;
  color: #fff;
  padding: 0.75rem 2rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 1.1rem;
  text-decoration: none;
  transition: background 0.2s;
}
.cta-btn:hover {
  background: #0369a1;
}
.features {
  padding: 2.5rem 1rem 1.5rem 1rem;
  background: #f8fafc;
  text-align: center;
}
.features h3 {
  font-size: 1.5rem;
  color: #0ea5e9;
  margin-bottom: 2rem;
}
.feature-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
}
.feature-item {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(56,189,248,0.08);
  padding: 1.5rem 1.2rem;
  width: 260px;
  max-width: 90vw;
  text-align: center;
}
.icon {
  font-size: 2.2rem;
  margin-bottom: 0.5rem;
}
.demo-section {
  background: #e0f2fe;
  padding: 2.5rem 1rem 2rem 1rem;
  text-align: center;
}
.demo-section h3 {
  color: #0ea5e9;
  font-size: 1.4rem;
  margin-bottom: 1.2rem;
}
.demo-box {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(56,189,248,0.08);
  padding: 2rem 1.5rem 1.5rem 1.5rem;
  max-width: 600px;
  margin: 0 auto 1.2rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.demo-text {
  font-size: 1.2rem;
  margin-bottom: 1.2rem;
  min-height: 2.5rem;
  line-height: 2.2rem;
  word-break: break-word;
  text-align: left;
  width: 100%;
  max-width: 500px;
  background: #f8fafc;
  border-radius: 0.5rem;
  padding: 0.7rem 1rem;
  transition: box-shadow 0.2s;
  letter-spacing: 0.01em;
}
.highlight-gradient {
  font-weight: 600;
  background: linear-gradient(90deg, #0ea5e9 0%, #111 0%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
  transition: background 0.05s linear;
}
.audio-btn {
  background: #0ea5e9;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.7rem 2.2rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.audio-btn:hover {
  background: #0369a1;
}
.demo-caption {
  color: #555;
  margin-top: 0.7rem;
}
.pricing-summary {
  background: #f8fafc;
  padding: 2.5rem 1rem 2rem 1rem;
  text-align: center;
}
.pricing-summary h3 {
  color: #0ea5e9;
  font-size: 1.4rem;
  margin-bottom: 1.2rem;
}
.pricing-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.pricing-card {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(56,189,248,0.08);
  padding: 1.5rem 1.2rem;
  width: 220px;
  max-width: 90vw;
  text-align: center;
  border: 2px solid #e0f2fe;
}
.pricing-card.pro {
  border: 2px solid #0ea5e9;
}
.pricing-card.enterprise {
  border: 2px dashed #38bdf8;
}
.pricing-card h4 {
  color: #0ea5e9;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}
.price {
  font-size: 1.4rem;
  font-weight: bold;
  color: #222;
  margin-bottom: 0.7rem;
}
.price span {
  font-size: 0.9rem;
  color: #888;
  font-weight: 400;
}
.pricing-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
}
.pricing-card ul li {
  margin-bottom: 0.5rem;
  color: #333;
  font-size: 0.98rem;
  padding-left: 1.1rem;
  position: relative;
}
.pricing-card ul li:before {
  content: '✔';
  color: #0ea5e9;
  position: absolute;
  left: 0;
  font-size: 0.98rem;
}
.pricing-btn {
  margin-top: 0.5rem;
}
.illustration {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0 3rem 0;
}
.illustration img {
  width: 320px;
  max-width: 90vw;
  opacity: 0.95;
}
</style> 