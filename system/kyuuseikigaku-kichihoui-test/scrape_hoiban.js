const puppeteer = require('puppeteer');

(async () => {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: "new",
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();

        // エラーハンドリング追加
        page.on('error', err => {
            console.log('Page error:', err);
        });

        page.on('pageerror', err => {
            console.log('Page script error:', err);
        });

        // 吉方位ページにアクセス
        console.log('Accessing localhost:3001/ban_kipou.html...');
        await page.goto('http://localhost:3001/ban_kipou.html', {
            waitUntil: 'networkidle2',
            timeout: 10000
        });

        // 生年月日設定（1982年10月12日男性）
        // 年の設定
        await page.evaluate(() => {
            const yearInput = document.querySelector('input[type="number"]') || document.querySelector('input');
            if (yearInput) yearInput.value = '1982';
        });

        // 月の設定
        await page.evaluate(() => {
            const monthSelect = document.querySelector('select') || document.querySelectorAll('select')[0];
            if (monthSelect) monthSelect.value = '10';
        });

        // 日の設定
        await page.evaluate(() => {
            const dayInput = document.querySelectorAll('input[type="number"]')[1] || document.querySelectorAll('input')[1];
            if (dayInput) dayInput.value = '12';
        });

        // 男性選択
        await page.evaluate(() => {
            const maleRadio = document.querySelector('input[type="radio"][value="male"]') || document.querySelector('input[type="radio"]');
            if (maleRadio) maleRadio.click();
        });

        // 少し待機してから方位盤データを取得
        await page.waitForTimeout(2000);

        // 方位盤のテキストデータを取得
        const hoibanData = await page.evaluate(() => {
            const result = {
                yearBan: {},
                monthBan: {},
                dayBan: {},
                colors: {}
            };

            // SVGテキスト要素から九星配置を読み取り
            const svgTexts = document.querySelectorAll('svg text.ban');
            svgTexts.forEach((text, index) => {
                const content = text.textContent;
                const rect = text.getBoundingClientRect();
                result[`text_${index}`] = {
                    content: content,
                    x: rect.x,
                    y: rect.y
                };
            });

            // パスの色情報を取得
            const paths = document.querySelectorAll('svg path');
            paths.forEach((path, index) => {
                const className = path.getAttribute('class');
                if (className && className.includes('kipou') || className.includes('kyou')) {
                    result.colors[`path_${index}`] = className;
                }
            });

            return result;
        });

        console.log('=== 方位盤データ取得結果 ===');
        console.log(JSON.stringify(hoibanData, null, 2));

    } catch (error) {
        console.error('Error:', error);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
})().catch(console.error);