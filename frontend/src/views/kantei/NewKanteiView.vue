<template>
  <MainLayout>
    <div class="new-kantei">
    <div class="page-header">
      <h1 class="page-title">
        <img src="/src/assets/icons/document-create.svg" alt="鑑定書作成" class="page-title-icon" />
        新しい鑑定書作成
      </h1>
      <p>お客様の情報を入力して鑑定を開始してください</p>
    </div>

    <!-- エラーメッセージ -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 成功メッセージ -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <div class="card">
      <div class="card-header">
        <h2>基本情報入力</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="submitDiagnosis" class="kantei-form">
          <!-- お客様名（姓と名を分けて入力） -->
          <div class="form-group">
            <label class="form-label required">お客様名</label>
            <div class="name-inputs">
              <div class="name-input-group">
                <label for="lastName" class="sub-label">姓</label>
                <input
                  v-model="form.lastName"
                  type="text"
                  id="lastName"
                  class="form-input"
                  placeholder="田中"
                  required
                  :disabled="loading"
                  @input="validateInput('lastName', $event)"
                  maxlength="9"
                />
              </div>
              <div class="name-input-group">
                <label for="firstName" class="sub-label">名</label>
                <input
                  v-model="form.firstName"
                  type="text"
                  id="firstName"
                  class="form-input"
                  placeholder="太郎"
                  required
                  :disabled="loading"
                  @input="validateInput('firstName', $event)"
                  maxlength="9"
                />
              </div>
            </div>
            <div class="field-help">
              ※姓と名を分けて入力してください（各9文字まで）。ひらがな、カタカナ、漢字のみ使用可能です。
            </div>
            <div v-if="nameValidationError" class="validation-error">
              {{ nameValidationError }}
              <div v-if="nameSuggestion" class="name-suggestion">
                <strong>推奨表記:</strong> {{ nameSuggestion }}
                <button
                  type="button"
                  class="suggestion-button"
                  @click="applySuggestion"
                >
                  この表記を使用
                </button>
              </div>
            </div>
          </div>

          <!-- 生年月日 -->
          <div class="form-group">
            <label for="birthDate" class="form-label required">生年月日</label>
            <input
              v-model="form.birthDate"
              type="date"
              id="birthDate"
              class="form-input"
              required
              :disabled="loading"
            />
          </div>

          <!-- 性別 -->
          <div class="form-group">
            <label class="form-label required">性別</label>
            <div class="radio-group">
              <label class="radio-item">
                <input
                  v-model="form.gender"
                  type="radio"
                  name="gender"
                  value="male"
                  :disabled="loading"
                />
                <span>男性</span>
              </label>
              <label class="radio-item">
                <input
                  v-model="form.gender"
                  type="radio"
                  name="gender"
                  value="female"
                  :disabled="loading"
                />
                <span>女性</span>
              </label>
            </div>
          </div>


          <!-- アクションボタン -->
          <div class="form-actions">
            <button
              type="button"
              class="btn btn-secondary"
              @click="resetForm"
              :disabled="loading"
            >
              リセット
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="loading || !isFormValid"
            >
              <div class="button-content">
                <div v-if="loading" class="loading-spinner"></div>
                <span>{{ loading ? '鑑定を開始しています...' : '鑑定を開始' }}</span>
              </div>
            </button>
          </div>
        </form>
      </div>
    </div>

    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient, type DiagnosisRequest } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'

const router = useRouter()

// フォーム状態
const form = ref({
  lastName: '',
  firstName: '',
  birthDate: '',
  gender: '' as 'male' | 'female' | ''
})

// UI状態
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const nameValidationError = ref('')
const nameSuggestion = ref('')
const suggestionType = ref<'lastName' | 'firstName' | null>(null)

// 日本語文字のバリデーション関数
const isValidJapanese = (text: string): boolean => {
  // 漢字、ひらがな、カタカナ（小文字含む）のみ許可
  const japanesePattern = /^[一-龯あ-ゖァ-ヶ]+$/
  return japanesePattern.test(text)
}

