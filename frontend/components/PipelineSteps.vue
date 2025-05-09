<template>
  <div class="pipeline-steps">
    <div v-for="(step, idx) in steps" :key="idx" class="step-row">
      <div :class="['step-circle', { active: idx+1 === currentStep, done: idx+1 < currentStep }]">
        <span v-if="idx+1 < currentStep">✔</span>
        <span v-else>{{ idx+1 }}</span>
      </div>
      <div class="step-info">
        <div :class="['step-title', { active: idx+1 === currentStep }]">{{ step }}</div>
        <div v-if="idx+1 === currentStep" class="step-status">Current step: {{ status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ currentStep: number, status: string }>()
const steps = [
  'Document Chunking',
  'Context Memory Management',
  'Annotation Generation',
  'Character Trait Assessment',
  'Voice Assignment',
  'Text To Speech',
  'Audio Post-processing',
  'Output Audio'
]
</script>

<style scoped>
.pipeline-steps {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem 0;
  max-width: 400px;
  margin: 0 auto;
}
.step-row {
  display: flex;
  align-items: flex-start;
  gap: 1.2rem;
}
.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e7ef;
  color: #0ea5e9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  border: 2px solid #e0e7ef;
  transition: background 0.2s, border 0.2s;
}
.step-circle.active {
  background: #0ea5e9;
  color: #fff;
  border: 2px solid #0ea5e9;
}
.step-circle.done {
  background: #38bdf8;
  color: #fff;
  border: 2px solid #38bdf8;
}
.step-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.step-title {
  font-size: 1.08rem;
  font-weight: 600;
  color: #222;
}
.step-title.active {
  color: #0ea5e9;
}
.step-status {
  font-size: 0.95rem;
  color: #0ea5e9;
  margin-top: 0.2rem;
}
</style> 