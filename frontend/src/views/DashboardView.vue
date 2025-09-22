<template>
  <MainLayout>
    <div class="dashboard">
      <div class="page-header">
        <h1 class="page-title">
          <img src="/src/assets/icons/dashboard.svg" alt="ダッシュボード" class="page-title-icon" />
          ダッシュボード
        </h1>
        <p class="page-subtitle">概況と重要な情報をご確認ください</p>
      </div>

      <!-- グローバルエラー表示 -->
      <ErrorMessage
        v-if="hasError"
        :message="error?.message || 'エラーが発生しました'"
        :retryable="error?.retryable || false"
        :show-retry="true"
        @retry="retryLoad"
        dismissible
        @dismiss="clearError"
      />

      <!-- グローバルローディング -->
      <LoadingIndicator
        v-if="isLoading"
        type="spinner"
        variant="card"
        :message="loading?.message"
      />

      <div v-if="!isLoading && !hasError" class="dashboard-grid">
        <!-- 統計カード -->
        <div class="card stats-card">
          <div class="card-header">
            <div class="card-title">今月の鑑定実績</div>
          </div>
          <div class="card-body">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ stats.thisMonth.completed }}</div>
                <div class="stat-label">鑑定書作成数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.thisMonth.downloads }}</div>
                <div class="stat-label">PDF出力数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.thisMonth.clients }}</div>
                <div class="stat-label">お客様数</div>
              </div>
            </div>
          </div>
        </div>

        <!-- クイックアクション -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">クイックアクション</div>
          </div>
          <div class="card-body">
            <div class="quick-actions">
              <router-link to="/kantei/new" class="action-btn btn-primary">
                <span class="material-icons">description</span>
                <span>新しい鑑定書作成</span>
              </router-link>
              <router-link to="/kantei/list" class="action-btn btn-secondary">
                <span class="material-icons">history</span>
                <span>鑑定履歴を見る</span>
              </router-link>
              <router-link to="/kantei/templates" class="action-btn btn-secondary">
                <span class="material-icons">palette</span>
                <span>テンプレート設定</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- 最近の鑑定 -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">最近の鑑定</div>
            <router-link to="/kantei/list" class="text-link">すべて見る</router-link>
          </div>
          <div class="card-body">
            <div v-if="isLoading" class="loading-state">
              <div class="loading-spinner"></div>
              <span>データを読み込み中...</span>
            </div>
            <div v-else-if="recentKantei.length === 0" class="empty-state">
              <span class="material-icons">description</span>
              <p>まだ鑑定記録がありません</p>
              <router-link to="/kantei/new" class="btn btn-primary">最初の鑑定を作成</router-link>
            </div>
            <div v-else class="kantei-list">
              <div
                v-for="kantei in recentKantei"
                :key="kantei.id"
                class="kantei-item"
              >
                <div class="kantei-info">
                  <div class="kantei-name">{{ kantei.client_name }}</div>
                  <div class="kantei-date">{{ formatDate(kantei.created_at) }}</div>
                </div>
                <div class="kantei-status">
                  <span class="badge" :class="getBadgeClass(kantei.status)">
                    {{ getStatusText(kantei.status) }}
                  </span>
                </div>
                <div class="kantei-actions">
                  <button class="icon-btn" @click="viewKantei(kantei.id)">
                    <span class="material-icons">visibility</span>
                  </button>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { apiClient } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'

const router = useRouter()
const { error, loading, hasError, isLoading, withErrorHandling, retry, clearError } = useErrorHandler()

// 状態
const stats = ref({
  thisMonth: {
    completed: 0,
    downloads: 0,
    clients: 0
  }
})

// 最近の鑑定データ
const recentKantei = ref([])


// 日付フォーマット
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// ステータスに応じたバッジクラス
const getBadgeClass = (status: string): string => {
  switch (status) {
    case 'completed': return 'badge-success'
    case 'pending': return 'badge-warning'
    case 'failed': return 'badge-error'
    default: return 'badge-primary'
  }
}

// ステータステキスト
const getStatusText = (status: string): string => {
  switch (status) {
    case 'completed': return '完了'
    case 'pending': return '処理中'
    case 'failed': return 'エラー'
    default: return '不明'
  }
}

// 鑑定詳細表示
const viewKantei = (id: number) => {
  router.push(`/kantei/preview/${id}`)
}



