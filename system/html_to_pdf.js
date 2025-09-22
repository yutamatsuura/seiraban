/**
 * HTML to PDF Converter using Puppeteer
 * HTMLファイルをPDFに変換
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function convertHtmlToPdf(htmlPath, pdfPath) {
    let browser = null;

    try {
        // ブラウザ起動
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-chrome-browser-cloud-management',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        });

        // 新しいページを開く
        const page = await browser.newPage();

        // HTMLファイル読み込み
        const htmlContent = fs.readFileSync(htmlPath, 'utf8');

        // HTMLをページに設定
        await page.setContent(htmlContent, {
            waitUntil: 'networkidle0'
        });

        // PDF生成オプション
        const pdfOptions = {
            format: 'A4',
            printBackground: true,
            displayHeaderFooter: true,
            headerTemplate: '<div></div>',
            footerTemplate: `
                <div style="width: 100%; font-size: 9px; padding: 10px; text-align: center;">
                    <span class="pageNumber"></span> / <span class="totalPages"></span>
                </div>
            `,
            margin: {
                top: '20mm',
                bottom: '20mm',
                left: '15mm',
                right: '15mm'
            }
        };

        // PDFを生成
        await page.pdf({
            path: pdfPath,
            ...pdfOptions
        });

        console.log(`PDF generated successfully: ${pdfPath}`);

        // ファイルサイズを取得
        const stats = fs.statSync(pdfPath);

        return {
            success: true,
            pdf_path: pdfPath,
            file_size: stats.size
        };

    } catch (error) {
        console.error('Error generating PDF:', error);
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

// コマンドライン引数から実行
async function main() {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        console.error('Usage: node html_to_pdf.js <html_path> <pdf_path>');
        process.exit(1);
    }

    const htmlPath = args[0];
    const pdfPath = args[1];

    // ファイル存在確認
    if (!fs.existsSync(htmlPath)) {
        console.error(`HTML file not found: ${htmlPath}`);
        process.exit(1);
    }

    // PDF生成実行
    const result = await convertHtmlToPdf(htmlPath, pdfPath);

    // 結果を標準出力に出力
    console.log(JSON.stringify(result));

    process.exit(result.success ? 0 : 1);
}

// エラーハンドリング
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection:', reason);
    process.exit(1);
});

// 実行
if (require.main === module) {
    main();
}

module.exports = { convertHtmlToPdf };