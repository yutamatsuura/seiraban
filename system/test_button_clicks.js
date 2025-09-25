#!/usr/bin/env node

/**
 * Test button clicks functionality for Nine Star Ki system
 * This script tests the exact flow that puppeteer_bridge_final.js should be using
 */

const puppeteer = require('puppeteer');

async function testButtonClicks() {
    const browser = await puppeteer.launch({
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

    try {
        const page = await browser.newPage();

        // Enable console logging from the page
        page.on('console', msg => {
            console.log(`🖥️  BROWSER CONSOLE [${msg.type()}]:`, msg.text());
        });

        console.log('🔗 Navigating to Nine Star Ki system...');

        await page.goto('http://localhost:3006/ban_top_full.html', {
            waitUntil: 'networkidle2',
            timeout: 10000
        });

        console.log('✅ Page loaded successfully');

        // Wait for Vue app to initialize
        await page.waitForSelector('#app', { timeout: 5000 });
        await page.waitForTimeout(1000);

        // Set test data
        console.log('📝 Setting test data...');
        const testData = {
            year: '1990',
            month: '5',
            day: '15',
            sex: '男'
        };

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
                console.log('Error setting data:', error.message);
                return false;
            }
        }, testData.year, testData.month, testData.day, testData.sex);

        console.log(`📊 Data input success: ${inputSuccess}`);

        // Test clicking the first button (九星を調べる)
        console.log('🔘 Testing first button click (九星を調べる)...');

        try {
            // Wait for navigation after button click
            const [response1] = await Promise.all([
                page.waitForNavigation({
                    waitUntil: 'networkidle2',
                    timeout: 10000
                }),
                page.click('span.button.beju:first-of-type a')
            ]);

            console.log('✅ First button click successful');
            console.log(`📄 New page title: ${await page.title()}`);
            console.log(`🌐 New URL: ${await page.url()}`);

            // Extract some data from the result page
            const pageData = await page.evaluate(() => {
                return {
                    title: document.title,
                    url: location.href,
                    bodyText: document.body && document.body.textContent ?
                        document.body.textContent.substring(0, 500) + '...' : 'No body content'
                };
            });

            console.log('📋 Page data:', JSON.stringify(pageData, null, 2));

            // Go back to test the second button
            console.log('⬅️ Going back to main page...');
            await page.goBack();
            await page.waitForTimeout(1000);

            // Test clicking the second button (吉方位を調べる)
            console.log('🔘 Testing second button click (吉方位を調べる)...');

            const [response2] = await Promise.all([
                page.waitForNavigation({
                    waitUntil: 'networkidle2',
                    timeout: 10000
                }),
                page.click('span.button.beju:last-of-type a')
            ]);

            console.log('✅ Second button click successful');
            console.log(`📄 New page title: ${await page.title()}`);
            console.log(`🌐 New URL: ${await page.url()}`);

            const pageData2 = await page.evaluate(() => {
                return {
                    title: document.title,
                    url: location.href,
                    bodyText: document.body && document.body.textContent ?
                        document.body.textContent.substring(0, 500) + '...' : 'No body content'
                };
            });

            console.log('📋 Second page data:', JSON.stringify(pageData2, null, 2));

        } catch (error) {
            console.error('❌ Button click test failed:', error.message);
        }

        // Take final screenshot
        await page.screenshot({
            path: '/tmp/button_test_screenshot.png',
            fullPage: true
        });
        console.log('📸 Screenshot saved to: /tmp/button_test_screenshot.png');

    } catch (error) {
        console.error('💥 Test failed:', error);
    } finally {
        await browser.close();
        console.log('🔚 Browser closed');
    }
}

// Run the test
testButtonClicks().catch(console.error);