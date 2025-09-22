<template>
  <MainLayout>
    <div class="template-settings">
      <div class="page-header">
        <h1 class="page-title">
          <img src="/src/assets/icons/template.svg" alt="テンプレート設定" class="page-title-icon" />
          テンプレート設定
        </h1>
        <p class="page-subtitle">鑑定書のロゴ・屋号・基本デザインをカスタマイズして独自ブランディングを実現</p>
      </div>

      <div class="content-layout">
        <!-- 設定エリア -->
        <div class="settings-panel">
          <h2 class="panel-title">設定項目</h2>

          <form @submit.prevent="handleSubmit" class="template-form">
            <!-- ロゴアップロード -->
            <div class="form-group">
              <label class="form-label">ロゴ画像</label>
              <div class="file-upload-area" @click="triggerFileInput" :class="{ dragover: isDragOver }"
                   @dragover.prevent="handleDragOver"
                   @drop.prevent="handleDrop"
                   @dragenter.prevent="isDragOver = true"
                   @dragleave.prevent="isDragOver = false">
                <div class="upload-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21,19V5c0,-1.1 -0.9,-2 -2,-2H5c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h14c1.1,0 2,-0.9 2,-2zM8.5,13.5l2.5,3.01L14.5,12l4.5,6H5l3.5,-4.5z"/>
                  </svg>
                </div>
                <div class="upload-text">クリックまたはドラッグしてロゴ画像をアップロード</div>
                <div class="upload-hint">JPG, PNG形式 / 最大2MB</div>
                <input type="file" ref="logoFileInput" @change="handleLogoUpload"
                       accept=".jpg,.jpeg,.png" class="file-input" />
              </div>

              <!-- 現在のロゴ表示 -->
              <div v-if="currentLogo" class="current-logo">
                <p class="logo-label">現在のロゴ:</p>
                <img :src="currentLogo" alt="現在のロゴ" class="logo-preview" />
                <button type="button" @click="removeLogo" class="btn btn-sm btn-secondary">削除</button>
              </div>
            </div>

            <!-- 屋号・事業者名 -->
            <div class="form-group">
              <label for="businessName" class="form-label">屋号・事業所名</label>
              <input
                type="text"
                id="businessName"
                v-model="settings.businessName"
                class="form-input"
                placeholder="例: 占いサロン 星花"
                @input="updatePreview"
              />
            </div>

            <!-- 鑑定士名 -->
            <div class="form-group">
              <label for="operatorName" class="form-label">鑑定士名</label>
              <input
                type="text"
                id="operatorName"
                v-model="settings.operatorName"
                class="form-input"
                placeholder="例: 星野 花子"
                @input="updatePreview"
              />
            </div>

            <!-- 基本色選択 -->
            <div class="form-group">
              <label class="form-label">基本色テーマ</label>
              <div class="color-palette">
                <div v-for="(theme, key) in colorThemes" :key="key"
                     class="color-option"
                     :class="{ selected: settings.colorTheme === key }"
                     @click="selectColorTheme(key)">
                  <div class="color-preview" :style="{ backgroundColor: theme.primary }"></div>
                  <div class="color-name">{{ theme.name }}</div>
                </div>
              </div>
            </div>

            <!-- フォントサイズ -->
            <div class="form-group">
              <label class="form-label">フォントサイズ</label>
              <div class="font-size-options">
                <div v-for="(size, key) in fontSizes" :key="key"
                     class="font-size-option"
                     :class="{ selected: settings.fontSize === key }"
                     @click="selectFontSize(key)">
                  <div class="font-size-label">{{ size.label }}</div>
                  <div class="font-size-example" :style="{ fontSize: size.example }">{{ size.text }}</div>
                </div>
              </div>
            </div>

            <!-- アクションボタン -->
            <div class="action-buttons">
              <button type="submit" class="btn btn-success" :disabled="loading">
                <svg v-if="!loading" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17 3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V7L17 3M19 19H5V5H16.17L19 7.83V19M12 12C13.66 12 15 13.34 15 15S13.66 18 12 18 9 16.66 9 15 10.34 12 12 12M6 6H15V10H6V6Z"/>
                </svg>
                <span v-if="loading">保存中...</span>
                <span v-else>設定を保存</span>
              </button>
              <button type="button" @click="resetForm" class="btn btn-secondary">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12,6V9L16,5L12,1V4A8,8 0 0,0 4,12C4,13.57 4.46,15.03 5.24,16.26L6.7,14.8C6.25,13.97 6,13 6,12A6,6 0 0,1 12,6M18.76,7.74L17.3,9.2C17.74,10.04 18,11 18,12A6,6 0 0,1 12,18V15L8,19L12,23V20A8,8 0 0,0 20,12C20,10.43 19.54,8.97 18.76,7.74Z"/>
                </svg>
                リセット
              </button>
            </div>
          </form>
        </div>

        <!-- プレビューエリア -->
        <div class="preview-panel">
          <h2 class="panel-title">プレビュー</h2>
          <p class="preview-description">
            設定した内容が実際の鑑定書でどのように表示されるかを確認できます
          </p>

          <div class="preview-document">
            <div class="preview-header">
              <div v-if="currentLogo" class="preview-logo-container">
                <img :src="currentLogo" alt="ロゴ" class="preview-logo" />
              </div>
              <div class="preview-business-name">{{ settings.businessName || '屋号・事業所名' }}</div>
              <div class="preview-operator-name">鑑定士：{{ settings.operatorName || '鑑定士名' }}</div>
              <h1 class="preview-title">九星気学鑑定書</h1>
            </div>

            <div class="preview-content">
              <div class="preview-section">
                <h3 class="preview-section-title">ご鑑定者様情報</h3>
                <div class="preview-text">
                  <p>お名前：田中 太郎 様</p>
                  <p>生年月日：昭和60年3月15日</p>
                  <p>本命星：二黒土星</p>
                </div>
              </div>

              <div class="preview-section">
                <h3 class="preview-section-title">九星気学による性格鑑定</h3>
                <div class="preview-text">
                  <p>あなたは二黒土星の生まれで、大地のような包容力と忍耐力を持つ方です。周囲の人々から信頼され、頼りにされる存在として活躍されることでしょう。</p>
                  <p>特に人間関係においては、相手の気持ちを理解する能力に長けており、調和を重んじる性格です。</p>
                </div>
              </div>

              <div class="preview-section">
                <h3 class="preview-section-title">吉方位アドバイス</h3>
                <div class="preview-text">
                  <p>2025年のあなたの吉方位は<strong>北東方向</strong>です。</p>
                  <p>特に3月、6月、9月はこの方角への移動が開運につながります。</p>
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
import MainLayout from '@/components/layout/MainLayout.vue'

