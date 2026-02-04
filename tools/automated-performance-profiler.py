#!/usr/bin/env python3
"""
Automated Performance Profiler - Advanced System Analysis Tool
Real-time performance monitoring and bottleneck detection
"""

import psutil
import time
import json
import argparse
import threading
from datetime import datetime
from typing import Dict, List, Any
import sys

class PerformanceProfiler:
    def __init__(self, duration: int = 60, interval: float = 1.0):
        self.duration = duration
        self.interval = interval
        self.metrics = []
        self.start_time = None
        self.running = False
        
    def collect_metrics(self):
        """Collect system performance metrics"""
        timestamp = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process metrics
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0.1 or pinfo['memory_percent'] > 0.1:
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        metric = {
            'timestamp': timestamp.isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'frequency': cpu_freq.current if cpu_freq else None,
                'count': cpu_count,
                'load_average': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100,
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'processes': sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
        }
        
        self.metrics.append(metric)
        
    def start_profiling(self):
        """Start performance profiling"""
        print(f"🚀 Starting performance profiler for {self.duration} seconds...")
        print(f"📊 Collecting metrics every {self.interval} seconds\n")
        
        self.start_time = time.time()
        self.running = True
        
        while self.running and (time.time() - self.start_time) < self.duration:
            self.collect_metrics()
            elapsed = time.time() - self.start_time
            remaining = self.duration - elapsed
            progress = (elapsed / self.duration) * 100
            
            print(f"\r⏱️  Progress: {progress:.1f}% | Time remaining: {remaining:.1f}s", end="")
            time.sleep(self.interval)
        
        print("\n✅ Profiling completed!")
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze collected metrics and generate insights"""
        if not self.metrics:
            return {"error": "No metrics collected"}
        
        # Calculate averages and peaks
        cpu_values = [m['cpu']['percent'] for m in self.metrics]
        memory_values = [m['memory']['percent'] for m in self.metrics]
        
        analysis = {
            'summary': {
                'duration': self.duration,
                'samples': len(self.metrics),
                'start_time': self.metrics[0]['timestamp'],
                'end_time': self.metrics[-1]['timestamp']
            },
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values),
                'peak': max(cpu_values),
                'min': min(cpu_values),
                'utilization_rate': len([c for c in cpu_values if c > 50]) / len(cpu_values) * 100
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values),
                'peak': max(memory_values),
                'min': min(memory_values),
                'pressure_time': len([m for m in memory_values if m > 80]) / len(memory_values) * 100
            },
            'bottlenecks': self.detect_bottlenecks(),
            'recommendations': self.generate_recommendations(),
            'performance_score': self.calculate_performance_score()
        }
        
        return analysis
    
    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        # CPU bottlenecks
        cpu_peaks = [m for m in self.metrics if m['cpu']['percent'] > 80]
        if len(cpu_peaks) > len(self.metrics) * 0.2:
            bottlenecks.append({
                'type': 'CPU',
                'severity': 'High' if len(cpu_peaks) > len(self.metrics) * 0.5 else 'Medium',
                'description': f'CPU usage exceeded 80% for {len(cpu_peaks)} samples',
                'impact': 'System responsiveness may be degraded'
            })
        
        # Memory bottlenecks
        memory_peaks = [m for m in self.metrics if m['memory']['percent'] > 85]
        if memory_peaks:
            bottlenecks.append({
                'type': 'Memory',
                'severity': 'High' if len(memory_peaks) > len(self.metrics) * 0.3 else 'Medium',
                'description': f'Memory usage exceeded 85% for {len(memory_peaks)} samples',
                'impact': 'Risk of memory pressure and swapping'
            })
        
        # Identify resource-intensive processes
        process_counts = {}
        for metric in self.metrics:
            for proc in metric['processes'][:3]:  # Top 3 processes
                name = proc['name']
                if name not in process_counts:
                    process_counts[name] = {'count': 0, 'cpu_total': 0, 'memory_total': 0}
                process_counts[name]['count'] += 1
                process_counts[name]['cpu_total'] += proc.get('cpu_percent', 0)
                process_counts[name]['memory_total'] += proc.get('memory_percent', 0)
        
        # Add top resource consumers as bottlenecks
        top_processes = sorted(process_counts.items(), 
                             key=lambda x: x[1]['cpu_total'], reverse=True)[:2]
        
        for proc_name, proc_data in top_processes:
            if proc_data['count'] > len(self.metrics) * 0.5:
                bottlenecks.append({
                    'type': 'Process',
                    'severity': 'Medium',
                    'description': f'{proc_name} consistently high CPU/memory usage',
                    'impact': 'Process may be optimized or investigated'
                })
        
        return bottlenecks
    
    def generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        avg_cpu = sum(m['cpu']['percent'] for m in self.metrics) / len(self.metrics)
        avg_memory = sum(m['memory']['percent'] for m in self.metrics) / len(self.metrics)
        
        if avg_cpu > 70:
            recommendations.append("🔧 Optimize CPU-intensive processes or scale horizontally")
        
        if avg_memory > 75:
            recommendations.append("💾 Consider memory optimization or adding RAM")
        
        # Check for I/O bottlenecks
        disk_usage = self.metrics[-1]['disk']['percent']
        if disk_usage > 90:
            recommendations.append("📀 Disk space critically low - clean up or expand storage")
        
        if len(self.metrics) > 10:
            recommendations.append("📊 Consider implementing automated monitoring and alerting")
            recommendations.append("⚡ Implement performance optimization caching strategies")
        
        if not recommendations:
            recommendations.append("✅ System performance appears optimal - continue monitoring")
        
        return recommendations
    
    def calculate_performance_score(self) -> int:
        """Calculate overall performance score (0-100)"""
        avg_cpu = sum(m['cpu']['percent'] for m in self.metrics) / len(self.metrics)
        avg_memory = sum(m['memory']['percent'] for m in self.metrics) / len(self.metrics)
        
        # Start with perfect score
        score = 100
        
        # Penalize high CPU usage
        if avg_cpu > 80:
            score -= 30
        elif avg_cpu > 60:
            score -= 15
        elif avg_cpu > 40:
            score -= 5
        
        # Penalize high memory usage
        if avg_memory > 85:
            score -= 30
        elif avg_memory > 70:
            score -= 15
        elif avg_memory > 50:
            score -= 5
        
        # Penalize bottlenecks
        bottlenecks = self.detect_bottlenecks()
        high_severity = len([b for b in bottlenecks if b['severity'] == 'High'])
        medium_severity = len([b for b in bottlenecks if b['severity'] == 'Medium'])
        
        score -= high_severity * 20
        score -= medium_severity * 10
        
        return max(0, min(100, score))
    
    def save_report(self, analysis: Dict[str, Any], filename: str = None):
        """Save analysis report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'tool': 'KirkBot2 Automated Performance Profiler',
                'version': '1.0.0',
                'business_context': 'AI Performance Optimization Services'
            },
            'raw_metrics': self.metrics,
            'analysis': analysis
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='Advanced Performance Profiler by KirkBot2 AI')
    parser.add_argument('--duration', '-d', type=int, default=60,
                       help='Profiling duration in seconds (default: 60)')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                       help='Collection interval in seconds (default: 1.0)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output filename for report (auto-generated if not specified)')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with detailed metrics')
    
    args = parser.parse_args()
    
    print("🚀 KirkBot2 AI - Automated Performance Profiler")
    print("=" * 50)
    
    # Initialize profiler
    profiler = PerformanceProfiler(duration=args.duration, interval=args.interval)
    
    # Start profiling
    analysis = profiler.start_profiling()
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\n🎯 Performance Score: {analysis['performance_score']}/100")
    print(f"⏱️  Duration: {analysis['summary']['duration']} seconds")
    print(f"📈 Samples Collected: {analysis['summary']['samples']}")
    
    print(f"\n💻 CPU Performance:")
    print(f"   Average Usage: {analysis['cpu']['average']:.1f}%")
    print(f"   Peak Usage: {analysis['cpu']['peak']:.1f}%")
    print(f"   Utilization Rate: {analysis['cpu']['utilization_rate']:.1f}%")
    
    print(f"\n💾 Memory Performance:")
    print(f"   Average Usage: {analysis['memory']['average']:.1f}%")
    print(f"   Peak Usage: {analysis['memory']['peak']:.1f}%")
    print(f"   Pressure Time: {analysis['memory']['pressure_time']:.1f}%")
    
    if analysis['bottlenecks']:
        print(f"\n⚠️  Performance Bottlenecks:")
        for bottleneck in analysis['bottlenecks']:
            print(f"   • {bottleneck['type']} ({bottleneck['severity']}): {bottleneck['description']}")
    
    if analysis['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"   {rec}")
    
    # Save report
    report_file = profiler.save_report(analysis, args.output)
    
    if args.json:
        print(f"\n📄 JSON Report:")
        print(json.dumps(analysis, indent=2))
    
    print(f"\n🎉 Performance profiling complete!")
    print(f"📞 For optimization services: kirkbot2.consulting@gmail.com")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Profiling interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)