# 技術的決定事項と今後の開発方針

## 📅 作成日: 2024年9月24日

## 1. 判明した技術的事実

### 1.1 計算ロジックの差異
**事実**:
- 既存システム（kigaku-navi.com）とローカル実装で日九星計算に2-4九星の差異
- 例: 2024年9月24日
  - 既存システム: 6
  - ローカルシステム: 8

**原因**:
- 九星気学には複数の流派が存在
- 夏至・冬至の起点、60日周期の計算方法が流派により異なる
- 閏年処理の実装差

### 1.2 既存システムの技術構成
```
ban.js (850KB)
  ↓ アンミニファイ
ban0924.js (2MB)
  - Vue.js 2.x ベース
  - Webpack バンドル済み
  - 直接的な関数呼び出し困難
```

## 2. 推奨される技術決定

### 2.1 計算ロジックの方針
**推奨**: **独自最適化版（オプションC）の採用**

**理由**:
1. 既存システムとの完全互換は技術的に困難
2. 一貫性のある計算ロジックを保証可能
3. 将来的な拡張・保守が容易

**実装方針**:
```typescript
// 設定で流派を切り替え可能にする
interface KyuseiConfig {
  ryuha: 'standard' | 'existing' | 'local';
  setuiriAdjustment: boolean;
  uruuHandling: 'strict' | 'loose';
}
```

### 2.2 アーキテクチャ決定

#### フロントエンド
**決定**: **React + TypeScript**
- 理由: TypeScriptとの親和性、コンポーネント再利用性
- 代替案: Vue.js 3（既存システムがVue.js 2のため）

#### バックエンド
**決定**: **Node.js + Express + TypeScript**
- 理由: フロントエンドとの言語統一、型安全性
- 代替案: Python FastAPI（高速、型ヒント）

#### データベース
**決定**: **PostgreSQL**
- 理由: ACID準拠、JSON対応、拡張性
- 代替案: MySQL（既存システムとの互換性）

## 3. 実装優先順位

### 🔴 最優先（今週中）
1. **計算ロジックの最終決定と実装**
   ```typescript
   // src/core/KyuseiCalculator.ts
   export class KyuseiCalculator {
     constructor(private config: KyuseiConfig) {}

     calculateHonmeisei(birthDate: Date): number {
       switch(this.config.ryuha) {
         case 'standard': return this.standardCalculation(birthDate);
         case 'existing': return this.existingSystemCalculation(birthDate);
         case 'local': return this.localSystemCalculation(birthDate);
       }
     }
   }
   ```

2. **データベース設計とマイグレーション**
   ```sql
   -- users table
   CREATE TABLE users (
     id UUID PRIMARY KEY,
     email VARCHAR(255) UNIQUE NOT NULL,
     birth_date DATE NOT NULL,
     gender VARCHAR(10),
     honmei_sei INTEGER,
     getumei_sei INTEGER
   );

   -- kantei_results table
   CREATE TABLE kantei_results (
     id UUID PRIMARY KEY,
     user_id UUID REFERENCES users(id),
     target_date DATE,
     result_json JSONB,
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```

### 🟡 次優先（来週）
1. **API実装**
   - RESTful API設計
   - 認証・認可実装（JWT）
   - バリデーション（express-validator）

2. **Reactコンポーネント開発**
   - 8角形方位盤コンポーネント
   - 日付入力フォーム
   - 結果表示コンポーネント

### 🟢 その後（2週間後）
1. **テスト実装**
   - Jest単体テスト
   - Cypress E2Eテスト
   - 負荷テスト

2. **CI/CD構築**
   - GitHub Actions
   - Docker化
   - 自動デプロイ

## 4. ディレクトリ構成（推奨）

```
kyuuseikigaku-kichihoui/
├── packages/
│   ├── frontend/          # Reactアプリ
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── pages/
│   │   │   └── utils/
│   │   └── package.json
│   │
│   ├── backend/           # Node.js API
│   │   ├── src/
│   │   │   ├── controllers/
│   │   │   ├── models/
│   │   │   ├── routes/
│   │   │   └── services/
│   │   └── package.json
│   │
│   └── shared/            # 共通型定義
│       ├── src/
│       │   ├── types/
│       │   └── constants/
│       └── package.json
│
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── docker-compose.yml
│
├── docs/
├── scripts/
└── package.json           # Monorepoルート
```

## 5. 開発環境セットアップ

### 必要なツール
```bash
# Node.js環境
node --version  # v18以上推奨
npm --version   # v9以上推奨

# データベース
psql --version  # PostgreSQL 14以上

# 開発ツール
git --version
docker --version  # オプション
```

### セットアップコマンド
```bash
# 依存関係インストール
npm install

# データベースセットアップ
npm run db:migrate

# 開発サーバー起動
npm run dev:frontend  # http://localhost:3000
npm run dev:backend   # http://localhost:8092

# テスト実行
npm run test
npm run test:e2e
```

## 6. コーディング規約

### TypeScript
```typescript
// ✅ Good
interface User {
  id: string;
  birthDate: Date;
  honmeiSei: number;
}

// ❌ Bad
interface user {
  ID: string;
  birth_date: Date;
  HonmeiSei: number;
}
```

### React
```tsx
// ✅ Good: 関数コンポーネント + hooks
const HoibanDisplay: FC<Props> = ({ data }) => {
  const [selected, setSelected] = useState<Direction | null>(null);

  return (
    <div className="hoiban-container">
      {/* ... */}
    </div>
  );
};

// ❌ Bad: クラスコンポーネント
class HoibanDisplay extends Component {
  // ...
}
```

## 7. git戦略

### ブランチ戦略
```
main
├── develop
│   ├── feature/user-auth
│   ├── feature/hoiban-ui
│   └── feature/api-endpoints
├── hotfix/calculation-bug
└── release/v1.0.0
```

### コミットメッセージ
```
feat: ユーザー認証機能を追加
fix: 日九星計算の閏年処理を修正
docs: API仕様書を更新
test: 方位盤表示のテストを追加
refactor: 計算ロジックをリファクタリング
```

## 8. 今後の決定事項

### 要検討
1. **デプロイ先**
   - AWS (EC2/ECS)
   - Vercel + Supabase
   - Heroku

2. **モニタリング**
   - Datadog
   - New Relic
   - 自前実装

3. **CDN利用**
   - CloudFlare
   - AWS CloudFront

### スケジュール
- Week 1: アーキテクチャ確定、DB設計
- Week 2: API実装、認証機能
- Week 3: UI実装、統合
- Week 4: テスト、最適化
- Week 5: デプロイ準備、ドキュメント

## 9. 連絡・質問事項

### 確認が必要な項目
1. ✅ 計算ロジックの方針 → 独自最適化版で進める
2. ⏳ デプロイ環境の選定
3. ⏳ ドメイン名の決定
4. ⏳ SSL証明書の取得方法

### 技術的な質問
- Q: 既存ban.jsの著作権は？
- Q: ユーザーデータの保持期間は？
- Q: GDPR対応は必要か？

---
*このドキュメントは開発進行に応じて更新されます*