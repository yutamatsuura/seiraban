<template>
  <div class="app-layout">
    <!-- サイドバー -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="brand">
        <div class="brand-title">sindankantei</div>
      </div>

      <nav class="nav">
        <ul class="nav-list">
          <li class="nav-item" v-for="item in navItems" :key="item.path">
            <router-link
              :to="item.path"
              class="nav-link"
              :class="{ active: isActive(item.path) }"
            >
              <span class="material-icons nav-icon">{{ item.icon }}</span>
              <span class="nav-text">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <span class="material-icons">account_circle</span>
          </div>
          <div class="user-details">
            <div class="user-name">{{ userStore.user?.business_name || 'ゲスト' }}</div>
            <div class="user-email">{{ userStore.user?.email || '' }}</div>
          </div>
        </div>
        <button @click="handleLogout" class="logout-btn">
          <span class="material-icons">logout</span>
        </button>
      </div>
    </aside>

    <!-- メインコンテンツ -->
    <div class="main-wrapper">
      <!-- ヘッダー -->
      <header class="app-header">
        <button @click="toggleSidebar" class="menu-toggle">
          <span class="material-icons">menu</span>
        </button>

        <div class="header-title">
          <h1>{{ currentPageTitle }}</h1>
        </div>

        <div class="header-actions">
          <button class="icon-btn">
            <span class="material-icons">notifications</span>
            <span class="badge-dot" v-if="hasNotifications"></span>
          </button>
          <button class="icon-btn">
            <span class="material-icons">help_outline</span>
          </button>
        </div>
      </header>

      <!-- ページコンテンツ -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- モバイルオーバーレイ -->
    <div
      v-if="sidebarOpen && isMobile"
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// サイドバー状態
const sidebarCollapsed = ref(false)
const sidebarOpen = ref(false)
const isMobile = ref(false)

// 通知
const hasNotifications = ref(false)

// ナビゲーションアイテム
const navItems = [
  {
    path: '/dashboard',
    label: 'ダッシュボード',
    icon: 'dashboard'
  },
  {
    path: '/kantei/new',
    label: '鑑定書作成',
    icon: 'description'
  },
  {
    path: '/kantei/preview',
    label: 'プレビュー・送信',
    icon: 'send'
  },
  {
    path: '/kantei/history',
    label: '鑑定履歴',
    icon: 'history'
  },
  {
    path: '/settings/template',
    label: 'テンプレート設定',
    icon: 'palette'
  },
  {
    path: '/settings/account',
    label: 'アカウント設定',
    icon: 'settings'
  }
]

// 現在のページタイトル
const currentPageTitle = computed(() => {
  const currentItem = navItems.find(item => route.path.startsWith(item.path))
  return currentItem?.label || 'sindankantei'
})

// アクティブ判定
const isActive = (path: string) => {
  return route.path.startsWith(path)
}

// サイドバー制御
const toggleSidebar = () => {
  if (isMobile.value) {
    sidebarOpen.value = !sidebarOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

// ログアウト
const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('ログアウトエラー:', error)
  }
}

// レスポンシブ対応
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped lang="scss">
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--background-default);
}

// サイドバー
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--background-paper);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 1000;
  transition: transform 0.3s ease, width 0.3s ease;

  &.sidebar-collapsed {
    width: 64px;

    .brand-title {
      display: none;
    }

    .nav-text {
      display: none;
    }

    .user-details {
      display: none;
    }
  }
}

.brand {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);

  .brand-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-main);
  }
}

.nav {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
}

.nav-list {
  list-style: none;
}

.nav-item {
  margin-bottom: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 4px solid transparent;

  &:hover {
    background-color: var(--background-paper);
    border-left-color: var(--primary-light);
  }

  &.active {
    background-color: rgba(52, 73, 94, 0.05);
    border-left-color: var(--primary-main);
    color: var(--primary-main);
    font-weight: 600;
  }
}

.nav-icon {
  margin-right: 12px;
  font-size: 20px;
  min-width: 20px;
}

.nav-text {
  white-space: nowrap;
}

// サイドバーフッター
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.user-avatar {
  margin-right: 12px;

  .material-icons {
    font-size: 32px;
    color: var(--text-secondary);
  }
}

.user-details {
  flex: 1;
  overflow: hidden;

  .user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-email {
    font-size: 0.75rem;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.logout-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--border-radius);
  transition: all 0.2s ease;

  &:hover {
    background-color: var(--background-default);
    color: var(--error-main);
  }

  .material-icons {
    font-size: 20px;
  }
}

// メインラッパー
.main-wrapper {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

// ヘッダー
.app-header {
  height: var(--header-height);
  background-color: var(--background-paper);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: 8px;
  margin-right: 16px;
  border-radius: var(--border-radius);

  &:hover {
    background-color: var(--background-default);
  }

  .material-icons {
    font-size: 24px;
  }
}

.header-title {
  flex: 1;

  h1 {
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--text-primary);
    margin: 0;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  position: relative;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--border-radius);
  transition: all 0.2s ease;

  &:hover {
    background-color: var(--background-default);
    color: var(--text-primary);
  }

  .material-icons {
    font-size: 20px;
  }

  .badge-dot {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 8px;
    height: 8px;
    background-color: var(--error-main);
    border-radius: 50%;
  }
}

// メインコンテンツ
.main-content {
  flex: 1;
  padding: 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

// モバイルオーバーレイ
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

// レスポンシブ
@media (max-width: 1200px) {
  .sidebar.sidebar-collapsed ~ .main-wrapper {
    margin-left: 64px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);

    &.sidebar-open {
      transform: translateX(0);
    }
  }

  .main-wrapper {
    margin-left: 0;
  }

  .menu-toggle {
    display: block;
  }

  .main-content {
    padding: 16px;
  }
}
</style>