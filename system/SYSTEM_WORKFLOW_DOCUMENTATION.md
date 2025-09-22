# 既存システム動作フロー完全文書

**作成日**: 2025年9月18日
**対象システム**: 九星気学・姓名判断統合システム
**統合方法**: Puppeteer Browser Automation

---

## 🎯 **システム概要**

### **システム構成**
```
/system/
├── kyuuseikigaku-kichihoui/    # 九星気学システム
├── seimeihandan/               # 姓名判断システム
├── puppeteer_bridge_fixed.js   # 統合ブリッジ（最終版）
└── package.json                # Puppeteer依存関係
```

### **技術スタック**
- **フロントエンド**: Vue.js 2.6.10 + TypeScript 3.6.3
- **バンドル**: webpack 4.41.0 + webpack-dev-server
- **外部API**: kigaku-navi.com (姓名判断用)
- **統合**: Puppeteer 21.11.0 (Browser Automation)

---

## 🌟 **九星気学システム (kyuuseikigaku-kichihoui)**

### **システムエントリーポイント**
- **webpack entry**: `src/js/bans/BanMain.ts`
- **HTML起点**: `src/ban_top_full.html`
- **開発サーバー**: http://localhost:3001/

### **完全な動作フロー**

#### **Phase 1: 入力画面**
```
URL: http://localhost:3001/ban_top_full.html
Component: <top-component>
Template: TopComponent.html
```

**TopComponent.ts の動作**:
1. 年月日・性別のselectボックス表示
2. LocalStorageから既存値を復元
3. 入力値をVue.jsリアクティブデータで管理

#### **Phase 2: 入力処理**
```javascript
// TopComponent.ts:submitBirthday()
submitBirthday() {
    localStorage.setItem(KibanConfig.YEAR, this.selectYear);
    localStorage.setItem(KibanConfig.MONTH, this.selectMonth);
    localStorage.setItem(KibanConfig.DAY, this.selectDay);
    localStorage.setItem(KibanConfig.SEX, this.selectSex);

    location.href = `/qsei/ban_birthday.php`;
}
```

**重要**: PHPファイル (`.php`) は webpack proxy で `.html` に変換
```javascript
// webpack.config.debug.js
proxy: {
    '/*.php': {
        target: 'http://localhost:3001',
        pathRewrite: { "php": "html" }
    }
}
```

#### **Phase 3: 結果表示**
```
URL: http://localhost:3001/ban_birthday.html
Component: <birthday-component>
Template: BirthdayComponent.html
```

**BirthdayComponent.ts の動作**:
1. `Config.getBirthDate()` でLocalStorageから生年月日取得
2. `BirthdayQseiGroup.of(birthDate, man)` で九星気学計算実行
3. 年命星・月命星・日命星・干支を算出
4. `<canvas-component>` で九星盤面を描画

### **計算ロジックの核心**

#### **正確な暦計算**
```typescript
// Setu.ts - 節入り計算
public static readonly SETU2 = {
    month: 2, D: 4.8693, A: 0.242713, year: -1
};

// QseiDate.ts - 九星特殊月処理
private static readonly QSEI_SPECIAL_MONTHS = new Map<string, SpecialMonth>();
```

#### **LocalStorage設定キー**
```typescript
// Config.ts
public static readonly SEX = "kiban_sex";      // 性別
public static readonly YEAR = "kiban_year";    // 生年
public static readonly MONTH = "kiban_month";  // 生月
public static readonly DAY = "kiban_day";      // 生日
```

---

## 📛 **姓名判断システム (seimeihandan)**

### **システムエントリーポイント**
- **webpack entry**: `src/js/seimeis/SeimeiMain.ts`
- **HTML起点**: `src/seimei.html`
- **開発サーバー**: http://localhost:3001/

### **完全な動作フロー**

#### **Phase 1: 姓名入力**
```
URL: http://localhost:3001/seimei.html
Components: <search-component>, <result-kousei-component>, <result-kantei-component>
```

**SearchComponent.ts の動作**:
1. 姓・名の入力フォーム表示
2. URLパラメータから既存値を復元
3. `submitKantei()` で外部API呼び出し

