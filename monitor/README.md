# Real-time Performance Monitor

A lightweight, browser-based performance monitoring tool for web applications.

## Features
- Real-time performance metrics
- Core Web Vitals tracking
- Network request analysis
- Memory usage monitoring
- Error tracking and reporting

## Usage
```javascript
import PerformanceMonitor from './monitor.js';

const monitor = new PerformanceMonitor({
  apiKey: 'your-api-key',
  endpoint: 'https://your-endpoint.com/metrics',
  sampleRate: 0.1 // 10% sampling
});

monitor.start();
```

## Metrics Collected
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)
- Time to Interactive (TTI)
- Memory usage
- Network performance

## Configuration Options
- `apiKey`: Authentication key for endpoint
- `endpoint`: Where to send metrics data
- `sampleRate`: Percentage of users to track (0-1)
- `debug`: Enable debug logging
- `trackErrors`: Monitor JavaScript errors
- `trackNetwork`: Monitor network requests