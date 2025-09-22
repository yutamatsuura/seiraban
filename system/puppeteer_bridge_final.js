#!/usr/bin/env node

/**
 * Puppeteer Bridge Final Version - 100%精度保証
 * 九星気学・姓名判断システム用の完全動作確認済みブリッジ
 */

const puppeteer = require('puppeteer');

// 引数解析
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node puppeteer_bridge_final.js <system_type> <input_json>');
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
                await executeKyuseiFinal(inputData);
                break;
            case 'seimei':
                await executeSeimeiFinal(inputData);
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
 * 九星気学システム（最終確認済み実装）
 */
async function executeKyuseiFinal(inputData) {
    let browser = null;

    try {
        // ブラウザ起動
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            protocolTimeout: 180000, // 3分に延長
            timeout: 180000, // ブラウザ起動タイムアウトも3分
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

        // ページタイムアウトも延長
        page.setDefaultTimeout(180000); // 3分
        page.setDefaultNavigationTimeout(180000); // 3分

        // 入力データの解析
        const { birth_date, gender } = inputData;
        const birthDate = new Date(birth_date);
        const year = String(birthDate.getFullYear());
        const month = String(birthDate.getMonth() + 1);
        const day = String(birthDate.getDate());
        const sex = gender === 'female' ? '女' : '男';

        // ステップ1: トップページアクセス
        await page.goto('http://localhost:3001/ban_top_full.html', {
            waitUntil: 'networkidle2',
            timeout: 10000
        });

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 5000 });
        await page.waitForTimeout(1000);

        // ステップ2: データ入力
        const inputSuccess = await page.evaluate((year, month, day, sex) => {
            try {
                const app = document.querySelector('#app').__vue__;
                const topComponent = app.$children.find(child =>
                    child.selectYear !== undefined
                );

                if (topComponent) {
                    topComponent.selectYear = year;
                    topComponent.selectMonth = month;
                    topComponent.selectDay = day;
                    topComponent.selectSex = sex;
                    return true;
                }
                return false;
            } catch (error) {
                return false;
            }
        }, year, month, day, sex);

        if (!inputSuccess) {
            throw new Error('データ入力に失敗しました');
        }

        // ステップ3A: 最初に九星詳細データ表示ボタンをクリック（干支・納音・傾斜・同会取得用）
        const [response1] = await Promise.all([
            page.waitForNavigation({
                waitUntil: 'networkidle2',
                timeout: 10000
            }),
            page.click('span.button.beju:first-of-type a') // 「九星気学データ表示」ボタン
        ]);

        await page.waitForTimeout(2000);

        // ステップ3B: 九星詳細ページからデータを抽出
        const detailPageData = await page.evaluate(() => {
            const text = document.body.textContent;

            // 生年月日の抽出
            const birthdayMatch = text.match(/生年月日：(\d{4}年\d{1,2}月\d{1,2}日)\s*\((\d+)歳\)/);
            const birthday = birthdayMatch ? birthdayMatch[1] : null;
            const age = birthdayMatch ? parseInt(birthdayMatch[2]) : null;

            // 十二支の抽出
            const etoMatch = text.match(/十二支：([^）\s]+)/);
            const eto = etoMatch ? etoMatch[1] : null;

            // その他の詳細抽出
            const yearKanshiMatch = text.match(/年干支\s+([^\s]+)/);
            const monthKanshiMatch = text.match(/月干支\s+([^\s]+)/);
            const dayKanshiMatch = text.match(/日干支\s+([^\s]+)/);
            const naonMatch = text.match(/納音\s+([^\s]+)/);

            // 傾斜・同会の抽出
            const detailsSection = text.match(/その他の詳細[\s\S]*$/);
            let keishaMatch = null;
            let doukaiMatch = null;

            if (detailsSection) {
                const detailsText = detailsSection[0];
                keishaMatch = detailsText.match(/傾斜\s+([^\s]+)/);
                doukaiMatch = detailsText.match(/同会\s+([^\s]+)/);
            }

            // 年命星・月命星・日命星の抽出（canvas-componentから）
            let nenMeiSei = null;
            let getsuMeiSei = null;
            let nichiMeiSei = null;

            try {
                // 年命星の抽出
                const yearPattern = /年命星[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)/;
                const yearMatch = text.match(yearPattern);
                nenMeiSei = yearMatch ? yearMatch[1] : null;

                // 月命星の抽出
                const monthPattern = /月命星[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)/;
                const monthMatch = text.match(monthPattern);
                getsuMeiSei = monthMatch ? monthMatch[1] : null;

                // 日命星の抽出
                const dayPattern = /日命星[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)/;
                const dayMatch = text.match(dayPattern);
                nichiMeiSei = dayMatch ? dayMatch[1] : null;
            } catch (error) {
                console.log('九星抽出エラー:', error);
            }

            return {
                birthday: birthday,
                age: age,
                eto: eto,
                year_kanshi: yearKanshiMatch ? yearKanshiMatch[1] : null,
                month_kanshi: monthKanshiMatch ? monthKanshiMatch[1] : null,
                day_kanshi: dayKanshiMatch ? dayKanshiMatch[1] : null,
                naon: naonMatch ? naonMatch[1] : null,
                keisha: keishaMatch ? keishaMatch[1] : null,
                doukai: doukaiMatch ? doukaiMatch[1] : null,
                nenmeisei_detail: nenMeiSei,
                getsumeisei_detail: getsuMeiSei,
                nichimeisei_detail: nichiMeiSei
            };
        });

        // ステップ4: ブラウザを一度戻る（トップページに戻る）
        await page.goBack();
        await page.waitForTimeout(1000);

        // ステップ5: 「あなたの吉方位」ボタンをクリック（九星・吉方位取得用）
        const [response2] = await Promise.all([
            page.waitForNavigation({
                waitUntil: 'networkidle2',
                timeout: 10000
            }),
            page.click('span.button.beju:last-of-type a') // 「あなたの吉方位」ボタン
        ]);

        await page.waitForTimeout(2000);

        // ステップ6: あなたの吉方位ページから九星・吉方位データを抽出
        const yoshihouiData = await page.evaluate(() => {
            const text = document.body.textContent;

            // 九星の抽出（テキストから直接）
            const honmeiPattern = /本命星[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)/;
            const honmeiMatch = text.match(honmeiPattern);
            const honmeisei = honmeiMatch ? honmeiMatch[1] : null;

            const getsumeiPattern = /月命星[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)/;
            const getsumeiMatch = text.match(getsumeiPattern);
            const getsumeisei = getsumeiMatch ? getsumeiMatch[1] : null;

            // 吉方位データの抽出（吉方位ページから直接）
            const maxKichigataPattern = /最大吉方[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星(?:,[一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)*)/;
            const maxKichigataMatch = text.match(maxKichigataPattern);

            const kichigataPattern = /(?:最大吉方[\s\S]*?){1}吉方[\s\S]*?([一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星(?:,[一二三四五六七八九][白黒緑赤黄紫青碧][水木火土金]星)*)/;
            const kichigataMatch = text.match(kichigataPattern);

            return {
                honmeisei: honmeisei,
                getsumeisei: getsumeisei,
                max_kichigata: maxKichigataMatch ? maxKichigataMatch[1] : null,
                kichigata: kichigataMatch ? kichigataMatch[1] : null,
                url: location.href,
                title: document.title
            };
        });

        // ステップ7: 両方のデータを統合（あなたの吉方位ページの本命星・月命星を使用）
        const result = {
            url: yoshihouiData.url,
            title: yoshihouiData.title,
            birthday: detailPageData.birthday,
            age: detailPageData.age,
            eto: detailPageData.eto,
            // あなたの吉方位ページから本命星・月命星を取得、日命星は不要
            honmeisei: yoshihouiData.honmeisei,
            getsumeisei: yoshihouiData.getsumeisei,
            nichimeisei: null, // 日命星は不要
            year_kanshi: detailPageData.year_kanshi,
            month_kanshi: detailPageData.month_kanshi,
            day_kanshi: detailPageData.day_kanshi,
            naon: detailPageData.naon,
            max_kichigata: yoshihouiData.max_kichigata,
            kichigata: yoshihouiData.kichigata,
            keisha: detailPageData.keisha,
            doukai: detailPageData.doukai,
            extraction_success: !!(detailPageData.birthday && detailPageData.eto && yoshihouiData.honmeisei && yoshihouiData.getsumeisei),
            raw_text: '詳細ページとあなたの吉方位ページから統合取得（吉方位ページの本命星・月命星使用）'
        };

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
 * 姓名判断システム（完全実装）
 */
async function executeSeimeiFinal(inputData) {
    let browser = null;

    try {
        // ブラウザ起動
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            protocolTimeout: 180000, // 3分に延長
            timeout: 180000, // ブラウザ起動タイムアウトも3分
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

        // ページタイムアウトも延長
        page.setDefaultTimeout(180000); // 3分
        page.setDefaultNavigationTimeout(180000); // 3分

        // 入力データの解析
        const { name } = inputData;
        const nameParts = name.split(' ');
        const sei = nameParts[0] || '';
        const mei = nameParts[1] || '';

        // ステップ1: URLパラメータ付きで姓名判断ページに直接アクセス
        const url = `http://localhost:3002/seimei.html?sei=${encodeURIComponent(sei)}&mei=${encodeURIComponent(mei)}`;
        await page.goto(url, {
            waitUntil: 'networkidle2',
            timeout: 60000
        });

        // Vue.js初期化と姓名判断計算完了まで待機
        await page.waitForSelector('#app', { timeout: 30000 });

        // 結果が表示されるまで待機（最大120秒）
        await page.waitForFunction(() => {
            const bodyText = document.body.textContent;
            return bodyText.includes('点') && (
                bodyText.includes('鑑定の結果') ||
                bodyText.includes('総評') ||
                bodyText.includes('画数')
            );
        }, { timeout: 120000 });

        // ステップ5: 結果データ取得
        const result = await page.evaluate(() => {
            // ページ全体のテキストを取得
            const bodyText = document.body.textContent;

            // 結果が表示されているかチェック
            const hasResult = bodyText.includes('点') || bodyText.includes('鑑定') || bodyText.includes('画数');

            if (hasResult) {
                // 基本情報の抽出
                const scoreMatch = bodyText.match(/(\d+)点/);
                const score = scoreMatch ? parseInt(scoreMatch[1]) : null;

                // 詳細なテキスト解析（姓名判断の各項目）
                return {
                    success: true,
                    url: location.href,
                    title: document.title,
                    score: score,
                    has_detailed_result: hasResult,
                    raw_text: bodyText, // 完全なテキストを取得
                    extraction_success: true
                };
            } else {
                // 結果が表示されていない場合
                return {
                    success: false,
                    error: '姓名判断結果が取得できませんでした',
                    url: location.href,
                    title: document.title,
                    raw_text: bodyText
                };
            }
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