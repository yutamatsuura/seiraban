<template>
  <MainLayout>
    <div class="preview">
    <div class="page-header">
      <h1 class="page-title">
        <img src="/src/assets/icons/document-preview.svg" alt="鑑定プレビュー" class="page-title-icon" />
        鑑定プレビュー
      </h1>
      <p v-if="diagnosis" class="diagnosis-datetime">鑑定日時: {{ formatDateTime(diagnosis.created_at) }}</p>

      <div class="action-buttons">
        <!-- 新しいダウンロードボタン -->
        <button
          @click="downloadFile('pdf')"
          :disabled="downloadGenerating || !diagnosis || (diagnosis.status !== 'completed' && diagnosis.status !== 'partial')"
          class="btn btn-primary"
        >
          <span v-if="downloadGenerating === 'pdf'">PDF出力中...</span>
          <span v-else>PDF出力</span>
        </button>
        <button
          @click="downloadFile('docx')"
          :disabled="downloadGenerating || !diagnosis || (diagnosis.status !== 'completed' && diagnosis.status !== 'partial')"
          class="btn btn-primary"
        >
          <span v-if="downloadGenerating === 'docx'">Word出力中...</span>
          <span v-else>Word出力</span>
        </button>

        <!-- テンプレート設定ボタン -->
        <button
          @click="toggleTemplatePanel"
          class="btn btn-template"
          :class="{ active: showTemplatePanel }"
          :disabled="!diagnosis || (diagnosis.status !== 'completed' && diagnosis.status !== 'partial')"
        >
          デザイン設定
        </button>

        <button
          @click="toggleAdminMode"
          class="btn btn-admin"
          :class="{ active: adminMode }"
        >
          <span v-if="adminMode">管理者モード ON</span>
          <span v-else>管理者モード OFF</span>
        </button>
        <button
          @click="backToForm"
          class="btn btn-secondary"
        >
          入力画面に戻る
        </button>
      </div>
    </div>

    <!-- Loading or Processing State - 超シンプル版（処理中の場合のみ） -->
    <div v-if="diagnosis && diagnosis.status === 'processing'" class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <div class="loading-text">
          <h2>鑑定を実行中です</h2>
          <p v-if="diagnosis">{{ diagnosis.client_name }} 様の鑑定結果を計算しています...</p>
          <p class="time-estimate">
            処理時間の目安：
            <span v-if="diagnosis?.diagnosis_pattern === 'kyusei_only'">5〜15秒程度</span>
            <span v-else-if="diagnosis?.diagnosis_pattern === 'seimei_only'">5〜15秒程度</span>
            <span v-else>15〜30秒程度</span>
          </p>
          <p class="loading-dots">お待ちください<span class="dots"></span></p>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <h3>エラーが発生しました</h3>
      <p>{{ error }}</p>
      <button @click="loadDiagnosis" class="btn btn-primary">再試行</button>
    </div>

    <!-- Main Content - Only show when diagnosis is completed -->
    <div
      v-else-if="diagnosis && (diagnosis.status === 'completed' || diagnosis.status === 'partial')"
      class="diagnosis-content"
      :class="{
        'pattern-clean': true,
        [`theme-${templateSettings?.color_theme}`]: templateSettings?.color_theme,
        [`font-${templateSettings?.font_family}`]: templateSettings?.font_family,
        [`layout-${templateSettings?.layout_style}`]: templateSettings?.layout_style
      }"
      :style="templateStyles"
      id="diagnosis-report"
    >

      <!-- Pattern A: Modern Minimal Header -->
      <div class="template-header modern-minimal">
        <div class="header-background"></div>
        <div class="header-content">
          <!-- Logo Section -->
          <div class="logo-section">
            <div v-if="logoUrl" class="logo-container">
              <img :src="logoUrl" alt="ロゴ" class="logo-image" />
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
              <span v-if="diagnosis.diagnosis_pattern === 'kyusei_only'">九星気学・吉方位鑑定書</span>
              <span v-else-if="diagnosis.diagnosis_pattern === 'seimei_only'">姓名判断鑑定書</span>
              <span v-else>九星気学・姓名判断 総合鑑定書</span>
            </h1>
            <div class="title-ornament"></div>
          </div>

          <!-- Business Info Section -->
          <div class="business-section">
            <div v-if="templateSettings?.business_name" class="business-card">
              <div class="business-info">
                <h2 class="business-name">{{ templateSettings.business_name }}</h2>
                <p v-if="templateSettings?.operator_name" class="operator-name">
                  <span class="operator-label">鑑定士</span>
                  <span class="operator-value">{{ templateSettings.operator_name }}</span>
                </p>
              </div>
            </div>
            <!-- デバッグ表示：テンプレート設定が読み込まれていない場合 -->
            <div v-else-if="!templateLoading" class="business-card debug-placeholder">
              <div class="business-info">
                <h2 class="business-name">テンプレート設定未取得</h2>
                <p class="operator-name">
                  <span class="operator-label">状態:</span>
                  <span class="operator-value">{{ templateSettings ? 'データあり' : 'データなし' }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Date Section -->
        <div class="date-section">
          <div class="date-container">
            <span class="date-label">鑑定実施日</span>
            <span class="date-value">{{ formatDate(diagnosis.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Client Information - 姓名判断パターンでは非表示 -->
      <div v-if="diagnosis.diagnosis_pattern !== 'seimei_only'" class="card client-info">
        <div class="card-header">
          <h2>依頼者情報</h2>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>お名前</label>
              <span>{{ diagnosis.client_name }}</span>
            </div>
            <div class="info-item">
              <label>生年月日</label>
              <span>{{
                formatDateWithAge(diagnosis.client_info?.birth_date) ||
                '未設定'
              }}</span>
            </div>
            <div v-if="diagnosis.client_info?.birth_time" class="info-item">
              <label>出生時間</label>
              <span>{{ diagnosis.client_info.birth_time }}</span>
            </div>
            <div class="info-item">
              <label>十二支</label>
              <span>{{ diagnosis.kyusei_result?.eto || '未取得' }}</span>
            </div>
            <div class="info-item">
              <label>性別</label>
              <span>{{ formatGender(diagnosis.client_info?.gender) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Kyusei (Nine Star Astrology) Results -->
      <div v-if="diagnosis.kyusei_result && (diagnosis.diagnosis_pattern === 'kyusei_only' || diagnosis.diagnosis_pattern === 'all' || !diagnosis.diagnosis_pattern)" class="card kyusei-results">
        <div class="card-header">
          <h2>九星気学・吉方位の鑑定結果</h2>
        </div>
        <div class="card-body">
          <div v-if="diagnosis.kyusei_result" class="kyusei-data">
            <!-- Basic Nine Star Information -->
            <div class="section">
              <h3>基本九星情報</h3>
              <div class="nine-star-grid">
                <div class="star-item">
                  <label>本命星</label>
                  <span class="star-value">{{ diagnosis.kyusei_result.honmeisei || '未取得' }}</span>
                </div>
                <div class="star-item">
                  <label>月命星</label>
                  <span class="star-value">{{ diagnosis.kyusei_result.getsumeisei || '未取得' }}</span>
                </div>
              </div>
            </div>

            <!-- Zodiac Information -->
            <div v-if="diagnosis.kyusei_result.year_kanshi || diagnosis.kyusei_result.month_kanshi || diagnosis.kyusei_result.day_kanshi" class="section">
              <h3>干支情報</h3>
              <div class="zodiac-grid">
                <div class="zodiac-item">
                  <label>年干支</label>
                  <span>{{ diagnosis.kyusei_result.year_kanshi || '未取得' }}</span>
                </div>
                <div class="zodiac-item">
                  <label>月干支</label>
                  <span>{{ diagnosis.kyusei_result.month_kanshi || '未取得' }}</span>
                </div>
                <div class="zodiac-item">
                  <label>日干支</label>
                  <span>{{ diagnosis.kyusei_result.day_kanshi || '未取得' }}</span>
                </div>
                <div v-if="diagnosis.kyusei_result.naon" class="zodiac-item">
                  <label>納音</label>
                  <span>{{ diagnosis.kyusei_result.naon }}</span>
                </div>
              </div>
            </div>


            <!-- 吉方位情報 -->
            <div v-if="isValidDirection(diagnosis.kyusei_result.max_kichigata) || isValidDirection(diagnosis.kyusei_result.kichigata)" class="section">
              <h3>吉方位情報</h3>
              <div class="direction-grid">
                <div v-if="isValidDirection(diagnosis.kyusei_result.max_kichigata)" class="direction-item">
                  <label>最大吉方</label>
                  <span>{{ diagnosis.kyusei_result.max_kichigata }}</span>
                </div>
                <div v-if="isValidDirection(diagnosis.kyusei_result.kichigata)" class="direction-item">
                  <label>吉方</label>
                  <span>{{ diagnosis.kyusei_result.kichigata }}</span>
                </div>
              </div>
            </div>

            <!-- 傾斜・同会情報 -->
            <div v-if="diagnosis.kyusei_result.keisha || diagnosis.kyusei_result.doukai" class="section">
              <h3>傾斜・同会情報</h3>
              <div class="special-info-grid">
                <div v-if="diagnosis.kyusei_result.keisha" class="special-info-item">
                  <label>傾斜</label>
                  <span>{{ diagnosis.kyusei_result.keisha }}</span>
                </div>
                <div v-if="diagnosis.kyusei_result.doukai" class="special-info-item">
                  <label>同会</label>
                  <span>{{ diagnosis.kyusei_result.doukai }}</span>
                </div>
              </div>
            </div>


            <!-- Raw Data (for debugging) - 管理者モードのみ表示 -->
            <details v-if="adminMode" class="raw-data">
              <summary>詳細データ（技術者向け）</summary>
              <pre>{{ JSON.stringify(diagnosis.kyusei_result, null, 2) }}</pre>
            </details>
          </div>
        </div>
      </div>

      <!-- Seimei (Name Divination) Results -->
      <div v-if="diagnosis.seimei_result && (diagnosis.diagnosis_pattern === 'seimei_only' || diagnosis.diagnosis_pattern === 'all' || !diagnosis.diagnosis_pattern)" class="card seimei-results">
        <div class="card-header">
          <h2>姓名判断の鑑定結果</h2>
        </div>
        <div class="card-body">
          <div v-if="diagnosis.seimei_result.data" class="seimei-data">
            <!-- Character Details -->
            <div v-if="diagnosis.seimei_result.data.画数" class="section">
              <h3>文字の構成</h3>
              <div class="character-table">
                <table>
                  <thead>
                    <tr>
                      <th>文字</th>
                      <th v-for="key in availableCharacterKeys" :key="key">
                        {{ nameCharacters[key] || key }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>画数</td>
                      <td v-for="key in availableCharacterKeys" :key="key">
                        {{ diagnosis.seimei_result.data.画数[key] }}
                      </td>
                    </tr>
                    <tr v-if="diagnosis.seimei_result.data.五行">
                      <td>五行</td>
                      <td v-for="key in availableCharacterKeys" :key="key">
                        {{ diagnosis.seimei_result.data.五行[key] }}
                      </td>
                    </tr>
                    <tr v-if="diagnosis.seimei_result.data.陰陽">
                      <td>陰陽</td>
                      <td v-for="key in availableCharacterKeys" :key="key">
                        {{ diagnosis.seimei_result.data.陰陽[key] }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Stroke Count Analysis -->
            <div v-if="diagnosis.seimei_result.data.格数" class="section">
              <div class="stroke-grid">
                <div v-if="diagnosis.seimei_result.data.格数.天格" class="stroke-item">
                  <label>天格</label>
                  <span>{{ diagnosis.seimei_result.data.格数.天格 }}</span>
                </div>
                <div v-if="diagnosis.seimei_result.data.格数.人格" class="stroke-item">
                  <label>人格</label>
                  <span>{{ diagnosis.seimei_result.data.格数.人格 }}</span>
                </div>
                <div v-if="diagnosis.seimei_result.data.格数.地格" class="stroke-item">
                  <label>地格</label>
                  <span>{{ diagnosis.seimei_result.data.格数.地格 }}</span>
                </div>
                <div v-if="diagnosis.seimei_result.data.格数.総画" class="stroke-item">
                  <label>総画</label>
                  <span>{{ diagnosis.seimei_result.data.格数.総画 }}</span>
                </div>
              </div>
            </div>

            <!-- Name Analysis Results -->
            <div class="section section-spacing-large">
              <h3>鑑定の結果</h3>
              <div class="result-content">
                <div class="score-section">
                  <div class="score-value">{{ diagnosis.seimei_result.data.総評点数 || '未取得' }}</div>
                  <div class="score-label">点/100</div>
                </div>
                <div v-if="diagnosis.seimei_result.data.総評メッセージ" class="message-section">
                  <p>{{ diagnosis.seimei_result.data.総評メッセージ }}</p>
                </div>
              </div>
            </div>

            <!-- 文字による鑑定 -->
            <div v-if="diagnosis.seimei_result.data.詳細鑑定?.文字による鑑定 && Object.keys(diagnosis.seimei_result.data.詳細鑑定.文字による鑑定).length > 0" class="section">
              <h3>文字による鑑定</h3>
              <div class="character-evaluation-grid">
                <div v-for="(detail, character) in diagnosis.seimei_result.data.詳細鑑定.文字による鑑定" :key="character" class="character-evaluation-item">
                  <div class="evaluation-header">
                    <span class="character-name">{{ character.replace(/_\d+$/, '') }}</span>
                  </div>
                  <div class="evaluation-detail" v-html="formatBrackets(detail)"></div>
                </div>
              </div>
            </div>

            <!-- 陰陽による鑑定 -->
            <div v-if="diagnosis.seimei_result.data.詳細鑑定?.陰陽による鑑定 && Object.keys(diagnosis.seimei_result.data.詳細鑑定.陰陽による鑑定).length > 0" class="section">
              <h3>陰陽による鑑定</h3>
              <div class="character-evaluation-grid">
                <div v-for="(detail, name) in diagnosis.seimei_result.data.詳細鑑定.陰陽による鑑定" :key="name" class="character-evaluation-item">
                  <div class="evaluation-header">
                    <span class="character-name">{{ name }}</span>
                  </div>
                  <div class="evaluation-detail" v-html="formatBrackets(detail)"></div>
                </div>
              </div>
            </div>

            <!-- 五行による鑑定 -->
            <div v-if="diagnosis.seimei_result.data.詳細鑑定?.五行による鑑定 && Object.keys(diagnosis.seimei_result.data.詳細鑑定.五行による鑑定).length > 0" class="section">
              <h3>五行による鑑定</h3>
              <div class="character-evaluation-grid">
                <div v-for="(detail, target) in diagnosis.seimei_result.data.詳細鑑定.五行による鑑定" :key="target" class="character-evaluation-item">
                  <div class="evaluation-header">
                    <span class="character-name">{{ target }}</span>
                  </div>
                  <div class="evaluation-detail" v-html="formatBrackets(detail)"></div>
                </div>
              </div>
            </div>

            <!-- 画数による鑑定 -->
            <div v-if="diagnosis.seimei_result.data.詳細鑑定?.画数による鑑定 && Object.keys(diagnosis.seimei_result.data.詳細鑑定.画数による鑑定).length > 0" class="section">
              <h3>画数による鑑定</h3>
              <div class="character-evaluation-grid">
                <div v-for="(detail, target) in diagnosis.seimei_result.data.詳細鑑定.画数による鑑定" :key="target" class="character-evaluation-item">
                  <div class="evaluation-header">
                    <span class="character-name">{{ target }}</span>
                  </div>
                  <div class="evaluation-detail" v-html="formatBrackets(detail)"></div>
                </div>
              </div>
            </div>

            <!-- 天地による鑑定 -->
            <div v-if="diagnosis.seimei_result.data.詳細鑑定?.天地による鑑定 && Object.keys(diagnosis.seimei_result.data.詳細鑑定.天地による鑑定).length > 0" class="section">
              <h3>天地による鑑定</h3>
              <div class="character-evaluation-grid">
                <div v-for="(detail, name) in diagnosis.seimei_result.data.詳細鑑定.天地による鑑定" :key="name" class="character-evaluation-item">
                  <div class="evaluation-header">
                    <span class="character-name">{{ name }}</span>
                  </div>
                  <div class="evaluation-detail" v-html="formatBrackets(detail)"></div>
                </div>
              </div>
            </div>


            <!-- Raw Data (for debugging) - 管理者モードのみ表示 -->
            <details v-if="adminMode" class="raw-data">
              <summary>詳細データ（技術者向け）</summary>
              <pre>{{ JSON.stringify(diagnosis.seimei_result.data, null, 2) }}</pre>
            </details>
          </div>
        </div>
      </div>

      <!-- Template Footer -->
      <div class="template-footer modern-minimal">
        <div class="footer-content">
          <div v-if="templateSettings?.business_name || templateSettings?.operator_name" class="footer-info">
            <div v-if="templateSettings?.business_name" class="footer-business">
              {{ templateSettings.business_name }}
            </div>
            <div v-if="templateSettings?.operator_name" class="footer-operator">
              鑑定士：{{ templateSettings.operator_name }}
            </div>
          </div>
          <div class="footer-disclaimer">
            ※この鑑定は参考用であり、結果について当事務所は責任を負いかねます。
          </div>
        </div>
      </div>

      <!-- 鑑定士コメント入力セクション -->
      <div v-if="diagnosis && (diagnosis.status === 'completed' || diagnosis.status === 'partial')" class="card appraiser-comment-section">
        <div class="card-header">
          <h2>鑑定士コメント</h2>
          <p>お客様への追加メッセージ（2-3行、任意）</p>
        </div>
        <div class="card-body">
          <textarea
            v-model="appraiserComment"
            class="appraiser-comment-input"
            placeholder="お客様へのメッセージを入力してください（2-3行程度）&#10;例：この鑑定結果は非常に興味深いものです。&#10;お客様の運勢について詳細に分析いたしました。"
            rows="3"
            maxlength="500"
          ></textarea>
          <div class="comment-actions">
            <button
              @click="updateAppraiserComment"
              :disabled="commentUpdating"
              class="btn btn-primary"
            >
              {{ commentUpdating ? '保存中...' : 'コメントを保存' }}
            </button>
            <div class="char-count">{{ appraiserComment.length }}/500</div>
          </div>
        </div>
      </div>

      <!-- テンプレート設定パネル -->
      <div v-if="showTemplatePanel" class="card template-panel">
        <div class="card-header">
          <h2>デザイン設定</h2>
          <p>鑑定書のデザインとブランディングを設定します</p>
        </div>

        <!-- エラー・成功メッセージ -->
        <div v-if="templateError" class="alert alert-error">
          {{ templateError }}
        </div>
        <div v-if="templateSuccess" class="alert alert-success">
          {{ templateSuccess }}
        </div>

        <div class="card-body">
          <div v-if="templateLoading" class="loading">
            設定を読み込み中...
          </div>

          <div v-else class="template-form">
            <div class="form-group">
              <label for="business_name">事業者名 *</label>
              <input
                id="business_name"
                v-model="templateForm.business_name"
                type="text"
                placeholder="占いサロン 星花"
                required
              />
            </div>

            <div class="form-group">
              <label for="operator_name">鑑定士名 *</label>
              <input
                id="operator_name"
                v-model="templateForm.operator_name"
                type="text"
                placeholder="星野 花子"
                required
              />
            </div>

            <div class="form-group">
              <label for="color_theme">カラーテーマ</label>
              <select id="color_theme" v-model="templateForm.color_theme" @change="applyTemplateChanges">
                <option value="default">デフォルト</option>
                <option value="elegant">エレガント</option>
                <option value="warm">ウォーム</option>
                <option value="natural">ナチュラル</option>
                <option value="professional">プロフェッショナル</option>
              </select>
            </div>

            <div class="form-group">
              <label for="font_family">フォントファミリー</label>
              <select id="font_family" v-model="templateForm.font_family" @change="applyTemplateChanges">
                <option value="default">デフォルト</option>
                <option value="noto-serif">Noto Serif JP</option>
                <option value="noto-sans">Noto Sans JP</option>
                <option value="mincho">明朝体</option>
                <option value="gothic">ゴシック体</option>
              </select>
            </div>

            <div class="form-group">
              <label for="layout_style">レイアウトスタイル</label>
              <select id="layout_style" v-model="templateForm.layout_style" @change="applyTemplateChanges">
                <option value="standard">スタンダード</option>
                <option value="compact">コンパクト</option>
                <option value="detailed">詳細</option>
              </select>
            </div>

            <div class="form-group">
              <label for="custom_css">カスタムCSS（任意）</label>
              <textarea
                id="custom_css"
                v-model="templateForm.custom_css"
                rows="4"
                placeholder="/* カスタムCSSを入力 */&#10;.diagnosis-title { color: #333; }"
                @input="applyTemplateChanges"
              ></textarea>
            </div>

            <div class="form-actions">
              <button
                type="button"
                @click="saveTemplateSettings"
                :disabled="templateSaving || !isTemplateFormValid"
                class="btn btn-primary"
              >
                {{ templateSaving ? '保存中...' : '設定を保存' }}
              </button>

              <button
                type="button"
                @click="loadTemplateSettings"
                :disabled="templateLoading"
                class="btn btn-secondary"
              >
                設定を再読み込み
              </button>

              <button
                type="button"
                @click="resetTemplateToDefault"
                class="btn btn-outline"
              >
                デフォルトにリセット
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- No Data State -->
    <div v-else-if="!loading && !diagnosis" class="no-data-container">
      <h3>鑑定データが見つかりません</h3>
      <p>鑑定IDが正しくないか、鑑定がまだ作成されていません。</p>
      <router-link to="/kantei/new" class="btn btn-primary">新しい鑑定を作成</router-link>
    </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'
import type { DiagnosisResult, TemplateSettings } from '@/services/api-client'

const route = useRoute()
const router = useRouter()

const diagnosis = ref<DiagnosisResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const pdfGenerating = ref(false)
const downloadGenerating = ref<string | null>(null) // 'pdf' | 'docx' | null
const autoRefreshTimer = ref<number | null>(null)
const stepProgress = ref(0)
const adminMode = ref(false)
const showTemplatePanel = ref(false)
const appraiserComment = ref('')
const commentUpdating = ref(false)

// テンプレート設定
const templateSettings = ref<TemplateSettings | null>(null)
const templateLoading = ref(false)
const templateSaving = ref(false)
const templateError = ref('')
const templateSuccess = ref('')
const templateForm = ref({
  business_name: '',
  operator_name: '',
  color_theme: 'default',
  font_family: 'default',
  layout_style: 'standard',
  custom_css: ''
})

// シンプルなローディング用の変数
const remainingSeconds = ref(60)
const currentStep = ref(0)
const countdownTimer = ref<number | null>(null)
const progressTimer = ref<number | null>(null)
const funFactTimer = ref<number | null>(null)
const currentFunFactIndex = ref(0)

// 処理状況の詳細データ（プロ鑑定士向け）
const processDetails = [
  {
    title: '九星気学データ処理中',
    content: '生年月日から本命星・月命星を算出し、十二支・干支データベースとの照合を行っています。'
  },
  {
    title: '吉方位算出処理',
    content: '現在の時期に適した最大吉方・吉方を九星盤から詳細計算しています。'
  },
  {
    title: '姓名判断データ解析',
    content: 'お名前の画数から天格・人格・地格・外格・総格を算出し、陰陽五行との照合を実行中です。'
  },
  {
    title: '総合鑑定結果統合',
    content: '九星気学と姓名判断の結果を統合し、プロ鑑定用の詳細レポートを生成しています。'
  },
  {
    title: 'PDF出力準備',
    content: '鑑定結果をお客様提示用のフォーマットに整形し、印刷可能な形式で準備しています。'
  }
]

const currentProcessDetail = computed(() => processDetails[currentFunFactIndex.value % processDetails.length])

const diagnosisId = computed(() => route.params.id as string)

// テンプレートフォームのバリデーション
const isTemplateFormValid = computed(() => {
  return templateForm.value.business_name.trim() !== '' &&
         templateForm.value.operator_name.trim() !== ''
})

const loadDiagnosis = async () => {
  if (!diagnosisId.value) {
    error.value = '鑑定IDが指定されていません'
    return
  }

  console.log('🎯 loadDiagnosis開始', {
    diagnosisId: diagnosisId.value,
    currentStatus: diagnosis.value?.status,
    currentLoading: loading.value
  })

  // 初回読み込み時は一時的にloadingを設定、完了状態の場合はすぐに解除
  loading.value = true
  error.value = null

  try {
    const result = await apiClient.getDiagnosis(diagnosisId.value, adminMode.value)
    console.log('📡 API応答受信:', {
      status: result.status,
      hasKyusei: !!result.kyusei_result,
      hasSeimei: !!result.seimei_result
    })
    diagnosis.value = result

    // 鑑定士コメントを初期化
    appraiserComment.value = result.appraiser_comment || ''

    // ステップ進行状況を更新
    updateStepProgress(result)
  } catch (err: any) {
    console.error('Failed to load diagnosis:', err)
    error.value = err.message || '鑑定データの読み込みに失敗しました'
  } finally {
    // loadingを解除（完了状態の場合はupdateStepProgressで既に解除済み）
    if (diagnosis.value?.status !== 'processing') {
      loading.value = false
    }
  }
}

// テンプレート設定読み込み
const loadTemplateSettings = async () => {
  templateLoading.value = true
  templateError.value = ''
  templateSuccess.value = ''
  console.log('🔧 テンプレート設定読み込み開始')

  try {
    const settings = await apiClient.getTemplateSettings()
    console.log('✅ テンプレート設定読み込み成功:', settings)
    templateSettings.value = settings

    // フォームデータに反映
    templateForm.value = {
      business_name: settings.business_name || '',
      operator_name: settings.operator_name || '',
      color_theme: settings.color_theme || 'default',
      font_family: settings.font_family || 'default',
      layout_style: settings.layout_style || 'standard',
      custom_css: settings.custom_css || ''
    }

    templateSuccess.value = '設定を読み込みました'
    setTimeout(() => templateSuccess.value = '', 3000)
  } catch (err: any) {
    console.error('❌ テンプレート設定読み込み失敗:', err)
    templateError.value = err.message || '設定の読み込みに失敗しました'
  } finally {
    templateLoading.value = false
  }
}

const generatePDF = async () => {
  if (!diagnosis.value) return

  pdfGenerating.value = true
  try {
    console.log('PDF generation started for:', diagnosis.value.id)

    const response = await apiClient.generatePDF(diagnosis.value.id)

    if (response.success) {
      console.log('PDF generation successful:', response)

      // 静的ファイルのURLを構築
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8502'
      const fileUrl = `${baseURL}${response.pdf_url.replace('/tmp/pdf_storage', '/static')}`

      if (response.filename.endsWith('.pdf')) {
        // PDFファイルの場合、ダウンロードリンクを作成
        const link = document.createElement('a')
        link.href = fileUrl
        link.download = response.filename
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        // 成功メッセージを表示
        alert(`${response.message}\nファイル名: ${response.filename}`)
      } else {
        // HTMLファイルの場合、新しいタブで開く
        window.open(fileUrl, '_blank')
        alert(`${response.message}\nファイル名: ${response.filename}`)
      }
    } else {
      throw new Error('PDF生成に失敗しました')
    }
  } catch (err: any) {
    console.error('PDF generation failed:', err)
    alert('PDF生成に失敗しました: ' + err.message)
  } finally {
    pdfGenerating.value = false
  }
}

const toggleAdminMode = async () => {
  adminMode.value = !adminMode.value
  // 管理者モード変更時にデータを再読み込み
  await loadDiagnosis()
}

const backToForm = () => {
  router.push('/kantei/new')
}

// 新しいダウンロード機能
const downloadFile = async (format: 'pdf' | 'docx') => {
  if (!diagnosis.value) return

  downloadGenerating.value = format
  try {
    console.log(`${format.toUpperCase()} ダウンロード開始:`, diagnosis.value.id)

    const response = await fetch(`http://localhost:8503/api/diagnosis/${diagnosis.value.id}/download/${format}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`${format.toUpperCase()}生成に失敗しました`)
    }

    // ファイルをダウンロード
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url

    // ファイル名を取得（Content-Dispositionヘッダーから）
    const disposition = response.headers.get('content-disposition')
    let filename = `鑑定書.${format}`
    if (disposition && disposition.includes('filename=')) {
      const filenameMatch = disposition.match(/filename\*?=([^;]+)/)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1].replace(/['"]/g, ''))
      }
    }

    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    console.log(`${format.toUpperCase()} ダウンロード完了`)
  } catch (err: any) {
    console.error(`${format.toUpperCase()} ダウンロードエラー:`, err)
    alert(`${format.toUpperCase()}ダウンロードに失敗しました: ${err.message}`)
  } finally {
    downloadGenerating.value = null
  }
}

// テンプレートパネルの切り替え
const toggleTemplatePanel = () => {
  showTemplatePanel.value = !showTemplatePanel.value
}

// 鑑定士コメント更新
const updateAppraiserComment = async () => {
  if (!diagnosis.value) return

  commentUpdating.value = true
  try {
    const response = await fetch(`http://localhost:8503/api/diagnosis/${diagnosis.value.id}/comment`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ comment: appraiserComment.value.trim() })
    })

    if (!response.ok) {
      throw new Error('コメントの保存に失敗しました')
    }

    const result = await response.json()
    console.log('鑑定士コメント更新成功:', result)

    // 診断データを更新
    if (diagnosis.value) {
      diagnosis.value.appraiser_comment = appraiserComment.value.trim()
    }

    alert('コメントを保存しました')
  } catch (err: any) {
    console.error('鑑定士コメント更新エラー:', err)
    alert('コメントの保存に失敗しました: ' + err.message)
  } finally {
    commentUpdating.value = false
  }
}

// テンプレート設定保存
const saveTemplateSettings = async () => {
  if (!isTemplateFormValid.value || templateSaving.value) return

  templateSaving.value = true
  templateError.value = ''
  templateSuccess.value = ''

  try {
    const updateData = {
      business_name: templateForm.value.business_name.trim(),
      operator_name: templateForm.value.operator_name.trim(),
      color_theme: templateForm.value.color_theme,
      font_family: templateForm.value.font_family,
      layout_style: templateForm.value.layout_style,
      custom_css: templateForm.value.custom_css.trim() || undefined
    }

    const result = await apiClient.updateTemplateSettings(updateData)
    templateSettings.value = result
    templateSuccess.value = '設定を保存しました'
    setTimeout(() => templateSuccess.value = '', 3000)

    console.log('テンプレート設定保存完了:', result)
  } catch (err: any) {
    templateError.value = err.message || '設定の保存に失敗しました'
    console.error('テンプレート設定保存エラー:', err)
  } finally {
    templateSaving.value = false
  }
}

// リアルタイムでテンプレート変更を適用
const applyTemplateChanges = () => {
  console.log('🎨 リアルタイムテンプレート変更適用:', templateForm.value)

  // カラーテーマの適用
  const root = document.documentElement
  switch (templateForm.value.color_theme) {
    case 'elegant':
      root.style.setProperty('--primary-color', '#6b46c1')
      root.style.setProperty('--accent-color', '#d8b4fe')
      break
    case 'warm':
      root.style.setProperty('--primary-color', '#dc2626')
      root.style.setProperty('--accent-color', '#fecaca')
      break
    case 'natural':
      root.style.setProperty('--primary-color', '#059669')
      root.style.setProperty('--accent-color', '#a7f3d0')
      break
    case 'professional':
      root.style.setProperty('--primary-color', '#1f2937')
      root.style.setProperty('--accent-color', '#e5e7eb')
      break
    default:
      root.style.setProperty('--primary-color', '#2563eb')
      root.style.setProperty('--accent-color', '#93c5fd')
  }

  // フォントファミリーの適用
  const bodyElement = document.body
  switch (templateForm.value.font_family) {
    case 'noto-serif':
      bodyElement.style.fontFamily = '"Noto Serif JP", serif'
      break
    case 'noto-sans':
      bodyElement.style.fontFamily = '"Noto Sans JP", sans-serif'
      break
    case 'mincho':
      bodyElement.style.fontFamily = '"游明朝", "Yu Mincho", "Hiragino Mincho Pro", serif'
      break
    case 'gothic':
      bodyElement.style.fontFamily = '"游ゴシック", "Yu Gothic", "Hiragino Kaku Gothic Pro", sans-serif'
      break
    default:
      bodyElement.style.fontFamily = ''
  }

  // カスタムCSSの適用
  let customStyleElement = document.getElementById('template-custom-css')
  if (!customStyleElement) {
    customStyleElement = document.createElement('style')
    customStyleElement.id = 'template-custom-css'
    document.head.appendChild(customStyleElement)
  }
  customStyleElement.textContent = templateForm.value.custom_css
}

// デフォルト設定にリセット
const resetTemplateToDefault = () => {
  templateForm.value = {
    business_name: '',
    operator_name: '',
    color_theme: 'default',
    font_family: 'default',
    layout_style: 'standard',
    custom_css: ''
  }
  applyTemplateChanges()
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '未設定'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

const formatBrackets = (text: string) => {
  // 【】括弧を太字に変換
  return text.replace(/【([^】]*)】/g, '<strong>【$1】</strong>')
}

const formatDateWithAge = (dateString?: string) => {
  if (!dateString) return '未設定'
  try {
    const birthDate = new Date(dateString)
    const today = new Date()

    // 年齢計算
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }

    const formattedDate = birthDate.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })

    return `${formattedDate}（${age}歳）`
  } catch {
    return dateString
  }
}

const formatDateTime = (dateString?: string) => {
  if (!dateString) return '未設定'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const formatGender = (gender?: string) => {
  if (!gender) return '未設定'
  return gender === 'male' ? '男性' : gender === 'female' ? '女性' : gender
}

const hasStrokeData = (data: any) => {
  return data && (data.天格 || data.人格 || data.地格 || data.外格 || data.総格)
}

const isValidDirection = (direction?: string) => {
  if (!direction || typeof direction !== 'string') return false
  const trimmed = direction.trim().replace(/[,、\s]*$/, '') // 末尾の区切り文字を除去
  if (!trimmed) return false

  // 無効な値をフィルタリング
  const invalidValues = ['月盤', '年盤', '日盤', 'なし', '無し', '-', '']
  if (invalidValues.includes(trimmed)) return false

  // 九星データのパターンをチェック（二黒土星,八白土星 など）
  const kyuseiPattern = /^[一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星([,、\s]*[一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)*$/
  return kyuseiPattern.test(trimmed)
}

// 実際の文字を取得するcomputed property
const nameCharacters = computed(() => {
  const name = diagnosis.value?.seimei_result?.input?.name
  if (!name) return {}

  // 姓名を分割（スペースで区切られていることを想定）
  const parts = name.split(/\s+/)
  if (parts.length !== 2) return {}

  const [sei, mei] = parts
  const characters: { [key: string]: string } = {}

  // 姓の文字（4文字以上対応）
  for (let i = 0; i < sei.length; i++) {
    characters[`姓${i + 1}`] = sei[i]
  }

  // 名の文字（4文字以上対応）
  for (let i = 0; i < mei.length; i++) {
    characters[`名${i + 1}`] = mei[i]
  }

  return characters
})

// 利用可能な文字キーの配列を取得
const availableCharacterKeys = computed(() => {
  const data = diagnosis.value?.seimei_result?.data
  if (!data || !data.画数) return []

  return Object.keys(data.画数).sort((a, b) => {
    // 姓1, 姓2, 名1, 名2 の順序でソート
    const aType = a.startsWith('姓') ? 0 : 1
    const bType = b.startsWith('姓') ? 0 : 1
    if (aType !== bType) return aType - bType

    const aNum = parseInt(a.slice(1))
    const bNum = parseInt(b.slice(1))
    return aNum - bNum
  })
})

// テンプレート設定に基づく動的スタイル
const templateStyles = computed(() => {
  const settings = templateSettings.value
  if (!settings) return {}

  const styles: Record<string, string> = {}

  // カラーテーマの適用
  if (settings.color_theme && settings.color_theme !== 'default') {
    const themeColors = getThemeColors(settings.color_theme)
    styles['--primary-color'] = themeColors.primary
    styles['--accent-color'] = themeColors.accent
  }

  // フォントファミリーの適用
  if (settings.font_family && settings.font_family !== 'default') {
    styles['--main-font'] = getFontFamily(settings.font_family)
  }

  return styles
})

// ロゴURLの取得
const logoUrl = computed(() => {
  if (!templateSettings.value?.logo_url) return null
  const url = templateSettings.value.logo_url
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8502'
  return url.startsWith('http') ? url : `${baseURL}/${url}`
})

// テーマカラーの取得
const getThemeColors = (theme: string) => {
  const colorMap = {
    elegant: { primary: '#8e44ad', accent: '#9b59b6' },
    warm: { primary: '#e67e22', accent: '#d35400' },
    natural: { primary: '#27ae60', accent: '#2ecc71' },
    professional: { primary: '#34495e', accent: '#2c3e50' }
  }
  return colorMap[theme as keyof typeof colorMap] || { primary: '#3498db', accent: '#2980b9' }
}

// フォントファミリーの取得
const getFontFamily = (font: string) => {
  const fontMap = {
    'noto-serif': '"Noto Serif JP", serif',
    'noto-sans': '"Noto Sans JP", sans-serif',
    'hiragino': '"Hiragino Mincho ProN", serif',
    'yu-mincho': '"Yu Mincho", serif'
  }
  return fontMap[font as keyof typeof fontMap] || 'inherit'
}

const updateStepProgress = (result: DiagnosisResult) => {
  // 診断が完了した時（completed または partial）は即座にプレビュー表示
  if (result.status === 'completed' || result.status === 'partial') {
    stopAutoRefresh()
    loading.value = false
    return
  }
}

// 自動更新機能
const startAutoRefresh = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
  }

  autoRefreshTimer.value = setInterval(() => {
    if (diagnosis.value?.status === 'processing') {
      loadDiagnosis()
    } else {
      stopAutoRefresh()
    }
  }, 1000) // 1秒ごとに更新
}

const stopAutoRefresh = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
    autoRefreshTimer.value = null
  }
}

// 診断ステータスが変更されたら自動更新を管理
watch(() => diagnosis.value?.status, (newStatus) => {
  if (newStatus === 'processing') {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// loading状態の変更を監視
watch(() => loading.value, (newLoading, oldLoading) => {
  console.log('🔄 Loading状態変更:', oldLoading, '→', newLoading)
})

// シンプルローディングではプログレス監視不要

// シンプルローディングではプログレスアニメーション不要

// 待機画面のシミュレーション
const startProgressSimulation = () => {
  let progress = 0
  const progressInterval = setInterval(() => {
    if (progress < 100 && (loading.value || (diagnosis.value && diagnosis.value.status === 'processing'))) {
      progress += Math.random() * 15 + 5 // 5-20%ずつ進行
      progressPercentage.value = Math.min(progress, 100)

      // ステップの更新
      if (progress >= 50 && currentStep.value === 0) {
        currentStep.value = 1
      }
      if (progress >= 100) {
        currentStep.value = 2
        clearInterval(progressInterval)
      }
    } else if (!loading.value && (!diagnosis.value || diagnosis.value.status !== 'processing')) {
      clearInterval(progressInterval)
    }
  }, 400) // 更新間隔を高速化（800ms→400ms）
}

// カウントダウンタイマー
const startCountdown = () => {
  const timer = setInterval(() => {
    if (remainingSeconds.value > 0 && (loading.value || (diagnosis.value && diagnosis.value.status === 'processing'))) {
      remainingSeconds.value--
    } else {
      clearInterval(timer)
    }
  }, 1000)
}

// 処理詳細のローテーション
const rotateProcessDetail = () => {
  const detailInterval = setInterval(() => {
    if (!loading.value && (!diagnosis.value || diagnosis.value.status !== 'processing')) {
      clearInterval(detailInterval)
      return
    }
    currentFunFactIndex.value = (currentFunFactIndex.value + 1) % processDetails.length
  }, 4000) // 4秒ごとに変更
}

onMounted(() => {
  console.log('🔥 PreviewView マウント開始', { diagnosisId: diagnosisId.value })
  loadDiagnosis()
  loadTemplateSettings()
  // startLoadingAnimationはwatchで呼ぶように変更
  console.log('🔥 PreviewView マウント完了')
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
// diagnosis-templates.scss は App.vue でグローバル読み込み済み

.diagnosis-meta {
  text-align: right;
  margin-bottom: 1px;
  padding: 8px 0;

  .meta-item {
    font-size: 0.85rem;
    color: var(--text-secondary);
    opacity: 0.8;
  }
}

.preview {
  @include page-container;
}

.page-header {
  @include page-header;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;

  .page-title {
    @include page-title;
  }

  p {
    @include small-text;
    margin: 0;
  }

  .diagnosis-datetime {
    @include small-text;
    margin: 16px 0 0 0;
    text-align: right;
    opacity: 0.8;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;

  &.btn-primary {
    background: var(--primary-main);
    color: white;

    &:hover:not(:disabled) {
      background: var(--primary-dark);
    }

    &:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
  }

  &.btn-secondary {
    background: #f5f5f5;
    color: var(--text-primary);
    border: 1px solid #ddd;

    &:hover {
      background: #e9e9e9;
    }
  }

  &.btn-admin {
    background: #6c757d;
    color: white;
    border: 1px solid #6c757d;

    &:hover {
      background: #5a6268;
    }

    &.active {
      background: #dc3545;
      border-color: #dc3545;

      &:hover {
        background: #c82333;
      }
    }
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  text-align: center;
  padding: 40px 20px;
}

.loading-content {
  max-width: 500px;
  width: 100%;
}

// 姓名判断セクション用のスタイル（共通CSSファイルにて定義）

// 総評メッセージのスタイル
.sohyo-message {
  margin-top: 16px;
  padding: 16px;
  background: #e8f4fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;

  p {
    margin: 0;
    color: #1976d2;
    font-size: 0.95rem;
    line-height: 1.5;
  }
}

// 文字による鑑定、文字表、結果表示などのスタイル（共通CSSファイルにて定義）

.section-spacing {
  margin-top: 20px;
}

.section-spacing-large {
  margin-top: 40px;
}

.appraisal-results {
  .appraisal-item {
    background: white;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 12px;

    .appraisal-type {
      font-size: 0.9rem;
      font-weight: bold;
      color: var(--primary-main);
      margin-bottom: 1px;
    }

    .appraisal-content {
      font-size: 0.9rem;
      color: var(--text-primary);
      line-height: 1.5;
    }
  }
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(52, 152, 219, 0.2);
  border-top: 4px solid var(--primary-main);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin: 0 auto 30px;
}

.loading-text {
  h2 {
    color: var(--primary-main);
    margin: 0 0 16px 0;
    font-size: 1.5rem;
  }

  p {
    color: var(--text-secondary);
    margin: 0 0 30px 0;
    font-size: 1rem;
  }
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
  gap: 20px;

  .step {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    opacity: 0.4;
    transition: all 0.3s ease;

    &.active {
      opacity: 1;
      transform: scale(1.05);
    }

    .step-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--background-default);
      border: 2px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      margin-bottom: 1px;
      transition: all 0.3s ease;
    }

    &.active .step-icon {
      background: var(--primary-main);
      border-color: var(--primary-main);
      color: white;
      box-shadow: 0 0 10px rgba(52, 152, 219, 0.3);
    }

    .step-text {
      font-size: 0.875rem;
      color: var(--text-secondary);
      text-align: center;
    }

    &.active .step-text {
      color: var(--primary-main);
      font-weight: 500;
    }
  }
}

.loading-tip {
  color: var(--text-disabled);
  font-size: 0.875rem;
}

.error-container, .no-data-container {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);

  h3 {
    color: var(--text-primary);
    margin-bottom: 16px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.processing-banner {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(155, 89, 182, 0.1));
  border: 2px solid var(--primary-main);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--shadow-1);

  .processing-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .processing-spinner {
    width: 24px;
    height: 24px;
    border: 3px solid rgba(52, 152, 219, 0.3);
    border-top: 3px solid var(--primary-main);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    flex-shrink: 0;
  }

  .processing-text {
    h3 {
      margin: 0 0 8px 0;
      color: var(--primary-main);
      font-size: 1.1rem;
    }

    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 0.9rem;
    }
  }
}

.error-container {
  color: #d32f2f;
}

.diagnosis-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// card, info-grid, info-item, nine-star-grid, zodiac-grid, stroke-grid等（共通CSSファイルにて定義）

.age-info {
  text-align: center;
  padding: 20px;

  .age-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-main);
  }
}

// name-info（共通CSSファイルにて定義）

.interpretation-content {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);

  p {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.raw-data {
  margin-top: 24px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;

  summary {
    padding: 12px;
    background: #f5f5f5;
    cursor: pointer;
    font-weight: 500;
    color: var(--text-secondary);
    border-radius: 6px 6px 0 0;

    &:hover {
      background: #ebebeb;
    }
  }

  pre {
    margin: 0;
    padding: 16px;
    background: #f9f9f9;
    font-size: 12px;
    line-height: 1.4;
    color: #666;
    overflow-x: auto;
    border-radius: 0 0 6px 6px;
  }
}

/* 鑑定士コメント入力セクションのスタイル */
.appraiser-comment-section {
  .card-header {
    p {
      margin: 8px 0 0;
      font-size: 0.9rem;
      color: var(--text-secondary);
    }
  }

  .appraiser-comment-input {
    width: 100%;
    padding: 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.5;
    resize: vertical;
    font-family: inherit;

    &:focus {
      outline: none;
      border-color: var(--primary-main);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    &::placeholder {
      color: #aaa;
    }
  }

  .comment-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;

    .btn {
      min-width: 120px;
    }

    .char-count {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
  }
}

/* テンプレート設定パネルのスタイル */
.template-panel {
  .card-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;

    h2 {
      color: white;
      margin: 0 0 8px;
    }

    p {
      margin: 0;
      opacity: 0.9;
    }
  }

  .alert {
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 14px;
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
    font-size: 16px;
  }

  .template-form {
    .form-group {
      margin-bottom: 20px;

      label {
        display: block;
        margin-bottom: 6px;
        font-weight: 600;
        color: #374151;
        font-size: 14px;
      }

      input, select, textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        transition: border-color 0.2s, box-shadow 0.2s;

        &:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }

      textarea {
        resize: vertical;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 13px;
        line-height: 1.4;
      }

      select {
        cursor: pointer;
      }
    }

    .form-actions {
      display: flex;
      gap: 12px;
      margin-top: 24px;
      flex-wrap: wrap;

      .btn {
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        border: none;

        &.btn-primary {
          background: #3b82f6;
          color: white;

          &:hover:not(:disabled) {
            background: #2563eb;
          }

          &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }
        }

        &.btn-secondary {
          background: #6b7280;
          color: white;

          &:hover:not(:disabled) {
            background: #4b5563;
          }
        }

        &.btn-outline {
          background: transparent;
          color: #6b7280;
          border: 1px solid #d1d5db;

          &:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
          }
        }
      }
    }
  }
}

.progress-bar-container {
  margin: 20px 0 30px;

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #e0e0e0;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 1px;

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary-main), var(--primary-light));
      border-radius: 20px;
      transition: width 0.5s ease;
    }
  }

  .progress-percentage {
    text-align: center;
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-weight: 500;
  }
}

