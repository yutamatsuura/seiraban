<template>
  <MainLayout>
    <div class="template-settings-view">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">
        <img src="/src/assets/icons/template.svg" alt="テンプレート設定" class="page-title-icon" />
        テンプレート設定
      </h1>
      <p class="page-subtitle">鑑定書のレイアウトとデザインをカスタマイズできます</p>
    </div>

    <!-- Main Content -->
    <div class="main-content" :class="{ 'settings-collapsed': isSettingsCollapsed }">
      <!-- Settings Panel (Mobile First) -->
      <div class="settings-panel mobile-panel" :class="{ collapsed: isSettingsCollapsed }">
        <div class="panel-header">
          <h2 v-if="!isSettingsCollapsed">カスタマイズ設定</h2>
          <div v-if="isSettingsCollapsed" class="collapsed-indicator">
            <span class="material-icons">tune</span>
            <span class="collapsed-text">設定</span>
          </div>
          <button @click="toggleSettings" class="collapse-btn" :title="isSettingsCollapsed ? '設定パネルを展開' : '設定パネルを閉じる'">
            <span class="material-icons">{{ isSettingsCollapsed ? 'expand_more' : 'expand_less' }}</span>
          </button>
        </div>

        <div v-if="!isSettingsCollapsed" class="panel-content">
          <!-- Settings Form -->
          <form @submit.prevent="saveSettings" class="settings-form">
            <!-- Basic Information -->
            <div class="form-section">
              <h3>基本情報</h3>
              <div class="form-group">
                <label for="businessName">事業者名</label>
                <input
                  id="businessName"
                  v-model="templateSettings.businessName"
                  type="text"
                  placeholder="事業者名を入力"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="operatorName">鑑定者名</label>
                <input
                  id="operatorName"
                  v-model="templateSettings.operatorName"
                  type="text"
                  placeholder="鑑定者名を入力"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="diagnosisTitle">鑑定書タイトル</label>
                <input
                  id="diagnosisTitle"
                  v-model="templateSettings.diagnosisTitle"
                  type="text"
                  placeholder="鑑定書タイトルを入力"
                  class="form-input"
                />
              </div>
            </div>

            <!-- Logo Settings -->
            <div class="form-section">
              <h3>ロゴ設定</h3>
              <div class="form-group">
                <label for="logoUrl">ロゴURL</label>
                <input
                  id="logoUrl"
                  v-model="templateSettings.logoUrl"
                  type="url"
                  placeholder="https://example.com/logo.png"
                  class="form-input"
                />
                <p class="form-help">ロゴ画像のURLを入力してください</p>
              </div>
            </div>

            <!-- Color Settings -->
            <div class="form-section">
              <h3>カラー設定</h3>
              <div class="form-group">
                <label for="primaryColor">メインカラー</label>
                <input
                  id="primaryColor"
                  v-model="templateSettings.primaryColor"
                  type="color"
                  class="form-input color-input"
                />
              </div>
              <div class="form-group">
                <label for="accentColor">アクセントカラー</label>
                <input
                  id="accentColor"
                  v-model="templateSettings.accentColor"
                  type="color"
                  class="form-input color-input"
                />
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="form-actions">
              <button
                type="button"
                @click="resetToDefaults"
                class="btn btn-secondary"
                :disabled="isSaving"
              >
                デフォルトに戻す
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSaving"
              >
                {{ isSaving ? '保存中...' : '設定を保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Preview Area -->
      <div class="preview-area">
        <div class="preview-header">
          <h2>プレビュー</h2>
          <button
            class="refresh-btn"
            @click="refreshPreview"
          >
            更新
          </button>
        </div>

        <!-- Template Preview -->
        <div class="template-preview">
          <!-- プレビューコンテンツ全体にpattern-cleanクラスを適用 -->
          <div class="diagnosis-content pattern-clean" :style="templateStyles">
          <!-- Header Section - 実際のPreviewView.vueと同じ構造 -->
          <div class="template-header modern-minimal">
            <div class="header-background"></div>
            <div class="header-content">
              <!-- Logo Section -->
              <div class="logo-section">
                <div v-if="templateSettings.logoUrl" class="logo-container">
                  <img :src="templateSettings.logoUrl" alt="ロゴ" class="logo-image" />
                </div>
                <div v-else class="logo-placeholder">
                  <div class="logo-placeholder-content">
                    ロゴ未設定
                  </div>
                </div>
              </div>

              <!-- Main Title Section -->
              <div class="title-section">
                <div class="title-ornament"></div>
                <h1 class="diagnosis-title">
                  {{ templateSettings.diagnosisTitle || '九星気学・姓名判断 総合鑑定書' }}
                </h1>
                <div class="title-ornament"></div>
              </div>

              <!-- Business Info Section -->
              <div class="business-section">
                <div v-if="templateSettings.businessName" class="business-card">
                  <div class="business-info">
                    <h2 class="business-name">{{ templateSettings.businessName }}</h2>
                    <p v-if="templateSettings.operatorName" class="operator-name">
                      <span class="operator-label">鑑定士</span>
                      <span class="operator-value">{{ templateSettings.operatorName }}</span>
                    </p>
                  </div>
                </div>
                <div v-else class="business-card debug-placeholder">
                  <div class="business-info">
                    <h2 class="business-name">事業者名未設定</h2>
                    <p class="operator-name">
                      <span class="operator-label">鑑定士</span>
                      <span class="operator-value">鑑定者名未設定</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Date Section -->
            <div class="date-section">
              <div class="date-container">
                <span class="date-label">鑑定実施日</span>
                <span class="date-value">{{ formatDate(new Date()) }}</span>
              </div>
            </div>
          </div>

          <!-- Client Information -->
          <div class="card client-info">
            <div class="card-header">
              <h2>依頼者情報</h2>
            </div>
            <div class="card-body">
              <div class="info-grid">
                <div class="info-item">
                  <label>お名前</label>
                  <span>山田 花子</span>
                </div>
                <div class="info-item">
                  <label>生年月日</label>
                  <span>1985年4月15日 (39歳)</span>
                </div>
                <div class="info-item">
                  <label>十二支</label>
                  <span>丑年</span>
                </div>
                <div class="info-item">
                  <label>性別</label>
                  <span>女性</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Kyusei Results -->
          <div class="card kyusei-results">
            <div class="card-header">
              <h2>九星気学・吉方位の鑑定結果</h2>
            </div>
            <div class="card-body">
              <!-- Basic Nine Star Information -->
              <div class="section">
                <h3>基本九星情報</h3>
                <div class="nine-star-grid">
                  <div class="star-item">
                    <label>本命星</label>
                    <span class="star-value">八白土星</span>
                  </div>
                  <div class="star-item">
                    <label>月命星</label>
                    <span class="star-value">三碧木星</span>
                  </div>
                </div>
              </div>

              <!-- Zodiac Information -->
              <div class="section">
                <h3>干支情報</h3>
                <div class="zodiac-grid">
                  <div class="zodiac-item">
                    <label>年干支</label>
                    <span>乙丑</span>
                  </div>
                  <div class="zodiac-item">
                    <label>月干支</label>
                    <span>庚辰</span>
                  </div>
                  <div class="zodiac-item">
                    <label>日干支</label>
                    <span>甲申</span>
                  </div>
                </div>
              </div>

              <!-- Direction Information -->
              <div class="section">
                <h3>吉方位情報</h3>
                <div class="direction-grid">
                  <div class="direction-item">
                    <label>最大吉方</label>
                    <span>北東</span>
                  </div>
                  <div class="direction-item">
                    <label>吉方</label>
                    <span>南西</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Seimei Results -->
          <div class="card seimei-results">
            <div class="card-header">
              <h2>姓名判断の鑑定結果</h2>
            </div>
            <div class="card-body">
              <!-- Character Table -->
              <div class="section">
                <h3>文字の構成</h3>
                <div class="character-table">
                  <table>
                    <thead>
                      <tr>
                        <th>文字</th>
                        <th>姓1</th>
                        <th>姓2</th>
                        <th>名1</th>
                        <th>名2</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>漢字</td>
                        <td>山</td>
                        <td>田</td>
                        <td>花</td>
                        <td>子</td>
                      </tr>
                      <tr>
                        <td>画数</td>
                        <td>3</td>
                        <td>5</td>
                        <td>7</td>
                        <td>3</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Stroke Results -->
              <div class="section">
                <h3>画数の鑑定結果</h3>
                <div class="stroke-grid">
                  <div class="stroke-item">
                    <label>天格</label>
                    <span>8画</span>
                  </div>
                  <div class="stroke-item">
                    <label>人格</label>
                    <span>12画</span>
                  </div>
                  <div class="stroke-item">
                    <label>地格</label>
                    <span>10画</span>
                  </div>
                  <div class="stroke-item">
                    <label>総格</label>
                    <span>18画</span>
                  </div>
                </div>
              </div>

              <!-- Result Content -->
              <div class="section">
                <div class="result-content">
                  <div class="score-section">
                    <span class="score-value">75</span>
                    <span class="score-label">点</span>
                  </div>
                  <div class="message-section">
                    <p>総合的に良いバランスの名前です。人格運が特に良く、対人関係に恵まれる傾向があります。</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer Section -->
          <div class="template-footer modern-minimal">
            <div class="footer-content">
              <div class="footer-info">
                <div class="footer-business">{{ templateSettings.businessName || '事業者名未設定' }}</div>
                <div class="footer-operator">鑑定士: {{ templateSettings.operatorName || '鑑定者名未設定' }}</div>
              </div>
              <div class="footer-disclaimer">
                本鑑定書は参考情報としてご活用ください。結果について一切の責任を負いません。
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      <!-- Settings Panel (Desktop) -->
      <div class="settings-panel desktop-panel" :class="{ collapsed: isSettingsCollapsed }">
        <div class="panel-header">
          <h2 v-if="!isSettingsCollapsed">カスタマイズ設定</h2>
          <div v-if="isSettingsCollapsed" class="collapsed-indicator">
            <span class="material-icons">tune</span>
            <span class="collapsed-text">設定</span>
          </div>
          <button @click="toggleSettings" class="collapse-btn" :title="isSettingsCollapsed ? '設定パネルを展開' : '設定パネルを閉じる'">
            <span class="material-icons">{{ isSettingsCollapsed ? 'chevron_left' : 'chevron_right' }}</span>
          </button>
        </div>

        <div v-if="!isSettingsCollapsed" class="panel-content">
          <!-- Settings Form -->
          <form @submit.prevent="saveSettings" class="settings-form">
            <!-- Basic Information -->
            <div class="form-section">
              <h3>基本情報</h3>
              <div class="form-group">
                <label for="businessName">事業者名</label>
                <input
                  id="businessName"
                  v-model="templateSettings.businessName"
                  type="text"
                  placeholder="事業者名を入力"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="operatorName">鑑定者名</label>
                <input
                  id="operatorName"
                  v-model="templateSettings.operatorName"
                  type="text"
                  placeholder="鑑定者名を入力"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="diagnosisTitle">鑑定書タイトル</label>
                <input
                  id="diagnosisTitle"
                  v-model="templateSettings.diagnosisTitle"
                  type="text"
                  placeholder="鑑定書タイトルを入力"
                  class="form-input"
                />
              </div>
            </div>

            <!-- Logo Settings -->
            <div class="form-section">
              <h3>ロゴ設定</h3>
              <div class="form-group">
                <label for="logoUrl">ロゴURL</label>
                <input
                  id="logoUrl"
                  v-model="templateSettings.logoUrl"
                  type="url"
                  placeholder="https://example.com/logo.png"
                  class="form-input"
                />
                <p class="form-help">ロゴ画像のURLを入力してください</p>
              </div>
            </div>

            <!-- Color Settings -->
            <div class="form-section">
              <h3>カラー設定</h3>
              <div class="form-group">
                <label for="primaryColor">メインカラー</label>
                <input
                  id="primaryColor"
                  v-model="templateSettings.primaryColor"
                  type="color"
                  class="form-input color-input"
                />
              </div>
              <div class="form-group">
                <label for="accentColor">アクセントカラー</label>
                <input
                  id="accentColor"
                  v-model="templateSettings.accentColor"
                  type="color"
                  class="form-input color-input"
                />
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="form-actions">
              <button
                type="button"
                @click="resetToDefaults"
                class="btn btn-secondary"
                :disabled="isSaving"
              >
                デフォルトに戻す
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSaving"
              >
                {{ isSaving ? '保存中...' : '設定を保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { apiClient } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'

// Types
interface TemplateSettings {
  businessName: string
  operatorName: string
  diagnosisTitle: string
  logoUrl: string
  primaryColor: string
  accentColor: string
}

// Stores
const userStore = useUserStore()

// Reactive Data
const isSaving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isSettingsCollapsed = ref(true)

const templateSettings = reactive<TemplateSettings>({
  businessName: '',
  operatorName: '',
  diagnosisTitle: '鑑定書',
  logoUrl: '',
  primaryColor: '#3498db',
  accentColor: '#2980b9'
})

// Default Settings
const defaultSettings: TemplateSettings = {
  businessName: '',
  operatorName: '',
  diagnosisTitle: '鑑定書',
  logoUrl: '',
  primaryColor: '#3498db',
  accentColor: '#2980b9'
}

// 設定パネルの開閉
const toggleSettings = () => {
  isSettingsCollapsed.value = !isSettingsCollapsed.value
}

// Methods
const loadSettings = async () => {
  try {
    errorMessage.value = ''

    const settings = await apiClient.getTemplateSettings()

    if (settings) {
      Object.assign(templateSettings, settings)
    }
  } catch (error) {
    console.error('設定の読み込みに失敗:', error)
    errorMessage.value = '設定の読み込みに失敗しました'
  }
}

const saveSettings = async () => {
  try {
    isSaving.value = true
    errorMessage.value = ''
    successMessage.value = ''

    await apiClient.updateTemplateSettings(templateSettings)

    successMessage.value = '設定を保存しました'

    // Success message auto-hide
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('設定の保存に失敗:', error)
    errorMessage.value = '設定の保存に失敗しました'
  } finally {
    isSaving.value = false
  }
}

const resetToDefaults = () => {
  Object.assign(templateSettings, defaultSettings)
  successMessage.value = 'デフォルト設定に戻しました'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

const refreshPreview = () => {
  // Preview refresh logic if needed
  console.log('プレビューを更新しました')
}

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Watchers
watch([
  () => templateSettings.primaryColor,
  () => templateSettings.accentColor
], ([primaryColor, accentColor]) => {
  // Apply CSS variables for live preview
  document.documentElement.style.setProperty('--primary-color', primaryColor)
  document.documentElement.style.setProperty('--accent-color', accentColor)
})

// Lifecycle
onMounted(async () => {
  if (!userStore.isAuthenticated) {
    errorMessage.value = 'ログインが必要です'
    return
  }

  await loadSettings()

  // Apply initial colors
  document.documentElement.style.setProperty('--primary-color', templateSettings.primaryColor)
  document.documentElement.style.setProperty('--accent-color', templateSettings.accentColor)
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
// 完全独立スタイル - diagnosis-templates.scssをApp.vueで管理することで競合を回避
.template-settings-view {
  @include page-container;
}

.page-header {
  @include page-header;

  .page-title {
    @include page-title;
    display: flex;
    align-items: center;
    gap: 12px;

    .page-title-icon {
      width: 32px;
      height: 32px;
    }
  }

  .page-subtitle {
    @include small-text;
    margin: 0;
    font-style: normal;
    font-weight: 300;
  }
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  align-items: start;
  transition: grid-template-columns 0.3s ease;

  &.settings-collapsed {
    grid-template-columns: 1fr 80px;
  }

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;

    .mobile-panel {
      order: -1;
    }

    .desktop-panel {
      display: none;
    }

    &.settings-collapsed {
      grid-template-columns: 1fr;

      .mobile-panel {
        &.collapsed {
          height: 60px;
          width: 100%;
          background: linear-gradient(90deg, #3498db, #2980b9);

          .panel-header {
            flex-direction: row;
            padding: 16px 24px;

            .collapsed-indicator {
              flex-direction: row;
              gap: 8px;

              .collapsed-text {
                font-size: 14px;
              }
            }

            .collapse-btn .material-icons {
              transform: rotate(0deg);
            }
          }

          &::before {
            display: none;
          }
        }
      }
    }
  }
}

.preview-area {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  overflow: hidden;

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;

    h2 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
      color: #333;
    }

    .refresh-btn {
      padding: 8px 16px;
      border: 1px solid #ddd;
      border-radius: 6px;
      background: white;
      color: #666;
      cursor: pointer;
      font-size: 0.9rem;

      &:hover:not(:disabled) {
        background: #f0f0f0;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }

  .template-preview {
    padding: 24px;
    // 高さ制限を削除してスクロールバー不要に
  }
}

.settings-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  overflow: hidden;
  transition: all 0.3s ease;

  &.desktop-panel {
    position: sticky;
    top: 20px;

    @media (max-width: 1200px) {
      display: none;
    }
  }

  &.mobile-panel {
    display: none;

    @media (max-width: 1200px) {
      display: block;
      position: relative;
      top: 0;
      margin-bottom: 24px;
    }
  }

  &.collapsed {
    width: 80px;
    background: linear-gradient(135deg, #3498db, #2980b9);
    border: 2px solid #2980b9;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);

    .panel-header {
      padding: 16px 8px;
      background: transparent;
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      flex-direction: column;
      gap: 8px;

      .collapsed-indicator {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        color: white;

        .material-icons {
          font-size: 24px;
        }

        .collapsed-text {
          font-size: 10px;
          font-weight: 600;
          text-align: center;
          white-space: nowrap;
        }
      }

      .collapse-btn {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);

        &:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .material-icons {
          color: white;
        }
      }
    }

    &::before {
      content: '設定パネルをクリックで展開';
      position: absolute;
      top: -30px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(52, 152, 219, 0.9);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      white-space: nowrap;
      opacity: 0;
      animation: fadeInOut 3s ease-in-out;
      pointer-events: none;
    }
  }

  .panel-header {
    padding: 20px 24px;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
      color: #333;
    }

    .collapse-btn {
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      transition: background-color 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        background: rgba(0, 0, 0, 0.1);
      }

      .material-icons {
        font-size: 20px;
        color: #666;
      }
    }
  }

  .panel-content {
    padding: 24px;
    max-height: 700px;
    overflow-y: auto;
  }
}


.settings-form {
  .form-section {
    margin-bottom: 32px;

    &:last-child {
      margin-bottom: 0;
    }

    h3 {
      margin: 0 0 16px 0;
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
      padding-bottom: 8px;
      border-bottom: 2px solid #3498db;
    }
  }

  .form-group {
    margin-bottom: 20px;

    label {
      display: block;
      margin-bottom: 6px;
      font-weight: 500;
      color: #333;
      font-size: 0.9rem;
    }

    .form-input {
      width: 100%;
      padding: 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s;

      &:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
      }

      &.color-input {
        width: 60px;
        height: 40px;
        padding: 4px;
        cursor: pointer;
      }
    }

    .form-help {
      margin: 6px 0 0 0;
      font-size: 0.8rem;
      color: #666;
    }
  }

  .form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding-top: 24px;
    border-top: 1px solid #e0e0e0;

    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      &.btn-secondary {
        background: #f8f9fa;
        color: #666;
        border: 1px solid #ddd;

        &:hover:not(:disabled) {
          background: #e9ecef;
        }
      }

      &.btn-primary {
        background: #3498db;
        color: white;

        &:hover:not(:disabled) {
          background: #2980b9;
        }
      }
    }
  }
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #e74c3c;
  color: white;
  padding: 12px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #27ae60;
  color: white;
  padding: 12px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

@keyframes fadeInOut {
  0% { opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { opacity: 0; }
}
</style>