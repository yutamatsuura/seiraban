<template>
  <div class="template-settings">
    <div class="page-header">
      <h1>テンプレート設定</h1>
      <p>鑑定書PDFのデザインと表示設定を管理できます</p>
    </div>

    <!-- エラーメッセージ -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 成功メッセージ -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <!-- ローディング状態 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>設定を読み込み中...</p>
    </div>

    <!-- 設定フォーム -->
    <div v-else class="settings-content">
      <!-- ロゴ設定セクション -->
      <div class="card">
        <div class="card-header">
          <h2>ロゴ設定</h2>
          <p>鑑定書に表示するロゴ画像を設定します（JPG/PNG、最大2MB）</p>
        </div>
        <div class="card-body">
          <div class="logo-section">
            <!-- 現在のロゴ表示 -->
            <div class="current-logo">
              <div v-if="settings?.logo_url" class="logo-preview">
                <img :src="getLogoUrl(settings.logo_url)" alt="現在のロゴ" />
                <div class="logo-info">
                  <p>ファイルサイズ: {{ formatFileSize(settings.logo_file_size || 0) }}</p>
                  <button @click="deleteLogo" class="btn btn-outline" :disabled="uploading">
                    <span class="material-icons">delete</span>
                    削除
                  </button>
                </div>
              </div>
              <div v-else class="no-logo">
                <span class="material-icons">image</span>
                <p>ロゴが設定されていません</p>
              </div>
            </div>

            <!-- ロゴアップロード -->
            <div class="logo-upload">
              <input
                ref="logoInput"
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                style="display: none"
                @change="handleFileSelect"
              />
              <button
                @click="triggerFileSelect"
                class="btn btn-primary"
                :disabled="uploading"
              >
                <span class="material-icons">cloud_upload</span>
                <span v-if="uploading">アップロード中...</span>
                <span v-else>{{ settings?.logo_url ? 'ロゴを変更' : 'ロゴをアップロード' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 基本情報設定 -->
      <div class="card">
        <div class="card-header">
          <h2>基本情報</h2>
          <p>鑑定書に表示される事業者情報を設定します</p>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveSettings" class="settings-form">
            <div class="form-group">
              <label for="businessName" class="form-label required">屋号・事業者名</label>
              <input
                v-model="form.business_name"
                type="text"
                id="businessName"
                class="form-input"
                placeholder="株式会社○○占い事務所"
                required
                :disabled="saving"
              />
            </div>

            <div class="form-group">
              <label for="operatorName" class="form-label required">運営者名</label>
              <input
                v-model="form.operator_name"
                type="text"
                id="operatorName"
                class="form-input"
                placeholder="鑑定師 田中太郎"
                required
                :disabled="saving"
              />
            </div>
          </form>
        </div>
      </div>

      <!-- デザイン設定 -->
      <div class="card">
        <div class="card-header">
          <h2>デザイン設定</h2>
          <p>鑑定書のデザインとレイアウトを設定します</p>
        </div>
        <div class="card-body">
          <div class="design-settings">
            <!-- カラーテーマ -->
            <div class="setting-group">
              <label class="setting-label">カラーテーマ</label>
              <div class="color-theme-options">
                <label
                  v-for="theme in colorThemes"
                  :key="theme.value"
                  class="theme-option"
                  :class="{ active: form.color_theme === theme.value }"
                >
                  <input
                    v-model="form.color_theme"
                    type="radio"
                    :value="theme.value"
                    :disabled="saving"
                  />
                  <div class="theme-preview" :style="{ backgroundColor: theme.primary }">
                    <div class="theme-accent" :style="{ backgroundColor: theme.accent }"></div>
                  </div>
                  <span>{{ theme.name }}</span>
                </label>
              </div>
            </div>

            <!-- フォントファミリー -->
            <div class="setting-group">
              <label for="fontFamily" class="setting-label">フォント</label>
              <select
                v-model="form.font_family"
                id="fontFamily"
                class="form-select"
                :disabled="saving"
              >
                <option value="default">デフォルト</option>
                <option value="noto-serif">Noto Serif JP（明朝体）</option>
                <option value="noto-sans">Noto Sans JP（ゴシック体）</option>
                <option value="hiragino">ヒラギノ明朝</option>
                <option value="yu-mincho">游明朝</option>
              </select>
            </div>

            <!-- レイアウトスタイル -->
            <div class="setting-group">
              <label for="layoutStyle" class="setting-label">レイアウト</label>
              <select
                v-model="form.layout_style"
                id="layoutStyle"
                class="form-select"
                :disabled="saving"
              >
                <option value="standard">標準レイアウト</option>
                <option value="compact">コンパクトレイアウト</option>
                <option value="detailed">詳細レイアウト</option>
                <option value="elegant">エレガントレイアウト</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- カスタムCSS設定 -->
      <div class="card">
        <div class="card-header">
          <h2>カスタムCSS</h2>
          <p>詳細なスタイルのカスタマイズが可能です（上級者向け）</p>
        </div>
        <div class="card-body">
          <div class="custom-css-section">
            <textarea
              v-model="form.custom_css"
              class="custom-css-input"
              placeholder="/* カスタムCSSを記述してください */
.diagnosis-title {
  color: #333;
  font-size: 24px;
}

.result-section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
}"
              rows="8"
              :disabled="saving"
            ></textarea>
            <div class="css-help">
              <details>
                <summary>利用可能なCSSクラス</summary>
                <ul>
                  <li><code>.diagnosis-title</code> - 鑑定書タイトル</li>
                  <li><code>.client-info</code> - お客様情報セクション</li>
                  <li><code>.kyusei-section</code> - 九星気学結果セクション</li>
                  <li><code>.seimei-section</code> - 姓名判断結果セクション</li>
                  <li><code>.result-item</code> - 個別結果項目</li>
                  <li><code>.footer-info</code> - フッター情報</li>
                </ul>
              </details>
            </div>
          </div>
        </div>
      </div>

      <!-- プレビューセクション -->
      <div class="card">
        <div class="card-header">
          <h2>プレビュー</h2>
          <p>現在の設定でのテンプレート表示例</p>
        </div>
        <div class="card-body">
          <div class="template-preview" :class="`theme-${form.color_theme}`">
            <div class="preview-header">
              <div v-if="settings?.logo_url" class="preview-logo">
                <img :src="getLogoUrl(settings.logo_url)" alt="ロゴ" />
              </div>
              <div class="preview-title">
                <h3>九星気学・姓名判断 鑑定書</h3>
                <p>{{ form.business_name }}</p>
                <p>{{ form.operator_name }}</p>
              </div>
            </div>
            <div class="preview-content">
              <div class="preview-section">
                <h4>お客様情報</h4>
                <p>お名前: サンプル 太郎様</p>
                <p>生年月日: 1990年5月15日</p>
              </div>
              <div class="preview-section">
                <h4>九星気学鑑定結果</h4>
                <p>本命星: 三碧木星</p>
                <p>運勢: 積極的で行動力があります</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 保存ボタン -->
      <div class="form-actions">
        <button
          @click="resetToDefaults"
          type="button"
          class="btn btn-outline"
          :disabled="saving"
        >
          デフォルトに戻す
        </button>
        <button
          @click="saveSettings"
          type="button"
          class="btn btn-primary"
          :disabled="saving || !isFormValid"
        >
          <div class="button-content">
            <div v-if="saving" class="loading-spinner"></div>
            <span>{{ saving ? '保存中...' : '設定を保存' }}</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient, type TemplateSettings, type TemplateSettingsUpdate } from '@/services/api-client'

