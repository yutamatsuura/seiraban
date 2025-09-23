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
@import '@/styles/template-settings.scss';

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

// Material Icons Fix
.material-icons {
  font-family: 'Material Icons';
  font-weight: normal;
  font-style: normal;
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
}

// Template Settings Global Styles
.template-settings-view {
  .font-family-grid {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 16px !important;

    @media (max-width: 768px) {
      grid-template-columns: 1fr !important;
    }
  }

  .font-family-card {
    background: white !important;
    border: 2px solid #e9ecef !important;
    border-radius: 12px !important;
    padding: 20px !important;
    text-align: center !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;

    &:hover {
      border-color: #3498db !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }

    &.active {
      border-color: #3498db !important;
      background: rgba(52, 152, 219, 0.05) !important;
      box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2) !important;
    }

    .font-preview {
      font-size: 2rem !important;
      margin-bottom: 12px !important;
      color: #2c3e50 !important;
      line-height: 1 !important;
    }

    .font-name {
      font-weight: 600 !important;
      color: #2c3e50 !important;
      margin-bottom: 4px !important;
    }

    .font-description {
      font-size: 0.85rem !important;
      color: #566573 !important;
    }
  }

  .size-options {
    display: flex !important;
    gap: 16px !important;
    justify-content: center !important;
  }

  .size-option {
    background: white !important;
    border: 2px solid #e9ecef !important;
    border-radius: 12px !important;
    padding: 24px !important;
    text-align: center !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    min-width: 120px !important;

    &:hover {
      border-color: #3498db !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }

    &.active {
      border-color: #3498db !important;
      background: rgba(52, 152, 219, 0.05) !important;
      box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2) !important;
    }
  }

  .typography-grid {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
    gap: 16px !important;
  }

  .enhanced-label .material-icons {
    color: #3498db !important;
    font-size: 1.2rem !important;
  }

  .section-icon {
    color: #3498db !important;
    font-size: 1.5rem !important;
  }
}
</style>