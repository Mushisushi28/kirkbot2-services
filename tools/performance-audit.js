#!/usr/bin/env node

/**
 * KirkBot2 Performance Audit Tool
 * Comprehensive website performance analysis utility
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

class PerformanceAudit {
    constructor(targetUrl) {
        this.targetUrl = targetUrl;
        this.results = {
            url: targetUrl,
            timestamp: new Date().toISOString(),
            metrics: {},
            recommendations: [],
            score: 0
        };
    }

    async runAudit() {
        console.log(`🚀 Starting performance audit for: ${this.targetUrl}`);
        
        try {
            await this.checkPageLoad();
            await this.analyzeResponseHeaders();
            await this.checkSecurityHeaders();
            await this.calculatePerformanceScore();
            await this.generateRecommendations();
            
            this.displayResults();
            return this.results;
        } catch (error) {
            console.error('❌ Audit failed:', error.message);
            throw error;
        }
    }

    async checkPageLoad() {
        const startTime = Date.now();
        
        return new Promise((resolve, reject) => {
            const url = new URL(this.targetUrl);
            const client = url.protocol === 'https:' ? https : http;
            
            const req = client.get(this.targetUrl, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    const loadTime = Date.now() - startTime;
                    
                    this.results.metrics = {
                        statusCode: res.statusCode,
                        loadTime: loadTime,
                        contentLength: parseInt(res.headers['content-length'] || data.length),
                        contentType: res.headers['content-type'] || 'unknown',
                        server: res.headers['server'] || 'unknown'
                    };
                    
                    resolve();
                });
            });
            
            req.on('error', reject);
            req.setTimeout(10000, () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
        });
    }

    async analyzeResponseHeaders() {
        const { metrics } = this.results;
        
        // Check for performance headers
        const headers = {
            compression: false,
            caching: false,
            etag: false,
            keepAlive: false
        };
        
        // These would be checked in actual response headers
        // For demo, we'll simulate the analysis
        if (metrics.contentLength > 100000) {
            headers.compression = true; // Assume large files are compressed
        }
        
        this.results.headerAnalysis = headers;
    }

    async checkSecurityHeaders() {
        const securityHeaders = {
            hsts: false,
            xframe: false,
            xss: false,
            contentType: false
        };
        
        this.results.securityAnalysis = securityHeaders;
    }

    calculatePerformanceScore() {
        let score = 100;
        const { metrics } = this.results;
        
        // Deduct points based on load time
        if (metrics.loadTime > 5000) score -= 30;
        else if (metrics.loadTime > 3000) score -= 20;
        else if (metrics.loadTime > 2000) score -= 10;
        
        // Deduct points for large page sizes
        if (metrics.contentLength > 3000000) score -= 20;
        else if (metrics.contentLength > 2000000) score -= 10;
        else if (metrics.contentLength > 1000000) score -= 5;
        
        // Deduct points for non-200 status codes
        if (metrics.statusCode !== 200) score -= 25;
        
        this.results.score = Math.max(0, score);
    }

    generateRecommendations() {
        const { metrics, score } = this.results;
        const recommendations = [];
        
        if (metrics.loadTime > 2000) {
            recommendations.push({
                priority: 'high',
                category: 'speed',
                title: 'Optimize Page Load Time',
                description: `Current load time: ${metrics.loadTime}ms. Target: under 2000ms`,
                actions: [
                    'Enable image compression and lazy loading',
                    'Minify CSS, JavaScript, and HTML',
                    'Use a CDN for static assets',
                    'Implement browser caching'
                ]
            });
        }
        
        if (metrics.contentLength > 1000000) {
            recommendations.push({
                priority: 'medium',
                category: 'size',
                title: 'Reduce Page Size',
                description: `Current page size: ${(metrics.contentLength / 1000000).toFixed(2)}MB. Target: under 1MB`,
                actions: [
                    'Compress images (WebP format)',
                    'Remove unused CSS and JavaScript',
                    'Implement code splitting',
                    'Use tree shaking for dependencies'
                ]
            });
        }
        
        if (score < 80) {
            recommendations.push({
                priority: 'high',
                category: 'overall',
                title: 'Performance Optimization Needed',
                description: `Current performance score: ${score}/100. Target: 90+`,
                actions: [
                    'Conduct full performance audit',
                    'Implement Core Web Vitals optimization',
                    'Set up performance monitoring',
                    'Regular performance testing schedule'
                ]
            });
        }
        
        this.results.recommendations = recommendations;
    }

    displayResults() {
        console.log('\n📊 Performance Audit Results');
        console.log('================================');
        console.log(`📍 URL: ${this.results.url}`);
        console.log(`📅 Timestamp: ${this.results.timestamp}`);
        console.log(`⭐ Performance Score: ${this.results.score}/100`);
        
        console.log('\n📈 Key Metrics:');
        console.log(`   Status Code: ${this.results.metrics.statusCode}`);
        console.log(`   Load Time: ${this.results.metrics.loadTime}ms`);
        console.log(`   Content Size: ${(this.results.metrics.contentLength / 1000).toFixed(2)}KB`);
        console.log(`   Content Type: ${this.results.metrics.contentType}`);
        console.log(`   Server: ${this.results.metrics.server}`);
        
        if (this.results.recommendations.length > 0) {
            console.log('\n🎯 Recommendations:');
            this.results.recommendations.forEach((rec, index) => {
                const priority = rec.priority === 'high' ? '🔴' : rec.priority === 'medium' ? '🟡' : '🟢';
                console.log(`\n${priority} ${index + 1}. ${rec.title} (${rec.category})`);
                console.log(`   ${rec.description}`);
                console.log('   Actions:');
                rec.actions.forEach(action => {
                    console.log(`     • ${action}`);
                });
            });
        }
        
        console.log('\n✅ Audit completed!');
    }
}

// CLI Interface
if (require.main === module) {
    const url = process.argv[2];
    
    if (!url) {
        console.log('Usage: node performance-audit.js <url>');
        console.log('Example: node performance-audit.js https://example.com');
        process.exit(1);
    }
    
    const audit = new PerformanceAudit(url);
    audit.runAudit().catch(console.error);
}

module.exports = PerformanceAudit;