// 特殊文字チェック（姓名判断システムで処理できない文字）
const hasUnsupportedCharacters = (text: string): boolean => {
  // 姓名判断システムで問題になる可能性のある文字をチェック
  const problematicChars = ['ー', '々', '〆', '〇', '〈', '〉', '《', '》', '「', '」', '盧', '廬']
  return problematicChars.some(char => text.includes(char))
}

// 代替案生成関数
const generateSuggestion = (text: string): string => {
  const replacements: Record<string, string> = {
    '々': '', // 々は除去して前の文字を繰り返し
    'ー': '',
    '〆': 'しめ',
    '〇': '○',
    '〈': '',
    '〉': '',
    '《': '',
    '》': '',
    '「': '',
    '」': '',
    '盧': '呂',
    '廬': '庵'
  }

  let suggestion = text

  // 々の特別処理（前の文字を繰り返し）
  suggestion = suggestion.replace(/(.)\々/g, '$1$1')

  // その他の文字の置換
  for (const [from, to] of Object.entries(replacements)) {
    if (from !== '々') { // 々は上で処理済み
      suggestion = suggestion.replace(new RegExp(from, 'g'), to)
    }
  }

  return suggestion
}

// より詳細な文字バリデーション
const getCharacterValidationMessage = (text: string): string => {
  if (text === '') return ''

  if (!isValidJapanese(text)) {
    return '姓名には漢字、ひらがな、カタカナのみ使用できます'
  }

  if (hasUnsupportedCharacters(text)) {
    const problematicChars = ['ー', '々', '〆', '〇', '〈', '〉', '《', '》', '「', '」', '盧', '廬']
    const foundChars = problematicChars.filter(char => text.includes(char))
    return `「${foundChars.join('、')}」は姓名判断システムで処理できません。別の表記をお試しください。`
  }

  return ''
}

// 入力バリデーション
const validateInput = (field: 'lastName' | 'firstName', event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value

  // 詳細なバリデーションメッセージを取得
  const validationMessage = getCharacterValidationMessage(value)
  nameValidationError.value = validationMessage

  // 代替案生成
  if (hasUnsupportedCharacters(value)) {
    const suggestion = generateSuggestion(value)
    if (suggestion !== value && suggestion.trim() !== '') {
      nameSuggestion.value = suggestion
      suggestionType.value = field
    } else {
      nameSuggestion.value = ''
      suggestionType.value = null
    }
  } else {
    nameSuggestion.value = ''
    suggestionType.value = null
  }

  // 基本的な日本語文字以外を削除（ただし問題のある文字は残す）
  if (!isValidJapanese(value) && value !== '') {
    // 完全に無効な文字（アルファベット、数字など）のみ削除
    const cleanValue = value.replace(/[^一-龯あ-ゖア-ヶー々〆〇〈〉《》「」]/g, '')
    if (cleanValue !== value) {
      form.value[field] = cleanValue
    }
  }
}

// バリデーション
const isFormValid = computed(() => {
  const hasBasicInfo = form.value.lastName.trim() !== '' &&
                      form.value.firstName.trim() !== '' &&
                      form.value.birthDate !== '' &&
                      form.value.gender !== '' &&
                      nameValidationError.value === ''

  const hasValidCharacters = isValidJapanese(form.value.lastName) &&
                            isValidJapanese(form.value.firstName) &&
                            !hasUnsupportedCharacters(form.value.lastName) &&
                            !hasUnsupportedCharacters(form.value.firstName)

  return hasBasicInfo && hasValidCharacters
})

// 代替案適用
const applySuggestion = () => {
  if (nameSuggestion.value && suggestionType.value) {
    form.value[suggestionType.value] = nameSuggestion.value
    nameSuggestion.value = ''
    suggestionType.value = null
    nameValidationError.value = ''
  }
}

// フォームリセット
const resetForm = () => {
  form.value = {
    lastName: '',
    firstName: '',
    birthDate: '',
    gender: ''
  }
  errorMessage.value = ''
  successMessage.value = ''
  nameValidationError.value = ''
  nameSuggestion.value = ''
  suggestionType.value = null
}