// データ状態
const settings = ref<TemplateSettings | null>(null)
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// ファイル入力参照
const logoInput = ref<HTMLInputElement>()

// フォーム状態
const form = ref({
  business_name: '',
  operator_name: '',
  color_theme: 'default',
  font_family: 'default',
  layout_style: 'standard',
  custom_css: ''
})

// カラーテーマオプション
const colorThemes = [
  { value: 'default', name: 'デフォルト', primary: '#3498db', accent: '#2980b9' },
  { value: 'elegant', name: 'エレガント', primary: '#8e44ad', accent: '#9b59b6' },
  { value: 'warm', name: 'ウォーム', primary: '#e67e22', accent: '#d35400' },
  { value: 'natural', name: 'ナチュラル', primary: '#27ae60', accent: '#2ecc71' },
  { value: 'professional', name: 'プロフェッショナル', primary: '#34495e', accent: '#2c3e50' }
]

// 計算プロパティ
const isFormValid = computed(() => {
  return form.value.business_name.trim() !== '' &&
         form.value.operator_name.trim() !== ''
})

// ヘルパー関数
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getLogoUrl = (url: string) => {
  // APIベースURLを使用してフルURLを構築
  if (url.startsWith('http')) {
    return url
  }
  return `http://localhost:8502/${url}`
}

