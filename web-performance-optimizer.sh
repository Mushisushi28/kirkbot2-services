#!/bin/bash
# Advanced Web Performance Optimization Suite
# AI-powered web performance testing and optimization

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/performance_results"
CONFIG_FILE="${SCRIPT_DIR}/web_optimization_config.json"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Create results directory
mkdir -p "$RESULTS_DIR"

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "Loading configuration from $CONFIG_FILE"
    else
        log "Creating default configuration"
        cat > "$CONFIG_FILE" << 'EOF'
{
  "websites": [
    {
      "name": "Example Site",
      "url": "https://example.com",
      "critical_path": true,
      "budget": {
        "first_contentful_paint": 1500,
        "largest_contentful_paint": 2500,
        "cumulative_layout_shift": 0.1,
        "first_input_delay": 100,
        "total_blocking_time": 300
      }
    }
  ],
  "optimization_level": "aggressive",
  "generate_reports": true,
  "run_lighthouse": true,
  "run_webpagetest": false,
  "webpagetest_api_key": "",
  "cache_results": true,
  "compare_with_baseline": true
}
EOF
    fi
}

# Check dependencies
check_dependencies() {
    log "Checking required dependencies..."
    
    local deps=("curl" "jq" "node" "npm")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing[*]}"
        log "Please install missing dependencies and try again"
        return 1
    fi
    
    # Install Node.js packages if needed
    if [[ ! -d "${SCRIPT_DIR}/node_modules" ]]; then
        log "Installing Node.js dependencies..."
        cd "$SCRIPT_DIR"
        npm init -y > /dev/null 2>&1
        npm install lighthouse chrome-launcher > /dev/null 2>&1
    fi
    
    success "All dependencies satisfied"
}

# Run Lighthouse audit
run_lighthouse() {
    local url=$1
    local site_name=$2
    local output_file="${RESULTS_DIR}/lighthouse_${site_name// /_}_${TIMESTAMP}.json"
    
    log "Running Lighthouse audit for $url..."
    
    cd "$SCRIPT_DIR"
    node << EOF > /dev/null 2>&1
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

(async () => {
    const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
    const options = {logLevel: 'info', output: 'json', port: chrome.port};
    
    const runnerResult = await lighthouse('$url', options);
    
    require('fs').writeFileSync('$output_file', JSON.stringify(runnerResult.lhr, null, 2));
    
    await chrome.kill();
})();
EOF
    
    if [[ -f "$output_file" ]]; then
        success "Lighthouse audit completed: $output_file"
        
        # Extract key metrics
        local fcp=$(jq -r '.audits["first-contentful-paint"].numericValue' "$output_file" | cut -d. -f1)
        local lcp=$(jq -r '.audits["largest-contentful-paint"].numericValue' "$output_file" | cut -d. -f1)
        local cls=$(jq -r '.audits["cumulative-layout-shift"].numericValue' "$output_file")
        local fid=$(jq -r '.audits["max-potential-fid"].numericValue' "$output_file" | cut -d. -f1)
        local tbt=$(jq -r '.audits["total-blocking-time"].numericValue' "$output_file" | cut -d. -f1)
        local performance_score=$(jq -r '.categories.performance.score * 100' "$output_file" | cut -d. -f1)
        
        echo "Performance Metrics for $site_name:" > "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        echo "Performance Score: $performance_score/100" >> "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        echo "First Contentful Paint: ${fcp}ms" >> "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        echo "Largest Contentful Paint: ${lcp}ms" >> "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        echo "Cumulative Layout Shift: $cls" >> "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        echo "First Input Delay: ${fid}ms" >> "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        echo "Total Blocking Time: ${tbt}ms" >> "${RESULTS_DIR}/lighthouse_summary_${site_name// /_}_${TIMESTAMP}.txt"
        
        return 0
    else
        error "Lighthouse audit failed"
        return 1
    fi
}

