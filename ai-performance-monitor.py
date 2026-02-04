#!/usr/bin/env python3
"""
AI-Powered Real-Time Performance Monitor
Advanced performance monitoring with ML-based anomaly detection
"""

import asyncio
import json
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from collections import deque

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_io_read: int
    disk_io_write: int
    network_bytes_sent: int
    network_bytes_recv: int
    response_time: Optional[float] = None
    error_rate: Optional[float] = None

class AIPerformanceMonitor:
    """AI-powered real-time performance monitoring with anomaly detection"""
    
    def __init__(self, config_path: str = "monitor_config.json"):
        self.config = self._load_config(config_path)
        self.metrics_history = deque(maxlen=1000)
        self.anomaly_threshold = 2.0  # Standard deviations
        self.alert_callbacks = []
        
    def _load_config(self, config_path: str) -> dict:
        """Load monitoring configuration"""
        default_config = {
            "monitoring_interval": 5,
            "endpoints": [
                {"url": "https://httpbin.org/status/200", "timeout": 5},
                {"url": "https://api.github.com/users/octocat", "timeout": 3}
            ],
            "thresholds": {
                "cpu_warning": 70,
                "cpu_critical": 90,
                "memory_warning": 75,
                "memory_critical": 90,
                "response_time_warning": 2000,
                "response_time_critical": 5000
            },
            "anomaly_detection": True,
            "ml_model_type": "isolation_forest"
        }
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config, using defaults: {e}")
            
        return default_config
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read = disk_io.read_bytes if disk_io else 0
        disk_write = disk_io.write_bytes if disk_io else 0
        
        # Network I/O
        net_io = psutil.net_io_counters()
        net_sent = net_io.bytes_sent if net_io else 0
        net_recv = net_io.bytes_recv if net_io else 0
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read=disk_read,
            disk_io_write=disk_write,
            network_bytes_sent=net_sent,
            network_bytes_recv=net_recv
        )
    
    def check_endpoint_health(self, endpoint: dict) -> tuple[float, bool]:
        """Check endpoint health and response time"""
        try:
            start_time = time.time()
            response = requests.get(
                endpoint["url"], 
                timeout=endpoint.get("timeout", 5)
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            is_healthy = response.status_code < 400
            return response_time, is_healthy
            
        except Exception as e:
            print(f"Endpoint check failed for {endpoint['url']}: {e}")
            return -1, False
    
    def detect_anomalies(self, current_metrics: PerformanceMetrics) -> List[str]:
        """AI-based anomaly detection using statistical analysis"""
        if len(self.metrics_history) < 10:
            return []
        
        anomalies = []
        
        # Extract recent metrics for analysis
        recent_cpu = [m.cpu_percent for m in list(self.metrics_history)[-50:]]
        recent_memory = [m.memory_percent for m in list(self.metrics_history)[-50:]]
        
        # Statistical anomaly detection
        if recent_cpu:
            cpu_mean = np.mean(recent_cpu)
            cpu_std = np.std(recent_cpu)
            
            if abs(current_metrics.cpu_percent - cpu_mean) > self.anomaly_threshold * cpu_std:
                anomalies.append(f"CPU anomaly: {current_metrics.cpu_percent:.1f}% (avg: {cpu_mean:.1f}%)")
        
        if recent_memory:
            memory_mean = np.mean(recent_memory)
            memory_std = np.std(recent_memory)
            
            if abs(current_metrics.memory_percent - memory_mean) > self.anomaly_threshold * memory_std:
                anomalies.append(f"Memory anomaly: {current_metrics.memory_percent:.1f}% (avg: {memory_mean:.1f}%)")
        
        return anomalies
    
    def check_thresholds(self, metrics: PerformanceMetrics) -> List[str]:
        """Check metrics against configured thresholds"""
        alerts = []
        thresholds = self.config["thresholds"]
        
        if metrics.cpu_percent >= thresholds["cpu_critical"]:
            alerts.append(f"🔥 CRITICAL: CPU at {metrics.cpu_percent:.1f}%")
        elif metrics.cpu_percent >= thresholds["cpu_warning"]:
            alerts.append(f"⚠️ WARNING: CPU at {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent >= thresholds["memory_critical"]:
            alerts.append(f"🔥 CRITICAL: Memory at {metrics.memory_percent:.1f}%")
        elif metrics.memory_percent >= thresholds["memory_warning"]:
            alerts.append(f"⚠️ WARNING: Memory at {metrics.memory_percent:.1f}%")
        
        # Check endpoint response times
        for endpoint in self.config.get("endpoints", []):
            response_time, is_healthy = self.check_endpoint_health(endpoint)
            
            if response_time > 0:
                if response_time >= thresholds["response_time_critical"]:
                    alerts.append(f"🔥 CRITICAL: {endpoint['url']} response time {response_time:.0f}ms")
                elif response_time >= thresholds["response_time_warning"]:
                    alerts.append(f"⚠️ WARNING: {endpoint['url']} response time {response_time:.0f}ms")
            
            if not is_healthy:
                alerts.append(f"🔥 CRITICAL: {endpoint['url']} is unhealthy")
        
        return alerts
    
    async def monitor_once(self) -> dict:
        """Perform a single monitoring cycle"""
        # Collect system metrics
        system_metrics = self.collect_system_metrics()
        
        # Check endpoint health
        endpoint_results = []
        for endpoint in self.config.get("endpoints", []):
            response_time, is_healthy = self.check_endpoint_health(endpoint)
            endpoint_results.append({
                "url": endpoint["url"],
                "response_time_ms": response_time,
                "healthy": is_healthy
            })
        
        # Detect anomalies
        anomalies = []
        if self.config.get("anomaly_detection", True):
            anomalies = self.detect_anomalies(system_metrics)
        
        # Check thresholds
        alerts = self.check_thresholds(system_metrics)
        
        # Store metrics
        self.metrics_history.append(system_metrics)
        
        # Create report
        report = {
            "timestamp": datetime.fromtimestamp(system_metrics.timestamp).isoformat(),
            "system_metrics": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_io_read_mb": system_metrics.disk_io_read / (1024*1024),
                "disk_io_write_mb": system_metrics.disk_io_write / (1024*1024),
                "network_sent_mb": system_metrics.network_bytes_sent / (1024*1024),
                "network_recv_mb": system_metrics.network_bytes_recv / (1024*1024)
            },
            "endpoint_health": endpoint_results,
            "anomalies": anomalies,
            "alerts": alerts,
            "status": "healthy" if not alerts else "warning" if "CRITICAL" not in str(alerts) else "critical"
        }
        
        return report
    
    def add_alert_callback(self, callback):
        """Add custom alert callback function"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self, duration_minutes: int = 60):
        """Start continuous monitoring"""
        print(f"🚀 Starting AI Performance Monitor for {duration_minutes} minutes")
        print(f"📊 Monitoring {len(self.config.get('endpoints', []))} endpoints")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        report_count = 0
        alert_count = 0
        
        while time.time() < end_time:
            try:
                report = await self.monitor_once()
                report_count += 1
                
                # Print status
                status_emoji = "✅" if report["status"] == "healthy" else "⚠️" if report["status"] == "warning" else "🔥"
                print(f"{status_emoji} {report['timestamp']} - CPU: {report['system_metrics']['cpu_percent']:.1f}%, Memory: {report['system_metrics']['memory_percent']:.1f}%")
                
                # Handle alerts
                if report["alerts"]:
                    alert_count += len(report["alerts"])
                    for alert in report["alerts"]:
                        print(f"🚨 {alert}")
                        
                    # Trigger alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            await callback(report)
                        except Exception as e:
                            print(f"Alert callback failed: {e}")
                
                # Handle anomalies
                if report["anomalies"]:
                    for anomaly in report["anomalies"]:
                        print(f"🤖 AI Anomaly Detected: {anomaly}")
                
                # Save report
                report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                # Wait for next cycle
                await asyncio.sleep(self.config.get("monitoring_interval", 5))
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(5)
        
        print(f"\n📈 Monitoring Summary:")
        print(f"   Reports generated: {report_count}")
        print(f"   Total alerts: {alert_count}")
        print(f"   Duration: {int((time.time() - start_time) / 60)} minutes")
    
    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance analysis report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}
        
        metrics = list(self.metrics_history)
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_percent for m in metrics]
        
        report = {
            "analysis_period": {
                "start": datetime.fromtimestamp(metrics[0].timestamp).isoformat(),
                "end": datetime.fromtimestamp(metrics[-1].timestamp).isoformat(),
                "duration_minutes": (metrics[-1].timestamp - metrics[0].timestamp) / 60
            },
            "system_performance": {
                "cpu": {
                    "avg": np.mean(cpu_values),
                    "max": np.max(cpu_values),
                    "min": np.min(cpu_values),
                    "std": np.std(cpu_values)
                },
                "memory": {
                    "avg": np.mean(memory_values),
                    "max": np.max(memory_values),
                    "min": np.min(memory_values),
                    "std": np.std(memory_values)
                }
            },
            "recommendations": self._generate_recommendations(cpu_values, memory_values)
        }
        
        return report
    
    def _generate_recommendations(self, cpu_values: List[float], memory_values: List[float]) -> List[str]:
        """Generate AI-powered optimization recommendations"""
        recommendations = []
        
        # CPU recommendations
        cpu_avg = np.mean(cpu_values)
        if cpu_avg > 70:
            recommendations.append("🔧 High CPU usage detected - consider scaling up or optimizing code")
        elif cpu_avg > 50:
            recommendations.append("💡 Moderate CPU usage - monitor during peak loads")
        
        # Memory recommendations
        memory_avg = np.mean(memory_values)
        if memory_avg > 75:
            recommendations.append("🔧 High memory usage - check for memory leaks or add more RAM")
        elif memory_avg > 60:
            recommendations.append("💡 Moderate memory usage - monitor growth trends")
        
        # Variability recommendations
        if np.std(cpu_values) > 20:
            recommendations.append("📊 High CPU variability - investigate workload patterns")
        
        if len(recommendations) == 0:
            recommendations.append("✅ System performance looks optimal!")
        
        return recommendations

async def main():
    """Main function to run the performance monitor"""
    monitor = AIPerformanceMonitor()
    
    # Example alert callback
    async def alert_callback(report):
        print(f"📧 Alert: System status is {report['status']}")
    
    monitor.add_alert_callback(alert_callback)
    
    # Start monitoring for 10 minutes (adjust as needed)
    await monitor.start_monitoring(duration_minutes=10)
    
    # Generate final report
    final_report = monitor.generate_performance_report()
    print("\n📊 Final Performance Report:")
    print(json.dumps(final_report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())