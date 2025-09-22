<template>
  <MainLayout>
    <div class="history">
    <div class="page-header">
      <h1>
        <img src="/src/assets/icons/document-list.svg" alt="鑑定履歴" class="page-title-icon" />
        鑑定履歴
      </h1>
      <p>過去の鑑定記録を確認できます</p>
    </div>

    <!-- エラーメッセージ -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- ローディング状態 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>鑑定履歴を読み込み中...</p>
    </div>

    <!-- 履歴が空の場合 -->
    <div v-else-if="!loading && diagnoses.length === 0" class="empty-state">
      <div class="empty-icon">
        <span class="material-icons">history</span>
      </div>
      <h3>鑑定履歴がありません</h3>
      <p>まだ鑑定を実行していません。新しい鑑定を開始してください。</p>
      <router-link to="/kantei/new" class="btn btn-primary">
        <span class="material-icons">add_circle</span>
        新規鑑定を開始
      </router-link>
    </div>

    <!-- 履歴一覧 -->
    <div v-else-if="!loading" class="history-content">
      <!-- フィルター・ソート -->
      <div class="controls">
        <div class="search-box">
          <span class="material-icons">search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="お客様名で検索..."
            class="search-input"
          />
        </div>
        <div class="filter-controls">
          <select v-model="statusFilter" class="filter-select">
            <option value="">すべての状態</option>
            <option value="completed">完了</option>
            <option value="processing">処理中</option>
            <option value="failed">失敗</option>
          </select>
          <select v-model="sortBy" class="filter-select">
            <option value="created_at_desc">作成日時（新しい順）</option>
            <option value="created_at_asc">作成日時（古い順）</option>
            <option value="client_name_asc">お客様名（あいうえお順）</option>
          </select>
        </div>
        <button @click="refreshList" class="btn btn-outline" :disabled="loading">
          <span class="material-icons">refresh</span>
          更新
        </button>
      </div>

      <!-- 診断件数 -->
      <div class="summary">
        <p>
          全 {{ filteredDiagnoses.length }} 件
          <span v-if="searchQuery || statusFilter">
            （{{ diagnoses.length }} 件中）
          </span>
        </p>
      </div>

      <!-- 履歴リスト -->
      <div class="history-list">
        <div
          v-for="diagnosis in paginatedDiagnoses"
          :key="diagnosis.id"
          class="history-item"
          :class="{ 'status-failed': diagnosis.status === 'failed' }"
        >
          <div class="item-header">
            <div class="client-info">
              <h3 class="client-name">{{ diagnosis.client_name }}</h3>
              <div class="diagnosis-meta">
                <span class="diagnosis-id">ID: {{ diagnosis.id.substring(0, 8) }}...</span>
                <span class="created-date">{{ formatDate(diagnosis.created_at) }}</span>
              </div>
            </div>
            <div class="status-badge" :class="`status-${diagnosis.status}`">
              {{ getStatusText(diagnosis.status) }}
            </div>
          </div>

          <div class="item-content">
            <div class="diagnosis-types">
              <span v-if="diagnosis.kyusei_result" class="type-badge kyusei">
                九星気学
              </span>
              <span v-if="diagnosis.seimei_result" class="type-badge seimei">
                姓名判断
              </span>
            </div>

            <div v-if="diagnosis.error_message" class="error-info">
              <span class="material-icons">error</span>
              {{ diagnosis.error_message }}
            </div>
          </div>

          <div class="item-actions">
            <router-link
              :to="`/kantei/preview/${diagnosis.id}`"
              class="btn btn-primary"
              :class="{ 'btn-disabled': diagnosis.status === 'failed' }"
            >
              <span class="material-icons">visibility</span>
              詳細を見る
            </router-link>
            <button
              v-if="diagnosis.status === 'completed'"
              @click="generatePDF(diagnosis.id)"
              class="btn btn-outline"
              :disabled="generatingPDF === diagnosis.id"
            >
              <span class="material-icons">picture_as_pdf</span>
              <span v-if="generatingPDF === diagnosis.id">生成中...</span>
              <span v-else>PDF出力</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ペジネーション -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn btn-outline"
        >
          <span class="material-icons">chevron_left</span>
          前へ
        </button>
        <span class="page-info">
          {{ currentPage }} / {{ totalPages }} ページ
        </span>
        <button
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn btn-outline"
        >
          次へ
          <span class="material-icons">chevron_right</span>
        </button>
      </div>
    </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient, type DiagnosisResult } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'

// データ状態
const diagnoses = ref<DiagnosisResult[]>([])
const loading = ref(false)
const errorMessage = ref('')
const generatingPDF = ref<string | null>(null)

// フィルター・ソート状態
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at_desc')

// ペジネーション状態
const currentPage = ref(1)
const itemsPerPage = 10