#### **Phase 2: 外部API統合**
```javascript
// SearchComponent.ts:kakusu()
private kakusu(sei: string, mei: string) {
    let url = `https://kigaku-navi.com/qsei/api/select_seimei.php?sei=${sei}&mei=${mei}`;

    $.ajax(url, {
        type: 'get',
        dataType: 'json',
        crossDomain: true
    }).done((json: JsonResult) => {
        let meis = json["mei"];
        let seis = json["sei"];
        this.send(seis, meis, json.ng, json.last_date);
    }).fail((errorText) => {
        alert("検索に失敗しました。" + errorText.responseText);
    });
}
```

#### **Phase 3: 漢字解析処理**
```typescript
// JsonResult Interface
interface JsonResult {
    sei: Array<JsonMojis>    // 姓の漢字データ
    mei: Array<JsonMojis>    // 名の漢字データ
    ng: Array<Ngwords>       // NGワード
    last_date: string        // 最終更新日
}

interface JsonMojis {
    name: string             // 漢字
    new: JsonMoji           // 新字体情報
    old: JsonMoji           // 旧字体情報
}

interface JsonMoji {
    code: string            // 文字コード
    kakusu: string          // 画数
    kana: string            // 読み方
    isbunri: string         // 分離名判定
}
```

#### **Phase 4: 五格・五行・陰陽計算**
```typescript
// SearchComponent.ts:send()
public send(jsonSeis: Array<JsonMojis>, jsonMeis: Array<JsonMojis>) {
    // 1. 文字→Charaオブジェクト変換
    charaSeis.push(Chara.of(sei.name, Number(val.kakusu), val.kana, val.isbunri == "1"));

    // 2. 姓名判断計算実行
    EVENT_HUB.$emit('kantei', new Seimei(charaSeis, charaMeis, ng));
}

// Seimei.ts - 五格計算
public tenkaku(): Kaku { return Kaku.ofTenkaku(this); }     // 天格
public jinkaku(): Kaku { return Kaku.ofJinkaku(this); }     // 人格
public tikaku(): Kaku { return Kaku.ofTikaku(this); }       // 地格
public soukaku(): Kaku { return Kaku.ofSoukaku(this); }     // 総格
```

---

## 🤖 **Puppeteer統合実装**

### **最終版ブリッジ**: `puppeteer_bridge_fixed.js`

#### **九星気学自動化**
```javascript
async function executeKyuseiFixed(inputData) {
    // 1. 開発サーバー起動
    devServer = await startDevServerWebpack(systemDir, 3001);

    // 2. ブラウザ起動
    browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    // 3. 入力ページアクセス
    await page.goto('http://localhost:3001/ban_top_full.html');

    // 4. Vue.js TopComponent操作
    await page.evaluate((year, month, day, sex) => {
        const topComponent = app.$children.find(child =>
            child.selectYear !== undefined);
        topComponent.selectYear = year;
        topComponent.selectMonth = month;
        topComponent.selectDay = day;
        topComponent.selectSex = sex;
    }, year, month, day, sex);

    // 5. 「九星を調べる」ボタンクリック
    await page.click('span.button.beju:first-of-type a');

    // 6. 結果ページ遷移待機
    await page.waitForNavigation();

    // 7. BirthdayComponentから結果取得
    const result = await page.evaluate(() => {
        const vueInstance = document.querySelector('birthday-component').__vue__;
        return {
            birthday: vueInstance.birthday,
            yearQseiName: vueInstance.yearQseiName,
            monthQseiName: vueInstance.monthQseiName,
            dayQseiName: vueInstance.dayQseiName
        };
    });
}
```

#### **姓名判断自動化**
```javascript
async function executeSeimeiFixed(inputData) {
    // 1-2. サーバー・ブラウザ起動 (同上)

    // 3. 姓名判断ページアクセス
    await page.goto('http://localhost:3001/seimei.html');

    // 4. SearchComponent操作
    await page.evaluate((sei, mei) => {
        const searchComponent = app.$children.find(child =>
            child.sei !== undefined);
        searchComponent.sei = sei;
        searchComponent.mei = mei;
        searchComponent.submitKantei();  // 外部API呼び出し実行
    }, sei, mei);

    // 5. 外部API完了待機
    await page.waitForTimeout(5000);

    // 6. 結果取得
    const result = await page.evaluate(() => {
        return {
            sei: searchComponent.sei,
            mei: searchComponent.mei,
            error: searchComponent.error
        };
    });
}
```

### **環境互換性対応**

#### **Node.js v23 + webpack v4 問題**
```javascript
// legacy OpenSSL provider 必須
env: { ...process.env, NODE_OPTIONS: '--openssl-legacy-provider' }
```

#### **起動コマンド**
```bash
# 九星気学テスト
NODE_OPTIONS='--openssl-legacy-provider' node puppeteer_bridge_fixed.js kyusei '{"birth_date":"1990-01-15","gender":"male"}'

