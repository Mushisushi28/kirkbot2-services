#!/bin/bash
# KirkBot2 Optimization Tools Suite
# Comprehensive system optimization and analysis tools

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script information
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    case $level in
        "INFO")  echo -e "${GREEN}[INFO]${NC}  ${timestamp} - ${message}" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC}  ${timestamp} - ${message}" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - ${message}" ;;
        "DEBUG") echo -e "${BLUE}[DEBUG]${NC} ${timestamp} - ${message}" ;;
        *)       echo "${timestamp} - ${message}" ;;
    esac
}

# System information gathering
gather_system_info() {
    log "INFO" "Gathering system information..."
    
    echo "=== SYSTEM INFORMATION ==="
    echo "Timestamp: $TIMESTAMP"
    echo "Hostname: $(hostname)"
    echo "OS: $(uname -a)"
    echo "Uptime: $(uptime)"
    echo "Load Average: $(cat /proc/loadavg)"
    echo ""
    
    echo "=== CPU INFORMATION ==="
    if command -v lscpu >/dev/null 2>&1; then
        lscpu | grep -E "(Model name|CPU\(s\)|Thread|Core|Socket)"
    else
        cat /proc/cpuinfo | grep -E "(processor|model name|cpu MHz)" | head -10
    fi
    echo ""
    
    echo "=== MEMORY INFORMATION ==="
    if command -v free >/dev/null 2>&1; then
        free -h
    else
        cat /proc/meminfo | head -10
    fi
    echo ""
    
    echo "=== DISK USAGE ==="
    df -h | head -10
    echo ""
    
    echo "=== NETWORK INTERFACES ==="
    ip addr show | grep -E "(inet|UP|DOWN)" | head -20
    echo ""
}

# Performance analysis
analyze_performance() {
    log "INFO" "Analyzing system performance..."
    
    echo "=== PERFORMANCE METRICS ==="
    
    # CPU usage
    echo "CPU Usage (last minute):"
    if command -v mpstat >/dev/null 2>&1; then
        mpstat 1 1 | tail -1
    else
        top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//'
    fi
    echo ""
    
    # Memory pressure
    echo "Memory Pressure:"
    local mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    local mem_usage=$(( (mem_total - mem_available) * 100 / mem_total ))
    echo "Memory Usage: ${mem_usage}%"
    echo ""
    
    # Disk I/O
    echo "Disk I/O Statistics:"
    if command -v iostat >/dev/null 2>&1; then
        iostat -x 1 1 | tail -n +4
    else
        echo "iostat not available - basic disk info:"
        df -i | head -5
    fi
    echo ""
    
    # Network I/O
    echo "Network I/O:"
    cat /proc/net/dev | grep -E "(eth|en|wl)" | head -5
    echo ""
}

# Process analysis
analyze_processes() {
    log "INFO" "Analyzing running processes..."
    
    echo "=== TOP PROCESSES BY CPU ==="
    if command -v ps >/dev/null 2>&1; then
        ps aux --sort=-%cpu | head -10
    else
        echo "ps command not available"
    fi
    echo ""
    
    echo "=== TOP PROCESSES BY MEMORY ==="
    if command -v ps >/dev/null 2>&1; then
        ps aux --sort=-%mem | head -10
    else
        echo "ps command not available"
    fi
    echo ""
    
    echo "=== SERVICE STATUS ==="
    if command -v systemctl >/dev/null 2>&1; then
        systemctl list-units --type=service --state=running | head -10
    else
        echo "systemctl not available"
    fi
    echo ""
}

# Security analysis
analyze_security() {
    log "INFO" "Performing security analysis..."
    
    echo "=== SECURITY ANALYSIS ==="
    
    # Check for open ports
    echo "Open Ports:"
    if command -v netstat >/dev/null 2>&1; then
        netstat -tlnp 2>/dev/null | head -10
    elif command -v ss >/dev/null 2>&1; then
        ss -tlnp | head -10
    else
        echo "Neither netstat nor ss available"
    fi
    echo ""
    
    # Check for failed login attempts
    echo "Recent Failed Logins:"
    if [ -f /var/log/auth.log ]; then
        grep "Failed password" /var/log/auth.log | tail -5 || echo "No failed logins found"
    elif [ -f /var/log/secure ]; then
        grep "Failed password" /var/log/secure | tail -5 || echo "No failed logins found"
    else
        echo "Auth log file not found"
    fi
    echo ""
    
    # Check system updates
    echo "System Update Status:"
    if command -v apt >/dev/null 2>&1; then
        apt list --upgradable 2>/dev/null | wc -l | xargs echo "Packages available for update:"
    elif command -v yum >/dev/null 2>&1; then
        yum check-update >/dev/null 2>&1 && echo "System up to date" || echo "Updates available"
    else
        echo "Package manager not detected"
    fi
    echo ""
}