@media (max-width: 768px) {
  .preview {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;

    .action-buttons {
      justify-content: center;
    }
  }

  // レスポンシブ対応（共通CSSファイルにて定義）

  .btn {
    flex: 1;
  }

  .constellation-spinner {
    width: 80px;
    height: 80px;

    .star {
      width: 6px;
      height: 6px;

      &.star-9 {
        width: 8px;
        height: 8px;
      }
    }
  }

  .progress-steps-enhanced {
    .step-card {
      padding: 16px;

      .step-title {
        font-size: 1rem;
      }

      .step-description {
        font-size: 0.85rem;
      }
    }
  }
}

// シンプルなローディング画面スタイル
.time-estimate {
  margin: 15px 0;
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.loading-dots {
  margin-top: 20px;
  font-size: 16px;
  color: #666;

  .dots::after {
    content: '...';
    animation: dots 1.5s infinite;
  }
}

@keyframes dots {
  0%, 20% {
    color: transparent;
    text-shadow: .25em 0 0 transparent, .5em 0 0 transparent;
  }
  40% {
    color: #666;
    text-shadow: .25em 0 0 transparent, .5em 0 0 transparent;
  }
  60% {
    text-shadow: .25em 0 0 #666, .5em 0 0 transparent;
  }
  80%, 100% {
    text-shadow: .25em 0 0 #666, .5em 0 0 #666;
  }
}

// テンプレート関連スタイル（共通CSSファイルにて定義）
</style>