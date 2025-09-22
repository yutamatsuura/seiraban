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
        <button
          @click="generatePDF"
          :disabled="loading || !diagnosis"
          class="btn btn-primary"
        >
          <span v-if="pdfGenerating">PDF生成中...</span>
          <span v-else>PDF生成</span>
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

    <!-- Loading or Processing State -->
    <div v-if="loading || (diagnosis && diagnosis.status === 'processing')" class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <div class="loading-text">
          <h2>鑑定を実行中です</h2>
          <p v-if="diagnosis">{{ diagnosis.client_name }} 様の鑑定結果を計算しています...</p>

          <!-- プログレスバー -->
          <div class="progress-bar-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: Math.round(progressPercentage) + '%' }"></div>
            </div>
            <div class="progress-percentage">{{ Math.round(progressPercentage) }}%</div>
          </div>
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
    <div v-else-if="diagnosis && diagnosis.status === 'completed'" class="diagnosis-content" id="diagnosis-report">

      <!-- Client Information -->
      <div class="card client-info">
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
      <div v-if="diagnosis.kyusei_result" class="card kyusei-results">
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
      <div v-if="diagnosis.seimei_result" class="card seimei-results">
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
            <div class="section">
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


    </div>

    <!-- No Data State -->
    <div v-else class="no-data-container">
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
import type { DiagnosisResult } from '@/services/api-client'

const route = useRoute()
const router = useRouter()

const diagnosis = ref<DiagnosisResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const pdfGenerating = ref(false)
const autoRefreshTimer = ref<number | null>(null)
const stepProgress = ref(0)
const adminMode = ref(false)

// 新しい待機画面用の変数
const progressPercentage = ref(0)
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

const loadDiagnosis = async () => {
  if (!diagnosisId.value) {
    error.value = '鑑定IDが指定されていません'
    return
  }

  loading.value = true
  error.value = null

  try {
    const result = await apiClient.getDiagnosis(diagnosisId.value, adminMode.value)
    diagnosis.value = result

    // ステップ進行状況を更新
    updateStepProgress(result)
  } catch (err: any) {
    console.error('Failed to load diagnosis:', err)
    error.value = err.message || '鑑定データの読み込みに失敗しました'
  } finally {
    loading.value = false
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
      const fileUrl = `http://localhost:8502${response.pdf_url.replace('/tmp/pdf_storage', '/static')}`

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

const updateStepProgress = (result: DiagnosisResult) => {
  let progress = 0
  let step = 0

  // 九星気学が実際に完了していれば1ステップ進む
  if (result.kyusei_result && result.kyusei_result.data) {
    const kyuseiData = result.kyusei_result.data
    // 本命星が「計算中」や「未取得」でなければ完了とみなす
    if (kyuseiData.本命星 && kyuseiData.本命星 !== '計算中' && kyuseiData.本命星 !== '未取得') {
      progress = 1
      step = 1
      progressPercentage.value = 50
    }
  }

  // 姓名判断が実際に完了していれば2ステップ進む
  // 診断が完全に完了した時のみステップ2を表示
  if (result.status === 'completed' && result.seimei_result && result.seimei_result.data) {
    const seimeiData = result.seimei_result.data
    // 総評点数が存在すれば完了とみなす
    if (seimeiData.総評点数 !== undefined && seimeiData.総評点数 !== null && seimeiData.総評点数 !== '未取得') {
      progress = 2
      step = 2
      progressPercentage.value = 100
    }
  }

  stepProgress.value = progress
  currentStep.value = step
  console.log('Step progress updated:', progress, result)
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
  }, 3000) // 3秒ごとに更新
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

// 待機画面の開始処理
const startLoadingAnimation = () => {
  if (loading.value || (diagnosis.value && diagnosis.value.status === 'processing')) {
    startProgressSimulation()
    startCountdown()
    rotateProcessDetail()
  }
}

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
  }, 800)
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
  loadDiagnosis()
  startLoadingAnimation()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.diagnosis-meta {
  text-align: right;
  margin-bottom: 8px;
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

// 姓名判断セクション用のスタイル
.name-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;

  .name-display {
    .analyzed-name {
      font-size: 1.5rem;
      font-weight: bold;
      color: var(--text-primary);
    }
  }

  .score-display {
    display: flex;
    align-items: center;
    gap: 4px;

    .score-value {
      font-size: 2.5rem;
      font-weight: bold;
      color: var(--primary-main);
      line-height: 1;
    }

    .score-label {
      font-size: 1.2rem;
      color: var(--text-secondary);
      margin-top: 8px;
      align-self: flex-end;
    }
  }
}

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

