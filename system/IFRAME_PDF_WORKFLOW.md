# iframe結果をPDF化するワークフロー

## 概要
既存システム（iframe表示）の鑑定結果を、統合された美しいPDFに変換する仕組み。

## システム構成

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   既存システム     │    │  Bridge Service  │    │  PDF Generation │
│  (iframe)       │    │  (Node.js)      │    │  (Python)       │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ ・九星気学        │───▶│ ・Puppeteer      │───▶│ ・ReportLab     │
│ ・姓名判断        │    │ ・データ抽出      │    │ ・テンプレート   │
│ ・Vue.js+TS      │    │ ・フォーマット変換│    │ ・ロゴ・屋号     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 処理フロー

### 1. 鑑定実行
```javascript
// フロントエンド（Vue.js 3.x）
async function executeDivination(clientData) {
    // iframe内の既存システムを操作
    const kyuseiIframe = document.getElementById('kyusei-iframe');
    const seimeiIframe = document.getElementById('seimei-iframe');

    // Bridge Service呼び出し
    const response = await fetch('/api/bridge/execute-divination', {
        method: 'POST',
        body: JSON.stringify({
            client_info: clientData,
            kyusei_params: { year, month, day, sex },
            seimei_params: { sei, mei }
        })
    });

    const result = await response.json();
    return result;
}
```

### 2. データ抽出・統合
```javascript
// Bridge Service (iframe_to_pdf_bridge.js)
async function executeFullDivination(clientData) {
    const bridge = new IframeToPDFBridge();
    await bridge.init();

    try {
        // 各システムから結果取得
        const kyuseiResult = await bridge.captureKyuseiKigakuResult(
            clientData.year, clientData.month, clientData.day, clientData.sex
        );

        const seimeiResult = await bridge.captureSeimeiHandanResult(
            clientData.sei, clientData.mei
        );

        // PDF生成用データフォーマット
        const pdfData = bridge.formatForPDFGeneration(
            kyuseiResult, seimeiResult, clientData, clientData.custom_message
        );

        return pdfData;

    } finally {
        await bridge.close();
    }
}
```

### 3. PDF生成
```python
# PDF Service (pdf_service.py)
def generate_pdf_from_iframe_data(self, db: Session, iframe_data: dict, user_id: int):
    """iframe結果からPDF生成"""

    # 鑑定記録をDBに保存
    kantei_record = KanteiRecord(
        user_id=user_id,
        client_name=iframe_data['client_info']['name'],
        client_info=iframe_data['client_info'],
        calculation_result=iframe_data['calculation_result'],
        custom_message=iframe_data.get('custom_message'),
        status="completed"
    )

    db.add(kantei_record)
    db.commit()

    # PDF生成（既存の仕組みを使用）
    pdf_path, file_size = self._create_pdf_document(
        kantei_record,
        template_settings=None,
        custom_message=iframe_data.get('custom_message')
    )

    return pdf_path, file_size
```

## API エンドポイント設計

### 1. 鑑定実行エンドポイント
```
POST /api/bridge/execute-divination
{
    "client_info": {
        "sei": "田中",
        "mei": "太郎",
        "year": 1990,
        "month": 5,
        "day": 15,
        "sex": 1,
        "birth_time": "14:30",
        "birth_place": "東京都"
    },
    "custom_message": "鑑定士からのメッセージ",
    "generate_pdf": true
}

Response:
{
    "success": true,
    "kantei_record_id": 123,
    "calculation_result": {...},
    "pdf_url": "/api/kantei/pdf/123"
}
```

### 2. 既存PDFエンドポイントを活用
```
GET /api/kantei/pdf/123          # プレビュー
POST /api/kantei/download        # ダウンロード
GET /api/kantei/status/123       # 生成状況
```

## 実装のメリット

### ✅ 既存システム完全活用
- 九星気学・姓名判断の精密計算ロジックをそのまま使用
- 新規実装やバグ混入のリスクゼロ
- システム更新時も自動追従

### ✅ 統合PDF生成
- ReportLabによる美しいレイアウト
- 鑑定士のロゴ・屋号・コメント統合
- 一貫したブランディング

### ✅ HTMLスナップショット保存
- デバッグ・検証用にHTML結果も保存
- 後から詳細確認可能
- トレーサビリティ確保

## セキュリティ考慮

### プロセス分離
```javascript
// 別プロセスでPuppeteer実行
const { spawn } = require('child_process');

async function secureExecuteDivination(data) {
    return new Promise((resolve, reject) => {
        const process = spawn('node', ['iframe_to_pdf_bridge.js'], {
            stdio: ['pipe', 'pipe', 'pipe'],
            timeout: 30000  // 30秒タイムアウト
        });

        process.stdin.write(JSON.stringify(data));
        process.stdin.end();

        // 結果取得...
    });
}
```

### リソース制限
- Puppeteerプロセスのメモリ・CPU制限
- 実行時間制限（30秒）
- 同時実行数制限

## パフォーマンス最適化

### ブラウザプール
```javascript
class BrowserPool {
    constructor(maxSize = 3) {
        this.pool = [];
        this.maxSize = maxSize;
    }

    async getBrowser() {
        if (this.pool.length > 0) {
            return this.pool.pop();
        }
        return await puppeteer.launch({...});
    }

    releaseBrowser(browser) {
        if (this.pool.length < this.maxSize) {
            this.pool.push(browser);
        } else {
            browser.close();
        }
    }
}
```

### キャッシュ戦略
- 同一入力データの結果キャッシュ（15分）
- ブラウザインスタンス再利用
- 既存システムのウォームアップ

## 運用監視

### ログ・メトリクス
- 実行時間計測
- エラー率監視
- メモリ使用量追跡
- 成功/失敗件数

### エラー処理
- iframe読み込み失敗時の再試行
- Puppeteerクラッシュ時の復旧
- データ抽出失敗時のフォールバック

## まとめ

この仕組みにより、iframeで表示される既存システムの結果を、統合された美しいPDFとして出力可能になります。

- **完全性**: 既存システムの精密計算をそのまま活用
- **品質**: ReportLabによる高品質PDF生成
- **拡張性**: 鑑定士のブランディング・コメント対応
- **保守性**: システム分離による影響範囲限定