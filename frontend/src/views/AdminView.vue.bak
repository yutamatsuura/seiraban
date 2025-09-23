<template>
  <MainLayout>
    <div class="admin">
      <div class="page-header">
        <h1 class="page-title">
          <img src="/src/assets/icons/admin-settings.svg" alt="管理者ページ" class="page-title-icon" />
          管理者ページ
        </h1>
        <p class="page-subtitle">ユーザー管理・アクセス制御・アカウント管理</p>
      </div>


      <div class="tab-content">
        <div class="section-header">
          <button @click="showAddUserModal = true" class="btn btn-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            ユーザー追加
          </button>
        </div>

        <!-- 検索・フィルタ -->
        <div class="filters">
          <div class="filter-group">
            <input
              v-model="userFilters.search"
              type="text"
              placeholder="名前・メールで検索"
              class="search-input"
            />
          </div>
          <div class="filter-group">
            <select v-model="userFilters.status" class="filter-select">
              <option value="">全てのステータス</option>
              <option value="active">有効</option>
              <option value="inactive">無効</option>
              <option value="suspended">停止</option>
            </select>
          </div>
          <div class="filter-group">
            <select v-model="userFilters.subscription" class="filter-select">
              <option value="">全てのプラン</option>
              <option value="free">無料</option>
              <option value="basic">ベーシック</option>
              <option value="premium">プレミアム</option>
            </select>
          </div>
        </div>

        <!-- ユーザー一覧 -->
        <div class="card">
          <div class="user-table-container">
            <table class="user-table">
              <thead>
                <tr>
                  <th>ユーザー</th>
                  <th>メール</th>
                  <th>登録日</th>
                  <th>ステータス</th>
                  <th>プラン</th>
                  <th>最終ログイン</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
                  <td>
                    <div class="user-info">
                      <div class="user-avatar">{{ user.display_name[0] }}</div>
                      <div class="user-details">
                        <div class="user-name">{{ user.display_name }}</div>
                        <div class="user-id">ID: {{ user.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td>{{ user.email }}</td>
                  <td>{{ formatDate(user.created_at) }}</td>
                  <td>
                    <span class="badge" :class="getStatusBadgeClass(user.status)">
                      {{ getStatusText(user.status) }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getSubscriptionBadgeClass(user.subscription_plan)">
                      {{ getSubscriptionText(user.subscription_plan) }}
                    </span>
                  </td>
                  <td>{{ formatDate(user.last_login) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button @click="editUser(user)" class="btn-icon" title="編集">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                      </button>
                      <button @click="toggleUserStatus(user)" class="btn-icon" title="ステータス切替">
                        <svg v-if="user.status === 'active'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <polygon points="5,3 19,12 5,21"/>
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <rect x="6" y="4" width="4" height="16"/>
                          <rect x="14" y="4" width="4" height="16"/>
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <!-- ユーザー追加モーダル -->
    <div v-if="showAddUserModal" class="modal-overlay" @click="showAddUserModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>新規ユーザー追加</h3>
          <button @click="showAddUserModal = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addUser" class="user-form">
            <div class="form-group">
              <label class="form-label">表示名</label>
              <input
                v-model="newUser.display_name"
                type="text"
                class="form-input"
                placeholder="表示名を入力"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">メールアドレス</label>
              <input
                v-model="newUser.email"
                type="email"
                class="form-input"
                placeholder="メールアドレスを入力"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">初期パスワード</label>
              <input
                v-model="newUser.password"
                type="password"
                class="form-input"
                placeholder="初期パスワードを入力"
                required
                minlength="8"
              />
            </div>
            <div class="form-group">
              <label class="form-label">サブスクリプションプラン</label>
              <select v-model="newUser.subscription_plan" class="form-select" required>
                <option value="free">無料</option>
                <option value="basic">ベーシック</option>
                <option value="premium">プレミアム</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" @click="showAddUserModal = false" class="btn btn-secondary">
                キャンセル
              </button>
              <button type="submit" class="btn btn-primary" :disabled="addingUser">
                <span v-if="addingUser">追加中...</span>
                <span v-else>ユーザー追加</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import MainLayout from '@/components/layout/MainLayout.vue'

// タブ定義

const users = ref([])
const userFilters = reactive({
  search: '',
  status: '',
  subscription: ''
})

const showAddUserModal = ref(false)
const addingUser = ref(false)

const newUser = reactive({
  display_name: '',
  email: '',
  password: '',
  subscription_plan: 'free'
})



// フィルタされたユーザー一覧
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchSearch = !userFilters.search ||
      user.display_name.toLowerCase().includes(userFilters.search.toLowerCase()) ||
      user.email.toLowerCase().includes(userFilters.search.toLowerCase())

    const matchStatus = !userFilters.status || user.status === userFilters.status
    const matchSubscription = !userFilters.subscription || user.subscription_plan === userFilters.subscription

    return matchSearch && matchStatus && matchSubscription
  })
})

// ユーザー追加
const addUser = async () => {
  try {
    addingUser.value = true

    // TODO: API呼び出しを実装
    // const response = await apiClient.createUser(newUser)

    // 仮の処理
    await new Promise(resolve => setTimeout(resolve, 1000))

    const newUserData = {
      id: `user_${Date.now()}`,
      display_name: newUser.display_name,
      email: newUser.email,
      status: 'active',
      subscription_plan: newUser.subscription_plan,
      created_at: new Date().toISOString(),
      last_login: null
    }

    users.value.push(newUserData)

    // フォームリセット
    Object.assign(newUser, {
      display_name: '',
      email: '',
      password: '',
      subscription_plan: 'free'
    })

    showAddUserModal.value = false
  } catch (error) {
    console.error('Add user error:', error)
  } finally {
    addingUser.value = false
  }
}

// ユーザー編集
const editUser = (user) => {
  // TODO: 編集モーダルを実装
  console.log('Edit user:', user)
}

// ユーザーステータス切替
const toggleUserStatus = async (user) => {
  try {
    const newStatus = user.status === 'active' ? 'inactive' : 'active'

    // TODO: API呼び出しを実装
    // await apiClient.updateUserStatus(user.id, newStatus)

    user.status = newStatus
  } catch (error) {
    console.error('Toggle user status error:', error)
  }
}


// データ読み込み
const loadUsers = async () => {
  try {
    // TODO: API呼び出しを実装
    // const response = await apiClient.getUsers()

    // 仮のデータ
    users.value = [
      {
        id: 'user_1',
        display_name: 'テストユーザー1',
        email: 'test1@example.com',
        status: 'active',
        subscription_plan: 'premium',
        created_at: '2024-01-15T00:00:00Z',
        last_login: '2024-12-01T10:30:00Z'
      },
      {
        id: 'user_2',
        display_name: 'テストユーザー2',
        email: 'test2@example.com',
        status: 'active',
        subscription_plan: 'basic',
        created_at: '2024-02-20T00:00:00Z',
        last_login: '2024-11-28T15:45:00Z'
      },
      {
        id: 'user_3',
        display_name: 'テストユーザー3',
        email: 'test3@example.com',
        status: 'inactive',
        subscription_plan: 'free',
        created_at: '2024-03-10T00:00:00Z',
        last_login: '2024-10-15T08:20:00Z'
      }
    ]
  } catch (error) {
    console.error('Load users error:', error)
  }
}



// ユーティリティ関数
const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`
}

const formatDateTime = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return `${formatDate(dateString)} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'active': return 'badge-success'
    case 'inactive': return 'badge-warning'
    case 'suspended': return 'badge-error'
    default: return 'badge-secondary'
  }
}