// 文字による鑑定のスタイル
.character-evaluation-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.character-evaluation-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;

  .evaluation-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;

    .character-name {
      font-size: 1.1rem;
      font-weight: bold;
      color: var(--text-primary);
    }

    .evaluation-category {
      background: #007bff;
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.85rem;
      font-weight: 500;
    }
  }

  .evaluation-detail {
    color: var(--text-secondary);
    line-height: 1.6;
    font-size: 0.95rem;
  }
}

.section-spacing {
  margin-top: 20px;
}

.character-table {
  margin: 16px 0;

  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    th, td {
      padding: 12px 16px;
      text-align: center;
      border-bottom: 1px solid #e5e7eb;
    }

    th {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-weight: 600;
      font-size: 1.1rem;

      &:first-child {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
      }
    }

    td {
      color: var(--text-primary);
      font-weight: 500;

      &:first-child {
        background: #f8fafc;
        font-weight: 600;
        color: var(--text-secondary);
      }
    }

    tr:last-child td {
      border-bottom: none;
    }

    tr:hover {
      background: rgba(102, 126, 234, 0.05);
    }
  }
}

.result-content {
  display: flex;
  align-items: center;
  gap: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #cbd5e1;

  .score-section {
    display: flex;
    align-items: baseline;
    gap: 8px;
    min-width: 120px;

    .score-value {
      font-size: 3rem;
      font-weight: 700;
      color: #1e40af;
      line-height: 1;
    }

    .score-label {
      font-size: 1.2rem;
      color: #64748b;
      font-weight: 500;
    }
  }

  .message-section {
    flex: 1;

    p {
      margin: 0;
      font-size: 1rem;
      line-height: 1.6;
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;

  .character-item {
    background: white;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 12px;
    text-align: center;

    .char-label {
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .char-details {
      font-size: 0.9rem;
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.stroke-analysis {
  margin-bottom: 24px;

  .stroke-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 16px;

    .stroke-item {
      background: white;
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 12px;
      text-align: center;

      .stroke-type {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }

      .stroke-value {
        font-size: 1.1rem;
        font-weight: bold;
        color: var(--primary-main);
      }
    }
  }
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
      margin-bottom: 8px;
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
      margin-bottom: 8px;
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
  margin-bottom: 24px;
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

.card {
  @include card;

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
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
  }

  span {
    font-size: 16px;
    color: var(--text-primary);
    font-weight: 500;
  }
}

.section {
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 16px 0;
    font-size: 1.1rem;
    color: var(--text-primary);
    border-bottom: 2px solid var(--primary-main);
    padding-bottom: 8px;
  }
}

.nine-star-grid, .zodiac-grid, .stroke-grid, .direction-grid, .special-info-grid, .naon-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.star-item, .zodiac-item, .stroke-item, .direction-item, .special-info-item, .naon-item {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  text-align: center;

  label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  span {
    font-size: 16px;
    font-weight: bold;
    color: var(--text-primary);
  }

  .star-value {
    color: var(--primary-main);
    font-size: 18px;
  }
}

.age-info {
  text-align: center;
  padding: 20px;

  .age-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-main);
  }
}

.name-info {
  text-align: center;
  padding: 20px;

  .name-display {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    border: 2px solid var(--primary-light);

    .analyzed-name {
      font-size: 1.5rem;
      font-weight: bold;
      color: var(--text-primary);
      letter-spacing: 0.1em;
    }
  }
}

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


.progress-bar-container {
  margin: 20px 0 30px;

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #e0e0e0;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 8px;

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

  .info-grid, .nine-star-grid, .zodiac-grid, .stroke-grid, .direction-grid, .special-info-grid, .naon-info {
    grid-template-columns: 1fr;
  }

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
</style>