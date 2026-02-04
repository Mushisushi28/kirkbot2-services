#!/usr/bin/env python3
"""
Automated Code Quality Analysis with AI Insights
Advanced code analysis tool with ML-based quality assessment and optimization suggestions
"""

import ast
import json
import os
import subprocess
import sys
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import threading

@dataclass
class CodeIssue:
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    suggestion: str
    rule_violated: Optional[str] = None
    confidence: float = 1.0

@dataclass
class FileMetrics:
    file_path: str
    lines_of_code: int
    complexity_score: int
    maintainability_index: float
    test_coverage: float
    duplication_percentage: float
    security_issues: int
    performance_issues: int

class AICodeQualityAnalyzer:
    """AI-powered code quality analysis with ML insights"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.issues: List[CodeIssue] = []
        self.file_metrics: List[FileMetrics] = []
        
        # Quality thresholds
        self.thresholds = {
            "maintainability_index": {
                "excellent": 85,
                "good": 70,
                "fair": 50,
                "poor": 0
            },
            "complexity_score": {
                "simple": 5,
                "moderate": 10,
                "complex": 20,
                "very_complex": 100
            },
            "test_coverage": {
                "excellent": 80,
                "good": 60,
                "fair": 40,
                "poor": 0
            }
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive code quality analysis"""
        print(f"🔍 Starting AI Code Quality Analysis for {self.project_path}")
        
        start_time = time.time()
        
        # Find code files
        code_files = self._find_code_files()
        print(f"📁 Found {len(code_files)} code files to analyze")
        
        # Analyze each file
        for file_path in code_files:
            print(f"🔬 Analyzing: {file_path}")
            self._analyze_file(file_path)
        
        # Generate project metrics
        project_metrics = self._calculate_project_metrics()
        
        # Generate AI-powered recommendations
        recommendations = self._generate_ai_recommendations()
        
        analysis_time = time.time() - start_time
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "analysis_duration_seconds": round(analysis_time, 2),
            "files_analyzed": len(code_files),
            "total_issues": len(self.issues),
            "severity_breakdown": self._get_severity_breakdown(),
            "project_metrics": project_metrics,
            "file_metrics": [asdict(m) for m in self.file_metrics],
            "issues": [asdict(i) for i in self.issues],
            "ai_recommendations": recommendations,
            "quality_score": self._calculate_quality_score()
        }
        
        return report
    
    def _find_code_files(self) -> List[Path]:
        """Find all code files in the project"""
        extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.java', '.cpp', '.c', '.h']
        code_files = []
        
        for ext in extensions:
            code_files.extend(self.project_path.rglob(f'*{ext}'))
        
        # Exclude common directories
        exclude_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env', '.venv', 'build', 'dist'}
        code_files = [f for f in code_files if not any(exclude_dir in f.parts for exclude_dir in exclude_dirs)]
        
        return code_files
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single code file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return
            
            # Calculate basic metrics
            lines_of_code = len([line for line in content.splitlines() if line.strip()])
            complexity_score = self._calculate_complexity(content, file_path.suffix)
            
            # Run static analysis based on file type
            if file_path.suffix == '.py':
                self._analyze_python_file(file_path, content)
            elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                self._analyze_javascript_file(file_path, content)
            elif file_path.suffix == '.go':
                self._analyze_go_file(file_path, content)
            
            # Calculate maintainability index
            maintainability_index = self._calculate_maintainability_index(
                content, lines_of_code, complexity_score
            )
            
            # Estimate test coverage (simplified)
            test_coverage = self._estimate_test_coverage(file_path)
            
            # Check for code duplication
            duplication_percentage = self._estimate_duplication(content)
            
            # Create file metrics
            file_metrics = FileMetrics(
                file_path=str(file_path),
                lines_of_code=lines_of_code,
                complexity_score=complexity_score,
                maintainability_index=maintainability_index,
                test_coverage=test_coverage,
                duplication_percentage=duplication_percentage,
                security_issues=len([i for i in self.issues if i.file_path == str(file_path) and 'security' in i.issue_type.lower()]),
                performance_issues=len([i for i in self.issues if i.file_path == str(file_path) and 'performance' in i.issue_type.lower()])
            )
            
            self.file_metrics.append(file_metrics)
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
    
    def _analyze_python_file(self, file_path: Path, content: str):
        """Analyze Python file for issues"""
        try:
            tree = ast.parse(content)
            
            # Check for various issues
            self._check_python_security_issues(tree, file_path)
            self._check_python_performance_issues(tree, file_path)
            self._check_python_style_issues(content, file_path)
            self._check_python_complexity(tree, file_path)
            
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=e.lineno or 1,
                issue_type="syntax",
                severity="critical",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax errors before proceeding"
            ))
    
    def _check_python_security_issues(self, tree: ast.AST, file_path: Path):
        """Check for common Python security issues"""
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.file_path = file_path
            
            def visit_Import(self, node):
                # Check for dangerous imports
                dangerous_modules = ['pickle', 'cPickle', 'subprocess', 'os']
                for alias in node.names:
                    if alias.name in dangerous_modules:
                        self.analyzer.issues.append(CodeIssue(
                            file_path=str(self.file_path),
                            line_number=node.lineno,
                            issue_type="security",
                            severity="medium",
                            message=f"Potentially dangerous import: {alias.name}",
                            suggestion=f"Consider safer alternatives or sanitize inputs when using {alias.name}"
                        ))
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    dangerous_calls = ['eval', 'exec', 'compile']
                    if node.func.id in dangerous_calls:
                        self.analyzer.issues.append(CodeIssue(
                            file_path=str(self.file_path),
                            line_number=node.lineno,
                            issue_type="security",
                            severity="high",
                            message=f"Dangerous function call: {node.func.id}",
                            suggestion=f"Avoid using {node.func.id} with untrusted input"
                        ))
                self.generic_visit(node)
        
        visitor = SecurityVisitor(self)
        visitor.visit(tree)
    
    def _check_python_performance_issues(self, tree: ast.AST, file_path: Path):
        """Check for Python performance issues"""
        class PerformanceVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.file_path = file_path
            
            def visit_For(self, node):
                # Check for nested loops (potential performance issue)
                nested_loops = sum(1 for child in ast.walk(node) if isinstance(child, ast.For))
                if nested_loops > 2:
                    self.analyzer.issues.append(CodeIssue(
                        file_path=str(self.file_path),
                        line_number=node.lineno,
                        issue_type="performance",
                        severity="medium",
                        message="Multiple nested loops detected",
                        suggestion="Consider optimizing algorithms or using vectorization"
                    ))
                self.generic_visit(node)
            
            def visit_ListComp(self, node):
                # Check for complex list comprehensions
                if len(list(ast.walk(node))) > 10:
                    self.analyzer.issues.append(CodeIssue(
                        file_path=str(self.file_path),
                        line_number=node.lineno,
                        issue_type="performance",
                        severity="low",
                        message="Complex list comprehension detected",
                        suggestion="Consider breaking into simpler expressions or using generator"
                    ))
                self.generic_visit(node)
        
        visitor = PerformanceVisitor(self)
        visitor.visit(tree)
    
    def _check_python_style_issues(self, content: str, file_path: Path):
        """Check for Python style issues"""
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:  # Black formatter default
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="style",
                    severity="low",
                    message=f"Line too long ({len(line)} characters)",
                    suggestion="Break long lines or use string concatenation"
                ))
            
            # Check for trailing whitespace
            if line.endswith(' '):
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="style",
                    severity="low",
                    message="Trailing whitespace",
                    suggestion="Remove trailing whitespace"
                ))
            
            # Check for TODO/FIXME comments
            if 'TODO' in line or 'FIXME' in line:
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="maintenance",
                    severity="medium",
                    message="Unresolved TODO/FIXME found",
                    suggestion="Address the TODO or convert to proper issue tracking"
                ))
    
    def _check_python_complexity(self, tree: ast.AST, file_path: Path):
        """Check Python code complexity"""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
            
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_With(self, node):
                self.complexity += 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        if visitor.complexity > 15:
            self.issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type="complexity",
                severity="medium",
                message=f"High cyclomatic complexity: {visitor.complexity}",
                suggestion="Consider breaking function into smaller pieces"
            ))
    
    def _analyze_javascript_file(self, file_path: Path, content: str):
        """Analyze JavaScript/TypeScript file for issues"""
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for console.log statements
            if 'console.log' in line:
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="maintenance",
                    severity="low",
                    message="console.log statement found",
                    suggestion="Remove console.log or replace with proper logging"
                ))
            
            # Check for var usage (use let/const instead)
            if re.match(r'^\s*var\s+', line):
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="style",
                    severity="medium",
                    message="var keyword usage",
                    suggestion="Use let or const instead of var"
                ))
            
            # Check for == vs ===
            if '==' in line and '===' not in line and '!=' in line and '!==' not in line:
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="quality",
                    severity="medium",
                    message="Loose equality operator",
                    suggestion="Use === and !== for strict equality comparison"
                ))
    
    def _analyze_go_file(self, file_path: Path, content: str):
        """Analyze Go file for issues"""
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for error handling
            if ('err :=' in line or 'err, :=' in line) and i < len(lines) - 1:
                next_line = lines[i]
                if 'if err != nil' not in next_line:
                    self.issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="quality",
                        severity="high",
                        message="Potential unhandled error",
                        suggestion="Always handle errors in Go"
                    ))
            
            # Check for TODO comments
            if 'TODO' in line or 'FIXME' in line:
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="maintenance",
                    severity="medium",
                    message="Unresolved TODO/FIXME found",
                    suggestion="Address the TODO or create proper issue"
                ))
    
    def _calculate_complexity(self, content: str, file_extension: str) -> int:
        """Calculate cyclomatic complexity"""
        # Simple complexity calculation based on control structures
        complexity_indicators = {
            '.py': [r'\bif\b', r'\belif\b', r'\bwhile\b', r'\bfor\b', r'\bexcept\b', r'\bwith\b'],
            '.js': [r'\bif\b', r'\belse\b', r'\bwhile\b', r'\bfor\b', r'\bcatch\b', r'\bfinally\b'],
            '.ts': [r'\bif\b', r'\belse\b', r'\bwhile\b', r'\bfor\b', r'\bcatch\b', r'\bfinally\b'],
            '.go': [r'\bif\b', r'\belse\b', r'\bfor\b', r'\bselect\b', r'\bswitch\b'],
        }
        
        patterns = complexity_indicators.get(file_extension, [])
        complexity = 1  # Base complexity
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content, re.IGNORECASE))
        
        return complexity
    
    def _calculate_maintainability_index(self, content: str, loc: int, complexity: int) -> float:
        """Calculate maintainability index (simplified version)"""
        if loc == 0:
            return 100
        
        # Count volume operators and operands
        volume = loc * 0.5  # Simplified volume calculation
        
        # Maintainability index formula (simplified)
        maintainability = max(0, 171 - 5.2 * (complexity ** 0.23) - 0.23 * complexity - 16.2 * (volume ** 0.5))
        
        return round(maintainability, 1)
    
    def _estimate_test_coverage(self, file_path: Path) -> float:
        """Estimate test coverage based on test file existence"""
        base_name = file_path.stem
        
        # Look for test files
        test_patterns = [
            f"test_{base_name}.py",
            f"{base_name}_test.py",
            f"{base_name}.test.js",
            f"{base_name}.spec.js",
            f"{base_name}_test.go"
        ]
        
        test_dir = file_path.parent / "test"
        tests_dir = file_path.parent / "tests"
        
        for pattern in test_patterns:
            if (file_path.parent / pattern).exists():
                return 75.0  # Assume decent coverage if test file exists
            if (test_dir / pattern).exists():
                return 75.0
            if (tests_dir / pattern).exists():
                return 75.0
        
        return 25.0  # Low estimated coverage
    
    def _estimate_duplication(self, content: str) -> float:
        """Estimate code duplication percentage"""
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        unique_lines = set(lines)
        
        if len(lines) == 0:
            return 0.0
        
        return ((len(lines) - len(unique_lines)) / len(lines)) * 100
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown of issues by severity"""
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for issue in self.issues:
            breakdown[issue.severity] += 1
        
        return breakdown
    
    def _calculate_project_metrics(self) -> Dict[str, Any]:
        """Calculate overall project metrics"""
        if not self.file_metrics:
            return {}
        
        total_loc = sum(m.lines_of_code for m in self.file_metrics)
        avg_complexity = sum(m.complexity_score for m in self.file_metrics) / len(self.file_metrics)
        avg_maintainability = sum(m.maintainability_index for m in self.file_metrics) / len(self.file_metrics)
        avg_test_coverage = sum(m.test_coverage for m in self.file_metrics) / len(self.file_metrics)
        total_security_issues = sum(m.security_issues for m in self.file_metrics)
        total_performance_issues = sum(m.performance_issues for m in self.file_metrics)
        
        return {
            "total_lines_of_code": total_loc,
            "average_complexity": round(avg_complexity, 1),
            "average_maintainability_index": round(avg_maintainability, 1),
            "average_test_coverage": round(avg_test_coverage, 1),
            "total_security_issues": total_security_issues,
            "total_performance_issues": total_performance_issues,
            "code_quality_grade": self._calculate_quality_grade(avg_maintainability, avg_test_coverage, total_security_issues)
        }
    
    def _calculate_quality_grade(self, maintainability: float, coverage: float, security_issues: int) -> str:
        """Calculate overall code quality grade"""
        if maintainability >= 85 and coverage >= 80 and security_issues == 0:
            return "A"
        elif maintainability >= 70 and coverage >= 60 and security_issues <= 2:
            return "B"
        elif maintainability >= 50 and coverage >= 40 and security_issues <= 5:
            return "C"
        else:
            return "D"
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-100)"""
        if not self.file_metrics:
            return 0.0
        
        # Weight factors
        weights = {
            "maintainability": 0.3,
            "complexity": 0.2,
            "test_coverage": 0.2,
            "security": 0.15,
            "performance": 0.15
        }
        
        # Calculate scores
        avg_maintainability = sum(m.maintainability_index for m in self.file_metrics) / len(self.file_metrics)
        avg_complexity = sum(m.complexity_score for m in self.file_metrics) / len(self.file_metrics)
        avg_test_coverage = sum(m.test_coverage for m in self.file_metrics) / len(self.file_metrics)
        total_security_issues = sum(m.security_issues for m in self.file_metrics)
        total_performance_issues = sum(m.performance_issues for m in self.file_metrics)
        
        # Normalize scores
        maintainability_score = min(avg_maintainability, 100)
        complexity_score = max(0, 100 - avg_complexity * 3)  # Lower complexity is better
        test_coverage_score = avg_test_coverage
        security_score = max(0, 100 - total_security_issues * 10)
        performance_score = max(0, 100 - total_performance_issues * 5)
        
        # Calculate weighted average
        quality_score = (
            maintainability_score * weights["maintainability"] +
            complexity_score * weights["complexity"] +
            test_coverage_score * weights["test_coverage"] +
            security_score * weights["security"] +
            performance_score * weights["performance"]
        )
        
        return round(quality_score, 1)
    
    def _generate_ai_recommendations(self) -> List[Dict[str, Any]]:
        """Generate AI-powered improvement recommendations"""
        recommendations = []
        
        if not self.file_metrics:
            return recommendations
        
        # Analyze patterns and generate recommendations
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        high_issues = [i for i in self.issues if i.severity == "high"]
        
        if critical_issues:
            recommendations.append({
                "priority": "critical",
                "category": "security",
                "recommendation": f"Address {len(critical_issues)} critical issues immediately",
                "impact": "High",
                "estimated_effort": "High",
                "ai_confidence": 0.95
            })
        
        if high_issues:
            recommendations.append({
                "priority": "high",
                "category": "quality",
                "recommendation": f"Resolve {len(high_issues)} high-priority issues",
                "impact": "Medium-High",
                "estimated_effort": "Medium",
                "ai_confidence": 0.85
            })
        
        # Test coverage recommendations
        avg_coverage = sum(m.test_coverage for m in self.file_metrics) / len(self.file_metrics)
        if avg_coverage < 60:
            recommendations.append({
                "priority": "medium",
                "category": "testing",
                "recommendation": f"Improve test coverage from {avg_coverage:.1f}% to 80%+",
                "impact": "High",
                "estimated_effort": "Medium",
                "ai_confidence": 0.90
            })
        
        # Maintainability recommendations
        avg_maintainability = sum(m.maintainability_index for m in self.file_metrics) / len(self.file_metrics)
        if avg_maintainability < 70:
            recommendations.append({
                "priority": "medium",
                "category": "architecture",
                "recommendation": f"Refactor code to improve maintainability index from {avg_maintainability:.1f} to 80+",
                "impact": "Medium",
                "estimated_effort": "High",
                "ai_confidence": 0.80
            })
        
        return recommendations

def main():
    """Main function to run code quality analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Code Quality Analyzer")
    parser.add_argument("path", nargs="?", default=".", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    analyzer = AICodeQualityAnalyzer(args.path)
    report = analyzer.analyze_project()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to {args.output}")
    
    if args.verbose:
        print("\n📊 Analysis Report:")
        print(json.dumps(report, indent=2))
    else:
        print(f"\n📈 Quality Score: {report['quality_score']}/100")
        print(f"🔍 Total Issues: {report['total_issues']}")
        print(f"📁 Files Analyzed: {report['files_analyzed']}")
        print(f"⏱️ Analysis Time: {report['analysis_duration_seconds']}s")

if __name__ == "__main__":
    main()