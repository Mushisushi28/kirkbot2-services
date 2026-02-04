# 🚀 KirkBot2 Tools - Usage Examples

This directory contains practical examples of how to use KirkBot2's performance optimization tools.

## 📋 Quick Start

### 1. Performance Audit Tool
Analyze website performance and get optimization recommendations:

```bash
# Basic audit
node tools/performance-audit.js https://example.com

# Using the CLI alias
kirk-audit https://your-website.com
```

**Example Output:**
```
🚀 Starting performance audit for: https://example.com

📊 Performance Audit Results
================================
📍 URL: https://example.com
📅 Timestamp: 2026-02-04T13:41:23.456Z
⭐ Performance Score: 75/100

📈 Key Metrics:
   Status Code: 200
   Load Time: 3200ms
   Content Size: 1.85MB
   Content Type: text/html; charset=utf-8
   Server: nginx

🎯 Recommendations:
🔴 1. Optimize Page Load Time (speed)
   Current load time: 3200ms. Target: under 2000ms
   Actions:
     • Enable image compression and lazy loading
     • Minify CSS, JavaScript, and HTML
     • Use a CDN for static assets
     • Implement browser caching
```

### 2. Image Optimization Tool
Compress and convert images for better web performance:

```bash
# Optimize all images in a directory
node tools/image-optimizer.js ./images

# With custom settings
node tools/image-optimizer.js ./images --quality=85 --webp=true --output=./optimized

# Using the CLI alias
kirk-optimize ./assets/images --quality=90
```

**Example Output:**
```
🖼️  Starting image optimization for: ./images
📸 Found 15 images to optimize
⚡ Processing: hero-banner.jpg (245.67KB)
   ✅ Optimized: hero-banner.jpg -> Saved 98.27KB (40.0%)
   🌐 Created WebP version: hero-banner.webp

📊 Image Optimization Summary
==============================
📸 Images Processed: 15
📦 Original Size: 3.45MB
⚡ Optimized Size: 2.12MB
💾 Space Saved: 1.33MB
📈 Reduction: 38.6%
📁 Output Directory: optimized
🌐 WebP Versions: Created for supported formats

✅ Optimization completed!
```

### 3. Bundle Analyzer Tool
Analyze JavaScript bundles for optimization opportunities:

```bash
# Analyze a bundle
node tools/bundle-analyzer.js ./dist/main.js

# With custom threshold
node tools/bundle-analyzer.js ./dist/main.js --threshold=300KB

# Using the CLI alias
kirk-analyze ./build/static/js/main.bundle.js --detailed=true
```

**Example Output:**
```
🔍 Analyzing bundle: ./dist/main.js
📦 Bundle size: 485.32KB

📊 Bundle Analysis Results
===========================
📦 Bundle Path: ./dist/main.js
⭐ Bundle Score: 65/100
📏 Total Size: 485.32KB

📦 Module Breakdown:

   FRAMEWORK (3 modules, 164.00KB):
     • react-dom: 120.00KB
     • react: 42.00KB
     • @babel/runtime: 2.00KB

   UTILITY (2 modules, 85.32KB):
     • lodash: 68.00KB
     • utils/helpers: 17.32KB

   CHARTS (1 modules, 150.00KB):
     • chart.js: 150.00KB

🎯 Optimization Recommendations:
🔴 1. Reduce Bundle Size (size)
   Current bundle is 485.32KB. Target: under 250.00KB
   Actions:
     • Implement code splitting
     • Use dynamic imports for rarely used features
     • Enable tree shaking
     • Remove unused dependencies

🟡 2. Optimize Lodash Usage (library)
   Lodash adds 68.00KB. Use tree-shakeable version
   Actions:
     • Import only needed functions: import { debounce } from "lodash-es"
     • Replace with native alternatives where possible
     • Use lodash-webpack-plugin for tree shaking

✅ Analysis completed!
```

## 🔧 Integration Examples

### CI/CD Pipeline Integration
Add performance checks to your build process:

```yaml
# .github/workflows/performance.yml
name: Performance Check
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Run Performance Audit
        run: |
          node tools/performance-audit.js https://your-staging-site.com
      
      - name: Analyze Bundle Size
        run: |
          node tools/bundle-analyzer.js ./dist/main.js --threshold=500KB
```

### npm Scripts Integration
Add to your `package.json`:

```json
{
  "scripts": {
    "perf:audit": "node kirkbot2-services/tools/performance-audit.js https://yoursite.com",
    "perf:optimize": "node kirkbot2-services/tools/image-optimizer.js ./public/images",
    "perf:bundle": "node kirkbot2-services/tools/bundle-analyzer.js ./dist/main.js",
    "perf:all": "npm run perf:audit && npm run perf:optimize && npm run perf:bundle"
  }
}
```

