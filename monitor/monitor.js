/**
 * Real-time Performance Monitor
 * Tracks and reports web application performance metrics
 */

class PerformanceMonitor {
  constructor(options = {}) {
    this.options = {
      apiKey: options.apiKey || null,
      endpoint: options.endpoint || null,
      sampleRate: options.sampleRate || 0.1,
      debug: options.debug || false,
      trackErrors: options.trackErrors || true,
      trackNetwork: options.trackNetwork || true,
      ...options
    };

    this.metrics = {};
    this.startTime = performance.now();
    this.observers = new Map();
    
    // Check if this user should be sampled
    this.shouldSample = Math.random() < this.options.sampleRate;
    
    if (!this.shouldSample) {
      this.log('User not sampled - performance monitoring disabled');
      return;
    }

    this.init();
  }

  init() {
    this.log('Initializing performance monitor');
    
    // Start timing immediately
    this.startTime = performance.now();
    
    // Set up various observers
    this.observeNavigation();
    this.observePaint();
    this.observeLCP();
    this.observeCLS();
    this.observeFID();
    
    if (this.options.trackErrors) {
      this.observeErrors();
    }
    
    if (this.options.trackNetwork) {
      this.observeNetwork();
    }
    
    // Send metrics on page unload
    window.addEventListener('beforeunload', () => this.sendMetrics());
  }

  observeNavigation() {
    if ('PerformanceNavigationTiming' in window) {
      const navEntry = performance.getEntriesByType('navigation')[0];
      if (navEntry) {
        this.metrics.navigation = {
          dns: navEntry.domainLookupEnd - navEntry.domainLookupStart,
          tcp: navEntry.connectEnd - navEntry.connectStart,
          ssl: navEntry.secureConnectionStart > 0 ? navEntry.connectEnd - navEntry.secureConnectionStart : 0,
          ttfb: navEntry.responseStart - navEntry.requestStart,
          download: navEntry.responseEnd - navEntry.responseStart,
          domParse: navEntry.domContentLoadedEventStart - navEntry.responseEnd,
          domReady: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
          load: navEntry.loadEventEnd - navEntry.loadEventStart
        };
      }
    }
  }

  observePaint() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.metrics.paint = this.metrics.paint || {};
          this.metrics.paint[entry.name] = entry.startTime;
        });
      });
      
      observer.observe({ entryTypes: ['paint'] });
      this.observers.set('paint', observer);
    }
  }

  observeLCP() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.metrics.lcp = lastEntry.startTime;
      });
      
      observer.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.set('lcp', observer);
    }
  }

  observeCLS() {
    if ('PerformanceObserver' in window) {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
            this.metrics.cls = clsValue;
          }
        });
      });
      
      observer.observe({ entryTypes: ['layout-shift'] });
      this.observers.set('cls', observer);
    }
  }

  observeFID() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.metrics.fid = entry.processingStart - entry.startTime;
        });
      });
      
      observer.observe({ entryTypes: ['first-input'] });
      this.observers.set('fid', observer);
    }
  }

  observeErrors() {
    window.addEventListener('error', (event) => {
      this.metrics.errors = this.metrics.errors || [];
      this.metrics.errors.push({
        type: 'javascript',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        timestamp: Date.now()
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.metrics.errors = this.metrics.errors || [];
      this.metrics.errors.push({
        type: 'promise',
        message: event.reason?.message || event.reason,
        timestamp: Date.now()
      });
    });
  }

  observeNetwork() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'resource') {
            this.metrics.network = this.metrics.network || [];
            this.metrics.network.push({
              name: entry.name,
              type: this.getResourceType(entry.name),
              duration: entry.duration,
              size: entry.transferSize,
              cached: entry.transferSize === 0 && entry.decodedBodySize > 0
            });
          }
        });
      });
      
      observer.observe({ entryTypes: ['resource'] });
      this.observers.set('network', observer);
    }
  }

  getResourceType(url) {
    const extension = url.split('.').pop()?.toLowerCase();
    const typeMap = {
      'js': 'script',
      'css': 'stylesheet',
      'png': 'image',
      'jpg': 'image',
      'jpeg': 'image',
      'gif': 'image',
      'svg': 'image',
      'webp': 'image',
      'woff': 'font',
      'woff2': 'font',
      'ttf': 'font',
      'eot': 'font'
    };
    
    return typeMap[extension] || 'other';
  }

  getMemoryUsage() {
    if ('memory' in performance) {
      this.metrics.memory = {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      };
    }
  }

  sendMetrics() {
    if (!this.shouldSample || !this.options.endpoint) {
      return;
    }

    // Get final metrics
    this.getMemoryUsage();
    this.metrics.pageLoadTime = performance.now() - this.startTime;
    this.metrics.userAgent = navigator.userAgent;
    this.metrics.url = window.location.href;
    this.metrics.timestamp = Date.now();

    const payload = {
      metrics: this.metrics,
      metadata: {
        apiKey: this.options.apiKey,
        version: '1.0.0'
      }
    };

    // Use sendBeacon if available for reliable delivery
    if ('sendBeacon' in navigator) {
      navigator.sendBeacon(this.options.endpoint, JSON.stringify(payload));
    } else {
      // Fallback to fetch with keepalive
      fetch(this.options.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
        keepalive: true
      }).catch(error => {
        this.log('Failed to send metrics:', error);
      });
    }
  }

  getMetrics() {
    return { ...this.metrics };
  }

  log(...args) {
    if (this.options.debug) {
      console.log('[PerformanceMonitor]', ...args);
    }
  }

  destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
  }
}

export default PerformanceMonitor;