// API呼び出し関数
const loadSettings = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await apiClient.getTemplateSettings()
    settings.value = response

    // フォームに現在の設定を適用
    form.value = {
      business_name: response.business_name,
      operator_name: response.operator_name,
      color_theme: response.color_theme,
      font_family: response.font_family,
      layout_style: response.layout_style,
      custom_css: response.custom_css || ''
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'テンプレート設定の取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  if (!isFormValid.value || saving.value) return

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const updateData: TemplateSettingsUpdate = {
      business_name: form.value.business_name,
      operator_name: form.value.operator_name,
      color_theme: form.value.color_theme,
      font_family: form.value.font_family,
      layout_style: form.value.layout_style,
      custom_css: form.value.custom_css || undefined
    }

    const response = await apiClient.updateTemplateSettings(updateData)
    settings.value = response
    successMessage.value = 'テンプレート設定を保存しました'

    // 成功メッセージを3秒後に消去
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error: any) {
    errorMessage.value = error.message || 'テンプレート設定の保存に失敗しました'
  } finally {
    saving.value = false
  }
}

const triggerFileSelect = () => {
  logoInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // ファイル検証
  if (!file.type.startsWith('image/')) {
    errorMessage.value = '画像ファイルを選択してください'
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    errorMessage.value = 'ファイルサイズが2MBを超えています'
    return
  }

  uploading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await apiClient.uploadLogo(file)

    // 設定を再読み込みして最新のロゴ情報を取得
    await loadSettings()

    successMessage.value = 'ロゴを正常にアップロードしました'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error: any) {
    errorMessage.value = error.message || 'ロゴのアップロードに失敗しました'
  } finally {
    uploading.value = false
    // ファイル入力をリセット
    if (target) target.value = ''
  }
}

const deleteLogo = async () => {
  if (!confirm('ロゴを削除してもよろしいですか？')) return

  uploading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await apiClient.deleteLogo()

    // 設定を再読み込みしてロゴ情報を更新
    await loadSettings()

    successMessage.value = 'ロゴを削除しました'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error: any) {
    errorMessage.value = error.message || 'ロゴの削除に失敗しました'
  } finally {
    uploading.value = false
  }
}

const resetToDefaults = () => {
  if (!confirm('すべての設定をデフォルトに戻してもよろしいですか？')) return

  form.value = {
    business_name: '',
    operator_name: '',
    color_theme: 'default',
    font_family: 'default',
    layout_style: 'standard',
    custom_css: ''
  }
}

// ライフサイクル
onMounted(() => {
  loadSettings()
})
</script>

<style scoped lang="scss">
.template-settings {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;

  h1 {
    font-size: 2rem;
    margin-bottom: 8px;
    color: var(--text-primary);
  }

  p {
    color: var(--text-secondary);
    margin: 0;
  }
}

.error-message {
  background: rgba(231, 76, 60, 0.1);
  color: #c0392b;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border: 1px solid rgba(231, 76, 60, 0.2);
}

.success-message {
  background: rgba(22, 160, 133, 0.1);
  color: #138d75;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border: 1px solid rgba(22, 160, 133, 0.2);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px 20px;
  color: var(--text-secondary);

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color);
    border-top: 3px solid var(--primary-main);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-1);
  margin-bottom: 24px;
  overflow: hidden;
}

.card-header {
  background: var(--background-paper);
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);

  h2 {
    margin: 0 0 8px 0;
    font-size: 1.25rem;
    color: var(--text-primary);
  }

  p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.875rem;
  }
}

.card-body {
  padding: 24px;
}

