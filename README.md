# 星羅盤（SEIRABAN）- 鑑定書楽々作成ツール

プロフェッショナルな鑑定書を1分で作成できるツール

## 概要

星羅盤は鑑定業務の効率化を実現する専門ツールです。直感的なインターフェースで、プロフェッショナルな鑑定書を短時間で作成できます。

## 技術スタック

### フロントエンド
- Vue.js 3
- TypeScript
- Vite
- Pinia (状態管理)
- SCSS

### バックエンド
- FastAPI
- Python 3.11+
- SQLAlchemy
- Pydantic
- JWT認証
- UTAGE連携

## セットアップ

### 前提条件
- Node.js 18以上
- Python 3.11以上

### フロントエンド
```bash
cd frontend
npm install
npm run dev
```

### バックエンド
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8502
```

## アクセス情報

- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8502
- API文書: http://localhost:8502/docs

## 機能

- ユーザー認証（JWT）
- 二段階権限管理（一般ユーザー・管理者）
- UTAGE会員管理システム連携
- レスポンシブデザイン
- アクセシビリティ対応

## ライセンス

Proprietary - All Rights Reserved
