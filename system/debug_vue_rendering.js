#!/usr/bin/env node

/**
 * Vue.js Rendering Debug Tool for Nine Star Ki System
 * Diagnoses why Puppeteer bridge is failing to find expected buttons
 */

const puppeteer = require('puppeteer');

async function debugVueRendering() {
    const browser = await puppeteer.launch({
        headless: "new", // Run in headless mode for testing
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

        page.on('pageerror', error => {
            console.error('🚨 PAGE ERROR:', error.message);
        });

        console.log('🔗 Navigating to Nine Star Ki system...');

        // Navigate to the correct URL (port 3006 based on puppeteer_bridge_final.js)
        await page.goto('http://localhost:3006/ban_top_full.html', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });

        console.log('✅ Page loaded successfully');

        // Check if the server is running
        const title = await page.title();
        const url = await page.url();
        console.log(`📄 Title: ${title}`);
        console.log(`🌐 URL: ${url}`);

        // Wait for Vue app to initialize
        console.log('⏳ Waiting for Vue.js app to initialize...');

        try {
            await page.waitForSelector('#app', { timeout: 10000 });
            console.log('✅ #app element found');
        } catch (error) {
            console.error('❌ #app element not found:', error.message);
        }

        // Check for top-component
        try {
            await page.waitForSelector('top-component', { timeout: 5000 });
            console.log('✅ top-component element found');
        } catch (error) {
            console.error('❌ top-component element not found:', error.message);
        }

        // Wait a bit more for Vue to render
        await page.waitForTimeout(3000);

        console.log('🔍 Analyzing current page structure...');

        // Get comprehensive page analysis
        const analysis = await page.evaluate(() => {
            const results = {
                title: document.title,
                url: location.href,
                hasApp: !!document.querySelector('#app'),
                hasTopComponent: !!document.querySelector('top-component'),
                appContent: '',
                vueInstance: null,
                buttonsFound: [],
                allElements: [],
                errors: []
            };

            // Get app content
            const appElement = document.querySelector('#app');
            if (appElement) {
                results.appContent = appElement.innerHTML;
            }

            // Check for Vue instance
            try {
                const vueApp = document.querySelector('#app').__vue__;
                if (vueApp) {
                    results.vueInstance = {
                        exists: true,
                        componentName: vueApp.$options.name || 'Unknown',
                        hasChildren: vueApp.$children && vueApp.$children.length > 0,
                        childrenCount: vueApp.$children ? vueApp.$children.length : 0
                    };

                    // Check for top component data
                    if (vueApp.$children && vueApp.$children.length > 0) {
                        const topComponent = vueApp.$children.find(child =>
                            child.$options.name === 'TopComponent' ||
                            child.selectYear !== undefined
                        );

                        if (topComponent) {
                            results.topComponentData = {
                                exists: true,
                                selectYear: topComponent.selectYear,
                                selectMonth: topComponent.selectMonth,
                                selectDay: topComponent.selectDay,
                                selectSex: topComponent.selectSex
                            };
                        }
                    }
                }
            } catch (error) {
                results.errors.push('Vue instance check failed: ' + error.message);
            }

            // Look for the specific buttons that Puppeteer is trying to find
            const buttonSelectors = [
                'span.button.beju:first-of-type a',
                'span.button.beju:last-of-type a',
                'span.button.beju a',
                '.button a',
                'a'
            ];

            buttonSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    results.buttonsFound.push({
                        selector: selector,
                        count: elements.length,
                        elements: Array.from(elements).map(el => ({
                            tagName: el.tagName,
                            className: el.className,
                            textContent: el.textContent.trim(),
                            href: el.href || 'no href'
                        }))
                    });
                }
            });

            // Get all elements for general analysis
            const allElems = document.querySelectorAll('*');
            results.allElements = Array.from(allElems).map(el => ({
                tagName: el.tagName,
                className: el.className,
                id: el.id,
                textContent: el.textContent ? el.textContent.trim().substring(0, 50) : ''
            }));

            return results;
        });

        console.log('\n📊 ANALYSIS RESULTS:');
        console.log('==================');
        console.log(`Title: ${analysis.title}`);
        console.log(`URL: ${analysis.url}`);
        console.log(`Has #app: ${analysis.hasApp}`);
        console.log(`Has top-component: ${analysis.hasTopComponent}`);

        if (analysis.vueInstance) {
            console.log('\n🎯 Vue Instance:');
            console.log(`  Exists: ${analysis.vueInstance.exists}`);
            console.log(`  Component Name: ${analysis.vueInstance.componentName}`);
            console.log(`  Has Children: ${analysis.vueInstance.hasChildren}`);
            console.log(`  Children Count: ${analysis.vueInstance.childrenCount}`);
        }

        if (analysis.topComponentData) {
            console.log('\n🔧 Top Component Data:');
            console.log(`  Exists: ${analysis.topComponentData.exists}`);
            console.log(`  Select Year: ${analysis.topComponentData.selectYear}`);
            console.log(`  Select Month: ${analysis.topComponentData.selectMonth}`);
            console.log(`  Select Day: ${analysis.topComponentData.selectDay}`);
            console.log(`  Select Sex: ${analysis.topComponentData.selectSex}`);
        }

        console.log('\n🔘 Buttons Found:');
        if (analysis.buttonsFound.length === 0) {
            console.log('  ❌ No buttons found with any of the expected selectors');
        } else {
            analysis.buttonsFound.forEach(buttonGroup => {
                console.log(`  📌 Selector: ${buttonGroup.selector}`);
                console.log(`     Count: ${buttonGroup.count}`);
                buttonGroup.elements.forEach((elem, index) => {
                    console.log(`     [${index}] ${elem.tagName}.${elem.className} - "${elem.textContent}" (${elem.href})`);
                });
            });
        }

        console.log('\n📋 App Content:');
        console.log(analysis.appContent);

        if (analysis.errors.length > 0) {
            console.log('\n🚨 Errors:');
            analysis.errors.forEach(error => console.log(`  - ${error}`));
        }

        // Check if JavaScript files are loading
        console.log('\n📦 Checking JavaScript loading...');
        const jsCheck = await page.evaluate(() => {
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            return scripts.map(script => ({
                src: script.src,
                loaded: script.readyState === 'complete' || !script.readyState
            }));
        });

        console.log('JavaScript files:');
        jsCheck.forEach(js => {
            console.log(`  ${js.loaded ? '✅' : '❌'} ${js.src}`);
        });

        // Check CSS loading
        console.log('\n🎨 Checking CSS loading...');
        const cssCheck = await page.evaluate(() => {
            const links = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
            return links.map(link => ({
                href: link.href,
                loaded: true // CSS doesn't have a reliable way to check if loaded
            }));
        });

        cssCheck.forEach(css => {
            console.log(`  ✅ ${css.href}`);
        });

        // Take a screenshot for visual inspection
        await page.screenshot({
            path: '/tmp/vue_debug_screenshot.png',
            fullPage: true
        });
        console.log('\n📸 Screenshot saved to: /tmp/vue_debug_screenshot.png');

        // Wait briefly for final checks
        console.log('\n⏸️  Final wait...');
        await page.waitForTimeout(2000);

    } catch (error) {
        console.error('💥 Debug script failed:', error);
    } finally {
        await browser.close();
        console.log('🔚 Browser closed');
    }
}

// Run the debug script
debugVueRendering().catch(console.error);