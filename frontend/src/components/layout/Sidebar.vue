<template>
  <aside class="sidebar">
    <!-- ロゴセクション -->
    <router-link to="/dashboard" class="sidebar-logo">
      <div class="logo-display">
        <img src="/src/assets/icons/logo-dots-constellation.svg" alt="運命織ロゴ" class="logo-image" />
        <div class="logo-text-wrapper">
          <span class="logo-text">運命織</span>
          <span class="logo-subtitle">鑑定書楽々作成ツール</span>
        </div>
      </div>
    </router-link>

    <!-- ナビゲーションメニュー -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <img v-if="item.iconPath" :src="item.iconPath" :alt="item.label" class="nav-icon-svg" />
        <span v-else class="nav-icon">{{ item.icon }}</span>
        <div class="nav-content">
          <span class="nav-text">{{ item.label }}</span>
          <span class="nav-description">{{ item.description }}</span>
        </div>
      </router-link>
    </nav>

    <!-- ユーザーセクション -->
    <div class="sidebar-user">
      <div class="user-info">
        <div class="user-avatar">
          <img src="/src/assets/icons/user-avatar.svg" alt="ユーザーアバター" class="user-avatar-icon" />
        </div>
        <div class="user-details">
          <p class="user-name">{{ userName }}</p>
          <p class="user-role">{{ userRole }}</p>
        </div>
      </div>
      <button @click="handleLogout" class="logout-button">
        ログアウト
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// メニュー項目
const menuItems = [
  {
    path: '/dashboard',
    iconPath: '/src/assets/icons/dashboard.svg',
    label: 'ダッシュボード',
    description: '統計とシステム概要'
  },
  {
    path: '/kantei/new',
    iconPath: '/src/assets/icons/document-create.svg',
    label: '鑑定書作成',
    description: '新規作成・PDF出力'
  },
  {
    path: '/kantei/list',
    iconPath: '/src/assets/icons/document-list.svg',
    label: '鑑定履歴',
    description: '過去の結果を管理'
  },
  {
    path: '/kantei/templates',
    iconPath: '/src/assets/icons/template.svg',
    label: 'テンプレート設定',
    description: '鑑定書デザイン調整'
  },
  {
    path: '/profile',
    iconPath: '/src/assets/icons/user-profile.svg',
    label: 'マイページ',
    description: 'アカウント設定'
  },
  {
    path: '/admin',
    iconPath: '/src/assets/icons/admin-settings.svg',
    label: '管理者ページ',
    description: 'ユーザー・システム管理'
  }
]

// ユーザー情報（実際のログインユーザー情報を使用）
const userName = computed(() => {
  if (userStore.user?.operator_name) {
    return userStore.user.operator_name
  }
  if (userStore.user?.business_name) {
    return userStore.user.business_name
  }
  return userStore.user?.email || ''
})

const userRole = computed(() => {
  if (userStore.user?.withdrawal_status === 'withdrawn') {
    return '退会済'
  }
  return userStore.isSuperuser ? '管理者' : '一般ユーザー'
})

const userInitial = computed(() => userName.value ? userName.value[0] : 'G')

// アクティブ判定
const isActive = (path: string) => {
  return route.path.startsWith(path)
}

// ログアウト処理
const handleLogout = async () => {
  if (confirm('ログアウトしますか？')) {
    try {
      await userStore.logout()
      router.push('/login')
    } catch (error) {
      console.error('ログアウトエラー:', error)
      // エラーが発生してもログイン画面に遷移
      router.push('/login')
    }
  }
}
</script>

<style scoped lang="scss">
// variables.scss は App.vue でグローバル読み込み済み

.sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
  box-shadow: 4px 0 20px rgba(44, 62, 80, 0.08);
  border-right: 1px solid rgba(222, 226, 230, 0.6);
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 100;
}

// ロゴセクション
.sidebar-logo {
  display: block;
  text-decoration: none;
  padding: var(--spacing-md) var(--spacing-md);
  margin: var(--spacing-md) var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.8;
  }

  .logo-display {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    justify-content: flex-start;

    .logo-image {
      width: 48px;
      height: 48px;
      border-radius: var(--radius-md);
      flex-shrink: 0;
    }

    .logo-text-wrapper {
      display: flex;
      flex-direction: column;
      align-items: flex-start;

      .logo-text {
        display: block;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--primary-main);
        line-height: 1.2;
        margin-bottom: 4px;
        font-family: 'Yu Mincho', 'YuMincho', 'Hiragino Mincho Pro', 'MS PMincho', serif;
        letter-spacing: 0.1em;
      }

      .logo-subtitle {
        display: block;
        font-size: 0.7rem;
        color: var(--text-secondary);
        line-height: 1.2;
        font-weight: 400;
      }
    }
  }
}

// ナビゲーションメニュー
.sidebar-nav {
  flex: 1;
  padding: var(--spacing-sm) 0;

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: 14px var(--spacing-lg);
    margin: 0 var(--spacing-md);
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.95rem;
    transition: all var(--transition-elegant);
    border-radius: var(--radius-lg);
    position: relative;
    overflow: hidden;
    min-height: 60px;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(44, 62, 80, 0.05), transparent);
      transition: left 0.6s ease;
    }

    &:hover::before {
      left: 100%;
    }

    &:hover {
      background: var(--background-elegant);
      color: var(--text-primary);
      box-shadow: var(--shadow-elegant);
      transform: translateY(-2px);

      .nav-icon-svg {
        opacity: 1;
      }
    }

    &.active {
      background: linear-gradient(135deg, var(--primary-main), var(--primary-dark));
      color: white;
      box-shadow: 0 6px 20px rgba(44, 62, 80, 0.25);
      transform: translateY(-2px);

      .nav-icon-svg {
        opacity: 1;
        filter: brightness(0) invert(1);
      }

      .nav-description {
        color: rgba(255, 255, 255, 0.8);
      }
    }

    .nav-icon {
      font-size: 1.25rem;
      width: 24px;
      text-align: center;
    }

    .nav-icon-svg {
      width: 24px;
      height: 24px;
      opacity: 0.7;
      transition: opacity var(--transition-fast);
    }

    .nav-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .nav-text {
      font-weight: 600;
      font-size: 0.85rem;
      line-height: 1.3;
    }

    .nav-description {
      font-size: 0.65rem;
      color: rgba(108, 117, 125, 0.7);
      line-height: 1.1;
      font-weight: 400;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

// ユーザーセクション
.sidebar-user {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  background: var(--background-default);

  .user-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);

    .user-avatar {
      width: 40px;
      height: 40px;
      background: var(--background-paper);
      border: 1px solid var(--border-color);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;

      .user-avatar-icon {
        width: 32px;
        height: 32px;
        opacity: 0.8;
      }
    }

    .user-details {
      flex: 1;

      .user-name {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.3;
      }

      .user-role {
        font-size: 0.7rem;
        color: var(--text-secondary);
        margin: 0;
      }
    }
  }

  .logout-button {
    width: 100%;
    padding: 10px 16px;
    background: var(--background-paper);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);

    &:hover {
      background: var(--error-main);
      color: white;
      border-color: var(--error-main);
    }
  }
}

// レスポンシブ対応
@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-normal);

    &.mobile-open {
      transform: translateX(0);
    }
  }
}
</style>