.logo-section {
  display: flex;
  gap: 24px;
  align-items: flex-start;

  .current-logo {
    flex: 1;

    .logo-preview {
      display: flex;
      gap: 16px;
      align-items: center;

      img {
        max-width: 120px;
        max-height: 80px;
        object-fit: contain;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 8px;
        background: white;
      }

      .logo-info {
        display: flex;
        flex-direction: column;
        gap: 8px;

        p {
          margin: 0;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
      }
    }

    .no-logo {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 32px;
      border: 2px dashed var(--border-color);
      border-radius: 8px;
      color: var(--text-disabled);

      .material-icons {
        font-size: 3rem;
        margin-bottom: 8px;
      }

      p {
        margin: 0;
        font-size: 0.875rem;
      }
    }
  }

  .logo-upload {
    flex-shrink: 0;
  }
}

.settings-form {
  .form-group {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .form-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;

    &.required::after {
      content: ' *';
      color: #e74c3c;
    }
  }

  .form-input, .form-select {
    width: 100%;
    padding: 12px 16px;
    font-size: 1rem;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    background: white;
    color: var(--text-primary);
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: var(--primary-main);
      box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }

    &:disabled {
      background-color: var(--background-default);
      opacity: 0.7;
    }

    &::placeholder {
      color: var(--text-disabled);
    }
  }
}

.design-settings {
  .setting-group {
    margin-bottom: 32px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .setting-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 12px;
  }
}

.color-theme-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;

  .theme-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--primary-main);
    }

    &.active {
      border-color: var(--primary-main);
      background: rgba(52, 152, 219, 0.05);
    }

    input[type="radio"] {
      display: none;
    }

    .theme-preview {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      position: relative;
      margin-bottom: 8px;

      .theme-accent {
        position: absolute;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        top: 2px;
        right: 2px;
        border: 2px solid white;
      }
    }

    span {
      font-size: 0.75rem;
      color: var(--text-secondary);
      text-align: center;
    }
  }
}

.custom-css-section {
  .custom-css-input {
    width: 100%;
    min-height: 200px;
    padding: 16px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    background: #f8f9fa;
    color: var(--text-primary);
    resize: vertical;

    &:focus {
      outline: none;
      border-color: var(--primary-main);
    }

    &:disabled {
      opacity: 0.7;
    }
  }

  .css-help {
    margin-top: 16px;

    details {
      summary {
        cursor: pointer;
        font-weight: 500;
        color: var(--primary-main);
        margin-bottom: 8px;

        &:hover {
          text-decoration: underline;
        }
      }

      ul {
        margin: 8px 0 0 16px;

        li {
          margin-bottom: 4px;
          font-size: 0.875rem;

          code {
            background: rgba(0, 0, 0, 0.05);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
          }
        }
      }
    }
  }
}

.template-preview {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 24px;
  background: white;

  &.theme-elegant {
    border-color: #8e44ad;

    .preview-title h3 {
      color: #8e44ad;
    }
  }

  &.theme-warm {
    border-color: #e67e22;

    .preview-title h3 {
      color: #e67e22;
    }
  }

  &.theme-natural {
    border-color: #27ae60;

    .preview-title h3 {
      color: #27ae60;
    }
  }

  &.theme-professional {
    border-color: #34495e;

    .preview-title h3 {
      color: #34495e;
    }
  }

  .preview-header {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);

    .preview-logo {
      flex-shrink: 0;

      img {
        max-width: 80px;
        max-height: 50px;
        object-fit: contain;
      }
    }

    .preview-title {
      h3 {
        margin: 0 0 8px 0;
        font-size: 1.5rem;
        color: var(--primary-main);
      }

      p {
        margin: 0 0 4px 0;
        font-size: 0.875rem;
        color: var(--text-secondary);
      }
    }
  }

  .preview-content {
    .preview-section {
      margin-bottom: 16px;

      h4 {
        margin: 0 0 8px 0;
        font-size: 1rem;
        color: var(--text-primary);
      }

      p {
        margin: 0 0 4px 0;
        font-size: 0.875rem;
        color: var(--text-secondary);
      }
    }
  }
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.btn-primary {
    background: var(--primary-main);
    color: white;

    &:hover:not(:disabled) {
      background: var(--primary-dark);
      transform: translateY(-1px);
      box-shadow: var(--shadow-2);
    }
  }

  &.btn-outline {
    background: transparent;
    color: var(--primary-main);
    border: 1px solid var(--primary-main);

    &:hover:not(:disabled) {
      background: var(--primary-main);
      color: white;
    }
  }

  .material-icons {
    font-size: 20px;
  }

  .button-content {
    display: flex;
    align-items: center;
    gap: 8px;

    .loading-spinner {
      width: 20px;
      height: 20px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// レスポンシブ
@media (max-width: 768px) {
  .logo-section {
    flex-direction: column;
    align-items: stretch;
  }

  .color-theme-options {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }

  .form-actions {
    flex-direction: column;
  }

  .preview-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>