# 姓名判断テスト
NODE_OPTIONS='--openssl-legacy-provider' node puppeteer_bridge_fixed.js seimei '{"name":"田中 太郎"}'
```

---

## 🔍 **システム検証方法**

### **手動ブラウザテスト**

#### **九星気学**
1. 開発サーバー起動:
   ```bash
   cd kyuuseikigaku-kichihoui
   NODE_OPTIONS='--openssl-legacy-provider' npx webpack-dev-server --config webpack.config.debug.js
   ```

2. ブラウザアクセス: http://localhost:3001/ban_top_full.html

3. 動作確認:
   - 年月日・性別選択
   - 「九星を調べる」クリック
   - ban_birthday.htmlへ遷移
   - 年命星・月命星・日命星表示確認

#### **姓名判断**
1. 開発サーバー起動:
   ```bash
   cd seimeihandan
   NODE_OPTIONS='--openssl-legacy-provider' npx webpack-dev-server --config webpack.config.debug.js
   ```

2. ブラウザアクセス: http://localhost:3001/seimei.html

3. 動作確認:
   - 姓名入力
   - 外部API呼び出し実行
   - 五格・総合評価表示確認

---

## ⚡ **パフォーマンス＆制限事項**

### **外部API依存**
- **姓名判断**: `https://kigaku-navi.com/qsei/api/select_seimei.php`
- **制限**: ネットワーク依存、レート制限あり
- **対策**: 5秒タイムアウト、エラーハンドリング

### **計算精度**
- **九星気学**: 節入り天体計算による高精度
- **姓名判断**: 新字体/旧字体対応、分離名判定

### **ブラウザリソース**
- **メモリ**: Puppeteerによる一時的なブラウザ起動
- **ポート**: 3001番ポート専用使用
- **プロセス**: webpack-dev-server + Chrome プロセス

---

## 🎯 **統合システム利用方法**

### **最終統合ファイル**
- **メインブリッジ**: `puppeteer_bridge_fixed.js`
- **依存関係**: `package.json` (Puppeteer)
- **実行環境**: Node.js (legacy OpenSSL provider)

### **API仕様**
```javascript
// 九星気学
Input: {
    "birth_date": "1990-01-15",
    "gender": "male"
}

Output: {
    "success": true,
    "type": "kyusei",
    "result": {
        "birthday": "平成2年1月15日",
        "yearQseiName": "二黒土星",
        "monthQseiName": "八白土星",
        "dayQseiName": "六白金星"
    }
}

// 姓名判断
Input: {
    "name": "田中 太郎"
}

Output: {
    "success": true,
    "type": "seimei",
    "result": {
        "sei": "田中",
        "mei": "太郎",
        "calculation_completed": true
    }
}
```

---

## 📋 **運用チェックリスト**

### **事前準備**
- [ ] Node.js環境確認
- [ ] npm install完了 (各システム + Puppeteer)
- [ ] PORT 3001利用可能確認
- [ ] インターネット接続確認 (姓名判断API用)

### **統合テスト**
- [ ] 九星気学: 手動ブラウザテスト
- [ ] 九星気学: Puppeteer自動化テスト
- [ ] 姓名判断: 手動ブラウザテスト
- [ ] 姓名判断: Puppeteer自動化テスト
- [ ] 外部API接続確認

### **本格運用**
- [ ] エラーハンドリング確認
- [ ] タイムアウト処理確認
- [ ] リソースクリーンアップ確認
- [ ] ログ出力設定

---

**この文書は既存システムの動作フローを完全に文書化したものです。**
**統合実装時は必ずこの仕様に従って開発してください。**