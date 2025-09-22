#!/usr/bin/env node
/**
 * 九星気学システム結果ページの詳細調査
 */

const puppeteer = require('puppeteer');

async function testResultPage() {
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

        console.log('🔗 結果ページへ直接アクセス中...');

        // まず結果ページに直接アクセスしてみる
        await page.goto('http://localhost:3001/qsei/ban_birthday.php', {
            waitUntil: 'networkidle0',
            timeout: 15000
        });

        console.log('✅ 結果ページアクセス完了');

        // ページ構造の詳細調査
        const pageInfo = await page.evaluate(() => {
            return {
                title: document.title,
                url: location.href,
                hasApp: !!document.querySelector('#app'),
                hasBirthdayComponent: !!document.querySelector('birthday-component'),
                bodyText: document.body.textContent.substring(0, 500),
                bodyHTML: document.body.innerHTML.substring(0, 1000),
                scripts: Array.from(document.querySelectorAll('script')).map(s => s.src || s.textContent.substring(0, 100))
            };
        });

        console.log('📄 結果ページ詳細:');
        console.log(JSON.stringify(pageInfo, null, 2));

        // 正しいフローでアクセス
        console.log('\n🔄 正しいフローでアクセス中...');

        await page.goto('http://localhost:3001/ban_top_full.html', {
            waitUntil: 'networkidle0',
            timeout: 15000
        });

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000);

        // データ入力
        await page.evaluate(() => {
            const app = document.querySelector('#app').__vue__;
            const topComponent = app.$children.find(child =>
                child.$options.name === 'TopComponent' || child.selectYear !== undefined
            );

            if (topComponent) {
                topComponent.selectYear = '1990';
                topComponent.selectMonth = '5';
                topComponent.selectDay = '15';
                topComponent.selectSex = '男';
            }
        });

        // ボタンクリック
        await page.click('span.button.beju:first-of-type a');

        // ページ遷移待機
        await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 });

        console.log('✅ 結果ページ遷移完了');

        // Vue.js結果描画待機
        await page.waitForTimeout(3000);

        // 結果データ取得
        const resultData = await page.evaluate(() => {
            const pageInfo = {
                title: document.title,
                url: location.href,
                hasApp: !!document.querySelector('#app'),
                hasBirthdayComponent: !!document.querySelector('birthday-component')
            };

            // Vue.jsインスタンス探索
            let vueData = null;
            const app = document.querySelector('#app');
            if (app && app.__vue__) {
                const vueInstance = app.__vue__;

                // BirthdayComponentを探す
                const birthdayComponent = vueInstance.$children.find(child =>
                    child.$options.name === 'BirthdayComponent' ||
                    child.birthday !== undefined
                );

                if (birthdayComponent) {
                    vueData = {
                        birthday: birthdayComponent.birthday,
                        age: birthdayComponent.age,
                        yearQseiName: birthdayComponent.yearQseiName,
                        monthQseiName: birthdayComponent.monthQseiName,
                        dayQseiName: birthdayComponent.dayQseiName,
                        eto60: birthdayComponent.eto60
                    };
                }
            }

            // DOMから直接データ取得
            const domData = {
                bodyText: document.body.textContent.substring(0, 500),
                allText: Array.from(document.querySelectorAll('*')).map(el => el.textContent?.trim()).filter(t => t && t.length > 5).slice(0, 10)
            };

            return {
                pageInfo,
                vueData,
                domData
            };
        });

        console.log('📊 結果データ:');
        console.log(JSON.stringify(resultData, null, 2));

        // スクリーンショット保存
        await page.screenshot({
            path: '/tmp/kyusei_result_page.png',
            fullPage: true
        });
        console.log('📸 スクリーンショット: /tmp/kyusei_result_page.png');

    } catch (error) {
        console.error('❌ エラー:', error.message);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

testResultPage();