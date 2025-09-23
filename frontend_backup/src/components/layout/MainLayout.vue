<template>
  <div class="main-layout">
    <!-- サイドバー -->
    <Sidebar />

    <!-- メインコンテンツエリア -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.main-layout {
  display: flex;
  min-height: 100vh;
  background: var(--background-page);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: 0;
  overflow-y: auto;

  // レスポンシブ対応
  @media (max-width: $breakpoint-md) {
    margin-left: 0;
    padding: 0;
  }
}
</style>