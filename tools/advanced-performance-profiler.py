#!/usr/bin/env python3
"""
Advanced System Performance Profiler
Comprehensive performance analysis tool for production systems

Author: KirkBot2 - AI Technical Consultant
Version: 2.0.1
Date: February 4, 2026
"""

import time
import psutil
import json
import sys
import os
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import statistics
import argparse

@dataclass
class PerformanceMetrics:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    process_count: int
    context_switches: int

class AdvancedProfiler:
    def __init__(self, duration: int = 60, interval: float = 1.0):
        self.duration = duration
        self.interval = interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.start_time = None
        self.end_time = None
        self.previous_io = None
        self.previous_net = None
        
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive system performance metrics"""
        timestamp = datetime.now().isoformat()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        load_avg = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # I/O metrics
        current_io = psutil.disk_io_counters()
        if self.previous_io:
            disk_read_mb = (current_io.read_bytes - self.previous_io.read_bytes) / (1024**2)
            disk_write_mb = (current_io.write_bytes - self.previous_io.write_bytes) / (1024**2)
        else:
            disk_read_mb = disk_write_mb = 0
        self.previous_io = current_io
        
        # Network metrics
        current_net = psutil.net_io_counters()
        if self.previous_net:
            network_sent_mb = (current_net.bytes_sent - self.previous_net.bytes_sent) / (1024**2)
            network_recv_mb = (current_net.bytes_recv - self.previous_net.bytes_recv) / (1024**2)
        else:
            network_sent_mb = network_recv_mb = 0
        self.previous_net = current_net
        
        # Process and context metrics
        process_count = len(psutil.pids())
        try:
            context_switches = psutil.cpu_stats().ctx_switches
        except AttributeError:
            context_switches = 0
        
        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            disk_usage_percent=disk_usage_percent,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            load_average=load_avg,
            process_count=process_count,
            context_switches=context_switches
        )
    
    def profile_continuous(self):
        """Run continuous profiling"""
        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(seconds=self.duration)
        
        print(f"Starting advanced system profiling...")
        print(f"Duration: {self.duration} seconds, Interval: {self.interval}s")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            while datetime.now() < end_time:
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Real-time display
                print(f"[{metrics.timestamp[-8:-3]}] "
                      f"CPU: {metrics.cpu_percent:5.1f}% | "
                      f"MEM: {metrics.memory_percent:5.1f}% | "
                      f"Disk R/W: {metrics.disk_read_mb:5.1f}/{metrics.disk_write_mb:5.1f}MB/s | "
                      f"Net S/R: {metrics.network_sent_mb:5.1f}/{metrics.network_recv_mb:5.1f}MB/s")
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\nProfiling interrupted by user")
        
        self.end_time = datetime.now()
        print(f"Profiling completed at {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze collected metrics and generate insights"""
        if not self.metrics_history:
            return {"error": "No metrics collected"}
        
        analysis = {
            "profiling_duration": (self.end_time - self.start_time).total_seconds(),
            "samples_collected": len(self.metrics_history),
            "analysis_timestamp": datetime.now().isoformat(),
            "performance_summary": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # CPU Analysis
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        analysis["performance_summary"]["cpu"] = {
            "average": statistics.mean(cpu_values),
            "max": max(cpu_values),
            "min": min(cpu_values),
            "std_dev": statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
        }
        
        # Memory Analysis
        memory_values = [m.memory_percent for m in self.metrics_history]
        analysis["performance_summary"]["memory"] = {
            "average": statistics.mean(memory_values),
            "max": max(memory_values),
            "min": min(memory_values),
            "std_dev": statistics.stdev(memory_values) if len(memory_values) > 1 else 0
        }
        
        # I/O Analysis
        disk_read_values = [m.disk_read_mb for m in self.metrics_history[1:]]  # Skip first (0) value
        disk_write_values = [m.disk_write_mb for m in self.metrics_history[1:]]
        analysis["performance_summary"]["disk"] = {
            "avg_read_mb_per_sec": statistics.mean(disk_read_values) if disk_read_values else 0,
            "avg_write_mb_per_sec": statistics.mean(disk_write_values) if disk_write_values else 0,
            "total_read_mb": sum(disk_read_values),
            "total_write_mb": sum(disk_write_values)
        }
        
        # Network Analysis
        net_sent_values = [m.network_sent_mb for m in self.metrics_history[1:]]
        net_recv_values = [m.network_recv_mb for m in self.metrics_history[1:]]
        analysis["performance_summary"]["network"] = {
            "avg_sent_mb_per_sec": statistics.mean(net_sent_values) if net_sent_values else 0,
            "avg_recv_mb_per_sec": statistics.mean(net_recv_values) if net_recv_values else 0,
            "total_sent_mb": sum(net_sent_values),
            "total_recv_mb": sum(net_recv_values)
        }
        
        # Identify Bottlenecks
        if analysis["performance_summary"]["cpu"]["max"] > 80:
            analysis["bottlenecks"].append("High CPU usage detected - consider CPU-intensive process optimization")
        
        if analysis["performance_summary"]["memory"]["max"] > 85:
            analysis["bottlenecks"].append("High memory usage - consider memory leak detection or optimization")
        
        if analysis["performance_summary"]["disk"]["avg_read_mb_per_sec"] > 50:
            analysis["bottlenecks"].append("High disk I/O - consider caching or database optimization")
        
        # Generate Recommendations
        if analysis["performance_summary"]["cpu"]["average"] > 50:
            analysis["recommendations"].append("Consider load balancing or scaling for CPU-intensive workloads")
        
        if analysis["performance_summary"]["memory"]["average"] > 60:
            analysis["recommendations"].append("Implement memory monitoring and optimization strategies")
        
        if analysis["performance_summary"]["disk"]["avg_read_mb_per_sec"] > 20:
            analysis["recommendations"].append("Consider SSD upgrade or implement read caching")
        
        return analysis
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate comprehensive performance report"""
        analysis = self.analyze_performance()
        
        report = []
        report.append("# Advanced System Performance Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Profiling Duration: {analysis['profiling_duration']:.1f} seconds")
        report.append(f"Samples Collected: {analysis['samples_collected']}")
        report.append("")
        
        # Performance Summary
        report.append("## Performance Summary")
        summary = analysis["performance_summary"]
        
        report.append(f"### CPU Performance")
        report.append(f"- Average: {summary['cpu']['average']:.1f}%")
        report.append(f"- Maximum: {summary['cpu']['max']:.1f}%")
        report.append(f"- Minimum: {summary['cpu']['min']:.1f}%")
        report.append("")
        
        report.append(f"### Memory Performance")
        report.append(f"- Average: {summary['memory']['average']:.1f}%")
        report.append(f"- Maximum: {summary['memory']['max']:.1f}%")
        report.append(f"- Available Memory (avg): {summary.get('memory', {}).get('available_gb', 0):.2f} GB")
        report.append("")
        
        report.append(f"### Disk I/O")
        report.append(f"- Average Read: {summary['disk']['avg_read_mb_per_sec']:.2f} MB/s")
        report.append(f"- Average Write: {summary['disk']['avg_write_mb_per_sec']:.2f} MB/s")
        report.append(f"- Total Read: {summary['disk']['total_read_mb']:.1f} MB")
        report.append(f"- Total Write: {summary['disk']['total_write_mb']:.1f} MB")
        report.append("")
        
        report.append(f"### Network I/O")
        report.append(f"- Average Sent: {summary['network']['avg_sent_mb_per_sec']:.2f} MB/s")
        report.append(f"- Average Received: {summary['network']['avg_recv_mb_per_sec']:.2f} MB/s")
        report.append(f"- Total Sent: {summary['network']['total_sent_mb']:.1f} MB")
        report.append(f"- Total Received: {summary['network']['total_recv_mb']:.1f} MB")
        report.append("")
        
        # Bottlenecks
        if analysis["bottlenecks"]:
            report.append("## 🔍 Performance Bottlenecks")
            for bottleneck in analysis["bottlenecks"]:
                report.append(f"- {bottleneck}")
            report.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            report.append("## 💡 Optimization Recommendations")
            for rec in analysis["recommendations"]:
                report.append(f"- {rec}")
            report.append("")
        
        # Metrics Data
        report.append("## Detailed Metrics")
        report.append("```json")
        report.append(json.dumps(analysis, indent=2))
        report.append("```")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text
    
    def save_metrics(self, filename: str):
        """Save raw metrics data to file"""
        data = {
            "profiling_session": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration": self.duration,
                "interval": self.interval
            },
            "metrics": [asdict(m) for m in self.metrics_history]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Metrics data saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Advanced System Performance Profiler')
    parser.add_argument('--duration', '-d', type=int, default=60, 
                       help='Profiling duration in seconds (default: 60)')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                       help='Sampling interval in seconds (default: 1.0)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for performance report')
    parser.add_argument('--metrics', '-m', type=str,
                       help='File to save raw metrics data')
    parser.add_argument('--no-display', action='store_true',
                       help='Suppress real-time display')
    
    args = parser.parse_args()
    
    profiler = AdvancedProfiler(duration=args.duration, interval=args.interval)
    
    try:
        # Run profiling
        if args.no_display:
            # Silent profiling
            profiler.start_time = datetime.now()
            end_time = profiler.start_time + timedelta(seconds=args.duration)
            
            while datetime.now() < end_time:
                metrics = profiler.collect_system_metrics()
                profiler.metrics_history.append(metrics)
                time.sleep(args.interval)
            
            profiler.end_time = datetime.now()
        else:
            profiler.profile_continuous()
        
        # Generate analysis
        analysis = profiler.analyze_performance()
        
        # Generate and save report
        report = profiler.generate_report(args.output)
        
        # Save metrics if requested
        if args.metrics:
            profiler.save_metrics(args.metrics)
        
        # Print summary
        print("\n" + "="*60)
        print("PERFORMANCE PROFILING SUMMARY")
        print("="*60)
        print(f"Duration: {analysis['profiling_duration']:.1f} seconds")
        print(f"Samples: {analysis['samples_collected']}")
        print(f"Avg CPU: {analysis['performance_summary']['cpu']['average']:.1f}%")
        print(f"Avg Memory: {analysis['performance_summary']['memory']['average']:.1f}%")
        print(f"Bottlenecks Found: {len(analysis['bottlenecks'])}")
        print(f"Recommendations: {len(analysis['recommendations'])}")
        
        if analysis['bottlenecks']:
            print("\n⚠️  Issues Detected:")
            for issue in analysis['bottlenecks']:
                print(f"  • {issue}")
        
        if analysis['recommendations']:
            print("\n💡 Key Recommendations:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
        
    except Exception as e:
        print(f"Error during profiling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()