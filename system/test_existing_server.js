#!/usr/bin/env node
/**
 * 既存サーバー専用Puppeteerテスト
 */

const puppeteer = require('puppeteer');

async function testExistingServer() {
    let browser;

    try {
        // ブラウザ起動（明示的なパス指定）
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-extensions',
                '--disable-sync',
                '--disable-default-apps',
                '--disable-chrome-browser-cloud-management'
            ],
            timeout: 0
        });

        const page = await browser.newPage();

        // ユーザーエージェント設定
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');

        console.log('🔗 九星気学システム（既存サーバー）にアクセス中...');

        // まずサーバーが動いているか確認
        try {
            await page.goto('http://localhost:3001/ban_top_full.html', {
                waitUntil: 'networkidle0',
                timeout: 15000
            });
        } catch (error) {
            console.log('❌ localhost:3001へのアクセスに失敗しました');
            console.log('サーバーが起動していない可能性があります');
            throw error;
        }

        console.log('✅ ページ読み込み完了');

        // ページタイトル確認
        const title = await page.title();
        console.log(`📄 ページタイトル: ${title}`);

        // Vue.jsアプリ読み込み待機
        try {
            await page.waitForSelector('#app', { timeout: 10000 });
            console.log('✅ Vue.jsアプリケーション検出完了');
        } catch (error) {
            console.log('⚠️ #app要素が見つかりません');
        }

        // DOM構造を確認
        const pageInfo = await page.evaluate(() => {
            return {
                hasApp: !!document.querySelector('#app'),
                hasTopComponent: !!document.querySelector('top-component'),
                hasVueInstance: !!(document.querySelector('#app') && document.querySelector('#app').__vue__),
                bodyHTML: document.body.innerHTML.substring(0, 500)
            };
        });

        console.log('🔍 ページ構造:', JSON.stringify(pageInfo, null, 2));

        // テストデータ入力試行
        console.log('📝 テストデータ入力開始...');

        const testData = {
            year: '1990',
            month: '5',
            day: '15',
            sex: '男'
        };

        const inputResult = await page.evaluate((data) => {
            try {
                const app = document.querySelector('#app');
                if (!app) return { success: false, error: '#app要素が見つかりません' };

                const vueInstance = app.__vue__;
                if (!vueInstance) return { success: false, error: 'Vue.jsインスタンスが見つかりません' };

                // TopComponentを探す
                let topComponent = null;

                // 方法1: $childrenから探す
                if (vueInstance.$children) {
                    topComponent = vueInstance.$children.find(child =>
                        child.$options.name === 'TopComponent' ||
                        child.selectYear !== undefined
                    );
                }

                if (!topComponent) {
                    return {
                        success: false,
                        error: 'TopComponentが見つかりません',
                        debugInfo: {
                            hasChildren: !!vueInstance.$children,
                            childrenCount: vueInstance.$children ? vueInstance.$children.length : 0
                        }
                    };
                }

                // データ設定
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
                return { success: false, error: error.message, stack: error.stack };
            }
        }, testData);

        console.log('📊 データ入力結果:', JSON.stringify(inputResult, null, 2));

        // スクリーンショット撮影
        await page.waitForTimeout(2000);
        await page.screenshot({
            path: '/tmp/kyusei_existing_test.png',
            fullPage: true
        });
        console.log('📸 スクリーンショット保存: /tmp/kyusei_existing_test.png');

        return {
            success: true,
            pageInfo: pageInfo,
            inputResult: inputResult,
            title: title
        };

    } catch (error) {
        console.error('❌ エラー発生:', error.message);
        return { success: false, error: error.message, stack: error.stack };
    } finally {
        if (browser) {
            await browser.close();
            console.log('🔚 ブラウザクローズ完了');
        }
    }
}

// 実行
if (require.main === module) {
    testExistingServer()
        .then(result => {
            console.log('\n🎉 テスト完了');
            console.log('結果:', JSON.stringify(result, null, 2));
            process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
            console.error('💥 テスト失敗:', error);
            process.exit(1);
        });
}

module.exports = { testExistingServer };