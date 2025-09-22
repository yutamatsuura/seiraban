/**
 * iframe結果をPDF化するためのブリッジ
 * 既存システムの結果をキャプチャしてPDF生成用データに変換
 */

const puppeteer = require('puppeteer');

class IframeToPDFBridge {
    constructor() {
        this.browser = null;
    }

    async init() {
        this.browser = await puppeteer.launch({
            headless: "new",
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        });
    }

    /**
     * iframe内の九星気学結果をデータ化
     */
    async captureKyuseiKigakuResult(year, month, day, sex) {
        const page = await this.browser.newPage();

        try {
            // 九星気学システムにアクセス
            await page.goto('http://localhost:3001/ban_top_full.html');
            await page.waitForSelector('.js-input-form', { timeout: 10000 });

            // 入力データ設定
            await page.evaluate((year, month, day, sex) => {
                const topComponent = app.$children.find(child =>
                    child.selectYear !== undefined);
                topComponent.selectYear = year;
                topComponent.selectMonth = month;
                topComponent.selectDay = day;
                topComponent.selectSex = sex;
            }, year, month, day, sex);

            // 計算実行
            await page.click('.js-submit-button');
            await page.waitForSelector('.result-display', { timeout: 15000 });

            // 結果データ抽出
            const resultData = await page.evaluate(() => {
                const resultComponent = app.$children.find(child =>
                    child.resultData !== undefined);

                if (!resultComponent || !resultComponent.resultData) {
                    return null;
                }

                return {
                    honmei_star: resultComponent.resultData.honmei || '',
                    gekkei_star: resultComponent.resultData.gekkei || '',
                    nichimei_star: resultComponent.resultData.nichimei || '',
                    fortune_summary: resultComponent.resultData.summary || '',
                    detailed_analysis: resultComponent.resultData.analysis || '',
                    lucky_directions: resultComponent.resultData.directions || [],
                    elemental_analysis: resultComponent.resultData.elements || {}
                };
            });

            // HTMLもキャプチャ（デバッグ・詳細表示用）
            const htmlContent = await page.content();

            return {
                data: resultData,
                html_snapshot: htmlContent,
                timestamp: new Date().toISOString()
            };

        } finally {
            await page.close();
        }
    }

    /**
     * iframe内の姓名判断結果をデータ化
     */
    async captureSeimeiHandanResult(sei, mei) {
        const page = await this.browser.newPage();

        try {
            // 姓名判断システムにアクセス
            await page.goto('http://localhost:3002/seimei_top.html');
            await page.waitForSelector('.name-input-form', { timeout: 10000 });

            // 姓名入力
            await page.type('#sei-input', sei);
            await page.type('#mei-input', mei);

            // 分析実行
            await page.click('.analyze-button');
            await page.waitForSelector('.analysis-result', { timeout: 15000 });

            // 結果データ抽出
            const resultData = await page.evaluate(() => {
                const searchComponent = app.$children.find(child =>
                    child.analysisResult !== undefined);

                if (!searchComponent || !searchComponent.analysisResult) {
                    return null;
                }

                return {
                    tenkaku: searchComponent.analysisResult.tenkaku || 0,
                    jinkaku: searchComponent.analysisResult.jinkaku || 0,
                    chikaku: searchComponent.analysisResult.chikaku || 0,
                    soukaku: searchComponent.analysisResult.soukaku || 0,
                    gaikaku: searchComponent.analysisResult.gaikaku || 0,
                    overall_rating: searchComponent.analysisResult.rating || '',
                    detailed_meaning: searchComponent.analysisResult.meaning || '',
                    kanji_analysis: searchComponent.analysisResult.kanjiDetails || [],
                    stroke_breakdown: searchComponent.analysisResult.strokes || {}
                };
            });

            const htmlContent = await page.content();

            return {
                data: resultData,
                html_snapshot: htmlContent,
                timestamp: new Date().toISOString()
            };

        } finally {
            await page.close();
        }
    }

    /**
     * 統合鑑定データをPDF生成用フォーマットに変換
     */
    formatForPDFGeneration(kyuseiResult, seimeiResult, clientInfo, customMessage = '') {
        return {
            client_info: {
                name: `${clientInfo.sei} ${clientInfo.mei}`,
                birth_date: `${clientInfo.year}年${clientInfo.month}月${clientInfo.day}日`,
                gender: clientInfo.sex === 1 ? '男性' : '女性',
                birth_time: clientInfo.birthTime || null,
                birth_place: clientInfo.birthPlace || null
            },
            calculation_result: {
                kyusei_kigaku: kyuseiResult.data,
                seimei_handan: seimeiResult.data,
                kichihoui: {
                    // 九星気学から吉方位を抽出
                    this_month: kyuseiResult.data?.lucky_directions?.[0] || '',
                    this_year: kyuseiResult.data?.lucky_directions?.[1] || '',
                    recommendations: kyuseiResult.data?.fortune_summary || ''
                },
                template_ids: [], // 使用したテンプレート
                raw_html_snapshots: {
                    kyusei_html: kyuseiResult.html_snapshot,
                    seimei_html: seimeiResult.html_snapshot
                }
            },
            custom_message: customMessage,
            generated_at: new Date().toISOString()
        };
    }

    /**
     * iframe結果を直接PDF化（代替方法）
     */
    async generatePDFFromIframe(url, outputPath, options = {}) {
        const page = await this.browser.newPage();

        try {
            await page.goto(url, { waitUntil: 'networkidle0' });

            // PDF生成
            await page.pdf({
                path: outputPath,
                format: 'A4',
                printBackground: true,
                margin: {
                    top: '20mm',
                    bottom: '20mm',
                    left: '15mm',
                    right: '15mm'
                },
                ...options
            });

            return outputPath;

        } finally {
            await page.close();
        }
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

module.exports = IframeToPDFBridge;

// 使用例
async function demonstrateUsage() {
    const bridge = new IframeToPDFBridge();
    await bridge.init();

    try {
        // 1. iframe結果をデータ化してReportLabでPDF生成
        const kyuseiResult = await bridge.captureKyuseiKigakuResult(1990, 5, 15, 1);
        const seimeiResult = await bridge.captureSeimeiHandanResult('田中', '太郎');

        const pdfData = bridge.formatForPDFGeneration(
            kyuseiResult,
            seimeiResult,
            { sei: '田中', mei: '太郎', year: 1990, month: 5, day: 15, sex: 1 },
            '鑑定士からの特別メッセージです'
        );

        console.log('PDF生成用データ:', JSON.stringify(pdfData, null, 2));

        // 2. 直接PDF化（代替方法）
        await bridge.generatePDFFromIframe(
            'http://localhost:3001/ban_result.html',
            '/tmp/kyusei_direct.pdf'
        );

    } finally {
        await bridge.close();
    }
}

if (require.main === module) {
    demonstrateUsage().catch(console.error);
}