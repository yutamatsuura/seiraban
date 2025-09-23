<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(async () => {
  await userStore.initialize()
})
</script>

<template>
  <div class="app">
    <RouterView />
  </div>
</template>

<style lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/components.scss';
@import '@/styles/themes/minimal.scss';
@import '@/styles/themes/elegant.scss';
@import '@/styles/themes/modern.scss';
@import '@/styles/diagnosis-templates.scss';

// Global base styles
* {
  box-sizing: border-box;
}

html {
  font-size: 16px;
  font-family: $font-family-sans;
  line-height: var(--line-height-base);
}

body {
  margin: 0;
  padding: 0;
  background: var(--background-default);
  color: var(--text-primary);
  font-size: var(--font-size-base);
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// Global reset
h1, h2, h3, h4, h5, h6 {
  margin: 0;
  line-height: var(--line-height-tight);
}

p {
  margin: 0;
  line-height: var(--line-height-base);
}

a {
  color: var(--primary-main);
  text-decoration: none;
  transition: color var(--transition-fast);

  &:hover {
    color: var(--primary-dark);
  }
}

button {
  font-family: inherit;
}

input, textarea, select {
  font-family: inherit;
  font-size: inherit;
}
</style>