# E2Eテスト環境設定

## 概要

このドキュメントでは、運命織アプリケーションのE2Eテスト環境構成について説明します。PlaywrightとTypeScriptを使用した包括的なテスト環境が構築されています。

## 環境構成

### ディレクトリ構造

```
tests/
├── playwright.config.ts          # Playwright設定ファイル
├── package.json                  # テスト環境用パッケージ定義
├── e2e/                         # E2Eテストファイル
│   ├── auth/                    # 認証関連テスト
│   ├── pages/                   # ページ固有テスト
│   ├── workflows/               # ワークフローテスト
│   └── fixtures/                # テストフィクスチャ
├── helpers/                     # 共通ヘルパー関数
│   └── auth.ts                  # 認証ヘルパー
└── reports/                     # テストレポート出力先
```

### 主要な設定

#### Playwright設定 (`playwright.config.ts`)

- **テストディレクトリ**: `./e2e`
- **ベースURL**: `http://localhost:5173`（Vite開発サーバー）
- **タイムアウト**: 30秒
- **レポート**: HTML、JSON、Line形式で出力
- **スクリーンショット**: テスト失敗時のみ
- **動画録画**: テスト失敗時のみ
- **トレース**: 再試行時に記録

#### サポートブラウザ

- **Desktop**: Chrome、Firefox、Safari
- **Mobile**: Mobile Chrome（Pixel 5）、Mobile Safari（iPhone 12）

### 認証システム

#### テストユーザー

環境変数またはデフォルト値で設定されたテストユーザーを使用：

- **一般ユーザー**:
  - Email: `TEST_USER_EMAIL` または `test@example.com`
  - Password: `TEST_USER_PASSWORD` または `testpass123`

- **管理者ユーザー**:
  - Email: `TEST_ADMIN_EMAIL` または `admin@example.com`
  - Password: `TEST_ADMIN_PASSWORD` または `adminpass123`

#### 認証ヘルパー関数

`helpers/auth.ts`で提供される主要な関数：

- `login()`: 汎用ログイン処理
- `loginAsUser()`: 一般ユーザーログイン
- `loginAsAdmin()`: 管理者ログイン
- `logout()`: ログアウト処理
- `isAuthenticated()`: 認証状態確認
- `resetAuthState()`: 認証状態リセット

## セットアップ手順

### 1. 依存関係のインストール

```bash
cd tests
npm install
```

### 2. Playwrightブラウザのインストール

```bash
cd tests
npx playwright install --with-deps
```

### 3. 環境変数の設定

`.env.local`ファイルにテスト用環境変数を設定：

```env
# テストユーザー設定
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpass123
TEST_ADMIN_EMAIL=admin@example.com
TEST_ADMIN_PASSWORD=adminpass123

# アプリケーション設定
VITE_API_BASE_URL=http://localhost:8502
```

### 4. 開発サーバーの起動

テスト実行前に以下のサーバーが起動している必要があります：

```bash
# フロントエンド開発サーバー（別ターミナル）
cd frontend
npm run dev

# バックエンドサーバー（別ターミナル）
cd backend
# サーバー起動コマンド
```

## テスト実行

### 基本的なテスト実行

```bash
cd tests

# すべてのテストを実行
npx playwright test

# 特定のブラウザでテスト実行
npx playwright test --project=chromium

# ヘッドフルモードでテスト実行
npx playwright test --headed

# 特定のテストファイルを実行
npx playwright test e2e/auth/login.spec.ts
```

### デバッグモード

```bash
# デバッグモードでテスト実行
npx playwright test --debug

# UI モードでテスト実行
npx playwright test --ui
```

### レポート表示

```bash
# HTMLレポートを表示
npx playwright show-report
```

## ベストプラクティス

### 1. テスト作成時の注意点

- **認証状態の管理**: `auth.ts`ヘルパーを使用
- **ページオブジェクトパターン**: 複雑なページは専用クラスを作成
- **データテストID**: `data-testid`属性を使用してセレクタを安定化
- **非同期処理**: 適切な待機処理を実装

### 2. テストデータ管理

- **テストユーザー**: 専用のテストアカウントを使用
- **テストデータ**: 各テスト後にクリーンアップ
- **外部依存**: モック可能な部分は適切にモック化

### 3. CI/CD対応

```bash
# CI環境でのテスト実行例
npx playwright test --reporter=html --output-dir=test-results
```

## トラブルシューティング

### よくある問題

1. **ブラウザ起動エラー**
   ```bash
   npx playwright install --with-deps
   ```

2. **タイムアウトエラー**
   - ネットワーク速度に応じてタイムアウト値を調整
   - `waitForLoadState('networkidle')`を使用

3. **認証エラー**
   - テストユーザーの存在確認
   - 環境変数の設定確認

### ログ確認

```bash
# デバッグログ付きでテスト実行
DEBUG=pw:api npx playwright test
```

## 拡張可能性

### 新しいテストカテゴリの追加

1. `e2e/`ディレクトリに新しいカテゴリフォルダを作成
2. 必要に応じて`helpers/`にヘルパー関数を追加
3. `playwright.config.ts`で設定を調整

### カスタムフィクスチャ

```typescript
// e2e/fixtures/custom-fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  // カスタムフィクスチャを定義
});
```

## 参考資料

- [Playwright公式ドキュメント](https://playwright.dev/)
- [Playwright TypeScript設定](https://playwright.dev/docs/test-typescript)
- [認証テストのベストプラクティス](https://playwright.dev/docs/auth)

## 更新履歴

- 2025-09-23: 初期環境構築完了
  - Playwright設定
  - 認証ヘルパー作成
  - ディレクトリ構造確立