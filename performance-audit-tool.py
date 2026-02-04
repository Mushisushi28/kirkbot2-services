#!/usr/bin/env python3
"""
KirkBot2 Performance Audit Tool
Automated system performance analysis and optimization recommendations
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse

class PerformanceAuditor:
    def __init__(self, target_path: str = "."):
        self.target_path = Path(target_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "target_path": str(target_path),
            "metrics": {},
            "recommendations": [],
            "score": 0
        }
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the codebase for performance issues"""
        print("🔍 Analyzing codebase...")
        
        metrics = {
            "file_count": 0,
            "total_lines": 0,
            "languages": {},
            "potential_issues": []
        }
        
        # File extensions to analyze
        code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        
        for file_path in self.target_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in code_extensions:
                    metrics["file_count"] += 1
                    language = code_extensions[ext]
                    metrics["languages"][language] = metrics["languages"].get(language, 0) + 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            metrics["total_lines"] += lines
                            
                            # Check for common performance anti-patterns
                            self._check_file_issues(file_path, language, metrics)
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        return metrics
    
    def _check_file_issues(self, file_path: Path, language: str, metrics: Dict):
        """Check individual files for performance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                issues = []
                
                if language == 'Python':
                    issues = self._check_python_issues(content, lines)
                elif language in ['JavaScript', 'TypeScript']:
                    issues = self._check_js_issues(content, lines)
                elif language == 'Go':
                    issues = self._check_go_issues(content, lines)
                
                for issue in issues:
                    metrics["potential_issues"].append({
                        "file": str(file_path.relative_to(self.target_path)),
                        "issue": issue,
                        "severity": self._assess_severity(issue)
                    })
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _check_python_issues(self, content: str, lines: List[str]) -> List[str]:
        """Check Python files for performance issues"""
        issues = []
        
        # Common Python performance anti-patterns
        if 'import *' in content:
            issues.append("Wildcard imports can slow down startup time")
        
        if content.count('for ') > 10 and 'list comprehension' not in content:
            issues.append("Multiple for loops found - consider list comprehensions")
        
        if 'time.sleep(' in content and 'async' not in content:
            issues.append("Blocking sleep detected - consider async/await")
        
        if 'eval(' in content or 'exec(' in content:
            issues.append("Dynamic code execution - security and performance risk")
        
        # Check for inefficient database queries
        if 'SELECT *' in content:
            issues.append("SELECT * queries - specify only needed columns")
        
        return issues
    
    def _check_js_issues(self, content: str, lines: List[str]) -> List[str]:
        """Check JavaScript/TypeScript files for performance issues"""
        issues = []
        
        if 'var ' in content:
            issues.append("Use 'let' or 'const' instead of 'var'")
        
        if content.count('console.log') > 5:
            issues.append("Multiple console.log statements - remove in production")
        
        if 'document.getElementById(' in content:
            issues.append("Repeated DOM queries - cache element references")
        
        if 'setTimeout(' in content and 'clearTimeout' not in content:
            issues.append("setTimeout without clearTimeout - potential memory leak")
        
        return issues
    
    def _check_go_issues(self, content: str, lines: List[str]) -> List[str]:
        """Check Go files for performance issues"""
        issues = []
        
        if 'fmt.Sprintf(' in content and 'strings.Builder' not in content:
            issues.append("String concatenation - consider strings.Builder")
        
        if 'goroutine' in content and 'sync.WaitGroup' not in content:
            issues.append("Goroutines without WaitGroup - potential race conditions")
        
        return issues
    
    def _assess_severity(self, issue: str) -> str:
        """Assess the severity of a performance issue"""
        high_severity = ['security', 'memory leak', 'crash', 'race condition']
        medium_severity = ['slow', 'performance', 'inefficient']
        
        issue_lower = issue.lower()
        if any(keyword in issue_lower for keyword in high_severity):
            return 'high'
        elif any(keyword in issue_lower for keyword in medium_severity):
            return 'medium'
        else:
            return 'low'
    
    def generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        # File structure recommendations
        if metrics["file_count"] > 100:
            recommendations.append("Consider modularizing large codebase into smaller packages")
        
        if metrics["total_lines"] > 50000:
            recommendations.append("Large codebase detected - consider code splitting and lazy loading")
        
        # Language-specific recommendations
        if 'Python' in metrics["languages"] and metrics["languages"]["Python"] > 20:
            recommendations.append("Large Python codebase - consider using PyPy for performance-critical parts")
        
        if 'JavaScript' in metrics["languages"]:
            recommendations.append("JavaScript detected - implement code splitting and tree shaking")
        
        # Issue-based recommendations
        high_issues = [i for i in metrics["potential_issues"] if i["severity"] == "high"]
        if high_issues:
            recommendations.append(f"Address {len(high_issues)} high-severity issues immediately")
        
        medium_issues = [i for i in metrics["potential_issues"] if i["severity"] == "medium"]
        if medium_issues:
            recommendations.append(f"Plan to address {len(medium_issues)} medium-severity issues")
        
        # General recommendations
        recommendations.extend([
            "Implement automated performance testing",
            "Set up monitoring and alerting for production systems",
            "Consider caching strategies for frequently accessed data",
            "Review and optimize database queries"
        ])
        
        return recommendations
    
    def calculate_score(self, metrics: Dict) -> int:
        """Calculate overall performance score (0-100)"""
        base_score = 100
        
        # Deduct points for issues
        for issue in metrics["potential_issues"]:
            if issue["severity"] == "high":
                base_score -= 10
            elif issue["severity"] == "medium":
                base_score -= 5
            else:
                base_score -= 2
        
        # Bonus points for good practices
        if metrics["file_count"] > 0:
            avg_lines_per_file = metrics["total_lines"] / metrics["file_count"]
            if avg_lines_per_file < 200:  # Good modularity
                base_score += 5
        
        return max(0, min(100, base_score))
    
    def run_audit(self) -> Dict[str, Any]:
        """Run complete performance audit"""
        print("🚀 Starting KirkBot2 Performance Audit")
        print(f"📁 Target: {self.target_path}")
        print("=" * 50)
        
        # Analyze codebase
        self.results["metrics"] = self.analyze_codebase()
        
        # Generate recommendations
        self.results["recommendations"] = self.generate_recommendations(self.results["metrics"])
        
        # Calculate score
        self.results["score"] = self.calculate_score(self.results["metrics"])
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _save_results(self):
        """Save audit results to file"""
        results_file = self.target_path / "performance-audit-results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Results saved to: {results_file}")
    
    def _print_summary(self):
        """Print audit summary"""
        metrics = self.results["metrics"]
        recommendations = self.results["recommendations"]
        
        print("\n📊 AUDIT RESULTS")
        print("=" * 30)
        print(f"📁 Files analyzed: {metrics['file_count']}")
        print(f"📝 Total lines: {metrics['total_lines']:,}")
        print(f"🐍 Languages: {', '.join(metrics['languages'].keys())}")
        print(f"⚠️  Issues found: {len(metrics['potential_issues'])}")
        print(f"🏆 Performance Score: {self.results['score']}/100")
        
        if metrics['potential_issues']:
            print("\n⚠️  TOP ISSUES:")
            high_issues = [i for i in metrics['potential_issues'] if i['severity'] == 'high'][:3]
            for issue in high_issues:
                print(f"  🔴 {issue['file']}: {issue['issue']}")
        
        print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n🎯 ACTION REQUIRED: {'IMMEDIATE' if self.results['score'] < 70 else 'PLANNED'}")
        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description="KirkBot2 Performance Audit Tool")
    parser.add_argument("path", nargs="?", default=".", help="Path to analyze (default: current directory)")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    auditor = PerformanceAuditor(args.path)
    results = auditor.run_audit()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    
    return 0 if results['score'] > 50 else 1

if __name__ == "__main__":
    sys.exit(main())