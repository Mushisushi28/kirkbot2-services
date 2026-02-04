#!/usr/bin/env python3
"""
Enhanced Performance Audit Tool for KirkBot2 AI Services
Real-time system analysis with ROI projections and client-ready reports
"""

import json
import time
import psutil
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class PerformanceAuditor:
    def __init__(self):
        self.start_time = time.time()
        self.report_data = {
            "audit_timestamp": datetime.now().isoformat(),
            "system_info": {},
            "performance_metrics": {},
            "recommendations": [],
            "roi_projections": {},
            "risk_assessment": {}
        }
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information"""
        try:
            cpu_info = {
                "model": self._get_cpu_model(),
                "cores": psutil.cpu_count(logical=True),
                "physical_cores": psutil.cpu_count(logical=False),
                "architecture": os.uname().machine if hasattr(os, 'uname') else "unknown"
            }
            
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent
            }
            
            disk = psutil.disk_usage('/')
            disk_info = {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2)
            }
            
            return {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "load_average": list(os.getloadavg()) if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_cpu_model(self) -> str:
        """Extract CPU model information"""
        try:
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':')[1].strip()
            return "Unknown CPU"
        except:
            return "Unknown CPU"
    
    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze current system performance"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_load = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            cpu_cores = psutil.cpu_count(logical=True)
            cpu_per_core = cpu_load / cpu_cores
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # I/O metrics
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            # Process analysis
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 1.0 or pinfo['memory_percent'] > 1.0:
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                "cpu": {
                    "current_usage": round(cpu_percent, 2),
                    "load_average": round(cpu_load, 2),
                    "per_core_load": round(cpu_per_core, 2),
                    "status": "critical" if cpu_per_core > 0.8 else "warning" if cpu_per_core > 0.6 else "optimal"
                },
                "memory": {
                    "usage_percent": round(memory.percent, 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "swap_usage": round(swap.percent, 2),
                    "status": "critical" if memory.percent > 90 else "warning" if memory.percent > 75 else "optimal"
                },
                "disk_io": {
                    "read_mb_s": round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                    "write_mb_s": round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,
                    "status": "optimal"  # Could be enhanced with thresholds
                },
                "network_io": {
                    "sent_mb_s": round(net_io.bytes_sent / (1024**2), 2) if net_io else 0,
                    "recv_mb_s": round(net_io.bytes_recv / (1024**2), 2) if net_io else 0
                },
                "top_processes": processes[:10],
                "overall_score": self._calculate_performance_score(cpu_percent, memory.percent, cpu_per_core)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_performance_score(self, cpu_percent: float, memory_percent: float, cpu_per_core: float) -> int:
        """Calculate overall performance score (0-100)"""
        base_score = 100
        
        # CPU impact (40% weight)
        if cpu_percent > 80:
            cpu_score = 40 - (cpu_percent - 80) * 2
        elif cpu_percent > 60:
            cpu_score = 40 - (cpu_percent - 60) * 1
        else:
            cpu_score = 40
        
        # Memory impact (30% weight)
        if memory_percent > 90:
            mem_score = 30 - (memory_percent - 90) * 3
        elif memory_percent > 75:
            mem_score = 30 - (memory_percent - 75) * 2
        else:
            mem_score = 30
        
        # Load average impact (30% weight)
        if cpu_per_core > 2.0:
            load_score = 30 - (cpu_per_core - 2.0) * 10
        elif cpu_per_core > 1.0:
            load_score = 30 - (cpu_per_core - 1.0) * 5
        else:
            load_score = 30
        
        total_score = max(0, min(100, cpu_score + mem_score + load_score))
        return round(total_score)
    
    def generate_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable optimization recommendations"""
        recommendations = []
        
        cpu_status = metrics.get("cpu", {})
        mem_status = metrics.get("memory", {})
        
        # CPU recommendations
        if cpu_status.get("status") == "critical":
            recommendations.append({
                "category": "CPU Optimization",
                "priority": "high",
                "issue": "CPU overload detected",
                "recommendation": "Implement CPU-intensive task queuing and process optimization",
                "estimated_improvement": "40-60%",
                "implementation_cost": "$200-400",
                "roi": "300-400%",
                "time_to_implement": "24-48 hours"
            })
        elif cpu_status.get("status") == "warning":
            recommendations.append({
                "category": "CPU Optimization", 
                "priority": "medium",
                "issue": "High CPU usage",
                "recommendation": "Optimize CPU-bound processes and implement better load balancing",
                "estimated_improvement": "20-30%",
                "implementation_cost": "$100-200",
                "roi": "200-250%",
                "time_to_implement": "12-24 hours"
            })
        
        # Memory recommendations
        if mem_status.get("status") == "critical":
            recommendations.append({
                "category": "Memory Optimization",
                "priority": "high", 
                "issue": "Memory exhaustion risk",
                "recommendation": "Implement memory caching strategies and process memory optimization",
                "estimated_improvement": "50-70%",
                "implementation_cost": "$150-300",
                "roi": "350-500%",
                "time_to_implement": "24-48 hours"
            })
        elif mem_status.get("status") == "warning":
            recommendations.append({
                "category": "Memory Optimization",
                "priority": "medium",
                "issue": "High memory usage",
                "recommendation": "Optimize memory allocation and implement garbage collection tuning",
                "estimated_improvement": "25-35%",
                "implementation_cost": "$75-150",
                "roi": "250-300%",
                "time_to_implement": "12-24 hours"
            })
        
        # Process optimization
        top_processes = metrics.get("top_processes", [])
        if top_processes and len(top_processes) > 0:
            top_cpu_process = top_processes[0]
            if top_cpu_process.get("cpu_percent", 0) > 20:
                recommendations.append({
                    "category": "Process Optimization",
                    "priority": "high",
                    "issue": f"Process {top_cpu_process.get('name', 'unknown')} consuming {top_cpu_process.get('cpu_percent', 0):.1f}% CPU",
                    "recommendation": "Analyze and optimize high-resource consuming processes",
                    "estimated_improvement": "15-25%",
                    "implementation_cost": "$100-200",
                    "roi": "200-300%",
                    "time_to_implement": "8-16 hours"
                })
        
        return recommendations
    
    def calculate_roi_projections(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ROI projections for optimizations"""
        if not recommendations:
            return {"total_cost": 0, "potential_roi": 0, "payback_period": "N/A"}
        
        total_cost = 0
        weighted_roi = 0
        total_weight = 0
        
        for rec in recommendations:
            cost_str = rec.get("implementation_cost", "$0").replace("$", "").replace(",", "")
            cost_range = cost_str.split("-")
            avg_cost = sum(float(c) for c in cost_range) / len(cost_range) if cost_range else 0
            
            roi_str = rec.get("roi", "0%").replace("%", "").replace("-", "").replace("+", "")
            roi_range = roi_str.split("-")
            avg_roi = sum(float(r) for r in roi_range) / len(roi_range) if roi_range else 0
            
            # Weight by priority
            priority_weight = {"high": 3, "medium": 2, "low": 1}.get(rec.get("priority", "low"), 1)
            
            total_cost += avg_cost
            weighted_roi += avg_roi * priority_weight
            total_weight += priority_weight
        
        avg_roi = weighted_roi / total_weight if total_weight > 0 else 0
        total_return = total_cost * (avg_roi / 100)
        payback_months = (total_cost / (total_return / 12)) if total_return > 0 else 999
        
        return {
            "total_implementation_cost": round(total_cost, 2),
            "average_roi_percent": round(avg_roi, 1),
            "expected_annual_return": round(total_return, 2),
            "payback_period_months": round(payback_months, 1),
            "risk_level": "low" if payback_months < 6 else "medium" if payback_months < 12 else "high"
        }
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete performance audit"""
        print("🚀 Starting KirkBot2 AI Performance Audit...")
        
        # Collect system information
        print("📊 Collecting system information...")
        self.report_data["system_info"] = self.collect_system_info()
        
        # Analyze performance metrics
        print("⚡ Analyzing performance metrics...")
        self.report_data["performance_metrics"] = self.analyze_performance_metrics()
        
        # Generate recommendations
        print("💡 Generating optimization recommendations...")
        self.report_data["recommendations"] = self.generate_recommendations(self.report_data["performance_metrics"])
        
        # Calculate ROI projections
        print("💰 Calculating ROI projections...")
        self.report_data["roi_projections"] = self.calculate_roi_projections(self.report_data["recommendations"])
        
        # Generate risk assessment
        print("⚠️ Assessing implementation risks...")
        self.report_data["risk_assessment"] = self._assess_risks()
        
        # Generate summary
        audit_duration = time.time() - self.start_time
        self.report_data["audit_summary"] = {
            "duration_seconds": round(audit_duration, 2),
            "performance_score": self.report_data["performance_metrics"].get("overall_score", 0),
            "recommendations_count": len(self.report_data["recommendations"]),
            "high_priority_issues": len([r for r in self.report_data["recommendations"] if r.get("priority") == "high"]),
            "status": "critical" if self.report_data["performance_metrics"].get("overall_score", 0) < 50 else "warning" if self.report_data["performance_metrics"].get("overall_score", 0) < 75 else "optimal"
        }
        
        print(f"✅ Audit completed in {audit_duration:.2f} seconds")
        return self.report_data
    
    def _assess_risks(self) -> Dict[str, Any]:
        """Assess implementation risks"""
        recommendations = self.report_data.get("recommendations", [])
        
        high_priority_count = len([r for r in recommendations if r.get("priority") == "high"])
        total_cost = sum(float(r.get("implementation_cost", "$0").replace("$", "").split("-")[0]) for r in recommendations)
        
        if high_priority_count >= 3:
            risk_level = "high"
        elif high_priority_count >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "overall_risk": risk_level,
            "high_priority_issues": high_priority_count,
            "total_investment_needed": total_cost,
            "implementation_complexity": "high" if total_cost > 500 else "medium" if total_cost > 200 else "low",
            "recommended_approach": "phased" if total_cost > 300 else "comprehensive"
        }
    
    def save_report(self, output_file: str = "performance-audit-report.json") -> str:
        """Save audit report to file"""
        with open(output_file, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        return output_file
    
    def print_summary(self):
        """Print executive summary"""
        summary = self.report_data.get("audit_summary", {})
        metrics = self.report_data.get("performance_metrics", {})
        roi = self.report_data.get("roi_projections", {})
        
        print("\n" + "="*60)
        print("🚀 KIRKBOT2 AI PERFORMANCE AUDIT REPORT")
        print("="*60)
        print(f"📅 Date: {self.report_data.get('audit_timestamp', 'Unknown')}")
        print(f"⚡ Performance Score: {metrics.get('overall_score', 0)}/100")
        print(f"📊 System Status: {summary.get('status', 'Unknown').upper()}")
        print(f"💰 Total Investment Needed: ${roi.get('total_implementation_cost', 0):,.2f}")
        print(f"📈 Expected ROI: {roi.get('average_roi_percent', 0)}%")
        print(f"⏱️ Payback Period: {roi.get('payback_period_months', 0)} months")
        print(f"🔥 High Priority Issues: {summary.get('high_priority_issues', 0)}")
        
        print("\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(self.report_data.get("recommendations", [])[:3], 1):
            print(f"{i}. {rec.get('category', 'Unknown')}: {rec.get('recommendation', 'No recommendation')}")
            print(f"   💰 Cost: {rec.get('implementation_cost', 'Unknown')} | 📈 ROI: {rec.get('roi', 'Unknown')}")
        
        print("\n" + "="*60)

def main():
    """Main execution function"""
    try:
        auditor = PerformanceAuditor()
        results = auditor.run_full_audit()
        auditor.print_summary()
        
        # Save detailed report
        output_file = auditor.save_report()
        print(f"\n📄 Detailed report saved to: {output_file}")
        
        # Generate client-friendly summary
        print(f"\n🎯 CLIENT PROPOSAL READY:")
        print(f"   Performance Score: {results.get('performance_metrics', {}).get('overall_score', 0)}/100")
        print(f"   Optimization Potential: {results.get('roi_projections', {}).get('average_roi_percent', 0)}% ROI")
        print(f"   Implementation: ${results.get('roi_projections', {}).get('total_implementation_cost', 0):,.2f}")
        
    except Exception as e:
        print(f"❌ Audit failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()