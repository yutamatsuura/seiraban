#!/usr/bin/env node
/**
 * 九星気学システムの手動フロー再現（最も安定したアプローチ）
 */

const puppeteer = require('puppeteer');

async function kyuseiManualFlow(inputData) {
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

        // 入力データの解析
        const { birth_date, gender } = inputData;
        const birthDate = new Date(birth_date);
        const year = String(birthDate.getFullYear());
        const month = String(birthDate.getMonth() + 1);
        const day = String(birthDate.getDate());
        const sex = gender === 'female' ? '女' : '男';

        console.log(`📅 計算対象: ${year}年${month}月${day}日 性別:${sex}`);

        // ステップ1: トップページアクセス
        console.log('🔗 トップページアクセス中...');
        await page.goto('http://localhost:3001/ban_top_full.html', {
            waitUntil: 'networkidle2',
            timeout: 10000
        });

        // Vue.js初期化待機
        await page.waitForSelector('#app', { timeout: 5000 });
        await page.waitForTimeout(1000);

        // ステップ2: データ入力
        console.log('📝 データ入力中...');
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

        // ステップ3: ボタンクリック
        console.log('🖱️ 九星調査ボタンクリック中...');

        // クリックと同時にナビゲーション待機
        const [response] = await Promise.all([
            page.waitForNavigation({
                waitUntil: 'networkidle2',
                timeout: 10000
            }),
            page.click('span.button.beju:first-of-type a')
        ]);

        console.log('✅ ページ遷移完了:', response.url());

        // ステップ4: 結果待機
        console.log('⏳ 結果描画待機中...');
        await page.waitForTimeout(2000);

        // ステップ5: 結果取得
        console.log('📊 結果取得中...');
        const result = await page.evaluate(() => {
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
            const maxKichigataMatch = text.match(/最大吉方\s+([^\s]+)/);
            const kichigataMatch = text.match(/吉方\s+([^\s]+)/);

            return {
                url: location.href,
                title: document.title,
                birthday: birthday,
                age: age,
                eto: eto,
                year_kanshi: yearKanshiMatch ? yearKanshiMatch[1] : null,
                month_kanshi: monthKanshiMatch ? monthKanshiMatch[1] : null,
                day_kanshi: dayKanshiMatch ? dayKanshiMatch[1] : null,
                naon: naonMatch ? naonMatch[1] : null,
                max_kichigata: maxKichigataMatch ? maxKichigataMatch[1] : null,
                kichigata: kichigataMatch ? kichigataMatch[1] : null,
                extraction_success: !!(birthday && eto)
            };
        });

        console.log('🎉 結果取得完了');
        console.log(JSON.stringify({
            success: true,
            type: 'kyusei',
            input: inputData,
            result: result
        }, null, 2));

        return {
            success: true,
            type: 'kyusei',
            input: inputData,
            result: result
        };

    } catch (error) {
        console.error('❌ エラー:', error.message);
        return {
            success: false,
            error: error.message
        };
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// 実行
const inputData = JSON.parse(process.argv[2] || '{"birth_date":"1990-05-15","gender":"male"}');
kyuseiManualFlow(inputData);