# Code optimization analysis
analyze_codebase() {
    log "INFO" "Analyzing codebase optimization opportunities..."
    
    local target_dir="${1:-.}"
    
    echo "=== CODEBASE ANALYSIS ==="
    echo "Target Directory: $(realpath "$target_dir")"
    echo ""
    
    # Count files by type
    echo "File Distribution:"
    find "$target_dir" -type f -name "*.py" | wc -l | xargs echo "Python files:"
    find "$target_dir" -type f -name "*.js" | wc -l | xargs echo "JavaScript files:"
    find "$target_dir" -type f -name "*.ts" | wc -l | xargs echo "TypeScript files:"
    find "$target_dir" -type f -name "*.go" | wc -l | xargs echo "Go files:"
    find "$target_dir" -type f -name "*.java" | wc -l | xargs echo "Java files:"
    echo ""
    
    # Check for common issues
    echo "Potential Optimization Opportunities:"
    
    # Large files
    echo "Large files (>1MB):"
    find "$target_dir" -type f -size +1M -exec ls -lh {} \; 2>/dev/null | head -5 || echo "No large files found"
    echo ""
    
    # Duplicate files (basic check)
    echo "Potential duplicate files:"
    find "$target_dir" -type f -name "*.py" -exec basename {} \; | sort | uniq -d | head -5 || echo "No duplicate Python files found"
    echo ""
    
    # Configuration files
    echo "Configuration files found:"
    find "$target_dir" -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.ini" | head -10
    echo ""
}

# Generate optimization recommendations
generate_recommendations() {
    log "INFO" "Generating optimization recommendations..."
    
    echo "=== OPTIMIZATION RECOMMENDATIONS ==="
    
    # Check available memory
    local mem_available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    if [ "$mem_available" -lt 1048576 ]; then  # Less than 1GB
        echo "⚠️  Low memory detected - consider adding RAM or optimizing memory usage"
    fi
    
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        echo "⚠️  High disk usage ($disk_usage%) - consider cleanup or expansion"
    fi
    
    # Check load average
    local load_avg=$(cat /proc/loadavg | awk '{print $1}')
    local cpu_count=$(nproc)
    if (( $(echo "$load_avg > $cpu_count" | bc -l) )); then
        echo "⚠️  High load average detected - investigate CPU bottlenecks"
    fi
    
    # General recommendations
    echo "💡 General Optimizations:"
    echo "  • Regular system updates and security patches"
    echo "  • Implement monitoring and alerting"
    echo "  • Optimize database queries and indexes"
    echo "  • Use caching strategies for frequently accessed data"
    echo "  • Implement proper logging and log rotation"
    echo "  • Regular backup verification"
    echo ""
    
    # Performance-specific
    echo "🚀 Performance Optimizations:"
    echo "  • Profile applications to identify bottlenecks"
    echo "  • Implement connection pooling for databases"
    echo "  • Use CDN for static assets"
    echo "  • Optimize images and media files"
    echo "  • Consider load balancing for high-traffic applications"
    echo ""
    
    # Security recommendations
    echo "🔒 Security Optimizations:"
    echo "  • Implement proper authentication and authorization"
    echo "  • Use HTTPS/TLS encryption"
    echo "  • Regular security audits and penetration testing"
    echo "  • Implement proper input validation and sanitization"
    echo "  • Keep all dependencies and libraries updated"
    echo ""
}

