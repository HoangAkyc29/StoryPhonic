<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('cancel')">&times;</button>
      <template v-if="type === 'name'">
        <h3>Name your new project</h3>
        <input v-model="inputName" class="modal-input" type="text" placeholder="Enter project name..." />
        <div class="modal-actions">
          <button class="modal-btn" @click="$emit('confirm', inputName)" :disabled="!inputName.trim()">Confirm</button>
        </div>
      </template>
      <template v-else-if="type === 'delete'">
        <h3>Delete project</h3>
        <p>Are you sure you want to delete <b>{{ projectName }}</b>? This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="modal-btn danger" @click="$emit('confirm')">Delete</button>
          <button class="modal-btn" @click="$emit('cancel')">Cancel</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ visible: boolean, type: 'name' | 'delete', projectName?: string }>()
const emit = defineEmits(['confirm', 'cancel'])
const inputName = ref('')
watch(() => props.visible, v => { if (v && props.type === 'name') inputName.value = '' })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  padding: 2rem 2.5rem 1.5rem 2.5rem;
  min-width: 320px;
  max-width: 90vw;
  position: relative;
  text-align: center;
}
.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #888;
  cursor: pointer;
}
.modal-input {
  width: 100%;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: 1px solid #e0e7ef;
  font-size: 1.1rem;
  margin: 1.2rem 0 0.5rem 0;
}
.modal-actions {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  margin-top: 1.2rem;
}
.modal-btn {
  background: #0ea5e9;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.5rem 1.5rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-btn:disabled {
  background: #b6e0fa;
  cursor: not-allowed;
}
.modal-btn.danger {
  background: #ef4444;
}
.modal-btn.danger:hover {
  background: #b91c1c;
}
.modal-btn:hover:not(:disabled):not(.danger) {
  background: #0369a1;
}
</style> 