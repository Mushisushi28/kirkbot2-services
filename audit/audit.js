/**
 * Speed Audit Framework
 * Comprehensive performance analysis tool
 */

import https from 'https';
import http from 'http';
import { performance } from 'perf_hooks';

export class SpeedAudit {
  constructor(options = {}) {
    this.options = {
      timeout: options.timeout || 30000,
      userAgent: options.userAgent || 'KirkBot2-Audit/1.0',
      enableScreenshots: options.enableScreenshots || false,
      competitors: options.competitors || [],
      ...options
    };
  }

  async analyze(url, options = {}) {
    console.log(`Starting speed audit for: ${url}`);
    
    const results = {
      url,
      timestamp: new Date().toISOString(),
      performance: {},
      resources: {},
      recommendations: [],
      score: 0
    };

    try {
      // Basic connectivity and load time test
      const loadResults = await this.testLoadTime(url);
      results.performance.loadTime = loadResults.loadTime;
      results.performance.ttfb = loadResults.ttfb;
      results.performance.contentSize = loadResults.contentSize;

      // Analyze resources
      const resourceAnalysis = await this.analyzeResources(url);
      results.resources = resourceAnalysis;

      // Generate recommendations
      results.recommendations = this.generateRecommendations(results);

      // Calculate overall score
      results.score = this.calculateScore(results);

      // Competitive analysis if provided
      if (this.options.competitors.length > 0) {
        results.competitive = await this.analyzeCompetitors(url);
      }

      console.log(`Audit completed. Score: ${results.score}/100`);
      return results;

    } catch (error) {
      console.error('Audit failed:', error.message);
      throw error;
    }
  }

