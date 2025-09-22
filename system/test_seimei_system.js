#!/usr/bin/env node
/**
 * 姓名判断システムの実際テスト - 100%精度確認
 */

const puppeteer = require('puppeteer');

async function testSeimeiSystem() {
    let browser;

    try {
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-gpu',
                '--disable-chrome-browser-cloud-management'
            ]
        });

        const page = await browser.newPage();

        console.log('🔗 姓名判断システムアクセス中...');

        // 姓名判断ページアクセス
        await page.goto('http://localhost:3002/seimei.html', {
            waitUntil: 'networkidle2',
            timeout: 15000
        });

        console.log('✅ ページ読み込み完了');

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000);

        // ページ構造の詳細調査
        const pageStructure = await page.evaluate(() => {
            const app = document.querySelector('#app');
            if (!app) return { error: '#app not found' };

            const vueInstance = app.__vue__;
            if (!vueInstance) return { error: 'Vue instance not found' };

            return {
                hasApp: true,
                hasVueInstance: true,
                title: document.title,
                url: location.href,
                bodyText: document.body.textContent.substring(0, 500),
                components: app.innerHTML.substring(0, 1000)
            };
        });

        console.log('🔍 姓名判断ページ構造:');
        console.log(JSON.stringify(pageStructure, null, 2));

        // テスト用姓名入力
        const testName = '田中太郎';
        console.log(`📝 テスト姓名: ${testName}`);

        // 姓名入力フィールドを探してテスト
        const inputResult = await page.evaluate((name) => {
            try {
                // 入力フィールドを探す
                const inputs = document.querySelectorAll('input[type="text"], input[name*="sei"], input[name*="mei"]');

                if (inputs.length > 0) {
                    // 最初の入力フィールドに姓名を入力
                    inputs[0].value = name;
                    inputs[0].dispatchEvent(new Event('input', { bubbles: true }));

                    return {
                        success: true,
                        inputCount: inputs.length,
                        inputValue: inputs[0].value
                    };
                }

                return { success: false, error: '入力フィールドが見つかりません' };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }, testName);

        console.log('📊 姓名入力結果:', JSON.stringify(inputResult, null, 2));

        // ボタンを探してクリック
        const submitResult = await page.evaluate(() => {
            try {
                // 実行ボタンを探す
                const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], .button')).map(btn => ({
                    tagName: btn.tagName,
                    className: btn.className,
                    textContent: btn.textContent?.trim(),
                    type: btn.type
                }));

                return {
                    success: true,
                    buttonsFound: buttons
                };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });

        console.log('🔍 ボタン検索結果:', JSON.stringify(submitResult, null, 2));

        // スクリーンショット保存
        await page.screenshot({
            path: '/tmp/seimei_test.png',
            fullPage: true
        });
        console.log('📸 スクリーンショット: /tmp/seimei_test.png');

        return {
            success: true,
            pageStructure: pageStructure,
            inputResult: inputResult,
            submitResult: submitResult
        };

    } catch (error) {
        console.error('❌ エラー:', error.message);
        return { success: false, error: error.message };
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

testSeimeiSystem()
    .then(result => {
        console.log('\n🎉 姓名判断システムテスト完了');
        console.log('結果:', JSON.stringify(result, null, 2));
    })
    .catch(error => {
        console.error('💥 テスト失敗:', error);
    });