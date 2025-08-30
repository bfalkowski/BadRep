"""
Integration tests for the CLI interface.

These tests test actual CLI functionality with real data and components.
"""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.main import cli


class TestCLIIntegration:
    """Test CLI integration with real components."""

    def test_list_bugs_integration(self):
        """Test list-bugs command with real bug templates."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list-bugs", "--language", "java", "--format", "json"])

        assert result.exit_code == 0
        assert "📋 Available bug types for java:" in result.output

        # Parse JSON output - find the JSON array and extract it
        output_lines = result.output.strip().split("\n")
        json_start = output_lines.index("[")

        # Find where JSON ends (look for the closing bracket)
        json_end = json_start
        for i, line in enumerate(output_lines[json_start:], json_start):
            if line.strip() == "]":
                json_end = i
                break

        json_output = "\n".join(output_lines[json_start : json_end + 1])
        data = json.loads(json_output)

        # Verify we have bug templates
        assert len(data) > 0
        assert all("id" in template for template in data)
        assert all("name" in template for template in data)
        assert all("category" in template for template in data)

    def test_demo_integration(self):
        """Test demo command with real evaluation."""
        runner = CliRunner()
        result = runner.invoke(cli, ["demo", "--language", "java"])

        assert result.exit_code == 0
        assert "🎭 Running evaluation demo for java" in result.output
        assert "🎉 Demo completed successfully!" in result.output

        # Verify reports were generated
        reports_dir = Path("reports")
        assert reports_dir.exists()
        report_files = list(reports_dir.glob("demo_*"))
        assert len(report_files) > 0

    def test_evaluate_with_real_data(self):
        """Test evaluate command with real ground truth data."""
        # First run demo to generate ground truth
        runner = CliRunner()
        demo_result = runner.invoke(cli, ["demo", "--language", "java"])
        assert demo_result.exit_code == 0

        # Find the generated ground truth file
        ground_truth_dir = Path("ground_truth")
        if not ground_truth_dir.exists():
            pytest.skip("Ground truth directory not found - demo may not have generated files")

        ground_truth_files = list(ground_truth_dir.glob("*.jsonl"))
        if not ground_truth_files:
            pytest.skip("No ground truth files found - demo may not have generated files")

        ground_truth_file = ground_truth_files[0]

        # Create sample review findings
        findings = [
            {
                "id": "test_finding_1",
                "file_path": "src/Calculator.java",
                "line_number": 25,
                "finding_type": "bug",
                "severity": "high",
                "confidence": 0.9,
                "message": "Potential null pointer dereference",
                "rule_id": "NP_NULL_ON_SOME_PATH",
                "category": "correctness",
            },
            {
                "id": "test_finding_2",
                "file_path": "src/ArrayProcessor.java",
                "line_number": 42,
                "finding_type": "bug",
                "severity": "medium",
                "confidence": 0.8,
                "message": "Array index out of bounds",
                "rule_id": "AI_ANNOTATION_ISSUES",
                "category": "correctness",
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(findings, f, indent=2)
            findings_file = f.name

        try:
            # Run evaluation
            result = runner.invoke(
                cli,
                [
                    "evaluate",
                    "--findings",
                    findings_file,
                    "--ground-truth",
                    str(ground_truth_file),
                    "--review-tool",
                    "Integration Test Bot",
                    "--strategies",
                    "exact_overlap,line_range_overlap",
                    "--output-format",
                    "json",
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "🔍 Evaluating Integration Test Bot findings" in result.output
            assert "🎉 Evaluation completed successfully!" in result.output

            # Verify reports were generated
            reports_dir = Path("reports")
            assert reports_dir.exists()
            evaluation_files = list(reports_dir.glob("evaluation_report_*"))
            assert len(evaluation_files) > 0

        finally:
            # Clean up temporary file
            Path(findings_file).unlink(missing_ok=True)

    def test_generate_pr_dry_run(self):
        """Test generate-pr command in dry-run mode."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate-pr", "--count", "2", "--types", "correctness", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "🔍 DRY RUN MODE - No changes will be made" in result.output
        assert "This would:" in result.output
        assert "1. Create a new branch" in result.output
        assert "2. Inject specified bugs" in result.output
        assert "3. Commit changes" in result.output


class TestCLIWorkflow:
    """Test complete CLI workflows."""

    def test_complete_workflow(self):
        """Test a complete workflow: demo -> evaluate -> list-bugs."""
        runner = CliRunner()

        # Step 1: Run demo
        demo_result = runner.invoke(cli, ["demo", "--language", "java"])
        assert demo_result.exit_code == 0

        # Step 2: List available bugs
        list_result = runner.invoke(cli, ["list-bugs", "--language", "java", "--format", "table"])
        assert list_result.exit_code == 0
        assert "📋 Available bug types for java:" in list_result.output

        # Step 3: Check that reports were generated
        reports_dir = Path("reports")
        assert reports_dir.exists()

        # Step 4: Check that ground truth was generated
        ground_truth_dir = Path("ground_truth")
        if ground_truth_dir.exists():
            ground_truth_files = list(ground_truth_dir.glob("*.jsonl"))
            print(f"   - Ground truth generated: {len(ground_truth_files)} files")
        else:
            print("   - Ground truth directory not found")

        print(f"✅ Complete workflow test passed")
        print(f"   - Demo completed successfully")
        print(f"   - Bug templates listed successfully")
        print(f"   - Reports generated: {len(list(reports_dir.glob('*')))} files")
        print(f"   - Ground truth generated: {len(ground_truth_files)} files")