### Webhook Integration
Automated performance monitoring:

```javascript
// performance-monitor.js
const { PerformanceAudit } = require('./tools/performance-audit');

async function checkPerformance(url) {
  const audit = new PerformanceAudit(url);
  const results = await audit.runAudit();
  
  if (results.score < 80) {
    // Send alert to monitoring system
    await sendAlert({
      type: 'performance',
      url: url,
      score: results.score,
      recommendations: results.recommendations
    });
  }
  
  return results;
}

// Run every hour
setInterval(() => {
  checkPerformance('https://your-production-site.com');
}, 3600000);
```

## 📊 Performance Monitoring Dashboard

Create a simple dashboard to track performance over time:

```javascript
// dashboard.js
const fs = require('fs');
const path = require('path');

class PerformanceDashboard {
  constructor() {
    this.dataFile = 'performance-data.json';
    this.loadData();
  }
  
  async recordAudit(url, results) {
    const entry = {
      timestamp: new Date().toISOString(),
      url: url,
      score: results.score,
      loadTime: results.metrics.loadTime,
      size: results.metrics.contentLength,
      recommendations: results.recommendations.length
    };
    
    this.data.push(entry);
    this.saveData();
    this.updateDashboard();
  }
  
  updateDashboard() {
    const latest = this.data.slice(-10); // Last 10 entries
    const avgScore = latest.reduce((sum, entry) => sum + entry.score, 0) / latest.length;
    
    console.log('📊 Performance Dashboard Update');
    console.log(`Average Score (last 10): ${avgScore.toFixed(1)}/100`);
    console.log(`Total Audits: ${this.data.length}`);
    
    // Generate HTML report
    this.generateHTMLReport(latest);
  }
  
  generateHTMLReport(data) {
    const html = `
<!DOCTYPE html>
<html>
<head>
    <title>KirkBot2 Performance Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; }
        .score { font-size: 24px; font-weight: bold; }
        .good { color: #4CAF50; }
        .warning { color: #FF9800; }
        .bad { color: #F44336; }
    </style>
</head>
<body>
    <h1>🚀 KirkBot2 Performance Dashboard</h1>
    <div class="metric">
        <div class="score ${avgScore > 80 ? 'good' : avgScore > 60 ? 'warning' : 'bad'}">
            ${avgScore.toFixed(1)}/100
        </div>
        <div>Average Score</div>
    </div>
    <div class="metric">
        <div class="score">${data.length}</div>
        <div>Recent Audits</div>
    </div>
    <h2>Recent Performance History</h2>
    <table>
        <tr><th>Time</th><th>URL</th><th>Score</th><th>Load Time</th></tr>
        ${data.map(entry => `
            <tr>
                <td>${new Date(entry.timestamp).toLocaleString()}</td>
                <td>${entry.url}</td>
                <td class="${entry.score > 80 ? 'good' : entry.score > 60 ? 'warning' : 'bad'}">
                    ${entry.score}/100
                </td>
                <td>${entry.loadTime}ms</td>
            </tr>
        `).join('')}
    </table>
</body>
</html>`;
    
    fs.writeFileSync('dashboard.html', html);
  }
}
```

## 🎯 Best Practices

### Performance Optimization Workflow
1. **Audit First**: Always start with a performance audit
2. **Optimize Images**: Often the biggest performance win
3. **Analyze Bundles**: Check for oversized JavaScript
4. **Monitor Regularly**: Set up automated checks
5. **Track Progress**: Use the dashboard to see improvements

### Tool Combinations
Combine tools for comprehensive optimization:

```bash
# Complete optimization workflow
npm run perf:audit          # Check current performance
npm run perf:optimize       # Optimize images
npm run perf:bundle         # Analyze bundle size
npm run build               # Rebuild with optimizations
npm run perf:audit          # Verify improvements
```

### Custom Configuration
Create a configuration file for your projects:

```javascript
// kirk.config.js
module.exports = {
  performance: {
    targetScore: 85,
    thresholds: {
      loadTime: 2000,
      bundleSize: 300000,
      imageSize: 500000
    }
  },
  optimization: {
    images: {
      quality: 85,
      webp: true,
      progressive: true
    },
    bundles: {
      analyzeAll: true,
      generateReport: true
    }
  },
  monitoring: {
    enabled: true,
    interval: 3600000, // 1 hour
    webhook: 'https://your-monitoring-service.com/webhook'
  }
};
```

---

## 📞 Need Help?

- **Documentation**: Check the tool-specific README files
- **Examples**: More examples in the `examples/` directory
- **Support**: kirk@kirkbot2.dev
- **Community**: [GitHub Issues](https://github.com/Mushisushi28/kirkbot2-services/issues)

*Happy optimizing! 🚀*