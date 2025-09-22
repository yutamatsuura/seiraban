# 既存システム連携実装用ファイル一覧

他のエンジニアに渡すファイルの完全リスト

## 🔴 必須ファイル（絶対に必要）

### Puppeteer連携システム
```
/system/puppeteer_bridge_final.js          # 既存システム連携ブリッジ
/system/package.json                        # Node.js依存関係
/system/package-lock.json                   # バージョンロック
```

### バックエンドサーバー
```
/backend/main.py                            # メインサーバー（port 8502）
/backend/requirements.txt                   # Python依存関係
```

### フロントエンド表示
```
/frontend/src/views/kantei/PreviewView.vue  # 鑑定結果表示画面
/frontend/src/services/api-client.ts        # API通信クライアント
/frontend/package.json                      # フロントエンド依存関係
/frontend/vite.config.ts                    # ビルド設定
```

### 設定ファイル
```
/.env.local                                 # 環境変数
/.ports.config                              # ポート設定
/docker-compose.yml                         # Docker設定
```

## 🟡 推奨ファイル（理解を深めるため）

### フロントエンド補助
```
/frontend/src/App.vue                       # メインアプリ
/frontend/src/main.ts                       # エントリーポイント
/frontend/src/router/index.ts               # ルーティング
```

### ドキュメント
```
/EXISTING_SYSTEM_INTEGRATION.md             # 詳細実装ガイド
/IMPLEMENTATION_CHECKLIST.md                # 実装チェックリスト
/FILES_TO_SHARE.md                          # このファイル
```

---

## 📦 ファイル提供方法

### 方法1: 個別ファイル送付
上記リストの各ファイルを個別に送付

### 方法2: アーカイブ作成
```bash
# プロジェクトルートで実行
tar -czf existing_system_integration.tar.gz \
  system/puppeteer_bridge_final.js \
  system/package.json \
  system/package-lock.json \
  backend/main.py \
  backend/requirements.txt \
  frontend/src/views/kantei/PreviewView.vue \
  frontend/src/services/api-client.ts \
  frontend/package.json \
  frontend/vite.config.ts \
  frontend/src/App.vue \
  frontend/src/main.ts \
  frontend/src/router/index.ts \
  .env.local \
  .ports.config \
  docker-compose.yml \
  EXISTING_SYSTEM_INTEGRATION.md \
  IMPLEMENTATION_CHECKLIST.md \
  FILES_TO_SHARE.md
```

### 方法3: Git部分クローン
```bash
# 必要な部分のみクローン
git clone --filter=blob:none --sparse <repository_url>
cd <repository>
git sparse-checkout set system/ backend/main.py frontend/src/views/kantei/ frontend/src/services/
```

---

## 🎯 受け取り側の確認手順

### 1. ファイル受領確認
```bash
# ファイル存在確認
ls system/puppeteer_bridge_final.js
ls backend/main.py
ls frontend/src/views/kantei/PreviewView.vue
ls frontend/src/services/api-client.ts
```

### 2. 依存関係確認
```bash
# Node.js版数確認
node --version  # v18以上

# Python版数確認
python --version  # 3.9以上
```

### 3. 設定ファイル編集
```bash
# 既存システムURLを自分の環境に合わせて変更
vim .env.local
```

### 4. インストール実行
```bash
cd system/ && npm install
cd ../backend/ && pip install -r requirements.txt
cd ../frontend/ && npm install
```

---

## ⚠️ 重要な注意事項

### 必須条件
- **既存鑑定システムが稼働中**（通常port 3002）
- **Node.js 18+** および **Python 3.9+** が必要
- **ポート8502**（バックエンド）と**ポート3000**（フロントエンド）が使用可能

### カスタマイズが必要な箇所
1. **既存システムURL**: `.env.local`で自分のシステムURLに変更
2. **抽出パターン**: `backend/main.py`の正規表現を既存システムの出力に合わせて調整
3. **ポート設定**: `.ports.config`で競合回避

### テスト用データ
実装後のテストには以下のような名前を推奨：
- 短い名前: 「田中 太郎」（4文字）
- 長い名前: 「松蔭時 鶴太郎」（6文字）
- 最長名前: 「佐々木 左衛門太郎」（9文字）

---

## 🆘 サポート情報

### 実装でつまずいた場合
1. `IMPLEMENTATION_CHECKLIST.md`で進捗確認
2. `EXISTING_SYSTEM_INTEGRATION.md`で詳細手順確認
3. 各ファイルのコメントとDEBUGログを参照

### よくある質問
**Q: Puppeteerがタイムアウトする**
A: 既存システムの起動確認、タイムアウト時間延長

**Q: 文字が4文字しか表示されない**
A: `extract_character_composition()`関数の動作確認

**Q: 管理者モードが動作しない**
A: APIクライアントのadminModeパラメータ確認

---

**これらのファイルで既存システム連携の完全実装が可能です！**