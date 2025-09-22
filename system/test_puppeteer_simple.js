#!/usr/bin/env node
/**
 * 簡易Puppeteerテスト - 既存サーバーを使用
 */

const puppeteer = require('puppeteer');

async function testKyuseiSystem() {
    const browser = await puppeteer.launch({
        headless: "new", // 新しいヘッドレスモード
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding'
        ]
    });

    try {
        const page = await browser.newPage();

        console.log('🔗 九星気学システムにアクセス中...');

        // 既存サーバーにアクセス
        await page.goto('http://localhost:3001/ban_top_full.html', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        console.log('✅ ページ読み込み完了');

        // ページタイトルを確認
        const title = await page.title();
        console.log(`📄 ページタイトル: ${title}`);

        // Vueアプリが読み込まれるまで待機
        await page.waitForSelector('#app', { timeout: 10000 });
        console.log('✅ Vue.jsアプリケーション読み込み完了');

        // ページの基本構造を確認
        const hasTopComponent = await page.$('top-component');
        console.log(`🔍 TopComponent要素: ${hasTopComponent ? '存在' : '未発見'}`);

        // テスト用のデータ入力を試行
        console.log('📝 テストデータ入力開始...');

        const testData = {
            year: '1990',
            month: '5',
            day: '15',
            sex: '男'
        };

        // Vue.jsコンポーネントにデータを設定
        const result = await page.evaluate((data) => {
            try {
                // Vueアプリケーションインスタンスにアクセス
                const app = document.querySelector('#app').__vue__;
                if (!app) return { success: false, error: 'Vue app not found' };

                // TopComponentを探す
                const topComponent = app.$children.find(child =>
                    child.$options.name === 'TopComponent' ||
                    child.selectYear !== undefined
                );

                if (!topComponent) return { success: false, error: 'TopComponent not found' };

                // データを設定
                topComponent.selectYear = data.year;
                topComponent.selectMonth = data.month;
                topComponent.selectDay = data.day;
                topComponent.selectSex = data.sex;

                return {
                    success: true,
                    message: 'データ設定完了',
                    componentData: {
                        year: topComponent.selectYear,
                        month: topComponent.selectMonth,
                        day: topComponent.selectDay,
                        sex: topComponent.selectSex
                    }
                };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }, testData);

        console.log('📊 データ入力結果:', JSON.stringify(result, null, 2));

        // 3秒待機してスクリーンショットを撮る
        await page.waitForTimeout(3000);
        await page.screenshot({
            path: '/tmp/kyusei_test.png',
            fullPage: true
        });
        console.log('📸 スクリーンショット保存: /tmp/kyusei_test.png');

        return result;

    } catch (error) {
        console.error('❌ エラー発生:', error.message);
        return { success: false, error: error.message };
    } finally {
        await browser.close();
        console.log('🔚 ブラウザクローズ完了');
    }
}

// 実行
if (require.main === module) {
    testKyuseiSystem()
        .then(result => {
            console.log('\n🎉 テスト完了');
            console.log('結果:', JSON.stringify(result, null, 2));
        })
        .catch(error => {
            console.error('💥 テスト失敗:', error);
            process.exit(1);
        });
}