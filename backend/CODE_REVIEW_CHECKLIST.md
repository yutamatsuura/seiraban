# コードレビューチェックリスト

## 🚫 ハードコード禁止チェック

### ❌ 絶対禁止項目

1. **ユーザーID のハードコード**
   ```python
   # ❌ 禁止
   user_id = 95
   user_id = 70
   USER_ID = 1

   # ✅ 正しい
   current_user: User = Depends(get_current_user)
   user_id = current_user.id
   ```

2. **ポート番号のハードコード**
   ```python
   # ❌ 禁止
   port = 8502
   uvicorn.run(app, port=8000)

   # ✅ 正しい
   port = int(os.getenv("PORT", "8502"))
   uvicorn.run(app, port=port)
   ```

3. **URL・パスのハードコード**
   ```python
   # ❌ 禁止
   api_url = "http://localhost:8502"
   file_path = "/var/uploads"

   # ✅ 正しい
   api_url = os.getenv("API_BASE_URL", "http://localhost:8502")
   file_path = os.getenv("UPLOAD_DIR", "/var/uploads")
   ```

4. **データベース設定のハードコード**
   ```python
   # ❌ 禁止
   DATABASE_URL = "postgresql://user:pass@localhost/db"

   # ✅ 正しい
   DATABASE_URL = os.getenv("DATABASE_URL")
   ```

### 📝 レビュー時の確認ポイント

#### 1. 認証・認可
- [ ] 全エンドポイントで適切な認証が実装されているか
- [ ] `get_current_user` 依存関数が使用されているか
- [ ] ハードコードされたuser_idが存在しないか
- [ ] 管理者権限チェックが適切に実装されているか

#### 2. 設定管理
- [ ] 環境変数が適切に使用されているか
- [ ] デフォルト値が設定されているか
- [ ] 秘匿情報がコードに直接書かれていないか
- [ ] 設定ファイル（.env）が適切に使用されているか

#### 3. データベースアクセス
- [ ] SQLクエリでハードコードされたIDが使用されていないか
- [ ] ユーザー固有データへのアクセス制御が適切か
- [ ] テーブル名やカラム名がハードコードされていないか

#### 4. ファイル・リソース管理
- [ ] ファイルパスがハードコードされていないか
- [ ] アップロードディレクトリが設定可能か
- [ ] 一時ファイルのパスが動的に生成されているか

### 🔧 推奨実装パターン

#### 1. 依存注入パターン
```python
# 認証が必要なエンドポイント
@router.get("/endpoint")
def endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user.id を使用
    pass
```

#### 2. 環境変数パターン
```python
import os
from functools import lru_cache

@lru_cache()
def get_settings():
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "api_port": int(os.getenv("API_PORT", "8502")),
        "upload_dir": os.getenv("UPLOAD_DIR", "uploads"),
    }
```

#### 3. 設定クラスパターン
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_port: int = 8502
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"

settings = Settings()
```

### ⚠️ 例外ケース（許可される場合）

1. **HTTPステータスコード**
   ```python
   # ✅ 許可
   status_code=status.HTTP_404_NOT_FOUND
   status_code=404
   ```

2. **数学的定数**
   ```python
   # ✅ 許可
   MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
   PAGINATION_DEFAULT = 20
   ```

3. **テストコード**
   ```python
   # ✅ テストでは許可
   def test_user_creation():
       user_id = 999  # テスト用固定ID
   ```

### 🛠️ 自動チェックツール

1. **pre-commit フック**
   - `.pre-commit-config.yaml` で設定済み
   - コミット前に自動実行

2. **検出スクリプト**
   ```bash
   # 手動実行
   python scripts/detect_hardcode.py app/**/*.py
   ```

3. **CI/CD パイプライン**
   ```yaml
   # GitHub Actions での実行例
   - name: Check hardcoded values
     run: python scripts/detect_hardcode.py $(find app -name "*.py")
   ```

### 📋 レビュー完了チェック

#### コミット前
- [ ] ハードコード検出スクリプトでエラーなし
- [ ] pre-commitフックが正常に通過
- [ ] 環境変数設定が`.env.example`に記載済み

#### マージ前
- [ ] 認証が適切に実装されている
- [ ] テストが全て通過している
- [ ] ドキュメントが更新されている
- [ ] セキュリティ要件を満たしている

### 🚨 違反時の対処法

1. **即座に修正**
   - ハードコードを環境変数に変更
   - 適切な依存注入に変更

2. **レビュー拒否**
   - 修正完了まで承認しない
   - 修正方法を具体的に指示

3. **教育・周知**
   - チーム内でのガイドライン共有
   - レビューポイントの再確認

---

## 💡 追加の品質チェック項目

### セキュリティ
- [ ] SQLインジェクション対策
- [ ] XSS対策
- [ ] CSRF対策
- [ ] 権限エスカレーション防止

### パフォーマンス
- [ ] N+1クエリ問題の回避
- [ ] 適切なインデックス使用
- [ ] キャッシュの活用
- [ ] ページネーション実装

### 保守性
- [ ] コードの可読性
- [ ] 適切なコメント
- [ ] エラーハンドリング
- [ ] ログ出力

このチェックリストを使用して、今後一切ハードコードが混入しないようにしてください。