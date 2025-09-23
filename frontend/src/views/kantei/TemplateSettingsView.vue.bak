<template>
  <MainLayout>
    <div class="template-settings">
      <div class="page-header">
        <h1 class="page-title">
          <img src="/src/assets/icons/template.svg" alt="テンプレート設定" class="page-title-icon" />
          テンプレート設定
        </h1>
        <p class="page-subtitle">デザインパターン比較ページで設定を行ってください</p>
      </div>

      <div class="redirect-notice">
        <div class="notice-card">
          <h2>設定画面が移動しました</h2>
          <p>すべてのテンプレート設定は「デザインパターン比較」ページで大きなプレビューを見ながら行えるようになりました。</p>

          <div class="features">
            <h3>設定可能な項目：</h3>
            <ul>
              <li>✅ デザインパターン選択</li>
              <li>✅ テーマカラー選択</li>
              <li>✅ 事業者名・鑑定士名設定</li>
              <li>✅ フォント設定</li>
              <li>✅ 文字サイズ設定</li>
              <li>✅ ロゴアップロード</li>
            </ul>
          </div>

          <div class="action-buttons">
            <button @click="goToDesignPatterns" class="primary-btn">
              デザインパターン比較ページに移動
            </button>
            <button @click="goToDashboard" class="secondary-btn">
              ダッシュボードに戻る
            </button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'

const router = useRouter()

const goToDesignPatterns = () => {
  router.push('/kantei/design-patterns')
}

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.template-settings {
  @include page-container;
}

.page-header {
  @include page-header;
  margin-bottom: 2rem;

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
    color: var(--text-secondary);
  }
}

.redirect-notice {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.notice-card {
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  max-width: 600px;
  text-align: center;

  h2 {
    color: var(--primary-main);
    font-size: 1.8rem;
    font-weight: 600;
    margin: 0 0 24px 0;
  }

  p {
    color: var(--text-secondary);
    font-size: 1.1rem;
    line-height: 1.6;
    margin: 0 0 32px 0;
  }

  .features {
    text-align: left;
    margin: 32px 0;
    padding: 24px;
    background: #f8f9fa;
    border-radius: 12px;

    h3 {
      color: var(--text-primary);
      font-size: 1.2rem;
      font-weight: 600;
      margin: 0 0 16px 0;
    }

    ul {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;

    .primary-btn {
      background: linear-gradient(135deg, var(--primary-main), var(--primary-dark));
      color: white;
      border: none;
      padding: 16px 32px;
      border-radius: 12px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 4px 16px rgba(52, 152, 219, 0.3);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(52, 152, 219, 0.4);
      }

      &:active {
        transform: translateY(0);
      }
    }

    .secondary-btn {
      background: white;
      color: var(--primary-main);
      border: 2px solid var(--primary-main);
      padding: 14px 32px;
      border-radius: 12px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: var(--primary-main);
        color: white;
        transform: translateY(-2px);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}

// レスポンシブ対応
@media (max-width: 768px) {
  .notice-card {
    padding: 32px 24px;
    margin: 16px;

    .action-buttons {
      flex-direction: column;

      .primary-btn,
      .secondary-btn {
        width: 100%;
      }
    }
  }
}
</style>