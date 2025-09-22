<template>
  <MainLayout>
    <div class="design-patterns">
      <div class="page-header">
        <h1 class="page-title">
          <span class="page-title-icon">🎨</span>
          鑑定書デザインパターン比較
        </h1>
        <p class="page-subtitle">様々なデザインパターンを比較して理想的なレイアウトを選択できます</p>
      </div>

      <!-- パターン選択 -->
      <div class="pattern-selector">
        <button
          v-for="(pattern, key) in designPatterns"
          :key="key"
          class="pattern-btn"
          :class="{ active: selectedPattern === key }"
          @click="selectPattern(key)"
        >
          {{ pattern.name }}
        </button>
      </div>

      <!-- 選択されたパターンのプレビュー -->
      <div class="pattern-preview">
        <div class="preview-header">
          <h3>{{ designPatterns[selectedPattern].name }} のプレビュー</h3>
          <button
            class="select-pattern-btn"
            @click="selectThisPattern"
          >
この設定を保存する
          </button>
        </div>
        <div
          class="diagnosis-document"
          :class="[`pattern-${selectedPattern}`, `theme-${selectedTheme}`]"
          :style="dynamicStyles"
        >

          <!-- パターンA: クリーン&コンパクト -->
          <template v-if="selectedPattern === 'clean'">
            <div class="template-header modern-minimal">
              <div class="header-background"></div>
              <div class="header-content">
                <div class="logo-section">
                  <div class="logo-placeholder">
                    <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="ロゴ" class="logo-image" />
                    <div v-else class="logo-placeholder-content">ロゴ</div>
                  </div>
                </div>
                <div class="title-section">
                  <div class="title-ornament"></div>
                  <h1 class="diagnosis-title">九星気学・姓名判断 総合鑑定書</h1>
                  <div class="title-ornament"></div>
                </div>
                <div class="business-section">
                  <div class="business-card">
                    <div class="business-name">{{ businessName }}</div>
                    <div class="operator-name">
                      <span class="operator-label">鑑定士</span>
                      <span class="operator-value">{{ operatorName }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="client-info-card">
              <div class="card-header">
                <h2>依頼者情報</h2>
              </div>
              <div class="card-body">
                <div class="info-grid">
                  <div class="info-item">
                    <label>お名前</label>
                    <span>田中 太郎</span>
                  </div>
                  <div class="info-item">
                    <label>生年月日</label>
                    <span>昭和60年3月15日（39歳）</span>
                  </div>
                  <div class="info-item">
                    <label>性別</label>
                    <span>男性</span>
                  </div>
                  <div class="info-item">
                    <label>十二支</label>
                    <span>乙丑</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="client-info-card">
              <div class="card-header">
                <h2>九星気学・吉方位の鑑定結果</h2>
              </div>
              <div class="card-body">
                <div class="section">
                  <h3>基本九星情報</h3>
                  <div class="nine-star-grid">
                    <div class="star-item">
                      <label>本命星</label>
                      <span class="star-value">二黒土星</span>
                    </div>
                    <div class="star-item">
                      <label>月命星</label>
                      <span class="star-value">八白土星</span>
                    </div>
                    <div class="star-item">
                      <label>日命星</label>
                      <span class="star-value">六白金星</span>
                    </div>
                  </div>
                </div>
                <div class="section">
                  <h3>今月の吉方位</h3>
                  <div class="direction-info">
                    <span class="direction-label">最良方位：</span>
                    <span class="direction-value">南東（巽）</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="client-info-card">
              <div class="card-header">
                <h2>姓名判断の鑑定結果</h2>
              </div>
              <div class="card-body">
                <div class="section">
                  <h3>文字の構成</h3>
                  <div class="character-info">
                    <span>田(5画) + 中(4画) = 9画</span>
                    <span>太(4画) + 郎(9画) = 13画</span>
                  </div>
                </div>
                <div class="section">
                  <h3>運勢判定</h3>
                  <div class="fortune-summary">
                    <div class="fortune-item">
                      <span class="fortune-label">総合運：</span>
                      <span class="fortune-value">吉</span>
                    </div>
                    <div class="fortune-item">
                      <span class="fortune-label">性格：</span>
                      <span class="fortune-value">誠実で努力家</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="template-footer">
              <div class="footer-info">
                <div class="footer-business">{{ businessName }}</div>
                <div class="footer-operator">鑑定士：{{ operatorName }}</div>
              </div>
              <div class="footer-disclaimer">
                ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
              </div>
            </div>
          </template>

          <!-- パターンB: エレガント&クラシック -->
          <template v-if="selectedPattern === 'elegant'">
            <div class="template-header elegant-classic">
              <div class="ornamental-border"></div>
              <div class="header-content">
                <div class="logo-section elegant">
                  <div class="logo-frame">
                    <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="ロゴ" class="logo-image elegant" />
                    <div v-else class="logo-placeholder-content">ロゴ</div>
                  </div>
                </div>
                <div class="title-section elegant">
                  <div class="title-ornament top"></div>
                  <h1 class="diagnosis-title elegant">九星気学・姓名判断 総合鑑定書</h1>
                  <div class="title-ornament bottom"></div>
                </div>
                <div class="business-section elegant">
                  <div class="business-card elegant">
                    <div class="business-name elegant">占いサロン 星花</div>
                    <div class="operator-line"></div>
                    <div class="operator-name elegant">鑑定士：星野 花子</div>
                  </div>
                </div>
              </div>
              <div class="date-section elegant">
                <div class="date-frame">
                  鑑定実施日：2025年1月15日
                </div>
              </div>
            </div>

            <div class="card elegant">
              <div class="card-header elegant">
                <div class="header-ornament"></div>
                <h2>依頼者情報</h2>
                <div class="header-ornament"></div>
              </div>
              <div class="card-body elegant">
                <div class="elegant-table">
                  <div class="table-row">
                    <div class="table-label">お名前</div>
                    <div class="table-value">田中 太郎</div>
                  </div>
                  <div class="table-row">
                    <div class="table-label">生年月日</div>
                    <div class="table-value">昭和60年3月15日（39歳）</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="template-footer elegant-classic">
              <div class="footer-ornament"></div>
              <div class="footer-content elegant">
                <div class="footer-business elegant">占いサロン 星花</div>
                <div class="footer-operator elegant">鑑定士：星野 花子</div>
                <div class="footer-disclaimer elegant">
                  ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
                </div>
              </div>
            </div>
          </template>

          <!-- パターンC: プロフェッショナル&ビジネス -->
          <template v-if="selectedPattern === 'professional'">
            <div class="template-header professional-business">
              <div class="header-grid">
                <div class="company-section">
                  <div class="logo-area">
                    <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="ロゴ" class="logo-image professional" />
                    <div v-else class="logo-placeholder-content">ロゴ</div>
                  </div>
                  <div class="company-info">
                    <div class="company-name">占いサロン 星花</div>
                    <div class="operator-info">鑑定士：星野 花子</div>
                  </div>
                </div>
                <div class="document-info">
                  <h1 class="document-title">九星気学・姓名判断 総合鑑定書</h1>
                  <div class="document-date">鑑定実施日：2025年1月15日</div>
                  <div class="document-id">鑑定書No. 2025-0115-001</div>
                </div>
              </div>
            </div>

            <div class="professional-table">
              <table class="data-table">
                <thead>
                  <tr>
                    <th colspan="2">依頼者情報</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="label-cell">お名前</td>
                    <td class="value-cell">田中 太郎</td>
                  </tr>
                  <tr>
                    <td class="label-cell">生年月日</td>
                    <td class="value-cell">昭和60年3月15日（39歳）</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="template-footer professional-business">
              <div class="footer-table">
                <div class="footer-row">
                  <div class="footer-label">発行者</div>
                  <div class="footer-value">占いサロン 星花　鑑定士：星野 花子</div>
                </div>
                <div class="footer-disclaimer professional">
                  ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
                </div>
              </div>
            </div>
          </template>

          <!-- パターンC: エレガント&ヴィンテージ -->
          <template v-if="selectedPattern === 'elegant2'">
            <div class="template-header elegant-vintage">
              <div class="vintage-frame"></div>
              <div class="header-content vintage">
                <div class="vintage-corner top-left"></div>
                <div class="vintage-corner top-right"></div>
                <div class="logo-section vintage">
                  <div class="vintage-logo">
                    <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="ロゴ" class="logo-image vintage" />
                    <div v-else class="logo-placeholder-content">LOGO</div>
                  </div>
                </div>
                <div class="title-section vintage">
                  <h1 class="diagnosis-title vintage">九星気学・姓名判断<br><span class="subtitle-vintage">総合鑑定書</span></h1>
                </div>
                <div class="business-section vintage">
                  <div class="vintage-divider"></div>
                  <div class="business-name vintage">占いサロン 星花</div>
                  <div class="operator-name vintage">鑑定士：星野 花子</div>
                  <div class="vintage-divider"></div>
                </div>
                <div class="date-section vintage">
                  <div class="date-vintage">鑑定実施日：2025年1月15日</div>
                </div>
                <div class="vintage-corner bottom-left"></div>
                <div class="vintage-corner bottom-right"></div>
              </div>
            </div>

            <div class="card vintage">
              <div class="card-header vintage">
                <div class="vintage-accent"></div>
                <h2>依頼者情報</h2>
                <div class="vintage-accent"></div>
              </div>
              <div class="card-body vintage">
                <div class="vintage-info-grid">
                  <div class="vintage-row">
                    <div class="vintage-label">お名前</div>
                    <div class="vintage-dots"></div>
                    <div class="vintage-value">田中 太郎</div>
                  </div>
                  <div class="vintage-row">
                    <div class="vintage-label">生年月日</div>
                    <div class="vintage-dots"></div>
                    <div class="vintage-value">昭和60年3月15日（39歳）</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="template-footer elegant-vintage">
              <div class="vintage-footer-pattern"></div>
              <div class="footer-content vintage">
                <div class="footer-business vintage">占いサロン 星花</div>
                <div class="footer-operator vintage">鑑定士：星野 花子</div>
                <div class="footer-disclaimer vintage">
                  ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
                </div>
              </div>
            </div>
          </template>

          <!-- パターンE: プロフェッショナル&エグゼクティブ -->
          <template v-if="selectedPattern === 'professional3'">
            <div class="template-header professional-executive">
              <div class="executive-frame">
                <div class="executive-border"></div>
                <div class="header-content executive">
                  <div class="executive-brand">
                    <div class="brand-logo">
                      <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="ロゴ" class="logo-image executive" />
                      <div v-else class="logo-placeholder-content">LOGO</div>
                    </div>
                    <div class="brand-line"></div>
                    <div class="brand-text">
                      <div class="company-name executive">占いサロン 星花</div>
                      <div class="company-sub">エグゼクティブ鑑定</div>
                    </div>
                  </div>
                  <div class="executive-title-area">
                    <div class="title-frame">
                      <h1 class="document-title executive">九星気学・姓名判断<br>総合鑑定書</h1>
                      <div class="title-line"></div>
                      <div class="subtitle executive">総合分析レポート</div>
                    </div>
                  </div>
                  <div class="executive-meta">
                    <div class="meta-grid">
                      <div class="meta-item">
                        <div class="meta-label">CONSULTANT</div>
                        <div class="meta-value">星野 花子</div>
                      </div>
                      <div class="meta-item">
                        <div class="meta-label">DATE</div>
                        <div class="meta-value">2025.01.15</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="executive-section">
              <div class="section-header executive">
                <div class="section-number">01</div>
                <div class="section-title executive">依頼者情報</div>
                <div class="section-line"></div>
              </div>
              <div class="executive-data">
                <div class="data-row executive">
                  <div class="data-label">氏名</div>
                  <div class="data-separator">—</div>
                  <div class="data-value">田中 太郎</div>
                </div>
                <div class="data-row executive">
                  <div class="data-label">生年月日</div>
                  <div class="data-separator">—</div>
                  <div class="data-value">昭和60年3月15日（39歳）</div>
                </div>
              </div>
            </div>

            <div class="template-footer professional-executive">
              <div class="executive-footer">
                <div class="footer-brand">
                  <div class="footer-logo">占いサロン 星花</div>
                  <div class="footer-consultant">鑑定士：星野 花子</div>
                </div>
                <div class="footer-legal">
                  <div class="legal-text">
                    ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
                  </div>
                  <div class="confidential">機密文書</div>
                </div>
              </div>
            </div>
          </template>

          <!-- パターンH: シンプルミニマル -->
          <template v-if="selectedPattern === 'minimal'">
            <div class="template-header simple-minimal">
              <div class="minimal-header">
                <div class="minimal-logo">
                  <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="ロゴ" class="logo-image minimal" />
                  <div v-else class="logo-placeholder-content">LOGO</div>
                </div>
                <div class="minimal-title">九星気学・姓名判断 総合鑑定書</div>
                <div class="minimal-date">2025.01.15</div>
              </div>
            </div>

            <div class="minimal-content">
              <div class="minimal-section">
                <h3 class="minimal-heading">依頼者情報</h3>
                <div class="minimal-list">
                  <div class="minimal-row">
                    <span class="minimal-label">お名前</span>
                    <span class="minimal-value">田中 太郎</span>
                  </div>
                  <div class="minimal-row">
                    <span class="minimal-label">生年月日</span>
                    <span class="minimal-value">昭和60年3月15日（39歳）</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="template-footer simple-minimal">
              <div class="minimal-footer">
                <div class="minimal-business">占いサロン 星花 | 鑑定士：星野 花子</div>
                <div class="minimal-disclaimer">
                  ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
                </div>
              </div>
            </div>
          </template>

        </div>
      </div>

      <!-- 読み込み中表示 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">設定を読み込み中...</div>
      </div>

      <!-- 設定パネル -->
      <div v-else class="settings-panel">
        <h3>カスタマイズ設定</h3>

        <!-- 基本情報設定 -->
        <div class="setting-section">
          <h4>基本情報</h4>
          <div class="setting-row">
            <label for="business_name">事業者名:</label>
            <input
              id="business_name"
              v-model="businessName"
              type="text"
              placeholder="占いサロン 星花"
              @input="updatePreview"
            />
          </div>
          <div class="setting-row">
            <label for="operator_name">鑑定士名:</label>
            <input
              id="operator_name"
              v-model="operatorName"
              type="text"
              placeholder="星野 花子"
              @input="updatePreview"
            />
          </div>
        </div>

        <!-- ロゴ設定 -->
        <div class="setting-section">
          <h4>ロゴ設定</h4>
          <div class="setting-row">
            <label for="logo_upload">ロゴファイル:</label>
            <input
              id="logo_upload"
              type="file"
              accept="image/*"
              @change="handleLogoUpload"
              class="logo-upload-input"
            />
          </div>
          <div v-if="logoPreviewUrl" class="logo-preview">
            <img :src="logoPreviewUrl" alt="ロゴプレビュー" class="logo-preview-image" />
            <button @click="removeLogo" class="remove-logo-btn">削除</button>
          </div>
        </div>

        <!-- テーマカラー選択 -->
        <div class="setting-section">
          <h4>テーマカラー</h4>
          <div class="theme-colors">
            <button
              v-for="(theme, key) in themes"
              :key="key"
              class="theme-btn"
              :class="{ active: selectedTheme === key }"
              :style="{ backgroundColor: theme.primary }"
              @click="selectTheme(key)"
            >
              {{ theme.name }}
            </button>
          </div>
        </div>

        <!-- フォント設定 -->
        <div class="setting-section">
          <h4>フォント設定</h4>
          <div class="setting-row">
            <label for="font_family">フォントファミリー:</label>
            <select id="font_family" v-model="fontFamily" @change="updatePreview">
              <option value="default">デフォルト</option>
              <option value="noto-serif">Noto Serif JP</option>
              <option value="noto-sans">Noto Sans JP</option>
              <option value="mincho">明朝体</option>
              <option value="gothic">ゴシック体</option>
            </select>
          </div>
          <div class="setting-row">
            <label for="font_size">文字サイズ:</label>
            <select id="font_size" v-model="fontSize" @change="updatePreview">
              <option value="small">小さい</option>
              <option value="medium">標準</option>
              <option value="large">大きい</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'

const router = useRouter()
const selectedPattern = ref('clean')
const selectedTheme = ref('default')

// 設定用の reactive variables
const businessName = ref('占いサロン 星花')
const operatorName = ref('星野 花子')
const fontFamily = ref('default')
const fontSize = ref('medium')
const logoFile = ref<File | null>(null)
const logoPreviewUrl = ref<string>('')

// 設定読み込み状態
const loading = ref(true)

const designPatterns = ref({
  clean: { name: 'A. クリーン&コンパクト' },
  elegant: { name: 'B. エレガント&クラシック' },
  elegant2: { name: 'C. エレガント&ヴィンテージ' },
  professional: { name: 'E. プロフェッショナル&ビジネス' },
  professional3: { name: 'G. プロフェッショナル&エグゼクティブ' },
  minimal: { name: 'H. シンプルミニマル' }
})

const themes = ref({
  default: { name: 'デフォルト', primary: '#3498db', accent: '#2980b9' },
  elegant: { name: 'エレガント', primary: '#8e44ad', accent: '#9b59b6' },
  warm: { name: 'ウォーム', primary: '#e67e22', accent: '#d35400' },
  natural: { name: 'ナチュラル', primary: '#27ae60', accent: '#2ecc71' },
  professional: { name: 'プロフェッショナル', primary: '#34495e', accent: '#2c3e50' }
})

const dynamicStyles = computed(() => {
  const theme = themes.value[selectedTheme.value]
  const fontSizeMap = {
    small: '0.9',
    medium: '1.0',
    large: '1.2'
  }
  const fontScale = fontSizeMap[fontSize.value]

  return {
    '--primary-color': theme.primary,
    '--accent-color': theme.accent,
    '--font-scale': fontScale,
    'font-family': fontFamily.value === 'default' ? '' :
                   fontFamily.value === 'noto-serif' ? '"Noto Serif JP", serif' :
                   fontFamily.value === 'noto-sans' ? '"Noto Sans JP", sans-serif' :
                   fontFamily.value === 'mincho' ? '"Yu Mincho", serif' :
                   fontFamily.value === 'gothic' ? '"Yu Gothic", sans-serif' : ''
  }
})

const selectPattern = (pattern: string) => {
  selectedPattern.value = pattern
}

const selectTheme = (theme: string) => {
  selectedTheme.value = theme
}

// プレビューを更新（将来的にAPI呼び出し等に使用）
const updatePreview = () => {
  // プレビューの更新処理（リアクティブなので自動更新される）
}

// ロゴファイルアップロード処理
const handleLogoUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    // ファイルサイズチェック（5MB制限）
    if (file.size > 5 * 1024 * 1024) {
      alert('ファイルサイズは5MB以下にしてください')
      return
    }

    // 画像ファイルかチェック
    if (!file.type.startsWith('image/')) {
      alert('画像ファイルを選択してください')
      return
    }

    logoFile.value = file

    // プレビュー用のURLを作成
    const reader = new FileReader()
    reader.onload = (e) => {
      logoPreviewUrl.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

// ロゴ削除
const removeLogo = async () => {
  try {
    console.log('ロゴを削除中...')
    await apiClient.deleteLogo()

    // フロントエンドの状態をクリア
    logoFile.value = null
    logoPreviewUrl.value = ''

    // input要素もクリア
    const logoInput = document.getElementById('logo_upload') as HTMLInputElement
    if (logoInput) {
      logoInput.value = ''
    }

    console.log('ロゴ削除完了')
  } catch (error) {
    console.error('ロゴ削除エラー:', error)
    alert('ロゴの削除に失敗しました')
  }
}

// 設定を読み込む
const loadSettings = async () => {
  try {
    loading.value = true
    const settings = await apiClient.getTemplateSettings()

    // デバッグ情報を表示
    console.log('読み込んだ設定データ:', settings)

    // 保存済み設定があれば反映
    if (settings) {
      selectedPattern.value = settings.design_pattern || 'clean'
      selectedTheme.value = settings.color_theme || 'default'
      businessName.value = settings.business_name || '占いサロン 星花'
      operatorName.value = settings.operator_name || '星野 花子'
      fontFamily.value = settings.font_family || 'default'
      fontSize.value = settings.font_size || 'medium'

      // ロゴURLがあれば表示
      if (settings.logo_url) {
        // 相対URLの場合は絶対URLに変換
        const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8502'
        logoPreviewUrl.value = settings.logo_url.startsWith('http')
          ? settings.logo_url
          : `${baseURL}/${settings.logo_url.startsWith('/') ? settings.logo_url.slice(1) : settings.logo_url}`
      }

      console.log('設定反映後の値:', {
        design_pattern: selectedPattern.value,
        color_theme: selectedTheme.value,
        business_name: businessName.value,
        operator_name: operatorName.value,
        font_family: fontFamily.value,
        font_size: fontSize.value,
        logo_url: logoPreviewUrl.value
      })
    }
  } catch (error) {
    console.error('設定読み込みエラー:', error)
    // エラーの場合はデフォルト値のまま
  } finally {
    loading.value = false
  }
}

// 選択したパターンをテンプレート設定に保存してページ移動
const selectThisPattern = async () => {
  try {
    // 現在のテンプレート設定を取得
    const currentSettings = await apiClient.getTemplateSettings()

    // ロゴファイルをアップロード（ある場合）
    let logoUrl = currentSettings.logo_url
    if (logoFile.value) {
      try {
        console.log('ロゴファイルをアップロード中...', logoFile.value.name)
        const logoResponse = await apiClient.uploadLogo(logoFile.value)
        logoUrl = logoResponse.logo_url
        console.log('ロゴアップロード成功:', logoUrl)
      } catch (logoError) {
        console.error('ロゴアップロードエラー:', logoError)
        alert('ロゴのアップロードに失敗しました。設定は他の項目のみ保存されます。')
      }
    }

    // 選択したすべての設定を反映
    const updateData = {
      ...currentSettings,
      design_pattern: selectedPattern.value,
      color_theme: selectedTheme.value,
      business_name: businessName.value,
      operator_name: operatorName.value,
      font_family: fontFamily.value,
      font_size: fontSize.value,
      logo_url: logoUrl
    }

    // デバッグ情報を表示
    console.log('保存する設定データ:', updateData)

    // テンプレート設定を更新
    await apiClient.updateTemplateSettings(updateData)

    // 保存完了メッセージ
    alert('設定を保存しました！\n\n鑑定書作成で新しい設定が反映されます。')
  } catch (error) {
    console.error('パターン選択エラー:', error)
    alert('設定の保存に失敗しました。もう一度お試しください。')
  }
}

// ページロード時に設定を読み込み
onMounted(() => {
  loadSettings()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.design-patterns {
  @include page-container;
}

// 読み込み中表示
.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;

  .loading-spinner {
    background: white;
    padding: 24px 32px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    color: var(--text-secondary);
    font-size: 1rem;
  }
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

// パターン選択ボタン
.pattern-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  flex-wrap: wrap;

  .pattern-btn {
    padding: 12px 20px;
    border: 2px solid #e0e0e0;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 500;

    &:hover {
      border-color: var(--primary-main);
      background: #f8f9fa;
    }

    &.active {
      border-color: var(--primary-main);
      background: var(--primary-main);
      color: white;
    }
  }
}

// プレビューエリア
.pattern-preview {
  background: #f5f5f5;
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 32px;
  min-height: 600px;

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    h3 {
      margin: 0;
      color: var(--text-primary);
      font-size: 1.2rem;
      font-weight: 600;
    }

    .select-pattern-btn {
      background: linear-gradient(135deg, var(--primary-main), var(--primary-dark));
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}

.diagnosis-document {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;

  // フォントサイズスケーリング
  font-size: calc(1rem * var(--font-scale, 1));

  .diagnosis-title {
    font-size: calc(1.4rem * var(--font-scale, 1));
  }

  .business-name {
    font-size: calc(1.1rem * var(--font-scale, 1));
  }

  .card-header h2 {
    font-size: calc(1.1rem * var(--font-scale, 1));
  }

  .section h3 {
    font-size: calc(1rem * var(--font-scale, 1));
  }

  label, .info-item label {
    font-size: calc(0.9rem * var(--font-scale, 1));
  }

  span, .info-item span {
    font-size: calc(1rem * var(--font-scale, 1));
  }
}

// 設定パネル
.settings-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;

  h3 {
    margin: 0 0 24px 0;
    color: var(--text-primary);
    font-size: 1.4rem;
    font-weight: 600;
  }

  .setting-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    h4 {
      margin: 0 0 16px 0;
      color: var(--text-secondary);
      font-size: 1.1rem;
      font-weight: 600;
      border-bottom: 1px solid #e0e0e0;
      padding-bottom: 8px;
    }
  }

  .setting-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      font-weight: 500;
      color: var(--text-primary);
      min-width: 120px;
      font-size: 0.9rem;
    }

    input, select {
      flex: 1;
      max-width: 300px;
      padding: 8px 12px;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      font-size: 0.9rem;
      transition: border-color 0.2s ease;

      &:focus {
        outline: none;
        border-color: var(--primary-main);
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
      }
    }

    .logo-upload-input {
      max-width: 250px;
    }
  }

  .logo-preview {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;

    .logo-preview-image {
      width: 60px;
      height: 30px;
      object-fit: contain;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      background: white;
    }

    .remove-logo-btn {
      padding: 4px 8px;
      background: #dc3545;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: background-color 0.2s ease;

      &:hover {
        background: #c82333;
      }
    }
  }

  .theme-colors {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .theme-btn {
    padding: 8px 16px;
    border: 2px solid white;
    border-radius: 20px;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 12px;
    font-weight: 600;

    &:hover {
      transform: scale(1.05);
    }

    &.active {
      border-color: #333;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
  }
}

// パターンA: クリーン&コンパクト（実際のPreviewView.vueのスタイル）
.template-header.modern-minimal {
  background: white;
  border: 2px solid var(--primary-color, #3498db);
  border-radius: 8px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .header-background {
    display: none;
  }

  .header-content {
    padding: 20px 24px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 20px;
    align-items: center;
  }

  .logo-section {
    .logo-placeholder {
      width: 120px;
      height: 50px;
      background: #f5f5f5;
      border: 2px dashed #ccc;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;

      .logo-placeholder-content {
        color: #999;
        font-size: 10px;
        text-align: center;
        line-height: 1.2;
      }

      .logo-image {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 6px;
      }
    }
  }

  .title-section {
    .title-ornament {
      display: none;
    }

    .diagnosis-title {
      font-size: 1.4rem;
      font-weight: 600;
      margin: 0;
      color: var(--primary-color, #3498db);
      line-height: 1.3;
    }
  }

  .business-section {
    text-align: right;

    .business-card {
      background: none;
      border: none;
      padding: 0;

      .business-name {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 4px 0;
        color: var(--primary-color, #3498db);
      }

      .operator-name {
        margin: 0;
        color: #666;
        font-size: 0.9rem;

        .operator-label {
          margin-right: 4px;
        }
      }
    }
  }
}

.client-info-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background: white;
  overflow: hidden;
  margin-bottom: 16px;

  .card-header {
    background: var(--primary-color, #3498db);
    color: white;
    padding: 12px 20px;
    border-bottom: none;

    h2 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
    }
  }

  .card-body {
    padding: 20px;

    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;

      .info-item {
        display: flex;
        align-items: baseline;
        gap: 12px;

        label {
          font-weight: 600;
          color: #555;
          min-width: 80px;
          font-size: 0.9rem;
        }

        span {
          color: #333;
          font-size: 1rem;
        }
      }
    }

    .section {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      h3 {
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary-color, #3498db);
        margin: 0 0 12px 0;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 4px;
      }
    }

    .nine-star-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 12px;

      .star-item {
        display: flex;
        align-items: baseline;
        gap: 8px;

        label {
          font-weight: 600;
          color: #555;
          font-size: 0.85rem;
          min-width: 60px;
        }

        .star-value {
          color: var(--primary-color, #3498db);
          font-weight: 600;
          font-size: 0.9rem;
        }
      }
    }

    .direction-info {
      display: flex;
      align-items: center;
      gap: 8px;

      .direction-label {
        font-weight: 600;
        color: #555;
        font-size: 0.9rem;
      }

      .direction-value {
        color: var(--primary-color, #3498db);
        font-weight: 600;
        font-size: 1rem;
      }
    }

    .character-info {
      display: flex;
      flex-direction: column;
      gap: 8px;

      span {
        color: #333;
        font-size: 0.9rem;
        padding: 4px 8px;
        background: #f8f9fa;
        border-radius: 4px;
      }
    }

    .fortune-summary {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .fortune-item {
        display: flex;
        align-items: center;
        gap: 8px;

        .fortune-label {
          font-weight: 600;
          color: #555;
          font-size: 0.9rem;
          min-width: 70px;
        }

        .fortune-value {
          color: var(--primary-color, #3498db);
          font-weight: 600;
          font-size: 0.9rem;
        }
      }
    }
  }
}

.template-footer {
  margin-top: 32px;
  border-top: 2px solid var(--primary-color, #3498db);
  background: #f8f9fa;
  padding: 20px 24px;
  text-align: center;

  .footer-info {
    margin-bottom: 16px;

    .footer-business {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--primary-color, #3498db);
      margin-bottom: 4px;
    }

    .footer-operator {
      color: #666;
      font-size: 0.9rem;
    }
  }

  .footer-disclaimer {
    color: #888;
    font-size: 0.8rem;
    line-height: 1.4;
  }
}

// パターンB: エレガント&クラシック
.template-header.elegant-classic {
  background: linear-gradient(135deg, #f8f6f0, #fff);
  border: 3px solid var(--primary-color, #8e44ad);
  position: relative;

  .ornamental-border {
    position: absolute;
    top: 8px;
    left: 8px;
    right: 8px;
    bottom: 8px;
    border: 1px solid var(--accent-color, #9b59b6);
    border-radius: 4px;
  }

  .header-content {
    padding: 40px;
    text-align: center;
    position: relative;
    z-index: 2;
  }

  .logo-frame {
    width: 80px;
    height: 80px;
    border: 2px solid var(--primary-color);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px;
    background: white;
    font-size: 12px;
    color: var(--primary-color);

    .logo-image.elegant {
      width: 70px;
      height: 70px;
      object-fit: contain;
      border-radius: 50%;
    }
  }

  .title-ornament {
    width: 120px;
    height: 2px;
    background: var(--accent-color);
    margin: 0 auto;
    position: relative;

    &.top { margin-bottom: 16px; }
    &.bottom { margin-top: 16px; }

    &::before, &::after {
      content: '';
      position: absolute;
      width: 8px;
      height: 8px;
      background: var(--accent-color);
      border-radius: 50%;
      top: -3px;
    }

    &::before { left: -12px; }
    &::after { right: -12px; }
  }

  .diagnosis-title.elegant {
    font-family: serif;
    font-size: 2rem;
    color: var(--primary-color);
    font-weight: 400;
    margin: 0;
  }

  .business-card.elegant {
    margin-top: 24px;
    padding: 20px;
    border: 1px solid var(--accent-color);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.8);
  }

  .business-name.elegant {
    font-size: 1.2rem;
    color: var(--primary-color);
    font-weight: 600;
    margin-bottom: 8px;
  }

  .operator-line {
    width: 60px;
    height: 1px;
    background: var(--accent-color);
    margin: 8px auto;
  }

  .operator-name.elegant {
    color: #666;
    font-size: 0.9rem;
  }

  .date-section.elegant {
    background: var(--primary-color);
    color: white;
    padding: 12px;
    text-align: center;
  }

  .date-frame {
    font-size: 0.9rem;
    font-weight: 500;
  }
}

.card.elegant {
  border: 1px solid var(--primary-color);
  border-radius: 0;
  margin: 24px 0;

  .card-header.elegant {
    background: var(--primary-color);
    color: white;
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;

    .header-ornament {
      width: 20px;
      height: 20px;
      border: 1px solid white;
      border-radius: 50%;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 8px;
        height: 8px;
        background: white;
        border-radius: 50%;
      }
    }

    h2 {
      font-family: serif;
      margin: 0;
      font-weight: 400;
    }
  }

  .card-body.elegant {
    padding: 24px;
  }
}

.elegant-table {
  .table-row {
    display: flex;
    padding: 12px 0;
    border-bottom: 1px dotted #ccc;

    &:last-child {
      border-bottom: none;
    }
  }

  .table-label {
    width: 120px;
    font-weight: 600;
    color: var(--primary-color);
  }

  .table-value {
    flex: 1;
    color: #333;
  }
}

.template-footer.elegant-classic {
  background: var(--primary-color);
  color: white;
  text-align: center;
  padding: 24px;
  position: relative;

  .footer-ornament {
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 2px;
    background: white;

    &::before, &::after {
      content: '';
      position: absolute;
      width: 6px;
      height: 6px;
      background: white;
      border-radius: 50%;
      top: -2px;
    }

    &::before { left: -8px; }
    &::after { right: -8px; }
  }

  .footer-content.elegant {
    padding-top: 16px;
  }

  .footer-business.elegant {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .footer-operator.elegant {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-bottom: 16px;
  }

  .footer-disclaimer.elegant {
    font-size: 0.75rem;
    opacity: 0.8;
    line-height: 1.4;
  }
}

// パターンC: プロフェッショナル&ビジネス
.template-header.professional-business {
  background: white;
  border-bottom: 3px solid var(--primary-color, #34495e);
  padding: 24px;

  .header-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 32px;
    align-items: start;
  }

  .company-section {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .logo-area {
    width: 60px;
    height: 60px;
    border: 2px solid var(--primary-color);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    color: var(--primary-color);
    font-weight: 600;

    .logo-image.professional {
      width: 55px;
      height: 55px;
      object-fit: contain;
    }
  }

  .company-info {
    .company-name {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--primary-color);
      margin-bottom: 4px;
    }

    .operator-info {
      font-size: 0.85rem;
      color: #666;
    }
  }

  .document-info {
    text-align: right;

    .document-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: var(--primary-color);
      margin: 0 0 8px 0;
    }

    .document-date {
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 4px;
    }

    .document-id {
      font-size: 0.8rem;
      color: #999;
      font-family: monospace;
    }
  }
}

.professional-table {
  margin: 24px 0;

  .data-table {
    width: 100%;
    border-collapse: collapse;
    border: 2px solid var(--primary-color);

    th {
      background: var(--primary-color);
      color: white;
      padding: 12px;
      font-weight: 600;
      text-align: center;
    }

    td {
      padding: 12px;
      border-bottom: 1px solid #e0e0e0;

      &.label-cell {
        background: #f8f9fa;
        font-weight: 600;
        color: var(--primary-color);
        width: 150px;
      }

      &.value-cell {
        color: #333;
      }
    }

    tr:last-child td {
      border-bottom: none;
    }
  }
}

.template-footer.professional-business {
  background: #f8f9fa;
  border-top: 2px solid var(--primary-color);
  padding: 20px;

  .footer-table {
    .footer-row {
      display: flex;
      margin-bottom: 12px;
    }

    .footer-label {
      width: 80px;
      font-weight: 600;
      color: var(--primary-color);
    }

    .footer-value {
      flex: 1;
      color: #333;
    }
  }

  .footer-disclaimer.professional {
    font-size: 0.8rem;
    color: #666;
    text-align: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #e0e0e0;
  }
}

// パターンD: モダングラデーション
.template-header.modern-gradient {
  background: linear-gradient(135deg, var(--primary-color, #3498db), var(--accent-color, #2980b9));
  color: white;
  position: relative;
  overflow: hidden;

  .gradient-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  }

  .header-content.modern {
    position: relative;
    z-index: 2;
    padding: 32px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 24px;
    align-items: center;
  }

  .logo-container.modern {
    .logo-circle {
      width: 60px;
      height: 60px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.3);
    }
  }

  .title-container.modern {
    text-align: center;

    .diagnosis-title.modern {
      font-size: 1.8rem;
      font-weight: 300;
      margin: 0;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      line-height: 1.2;
    }
  }

  .info-container.modern {
    text-align: right;

    .business-name.modern {
      font-size: 1rem;
      font-weight: 500;
      margin-bottom: 4px;
    }

    .operator-name.modern {
      font-size: 0.85rem;
      opacity: 0.9;
      margin-bottom: 8px;
    }

    .date-modern {
      font-size: 0.8rem;
      opacity: 0.8;
    }
  }
}

.modern-card {
  margin: 24px 0;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .card-title.modern {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    color: white;
    padding: 16px;
    font-weight: 600;
  }

  .modern-grid {
    padding: 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  .modern-item {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid var(--accent-color);

    .item-label {
      font-size: 0.8rem;
      color: #666;
      margin-bottom: 4px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .item-value {
      color: #333;
      font-weight: 500;
    }
  }
}

.template-footer.modern-gradient {
  background: var(--primary-color);
  color: white;
  position: relative;
  overflow: hidden;

  .footer-gradient {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  }

  .footer-content.modern {
    position: relative;
    z-index: 2;
    padding: 20px;
    text-align: center;

    .footer-text {
      font-weight: 500;
      margin-bottom: 12px;
    }

    .footer-disclaimer.modern {
      font-size: 0.8rem;
      opacity: 0.8;
    }
  }
}

// パターンC: エレガント&ヴィンテージ
.template-header.elegant-vintage {
  background: linear-gradient(135deg, #f9f7f3, #f0ede6);
  border: 2px solid var(--primary-color, #8b4513);
  position: relative;
  padding: 40px;

  .vintage-frame {
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    bottom: 10px;
    border: 1px solid rgba(139, 69, 19, 0.3);
  }

  .header-content.vintage {
    position: relative;
    z-index: 2;
    text-align: center;
  }

  .vintage-corner {
    position: absolute;
    width: 20px;
    height: 20px;
    border: 2px solid var(--primary-color);

    &.top-left {
      top: 20px;
      left: 20px;
      border-right: none;
      border-bottom: none;
    }

    &.top-right {
      top: 20px;
      right: 20px;
      border-left: none;
      border-bottom: none;
    }

    &.bottom-left {
      bottom: 20px;
      left: 20px;
      border-right: none;
      border-top: none;
    }

    &.bottom-right {
      bottom: 20px;
      right: 20px;
      border-left: none;
      border-top: none;
    }
  }

  .vintage-logo {
    font-family: serif;
    font-size: 14px;
    color: var(--primary-color);
    margin-bottom: 16px;
    letter-spacing: 2px;

    .logo-image.vintage {
      width: 60px;
      height: 60px;
      object-fit: contain;
    }
  }

  .diagnosis-title.vintage {
    font-family: serif;
    font-size: 1.8rem;
    color: var(--primary-color);
    margin: 16px 0;

    .subtitle-vintage {
      font-size: 1.2rem;
      display: block;
      margin-top: 8px;
    }
  }

  .vintage-divider {
    width: 60px;
    height: 2px;
    background: var(--primary-color);
    margin: 8px auto;
  }

  .business-name.vintage {
    font-family: serif;
    font-size: 1.1rem;
    color: var(--primary-color);
    margin: 8px 0;
  }

  .operator-name.vintage {
    font-family: serif;
    font-size: 0.9rem;
    color: #666;
    margin: 8px 0;
  }

  .date-vintage {
    font-family: serif;
    font-size: 0.85rem;
    color: #666;
    margin-top: 16px;
  }
}

.card.vintage {
  background: #faf9f6;
  border: 1px solid #ddd;
  margin: 24px 0;

  .card-header.vintage {
    background: var(--primary-color);
    color: #f9f7f3;
    text-align: center;
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;

    .vintage-accent {
      width: 30px;
      height: 2px;
      background: #f9f7f3;
    }

    h2 {
      font-family: serif;
      margin: 0;
      font-size: 1.2rem;
    }
  }

  .card-body.vintage {
    padding: 24px;

    .vintage-info-grid {
      .vintage-row {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        font-family: serif;

        .vintage-label {
          flex: 0 0 120px;
          color: var(--primary-color);
          font-weight: 600;
        }

        .vintage-dots {
          flex: 1;
          height: 1px;
          background: repeating-linear-gradient(
            to right,
            transparent,
            transparent 2px,
            #ccc 2px,
            #ccc 4px
          );
          margin: 0 12px;
        }

        .vintage-value {
          color: #333;
        }
      }
    }
  }
}

.template-footer.elegant-vintage {
  background: var(--primary-color);
  color: #f9f7f3;
  padding: 24px;
  position: relative;

  .vintage-footer-pattern {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: repeating-linear-gradient(
      to right,
      #f9f7f3,
      #f9f7f3 8px,
      transparent 8px,
      transparent 16px
    );
  }

  .footer-content.vintage {
    text-align: center;
    font-family: serif;

    .footer-business.vintage,
    .footer-operator.vintage {
      margin-bottom: 8px;
    }

    .footer-disclaimer.vintage {
      font-size: 0.8rem;
      opacity: 0.9;
      margin-top: 12px;
    }
  }
}

// パターンD: エレガント&ロイヤル
.template-header.elegant-royal {
  background: linear-gradient(135deg, #f8f6f0, #ffffff);
  border: 3px solid var(--primary-color, #4a4a8a);
  position: relative;
  padding: 48px 32px;
  text-align: center;

  .royal-crown {
    position: absolute;
    top: -15px;
    left: 50%;
    transform: translateX(-50%);
    width: 30px;
    height: 20px;
    background: var(--primary-color);
    clip-path: polygon(50% 0%, 0% 100%, 20% 100%, 35% 20%, 50% 40%, 65% 20%, 80% 100%, 100% 100%);
  }

  .royal-crest {
    margin-bottom: 24px;

    .crest-inner {
      font-size: 2rem;
      color: var(--primary-color);
    }
  }

  .royal-line {
    width: 80px;
    height: 2px;
    background: var(--primary-color);
    margin: 16px auto;

    &.top {
      margin-bottom: 16px;
    }

    &.bottom {
      margin-top: 16px;
    }
  }

  .diagnosis-title.royal {
    font-family: serif;
    font-size: 1.6rem;
    color: var(--primary-color);
    margin: 0;
    font-weight: 700;
    letter-spacing: 1px;
  }

  .royal-shield {
    background: rgba(74, 74, 138, 0.1);
    border: 2px solid var(--primary-color);
    padding: 16px;
    margin: 24px auto;
    max-width: 280px;
    clip-path: polygon(0% 0%, 100% 0%, 100% 75%, 50% 100%, 0% 75%);
    padding-bottom: 24px;

    .business-name.royal {
      font-family: serif;
      font-size: 1.1rem;
      color: var(--primary-color);
      font-weight: 600;
      margin-bottom: 8px;
    }

    .royal-separator {
      width: 40px;
      height: 1px;
      background: var(--primary-color);
      margin: 8px auto;
    }

    .operator-name.royal {
      font-family: serif;
      font-size: 0.9rem;
      color: #666;
    }
  }

  .date-royal {
    font-family: serif;
    font-size: 0.85rem;
    color: #666;
    margin-top: 20px;
  }

  .royal-pattern {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image:
      radial-gradient(circle at 25% 25%, rgba(74, 74, 138, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 75% 75%, rgba(74, 74, 138, 0.05) 0%, transparent 50%);
    pointer-events: none;
  }
}

.card.royal {
  background: #fefdfb;
  border: 2px solid var(--primary-color);
  margin: 24px 0;

  .card-header.royal {
    background: var(--primary-color);
    color: white;
    text-align: center;
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;

    .royal-emblem {
      font-size: 1.2rem;
    }

    h2 {
      font-family: serif;
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
    }
  }

  .card-body.royal {
    padding: 24px;

    .royal-table {
      .royal-row {
        display: grid;
        grid-template-columns: 120px auto 1fr;
        gap: 12px;
        align-items: center;
        margin-bottom: 16px;
        font-family: serif;

        .royal-cell.label {
          color: var(--primary-color);
          font-weight: 600;
        }

        .royal-cell.separator {
          color: var(--primary-color);
          font-weight: bold;
        }

        .royal-cell.value {
          color: #333;
        }
      }
    }
  }
}

.template-footer.elegant-royal {
  background: var(--primary-color);
  color: white;
  padding: 24px;
  position: relative;

  .royal-footer-border {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: linear-gradient(
      to right,
      transparent,
      white,
      transparent
    );
  }

  .footer-content.royal {
    text-align: center;
    font-family: serif;

    .footer-brand {
      margin-bottom: 16px;

      .footer-logo {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 4px;
      }

      .footer-consultant {
        font-size: 0.9rem;
        opacity: 0.9;
      }
    }

    .footer-legal {
      .legal-text {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-bottom: 8px;
      }

      .confidential {
        font-size: 0.75rem;
        opacity: 0.7;
        letter-spacing: 1px;
      }
    }
  }
}

// パターンF: プロフェッショナル&コーポレート
.template-header.professional-corporate {
  background: #f8f9fa;
  border: none;
  border-bottom: 4px solid var(--primary-color, #2c3e50);

  .corporate-header {
    padding: 24px 32px;

    .header-top {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 24px;
      align-items: center;
      margin-bottom: 16px;

      .corporate-logo {
        .logo-square {
          width: 60px;
          height: 60px;
          background: var(--primary-color);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          font-weight: bold;
        }
      }

      .corporate-info {
        .corporate-name {
          font-size: 1.4rem;
          font-weight: 600;
          color: var(--primary-color);
          margin-bottom: 4px;
        }

        .corporate-tagline {
          font-size: 0.8rem;
          color: #666;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
      }

      .header-right {
        text-align: right;

        .document-ref {
          font-size: 0.8rem;
          color: #666;
          margin-bottom: 4px;
        }

        .issue-date {
          font-size: 0.8rem;
          color: #666;
        }
      }
    }

    .header-separator {
      width: 100%;
      height: 1px;
      background: #ddd;
      margin: 16px 0;
    }

    .document-title-section {
      text-align: center;

      .document-title.corporate {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--primary-color);
        margin: 0 0 8px 0;
      }

      .title-subtitle {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
    }
  }
}

.corporate-content {
  margin: 24px 0;
  background: white;
  border: 1px solid #e9ecef;

  .section-header {
    background: var(--primary-color);
    color: white;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 12px;

    .section-icon {
      font-size: 1.2rem;
    }

    .section-title {
      font-size: 1rem;
      font-weight: 600;
      margin: 0;
    }
  }

  .corporate-grid {
    padding: 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;

    .grid-item {
      .field-label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        font-weight: 500;
      }

      .field-value {
        font-size: 1rem;
        color: #333;
        font-weight: 500;
        padding: 8px 0;
        border-bottom: 2px solid var(--primary-color);
      }
    }
  }
}

.template-footer.professional-corporate {
  background: #f8f9fa;
  border-top: 1px solid #ddd;
  padding: 20px 24px;

  .footer-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    align-items: center;

    .footer-left {
      .footer-company {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 4px;
      }

      .footer-consultant {
        font-size: 0.9rem;
        color: #666;
      }
    }

    .footer-right {
      text-align: right;

      .footer-disclaimer.corporate {
        font-size: 0.75rem;
        color: #666;
        line-height: 1.4;
      }
    }
  }
}

// パターンG: プロフェッショナル&エグゼクティブ
.template-header.professional-executive {
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border: none;

  .executive-frame {
    border: 3px solid var(--primary-color, #2c3e50);
    position: relative;
    margin: 16px;

    .executive-border {
      position: absolute;
      top: 8px;
      left: 8px;
      right: 8px;
      bottom: 8px;
      border: 1px solid rgba(44, 62, 80, 0.3);
    }

    .header-content.executive {
      padding: 32px;
      position: relative;
      z-index: 2;

      .executive-brand {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 32px;

        .brand-logo {
          width: 80px;
          height: 80px;
          background: var(--primary-color);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: bold;

          .logo-image.executive {
            width: 75px;
            height: 75px;
            object-fit: contain;
          }
        }

        .brand-line {
          width: 2px;
          height: 60px;
          background: var(--primary-color);
        }

        .brand-text {
          .company-name.executive {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 4px;
          }

          .company-sub {
            font-size: 0.85rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
          }
        }
      }

      .executive-title-area {
        text-align: center;
        margin-bottom: 32px;

        .title-frame {
          .document-title.executive {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0 0 16px 0;
            letter-spacing: 1px;
          }

          .title-line {
            width: 120px;
            height: 3px;
            background: var(--primary-color);
            margin: 0 auto 16px auto;
          }

          .subtitle.executive {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1.5px;
          }
        }
      }

      .executive-meta {
        .meta-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          max-width: 400px;
          margin: 0 auto;

          .meta-item {
            text-align: center;

            .meta-label {
              font-size: 0.75rem;
              color: #666;
              text-transform: uppercase;
              letter-spacing: 1px;
              margin-bottom: 6px;
            }

            .meta-value {
              font-size: 1rem;
              color: var(--primary-color);
              font-weight: 600;
            }
          }
        }
      }
    }
  }
}

.executive-section {
  margin: 32px 0;
  background: white;
  border: 2px solid var(--primary-color);

  .section-header.executive {
    background: var(--primary-color);
    color: white;
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 16px;

    .section-number {
      font-size: 1.5rem;
      font-weight: 700;
      width: 40px;
      text-align: center;
    }

    .section-title.executive {
      font-size: 1.1rem;
      font-weight: 600;
      flex: 1;
    }

    .section-line {
      flex: 1;
      height: 2px;
      background: rgba(255, 255, 255, 0.3);
    }
  }

  .executive-data {
    padding: 32px;

    .data-row.executive {
      display: grid;
      grid-template-columns: 150px auto 1fr;
      gap: 16px;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 20px;
      border-bottom: 1px solid #eee;

      &:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
      }

      .data-label {
        font-size: 0.9rem;
        color: var(--primary-color);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .data-separator {
        color: var(--primary-color);
        font-weight: bold;
        font-size: 1.2rem;
      }

      .data-value {
        font-size: 1.1rem;
        color: #333;
        font-weight: 500;
      }
    }
  }
}

.template-footer.professional-executive {
  background: var(--primary-color);
  color: white;
  padding: 24px;

  .executive-footer {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    align-items: center;

    .footer-brand {
      .footer-logo {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 6px;
      }

      .footer-consultant {
        font-size: 0.9rem;
        opacity: 0.9;
      }
    }

    .footer-legal {
      text-align: right;

      .legal-text {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-bottom: 8px;
        line-height: 1.4;
      }

      .confidential {
        font-size: 0.75rem;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
    }
  }
}

// パターンH: シンプルミニマル
.template-header.simple-minimal {
  background: white;
  border: none;

  .minimal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0;
    border-bottom: 1px solid #e0e0e0;
  }

  .minimal-logo {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--primary-color, #333);
    letter-spacing: 2px;

    .logo-image.minimal {
      width: 50px;
      height: 50px;
      object-fit: contain;
    }
  }

  .minimal-title {
    font-size: 1.3rem;
    font-weight: 500;
    color: #333;
    text-align: center;
    flex: 1;
    margin: 0 20px;
  }

  .minimal-date {
    font-size: 0.9rem;
    color: #666;
    font-family: monospace;
  }
}

.minimal-content {
  padding: 32px 0;

  .minimal-section {
    margin-bottom: 32px;
  }

  .minimal-heading {
    font-size: 1rem;
    font-weight: 600;
    color: var(--primary-color, #333);
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--primary-color, #333);
  }

  .minimal-list {
    .minimal-row {
      display: flex;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }
    }

    .minimal-label {
      width: 120px;
      font-weight: 500;
      color: #666;
    }

    .minimal-value {
      flex: 1;
      color: #333;
    }
  }
}

.template-footer.simple-minimal {
  border-top: 1px solid #e0e0e0;
  padding: 20px 0;

  .minimal-footer {
    text-align: center;

    .minimal-business {
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 12px;
    }

    .minimal-disclaimer {
      font-size: 0.75rem;
      color: #999;
    }
  }
}

// レスポンシブ
@media (max-width: 768px) {
  .pattern-selector {
    flex-direction: column;
  }

  .pattern-preview {
    padding: 20px;
  }

  .theme-colors {
    flex-direction: column;
  }
}
</style>