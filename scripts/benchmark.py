#!/usr/bin/env python3
"""
ReviewLab Performance Benchmarking Script

This script benchmarks various ReviewLab operations to measure performance
and identify optimization opportunities.
"""

import time
import statistics
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.bug_injection import BugInjectionEngine
from core.evaluation import EvaluationEngine
from core.git_operations import GitManager
from core.github_integration import GitHubManager, GitHubWorkflow
from core.bug_templates import BugTemplateManager
from core.report_generator import ReportGenerator


class BenchmarkRunner:
    """Runs performance benchmarks for ReviewLab operations."""
    
    def __init__(self, output_file: str = None):
        self.output_file = output_file
        self.results = {}
        self.temp_dir = Path("temp_benchmark")
        self.temp_dir.mkdir(exist_ok=True)
    
    def run_benchmark(self, name: str, func: callable, iterations: int = 5, **kwargs) -> Dict[str, Any]:
        """Run a benchmark multiple times and return statistics."""
        print(f"🔄 Running benchmark: {name}")
        
        times = []
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = func(**kwargs)
                end_time = time.perf_counter()
                times.append(end_time - start_time)
                print(f"  Iteration {i+1}: {times[-1]:.4f}s")
            except Exception as e:
                print(f"  ❌ Iteration {i+1} failed: {e}")
                continue
        
        if not times:
            return {"error": "All iterations failed"}
        
        stats = {
            "iterations": len(times),
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "total_time": sum(times)
        }
        
        print(f"  📊 Results: avg={stats['avg_time']:.4f}s, std={stats['std_dev']:.4f}s")
        return stats
    
    def benchmark_template_loading(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark bug template loading performance."""
        def load_templates():
            manager = BugTemplateManager()
            return manager.get_templates()
        
        return self.run_benchmark("Template Loading", load_templates, iterations)
    
    def benchmark_bug_injection(self, language: str = "java", iterations: int = 5) -> Dict[str, Any]:
        """Benchmark bug injection performance."""
        # Create a temporary project
        project_dir = self.temp_dir / f"test_project_{language}"
        project_dir.mkdir(exist_ok=True)
        
        # Create a simple source file
        if language == "java":
            source_file = project_dir / "Main.java"
            source_content = """
public class Main {
    public static void main(String[] args) {
        String message = "Hello, World!";
        System.out.println(message);
        
        int[] numbers = {1, 2, 3, 4, 5};
        for (int i = 0; i < numbers.length; i++) {
            System.out.println(numbers[i]);
        }
    }
}
"""
        elif language == "python":
            source_file = project_dir / "main.py"
            source_content = """
def main():
    message = "Hello, World!"
    print(message)
    
    numbers = [1, 2, 3, 4, 5]
    for i in range(len(numbers)):
        print(numbers[i])

if __name__ == "__main__":
    main()
"""
        else:
            source_file = project_dir / "main.js"
            source_content = """
function main() {
    const message = "Hello, World!";
    console.log(message);
    
    const numbers = [1, 2, 3, 4, 5];
    for (let i = 0; i < numbers.length; i++) {
        console.log(numbers[i]);
    }
}

main();
"""
        
        source_file.write_text(source_content)
        
        def inject_bugs():
            engine = BugInjectionEngine(project_dir, language)
            return engine.inject_multiple_bugs(5)
        
        return self.run_benchmark(f"Bug Injection ({language})", inject_bugs, iterations)
    
    def benchmark_evaluation(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark evaluation engine performance."""
        # Create sample data
        findings = [
            {
                "id": f"finding_{i}",
                "file_path": f"src/file{i}.java",
                "line_number": i * 10,
                "message": f"Test finding {i}",
                "severity": "Medium",
                "category": "Bug",
                "confidence": 0.8,
                "tool": "TestTool"
            }
            for i in range(100)
        ]
        
        ground_truth = [
            {
                "id": f"bug_{i}",
                "template_id": f"template_{i}",
                "file_path": f"src/file{i}.java",
                "line_number": i * 10,
                "original_line": f"original line {i}",
                "modified_line": f"modified line {i}",
                "category": "Correctness",
                "severity": "Medium",
                "difficulty": "Easy"
            }
            for i in range(100)
        ]
        
        def evaluate():
            evaluator = EvaluationEngine()
            return evaluator.evaluate(findings, ground_truth)
        
        return self.run_benchmark("Evaluation Engine", evaluate, iterations)
    
    def benchmark_report_generation(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark report generation performance."""
        # Create sample evaluation result
        evaluation_result = {
            "precision": 0.75,
            "recall": 0.60,
            "f1_score": 0.67,
            "accuracy": 0.75,
            "total_findings": 100,
            "total_bugs": 50,
            "matched_bugs": 30,
            "false_positives": 10,
            "false_negatives": 20,
            "strategy_results": {},
            "recommendations": ["Optimize detection", "Reduce false positives"]
        }
        
        def generate_reports():
            generator = ReportGenerator()
            return generator.generate_all_reports(
                evaluation_result,
                "TestTool",
                "reports/benchmark"
            )
        
        return self.run_benchmark("Report Generation", generate_reports, iterations)
    
    def benchmark_git_operations(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark Git operations performance."""
        git_dir = self.temp_dir / "git_test"
        git_dir.mkdir(exist_ok=True)
        
        def git_ops():
            git_manager = GitManager(git_dir)
            git_manager.init_repository()
            git_manager.create_branch("test-branch")
            return True
        
        return self.run_benchmark("Git Operations", git_ops, iterations)
    
    def benchmark_memory_usage(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark memory usage for large operations."""
        import psutil
        import os
        
        def memory_intensive():
            # Create large data structures
            large_list = [f"item_{i}" * 1000 for i in range(10000)]
            large_dict = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}
            return len(large_list) + len(large_dict)
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        result = self.run_benchmark("Memory Usage", memory_intensive, iterations)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        result["memory_delta_mb"] = final_memory - initial_memory
        result["peak_memory_mb"] = final_memory
        
        return result
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks and return comprehensive results."""
        print("🚀 Starting ReviewLab Performance Benchmarks")
        print("=" * 50)
        
        # Run individual benchmarks
        self.results["template_loading"] = self.benchmark_template_loading()
        self.results["bug_injection_java"] = self.benchmark_bug_injection("java")
        self.results["bug_injection_python"] = self.benchmark_bug_injection("python")
        self.results["bug_injection_javascript"] = self.benchmark_bug_injection("javascript")
        self.results["evaluation_engine"] = self.benchmark_evaluation()
        self.results["report_generation"] = self.benchmark_report_generation()
        self.results["git_operations"] = self.benchmark_git_operations()
        self.results["memory_usage"] = self.benchmark_memory_usage()
        
        # Generate summary
        self.results["summary"] = self._generate_summary()
        
        # Save results
        if self.output_file:
            self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all benchmark results."""
        summary = {
            "total_benchmarks": len(self.results) - 1,  # Exclude summary itself
            "successful_benchmarks": 0,
            "failed_benchmarks": 0,
            "fastest_operation": None,
            "slowest_operation": None,
            "total_execution_time": 0
        }
        
        fastest_time = float('inf')
        slowest_time = 0
        
        for name, result in self.results.items():
            if name == "summary":
                continue
            
            if "error" in result:
                summary["failed_benchmarks"] += 1
            else:
                summary["successful_benchmarks"] += 1
                summary["total_execution_time"] += result["total_time"]
                
                if result["avg_time"] < fastest_time:
                    fastest_time = result["avg_time"]
                    summary["fastest_operation"] = name
                
                if result["avg_time"] > slowest_time:
                    slowest_time = result["avg_time"]
                    summary["slowest_operation"] = name
        
        return summary
    
    def _save_results(self):
        """Save benchmark results to file."""
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_path}")
    
    def _print_summary(self):
        """Print a summary of benchmark results."""
        print("\n" + "=" * 50)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 50)
        
        summary = self.results["summary"]
        print(f"Total Benchmarks: {summary['total_benchmarks']}")
        print(f"Successful: {summary['successful_benchmarks']}")
        print(f"Failed: {summary['failed_benchmarks']}")
        print(f"Fastest Operation: {summary['fastest_operation']}")
        print(f"Slowest Operation: {summary['slowest_operation']}")
        print(f"Total Execution Time: {summary['total_execution_time']:.2f}s")
        
        print("\n🏆 PERFORMANCE RANKINGS")
        print("-" * 30)
        
        # Sort by average time
        sorted_results = []
        for name, result in self.results.items():
            if name != "summary" and "error" not in result:
                sorted_results.append((name, result["avg_time"]))
        
        sorted_results.sort(key=lambda x: x[1])
        
        for i, (name, avg_time) in enumerate(sorted_results, 1):
            print(f"{i:2d}. {name:25s}: {avg_time:.4f}s")
    
    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        print("🧹 Cleaned up temporary files")


def main():
    """Main entry point for the benchmark script."""
    parser = argparse.ArgumentParser(description="ReviewLab Performance Benchmarking")
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    parser.add_argument("--iterations", "-i", type=int, default=5, help="Number of iterations per benchmark")
    parser.add_argument("--languages", "-l", nargs="+", default=["java"], help="Languages to benchmark for bug injection")
    
    args = parser.parse_args()
    
    try:
        runner = BenchmarkRunner(args.output)
        results = runner.run_all_benchmarks()
        
        if args.output:
            print(f"\n✅ Benchmark completed successfully!")
            print(f"📁 Results saved to: {args.output}")
        else:
            print(f"\n✅ Benchmark completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        sys.exit(1)
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()
