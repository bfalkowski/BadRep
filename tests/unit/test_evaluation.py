"""
Unit tests for the evaluation engine.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.bug_injection import GroundTruthEntry
from core.errors import EvaluationError
from core.evaluation import (
    EvaluationEngine,
    EvaluationMetrics,
    EvaluationResult,
    FindingType,
    MatchResult,
    MatchStrategy,
    ReviewFinding,
)


class TestMatchStrategy:
    """Test the MatchStrategy enum."""

    def test_match_strategy_values(self):
        """Test that all match strategies have expected values."""
        assert MatchStrategy.EXACT_OVERLAP.value == "exact_overlap"
        assert MatchStrategy.LINE_RANGE_OVERLAP.value == "line_range_overlap"
        assert MatchStrategy.SEMANTIC_SIMILARITY.value == "semantic_similarity"
        assert MatchStrategy.BREADCRUMB_MATCHING.value == "breadcrumb_matching"
        assert MatchStrategy.FUZZY_MATCHING.value == "fuzzy_matching"


class TestFindingType:
    """Test the FindingType enum."""

    def test_finding_type_values(self):
        """Test that all finding types have expected values."""
        assert FindingType.BUG.value == "bug"
        assert FindingType.CODE_SMELL.value == "code_smell"
        assert FindingType.SECURITY_ISSUE.value == "security_issue"
        assert FindingType.PERFORMANCE_ISSUE.value == "performance_issue"
        assert FindingType.MAINTAINABILITY_ISSUE.value == "maintainability_issue"
        assert FindingType.OTHER.value == "other"


class TestReviewFinding:
    """Test the ReviewFinding class."""

    def test_review_finding_creation(self):
        """Test creating a ReviewFinding instance."""
        finding = ReviewFinding(
            id="test_finding_1",
            file_path="src/Test.java",
            line_number=42,
            end_line=45,
            finding_type=FindingType.BUG,
            severity="high",
            confidence=0.9,
            message="Potential null pointer dereference",
            rule_id="NP_NULL_ON_SOME_PATH",
            category="correctness",
        )

        assert finding.id == "test_finding_1"
        assert finding.file_path == "src/Test.java"
        assert finding.line_number == 42
        assert finding.end_line == 45
        assert finding.finding_type == FindingType.BUG
        assert finding.severity == "high"
        assert finding.confidence == 0.9
        assert finding.message == "Potential null pointer dereference"
        assert finding.rule_id == "NP_NULL_ON_SOME_PATH"
        assert finding.category == "correctness"

    def test_review_finding_to_dict(self):
        """Test converting ReviewFinding to dictionary."""
        finding = ReviewFinding(
            id="test_finding_2",
            file_path="src/Test.java",
            line_number=42,
            finding_type=FindingType.BUG,
            message="Test finding",
        )

        finding_dict = finding.to_dict()
        assert finding_dict["id"] == "test_finding_2"
        assert finding_dict["file_path"] == "src/Test.java"
        assert finding_dict["line_number"] == 42
        assert finding_dict["finding_type"] == "bug"
        assert finding_dict["message"] == "Test finding"


class TestMatchResult:
    """Test the MatchResult class."""

    def test_match_result_creation(self):
        """Test creating a MatchResult instance."""
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
            metadata={"match_type": "exact"},
        )

        assert match_result.finding == finding
        assert match_result.ground_truth == ground_truth
        assert match_result.match_strategy == MatchStrategy.EXACT_OVERLAP
        assert match_result.confidence == 1.0
        assert match_result.overlap_score == 1.0
        assert match_result.metadata["match_type"] == "exact"

    def test_match_result_to_dict(self):
        """Test converting MatchResult to dictionary."""
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

        match_dict = match_result.to_dict()
        assert match_dict["finding"]["id"] == "test_finding"
        assert match_dict["ground_truth_id"] == "test_gt"
        assert match_dict["match_strategy"] == "exact_overlap"
        assert match_dict["confidence"] == 1.0
        assert match_dict["overlap_score"] == 1.0


class TestEvaluationMetrics:
    """Test the EvaluationMetrics class."""

    def test_evaluation_metrics_creation(self):
        """Test creating EvaluationMetrics instance."""
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
            match_breakdown={"exact_overlap": 40, "line_range_overlap": 20},
        )

        assert metrics.total_findings == 100
        assert metrics.total_ground_truth == 80
        assert metrics.true_positives == 60
        assert metrics.false_positives == 40
        assert metrics.false_negatives == 20
        assert metrics.precision == 0.6
        assert metrics.recall == 0.75
        assert metrics.f1_score == 0.67
        assert metrics.accuracy == 0.6
        assert metrics.match_breakdown["exact_overlap"] == 40

    def test_evaluation_metrics_to_dict(self):
        """Test converting EvaluationMetrics to dictionary."""
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

        metrics_dict = metrics.to_dict()
        assert metrics_dict["total_findings"] == 100
        assert metrics_dict["precision"] == 0.6
        assert metrics_dict["f1_score"] == 0.67


class TestEvaluationResult:
    """Test the EvaluationResult class."""

    def test_evaluation_result_creation(self):
        """Test creating EvaluationResult instance."""
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

        result = EvaluationResult(
            session_id="test_session",
            review_tool="test_tool",
            evaluation_timestamp="2024-01-01T00:00:00",
            metrics=metrics,
            matches=[match_result],
            unmatched_findings=[],
            unmatched_ground_truth=[],
            metadata={"test": "data"},
        )

        assert result.session_id == "test_session"
        assert result.review_tool == "test_tool"
        assert result.metrics == metrics
        assert len(result.matches) == 1
        assert result.metadata["test"] == "data"

    def test_evaluation_result_to_dict(self):
        """Test converting EvaluationResult to dictionary."""
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

        result_dict = result.to_dict()
        assert result_dict["session_id"] == "test_session"
        assert result_dict["review_tool"] == "test_tool"
        assert result_dict["metrics"]["total_findings"] == 100


class TestEvaluationEngine:
    """Test the EvaluationEngine class."""

    def test_evaluation_engine_creation(self):
        """Test creating EvaluationEngine instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))
            assert engine.ground_truth_dir == Path(temp_dir)
            assert len(engine.match_strategies) == 5

    def test_evaluate_review_empty_inputs(self):
        """Test evaluation with empty inputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            with pytest.raises(
                EvaluationError, match="Both review findings and ground truth entries are required"
            ):
                engine.evaluate_review([], [])

    def test_exact_overlap_match(self):
        """Test exact overlap matching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

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

            match_result = engine._exact_overlap_match(finding, ground_truth)

            assert match_result is not None
            assert match_result.confidence == 1.0
            assert match_result.overlap_score == 1.0
            assert match_result.match_strategy == MatchStrategy.EXACT_OVERLAP

    def test_exact_overlap_no_match(self):
        """Test exact overlap matching when no match."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

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
                line_number=43,  # Different line
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match_result = engine._exact_overlap_match(finding, ground_truth)
            assert match_result is None

    def test_line_range_overlap_match(self):
        """Test line range overlap matching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            finding = ReviewFinding(
                id="test_finding",
                file_path="src/Test.java",
                line_number=40,
                end_line=45,
                message="Test finding",
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/Test.java",
                line_number=42,  # Within range
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match_result = engine._line_range_overlap_match(finding, ground_truth)

            assert match_result is not None
            assert match_result.confidence > 0.2
            assert match_result.overlap_score > 0.1
            assert match_result.match_strategy == MatchStrategy.LINE_RANGE_OVERLAP

    def test_semantic_similarity_match(self):
        """Test semantic similarity matching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            finding = ReviewFinding(
                id="test_finding",
                file_path="src/Test.java",
                line_number=42,
                finding_type=FindingType.BUG,
                message="null pointer dereference error",
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/Test.java",
                line_number=50,
                bug_type="correctness",
                description="null pointer dereference bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match_result = engine._semantic_similarity_match(finding, ground_truth)

            assert match_result is not None
            assert match_result.match_strategy == MatchStrategy.SEMANTIC_SIMILARITY
            assert match_result.confidence > 0.3

    def test_breadcrumb_match(self):
        """Test breadcrumb matching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            finding = ReviewFinding(
                id="test_finding",
                file_path="src/main/Test.java",
                line_number=42,
                message="Test finding",
            )

            ground_truth = GroundTruthEntry(
                id="test_gt",
                injection_id="test_injection",
                template_id="test_template",
                project_path="/test/project",
                language="java",
                file_path="src/main/Test.java",
                line_number=45,  # Close line
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match_result = engine._breadcrumb_match(finding, ground_truth)

            assert match_result is not None
            assert match_result.match_strategy == MatchStrategy.BREADCRUMB_MATCHING
            assert match_result.confidence > 0.6

    def test_fuzzy_match(self):
        """Test fuzzy matching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

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
                line_number=50,  # Reasonably close
                bug_type="correctness",
                description="Test bug",
                severity="high",
                difficulty="easy",
                injection_timestamp="2024-01-01T00:00:00",
                original_code="original",
                modified_code="modified",
            )

            match_result = engine._fuzzy_match(finding, ground_truth)

            assert match_result is not None
            assert match_result.match_strategy == MatchStrategy.FUZZY_MATCHING
            assert match_result.confidence > 0.4

    def test_extract_keywords(self):
        """Test keyword extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            text = "The null pointer dereference error occurs in the main method"
            keywords = engine._extract_keywords(text)

            assert "null" in keywords
            assert "pointer" in keywords
            assert "dereference" in keywords
            assert "error" in keywords
            assert "main" in keywords
            assert "method" in keywords

            # Common words should be filtered out
            assert "the" not in keywords
            assert "in" not in keywords
            assert "occurs" not in keywords

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            metrics = engine._calculate_metrics(100, 80, 60)

            assert metrics.total_findings == 100
            assert metrics.total_ground_truth == 80
            assert metrics.true_positives == 60
            assert metrics.false_positives == 40
            assert metrics.false_negatives == 20
            assert metrics.precision == 0.6
            assert metrics.recall == 0.75
            assert abs(metrics.f1_score - 0.67) < 0.01
            assert metrics.accuracy == 0.75

    def test_calculate_metrics_edge_cases(self):
        """Test metrics calculation edge cases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

            # No findings
            metrics = engine._calculate_metrics(0, 0, 0)
            assert metrics.precision == 0.0
            assert metrics.recall == 0.0
            assert metrics.f1_score == 0.0
            assert metrics.accuracy == 0.0

            # No false positives
            metrics = engine._calculate_metrics(60, 80, 60)
            assert metrics.precision == 1.0
            assert metrics.recall == 0.75
            assert abs(metrics.f1_score - 0.86) < 0.01

    def test_generate_summary_report(self):
        """Test summary report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvaluationEngine(Path(temp_dir))

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

            report = engine.generate_summary_report(result)

            assert "REVIEW EVALUATION SUMMARY REPORT" in report
            assert "test_session" in report
            assert "test_tool" in report
            assert "0.600" in report  # Precision
            assert "0.750" in report  # Recall
            assert "0.670" in report  # F1-Score
