<template>
  <div>
    <AppHeader />
    <main>
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/AppHeader.vue'
import AppFooter from '~/components/AppFooter.vue'
</script>

<style scoped>
main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(120deg, #f8fbff 0%, #e0f2fe 100%);
}
</style> 