// 状態管理
const loading = ref(false)
const isDragOver = ref(false)
const logoFileInput = ref<HTMLInputElement>()
const currentLogo = ref<string>('')

// 設定データ
const settings = reactive({
  businessName: '占いサロン 星花',
  operatorName: '星野 花子',
  colorTheme: 'professional',
  fontSize: 'medium',
  logoFile: null as File | null
})

// カラーテーマ定義
const colorThemes = {
  professional: { primary: '#34495e', accent: '#16a085', name: 'プロフェッショナル\n（紺色）' },
  elegant: { primary: '#8b4513', accent: '#d2691e', name: 'エレガント\n（茶色）' },
  modern: { primary: '#2c3e50', accent: '#3498db', name: 'モダン\n（ダークグレー）' },
  warm: { primary: '#d35400', accent: '#f39c12', name: 'ウォーム\n（オレンジ）' },
  nature: { primary: '#27ae60', accent: '#2ecc71', name: 'ナチュラル\n（緑色）' }
}

// フォントサイズ定義
const fontSizes = {
  small: { label: '小', example: '0.75rem', text: '読みやすい' },
  medium: { label: '中', example: '0.875rem', text: '標準的' },
  large: { label: '大', example: '1rem', text: '見やすい' }
}

// ファイルアップロード処理
const triggerFileInput = () => {
  logoFileInput.value?.click()
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false

  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleLogoFile(files[0])
  }
}

