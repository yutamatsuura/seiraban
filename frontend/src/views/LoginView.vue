<template>
  <div class="login-page">
    <div class="login-container">
      <div class="logo-section">
        <div class="logo">運命織</div>
        <div class="subtitle">UnmeiOri - 鑑定書楽々作成ツール</div>
        <div class="tagline">プロフェッショナルな鑑定書を1分で作成します</div>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <!-- エラーメッセージ -->
        <div v-if="errorMessage" class="error-message" role="alert" aria-live="polite">
          {{ errorMessage }}
        </div>

        <!-- 成功メッセージ -->
        <div v-if="successMessage" class="success-message" role="alert" aria-live="polite">
          {{ successMessage }}
        </div>

        <div class="form-group">
          <label for="email" class="form-label">
            <svg class="form-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12.713l-11.985-9.713h23.97l-11.985 9.713zm0 2.574l-12-9.725v15.438h24v-15.438l-12 9.725z"/>
            </svg>
            メールアドレス
          </label>
          <input
            v-model="form.email"
            type="email"
            id="email"
            class="form-input"
            placeholder="your@email.com"
            required
            :disabled="loading"
            autocomplete="email"
            aria-describedby="email-help"
          />
        </div>

        <div class="form-group">
          <label for="password" class="form-label">
            <svg class="form-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6z"/>
            </svg>
            パスワード
          </label>
          <input
            v-model="form.password"
            type="password"
            id="password"
            class="form-input"
            placeholder="パスワードを入力"
            required
            :disabled="loading"
            autocomplete="current-password"
            aria-describedby="password-help"
          />
        </div>

        <!-- 認証情報入力ボタン -->
        <div class="credential-buttons">
          <button
            type="button"
            @click="fillAdminCredentials"
            class="admin-fill-button"
            :disabled="loading"
          >
            <svg class="button-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-1 6h2v2h-2V7zm0 4h2v6h-2v-6z"/>
            </svg>
            管理者認証情報を入力
          </button>

          <button
            type="button"
            @click="fillUserCredentials"
            class="user-fill-button"
            :disabled="loading"
          >
            <svg class="button-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            一般ユーザー認証情報を入力
          </button>
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading || !isFormValid"
          aria-describedby="login-help"
        >
          <div class="button-content">
            <div v-if="loading" class="loading-spinner"></div>
            <span>{{ loading ? '認証中...' : 'ログイン' }}</span>
          </div>
        </button>
      </form>

      <div class="security-info">
        <div class="security-badge">
          🔒 セキュア認証
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// フォーム状態
const form = ref({
  email: '',
  password: ''
})

// UI状態
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 計算プロパティ
const isFormValid = computed(() => {
  return form.value.email.trim() !== '' && form.value.password.trim() !== ''
})

// 管理者認証情報入力
const fillAdminCredentials = () => {
  form.value.email = 'matsuura.yuta@gmail.com'
  form.value.password = 'ia0110299'
}

// 一般ユーザー認証情報入力
const fillUserCredentials = () => {
  form.value.email = 'matsuura.yuta02@gmail.com'
  form.value.password = 'ia0110299'
}

// ログイン処理
const handleLogin = async () => {
  if (!isFormValid.value || loading.value) return

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // バリデーション
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(form.value.email)) {
      errorMessage.value = '正しいメールアドレス形式で入力してください'
      return
    }

    // ログイン実行
    await userStore.login(form.value.email, form.value.password)

    // リダイレクト先を取得
    const redirectPath = (route.query.redirect as string) || '/dashboard'

    // 即座にリダイレクト
    router.push(redirectPath)

  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || userStore.error || 'ログインに失敗しました'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-page {
  font-family: "Times New Roman", "Noto Serif JP", serif;
  background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2c3e50;
}

.login-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 16px 32px rgba(52, 73, 94, 0.18);
  padding: 48px;
  width: 100%;
  max-width: 450px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #34495e 0%, #16a085 100%);
  }
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;

  .logo {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
  }

  .subtitle {
    font-size: 0.875rem;
    color: #566573;
    font-weight: 400;
    margin-bottom: 6px;
  }

  .tagline {
    font-size: 0.75rem;
    color: #85929e;
    font-weight: 400;
    opacity: 0.8;
  }
}

.login-form {
  .form-group {
    margin-bottom: 24px;
  }

  .form-label {
    display: flex;
    align-items: center;
    font-size: 0.875rem;
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 8px;

    .form-icon {
      margin-right: 8px;
      color: #566573;
      flex-shrink: 0;
    }
  }

  .form-input {
    width: 100%;
    padding: 16px;
    font-size: 1rem;
    font-family: inherit;
    border: 2px solid #d5dbdb;
    border-radius: 8px;
    background: #ffffff;
    color: #2c3e50;
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-color: #34495e;
      box-shadow: 0 0 0 3px rgba(52, 73, 94, 0.1);
    }

    &::placeholder {
      color: #85929e;
    }

    &:disabled {
      background: #bdc3c7;
      cursor: not-allowed;
      opacity: 0.7;
    }
  }
}

.credential-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;

  @media (max-width: 600px) {
    flex-direction: column;
    gap: 12px;
  }
}

.admin-fill-button,
.user-fill-button {
  flex: 1;
  padding: 12px 16px;
  font-size: 0.8rem;
  font-weight: 500;
  font-family: inherit;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: none;
  display: flex;
  align-items: center;
  justify-content: center;

  .button-icon {
    margin-right: 6px;
    flex-shrink: 0;
  }

  &:hover {
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: #bdc3c7 !important;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  @media (max-width: 600px) {
    font-size: 0.875rem;
  }
}

.admin-fill-button {
  background: linear-gradient(135deg, #16a085 0%, #138d75 100%);

  &:hover {
    box-shadow: 0 4px 12px rgba(22, 160, 133, 0.25);
  }
}

.user-fill-button {
  background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);

  &:hover {
    box-shadow: 0 4px 12px rgba(243, 156, 18, 0.25);
  }
}

.login-button {
  width: 100%;
  padding: 16px;
  font-size: 1rem;
  font-weight: 500;
  font-family: inherit;
  background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: none;
  margin-bottom: 16px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(52, 73, 94, 0.2);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;

    .loading-spinner {
      width: 20px;
      height: 20px;
      border: 2px solid transparent;
      border-top: 2px solid #ffffff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-right: 8px;
    }
  }
}

.error-message {
  background: rgba(231, 76, 60, 0.1);
  color: #c0392b;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  margin-bottom: 16px;
  border: 1px solid rgba(231, 76, 60, 0.2);
}

.success-message {
  background: rgba(22, 160, 133, 0.1);
  color: #138d75;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  margin-bottom: 16px;
  border: 1px solid rgba(22, 160, 133, 0.2);
}

.security-info {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #d5dbdb;

  .security-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    background: rgba(22, 160, 133, 0.1);
    color: #138d75;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// レスポンシブ対応
@media (max-width: 600px) {
  .login-container {
    margin: 16px;
    padding: 32px 24px;
  }

  .logo-section .logo {
    font-size: 2rem;
  }

  .welcome-text h1 {
    font-size: 1.25rem;
  }
}

// アクセシビリティ対応
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

// ハイコントラスト対応
@media (prefers-contrast: high) {
  .form-input {
    border-color: #000000;

    &:focus {
      border-color: #000000;
      box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.3);
    }
  }
}

// フォーカス表示の改善
.login-button:focus-visible,
.form-input:focus-visible {
  outline: 2px solid #34495e;
  outline-offset: 2px;
}
</style>