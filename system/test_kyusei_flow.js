#!/usr/bin/env node
/**
 * 九星気学システムの動作フロー詳細テスト
 */

const puppeteer = require('puppeteer');

async function testKyuseiFlow() {
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

        console.log('🔗 九星気学システムアクセス中...');

        // トップページアクセス
        await page.goto('http://localhost:3001/ban_top_full.html', {
            waitUntil: 'networkidle0',
            timeout: 15000
        });

        console.log('✅ トップページ読み込み完了');

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000);

        // ページ構造の詳細調査
        const pageStructure = await page.evaluate(() => {
            const app = document.querySelector('#app');
            if (!app) return { error: '#app not found' };

            const vueInstance = app.__vue__;
            if (!vueInstance) return { error: 'Vue instance not found' };

            // すべてのボタンとリンクを探す
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], a')).map(el => ({
                tagName: el.tagName,
                className: el.className,
                textContent: el.textContent?.trim(),
                href: el.href,
                onclick: el.onclick ? el.onclick.toString() : null
            }));

            return {
                hasApp: true,
                hasVueInstance: true,
                buttons: buttons,
                bodyHTML: document.body.innerHTML
            };
        });

        console.log('🔍 ページ構造詳細:');
        console.log('ボタン一覧:', JSON.stringify(pageStructure.buttons, null, 2));

        // テストデータ入力
        console.log('📝 データ入力中...');
        const inputResult = await page.evaluate(() => {
            try {
                const app = document.querySelector('#app').__vue__;
                const topComponent = app.$children.find(child =>
                    child.$options.name === 'TopComponent' || child.selectYear !== undefined
                );

                if (topComponent) {
                    topComponent.selectYear = '1990';
                    topComponent.selectMonth = '5';
                    topComponent.selectDay = '15';
                    topComponent.selectSex = '男';

                    return {
                        success: true,
                        data: {
                            year: topComponent.selectYear,
                            month: topComponent.selectMonth,
                            day: topComponent.selectDay,
                            sex: topComponent.selectSex
                        }
                    };
                }
                return { success: false, error: 'TopComponent not found' };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });

        console.log('📊 入力結果:', JSON.stringify(inputResult, null, 2));

        // 九星調査ボタンを探してクリック
        console.log('🔍 ボタン検索中...');

        // より具体的なセレクタでボタンを探す
        const clickResult = await page.evaluate(() => {
            // 可能性のあるセレクタを試す
            const selectors = [
                'span.button.beju:first-of-type a',
                'span.button a',
                '.button a',
                'a[href*="birthday"]',
                'button',
                'input[type="submit"]'
            ];

            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    console.log(`Found element with selector: ${selector}`);
                    element.click();
                    return { success: true, selector: selector, element: element.outerHTML };
                }
            }

            return { success: false, error: 'No clickable element found' };
        });

        console.log('🖱️ クリック結果:', JSON.stringify(clickResult, null, 2));

        // クリック後の動作を待機
        if (clickResult.success) {
            console.log('⏳ ページ遷移またはレスポンス待機中...');

            try {
                // ナビゲーション待機（URLが変わる場合）
                await Promise.race([
                    page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }),
                    page.waitForTimeout(5000) // 5秒でタイムアウト
                ]);
            } catch (navError) {
                console.log('⚠️ ナビゲーション待機エラー（Ajax処理の可能性）:', navError.message);
            }

            // 現在のページ状態を確認
            const finalState = await page.evaluate(() => ({
                url: location.href,
                title: document.title,
                hasNewContent: !!document.querySelector('birthday-component')
            }));

            console.log('🏁 最終状態:', JSON.stringify(finalState, null, 2));
        }

        // スクリーンショット保存
        await page.screenshot({
            path: '/tmp/kyusei_flow_test.png',
            fullPage: true
        });
        console.log('📸 スクリーンショット: /tmp/kyusei_flow_test.png');

    } catch (error) {
        console.error('❌ エラー:', error.message);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

testKyuseiFlow();