# Run WebPageTest API
run_webpagetest() {
    local url=$1
    local site_name=$2
    local api_key=$(jq -r '.webpagetest_api_key' "$CONFIG_FILE")
    
    if [[ -z "$api_key" || "$api_key" == "null" ]]; then
        warning "WebPageTest API key not configured, skipping"
        return 0
    fi
    
    log "Running WebPageTest audit for $url..."
    
    local test_id=$(curl -s "https://www.webpagetest.org/runtest.php?url=$(echo "$url" | sed 's/&/\%26/g')&k=$api_key&f=json&location=us-east1:Chrome" | jq -r '.data.testId // empty')
    
    if [[ -n "$test_id" ]]; then
        log "WebPageTest started, test ID: $test_id"
        
        # Wait for results
        local status="running"
        local attempts=0
        local max_attempts=30
        
        while [[ "$status" == "running" && $attempts -lt $max_attempts ]]; do
            sleep 10
            status=$(curl -s "https://www.webpagetest.org/testStatus.php?test=$test_id&f=json" | jq -r '.data.status // "running"')
            ((attempts++))
        done
        
        if [[ "$status" == "completed" ]]; then
            local results_json=$(curl -s "https://www.webpagetest.org/jsonResult.php?test=$test_id&pagespeed=1&breakdown=1&requests=1")
            echo "$results_json" > "${RESULTS_DIR}/webpagetest_${site_name// /_}_${TIMESTAMP}.json"
            
            # Extract key metrics
            local ttfb=$(echo "$results_json" | jq -r '.data.runs["1"].firstView.TTFB // 0')
            local load_time=$(echo "$results_json" | jq -r '.data.runs["1"].firstView.loadTime // 0')
            local speed_index=$(echo "$results_json" | jq -r '.data.runs["1"].firstView.SpeedIndex // 0')
            
            echo "WebPageTest Results for $site_name:" > "${RESULTS_DIR}/webpagetest_summary_${site_name// /_}_${TIMESTAMP}.txt"
            echo "Time to First Byte: ${ttfb}ms" >> "${RESULTS_DIR}/webpagetest_summary_${site_name// /_}_${TIMESTAMP}.txt"
            echo "Load Time: ${load_time}ms" >> "${RESULTS_DIR}/webpagetest_summary_${site_name// /_}_${TIMESTAMP}.txt"
            echo "Speed Index: $speed_index" >> "${RESULTS_DIR}/webpagetest_summary_${site_name// /_}_${TIMESTAMP}.txt"
            
            success "WebPageTest audit completed"
        else
            error "WebPageTest did not complete within timeout"
        fi
    else
        error "Failed to start WebPageTest"
    fi
}