const handleLogoUpload = (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    handleLogoFile(file)
  }
}

const handleLogoFile = (file: File) => {
  // ファイル検証
  if (!validateImageFile(file)) return

  settings.logoFile = file

  // プレビュー生成
  const reader = new FileReader()
  reader.onload = (e) => {
    currentLogo.value = e.target?.result as string
    updatePreview()
  }
  reader.readAsDataURL(file)
}

const validateImageFile = (file: File): boolean => {
  const maxSize = 2 * 1024 * 1024 // 2MB
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']

  if (!allowedTypes.includes(file.type)) {
    alert('JPEGまたはPNG形式の画像ファイルを選択してください。')
    return false
  }

  if (file.size > maxSize) {
    alert('ファイルサイズは2MB以下にしてください。')
    return false
  }

  return true
}

const removeLogo = () => {
  settings.logoFile = null
  currentLogo.value = ''
  if (logoFileInput.value) {
    logoFileInput.value.value = ''
  }
  updatePreview()
}

// カラーテーマ選択
const selectColorTheme = (theme: string) => {
  settings.colorTheme = theme
  updatePreview()
}

// フォントサイズ選択
const selectFontSize = (size: string) => {
  settings.fontSize = size
  updatePreview()
}

// プレビュー更新
const updatePreview = () => {
  // CSS変数を更新してプレビューに反映
  const theme = colorThemes[settings.colorTheme as keyof typeof colorThemes]
  const fontSize = fontSizes[settings.fontSize as keyof typeof fontSizes]

  // ルート要素のCSS変数を更新
  document.documentElement.style.setProperty('--preview-primary', theme.primary)
  document.documentElement.style.setProperty('--preview-accent', theme.accent)
  document.documentElement.style.setProperty('--preview-font-size', fontSize.example)
}

// フォーム送信
const handleSubmit = async () => {
  loading.value = true

  try {
    // FormDataを作成
    const formData = new FormData()

    if (settings.logoFile) {
      formData.append('logo_file', settings.logoFile)
    }

    formData.append('settings', JSON.stringify({
      business_name: settings.businessName,
      operator_name: settings.operatorName,
      color_theme: settings.colorTheme,
      font_size: settings.fontSize
    }))

    // API呼び出し（模擬）
    await new Promise(resolve => setTimeout(resolve, 1000))

    alert('テンプレート設定が正常に保存されました。')

  } catch (error) {
    console.error('設定の保存に失敗しました:', error)
    alert('設定の保存に失敗しました。再度お試しください。')
  } finally {
    loading.value = false
  }
}

// フォームリセット
const resetForm = () => {
  if (confirm('設定をリセットしてもよろしいですか？')) {
    settings.businessName = '占いサロン 星花'
    settings.operatorName = '星野 花子'
    settings.colorTheme = 'professional'
    settings.fontSize = 'medium'
    settings.logoFile = null
    currentLogo.value = ''

    if (logoFileInput.value) {
      logoFileInput.value.value = ''
    }

    updatePreview()
    alert('設定をリセットしました。')
  }
}

// 初期化
onMounted(() => {
  updatePreview()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.template-settings {
  @include page-container;
}

.page-header {
  @include page-header;
}

.page-title {
  @include page-title;
}

.page-subtitle {
  @include small-text;
  margin: 0;
  font-style: normal;
  font-weight: 300;
}

// レイアウト
.content-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);

  @media (max-width: $breakpoint-md) {
    grid-template-columns: 1fr;
  }
}

// 設定パネル
.settings-panel {
  @include card;
  padding: 0;
}

