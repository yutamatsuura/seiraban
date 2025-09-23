<template>
  <div class="template-settings">
    <div class="header">
      <h1>テンプレート設定</h1>
      <p>鑑定書のデザインとブランディングを設定します</p>
    </div>

    <!-- エラー・成功メッセージ -->
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <!-- 読み込み中 -->
    <div v-if="loading" class="loading">
      設定を読み込み中...
    </div>

    <!-- 設定フォーム -->
    <div v-else class="settings-form">
      <div class="form-group">
        <label for="business_name">事業者名 *</label>
        <input
          id="business_name"
          v-model="form.business_name"
          type="text"
          placeholder="占いサロン 星花"
          required
        />
      </div>

      <div class="form-group">
        <label for="operator_name">鑑定士名 *</label>
        <input
          id="operator_name"
          v-model="form.operator_name"
          type="text"
          placeholder="星野 花子"
          required
        />
      </div>

      <div class="form-group">
        <label for="color_theme">カラーテーマ</label>
        <select id="color_theme" v-model="form.color_theme">
          <option value="default">デフォルト</option>
          <option value="elegant">エレガント</option>
          <option value="warm">ウォーム</option>
          <option value="natural">ナチュラル</option>
          <option value="professional">プロフェッショナル</option>
        </select>
      </div>

      <div class="form-group">
        <label for="font_family">フォントファミリー</label>
        <select id="font_family" v-model="form.font_family">
          <option value="default">デフォルト</option>
          <option value="noto-serif">Noto Serif JP</option>
          <option value="noto-sans">Noto Sans JP</option>
          <option value="mincho">明朝体</option>
          <option value="gothic">ゴシック体</option>
        </select>
      </div>

      <div class="form-group">
        <label for="layout_style">レイアウトスタイル</label>
        <select id="layout_style" v-model="form.layout_style">
          <option value="standard">スタンダード</option>
          <option value="compact">コンパクト</option>
          <option value="detailed">詳細</option>
        </select>
      </div>

      <div class="form-group">
        <label for="custom_css">カスタムCSS（任意）</label>
        <textarea
          id="custom_css"
          v-model="form.custom_css"
          rows="4"
          placeholder="/* カスタムCSSを入力 */&#10;.diagnosis-title { color: #333; }"
        ></textarea>
      </div>

      <div class="form-actions">
        <button
          type="button"
          @click="saveSettings"
          :disabled="saving || !isFormValid"
          class="btn btn-primary"
        >
          {{ saving ? '保存中...' : '設定を保存' }}
        </button>

        <button
          type="button"
          @click="loadSettings"
          :disabled="loading"
          class="btn btn-secondary"
        >
          設定を再読み込み
        </button>
      </div>
    </div>

    <!-- 現在の設定値表示（デバッグ用） -->
    <div class="debug-info">
      <h3>現在の設定値</h3>
      <pre>{{ JSON.stringify(form, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/services/api-client'

// データ状態
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// フォームデータ
const form = ref({
  business_name: '',
  operator_name: '',
  color_theme: 'default',
  font_family: 'default',
  layout_style: 'standard',
  custom_css: ''
})

// バリデーション
const isFormValid = computed(() => {
  return form.value.business_name.trim() !== '' &&
         form.value.operator_name.trim() !== ''
})

// 設定読み込み
const loadSettings = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await apiClient.getTemplateSettings()

    // APIレスポンスをフォームに反映
    form.value = {
      business_name: response.business_name || '',
      operator_name: response.operator_name || '',
      color_theme: response.color_theme || 'default',
      font_family: response.font_family || 'default',
      layout_style: response.layout_style || 'standard',
      custom_css: response.custom_css || ''
    }

    successMessage.value = '設定を読み込みました'
    setTimeout(() => successMessage.value = '', 3000)
  } catch (error: any) {
    errorMessage.value = error.message || '設定の読み込みに失敗しました'
    console.error('設定読み込みエラー:', error)
  } finally {
    loading.value = false
  }
}

// 設定保存
const saveSettings = async () => {
  if (!isFormValid.value || saving.value) return

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const updateData = {
      business_name: form.value.business_name.trim(),
      operator_name: form.value.operator_name.trim(),
      color_theme: form.value.color_theme,
      font_family: form.value.font_family,
      layout_style: form.value.layout_style,
      custom_css: form.value.custom_css.trim() || undefined
    }

    const response = await apiClient.updateTemplateSettings(updateData)

    successMessage.value = '設定を保存しました'
    setTimeout(() => successMessage.value = '', 3000)

    console.log('保存完了:', response)
  } catch (error: any) {
    errorMessage.value = error.message || '設定の保存に失敗しました'
    console.error('設定保存エラー:', error)
  } finally {
    saving.value = false
  }
}

// コンポーネント初期化
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.template-settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.header p {
  margin: 0;
  color: #666;
}

.alert {
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.alert-error {
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
}

.alert-success {
  background-color: #efe;
  border: 1px solid #cfc;
  color: #363;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.settings-form {
  background: #f9f9f9;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
}

.form-actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.debug-info {
  background: #f0f0f0;
  padding: 20px;
  border-radius: 4px;
  margin-top: 30px;
}

.debug-info h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.debug-info pre {
  background: white;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin: 0;
}
</style>