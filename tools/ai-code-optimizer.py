#!/usr/bin/env python3
"""
KirkBot2 AI-Powered Code Optimization Tool
Advanced code analysis with machine learning integration
"""

import os
import sys
import json
import time
import re
import ast
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import argparse
import threading

@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    suggestion: str
    confidence: float

class AICodeOptimizer:
    """AI-powered code analysis and optimization tool"""
    
    def __init__(self, target_path: str = "."):
        self.target_path = Path(target_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "target_path": str(target_path),
            "analysis_type": "ai_optimization",
            "issues_found": [],
            "optimizations": [],
            "metrics": {},
            "score": 0
        }
        
        # AI-based patterns for optimization
        self.performance_patterns = {
            "inefficient_loops": [
                r"for\s+\w+\s+in\s+range\(len\(",  # range(len()) pattern
                r"for\s+\w+\s+in\s+\w+\.keys\(\)",  # iterating over keys
            ],
            "memory_issues": [
                r"\.append\(\)\s*\n.*\.append\(\)",  # repeated appends
                r"list\(\w+\.\*.*\)",  # unnecessary list conversion
            ],
            "string_operations": [
                r"\+\s*['\"]\w+['\"]\s*\+",  # string concatenation in loops
                r"format\(\s*\)",  # potential f-string replacement
            ]
        }
        
        # Optimization rules with impact scores
        self.optimization_rules = {
            "list_comprehension": {
                "pattern": r"for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\.append\(",
                "replacement": "list_comprehension",
                "impact": 8,
                "description": "Replace loop+append with list comprehension"
            },
            "f_strings": {
                "pattern": r"format\(",
                "replacement": "f_string",
                "impact": 3,
                "description": "Use f-strings for better performance"
            },
            "enumerate": {
                "pattern": r"for\s+\w+\s+in\s+range\(len\(",
                "replacement": "enumerate",
                "impact": 5,
                "description": "Use enumerate instead of range(len())"
            }
        }

    def analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Analyze a single Python file for optimization opportunities"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path, lines, issues)
            except SyntaxError as e:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    issue_type="syntax_error",
                    severity="error",
                    description=f"Syntax error: {e.msg}",
                    suggestion="Fix syntax before optimization",
                    confidence=1.0
                ))
                return issues
            
            # Pattern-based analysis
            for line_num, line in enumerate(lines, 1):
                self._check_patterns(line, line_num, file_path, issues)
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return issues

    def _analyze_ast(self, tree: ast.AST, file_path: Path, lines: List[str], issues: List[CodeIssue]):
        """Analyze AST for structural optimization opportunities"""
        
        for node in ast.walk(tree):
            # Check for inefficient function definitions
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_path, lines, issues)
            
            # Check for inefficient imports
            elif isinstance(node, ast.ImportFrom):
                self._analyze_import(node, file_path, lines, issues)
            
            # Check for loop optimizations
            elif isinstance(node, ast.For):
                self._analyze_for_loop(node, file_path, lines, issues)

    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, lines: List[str], issues: List[CodeIssue]):
        """Analyze function for optimization opportunities"""
        
        # Check function complexity
        complexity = self._calculate_complexity(node)
        if complexity > 10:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type="high_complexity",
                severity="warning",
                description=f"Function '{node.name}' has high complexity ({complexity})",
                suggestion="Consider breaking into smaller functions",
                confidence=0.8
            ))
        
        # Check for default mutable arguments
        for arg in node.args.defaults:
            if isinstance(arg, (ast.List, ast.Dict)):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="mutable_default",
                    severity="warning",
                    description=f"Function '{node.name}' uses mutable default argument",
                    suggestion="Use None and initialize inside function",
                    confidence=0.9
                ))

    def _analyze_import(self, node: ast.ImportFrom, file_path: Path, lines: List[str], issues: List[CodeIssue]):
        """Analyze import statements for optimization"""
        
        if node.module and node.module.startswith('.'):
            if node.level > 2:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="deep_import",
                    severity="info",
                    description=f"Deep relative import ({node.level} levels)",
                    suggestion="Consider restructuring or absolute imports",
                    confidence=0.6
                ))

    def _analyze_for_loop(self, node: ast.For, file_path: Path, lines: List[str], issues: List[CodeIssue]):
        """Analyze for loops for optimization opportunities"""
        
        # Check for range(len()) pattern
        if (isinstance(node.target, ast.Name) and
            isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range' and
            len(node.iter.args) == 1 and
            isinstance(node.iter.args[0], ast.Call) and
            isinstance(node.iter.args[0].func, ast.Name) and
            node.iter.args[0].func.id == 'len'):
            
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type="range_len_pattern",
                severity="info",
                description="Using range(len()) pattern",
                suggestion="Use enumerate() for cleaner code",
                confidence=0.9
            ))

    def _check_patterns(self, line: str, line_num: int, file_path: Path, issues: List[CodeIssue]):
        """Check line against known performance patterns"""
        
        for category, patterns in self.performance_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line):
                    severity = "warning" if "memory" in category else "info"
                    
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=category,
                        severity=severity,
                        description=f"Potential {category} detected",
                        suggestion=f"Review for optimization opportunities",
                        confidence=0.7
                    ))

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

    def generate_optimizations(self, issues: List[CodeIssue]) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations"""
        optimizations = []
        
        # Group issues by type for comprehensive recommendations
        issue_groups = {}
        for issue in issues:
            key = issue.issue_type
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(issue)
        
        for issue_type, issue_list in issue_groups.items():
            if issue_type in self.optimization_rules:
                rule = self.optimization_rules[issue_type]
                optimizations.append({
                    "type": issue_type,
                    "impact_score": rule["impact"],
                    "files_affected": list(set(issue.file_path for issue in issue_list)),
                    "count": len(issue_list),
                    "description": rule["description"],
                    "estimated_improvement": f"{rule['impact'] * 5}%",
                    "implementation": self._get_implementation_guide(issue_type)
                })
        
        return optimizations

    def _get_implementation_guide(self, issue_type: str) -> str:
        """Get implementation guide for optimization type"""
        
        guides = {
            "list_comprehension": """