.panel-title {
  font-size: 1.5rem;
  font-weight: $font-weight-medium;
  color: var(--primary-main);
  margin: 0 0 var(--spacing-lg) 0;
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-sm);
  border-bottom: 2px solid var(--primary-main);
}

.template-form {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

// ファイルアップロード
.file-upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-xl);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--background-default);

  &:hover, &.dragover {
    border-color: var(--primary-main);
    background: var(--background-paper);
  }
}

.upload-icon {
  font-size: 3rem;
  color: var(--text-disabled);
  margin-bottom: var(--spacing-md);
}

.upload-text {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
}

.upload-hint {
  font-size: 0.75rem;
  color: var(--text-disabled);
}

.file-input {
  display: none;
}

.current-logo {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--background-default);

  .logo-label {
    margin-bottom: var(--spacing-sm);
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  .logo-preview {
    max-width: 200px;
    max-height: 100px;
    object-fit: contain;
    margin-bottom: var(--spacing-sm);
  }
}

// カラーパレット
.color-palette {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}

.color-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;

  &:hover {
    border-color: var(--primary-main);
    box-shadow: var(--shadow-1);
  }

  &.selected {
    border-color: var(--primary-main);
    background: var(--background-paper);
    box-shadow: var(--shadow-2);
  }
}

.color-preview {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-bottom: var(--spacing-sm);
  border: 1px solid var(--border-color);
}

.color-name {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: pre-line;
}

// フォントサイズオプション
.font-size-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}

.font-size-option {
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    border-color: var(--primary-main);
    box-shadow: var(--shadow-1);
  }

  &.selected {
    border-color: var(--primary-main);
    background: var(--background-paper);
    box-shadow: var(--shadow-2);
  }
}

.font-size-label {
  font-size: 0.875rem;
  font-weight: $font-weight-medium;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.font-size-example {
  color: var(--text-secondary);
}

// プレビューパネル
.preview-panel {
  @include card;
  padding: 0;
  position: sticky;
  top: var(--spacing-xl);
  max-height: calc(100vh - 2 * var(--spacing-xl));
  overflow-y: auto;
}

.preview-description {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
  font-size: 0.875rem;
  padding: 0 var(--spacing-lg);
}

.preview-document {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-xl);
  background: var(--background-default);
  box-shadow: var(--shadow-1);
  margin: 0 var(--spacing-lg) var(--spacing-lg);
}

.preview-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--preview-primary, var(--primary-main));
}

.preview-logo-container {
  margin-bottom: var(--spacing-md);
}

.preview-logo {
  max-width: 150px;
  max-height: 80px;
  object-fit: contain;
}

.preview-business-name {
  font-size: 1.5rem;
  font-weight: $font-weight-bold;
  color: var(--preview-primary, var(--primary-main));
  margin-bottom: var(--spacing-sm);
}

.preview-operator-name {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
}

.preview-title {
  font-size: 2rem;
  font-weight: $font-weight-bold;
  color: var(--text-primary);
}

.preview-content {
  margin-top: var(--spacing-lg);
}

.preview-section {
  margin-bottom: var(--spacing-lg);
}

.preview-section-title {
  font-size: calc(1.25rem * var(--preview-font-size, 1));
  font-weight: $font-weight-medium;
  color: var(--preview-primary, var(--primary-main));
  margin-bottom: var(--spacing-md);
  border-left: 4px solid var(--preview-accent, var(--success-main));
  padding-left: var(--spacing-md);
}

.preview-text {
  color: var(--text-primary);
  line-height: 1.8;
  font-size: var(--preview-font-size, 1rem);

  p {
    margin-bottom: var(--spacing-sm);
  }
}

// アクションボタン
.action-buttons {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);

  .btn {
    @include button-base;

    &.btn-success {
      @include button-primary;
      background: var(--success-main);

      &:hover:not(:disabled) {
        background: var(--success-dark, #138d75);
      }
    }
  }
}
</style>