// 鑑定開始
const submitDiagnosis = async () => {
  if (!isFormValid.value || loading.value) return

  console.log('🚀 鑑定開始ボタンが押されました')
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const fullName = `${form.value.lastName} ${form.value.firstName}`
    const request: DiagnosisRequest = {
      client_name: fullName,
      birth_date: form.value.birthDate,
      gender: form.value.gender,
      name_for_seimei: fullName // 姓名判断も自動的に実行
    }

    console.log('📤 API呼び出し開始', request)
    const response = await apiClient.createDiagnosis(request)
    console.log('📥 API呼び出し完了', response)

    if (response.success) {
      console.log('✅ 鑑定作成成功 - ページ遷移開始', response.diagnosis_id)
      // すぐに結果ページに遷移
      await router.push(`/kantei/preview/${response.diagnosis_id}`)
      console.log('✅ ページ遷移完了')
    } else {
      console.error('❌ 鑑定作成失敗', response)
      errorMessage.value = '鑑定の開始に失敗しました'
    }
  } catch (error: any) {
    console.error('❌ 鑑定開始エラー', error)
    errorMessage.value = error.message || '鑑定の開始に失敗しました'
  } finally {
    loading.value = false
  }
}

</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.new-kantei {
  @include page-container;
}

.page-header {
  @include page-header;

  h1 {
    @include page-title;
  }

  p {
    @include small-text;
    margin: 0;
    font-style: normal;
    font-weight: 300;
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
  background: linear-gradient(135deg, #f0fdf9, #ecfdf5);
  color: #059669;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  font-size: 1rem;
  position: relative;
  overflow: hidden;

  &::before {
    content: '✨';
    font-size: 1.5rem;
    animation: sparkle 1.5s ease-in-out infinite;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shimmer 2s ease-in-out infinite;
  }
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.card {
  @include card;

  // すべてのインタラクティブ要素が確実にクリック・選択できるように
  .form-input, input, select, textarea, button, .btn,
  label, .form-label, .sub-label, .radio-item,
  .field-help, .validation-error, span, p, h1, h2, h3 {
    position: relative;
    z-index: 10;
  }

  // ラジオボタングループ全体もz-indexを設定
  .radio-group {
    position: relative;
    z-index: 10;
  }
}

.card-header {
  background: var(--background-paper);
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);

  h2, h3 {
    margin: 0;
    font-size: 1.25rem;
    color: var(--text-primary);
  }
}

.card-body {
  padding: 24px;
}

.kantei-form {
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

    .optional {
      color: var(--text-secondary);
      font-weight: normal;
    }
  }

  .form-input {
    @include form-input;

    &:disabled {
      background-color: var(--background-default);
      opacity: 0.7;
    }
  }

  .radio-group {
    display: flex;
    gap: 16px;

    .radio-item {
      display: flex;
      align-items: center;
      cursor: pointer;

      input[type="radio"] {
        margin-right: 8px;
      }

      span {
        font-size: 1rem;
        color: var(--text-primary);
      }
    }
  }

  .field-help {
    margin-top: 6px;
    font-size: 0.75rem;
    color: var(--text-secondary);
  }

  .name-inputs {
    display: flex;
    gap: 1rem;
  }

  .name-input-group {
    flex: 1;

    .sub-label {
      display: block;
      font-size: 0.9rem;
      font-weight: 500;
      color: #374151;
      margin-bottom: 0.25rem;
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
  justify-content: center;

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

  &.btn-secondary {
    @include button-secondary;
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

  .button-content {
    display: flex;
    align-items: center;

    .loading-spinner {
      width: 20px;
      height: 20px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-right: 8px;
    }
  }
}

.validation-error {
  margin-top: 6px;
  font-size: 0.75rem;
  color: #e74c3c;
  font-weight: 500;
}

.name-suggestion {
  margin-top: 12px;
  padding: 12px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  color: #856404;

  .suggestion-button {
    background: #007bff;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    margin-left: 8px;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background: #0056b3;
    }

    &:focus {
      outline: 2px solid #80bdff;
      outline-offset: 2px;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// レスポンシブ
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }


  .radio-group {
    flex-direction: column;
    gap: 8px;
  }
}
</style>