# Generate optimization recommendations
generate_recommendations() {
    local site_name=$1
    local lighthouse_file="${RESULTS_DIR}/lighthouse_${site_name// /_}_${TIMESTAMP}.json"
    
    if [[ ! -f "$lighthouse_file" ]]; then
        warning "No Lighthouse results found for $site_name"
        return 1
    fi
    
    log "Generating AI-powered optimization recommendations for $site_name..."
    
    # Extract audit data
    local performance_score=$(jq -r '.categories.performance.score * 100' "$lighthouse_file" | cut -d. -f1)
    local audits=$(jq -r '.audits | to_entries[] | select(.value.score != null) | select(.value.score < 0.9) | "\(.key): \(.value.title) (Score: \(.value.score * 100 | floor))"' "$lighthouse_file")
    
    # Create recommendations report
    {
        echo "# AI-Powered Performance Optimization Recommendations"
        echo "# Site: $site_name"
        echo "# Generated: $(date)"
        echo "# Current Performance Score: $performance_score/100"
        echo ""
        echo "## Critical Issues to Address:"
        echo ""
        
        echo "$audits" | while IFS=: read -r key title score_info; do
            local description=$(jq -r ".audits.$key.description" "$lighthouse_file")
            echo "### $title"
            echo "**Score:** $score_info"
            echo "**Issue:** $description"
            echo ""
            
            # Generate specific recommendations based on audit type
            case "$key" in
                "uses-webp-images")
                    echo "**Recommendation:** Convert JPEG/PNG images to WebP format for 30% smaller file sizes with equivalent quality."
                    echo "**Implementation:**"
                    echo "  - Use image conversion tools (cwebp, squoosh)"
                    echo "  - Implement <picture> element with WebP fallback"
                    echo "  - Enable WebP in CDN settings"
                    ;;
                "unused-css-rules")
                    echo "**Recommendation:** Remove unused CSS to reduce bundle size and improve parsing performance."
                    echo "**Implementation:**"
                    echo "  - Use PurgeCSS or UnCSS to remove unused styles"
                    echo "  - Implement CSS code splitting"
                    echo "  - Consider critical CSS inlining"
                    ;;
                "render-blocking-resources")
                    echo "**Recommendation:** Eliminate render-blocking resources to improve first paint."
                    echo "**Implementation:**"
                    echo "  - Add async/defer attributes to non-critical scripts"
                    echo "  - Use preload for critical resources"
                    echo "  - Implement resource hints (dns-prefetch, preconnect)"
                    ;;
                "unused-javascript")
                    echo "**Recommendation:** Remove unused JavaScript to reduce download and execution time."
                    echo "**Implementation:**"
                    echo "  - Use tree-shaking with bundlers (webpack, rollup)"
                    echo "  - Implement code splitting by routes"
                    echo "  - Remove unused libraries and dependencies"
                    ;;
                "efficient-animated-content")
                    echo "**Recommendation:** Optimize animated content for better performance."
                    echo "**Implementation:**"
                    echo "  - Use CSS animations instead of JavaScript when possible"
                    echo "  - Implement will-change property cautiously"
                    echo "  - Consider reducing animation complexity"
                    ;;
                *)
                    echo "**Recommendation:** Review and optimize based on the specific issue identified."
                    ;;
            esac
            echo ""
            echo "---"
            echo ""
        done
        
        echo "## General Performance Best Practices:"
        echo ""
        echo "1. **Image Optimization:**"
        echo "   - Compress images (target: <500KB for hero images)"
        echo "   - Use responsive images with srcset"
        echo "   - Implement lazy loading for below-the-fold images"
        echo ""
        echo "2. **Caching Strategy:**"
        echo "   - Set appropriate cache headers (Cache-Control, ETag)"
        echo "   - Implement service worker for offline support"
        echo "   - Use CDN for static assets"
        echo ""
        echo "3. **Network Optimization:**"
        echo "   - Enable HTTP/2 or HTTP/3"
        echo "   - Implement resource bundling"
        echo "   - Use Brotli compression"
        echo ""
        echo "4. **JavaScript Performance:**"
        echo "   - Minimize main thread work"
        echo "   - Use web workers for heavy computations"
        echo "   - Implement code splitting and lazy loading"
        echo ""
    } > "${RESULTS_DIR}/recommendations_${site_name// /_}_${TIMESTAMP}.md"
    
    success "Recommendations generated: ${RESULTS_DIR}/recommendations_${site_name// /_}_${TIMESTAMP}.md"
}

# Compare with baseline
compare_with_baseline() {
    local site_name=$1
    local baseline_file="${RESULTS_DIR}/baseline_${site_name// /_}.json"
    local current_file="${RESULTS_DIR}/lighthouse_${site_name// /_}_${TIMESTAMP}.json"
    
    if [[ ! -f "$baseline_file" ]]; then
        warning "No baseline found for $site_name, creating new baseline"
        cp "$current_file" "$baseline_file"
        return 0
    fi
    
    log "Comparing performance with baseline for $site_name..."
    
    local baseline_score=$(jq -r '.categories.performance.score * 100' "$baseline_file" | cut -d. -f1)
    local current_score=$(jq -r '.categories.performance.score * 100' "$current_file" | cut -d. -f1)
    local score_change=$((current_score - baseline_score))
    
    local baseline_fcp=$(jq -r '.audits["first-contentful-paint"].numericValue' "$baseline_file" | cut -d. -f1)
    local current_fcp=$(jq -r '.audits["first-contentful-paint"].numericValue' "$current_file" | cut -d. -f1)
    local fcp_change=$((current_fcp - baseline_fcp))
    
    {
        echo "# Performance Comparison Report"
        echo "# Site: $site_name"
        echo "# Generated: $(date)"
        echo ""
        echo "## Performance Score Comparison"
        echo "- **Baseline:** $baseline_score/100"
        echo "- **Current:** $current_score/100"
        echo "- **Change:** ${score_change:+$score_change} points"
        echo ""
        echo "## First Contentful Paint Comparison"
        echo "- **Baseline:** ${baseline_fcp}ms"
        echo "- **Current:** ${current_fcp}ms"
        echo "- **Change:** ${fcp_change:+$fcp_change}ms"
        echo ""
        
        if [[ $score_change -gt 0 ]]; then
            echo "🎉 Performance has **improved** by $score_change points!"
        elif [[ $score_change -lt 0 ]]; then
            echo "⚠️ Performance has **degraded** by ${score_change#-} points."
        else
            echo "➡️ Performance score remains **unchanged**."
        fi
    } > "${RESULTS_DIR}/comparison_${site_name// /_}_${TIMESTAMP}.md"
    
    success "Comparison report generated: ${RESULTS_DIR}/comparison_${site_name// /_}_${TIMESTAMP}.md"
}

