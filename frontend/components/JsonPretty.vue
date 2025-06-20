<template>
  <div class="json-pretty">
    <template v-for="(value, key) in data" :key="key">
      <div v-if="typeof value === 'object' && value !== null && !Array.isArray(value)">
        <div class="json-key">{{ key }}:</div>
        <div class="json-nested">
          <JsonPretty :data="value" />
        </div>
      </div>
      <div v-else-if="Array.isArray(value)">
        <div class="json-key">{{ key }}:</div>
        <ul class="json-array">
          <li v-for="(item, idx) in value" :key="idx">
            <JsonPretty :data="item" />
          </li>
        </ul>
      </div>
      <div v-else>
        <span class="json-key">{{ key }}:</span>
        <span class="json-value">{{ value }}</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{ data: any }>()
</script>

<style scoped>
.json-pretty { font-size: 1rem; }
.json-key { font-weight: 600; color: #0ea5e9; margin-right: 0.3em; }
.json-value { color: #334155; }
.json-nested { margin-left: 1em; border-left: 2px solid #e0e7ef; padding-left: 0.7em; }
.json-array { margin: 0.2em 0 0.2em 1.2em; padding: 0; list-style: disc; }
</style> 