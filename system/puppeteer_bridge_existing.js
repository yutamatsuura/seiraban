#!/usr/bin/env node

/**
 * Puppeteer Bridge for Existing Systems (For Running Servers)
 * 既存起動中サーバー用のPuppeteerブリッジ
 */

const puppeteer = require('puppeteer');

// 引数解析
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node puppeteer_bridge_existing.js <system_type> <input_json>');
    console.error('system_type: kyusei | seimei');
    process.exit(1);
}

const systemType = args[0];
const inputJson = args[1];

async function main() {
    try {
        const inputData = JSON.parse(inputJson);

        switch (systemType) {
            case 'kyusei':
                await executeKyuseiExisting(inputData);
                break;
            case 'seimei':
                await executeSeimeiExisting(inputData);
                break;
            default:
                throw new Error(`Unknown system type: ${systemType}`);
        }
    } catch (error) {
        console.error(JSON.stringify({
            success: false,
            error: error.message,
            stack: error.stack
        }));
        process.exit(1);
    }
}

/**
 * 九星気学システム（既存サーバー使用）
 */
async function executeKyuseiExisting(inputData) {
    let browser = null;

    try {
        // ブラウザ起動
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

        // 入力データの解析
        const { birth_date, gender } = inputData;
        const birthDate = new Date(birth_date);
        const year = String(birthDate.getFullYear());
        const month = String(birthDate.getMonth() + 1);
        const day = String(birthDate.getDate());
        const sex = gender === 'female' ? '女' : '男';

        // ステップ1: トップページで入力
        await page.goto('http://localhost:3001/ban_top_full.html', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000);

        // フォーム入力
        await page.evaluate((year, month, day, sex) => {
            const app = document.querySelector('#app').__vue__;
            const topComponent = app.$children.find(child =>
                child.$options.name === 'TopComponent' || child.selectYear !== undefined
            );

            if (topComponent) {
                topComponent.selectYear = year;
                topComponent.selectMonth = month;
                topComponent.selectDay = day;
                topComponent.selectSex = sex;
            }
        }, year, month, day, sex);

        // 「九星を調べる」ボタンクリック
        await page.click('span.button.beju:first-of-type a');

        // ページ遷移待機 (ban_birthday.phpへ)
        await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 });

        // 結果の取得
        await page.waitForTimeout(3000); // Vue.js結果描画待機

        const result = await page.evaluate(() => {
            const pageData = {
                page_title: document.title,
                page_url: location.href,
                full_text: document.body.textContent
            };

            // テキストから九星気学の結果を抽出
            const text = document.body.textContent;

            // 生年月日の抽出
            const birthdayMatch = text.match(/生年月日：(\d{4}年\d{1,2}月\d{1,2}日)\s*\((\d+)歳\)/);
            const birthday = birthdayMatch ? birthdayMatch[1] : null;
            const age = birthdayMatch ? parseInt(birthdayMatch[2]) : null;

            // 十二支の抽出
            const etoMatch = text.match(/十二支：([^）\s]+)/);
            const eto = etoMatch ? etoMatch[1] : null;

            // 年干支、月干支、日干支の抽出
            const yearKanshiMatch = text.match(/年干支\s+([^\s]+)/);
            const monthKanshiMatch = text.match(/月干支\s+([^\s]+)/);
            const dayKanshiMatch = text.match(/日干支\s+([^\s]+)/);

            // 納音の抽出
            const naonMatch = text.match(/納音\s+([^\s]+)/);

            // 最大吉方の抽出
            const maxKichigataMatch = text.match(/最大吉方\s+([^\s]+)/);

            // 吉方の抽出
            const kichigataMatch = text.match(/吉方\s+([^\s]+)/);

            return {
                success: true,
                birthday: birthday,
                age: age,
                eto: eto,
                year_kanshi: yearKanshiMatch ? yearKanshiMatch[1] : null,
                month_kanshi: monthKanshiMatch ? monthKanshiMatch[1] : null,
                day_kanshi: dayKanshiMatch ? dayKanshiMatch[1] : null,
                naon: naonMatch ? naonMatch[1] : null,
                max_kichigata: maxKichigataMatch ? maxKichigataMatch[1] : null,
                kichigata: kichigataMatch ? kichigataMatch[1] : null,
                raw_data: pageData
            };
        });

        console.log(JSON.stringify({
            success: true,
            type: 'kyusei',
            input: inputData,
            result: result
        }));

    } catch (error) {
        throw new Error(`九星気学システム実行エラー: ${error.message}`);
    } finally {
        if (browser) await browser.close();
    }
}

/**
 * 姓名判断システム（既存サーバー使用）
 */
async function executeSeimeiExisting(inputData) {
    let browser = null;

    try {
        // ブラウザ起動
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-chrome-browser-cloud-management'
            ]
        });
        const page = await browser.newPage();

        // 姓名判断ページアクセス
        await page.goto('http://localhost:3001/seimei.html', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000);

        // 姓名入力
        const { name } = inputData;
        const nameParts = name.split(' ');
        const sei = nameParts[0] || '';
        const mei = nameParts[1] || '';

        // SearchComponentに入力
        await page.evaluate((sei, mei) => {
            const app = document.querySelector('#app').__vue__;
            const searchComponent = app.$children.find(child =>
                child.$options.name === 'SearchComponent' || child.sei !== undefined
            );

            if (searchComponent) {
                searchComponent.sei = sei;
                searchComponent.mei = mei;

                // 外部API呼び出し実行
                searchComponent.submitKantei();
            }
        }, sei, mei);

        // 外部API呼び出し＆結果表示待機
        await page.waitForTimeout(5000);

        // 結果取得
        const result = await page.evaluate(() => {
            const app = document.querySelector('#app').__vue__;
            const searchComponent = app.$children.find(child =>
                child.sei !== undefined
            );

            if (searchComponent) {
                return {
                    sei: searchComponent.sei,
                    mei: searchComponent.mei,
                    error: searchComponent.error,
                    calculation_completed: !searchComponent.error
                };
            }

            return {
                page_url: location.href,
                page_title: document.title,
                error_msg: 'Vue.jsコンポーネント取得失敗'
            };
        });

        console.log(JSON.stringify({
            success: true,
            type: 'seimei',
            input: inputData,
            result: result
        }));

    } catch (error) {
        throw new Error(`姓名判断システム実行エラー: ${error.message}`);
    } finally {
        if (browser) await browser.close();
    }
}

main();