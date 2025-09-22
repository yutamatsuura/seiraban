#!/usr/bin/env node

/**
 * Puppeteer Bridge for Existing Systems
 * 既存の九星気学・姓名判断システムをPuppeteerで制御して結果を取得
 */

const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');

// 引数解析
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node puppeteer_bridge.js <system_type> <input_json>');
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
                await executeKyusei(inputData);
                break;
            case 'seimei':
                await executeSeimei(inputData);
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
 * 九星気学システムをPuppeteerで実行
 */
async function executeKyusei(inputData) {
    const systemDir = path.join(__dirname, 'kyuuseikigaku-kichihoui');
    let devServer = null;
    let browser = null;

    try {
        // 開発サーバー起動
        devServer = await startDevServerWebpack(systemDir, 3001);
        await waitForServer('http://localhost:3001', 30000);

        // ブラウザ起動
        browser = await puppeteer.launch({
            headless: "new",
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        });
        const page = await browser.newPage();

        // 九星気学ページにアクセス
        await page.goto('http://localhost:3001/ban_birthday.html', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Vue.jsコンポーネントの読み込み待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000); // Vue.js初期化待機

        // 入力データを設定
        const { birth_date, gender } = inputData;
        const birthDate = new Date(birth_date);
        const year = birthDate.getFullYear();
        const month = birthDate.getMonth() + 1;
        const day = birthDate.getDate();

        // フォーム入力
        await page.evaluate((year, month, day) => {
            // Vue.jsコンポーネントのデータを直接操作
            const app = document.querySelector('#app').__vue__;
            if (app && app.$children && app.$children[0]) {
                const component = app.$children[0];
                if (component.setDate) {
                    component.setDate(year, month, day);
                } else {
                    // 直接input要素に値を設定
                    const yearInput = document.querySelector('input[type="number"]');
                    const monthSelect = document.querySelector('select');
                    const daySelect = document.querySelectorAll('select')[1];

                    if (yearInput) yearInput.value = year;
                    if (monthSelect) monthSelect.value = month;
                    if (daySelect) daySelect.value = day;

                    // イベントトリガー
                    [yearInput, monthSelect, daySelect].forEach(el => {
                        if (el) {
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                }
            }
        }, year, month, day);

        // 計算ボタンクリック
        await page.click('button, input[type="submit"], .submit-btn, .calculate-btn');

        // 結果の表示待機
        await page.waitForTimeout(3000);

        // 結果を取得
        const result = await page.evaluate(() => {
            // 九星気学の結果を抽出
            const resultElements = document.querySelectorAll('.result, .kyusei-result, .star-result');
            const honmei = document.querySelector('.honmei, .main-star')?.textContent?.trim();
            const gekkei = document.querySelector('.gekkei, .month-star')?.textContent?.trim();
            const nichimei = document.querySelector('.nichimei, .day-star')?.textContent?.trim();

            // 盤面データの取得
            const banData = document.querySelector('.ban-data, .kyusei-ban')?.textContent?.trim();

            // 吉方位の取得
            const kichihoui = document.querySelector('.kichihoui, .lucky-direction')?.textContent?.trim();

            return {
                honmei: honmei || 'データ取得失敗',
                gekkei: gekkei || 'データ取得失敗',
                nichimei: nichimei || 'データ取得失敗',
                ban_data: banData || 'データ取得失敗',
                kichihoui: kichihoui || 'データ取得失敗',
                page_content: document.body.innerHTML.substring(0, 1000) // デバッグ用
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
        if (devServer) devServer.kill();
    }
}

/**
 * 姓名判断システムをPuppeteerで実行
 */
async function executeSeimei(inputData) {
    const systemDir = path.join(__dirname, 'seimeihandan');
    let devServer = null;
    let browser = null;

    try {
        // 開発サーバー起動
        devServer = await startDevServerWebpack(systemDir, 3001);
        await waitForServer('http://localhost:3001', 30000);

        // ブラウザ起動
        browser = await puppeteer.launch({
            headless: "new",
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        });
        const page = await browser.newPage();

        // 姓名判断ページにアクセス
        await page.goto('http://localhost:3001/seimei.html', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Vue.jsコンポーネントの読み込み待機
        await page.waitForSelector('#app', { timeout: 10000 });
        await page.waitForTimeout(2000); // Vue.js初期化待機

        // 姓名入力
        const { name } = inputData;
        const nameParts = name.split(' ');
        const sei = nameParts[0] || '';
        const mei = nameParts[1] || '';

        // フォーム入力
        await page.evaluate((sei, mei) => {
            // Vue.jsコンポーネントのデータを直接操作
            const app = document.querySelector('#app').__vue__;
            if (app && app.$children && app.$children[0]) {
                const component = app.$children[0];
                if (component.sei !== undefined) {
                    component.sei = sei;
                    component.mei = mei;
                } else {
                    // 直接input要素に値を設定
                    const seiInput = document.querySelector('input[placeholder*="姓"], input[name="sei"]');
                    const meiInput = document.querySelector('input[placeholder*="名"], input[name="mei"]');

                    if (seiInput) seiInput.value = sei;
                    if (meiInput) meiInput.value = mei;

                    // イベントトリガー
                    [seiInput, meiInput].forEach(el => {
                        if (el) {
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                }
            }
        }, sei, mei);

        // 計算ボタンクリック
        await page.click('button, input[type="submit"], .submit-btn, .calculate-btn');

        // 結果の表示待機
        await page.waitForTimeout(5000); // 外部API呼び出し待機

        // 結果を取得
        const result = await page.evaluate(() => {
            // 姓名判断の結果を抽出
            const tenkaku = document.querySelector('.tenkaku, .ten-kaku')?.textContent?.trim();
            const jinkaku = document.querySelector('.jinkaku, .jin-kaku')?.textContent?.trim();
            const chikaku = document.querySelector('.chikaku, .chi-kaku')?.textContent?.trim();
            const soukaku = document.querySelector('.soukaku, .sou-kaku')?.textContent?.trim();
            const gaikaku = document.querySelector('.gaikaku, .gai-kaku')?.textContent?.trim();

            // 総合評価
            const evaluation = document.querySelector('.evaluation, .total-score')?.textContent?.trim();

            // エラーメッセージ
            const errorMsg = document.querySelector('.error, .alert-danger')?.textContent?.trim();

            return {
                tenkaku: tenkaku || 'データ取得失敗',
                jinkaku: jinkaku || 'データ取得失敗',
                chikaku: chikaku || 'データ取得失敗',
                soukaku: soukaku || 'データ取得失敗',
                gaikaku: gaikaku || 'データ取得失敗',
                evaluation: evaluation || 'データ取得失敗',
                error: errorMsg || null,
                page_content: document.body.innerHTML.substring(0, 1000) // デバッグ用
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
        if (devServer) devServer.kill();
    }
}

/**
 * Webpack開発サーバー起動
 */
function startDevServerWebpack(systemDir, port) {
    return new Promise((resolve, reject) => {
        const server = spawn('npx', ['webpack-dev-server', '--config', 'webpack.config.debug.js'], {
            cwd: systemDir,
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, NODE_OPTIONS: '--openssl-legacy-provider' }
        });

        server.stdout.on('data', (data) => {
            const output = data.toString();
            console.error('Dev server:', output); // stderr に出力
        });

        server.stderr.on('data', (data) => {
            console.error('Dev server error:', data.toString());
        });

        server.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Dev server exited with code ${code}`));
            }
        });

        // サーバー起動を少し待つ
        setTimeout(() => resolve(server), 5000);
    });
}

/**
 * サーバーの起動待機
 */
function waitForServer(url, timeout = 30000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        function check() {
            const http = require('http');
            const request = http.get(url, (res) => {
                resolve();
            });

            request.on('error', () => {
                if (Date.now() - startTime > timeout) {
                    reject(new Error('Server startup timeout'));
                } else {
                    setTimeout(check, 1000);
                }
            });
        }

        check();
    });
}

main();