import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// ユーザー型定義（バックエンドAPIに対応）
interface User {
  id: number
  email: string
  business_name?: string
  operator_name?: string // 鑑定士名
  is_active: boolean
  is_superuser: boolean
  withdrawal_status: string // active/withdrawn
  created_at: string
  updated_at: string
}

// API レスポンス型定義（バックエンドAPIに対応）
interface LoginResponse {
  access_token: string
  token_type: string
  user_id: number
  is_superuser: boolean
  withdrawal_status: string
}


interface MessageResponse {
  success: boolean
  message: string
}

interface RegistrationRequest {
  email: string
  password: string
  business_name?: string
  operator_name?: string // 鑑定士名
}

interface RegistrationResponse {
  success: boolean
  message: string
  user_id: number
  email: string
}

// API ベース URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8503'

// Axios インスタンス作成
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const useUserStore = defineStore('user', () => {
  // 状態
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 計算プロパティ
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const isActive = computed(() => user.value?.is_active ?? false)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  // Axios インターセプター設定
  api.interceptors.request.use(
    (config) => {
      if (token.value) {
        config.headers.Authorization = `Bearer ${token.value}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // 認証エラーの場合、自動ログアウト
        logout()
      }
      return Promise.reject(error)
    }
  )

  // ローカルストレージからトークンを復元
  const restoreFromStorage = () => {
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('user_data')

    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('ストレージからのデータ復元に失敗:', e)
        clearStorage()
      }
    }
  }

  // ストレージにデータを保存
  const saveToStorage = (tokenValue: string, userData: User) => {
    localStorage.setItem('auth_token', tokenValue)
    localStorage.setItem('user_data', JSON.stringify(userData))
  }

  // ストレージをクリア
  const clearStorage = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
  }

  // ログイン（実際のAPIを使用）
  const login = async (email: string, password: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      // バックエンドの認証APIを呼び出し
      const response = await api.post<LoginResponse>('/api/auth/login', {
        email: email,
        password: password
      })

      // トークンを保存
      token.value = response.data.access_token

      // ユーザー情報を取得（トークン検証を兼ねる）
      const userInfoResponse = await api.get<User>('/api/auth/verify', {
        headers: {
          Authorization: `Bearer ${response.data.access_token}`
        }
      })

      user.value = userInfoResponse.data

      // ローカルストレージに保存
      saveToStorage(token.value, user.value)

      console.log('ログイン成功:', user.value)
    } catch (err: any) {
      console.error('ログインエラー:', err)
      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'ログインに失敗しました'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  // ログアウト
  const logout = async (): Promise<void> => {
    try {
      // サーバーにログアウトリクエストを送信
      if (token.value) {
        await api.post('/api/auth/logout')
      }
    } catch (err) {
      console.error('ログアウトエラー:', err)
    } finally {
      // 状態をクリア
      user.value = null
      token.value = null
      error.value = null

      // ローカルストレージをクリア
      clearStorage()

      console.log('ログアウト完了')
    }
  }

  // トークン検証
  const verifyToken = async (): Promise<boolean> => {
    if (!token.value) {
      return false
    }

    try {
      const response = await api.get<User>('/api/auth/verify')
      user.value = response.data

      // ユーザー情報を更新して保存
      saveToStorage(token.value, response.data)

      return true
    } catch (err) {
      console.error('トークン検証エラー:', err)

      // 無効なトークンの場合はクリア
      user.value = null
      token.value = null
      clearStorage()

      return false
    }
  }

  // ユーザー情報を更新
  const updateProfile = async (profileData: Partial<User>): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put<User>('/auth/profile', profileData)
      user.value = response.data

      // 更新されたユーザー情報を保存
      if (token.value) {
        saveToStorage(token.value, response.data)
      }

      console.log('プロフィール更新成功:', response.data)
    } catch (err: any) {
      console.error('プロフィール更新エラー:', err)

      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'プロフィールの更新に失敗しました'
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  // ユーザー登録
  const register = async (registrationData: RegistrationRequest): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post<RegistrationResponse>('/api/auth/register', registrationData)
      console.log('ユーザー登録成功:', response.data)
    } catch (err: any) {
      console.error('ユーザー登録エラー:', err)

      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = 'ユーザー登録に失敗しました'
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  // 管理者に昇格（開発用）
  const promoteToAdmin = async (email: string, password: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post<MessageResponse>('/api/auth/promote-to-admin', {
        email: email,
        password: password
      })
      console.log('管理者昇格成功:', response.data.message)
    } catch (err: any) {
      console.error('管理者昇格エラー:', err)

      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = '管理者昇格に失敗しました'
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  // 管理者用API：ユーザー一覧取得
  const getUsers = async (skip: number = 0, limit: number = 100, search?: string) => {
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString()
      })
      if (search) {
        params.append('search', search)
      }

      const response = await api.get(`/api/admin/users?${params}`)
      return response.data
    } catch (err) {
      console.error('ユーザー一覧取得エラー:', err)
      throw err
    }
  }

  // 管理者用API：ユーザーステータス更新
  const updateUserStatus = async (userId: number, statusData: { withdrawal_status?: string, is_active?: boolean, reason?: string }) => {
    try {
      const response = await api.put(`/api/admin/users/${userId}/status`, statusData)
      return response.data
    } catch (err) {
      console.error('ユーザーステータス更新エラー:', err)
      throw err
    }
  }

  // 管理者用API：システム統計取得
  const getSystemStats = async () => {
    try {
      const response = await api.get('/api/admin/stats')
      return response.data
    } catch (err) {
      console.error('システム統計取得エラー:', err)
      throw err
    }
  }

  // 初期化（アプリ起動時に呼び出し）
  const initialize = async (): Promise<void> => {
    restoreFromStorage()

    if (token.value) {
      await verifyToken()
    }
  }

  // エラーをクリア
  const clearError = () => {
    error.value = null
  }

  return {
    // 状態
    user,
    token,
    loading,
    error,

    // 計算プロパティ
    isAuthenticated,
    isActive,
    isSuperuser,

    // メソッド
    login,
    logout,
    verifyToken,
    register,
    promoteToAdmin,
    updateProfile,
    getUsers,
    updateUserStatus,
    getSystemStats,
    initialize,
    clearError,

    // Axios インスタンス（他のストアで使用可能）
    api,
  }
})