  async testLoadTime(url) {
    return new Promise((resolve, reject) => {
      const startTime = performance.now();
      const protocol = url.startsWith('https') ? https : http;
      
      const options = {
        headers: {
          'User-Agent': this.options.userAgent
        },
        timeout: this.options.timeout
      };

      const req = protocol.get(url, options, (res) => {
        let data = '';
        let contentSize = 0;
        const ttfb = performance.now() - startTime;

        res.on('data', (chunk) => {
          data += chunk;
          contentSize += chunk.length;
        });

        res.on('end', () => {
          const loadTime = performance.now() - startTime;
          resolve({
            loadTime: Math.round(loadTime),
            ttfb: Math.round(ttfb),
            contentSize,
            statusCode: res.statusCode,
            headers: res.headers
          });
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      req.end();
    });
  }

  async analyzeResources(url) {
    // Simulate resource analysis - in real implementation, would parse HTML
    // and analyze all linked resources (images, scripts, stylesheets)
    
    return {
      images: {
        count: 0,
        totalSize: 0,
        needsOptimization: false,
        webpCandidates: 0,
        lazyLoadCandidates: 0
      },
      scripts: {
        count: 0,
        totalSize: 0,
        blocking: 0,
        needsMinification: 0
      },
      stylesheets: {
        count: 0,
        totalSize: 0,
        critical: 0,
        unused: 0
      },
      fonts: {
        count: 0,
        totalSize: 0,
        displaySwap: 0
      },
      network: {
        totalRequests: 0,
        totalSize: 0,
        cached: 0,
        compressed: 0
      }
    };
  }

  generateRecommendations(results) {
    const recommendations = [];
    
    // Load time recommendations
    if (results.performance.loadTime > 3000) {
      recommendations.push({
        type: 'critical',
        category: 'load-time',
        title: 'Page Load Time Too Slow',
        description: `Your page takes ${Math.round(results.performance.loadTime / 1000)}s to load. Target should be under 3 seconds.`,
        impact: 'high',
        effort: 'medium',
        savings: `${Math.round(results.performance.loadTime - 3000)}ms faster`
      });
    }

    // TTFB recommendations
    if (results.performance.ttfb > 600) {
      recommendations.push({
        type: 'warning',
        category: 'server',
        title: 'Server Response Time Too High',
        description: `Time to First Byte is ${Math.round(results.performance.ttfb)}ms. Target should be under 600ms.`,
        impact: 'medium',
        effort: 'medium',
        savings: `${Math.round(results.performance.ttfb - 600)}ms faster`
      });
    }

    // Content size recommendations
    if (results.performance.contentSize > 3000000) { // 3MB
      recommendations.push({
        type: 'warning',
        category: 'size',
        title: 'Page Size Too Large',
        description: `Page size is ${Math.round(results.performance.contentSize / 1024 / 1024)}MB. Consider optimizing images and reducing unused code.`,
        impact: 'medium',
        effort: 'low',
        savings: '50% smaller page size'
      });
    }

    // Resource-specific recommendations (would be based on actual analysis)
    recommendations.push(
      {
        type: 'info',
        category: 'images',
        title: 'Optimize Images',
        description: 'Use WebP format, implement lazy loading, and compress images.',
        impact: 'high',
        effort: 'low',
        savings: '30-50% reduction in image size'
      },
      {
        type: 'info',
        category: 'scripts',
        title: 'Minimize JavaScript',
        description: 'Remove unused JavaScript and implement code splitting.',
        impact: 'medium',
        effort: 'medium',
        savings: '20-40% reduction in bundle size'
      },
      {
        type: 'info',
        category: 'caching',
        title: 'Implement Caching',
        description: 'Set appropriate cache headers and use CDN for static assets.',
        impact: 'high',
        effort: 'low',
        savings: '50-80% faster repeat visits'
      }
    );

    return recommendations.sort((a, b) => {
      const priority = { critical: 3, warning: 2, info: 1 };
      return priority[b.type] - priority[a.type];
    });
  }

  calculateScore(results) {
    let score = 100;

    // Deduct points for slow load time
    if (results.performance.loadTime > 3000) {
      score -= Math.min(30, Math.round((results.performance.loadTime - 3000) / 100));
    }

    // Deduct points for high TTFB
    if (results.performance.ttfb > 600) {
      score -= Math.min(20, Math.round((results.performance.ttfb - 600) / 50));
    }

    // Deduct points for large page size
    if (results.performance.contentSize > 3000000) {
      score -= Math.min(15, Math.round((results.performance.contentSize - 3000000) / 100000));
    }

    // Deduct points for critical issues
    const criticalIssues = results.recommendations.filter(r => r.type === 'critical').length;
    score -= criticalIssues * 10;

    return Math.max(0, Math.min(100, score));
  }

  async analyzeCompetitors(url) {
    const competitive = {
      url,
      competitors: [],
      industry: 'Unknown',
      ranking: 0
    };

    for (const competitorUrl of this.options.competitors) {
      try {
        console.log(`Analyzing competitor: ${competitorUrl}`);
        const competitorResults = await this.analyze(competitorUrl, { skipRecommendations: true });
        
        competitive.competitors.push({
          url: competitorUrl,
          score: competitorResults.score,
          loadTime: competitorResults.performance.loadTime,
          ttfb: competitorResults.performance.ttfb
        });
      } catch (error) {
        console.warn(`Failed to analyze competitor ${competitorUrl}:`, error.message);
      }
    }

    // Sort competitors by score
    competitive.competitors.sort((a, b) => b.score - a.score);

    return competitive;
  }

  generateHTMLReport(results) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Performance Audit Report - ${results.url}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .score { font-size: 48px; font-weight: bold; color: ${results.score >= 80 ? 'green' : results.score >= 60 ? 'orange' : 'red'}; }
        .recommendation { margin: 10px 0; padding: 10px; border-left: 4px solid; }
        .critical { border-color: red; background: #ffebee; }
        .warning { border-color: orange; background: #fff3e0; }
        .info { border-color: blue; background: #e3f2fd; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { padding: 15px; background: #f5f5f5; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Performance Audit Report</h1>
    <p><strong>URL:</strong> ${results.url}</p>
    <p><strong>Date:</strong> ${results.timestamp}</p>
    
    <div class="metrics">
        <div class="metric">
            <h3>Performance Score</h3>
            <div class="score">${results.score}/100</div>
        </div>
        <div class="metric">
            <h3>Load Time</h3>
            <p>${Math.round(results.performance.loadTime / 1000)}s</p>
        </div>
        <div class="metric">
            <h3>Time to First Byte</h3>
            <p>${results.performance.ttfb}ms</p>
        </div>
        <div class="metric">
            <h3>Page Size</h3>
            <p>${Math.round(results.performance.contentSize / 1024 / 1024)}MB</p>
        </div>
    </div>

    <h2>Recommendations</h2>
    ${results.recommendations.map(rec => `
        <div class="recommendation ${rec.type}">
            <h4>${rec.title}</h4>
            <p>${rec.description}</p>
            <p><strong>Impact:</strong> ${rec.impact} | <strong>Effort:</strong> ${rec.effort}</p>
            <p><strong>Potential Savings:</strong> ${rec.savings}</p>
        </div>
    `).join('')}
</body>
</html>
    `;
  }
}

export default SpeedAudit;