# Performance benchmarking
run_benchmarks() {
    log "INFO" "Running performance benchmarks..."
    
    echo "=== PERFORMANCE BENCHMARKS ==="
    
    # CPU benchmark (simple)
    echo "CPU Benchmark (calculating π):"
    if command -v python3 >/dev/null 2>&1; then
        local start_time=$(date +%s.%N)
        python3 -c "
import math
import time
start = time.time()
for i in range(1000000):
    math.sqrt(i)
end = time.time()
print(f'Calculation time: {end - start:.4f} seconds')
"
    fi
    echo ""
    
    # Memory benchmark
    echo "Memory Benchmark:"
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import time
start = time.time()
data = []
for i in range(100000):
    data.append(list(range(100)))
end = time.time()
print(f'Memory allocation time: {end - start:.4f} seconds')
print(f'Allocated {len(data) * len(data[0])} integers')
"
    fi
    echo ""
    
    # Disk I/O benchmark
    echo "Disk I/O Benchmark:"
    local test_file="/tmp/kirkbot2_benchmark.tmp"
    local start_time=$(date +%s.%N)
    dd if=/dev/zero of="$test_file" bs=1M count=100 2>/dev/null
    local end_time=$(date +%s.%N)
    local io_time=$(echo "$end_time - $start_time" | bc -l)
    echo "Disk write time (100MB): ${io_time} seconds"
    rm -f "$test_file"
    echo ""
}

# Generate comprehensive report
generate_report() {
    local output_file="${1:-kirkbot2-optimization-report-$(date +%Y%m%d-%H%M%S).txt}"
    
    log "INFO" "Generating comprehensive report: $output_file"
    
    {
        echo "KIRKBOT2 OPTIMIZATION REPORT"
        echo "=============================="
        echo "Generated: $TIMESTAMP"
        echo "Version: $VERSION"
        echo ""
        
        gather_system_info
        echo ""
        
        analyze_performance
        echo ""
        
        analyze_processes
        echo ""
        
        analyze_security
        echo ""
        
        analyze_codebase .
        echo ""
        
        generate_recommendations
        echo ""
        
        run_benchmarks
        echo ""
        
        echo "=== REPORT SUMMARY ==="
        echo "This report provides a comprehensive analysis of your system's performance,"
        echo "security, and optimization opportunities. Review the recommendations above"
        echo "and prioritize actions based on your specific requirements and constraints."
        echo ""
        echo "For detailed optimization services, contact KirkBot2 for professional consulting."
        echo ""
        echo "Report completed: $(date)"
        
    } > "$output_file"
    
    log "INFO" "Report saved to: $output_file"
}

# Main function
main() {
    echo "KirkBot2 Optimization Tools Suite v$VERSION"
    echo "=========================================="
    echo ""
    
    case "${1:-full}" in
        "system")
            gather_system_info
            ;;
        "performance")
            analyze_performance
            ;;
        "processes")
            analyze_processes
            ;;
        "security")
            analyze_security
            ;;
        "codebase")
            analyze_codebase "${2:-.}"
            ;;
        "recommendations")
            generate_recommendations
            ;;
        "benchmarks")
            run_benchmarks
            ;;
        "report")
            generate_report "${2:-}"
            ;;
        "full")
            gather_system_info
            echo ""
            analyze_performance
            echo ""
            analyze_processes
            echo ""
            analyze_security
            echo ""
            analyze_codebase .
            echo ""
            generate_recommendations
            echo ""
            run_benchmarks
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  system           - Display system information"
            echo "  performance      - Analyze system performance"
            echo "  processes        - Analyze running processes"
            echo "  security         - Perform security analysis"
            echo "  codebase [dir]   - Analyze codebase optimization opportunities"
            echo "  recommendations  - Generate optimization recommendations"
            echo "  benchmarks       - Run performance benchmarks"
            echo "  report [file]    - Generate comprehensive report"
            echo "  full             - Run complete analysis (default)"
            echo "  help             - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run complete analysis"
            echo "  $0 performance         # Performance analysis only"
            echo "  $0 codebase ./src      # Analyze specific directory"
            echo "  $0 report my-report.txt # Generate custom report"
            exit 0
            ;;
        *)
            log "ERROR" "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
    
    echo ""
    echo "✅ Analysis complete!"
    echo "💡 For professional optimization services, contact KirkBot2"
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    for cmd in bc python3; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "WARN" "Missing optional dependencies: ${missing_deps[*]}"
        log "INFO" "Some features may be limited"
    fi
}

# Run dependency check
check_dependencies

# Execute main function
main "$@"