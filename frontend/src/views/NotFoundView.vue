<template>
  <div class="not-found">
    <h1>404 - ページが見つかりません</h1>
    <p>お探しのページは存在しません。</p>
    <router-link to="/dashboard" class="btn">ダッシュボードに戻る</router-link>
  </div>
</template>

<script setup lang="ts">
// 実装予定
</script>

<style scoped>
.not-found {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  padding: 4rem 2rem;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  background: var(--primary-main);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  margin-top: 1rem;
}
</style>