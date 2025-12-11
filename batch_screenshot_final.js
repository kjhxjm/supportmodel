/**
 * 优化的批量截图脚本 - 通过模拟点击缩放按钮控制缩放
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 从Python文件导入场景数据
const TEST_SCENARIOS = require('./test_scenarios_data.json');

const BASE_URL = 'http://127.0.0.1:5000';
const SCREENSHOT_DIR = 'test_screenshots_final';
const BROWSER_WIDTH = 2400;  // 更大的宽度以确保完整显示
const BROWSER_HEIGHT = 1400;
const ZOOM_OUT_CLICKS = 3;  // 点击缩小按钮的次数

function sanitizeFilename(text) {
    return text.replace(/[\/\\:*?"<>|.]/g, '-').replace(/\s+/g, '_');
}

async function captureScreenshot(page, scenario, index) {
    const encodedInput = encodeURIComponent(scenario.input);
    const url = `${BASE_URL}/?input=${encodedInput}`;
    
    console.log(`\n[${index}/${TEST_SCENARIOS.length}] ${scenario.test_name}`);
    console.log(`  输入: ${scenario.input.substring(0, 50)}...`);
    
    try {
        // 导航到页面
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        
        // 等待加载动画消失
        try {
            await page.waitForSelector('.loading-mask', { state: 'hidden', timeout: 20000 });
            console.log('  ✓ 加载动画已消失');
        } catch (e) {
            console.log('  ⚠ 等待加载动画超时，继续...');
        }
        
        // 等待行为树容器和canvas渲染
        try {
            await page.waitForSelector('#behaviorTree', { state: 'visible', timeout: 10000 });
            await page.waitForSelector('#behaviorTree canvas', { timeout: 10000 });
            console.log('  ✓ 行为树已渲染');
        } catch (e) {
            console.log('  ⚠ 行为树渲染超时');
        }
        
        // 额外等待确保完全渲染
        await page.waitForTimeout(3000);
        
        // 获取初始缩放比例
        const initialZoom = await page.evaluate(() => {
            if (window.graphObj) {
                return window.graphObj.getZoom();
            }
            return null;
        });
        
        if (initialZoom) {
            console.log(`  ✓ 初始缩放比例: ${initialZoom.toFixed(2)}`);
            
            // 查找缩小按钮
            const zoomOutButton = await page.$('#treeZoomOut');
            
            if (zoomOutButton) {
                // 点击缩小按钮3次
                for (let i = 0; i < ZOOM_OUT_CLICKS; i++) {
                    await zoomOutButton.click();
                    await page.waitForTimeout(300); // 每次点击后等待300ms
                }
                
                // 获取调整后的缩放比例
                const finalZoom = await page.evaluate(() => {
                    if (window.graphObj) {
                        return window.graphObj.getZoom();
                    }
                    return null;
                });
                
                if (finalZoom) {
                    const zoomPercent = Math.round(finalZoom * 100);
                    console.log(`  ✓ 点击${ZOOM_OUT_CLICKS}次缩小按钮后: ${finalZoom.toFixed(2)} (${zoomPercent}%)`);
                }
                
                // 等待缩放动画完成
                await page.waitForTimeout(1000);
            } else {
                console.log('  ⚠ 未找到缩小按钮，使用默认缩放');
            }
        } else {
            console.log('  ⚠ 无法获取缩放信息（graphObj未找到）');
        }
        
        // 截图
        const categorySafe = sanitizeFilename(scenario.category);
        const filename = `${String(index).padStart(2, '0')}_${scenario.id}.png`;
        const filepath = path.join(SCREENSHOT_DIR, categorySafe, filename);
        
        // 确保目录存在
        const dir = path.dirname(filepath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
        
        // 截取整个视口
        await page.screenshot({ path: filepath, fullPage: false });
        
        console.log(`  ✅ 截图已保存: ${filepath}`);
        
        return { success: true, filepath };
    } catch (error) {
        console.error(`  ❌ 错误: ${error.message}`);
        return { success: false, error: error.message };
    }
}

async function main() {
    console.log('='.repeat(80));
    console.log('优化的批量截图脚本 - 模拟点击缩放按钮');
    console.log('='.repeat(80));
    console.log(`\n总场景数: ${TEST_SCENARIOS.length}`);
    console.log(`浏览器尺寸: ${BROWSER_WIDTH}x${BROWSER_HEIGHT}`);
    console.log(`缩放策略: 点击缩小按钮${ZOOM_OUT_CLICKS}次（约70%）`);
    console.log(`输出目录: ${SCREENSHOT_DIR}`);
    
    // 启动浏览器
    const browser = await chromium.launch({
        headless: true,
        args: [
            `--window-size=${BROWSER_WIDTH},${BROWSER_HEIGHT}`,
            '--force-device-scale-factor=1'
        ]
    });
    
    const context = await browser.newContext({
        viewport: { width: BROWSER_WIDTH, height: BROWSER_HEIGHT },
        deviceScaleFactor: 1
    });
    
    const page = await context.newPage();
    
    // 统计
    const results = [];
    let successCount = 0;
    let failCount = 0;
    
    // 逐个处理场景
    for (let i = 0; i < TEST_SCENARIOS.length; i++) {
        const result = await captureScreenshot(page, TEST_SCENARIOS[i], i + 1);
        results.push({
            scenario: TEST_SCENARIOS[i],
            ...result
        });
        
        if (result.success) {
            successCount++;
        } else {
            failCount++;
        }
        
        // 短暂延迟避免过载
        if (i < TEST_SCENARIOS.length - 1) {
            await page.waitForTimeout(500);
        }
    }
    
    await browser.close();
    
    // 打印摘要
    console.log('\n' + '='.repeat(80));
    console.log('截图任务完成');
    console.log('='.repeat(80));
    console.log(`成功: ${successCount}`);
    console.log(`失败: ${failCount}`);
    console.log(`总计: ${TEST_SCENARIOS.length}`);
    console.log(`成功率: ${(successCount / TEST_SCENARIOS.length * 100).toFixed(1)}%`);
    
    // 保存结果报告
    const reportPath = path.join(SCREENSHOT_DIR, 'screenshot_report.json');
    fs.writeFileSync(reportPath, JSON.stringify({
        timestamp: new Date().toISOString(),
        browser_size: `${BROWSER_WIDTH}x${BROWSER_HEIGHT}`,
        zoom_strategy: `Click zoom-out button ${ZOOM_OUT_CLICKS} times`,
        total: TEST_SCENARIOS.length,
        success: successCount,
        failed: failCount,
        results
    }, null, 2));
    
    console.log(`\n报告已保存: ${reportPath}`);
    
    // 生成Markdown报告
    const mdPath = path.join(SCREENSHOT_DIR, 'SCREENSHOT_REPORT.md');
    generateMarkdownReport(mdPath, results);
    console.log(`Markdown报告已保存: ${mdPath}`);
}

function generateMarkdownReport(filepath, results) {
    let md = '# 批量截图报告\n\n';
    md += `**生成时间**: ${new Date().toLocaleString('zh-CN')}\n\n`;
    md += `**浏览器尺寸**: ${BROWSER_WIDTH}x${BROWSER_HEIGHT}\n\n`;
    md += `**缩放策略**: 点击缩小按钮${ZOOM_OUT_CLICKS}次（约70%）\n\n`;
    md += `**成功数量**: ${results.filter(r => r.success).length}/${results.length}\n\n`;
    md += '---\n\n';
    
    let currentCategory = null;
    results.forEach((result, index) => {
        if (result.scenario.category !== currentCategory) {
            currentCategory = result.scenario.category;
            md += `\n## ${currentCategory}\n\n`;
        }
        
        const status = result.success ? '✅' : '❌';
        md += `### ${status} ${index + 1}. ${result.scenario.test_name}\n\n`;
        md += `**输入**: ${result.scenario.input}\n\n`;
        
        if (result.success) {
            const relativePath = result.filepath.replace(SCREENSHOT_DIR + '/', '');
            md += `**截图**: [查看](${relativePath})\n\n`;
            md += `![${result.scenario.test_name}](${relativePath})\n\n`;
        } else {
            md += `**错误**: ${result.error}\n\n`;
        }
        
        md += '---\n\n';
    });
    
    fs.writeFileSync(filepath, md, 'utf8');
}

main().catch(console.error);

