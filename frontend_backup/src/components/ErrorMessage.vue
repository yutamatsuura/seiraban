<template>
  <div v-if="show" class="error-message" :class="[`error-${variant}`, { 'error-dismissible': dismissible }]">
    <div class="error-content">
      <div class="error-icon">
        <span class="material-icons">{{ icon }}</span>
      </div>
      <div class="error-text">
        <div v-if="title" class="error-title">{{ title }}</div>
        <div class="error-message-text">{{ message }}</div>
        <div v-if="details" class="error-details">{{ details }}</div>
      </div>
      <div v-if="retryable && showRetry" class="error-actions">
        <button @click="$emit('retry')" class="btn btn-outline btn-sm" :disabled="retrying">
          <span class="material-icons">refresh</span>
          <span v-if="retrying">再試行中...</span>
          <span v-else>再試行</span>
        </button>
      </div>
      <div v-if="dismissible" class="error-dismiss">
        <button @click="dismiss" class="btn-close">
          <span class="material-icons">close</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  show?: boolean
  message: string
  title?: string
  details?: string
  variant?: 'error' | 'warning' | 'info'
  icon?: string
  retryable?: boolean
  showRetry?: boolean
  retrying?: boolean
  dismissible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  show: true,
  variant: 'error',
  showRetry: true,
  retrying: false,
  dismissible: false
})

const emit = defineEmits<{
  retry: []
  dismiss: []
}>()

const icon = computed(() => {
  if (props.icon) return props.icon

  switch (props.variant) {
    case 'warning':
      return 'warning'
    case 'info':
      return 'info'
    default:
      return 'error'
  }
})

const dismiss = () => {
  emit('dismiss')
}
</script>

<style scoped lang="scss">
.error-message {
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid;

  &.error-error {
    background: rgba(231, 76, 60, 0.1);
    color: #c0392b;
    border-color: rgba(231, 76, 60, 0.2);
  }

  &.error-warning {
    background: rgba(243, 156, 18, 0.1);
    color: #d68910;
    border-color: rgba(243, 156, 18, 0.2);
  }

  &.error-info {
    background: rgba(52, 152, 219, 0.1);
    color: #2980b9;
    border-color: rgba(52, 152, 219, 0.2);
  }

  .error-content {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }

  .error-icon {
    flex-shrink: 0;
    margin-top: 2px;

    .material-icons {
      font-size: 20px;
    }
  }

  .error-text {
    flex: 1;
    min-width: 0;

    .error-title {
      font-weight: 600;
      margin-bottom: 4px;
      font-size: 0.875rem;
    }

    .error-message-text {
      font-size: 0.875rem;
      line-height: 1.4;
    }

    .error-details {
      font-size: 0.75rem;
      margin-top: 8px;
      opacity: 0.8;
      word-break: break-word;
    }
  }

  .error-actions {
    flex-shrink: 0;
  }

  .error-dismiss {
    flex-shrink: 0;
    margin-left: auto;
  }

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

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    &.btn-outline {
      background: transparent;
      border: 1px solid currentColor;

      &:hover:not(:disabled) {
        background: currentColor;
        color: white;
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

  .btn-close {
    background: none;
    border: none;
    color: currentColor;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    opacity: 0.7;
    transition: opacity 0.2s ease;

    &:hover {
      opacity: 1;
    }

    .material-icons {
      font-size: 18px;
    }
  }
}

// レスポンシブ
@media (max-width: 768px) {
  .error-message {
    .error-content {
      flex-direction: column;
      gap: 8px;
    }

    .error-actions,
    .error-dismiss {
      align-self: flex-start;
    }
  }
}
</style>