const getStatusText = (status: string): string => {
  switch (status) {
    case 'active': return '有効'
    case 'inactive': return '無効'
    case 'suspended': return '停止'
    default: return '不明'
  }
}

const getSubscriptionBadgeClass = (plan: string): string => {
  switch (plan) {
    case 'premium': return 'badge-primary'
    case 'basic': return 'badge-info'
    case 'free': return 'badge-secondary'
    default: return 'badge-secondary'
  }
}

const getSubscriptionText = (plan: string): string => {
  switch (plan) {
    case 'premium': return 'プレミアム'
    case 'basic': return 'ベーシック'
    case 'free': return '無料'
    default: return '不明'
  }
}

// マウント時の処理
onMounted(() => {
  loadUsers()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.admin {
  @include page-container;
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


.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border: none;
    border-radius: var(--border-radius);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;

    &.btn-primary {
      background-color: var(--primary-main);
      color: white;

      svg {
        width: 16px;
        height: 16px;
        stroke-width: 2;
      }

      &:hover {
        background-color: var(--primary-dark);
      }
    }
  }
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--background-paper);
  border-radius: var(--border-radius);

  .filter-group {
    flex: 1;
    max-width: 200px;
  }

  .search-input,
  .filter-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 0.9rem;

    &:focus {
      outline: none;
      border-color: var(--primary-main);
    }
  }
}

.user-table-container {
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
  }

  th {
    background: var(--background-default);
    font-weight: 600;
    color: var(--text-primary);
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;

    .user-avatar {
      width: 40px;
      height: 40px;
      background: var(--primary-main);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
    }

    .user-details {
      .user-name {
        font-weight: 500;
        color: var(--text-primary);
      }

      .user-id {
        font-size: 0.8rem;
        color: var(--text-secondary);
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 8px;

    .btn-icon {
      background: none;
      border: none;
      padding: 4px;
      cursor: pointer;
      border-radius: 4px;
      transition: background 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;

      svg {
        width: 16px;
        height: 16px;
        stroke-width: 2;
      }

      &:hover {
        background: var(--background-default);
      }
    }
  }
}




.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;

  &.badge-success {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4caf50;
  }

  &.badge-warning {
    background-color: rgba(255, 152, 0, 0.1);
    color: #ff9800;
  }

  &.badge-error {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
  }

  &.badge-primary {
    background-color: rgba(52, 73, 94, 0.1);
    color: var(--primary-main);
  }

  &.badge-info {
    background-color: rgba(33, 150, 243, 0.1);
    color: #2196f3;
  }

  &.badge-secondary {
    background-color: rgba(158, 158, 158, 0.1);
    color: #9e9e9e;
  }
}

// モーダル
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--background-paper);
  border-radius: var(--border-radius);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid var(--border-color);

    h3 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .modal-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: var(--text-secondary);

      &:hover {
        color: var(--text-primary);
      }
    }
  }

  .modal-body {
    padding: 20px;
  }
}

.user-form {
  .form-group {
    margin-bottom: 16px;

    .form-label {
      display: block;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .form-input,
    .form-select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius);
      font-size: 1rem;

      &:focus {
        outline: none;
        border-color: var(--primary-main);
      }
    }
  }

  .form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: var(--border-radius);
      font-weight: 500;
      cursor: pointer;

      &.btn-secondary {
        background: var(--background-default);
        color: var(--text-primary);
        border: 1px solid var(--border-color);

        &:hover {
          background: var(--background-paper);
        }
      }

      &.btn-primary {
        background: var(--primary-main);
        color: white;

        &:hover:not(:disabled) {
          background: var(--primary-dark);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }
    }
  }
}


// レスポンシブ対応
@media (max-width: 768px) {
  .filters {
    flex-direction: column;

    .filter-group {
      max-width: none;
    }
  }


  .user-table {
    font-size: 0.9rem;

    th,
    td {
      padding: 8px;
    }
  }
}
</style>