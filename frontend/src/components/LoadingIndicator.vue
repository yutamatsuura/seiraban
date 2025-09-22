<template>
  <div v-if="show" class="loading-indicator" :class="[`loading-${variant}`, `loading-${size}`]">
    <div class="loading-content">
      <!-- スピナー -->
      <div v-if="type === 'spinner'" class="loading-spinner">
        <div class="spinner-circle"></div>
      </div>

      <!-- ドット -->
      <div v-else-if="type === 'dots'" class="loading-dots">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>

      <!-- プルス -->
      <div v-else-if="type === 'pulse'" class="loading-pulse">
        <div class="pulse-circle"></div>
      </div>

      <!-- プログレスバー -->
      <div v-else-if="type === 'progress'" class="loading-progress">
        <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
      </div>

      <!-- スケルトン -->
      <div v-else-if="type === 'skeleton'" class="loading-skeleton">
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line medium"></div>
      </div>

      <!-- テキスト表示 -->
      <div v-if="message" class="loading-message">
        {{ message }}
      </div>

      <!-- プログレス表示 -->
      <div v-if="showProgress && progress !== undefined" class="loading-progress-text">
        {{ Math.round(progress) }}%
      </div>

      <!-- 経過時間 -->
      <div v-if="showElapsed && elapsed" class="loading-elapsed">
        {{ formatElapsed(elapsed) }}
      </div>

      <!-- キャンセルボタン -->
      <div v-if="cancellable" class="loading-actions">
        <button @click="$emit('cancel')" class="btn btn-outline btn-sm">
          <span class="material-icons">close</span>
          キャンセル
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  show?: boolean
  type?: 'spinner' | 'dots' | 'pulse' | 'progress' | 'skeleton'
  variant?: 'default' | 'overlay' | 'inline' | 'card'
  size?: 'sm' | 'md' | 'lg'
  message?: string
  progress?: number
  showProgress?: boolean
  showElapsed?: boolean
  cancellable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  show: true,
  type: 'spinner',
  variant: 'default',
  size: 'md',
  showProgress: false,
  showElapsed: false,
  cancellable: false
})

const emit = defineEmits<{
  cancel: []
}>()

const elapsed = ref(0)
let elapsedInterval: number | null = null

// 経過時間の計測
onMounted(() => {
  if (props.showElapsed) {
    elapsedInterval = setInterval(() => {
      elapsed.value += 1
    }, 1000) as any
  }
})

onUnmounted(() => {
  if (elapsedInterval) {
    clearInterval(elapsedInterval)
  }
})

const formatElapsed = (seconds: number) => {
  if (seconds < 60) {
    return `${seconds}秒`
  }
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}分${remainingSeconds}秒`
}
</script>

<style scoped lang="scss">
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;

  &.loading-default {
    padding: 24px;
  }

  &.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9999;
    backdrop-filter: blur(2px);
  }

  &.loading-inline {
    padding: 12px;
  }

  &.loading-card {
    padding: 32px;
    background: white;
    border-radius: 8px;
    box-shadow: var(--shadow-2);
    border: 1px solid var(--border-color);
  }

  &.loading-sm {
    .loading-content {
      scale: 0.8;
    }
  }

  &.loading-lg {
    .loading-content {
      scale: 1.2;
    }
  }

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    text-align: center;
  }

  .loading-message {
    color: var(--text-secondary);
    font-size: 0.875rem;
    font-weight: 500;
  }

  .loading-progress-text {
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-weight: 600;
  }

  .loading-elapsed {
    color: var(--text-disabled);
    font-size: 0.75rem;
  }

  .loading-actions {
    margin-top: 8px;
  }
}

// スピナー
.loading-spinner {
  .spinner-circle {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color);
    border-top: 3px solid var(--primary-main);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

// ドット
.loading-dots {
  display: flex;
  gap: 6px;

  .dot {
    width: 8px;
    height: 8px;
    background: var(--primary-main);
    border-radius: 50%;
    animation: dot-pulse 1.4s ease-in-out infinite both;

    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }
}

// パルス
.loading-pulse {
  .pulse-circle {
    width: 40px;
    height: 40px;
    background: var(--primary-main);
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }
}

// プログレスバー
.loading-progress {
  width: 200px;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;

  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-main), var(--primary-light));
    border-radius: 2px;
    transition: width 0.3s ease;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
      );
      animation: shimmer 1.5s infinite;
    }
  }
}

// スケルトン
.loading-skeleton {
  width: 100%;
  max-width: 300px;

  .skeleton-line {
    height: 16px;
    background: linear-gradient(
      90deg,
      var(--border-color) 25%,
      var(--background-paper) 50%,
      var(--border-color) 75%
    );
    background-size: 200% 100%;
    border-radius: 4px;
    margin-bottom: 8px;
    animation: skeleton-loading 1.5s infinite;

    &.short {
      width: 60%;
    }

    &.medium {
      width: 80%;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }
}

// ボタンスタイル
.btn {
  padding: 6px 12px;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;

  &.btn-outline {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-color);

    &:hover {
      background: var(--background-default);
      border-color: var(--primary-main);
      color: var(--primary-main);
    }
  }

  &.btn-sm {
    padding: 4px 8px;
    font-size: 0.75rem;
  }

  .material-icons {
    font-size: 16px;
  }
}

// アニメーション
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes dot-pulse {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.1);
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

// レスポンシブ
@media (max-width: 768px) {
  .loading-indicator {
    &.loading-overlay .loading-content {
      max-width: 90%;
      margin: 0 auto;
    }
  }

  .loading-progress {
    width: 150px;
  }
}
</style>