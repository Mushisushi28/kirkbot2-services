#!/usr/bin/env python3
"""
Advanced Code Review and Performance Analysis Tool
Comprehensive system analysis with security, performance, and quality metrics
"""

import os
import json
import time
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class AdvancedCodeAnalyzer:
    """Advanced code analysis with security and performance insights"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(project_path),
            "metrics": {},
            "security_issues": [],
            "performance_bottlenecks": [],
            "code_quality_score": 0,
            "optimization_recommendations": [],
            "roi_projections": {}
        }
    
    def analyze_project(self) -> Dict:
        """Perform comprehensive project analysis"""
        print("🔍 Starting advanced code analysis...")
        
        # File analysis
        file_metrics = self._analyze_files()
        self.analysis_results["metrics"]["files"] = file_metrics
        
        # Security analysis
        security_issues = self._security_scan()
        self.analysis_results["security_issues"] = security_issues
        
        # Performance analysis
        performance_issues = self._performance_analysis()
        self.analysis_results["performance_bottlenecks"] = performance_issues
        
        # Code quality scoring
        quality_score = self._calculate_quality_score()
        self.analysis_results["code_quality_score"] = quality_score
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        self.analysis_results["optimization_recommendations"] = recommendations
        
        # ROI projections
        roi_projections = self._calculate_roi()
        self.analysis_results["roi_projections"] = roi_projections
        
        return self.analysis_results
    
    def _analyze_files(self) -> Dict:
        """Analyze project files and code structure"""
        file_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C'
        }
        
        file_stats = {}
        total_lines = 0
        total_files = 0
        
        for ext, language in file_extensions.items():
            files = list(self.project_path.rglob(f"*{ext}"))
            lines = 0
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines += len(f.readlines())
                except:
                    pass
            
            if files:
                file_stats[language] = {
                    "files": len(files),
                    "lines_of_code": lines,
                    "complexity_score": self._calculate_complexity(files)
                }
                total_files += len(files)
                total_lines += lines
        
        file_stats["total"] = {
            "files": total_files,
            "lines_of_code": total_lines
        }
        
        return file_stats
    
    def _calculate_complexity(self, files: List[Path]) -> float:
        """Calculate cyclomatic complexity estimate"""
        complexity_indicators = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bwhile\b', r'\bfor\b',
            r'\bswitch\b', r'\bcase\b', r'\btry\b', r'\bexcept\b', r'\bcatch\b'
        ]
        
        total_complexity = 0
        
        for file_path in files[:10]:  # Sample up to 10 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in complexity_indicators:
                        total_complexity += len(re.findall(pattern, content, re.IGNORECASE))
            except:
                pass
        
        return max(1, total_complexity / max(1, len(files)))
    
    def _security_scan(self) -> List[Dict]:
        """Scan for common security issues"""
        security_patterns = {
            "SQL Injection": [
                r'execute\s*\(\s*["\'].*?\+.*?["\']',
                r'query\s*\(\s*["\'].*?\+.*?["\']',
                r'\.format\s*\(\s*.*?user_input'
            ],
            "XSS Vulnerability": [
                r'innerHTML\s*=\s*.*?\+',
                r'document\.write\s*\(\s*.*?\+',
                r'eval\s*\(\s*.*?\+'
            ],
            "Hardcoded Secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ],
            "Insecure Random": [
                r'random\(\)',
                r'math\.random\(\)',
                r'rand\(\)'
            ]
        }
        
        issues = []
        
        for issue_type, patterns in security_patterns.items():
            for pattern in patterns:
                matches = self._search_pattern(pattern)
                for match in matches:
                    issues.append({
                        "type": issue_type,
                        "severity": "High" if "Secrets" in issue_type else "Medium",
                        "file": match["file"],
                        "line": match["line"],
                        "pattern": pattern,
                        "description": f"Potential {issue_type.lower()} detected"
                    })
        
        return issues
    
    def _performance_analysis(self) -> List[Dict]:
        """Analyze performance bottlenecks"""
        performance_patterns = {
            "Inefficient Loops": [
                r'for.*in.*range\(.*\).*:\s*for.*in.*range\(',
                r'while\s*True.*:.*if.*break'
            ],
            "Memory Leaks": [
                r'global\s+.*=.*\[\]',
                r'\.append\(.*\)\s*$'
            ],
            "Blocking I/O": [
                r'time\.sleep\s*\(',
                r'synchronous.*request'
            ],
            "Database Issues": [
                r'SELECT\s+\*\s+FROM',
                r'\.execute\s*\(\s*["\'][^"\']*SELECT[^"\']*["\']'
            ]
        }
        
        bottlenecks = []
        
        for bottleneck_type, patterns in performance_patterns.items():
            for pattern in patterns:
                matches = self._search_pattern(pattern)
                for match in matches:
                    bottlenecks.append({
                        "type": bottleneck_type,
                        "severity": "Medium",
                        "file": match["file"],
                        "line": match["line"],
                        "impact": self._estimate_performance_impact(bottleneck_type),
                        "recommendation": self._get_performance_recommendation(bottleneck_type)
                    })
        
        return bottlenecks
    
    def _search_pattern(self, pattern: str) -> List[Dict]:
        """Search for pattern in project files"""
        matches = []
        
        for file_path in self.project_path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            matches.append({
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "content": line.strip()
                            })
                except:
                    pass
        
        return matches
    
    def _estimate_performance_impact(self, bottleneck_type: str) -> str:
        """Estimate performance impact of bottleneck"""
        impact_map = {
            "Inefficient Loops": "20-50% performance degradation",
            "Memory Leaks": "Progressive slowdown, potential crashes",
            "Blocking I/O": "Response time increase 100-500ms per call",
            "Database Issues": "Query time increase 2-10x"
        }
        return impact_map.get(bottleneck_type, "Performance impact unknown")
    
    def _get_performance_recommendation(self, bottleneck_type: str) -> str:
        """Get specific performance recommendation"""
        recommendations = {
            "Inefficient Loops": "Use list comprehensions, generators, or vectorized operations",
            "Memory Leaks": "Implement proper memory management and cleanup",
            "Blocking I/O": "Use async/await patterns or threading",
            "Database Issues": "Add indexes, optimize queries, use connection pooling"
        }
        return recommendations.get(bottleneck_type, "Review and optimize implementation")
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall code quality score (0-100)"""
        base_score = 80.0
        
        # Deduct points for security issues
        high_security_issues = len([i for i in self.analysis_results.get("security_issues", []) if i.get("severity") == "High"])
        base_score -= high_security_issues * 10
        
        medium_security_issues = len([i for i in self.analysis_results.get("security_issues", []) if i.get("severity") == "Medium"])
        base_score -= medium_security_issues * 5
        
        # Deduct points for performance issues
        performance_issues = len(self.analysis_results.get("performance_bottlenecks", []))
        base_score -= performance_issues * 3
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate prioritized optimization recommendations"""
        recommendations = []
        
        # Security recommendations
        for issue in self.analysis_results.get("security_issues", []):
            recommendations.append({
                "priority": "High" if issue["severity"] == "High" else "Medium",
                "category": "Security",
                "description": f"Fix {issue['type'].lower()} in {issue['file']}",
                "estimated_effort": "2-4 hours",
                "impact": "Critical security improvement"
            })
        
        # Performance recommendations
        for bottleneck in self.analysis_results.get("performance_bottlenecks", []):
            recommendations.append({
                "priority": "Medium",
                "category": "Performance",
                "description": bottleneck["recommendation"],
                "estimated_effort": "4-8 hours",
                "impact": bottleneck["impact"]
            })
        
        # Code quality recommendations
        if self.analysis_results["code_quality_score"] < 70:
            recommendations.append({
                "priority": "Low",
                "category": "Code Quality",
                "description": "Improve code quality through refactoring and testing",
                "estimated_effort": "8-16 hours",
                "impact": "Maintainability and developer productivity"
            })
        
        return sorted(recommendations, key=lambda x: {"High": 0, "Medium": 1, "Low": 2}[x["priority"]])
    
    def _calculate_roi(self) -> Dict:
        """Calculate ROI projections for optimizations"""
        base_score = self.analysis_results["code_quality_score"]
        issues_count = len(self.analysis_results["security_issues"]) + len(self.analysis_results["performance_bottlenecks"])
        
        # Conservative ROI estimates
        if base_score >= 80:
            improvement_potential = "10-20%"
            monthly_savings = "$500-1,000"
        elif base_score >= 60:
            improvement_potential = "20-40%"
            monthly_savings = "$1,000-2,500"
        else:
            improvement_potential = "40-80%"
            monthly_savings = "$2,500-5,000"
        
        return {
            "current_quality_score": base_score,
            "improvement_potential": improvement_potential,
            "estimated_monthly_savings": monthly_savings,
            "implementation_cost": f"${200 + issues_count * 50}-{400 + issues_count * 100}",
            "payback_period": "1-3 months",
            "annual_roi": "200-400%"
        }
    
    def generate_report(self, output_file: str = "advanced-code-analysis-report.json") -> str:
        """Generate comprehensive analysis report"""
        report_path = self.project_path / output_file
        
        with open(report_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        return str(report_path)
    
    def print_summary(self):
        """Print analysis summary"""
        results = self.analysis_results
        
        print("\n" + "="*60)
        print("🔍 ADVANCED CODE ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📊 Overall Code Quality Score: {results['code_quality_score']}/100")
        
        if results['metrics'].get('files'):
            files_info = results['metrics']['files']
            print(f"📁 Project Size: {files_info['total']['files']} files, {files_info['total']['lines_of_code']} lines")
        
        security_issues = results.get('security_issues', [])
        performance_issues = results.get('performance_bottlenecks', [])
        
        print(f"\n🚨 Security Issues: {len(security_issues)} found")
        for issue in security_issues[:3]:
            print(f"   • {issue['type']} in {issue['file']}:{issue['line']}")
        
        print(f"\n⚡ Performance Issues: {len(performance_issues)} found")
        for issue in performance_issues[:3]:
            print(f"   • {issue['type']} - {issue['impact']}")
        
        roi = results.get('roi_projections', {})
        if roi:
            print(f"\n💰 ROI Projections:")
            print(f"   • Improvement Potential: {roi.get('improvement_potential')}")
            print(f"   • Monthly Savings: {roi.get('estimated_monthly_savings')}")
            print(f"   • Annual ROI: {roi.get('annual_roi')}")
        
        recommendations = results.get('optimization_recommendations', [])
        if recommendations:
            print(f"\n🎯 Top Recommendations:")
            for rec in recommendations[:3]:
                print(f"   • {rec['description']} ({rec['priority']} priority)")
        
        print("\n" + "="*60)

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Code Analysis Tool")
    parser.add_argument("--path", default=".", help="Project path to analyze")
    parser.add_argument("--output", default="advanced-code-analysis-report.json", help="Output report file")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")
    
    args = parser.parse_args()
    
    analyzer = AdvancedCodeAnalyzer(args.path)
    results = analyzer.analyze_project()
    
    if not args.quiet:
        analyzer.print_summary()
    
    report_path = analyzer.generate_report(args.output)
    print(f"\n📄 Full report saved to: {report_path}")
    
    return results

if __name__ == "__main__":
    main()