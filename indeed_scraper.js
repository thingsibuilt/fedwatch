/**
 * FedWatch - Indeed Job Trends Scraper (Node.js)
 * Real-time employment indicator using Puppeteer
 */

const puppeteer = require('puppeteer');

const JOB_CATEGORIES = {
    tech: ['software engineer', 'data scientist', 'developer'],
    retail: ['retail', 'store associate', 'cashier'],
    manufacturing: ['manufacturing', 'factory', 'warehouse'],
    healthcare: ['nurse', 'medical', 'healthcare'],
    finance: ['finance', 'accountant', 'analyst'],
};

async function getJobCount(browser, keywords, location = 'United States') {
    const searchUrl = `https://www.indeed.com/jobs?q=${encodeURIComponent(keywords)}&l=${encodeURIComponent(location)}`;
    
    const page = await browser.newPage();
    
    try {
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
        
        // Wait for search results
        await page.waitForSelector('#searchCount, .jobsearch-ResultsResultsContainer', { timeout: 10000 });
        
        // Get job count from search results
        const count = await page.evaluate(() => {
            // Try different selectors Indeed uses
            const selectors = [
                '#searchCount',
                '.jobsearch-ResultsResultsContainer h1',
                '.resultsCount',
                '[data-testid="searchCount"]'
            ];
            
            for (const sel of selectors) {
                const elem = document.querySelector(sel);
                if (elem) {
                    const text = elem.textContent;
                    // Extract number from "Page 1 of 1,234 jobs" or "1,234 jobs"
                    const match = text.match(/of\s+([\d,]+)\s+jobs?|([\d,]+)\s+jobs?/i);
                    if (match) {
                        return parseInt(match[1] || match[2], 10);
                    }
                }
            }
            return null;
        });
        
        return count;
    } catch (e) {
        console.error(`Error fetching ${keywords}:`, e.message);
        return null;
    } finally {
        await page.close();
    }
}

async function scrapeIndeed() {
    console.log('🚀 Starting FedWatch Indeed Scraper...\n');
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    const results = {};
    
    try {
        for (const [category, keywords] of Object.entries(JOB_CATEGORIES)) {
            console.log(`📊 Fetching ${category} jobs...`);
            const keywordStr = keywords.join(' OR ');
            const count = await getJobCount(browser, keywordStr);
            
            results[category] = {
                keywords: keywordStr,
                count: count || 0,
                timestamp: new Date().toISOString()
            };
            
            console.log(`   → ${count || 'N/A'} jobs found`);
            
            // Rate limit
            await new Promise(r => setTimeout(r, 2000));
        }
        
        // Calculate health score
        const totalJobs = Object.values(results).reduce((sum, r) => sum + r.count, 0);
        const healthScore = totalJobs > 0 ? Math.min(100, Math.round((totalJobs / 1000000) * 100)) : 50;
        
        console.log('\n' + '='.repeat(50));
        console.log(`💼 Total Job Postings: ${totalJobs.toLocaleString()}`);
        console.log(`💚 Market Health Score: ${healthScore}/100`);
        
        // Save results
        const fs = require('fs');
        const output = {
            timestamp: new Date().toISOString(),
            totalJobs,
            healthScore,
            categories: results
        };
        
        fs.writeFileSync('/root/.openclaw/workspace/fedwatch/indeed_results.json', JSON.stringify(output, null, 2));
        console.log('\n✅ Results saved to indeed_results.json');
        
    } finally {
        await browser.close();
    }
}

scrapeIndeed().catch(console.error);