// 計算プロパティ
const filteredDiagnoses = computed(() => {
  let filtered = diagnoses.value

  // 検索フィルター
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(d =>
      d.client_name.toLowerCase().includes(query)
    )
  }

  // ステータスフィルター
  if (statusFilter.value) {
    filtered = filtered.filter(d => d.status === statusFilter.value)
  }

  // ソート
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'created_at_desc':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'created_at_asc':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      case 'client_name_asc':
        return a.client_name.localeCompare(b.client_name, 'ja')
      default:
        return 0
    }
  })

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredDiagnoses.value.length / itemsPerPage))

const paginatedDiagnoses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredDiagnoses.value.slice(start, end)
})

// ヘルパー関数
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '完了'
    case 'processing':
      return '処理中'
    case 'failed':
      return '失敗'
    default:
      return '不明'
  }
}

// API呼び出し関数
const loadDiagnoses = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await apiClient.listDiagnoses()
    diagnoses.value = response.diagnoses || []
  } catch (error: any) {
    errorMessage.value = error.message || '鑑定履歴の取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const refreshList = () => {
  currentPage.value = 1
  loadDiagnoses()
}

const generatePDF = async (diagnosisId: string) => {
  generatingPDF.value = diagnosisId

  try {
    const response = await apiClient.generatePDF(diagnosisId)
    if (response.success) {
      // PDFダウンロード処理（実装はPDF機能の詳細に依存）
      console.log('PDF generated:', response.pdf_url)
      // 実際の実装では、ダウンロードリンクを提供するか直接ダウンロードを開始
    }
  } catch (error: any) {
    errorMessage.value = `PDF生成に失敗しました: ${error.message}`
  } finally {
    generatingPDF.value = null
  }
}

// ライフサイクル
onMounted(() => {
  loadDiagnoses()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.history {
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

.empty-state {
  text-align: center;
  padding: 64px 20px;

  .empty-icon {
    .material-icons {
      font-size: 4rem;
      color: var(--text-disabled);
      margin-bottom: 16px;
    }
  }

  h3 {
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  p {
    color: var(--text-secondary);
    margin-bottom: 24px;
  }
}

.controls {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: center;

  .search-box {
    position: relative;
    flex: 1;
    min-width: 200px;

    .material-icons {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-disabled);
      font-size: 20px;
    }

    .search-input {
      width: 100%;
      padding: 12px 16px 12px 44px;
      border: 2px solid var(--border-color);
      border-radius: 6px;
      font-size: 1rem;
      background: white;

      &:focus {
        outline: none;
        border-color: var(--primary-main);
      }
    }
  }

  .filter-controls {
    display: flex;
    gap: 8px;
  }

  .filter-select {
    padding: 8px 12px;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    background: white;
    font-size: 0.875rem;

    &:focus {
      outline: none;
      border-color: var(--primary-main);
    }
  }
}

.summary {
  margin-bottom: 16px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: var(--shadow-2);
  }

  &.status-failed {
    border-left: 4px solid #e74c3c;
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;

    .client-info {
      .client-name {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 4px 0;
      }

      .diagnosis-meta {
        display: flex;
        gap: 12px;
        font-size: 0.75rem;
        color: var(--text-secondary);

        .diagnosis-id {
          font-family: monospace;
        }
      }
    }

    .status-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 500;

      &.status-completed {
        background: rgba(22, 160, 133, 0.1);
        color: #138d75;
      }

      &.status-processing {
        background: rgba(52, 152, 219, 0.1);
        color: #2980b9;
      }

      &.status-failed {
        background: rgba(231, 76, 60, 0.1);
        color: #c0392b;
      }
    }
  }

  .item-content {
    margin-bottom: 16px;

    .diagnosis-types {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;

      .type-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;

        &.kyusei {
          background: rgba(156, 39, 176, 0.1);
          color: #8e24aa;
        }

        &.seimei {
          background: rgba(255, 152, 0, 0.1);
          color: #f57c00;
        }
      }
    }

    .error-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #c0392b;
      font-size: 0.875rem;

      .material-icons {
        font-size: 16px;
      }
    }
  }

  .item-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;

  .page-info {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }
}

.btn {
  padding: 8px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.btn-primary {
    background: var(--primary-main);
    color: white;

    &:hover:not(:disabled) {
      background: var(--primary-dark);
    }

    &.btn-disabled {
      background: var(--text-disabled);
      cursor: not-allowed;
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
    font-size: 18px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// レスポンシブ
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;

    .search-box {
      min-width: auto;
    }

    .filter-controls {
      flex-direction: column;
    }
  }

  .history-item {
    .item-header {
      flex-direction: column;
      gap: 8px;
    }

    .item-actions {
      flex-direction: column;
    }
  }

  .pagination {
    flex-direction: column;
    gap: 8px;
  }
}
</style>