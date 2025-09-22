import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

// ルート設定
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      requiresAuth: false,
      hideLayout: true // レイアウトを非表示
    }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/kantei/new',
    name: 'NewKantei',
    component: () => import('@/views/kantei/NewKanteiView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/kantei/preview/:id?',
    name: 'PreviewKantei',
    component: () => import('@/views/kantei/PreviewView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/kantei/list',
    name: 'KanteiHistory',
    component: () => import('@/views/kantei/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/kantei/templates',
    name: 'TemplateSettings',
    component: () => import('@/views/kantei/TemplateSettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings/account',
    name: 'AccountSettings',
    component: () => import('@/views/settings/AccountSettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { requiresAuth: false }
  }
]

// ルーター作成
const router = createRouter({
  history: createWebHistory(),
  routes
})

// ルートガード
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // ログインが必要なページかチェック
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth) {
    // 認証状態をチェック
    if (!userStore.isAuthenticated) {
      // トークンが存在する場合、検証を試行
      if (userStore.token) {
        try {
          const isValid = await userStore.verifyToken()
          if (isValid) {
            next()
            return
          }
        } catch {
          // トークンが無効な場合
        }
      }

      // 認証されていない場合はログインページにリダイレクト
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // UTAGE課金状態チェック
    if (!userStore.isActive) {
      // 課金が無効な場合のハンドリング
      // 今は警告のみ、後で専用ページを作成
      console.warn('UTAGE課金状態が無効です')
    }
  } else {
    // 認証不要ページ（ログインページなど）
    if (to.name === 'Login' && userStore.isAuthenticated) {
      // すでにログイン済みの場合はダッシュボードにリダイレクト
      next({ name: 'Dashboard' })
      return
    }
  }

  next()
})

export default router