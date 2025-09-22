# 🚨 重要実装ノート - 絶対に見逃してはいけないポイント

**最終更新**: 2025年9月18日 15:43
**重要度**: ⭐⭐⭐⭐⭐ (最高レベル)

---

## ❗ **実装時の致命的な誤解を避ける**

### **1. 最初の実装で犯した重大な間違い**

#### **❌ 間違った理解**
```
ban_birthday.html = 入力ページ
BirthdayComponent = 入力フォーム
```

#### **✅ 正しい理解**
```
ban_top_full.html = 入力ページ (TopComponent)
ban_birthday.html = 結果表示ページ (BirthdayComponent)
```

**重要**: BirthdayComponentは表示専用。入力機能は一切ない。

---

## 🔄 **システムフローの決定的な特徴**

### **九星気学の正確な流れ**
```
1. TopComponent (入力)
   ↓ localStorage保存
2. submitBirthday() 実行
   ↓ location.href = "/qsei/ban_birthday.php"
3. BirthdayComponent (表示)
   ↓ Config.getBirthDate() でlocalStorage読込
4. 計算結果表示
```

**絶対に理解すべき点**:
- **入力と表示は完全に分離**
- **LocalStorageがデータ橋渡し役**
- **ページ遷移が必須**

---

## 🎯 **Puppeteer実装の核心ポイント**

### **Vue.jsコンポーネント操作の正確な方法**
```javascript
// ❌ 間違った方法 (DOM操作)
await page.click('input[name="year"]');

// ✅ 正しい方法 (Vue.js操作)
await page.evaluate((year) => {
    const topComponent = app.$children.find(child =>
        child.selectYear !== undefined);
    topComponent.selectYear = year;
}, year);
```

**理由**: selectボックスはv-modelでVue.jsが管理しているため。

---

## 🌐 **外部API統合の重要事項**

### **姓名判断の外部依存**
```
URL: https://kigaku-navi.com/qsei/api/select_seimei.php
Method: GET
Parameters: sei, mei
Response: JSON (JsonResult Interface)
```

**絶対に考慮すべき点**:
- **ネットワーク障害でシステム全体が停止する**
- **レート制限によるエラーの可能性**
- **APIレスポンス時間は不定 (最大5秒想定)**

---

## ⚙️ **環境依存問題の回避**

### **Node.js v23 + webpack v4 互換性**
```bash
# ❌ 起動失敗パターン
npx webpack-dev-server --config webpack.config.debug.js

# ✅ 正常起動パターン
NODE_OPTIONS='--openssl-legacy-provider' npx webpack-dev-server --config webpack.config.debug.js
```

**原因**: Node.js v17以降のOpenSSL 3.0がwebpack v4と非互換。

---

## 📂 **ファイル構造の絶対的ルール**

### **webpack設定ファイルの役割**
```javascript
// kyuuseikigaku-kichihoui/webpack.config.debug.js
entry: {
    ban: "./src/js/bans/BanMain.ts"  // 九星気学エントリー
}

// seimeihandan/webpack.config.debug.js
entry: {
    seimei: "./src/js/seimeis/SeimeiMain.ts"  // 姓名判断エントリー
}
```

**重要**: エントリーポイントを変更すると全システム動作不能。

---

## 🔍 **デバッグ時の必須確認項目**

### **開発サーバー起動確認**
```
✅ Project is running at http://localhost:3001/
✅ webpack output is served from /
✅ Compiled successfully.
```

### **ブラウザアクセス確認**
```
✅ http://localhost:3001/ban_top_full.html (九星気学入力)
✅ http://localhost:3001/ban_birthday.html (九星気学結果)
✅ http://localhost:3001/seimei.html (姓名判断)
```

### **Vue.js初期化確認**
```javascript
// コンソールで確認
document.querySelector('#app').__vue__  // Vue.jsインスタンス存在確認
```

---

## 💾 **LocalStorageキーの絶対仕様**

### **九星気学で使用するキー**
```javascript
"kiban_year"   // 生年
"kiban_month"  // 生月
"kiban_day"    // 生日
"kiban_sex"    // 性別 ("男" or "女")
```

**注意**: キー名を1文字でも間違えるとデータ取得不可。

---

## 🚫 **絶対にやってはいけないこと**

### **1. 独自計算ロジックの実装**
```javascript
// ❌ 絶対禁止
function calculateKyusei(birthDate) {
    // 独自の九星気学計算ロジック
}
```
**理由**: 既存システムと結果が異なる。

### **2. 外部APIの再実装**
```javascript
// ❌ 絶対禁止
const kanjiDatabase = { /* 独自漢字データ */ };
```
**理由**: kigaku-navi.comのデータベースと差異が発生。

### **3. HTML構造の変更**
```html
<!-- ❌ 絶対禁止 -->
<div id='app'>
    <my-custom-component></my-custom-component>
</div>
```
**理由**: Vue.jsコンポーネント登録が破綻。

---

## ⭐ **成功の絶対条件**

### **1. 既存システムの100%活用**
- 計算ロジック: そのまま使用
- Vue.jsコンポーネント: そのまま使用
- 外部API: そのまま使用

### **2. Puppeteerによる正確な操作**
- ページ遷移の完全再現
- Vue.jsデータバインディングの理解
- 非同期処理の適切な待機

### **3. 環境設定の厳密な管理**
- Node.js legacy OpenSSL設定
- webpackバージョン固定
- ポート3001専用使用

---

**このノートに従わない場合、統合は100%失敗します。**
**実装前に必ずこの文書を再確認してください。**