// データ読み込み関数
const loadDashboardData = async () => {
  const result = await withErrorHandling(async () => {
    // 鑑定履歴を取得
    const diagnosesResponse = await apiClient.listDiagnoses()
    const diagnoses = diagnosesResponse.diagnoses || []

    // 最近の鑑定（最新5件）
    recentKantei.value = diagnoses
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5)

    // 今月の統計を計算
    const now = new Date()
    const thisMonth = diagnoses.filter(d => {
      const createdDate = new Date(d.created_at)
      return createdDate.getMonth() === now.getMonth() &&
             createdDate.getFullYear() === now.getFullYear()
    })

    const completedThisMonth = thisMonth.filter(d => d.status === 'completed')

    // ユニークなお客様数を計算
    const uniqueClients = new Set(completedThisMonth.map(d => d.client_name)).size

    stats.value = {
      thisMonth: {
        completed: completedThisMonth.length,
        downloads: Math.floor(completedThisMonth.length * 0.8), // 仮: 完了数の80%がダウンロード
        clients: uniqueClients
      }
    }

    return true
  }, {
    loadingMessage: 'ダッシュボードデータを読み込み中...',
    retryCount: 2
  })

  return result
}

// リトライ処理
const retryLoad = async () => {
  await retry(loadDashboardData)
}

// マウント時の処理
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.dashboard {
  @include page-container;
}

.card {
  @include card;

  .card-body {
    padding: 16px 20px;
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

.dashboard-grid {
  @include responsive-grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px 12px;
  background: var(--background-elegant);
  border-radius: var(--radius-elegant-sm);
  border: 1px solid rgba(222, 226, 230, 0.6);
  transition: all var(--transition-elegant);
  box-shadow: var(--shadow-elegant);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(44, 62, 80, 0.08);
  }

  .stat-value {
    font-size: var(--font-size-2xl);
    font-weight: 300;
    color: var(--primary-main);
    line-height: var(--line-height-tight);
    margin-bottom: 4px;
  }

  .stat-label {
    @include form-label;
  }
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  text-decoration: none;
  gap: var(--spacing-sm);

  .material-icons {
    font-size: 20px;
  }

  &.btn-primary {
    @include button-primary;
  }

  &.btn-secondary {
    @include button-secondary;
  }
}


.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--background-paper);
  border-bottom: 1px solid var(--border-color);

  .card-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 500;
    color: var(--text-primary);
  }

  .text-link {
    color: var(--primary-main);
    font-size: var(--font-size-sm);
    text-decoration: none;
    font-weight: $font-weight-medium;

    &:hover {
      text-decoration: underline;
    }
  }
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--text-secondary);

  .loading-spinner {
    margin-right: 12px;
  }
}

.empty-state {
  text-align: center;
  padding: 32px;

  .material-icons {
    font-size: 48px;
    color: var(--text-disabled);
    margin-bottom: 16px;
  }

  p {
    color: var(--text-secondary);
    margin-bottom: 16px;
  }
}

.kantei-list {
  .kantei-item {
    display: flex;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s ease;

    &:hover {
      background-color: var(--background-paper);
    }

    &:last-child {
      border-bottom: none;
    }

    .kantei-info {
      flex: 1;

      .kantei-name {
        @include body-text;
        font-weight: $font-weight-medium;
        margin-bottom: var(--spacing-xs);
      }

      .kantei-date {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
      }
    }

    .kantei-status {
      margin-right: 16px;
    }

    .kantei-actions {
      .icon-btn {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 8px;
        border-radius: var(--border-radius);
        transition: all 0.2s ease;

        &:hover {
          background-color: var(--background-default);
          color: var(--text-primary);
        }

        .material-icons {
          font-size: 18px;
        }
      }
    }
  }
}

.notice-list {
  .notice-item {
    display: flex;
    align-items: flex-start;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
    gap: 8px;

    &:last-child {
      border-bottom: none;
    }

    .notice-icon {
      margin-top: 1px;

      .material-icons {
        font-size: 16px;
      }
    }

    .notice-content {
      flex: 1;

      &.clickable {
        cursor: pointer;
        border-radius: 4px;
        padding: 4px;
        margin: -4px;
        transition: background-color 0.2s ease;

        &:hover {
          background-color: rgba(52, 73, 94, 0.05);
        }
      }

      .notice-title {
        @include form-label;
        margin-bottom: 2px;
      }

      .notice-text {
        @include small-text;
        margin-bottom: 2px;
        font-size: 0.75rem;
        line-height: 1.3;
      }

      .notice-date {
        font-size: 0.7rem;
        color: var(--text-disabled);
      }
    }

    .notice-link {
      .external-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        transition: background-color 0.2s ease;
        color: var(--text-secondary);
        text-decoration: none;

        &:hover {
          background-color: var(--background-default);
          color: var(--primary-main);
        }

        .material-icons {
          font-size: 14px;
        }
      }
    }
  }
}

// レスポンシブ
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .kantei-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;

    .kantei-status,
    .kantei-actions {
      margin: 0;
    }
  }
}
</style>