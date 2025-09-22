<template>
  <div class="logo-switcher">
    <div class="logo-display" @click="showSelector = !showSelector">
      <component
        :is="'img'"
        :src="currentLogoPath"
        alt="星羅盤ロゴ"
        class="logo-image"
      />
      <span class="logo-text">星羅盤</span>
      <span class="logo-subtitle">鑑定書楽々作成ツール</span>
    </div>

    <div v-if="showSelector" class="logo-selector" @click.stop>
      <h3>ロゴを選択</h3>
      <div class="logo-options">
        <div
          v-for="logo in logoOptions"
          :key="logo.id"
          class="logo-option"
          :class="{ active: currentLogo === logo.id }"
          @click="selectLogo(logo.id)"
        >
          <img :src="logo.path" :alt="logo.name" class="option-image" />
          <span class="option-name">{{ logo.name }}</span>
        </div>
      </div>
      <button @click="showSelector = false" class="close-button">閉じる</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface LogoOption {
  id: string
  name: string
  path: string
}

const currentLogo = ref('dots-constellation')
const showSelector = ref(false)

const logoOptions: LogoOption[] = [
  { id: 'minimal-dot', name: 'ミニマルドット', path: '/src/assets/icons/logo-minimal-dot.svg' },
  { id: 'dots-triangle', name: 'ドット三角', path: '/src/assets/icons/logo-dots-triangle.svg' },
  { id: 'dots-constellation', name: 'ドット星座', path: '/src/assets/icons/logo-dots-constellation.svg' },
  { id: 'dots-grid', name: 'ドットグリッド', path: '/src/assets/icons/logo-dots-grid.svg' },
  { id: 'geometric', name: '幾何学', path: '/src/assets/icons/logo-geometric.svg' }
]

const currentLogoPath = computed(() => {
  const logo = logoOptions.find(l => l.id === currentLogo.value)
  return logo ? logo.path : logoOptions[0].path
})

const selectLogo = (logoId: string) => {
  currentLogo.value = logoId
  showSelector.value = false
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.logo-switcher {
  position: relative;
}

.logo-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);

  &:hover {
    background: rgba(52, 73, 94, 0.05);
  }

  .logo-image {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
  }

  .logo-text {
    font-size: 1.25rem;
    font-weight: $font-weight-bold;
    color: var(--text-primary);
    line-height: 1.2;
  }

  .logo-subtitle {
    font-size: 0.75rem;
    color: var(--text-secondary);
    position: absolute;
    top: 32px;
    left: 60px;
  }
}

.logo-selector {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--background-paper);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 1000;
  min-width: 300px;

  h3 {
    margin: 0 0 var(--spacing-md) 0;
    font-size: 1rem;
    font-weight: $font-weight-medium;
    color: var(--text-primary);
  }

  .logo-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
  }

  .logo-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-md);
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);

    &:hover {
      border-color: var(--primary-main);
      background: rgba(52, 73, 94, 0.05);
    }

    &.active {
      border-color: var(--primary-main);
      background: rgba(52, 73, 94, 0.1);
    }

    .option-image {
      width: 40px;
      height: 40px;
    }

    .option-name {
      font-size: 0.75rem;
      font-weight: $font-weight-medium;
      color: var(--text-primary);
      text-align: center;
    }
  }

  .close-button {
    width: 100%;
    padding: 10px 16px;
    background: var(--primary-main);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    font-weight: $font-weight-medium;
    cursor: pointer;
    transition: all var(--transition-fast);

    &:hover {
      background: var(--primary-dark);
    }
  }
}
</style>