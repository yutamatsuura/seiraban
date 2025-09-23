# バックアップ状態ドキュメント

## 🔒 現在の作業状態 (2025-09-23)

### Git コミット情報
- **コミットID**: 8c4a42b
- **コミットメッセージ**: "🔒 BACKUP: Working state - main.py implementation restored"
- **ブランチ**: main

### システム構成

#### バックエンド
- **メインファイル**: `/backend/main.py` (自己完結型)
- **データベース**: PostgreSQL (NEON Cloud)
- **認証**: 固定ユーザーID=70 (本番環境では要修正)
- **ポート**: 8502
- **起動コマンド**: `cd backend && ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8502 --reload`

#### フロントエンド
- **フレームワーク**: Vue.js 3 + TypeScript
- **ポート**: 5173 (開発サーバー)
- **起動コマンド**: `cd frontend && npm run dev`

#### 主要機能の状態
✅ **正常動作中:**
- 認証システム (`/api/auth/verify`)
- 診断作成 (`/api/diagnosis/create`)
- 診断表示 (`/api/diagnosis/{id}`)
- テンプレート設定 (`/api/admin/template-settings`)

### データベース接続
```python
# main.py内の設定
DATABASE_URL = "postgresql://neondb_owner:npg_FLj8pL8L7Rj9@ep-bitter-paper-a5gzfqjg.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

### 重要な実装詳細

#### 1. 診断作成API
- **エンドポイント**: `POST /api/diagnosis/create`
- **スキーマ**: `DiagnosisRequest` (KanteiCalculateRequestから変更)
- **固定値**: `user_id=70`, `admin_mode=True`

#### 2. 認証システム
- **エンドポイント**: `GET /api/auth/verify`
- **レスポンス**: 固定ユーザー情報
```json
{
  "user": {
    "id": 70,
    "email": "test@example.com",
    "business_name": "テスト事業者",
    "operator_name": "テスト鑑定士"
  }
}
```

#### 3. データベースモデル
- `User`: ユーザー情報
- `KanteiRecord`: 鑑定記録（診断データ）

### アーキテクチャの変更履歴
1. **以前**: モジュラー構造 (`app/` ディレクトリ)
2. **現在**: 単一ファイル構造 (`main.py`)
3. **バックアップ**: モジュラー構造は `backend/app_backup/` に移動

### 動作確認済み項目
- ✅ フロントエンド・バックエンド連携
- ✅ 診断作成・表示機能
- ✅ テンプレート設定機能
- ✅ データベース連携

### 本番環境で修正が必要な項目
⚠️ **セキュリティ・品質改善が必要:**
1. 固定ユーザーID (user_id=70) の動的認証への変更
2. admin_mode=True の適切な権限チェックへの変更
3. ハードコードされた認証情報の環境変数化
4. エラーハンドリングの強化
5. ログ機能の実装

### 環境変数
現在は直接コードに記述。本番環境では `.env` ファイル化必要:
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ENVIRONMENT=production
```

### 依存関係
- Python 3.x
- FastAPI
- SQLAlchemy
- PostgreSQL (psycopg2)
- Uvicorn
- Vue.js 3
- TypeScript
- Node.js

## 復元手順

### 完全復元 (この状態に戻す)
```bash
# 1. Git復元
git checkout 8c4a42b

# 2. 仮想環境設定
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
./venv/Scripts/activate   # Windows

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. フロントエンド依存関係
cd ../frontend
npm install

# 5. 両方のサーバー起動
cd ../backend
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8502 --reload &
cd ../frontend
npm run dev
```

### データベース復元
```bash
# データベースは外部NEON Cloudサービスのため、データは保持される
# 新しい環境では main.py 内の DATABASE_URL を確認・更新
```

## 注意事項
- このバックアップは開発状態であり、本番運用には追加のセキュリティ対策が必要
- 固定認証情報やハードコードされた値は本番環境では変更必須
- データベース接続情報は環境に応じて調整が必要

---
**作成日**: 2025-09-23
**バックアップ対象**: 診断作成機能復旧後の安定動作状態