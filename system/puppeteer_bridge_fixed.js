#!/usr/bin/env node

/**
 * Puppeteer Bridge for Existing Systems (Fixed Version)
 * 既存システムの正確な動作フローに基づいた実装
 */

const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');

// 引数解析
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node puppeteer_bridge_fixed.js <system_type> <input_json>');
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
                await executeKyuseiFixed(inputData);
                break;
            case 'seimei':
                await executeSeimeiFixed(inputData);
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
 * 九星気学システム（正確な実装）
 */
async function executeKyuseiFixed(inputData) {
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
        await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 30000 });

        // 結果の取得
        await page.waitForTimeout(3000); // Vue.js結果描画待機

        const result = await page.evaluate(() => {
            // BirthdayComponentから結果を取得
            const birthdayData = document.querySelector('birthday-component');
            if (birthdayData) {
                const vueInstance = birthdayData.__vue__;
                if (vueInstance) {
                    return {
                        birthday: vueInstance.birthday || 'データなし',
                        age: vueInstance.age || 0,
                        yearQseiName: vueInstance.yearQseiName || 'データなし',
                        monthQseiName: vueInstance.monthQseiName || 'データなし',
                        dayQseiName: vueInstance.dayQseiName || 'データなし',
                        eto60: vueInstance.eto60 ? {
                            name: vueInstance.eto60.name,
                            lastName: vueInstance.eto60.lastName
                        } : null
                    };
                }
            }

            // フォールバック: HTML要素から直接取得
            return {
                birthday: document.querySelector('[data-birthday]')?.textContent?.trim() || 'HTML解析失敗',
                page_title: document.title,
                page_url: location.href,
                localStorage_data: {
                    year: localStorage.getItem('kiban_year'),
                    month: localStorage.getItem('kiban_month'),
                    day: localStorage.getItem('kiban_day'),
                    sex: localStorage.getItem('kiban_sex')
                }
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
 * 姓名判断システム（正確な実装）
 */
async function executeSeimeiFixed(inputData) {
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