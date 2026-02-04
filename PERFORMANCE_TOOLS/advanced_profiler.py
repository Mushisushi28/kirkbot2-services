#!/usr/bin/env python3
"""
Advanced Performance Profiler
AI-powered system performance analysis and bottleneck detection
"""

import time
import psutil
import threading
import json
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
import statistics

class AdvancedProfiler:
    """Advanced performance monitoring and analysis system"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.metrics_history = deque(maxlen=3600)  # 1 hour of data at 1s intervals
        self.alerts = []
        self.baseline_metrics = {}
        
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        print("🔍 Advanced performance monitoring started")
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        print("⏹️ Performance monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self._analyze_performance(metrics)
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        current_time = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())
        
        # Process metrics
        processes = len(psutil.pids())
        
        return {
            'timestamp': current_time.isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'frequency': cpu_freq.current if cpu_freq else None
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
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
                'connections': net_connections
            },
            'processes': processes
        }
        
    def _analyze_performance(self, current_metrics: Dict[str, Any]):
        """Analyze current metrics for performance issues"""
        alerts = []
        
        # CPU analysis
        if current_metrics['cpu']['percent'] > 80:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"High CPU usage: {current_metrics['cpu']['percent']:.1f}%",
                'value': current_metrics['cpu']['percent']
            })
            
        # Memory analysis
        if current_metrics['memory']['percent'] > 85:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f"High memory usage: {current_metrics['memory']['percent']:.1f}%",
                'value': current_metrics['memory']['percent']
            })
            
        # Disk analysis
        if current_metrics['disk']['percent'] > 90:
            alerts.append({
                'type': 'disk_full',
                'severity': 'critical',
                'message': f"Disk space critical: {current_metrics['disk']['percent']:.1f}%",
                'value': current_metrics['disk']['percent']
            })
            
        # Swap usage analysis
        if current_metrics['memory']['swap_percent'] > 50:
            alerts.append({
                'type': 'swap_high',
                'severity': 'warning',
                'message': f"High swap usage: {current_metrics['memory']['swap_percent']:.1f}%",
                'value': current_metrics['memory']['swap_percent']
            })
            
        for alert in alerts:
            if self._should_alert(alert):
                self.alerts.append(alert)
                print(f"🚨 {alert['message']}")
                
    def _should_alert(self, alert: Dict[str, Any]) -> bool:
        """Determine if an alert should be generated"""
        # Avoid alert spam - check if similar alert was generated recently
        recent_alerts = [a for a in self.alerts 
                        if a['type'] == alert['type'] 
                        and (datetime.now() - datetime.fromisoformat(a.get('timestamp', datetime.now().isoformat()))).seconds < 300]
        return len(recent_alerts) == 0
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}
            
        # Calculate averages and statistics
        cpu_values = [m['cpu']['percent'] for m in self.metrics_history]
        memory_values = [m['memory']['percent'] for m in self.metrics_history]
        
        # Performance score (0-100)
        performance_score = self._calculate_performance_score()
        
        return {
            'report_generated': datetime.now().isoformat(),
            'monitoring_duration_seconds': len(self.metrics_history) * self.monitoring_interval,
            'performance_score': performance_score,
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': statistics.mean(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'percentile_95': statistics.quantiles(cpu_values, n=20)[18] if len(cpu_values) > 20 else max(cpu_values)
            },
            'memory': {
                'current': memory_values[-1] if memory_values else 0,
                'average': statistics.mean(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'percentile_95': statistics.quantiles(memory_values, n=20)[18] if len(memory_values) > 20 else max(memory_values)
            },
            'alerts_count': len(self.alerts),
            'recent_alerts': self.alerts[-5:],
            'recommendations': self._generate_recommendations()
        }
        
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if not self.metrics_history:
            return 100.0
            
        latest_metrics = list(self.metrics_history)[-1]  # Get most recent
        
        # Component scores
        cpu_score = max(0, 100 - latest_metrics['cpu']['percent'])
        memory_score = max(0, 100 - latest_metrics['memory']['percent'])
        disk_score = max(0, 100 - latest_metrics['disk']['percent'])
        swap_score = max(0, 100 - latest_metrics['memory']['swap_percent'])
        
        # Weighted average (CPU and Memory are most important)
        performance_score = (cpu_score * 0.35 + memory_score * 0.35 + 
                           disk_score * 0.2 + swap_score * 0.1)
        
        return round(performance_score, 1)
        
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        if not self.metrics_history:
            return ["Start monitoring to receive personalized recommendations"]
            
        latest_metrics = list(self.metrics_history)[-1]
        
        if latest_metrics['cpu']['percent'] > 70:
            recommendations.append("Consider optimizing CPU-intensive processes or upgrading CPU")
            
        if latest_metrics['memory']['percent'] > 80:
            recommendations.append("High memory usage detected - consider memory optimization or adding RAM")
            
        if latest_metrics['disk']['percent'] > 80:
            recommendations.append("Disk space running low - cleanup unnecessary files or expand storage")
            
        if latest_metrics['memory']['swap_percent'] > 30:
            recommendations.append("High swap usage indicates memory pressure - investigate memory leaks")
            
        # Check for alert patterns
        cpu_alerts = len([a for a in self.alerts if a['type'] == 'cpu_high'])
        if cpu_alerts > 3:
            recommendations.append("Frequent high CPU alerts - consider process optimization or scaling")
            
        memory_alerts = len([a for a in self.alerts if a['type'] == 'memory_high'])
        if memory_alerts > 3:
            recommendations.append("Frequent high memory alerts - investigate memory usage patterns")
            
        if not recommendations:
            recommendations.append("System performance looks good! Continue monitoring for trends.")
            
        return recommendations
        
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics data to JSON file"""
        if filename is None:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'metrics_history': list(self.metrics_history),
            'alerts': self.alerts,
            'report': self.get_performance_report()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        return filename
        
    def set_baseline(self, duration_minutes: int = 10):
        """Establish performance baseline"""
        print(f"📊 Establishing baseline over {duration_minutes} minutes...")
        
        # Collect baseline data
        baseline_start = time.time()
        baseline_data = []
        
        while time.time() - baseline_start < duration_minutes * 60:
            metrics = self._collect_metrics()
            baseline_data.append(metrics)
            time.sleep(self.monitoring_interval)
            
        # Calculate baseline averages
        self.baseline_metrics = {
            'cpu_baseline': statistics.mean([m['cpu']['percent'] for m in baseline_data]),
            'memory_baseline': statistics.mean([m['memory']['percent'] for m in baseline_data]),
            'disk_baseline': statistics.mean([m['disk']['percent'] for m in baseline_data])
        }
        
        print("✅ Baseline established successfully")
        return self.baseline_metrics

def main():
    """Demo usage of Advanced Performance Profiler"""
    profiler = AdvancedProfiler(monitoring_interval=2.0)
    
    print("🚀 Starting Advanced Performance Profiler Demo")
    print("=" * 50)
    
    # Start monitoring
    profiler.start_monitoring()
    
    try:
        # Monitor for 30 seconds
        time.sleep(30)
        
        # Generate report
        print("\n📊 Generating Performance Report...")
        report = profiler.get_performance_report()
        
        print(f"Performance Score: {report['performance_score']}/100")
        print(f"CPU Usage: {report['cpu']['current']:.1f}% (avg: {report['cpu']['average']:.1f}%)")
        print(f"Memory Usage: {report['memory']['current']:.1f}% (avg: {report['memory']['average']:.1f}%)")
        print(f"Alerts Generated: {report['alerts_count']}")
        
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"• {rec}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    finally:
        profiler.stop_monitoring()

if __name__ == "__main__":
    main()