# Generate comprehensive report
generate_comprehensive_report() {
    local report_file="${RESULTS_DIR}/comprehensive_report_${TIMESTAMP}.html"
    
    log "Generating comprehensive HTML report..."
    
    cat > "$report_file" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Performance Optimization Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .metric { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
        .good { border-left-color: #27ae60; }
        .warning { border-left-color: #f39c12; }
        .critical { border-left-color: #e74c3c; }
        .score { font-size: 24px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Web Performance Optimization Report</h1>
        <p><strong>Generated:</strong> $(date)</p>
        <p><strong>Analysis Tool:</strong> AI-Powered Web Performance Suite</p>
        
EOF
    
    # Add site summaries
    for site in $(jq -r '.websites[].name' "$CONFIG_FILE"); do
        local site_clean=${site// /_}
        local summary_file="${RESULTS_DIR}/lighthouse_summary_${site_clean}_${TIMESTAMP}.txt"
        
        if [[ -f "$summary_file" ]]; then
            echo "<h2>📊 $site Performance Summary</h2>" >> "$report_file"
            while IFS= read -r line; do
                echo "<div class='metric'>$line</div>" >> "$report_file"
            done < "$summary_file"
        fi
    done
    
    # Close HTML
    cat >> "$report_file" << 'EOF'
    </div>
</body>
</html>
EOF
    
    success "Comprehensive report generated: $report_file"
}

# Main execution
main() {
    log "🚀 Starting Advanced Web Performance Optimization Suite"
    
    # Load configuration
    load_config
    
    # Check dependencies
    check_dependencies || exit 1
    
    # Process each website
    local websites_count=$(jq '.websites | length' "$CONFIG_FILE")
    
    for ((i=0; i<websites_count; i++)); do
        local url=$(jq -r ".websites[$i].url" "$CONFIG_FILE")
        local name=$(jq -r ".websites[$i].name" "$CONFIG_FILE")
        
        log "Processing website: $name ($url)"
        
        # Run Lighthouse
        if [[ "$(jq -r '.run_lighthouse' "$CONFIG_FILE")" == "true" ]]; then
            run_lighthouse "$url" "$name" || continue
        fi
        
        # Run WebPageTest
        if [[ "$(jq -r '.run_webpagetest' "$CONFIG_FILE")" == "true" ]]; then
            run_webpagetest "$url" "$name"
        fi
        
        # Generate recommendations
        if [[ "$(jq -r '.generate_reports' "$CONFIG_FILE")" == "true" ]]; then
            generate_recommendations "$name"
        fi
        
        # Compare with baseline
        if [[ "$(jq -r '.compare_with_baseline' "$CONFIG_FILE")" == "true" ]]; then
            compare_with_baseline "$name"
        fi
    done
    
    # Generate comprehensive report
    if [[ "$(jq -r '.generate_reports' "$CONFIG_FILE")" == "true" ]]; then
        generate_comprehensive_report
    fi
    
    success "🎉 Web Performance Optimization completed successfully!"
    log "📁 Results saved to: $RESULTS_DIR"
    log "📊 View the comprehensive report: ${RESULTS_DIR}/comprehensive_report_${TIMESTAMP}.html"
}

# Help function
show_help() {
    cat << EOF
Advanced Web Performance Optimization Suite

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -c, --config FILE       Use custom configuration file
    -o, --output DIR        Specify output directory
    --dry-run               Show what would be done without executing

EXAMPLES:
    $0                      Run with default configuration
    $0 -c my_config.json    Use custom configuration
    $0 -o /tmp/results      Save results to specific directory

CONFIGURATION:
    Edit $CONFIG_FILE to configure websites and settings

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            RESULTS_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main