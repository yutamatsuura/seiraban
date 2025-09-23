<template>
  <MainLayout>
    <div class="profile">
      <div class="page-header">
        <h1 class="page-title">
          <img src="/src/assets/icons/user-profile.svg" alt="マイページ" class="page-title-icon" />
          マイページ
        </h1>
        <p class="page-subtitle">アカウント情報の確認・変更ができます</p>
      </div>

      <!-- エラーメッセージ -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <!-- 成功メッセージ -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <div class="profile-content">
        <!-- アカウント情報 -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">アカウント情報</h2>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile" class="profile-form">
              <div class="form-group">
                <label for="display_name" class="form-label">表示名</label>
                <input
                  id="display_name"
                  v-model="profileForm.display_name"
                  type="text"
                  class="form-input"
                  placeholder="表示名を入力"
                  required
                />
              </div>

              <div class="form-group">
                <label for="email" class="form-label">メールアドレス</label>
                <input
                  id="email"
                  v-model="profileForm.email"
                  type="email"
                  class="form-input"
                  placeholder="メールアドレスを入力"
                  required
                />
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  <span v-if="updating">更新中...</span>
                  <span v-else>プロフィール更新</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- パスワード変更 -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">パスワード変更</h2>
          </div>
          <div class="card-body">
            <form @submit.prevent="updatePassword" class="password-form">
              <div class="form-group">
                <label for="current_password" class="form-label">現在のパスワード</label>
                <input
                  id="current_password"
                  v-model="passwordForm.current_password"
                  type="password"
                  class="form-input"
                  placeholder="現在のパスワードを入力"
                  required
                />
              </div>

              <div class="form-group">
                <label for="new_password" class="form-label">新しいパスワード</label>
                <input
                  id="new_password"
                  v-model="passwordForm.new_password"
                  type="password"
                  class="form-input"
                  placeholder="新しいパスワードを入力"
                  required
                  minlength="8"
                />
                <div class="form-help">8文字以上で入力してください</div>
              </div>

              <div class="form-group">
                <label for="confirm_password" class="form-label">パスワード確認</label>
                <input
                  id="confirm_password"
                  v-model="passwordForm.confirm_password"
                  type="password"
                  class="form-input"
                  placeholder="新しいパスワードを再入力"
                  required
                />
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="updatingPassword">
                  <span v-if="updatingPassword">変更中...</span>
                  <span v-else">パスワード変更</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- アカウント詳細 -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">アカウント詳細</h2>
          </div>
          <div class="card-body">
            <div class="detail-grid">
              <div class="detail-item">
                <div class="detail-label">ユーザーID</div>
                <div class="detail-value">{{ userInfo.id || '-' }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">アカウント作成日</div>
                <div class="detail-value">{{ formatDate(userInfo.created_at) || '-' }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">最終ログイン</div>
                <div class="detail-value">{{ formatDate(userInfo.last_login) || '-' }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">サブスクリプション状態</div>
                <div class="detail-value">
                  <span class="badge" :class="getSubscriptionBadgeClass(userInfo.subscription_status)">
                    {{ getSubscriptionText(userInfo.subscription_status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'

const router = useRouter()

// 状態
const updating = ref(false)
const updatingPassword = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// フォームデータ
const profileForm = reactive({
  display_name: '',
  email: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// ユーザー情報
const userInfo = reactive({
  id: '',
  email: '',
  display_name: '',
  created_at: '',
  last_login: '',
  subscription_status: 'active'
})

// プロフィール更新
const updateProfile = async () => {
  try {
    updating.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // バリデーション
    if (!profileForm.display_name || !profileForm.email) {
      errorMessage.value = '全ての項目を入力してください'
      return
    }

    // TODO: API呼び出しを実装
    // const response = await apiClient.updateProfile(profileForm)

    // 仮の成功処理
    await new Promise(resolve => setTimeout(resolve, 1000))

    userInfo.display_name = profileForm.display_name
    userInfo.email = profileForm.email

    successMessage.value = 'プロフィールを更新しました'
  } catch (error) {
    errorMessage.value = 'プロフィールの更新に失敗しました'
    console.error('Profile update error:', error)
  } finally {
    updating.value = false
  }
}

// パスワード更新
const updatePassword = async () => {
  try {
    updatingPassword.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // バリデーション
    if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      errorMessage.value = '全ての項目を入力してください'
      return
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      errorMessage.value = '新しいパスワードが一致しません'
      return
    }

    if (passwordForm.new_password.length < 8) {
      errorMessage.value = 'パスワードは8文字以上で入力してください'
      return
    }

    // TODO: API呼び出しを実装
    // const response = await apiClient.updatePassword({
    //   current_password: passwordForm.current_password,
    //   new_password: passwordForm.new_password
    // })

    // 仮の成功処理
    await new Promise(resolve => setTimeout(resolve, 1000))

    // フォームリセット
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''

    successMessage.value = 'パスワードを変更しました'
  } catch (error) {
    errorMessage.value = 'パスワードの変更に失敗しました'
    console.error('Password update error:', error)
  } finally {
    updatingPassword.value = false
  }
}

// ユーザー情報読み込み
const loadUserInfo = async () => {
  try {
    // TODO: API呼び出しを実装
    // const response = await apiClient.getUserInfo()

    // 仮のデータ
    const mockData = {
      id: 'user_123',
      email: 'test@example.com',
      display_name: 'テストユーザー',
      created_at: '2024-01-01T00:00:00Z',
      last_login: '2024-12-01T12:00:00Z',
      subscription_status: 'active'
    }

    Object.assign(userInfo, mockData)
    profileForm.display_name = mockData.display_name
    profileForm.email = mockData.email
  } catch (error) {
    errorMessage.value = 'ユーザー情報の読み込みに失敗しました'
    console.error('Load user info error:', error)
  }
}

// 日付フォーマット
const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

// サブスクリプション状態のバッジクラス
const getSubscriptionBadgeClass = (status: string): string => {
  switch (status) {
    case 'active': return 'badge-success'
    case 'inactive': return 'badge-warning'
    case 'expired': return 'badge-error'
    default: return 'badge-secondary'
  }
}

// サブスクリプション状態のテキスト
const getSubscriptionText = (status: string): string => {
  switch (status) {
    case 'active': return '有効'
    case 'inactive': return '無効'
    case 'expired': return '期限切れ'
    default: return '不明'
  }
}

// マウント時の処理
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.profile {
  @include page-container;
}

.page-header {
  @include page-header;

  .page-title {
    @include page-title;
  }

  .page-subtitle {
    @include small-text;
    margin: 0;
    font-style: normal;
    font-weight: 300;
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  margin-bottom: 20px;

  .form-label {
    display: block;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .form-input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 1rem;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: var(--primary-main);
      box-shadow: 0 0 0 3px rgba(52, 73, 94, 0.1);
    }
  }

  .form-help {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-top: 4px;
  }
}

.form-actions {
  margin-top: 24px;

  .btn {
    padding: 12px 24px;
    border: none;
    border-radius: var(--border-radius);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;

    &.btn-primary {
      background-color: var(--primary-main);
      color: white;

      &:hover:not(:disabled) {
        background-color: var(--primary-dark);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  .detail-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .detail-value {
    font-size: 1rem;
    color: var(--text-primary);
  }
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;

  &.badge-success {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4caf50;
  }

  &.badge-warning {
    background-color: rgba(255, 152, 0, 0.1);
    color: #ff9800;
  }

  &.badge-error {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
  }

  &.badge-secondary {
    background-color: rgba(158, 158, 158, 0.1);
    color: #9e9e9e;
  }
}

.error-message {
  background-color: rgba(244, 67, 54, 0.1);
  color: #f44336;
  padding: 12px 16px;
  border-radius: var(--border-radius);
  margin-bottom: 16px;
  border: 1px solid rgba(244, 67, 54, 0.2);
}

.success-message {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4caf50;
  padding: 12px 16px;
  border-radius: var(--border-radius);
  margin-bottom: 16px;
  border: 1px solid rgba(76, 175, 80, 0.2);
}

// レスポンシブ対応
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>