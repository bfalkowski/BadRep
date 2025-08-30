"""
Unit tests for the report generator.
"""

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.evaluation import (
    EvaluationMetrics,
    EvaluationResult,
    FindingType,
    GroundTruthEntry,
    MatchResult,
    MatchStrategy,
    ReviewFinding,
)
from core.report_generator import ReportConfig, ReportGenerator


class TestReportConfig:
    """Test the ReportConfig class."""

    def test_report_config_creation(self):
        """Test creating a ReportConfig instance."""
        config = ReportConfig(
            include_detailed_matches=False,
            include_unmatched_items=False,
            include_visualizations=False,
            output_format="csv",
            report_title="Custom Report",
            include_timestamps=False,
            include_metadata=False,
        )

        assert config.include_detailed_matches is False
        assert config.include_unmatched_items is False
        assert config.include_visualizations is False
        assert config.output_format == "csv"
        assert config.report_title == "Custom Report"
        assert config.include_timestamps is False
        assert config.include_metadata is False


class TestReportGenerator:
    """Test the ReportGenerator class."""

    def test_report_generator_creation(self):
        """Test creating a ReportGenerator instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig()
            generator = ReportGenerator(config)

            assert generator.config == config
            assert generator.reports_dir == Path("reports")

    def test_generate_comprehensive_report_json(self):
        """Test generating a JSON report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(output_format="json")
            generator = ReportGenerator(config)

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=60,
                false_positives=40,
                false_negatives=20,
                precision=0.6,
                recall=0.75,
                f1_score=0.67,
                accuracy=0.6,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            output_file = Path(temp_dir) / "test_report.json"
            generated_file = generator.generate_comprehensive_report(result, output_file)

            assert generated_file.exists()
            assert generated_file.suffix == ".json"

            # Verify JSON content
            with open(generated_file, "r") as f:
                report_data = json.load(f)

            assert report_data["report_info"]["title"] == config.report_title
            assert report_data["summary"]["metrics"]["total_findings"] == 100
            assert report_data["summary"]["metrics"]["precision"] == 0.6

    def test_generate_comprehensive_report_csv(self):
        """Test generating a CSV report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(output_format="csv")
            generator = ReportGenerator(config)

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=60,
                false_positives=40,
                false_negatives=20,
                precision=0.6,
                recall=0.75,
                f1_score=0.67,
                accuracy=0.6,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            output_file = Path(temp_dir) / "test_report.csv"
            generated_file = generator.generate_comprehensive_report(result, output_file)

            assert generated_file.exists()
            assert generated_file.suffix == ".csv"

            # Verify CSV content
            with open(generated_file, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)

            assert len(rows) >= 2  # Header + data
            assert "Report Title" in rows[0]
            assert "100" in rows[1]  # Total findings
            assert "0.6000" in rows[1]  # Precision

    def test_generate_comprehensive_report_txt(self):
        """Test generating a text report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(output_format="txt")
            generator = ReportGenerator(config)

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=60,
                false_positives=40,
                false_negatives=20,
                precision=0.6,
                recall=0.75,
                f1_score=0.67,
                accuracy=0.6,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            output_file = Path(temp_dir) / "test_report.txt"
            generated_file = generator.generate_comprehensive_report(result, output_file)

            assert generated_file.exists()
            assert generated_file.suffix == ".txt"

            # Verify text content
            with open(generated_file, "r") as f:
                content = f.read()

            assert "Code Review Bot Evaluation Report" in content
            assert "test_session" in content
            assert "0.600" in content  # Precision
            assert "0.750" in content  # Recall

    def test_generate_comprehensive_report_html(self):
        """Test generating an HTML report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(output_format="html")
            generator = ReportGenerator(config)

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=60,
                false_positives=40,
                false_negatives=20,
                precision=0.6,
                recall=0.75,
                f1_score=0.67,
                accuracy=0.6,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            output_file = Path(temp_dir) / "test_report.html"
            generated_file = generator.generate_comprehensive_report(result, output_file)

            assert generated_file.exists()
            assert generated_file.suffix == ".html"

            # Verify HTML content
            with open(generated_file, "r") as f:
                content = f.read()

            assert "<!DOCTYPE html>" in content
            assert "Code Review Bot Evaluation Report" in content
            assert "test_session" in content
            assert "0.600" in content  # Precision

    def test_generate_comprehensive_report_unsupported_format(self):
        """Test generating report with unsupported format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(output_format="xml")
            generator = ReportGenerator(config)

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=60,
                false_positives=40,
                false_negatives=20,
                precision=0.6,
                recall=0.75,
                f1_score=0.67,
                accuracy=0.6,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            with pytest.raises(Exception, match="Unsupported output format"):
                generator.generate_comprehensive_report(result)

    def test_generate_comprehensive_report_with_matches(self):
        """Test generating report with detailed matches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(
                output_format="json", include_detailed_matches=True, include_unmatched_items=True
            )
            generator = ReportGenerator(config)

            # Create test findings and ground truth
            finding = ReviewFinding(
                id="test_finding", file_path="src/Test.java", line_number=42, message="Test finding"
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/Test.java",
                line_number=42,
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match_result = MatchResult(
                finding=finding,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.EXACT_OVERLAP,
                confidence=1.0,
                overlap_score=1.0,
            )

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=1,
                total_ground_truth=1,
                true_positives=1,
                false_positives=0,
                false_negatives=0,
                precision=1.0,
                recall=1.0,
                f1_score=1.0,
                accuracy=1.0,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[match_result],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            output_file = Path(temp_dir) / "test_report.json"
            generated_file = generator.generate_comprehensive_report(result, output_file)

            # Verify JSON content includes matches
            with open(generated_file, "r") as f:
                report_data = json.load(f)

            assert len(report_data["matches"]) == 1
            assert report_data["matches"][0]["finding"]["id"] == "test_finding"
            assert report_data["matches"][0]["ground_truth_id"] == "test_gt"

    def test_generate_comprehensive_report_without_matches(self):
        """Test generating report without detailed matches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReportConfig(
                output_format="json", include_detailed_matches=False, include_unmatched_items=False
            )
            generator = ReportGenerator(config)

            # Create test evaluation result
            metrics = EvaluationMetrics(
                total_findings=1,
                total_ground_truth=1,
                true_positives=1,
                false_positives=0,
                false_negatives=0,
                precision=1.0,
                recall=1.0,
                f1_score=1.0,
                accuracy=1.0,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            output_file = Path(temp_dir) / "test_report.json"
            generated_file = generator.generate_comprehensive_report(result, output_file)

            # Verify JSON content excludes matches
            with open(generated_file, "r") as f:
                report_data = json.load(f)

            assert len(report_data["matches"]) == 0
            assert len(report_data["unmatched_findings"]) == 0
            assert len(report_data["unmatched_ground_truth"]) == 0

    def test_get_performance_rating(self):
        """Test performance rating calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            assert generator._get_performance_rating(0.95) == "Excellent"
            assert generator._get_performance_rating(0.85) == "Very Good"
            assert generator._get_performance_rating(0.75) == "Good"
            assert generator._get_performance_rating(0.65) == "Fair"
            assert generator._get_performance_rating(0.55) == "Poor"
            assert generator._get_performance_rating(0.35) == "Very Poor"

    def test_get_performance_class(self):
        """Test performance class calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            assert generator._get_performance_class(0.85) == "excellent"
            assert generator._get_performance_class(0.75) == "good"
            assert generator._get_performance_class(0.45) == "poor"

    def test_get_performance_color(self):
        """Test performance color calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            assert generator._get_performance_color(0.85) == "#28a745"  # Green
            assert generator._get_performance_color(0.75) == "#ffc107"  # Yellow
            assert generator._get_performance_color(0.45) == "#dc3545"  # Red

    def test_get_match_breakdown(self):
        """Test match breakdown calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test matches
            finding1 = ReviewFinding(
                id="finding1", file_path="src/Test.java", line_number=42, message="Test finding 1"
            )

            finding2 = ReviewFinding(
                id="finding2", file_path="src/Test.java", line_number=50, message="Test finding 2"
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/Test.java",
                line_number=42,
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match1 = MatchResult(
                finding=finding1,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.EXACT_OVERLAP,
                confidence=1.0,
                overlap_score=1.0,
            )

            match2 = MatchResult(
                finding=finding2,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.LINE_RANGE_OVERLAP,
                confidence=0.8,
                overlap_score=0.8,
            )

            matches = [match1, match2]
            breakdown = generator._get_match_breakdown(matches)

            assert breakdown["exact_overlap"] == 1
            assert breakdown["line_range_overlap"] == 1
            assert len(breakdown) == 2

    def test_identify_strengths(self):
        """Test strength identification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test result with high precision
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=80,
                false_positives=20,
                false_negatives=0,
                precision=0.8,
                recall=1.0,
                f1_score=0.89,
                accuracy=0.8,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            strengths = generator._identify_strengths(result)

            assert "High recall indicates good coverage of ground truth" in strengths
            assert "High recall indicates good coverage of ground truth" in strengths
            assert "Balanced precision and recall performance" in strengths

    def test_identify_weaknesses(self):
        """Test weakness identification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test result with low precision
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=40,
                false_positives=60,
                false_negatives=40,
                precision=0.4,
                recall=0.5,
                f1_score=0.44,
                accuracy=0.4,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            weaknesses = generator._identify_weaknesses(result)

            assert "Low precision indicates high false positive rate" in weaknesses
            assert "Low recall indicates poor coverage of ground truth" in weaknesses
            assert "Poor overall performance balance" in weaknesses

    def test_generate_performance_insights(self):
        """Test performance insights generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test result
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=60,
                false_positives=40,
                false_negatives=20,
                precision=0.6,
                recall=0.75,
                f1_score=0.67,
                accuracy=0.6,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            insights = generator._generate_performance_insights(result)

            assert (
                "Higher recall than precision suggests the tool prioritizes coverage over accuracy"
                in insights
            )

    def test_generate_recommendations(self):
        """Test recommendations generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test result with low precision
            metrics = EvaluationMetrics(
                total_findings=100,
                total_ground_truth=80,
                true_positives=40,
                false_positives=60,
                false_negatives=40,
                precision=0.4,
                recall=0.5,
                f1_score=0.44,
                accuracy=0.4,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[],
                unmatched_findings=[],
                unmatched_ground_truth=[],
            )

            recommendations = generator._generate_recommendations(result)

            assert (
                "Focus on reducing false positives by improving detection rules" in recommendations
            )
            assert "Improve coverage by expanding detection patterns and rules" in recommendations

    def test_analyze_file_performance(self):
        """Test file performance analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test result with file-specific data
            finding1 = ReviewFinding(
                id="finding1", file_path="src/Test1.java", line_number=42, message="Test finding 1"
            )

            finding2 = ReviewFinding(
                id="finding2", file_path="src/Test2.java", line_number=50, message="Test finding 2"
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/Test1.java",
                line_number=42,
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            # Create test metrics
            metrics = EvaluationMetrics(
                total_findings=2,
                total_ground_truth=1,
                true_positives=1,
                false_positives=1,
                false_negatives=0,
                precision=0.5,
                recall=1.0,
                f1_score=0.67,
                accuracy=1.0,
            )

            match_result = MatchResult(
                finding=finding1,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.EXACT_OVERLAP,
                confidence=1.0,
                overlap_score=1.0,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[match_result],
                unmatched_findings=[finding2],
                unmatched_ground_truth=[],
            )

            file_analysis = generator._analyze_file_performance(result)

            assert "src/Test1.java" in file_analysis
            assert file_analysis["src/Test1.java"]["matches"] == 1
            assert "src/Test2.java" in file_analysis
            assert file_analysis["src/Test2.java"]["total_findings"] == 1

    def test_analyze_severity_performance(self):
        """Test severity performance analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator()

            # Create test result with severity data
            finding1 = ReviewFinding(
                id="finding1",
                file_path="src/Test.java",
                line_number=42,
                severity="high",
                message="Test finding 1",
            )

            finding2 = ReviewFinding(
                id="finding2",
                file_path="src/Test.java",
                line_number=50,
                severity="medium",
                message="Test finding 2",
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/Test.java",
                line_number=42,
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            # Create test metrics
            metrics = EvaluationMetrics(
                total_findings=2,
                total_ground_truth=1,
                true_positives=1,
                false_positives=1,
                false_negatives=0,
                precision=0.5,
                recall=1.0,
                f1_score=0.67,
                accuracy=1.0,
            )

            match_result = MatchResult(
                finding=finding1,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.EXACT_OVERLAP,
                confidence=1.0,
                overlap_score=1.0,
            )

            result = EvaluationResult(
                session_id="test_session",
                review_tool="test_tool",
                evaluation_timestamp="2024-01-01T00:00:00",
                metrics=metrics,
                matches=[match_result],
                unmatched_findings=[finding2],
                unmatched_ground_truth=[],
            )

            severity_analysis = generator._analyze_severity_performance(result)

            assert "high" in severity_analysis
            assert severity_analysis["high"]["matches"] == 1
            assert "medium" in severity_analysis
            assert severity_analysis["medium"]["total_findings"] == 1