# Replace this pattern:
result = []
for item in items:
    if condition(item):
        result.append(transform(item))

# With this:
result = [transform(item) for item in items if condition(item)]
            """,
            
            "f_strings": """
# Replace this pattern:
result = "Hello {} {}.".format(name, surname)

# With this:
result = f"Hello {name} {surname}."
            """,
            
            "enumerate": """
# Replace this pattern:
for i in range(len(items)):
    print(i, items[i])

# With this:
for i, item in enumerate(items):
    print(i, item)
            """
        }
        
        return guides.get(issue_type, "Consult Python optimization guidelines")

    def calculate_performance_score(self, issues: List[CodeIssue]) -> int:
        """Calculate overall performance score (0-100)"""
        
        if not issues:
            return 100
        
        # Weight issues by severity
        severity_weights = {
            "error": 20,
            "warning": 10,
            "info": 5
        }
        
        total_deduction = 0
        for issue in issues:
            weight = severity_weights.get(issue.severity, 5)
            total_deduction += weight * issue.confidence
        
        score = max(0, 100 - int(total_deduction))
        return score

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete code analysis and return results"""
        
        print(f"🔍 Analyzing code in: {self.target_path}")
        
        # Find all Python files
        python_files = list(self.target_path.rglob("*.py"))
        
        if not python_files:
            print("❌ No Python files found")
            return self.results
        
        print(f"📊 Found {len(python_files)} Python files")
        
        all_issues = []
        
        # Analyze each file
        for file_path in python_files:
            print(f"🔍 Analyzing: {file_path}")
            issues = self.analyze_file(file_path)
            all_issues.extend(issues)
        
        # Generate optimizations
        optimizations = self.generate_optimizations(all_issues)
        
        # Calculate metrics
        self.results.update({
            "files_analyzed": len(python_files),
            "issues_found": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "confidence": issue.confidence
                }
                for issue in all_issues
            ],
            "optimizations": optimizations,
            "metrics": {
                "total_issues": len(all_issues),
                "errors": len([i for i in all_issues if i.severity == "error"]),
                "warnings": len([i for i in all_issues if i.severity == "warning"]),
                "info": len([i for i in all_issues if i.severity == "info"]),
                "performance_score": self.calculate_performance_score(all_issues),
                "files_analyzed": len(python_files)
            }
        })
        
        return self.results

    def print_summary(self):
        """Print analysis summary"""
        metrics = self.results["metrics"]
        
        print(f"\n📊 **Code Analysis Summary**")
        print(f"📁 Files analyzed: {metrics['files_analyzed']}")
        print(f"🔍 Total issues: {metrics['total_issues']}")
        print(f"❌ Errors: {metrics['errors']}")
        print(f"⚠️  Warnings: {metrics['warnings']}")
        print(f"ℹ️  Info: {metrics['info']}")
        print(f"📈 Performance Score: {metrics['performance_score']}/100")
        
        if self.results["optimizations"]:
            print(f"\n🚀 **Top Optimizations**")
            for opt in sorted(self.results["optimizations"], 
                            key=lambda x: x["impact_score"], reverse=True)[:5]:
                print(f"• {opt['description']} (Impact: {opt['impact_score']})")
                print(f"  Files affected: {len(opt['files_affected'])}")

    def save_report(self, output_file: str = None):
        """Save analysis report to JSON file"""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"code_optimization_report_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Code Optimization Tool")
    parser.add_argument("path", nargs="?", default=".", 
                       help="Path to analyze (default: current directory)")
    parser.add_argument("--output", "-o", 
                       help="Output file for analysis report")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Minimal output")
    
    args = parser.parse_args()
    
    # Run analysis
    optimizer = AICodeOptimizer(args.path)
    results = optimizer.run_analysis()
    
    if not args.quiet:
        optimizer.print_summary()
    
    # Save report
    optimizer.save_report(args.output)
    
    # Return appropriate exit code
    score = results["metrics"]["performance_score"]
    sys.exit(0 if score >= 70 else 1)

if __name__ == "__main__":
    main()