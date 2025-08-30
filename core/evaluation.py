"""
Evaluation Engine for ReviewLab.

This module provides the core evaluation capabilities for measuring
code review bot accuracy against ground truth data.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from core.errors import EvaluationError
from core.bug_injection import GroundTruthEntry


class MatchStrategy(Enum):
    """Strategies for matching review findings to ground truth."""
    EXACT_OVERLAP = "exact_overlap"
    LINE_RANGE_OVERLAP = "line_range_overlap"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    BREADCRUMB_MATCHING = "breadcrumb_matching"
    FUZZY_MATCHING = "fuzzy_matching"


class FindingType(Enum):
    """Types of code review findings."""
    BUG = "bug"
    CODE_SMELL = "code_smell"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    MAINTAINABILITY_ISSUE = "maintainability_issue"
    OTHER = "other"


@dataclass
class ReviewFinding:
    """Represents a finding from a code review bot."""
    id: str
    file_path: str
    line_number: int
    end_line: Optional[int] = None
    finding_type: FindingType = FindingType.BUG
    severity: str = "medium"
    confidence: float = 0.8
    message: str = ""
    rule_id: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'end_line': self.end_line,
            'finding_type': self.finding_type.value,
            'severity': self.severity,
            'confidence': self.confidence,
            'message': self.message,
            'rule_id': self.rule_id,
            'category': self.category,
            'metadata': self.metadata
        }


@dataclass
class MatchResult:
    """Result of matching a review finding to ground truth."""
    finding: ReviewFinding
    ground_truth: GroundTruthEntry
    match_strategy: MatchStrategy
    confidence: float
    overlap_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'finding': self.finding.to_dict(),
            'ground_truth_id': self.ground_truth.id,
            'match_strategy': self.match_strategy.value,
            'confidence': self.confidence,
            'overlap_score': self.overlap_score,
            'metadata': self.metadata
        }


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for a review session."""
    total_findings: int
    total_ground_truth: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    match_breakdown: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'total_findings': self.total_findings,
            'total_ground_truth': self.total_ground_truth,
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'accuracy': self.accuracy,
            'match_breakdown': self.match_breakdown
        }


@dataclass
class EvaluationResult:
    """Complete evaluation result for a review session."""
    session_id: str
    review_tool: str
    evaluation_timestamp: str
    metrics: EvaluationMetrics
    matches: List[MatchResult]
    unmatched_findings: List[ReviewFinding]
    unmatched_ground_truth: List[GroundTruthEntry]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'session_id': self.session_id,
            'review_tool': self.review_tool,
            'evaluation_timestamp': self.evaluation_timestamp,
            'metrics': self.metrics.to_dict(),
            'matches': [match.to_dict() for match in self.matches],
            'unmatched_findings': [finding.to_dict() for finding in self.unmatched_findings],
            'unmatched_ground_truth': [gt.to_dict() for gt in self.unmatched_ground_truth],
            'metadata': self.metadata
        }


class EvaluationEngine:
    """Main engine for evaluating code review bot accuracy."""
    
    def __init__(self, ground_truth_dir: Optional[Path] = None):
        self.ground_truth_dir = Path(ground_truth_dir) if ground_truth_dir else Path("ground_truth")
        self.match_strategies = {
            MatchStrategy.EXACT_OVERLAP: self._exact_overlap_match,
            MatchStrategy.LINE_RANGE_OVERLAP: self._line_range_overlap_match,
            MatchStrategy.SEMANTIC_SIMILARITY: self._semantic_similarity_match,
            MatchStrategy.BREADCRUMB_MATCHING: self._breadcrumb_match,
            MatchStrategy.FUZZY_MATCHING: self._fuzzy_match
        }
    
    def evaluate_review(self, review_findings: List[ReviewFinding], 
                       ground_truth_entries: List[GroundTruthEntry],
                       review_tool: str = "unknown",
                       strategies: Optional[List[MatchStrategy]] = None) -> EvaluationResult:
        """Evaluate review findings against ground truth data."""
        if not review_findings or not ground_truth_entries:
            raise EvaluationError("Both review findings and ground truth entries are required")
        
        # Use default strategies if none specified
        if not strategies:
            strategies = [
                MatchStrategy.EXACT_OVERLAP,
                MatchStrategy.LINE_RANGE_OVERLAP,
                MatchStrategy.SEMANTIC_SIMILARITY
            ]
        
        # Match findings to ground truth
        matches = []
        matched_findings = set()
        matched_ground_truth = set()
        
        # Try each strategy in order
        for strategy in strategies:
            if strategy not in self.match_strategies:
                continue
            
            strategy_matches = self._apply_match_strategy(
                strategy, review_findings, ground_truth_entries,
                matched_findings, matched_ground_truth
            )
            matches.extend(strategy_matches)
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            len(review_findings),
            len(ground_truth_entries),
            len(matches)
        )
        
        # Identify unmatched items
        unmatched_findings = [
            f for f in review_findings 
            if f.id not in matched_findings
        ]
        
        unmatched_ground_truth = [
            gt for gt in ground_truth_entries
            if gt.id not in matched_ground_truth
        ]
        
        # Create evaluation result
        result = EvaluationResult(
            session_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            review_tool=review_tool,
            evaluation_timestamp=datetime.now().isoformat(),
            metrics=metrics,
            matches=matches,
            unmatched_findings=unmatched_findings,
            unmatched_ground_truth=unmatched_ground_truth,
            metadata={
                'strategies_used': [s.value for s in strategies],
                'total_matches': len(matches)
            }
        )
        
        return result
    
    def _apply_match_strategy(self, strategy: MatchStrategy,
                            findings: List[ReviewFinding],
                            ground_truth: List[GroundTruthEntry],
                            matched_findings: Set[str],
                            matched_ground_truth: Set[str]) -> List[MatchResult]:
        """Apply a specific matching strategy."""
        matches = []
        matcher = self.match_strategies[strategy]
        
        for finding in findings:
            if finding.id in matched_findings:
                continue
                
            for gt in ground_truth:
                if gt.id in matched_ground_truth:
                    continue
                
                match_result = matcher(finding, gt)
                if match_result and match_result.confidence > 0.5:
                    matches.append(match_result)
                    matched_findings.add(finding.id)
                    matched_ground_truth.add(gt.id)
                    break
        
        return matches
    
    def _exact_overlap_match(self, finding: ReviewFinding, 
                            ground_truth: GroundTruthEntry) -> Optional[MatchResult]:
        """Exact overlap matching based on file and line."""
        if (finding.file_path == ground_truth.file_path and 
            finding.line_number == ground_truth.line_number):
            return MatchResult(
                finding=finding,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.EXACT_OVERLAP,
                confidence=1.0,
                overlap_score=1.0,
                metadata={'match_type': 'exact'}
            )
        return None
    
    def _line_range_overlap_match(self, finding: ReviewFinding,
                                ground_truth: GroundTruthEntry) -> Optional[MatchResult]:
        """Line range overlap matching."""
        if finding.file_path != ground_truth.file_path:
            return None
        
        # Check if lines overlap
        finding_start = finding.line_number
        finding_end = finding.end_line or finding.line_number
        gt_start = ground_truth.line_number
        gt_end = ground_truth.line_number  # Ground truth is typically single line
        
        # Calculate overlap
        overlap_start = max(finding_start, gt_start)
        overlap_end = min(finding_end, gt_end)
        
        if overlap_start <= overlap_end:
            # Calculate overlap score
            finding_range = finding_end - finding_start + 1
            overlap_range = overlap_end - overlap_start + 1
            overlap_score = overlap_range / finding_range
            
            # Calculate confidence based on overlap
            confidence = min(overlap_score * 1.5, 1.0)  # Boost confidence more for better matching
            
            return MatchResult(
                finding=finding,
                ground_truth=ground_truth,
                match_strategy=MatchStrategy.LINE_RANGE_OVERLAP,
                confidence=confidence,
                overlap_score=overlap_score,
                metadata={
                    'match_type': 'range_overlap',
                    'overlap_start': overlap_start,
                    'overlap_end': overlap_end,
                    'overlap_range': overlap_range
                }
            )
        
        return None
    
    def _semantic_similarity_match(self, finding: ReviewFinding,
                                 ground_truth: GroundTruthEntry) -> Optional[MatchResult]:
        """Semantic similarity matching based on bug type and description."""
        # Check if bug types are similar
        if finding.finding_type.value == "bug" and ground_truth.bug_type:
            # Simple keyword matching for now
            finding_keywords = self._extract_keywords(finding.message.lower())
            gt_keywords = self._extract_keywords(ground_truth.description.lower())
            
            if finding_keywords and gt_keywords:
                # Calculate keyword overlap
                common_keywords = finding_keywords.intersection(gt_keywords)
                total_keywords = finding_keywords.union(gt_keywords)
                
                if total_keywords:
                    similarity_score = len(common_keywords) / len(total_keywords)
                    
                    if similarity_score > 0.3:  # Threshold for semantic match
                        return MatchResult(
                            finding=finding,
                            ground_truth=ground_truth,
                            match_strategy=MatchStrategy.SEMANTIC_SIMILARITY,
                            confidence=similarity_score * 0.8,  # Reduce confidence for semantic matches
                            overlap_score=similarity_score,
                            metadata={
                                'match_type': 'semantic',
                                'common_keywords': list(common_keywords),
                                'similarity_score': similarity_score
                            }
                        )
        
        return None
    
    def _breadcrumb_match(self, finding: ReviewFinding,
                         ground_truth: GroundTruthEntry) -> Optional[MatchResult]:
        """Breadcrumb matching based on contextual clues."""
        # Check if files are in the same directory or have similar names
        finding_file = Path(finding.file_path)
        gt_file = Path(ground_truth.file_path)
        
        # Same directory match
        if finding_file.parent == gt_file.parent:
            # Check if line numbers are close
            line_distance = abs(finding.line_number - ground_truth.line_number)
            if line_distance <= 10:  # Within 10 lines
                confidence = max(0.6, 1.0 - (line_distance * 0.05))
                return MatchResult(
                    finding=finding,
                    ground_truth=ground_truth,
                    match_strategy=MatchStrategy.BREADCRUMB_MATCHING,
                    confidence=confidence,
                    overlap_score=0.5,  # Moderate overlap for breadcrumb
                    metadata={
                        'match_type': 'breadcrumb',
                        'line_distance': line_distance,
                        'same_directory': True
                    }
                )
        
        return None
    
    def _fuzzy_match(self, finding: ReviewFinding,
                    ground_truth: GroundTruthEntry) -> Optional[MatchResult]:
        """Fuzzy matching for edge cases."""
        # Check if files have similar names
        finding_file = Path(finding.file_path).stem
        gt_file = Path(ground_truth.file_path).stem
        
        # Simple string similarity
        if finding_file == gt_file:
            # Same file, check if lines are reasonably close
            line_distance = abs(finding.line_number - ground_truth.line_number)
            if line_distance <= 20:  # Within 20 lines
                confidence = max(0.4, 1.0 - (line_distance * 0.03))
                return MatchResult(
                    finding=finding,
                    ground_truth=ground_truth,
                    match_strategy=MatchStrategy.FUZZY_MATCHING,
                    confidence=confidence,
                    overlap_score=0.3,  # Low overlap for fuzzy matches
                    metadata={
                        'match_type': 'fuzzy',
                        'line_distance': line_distance,
                        'file_similarity': 1.0
                    }
                )
        
        return None
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text for semantic matching."""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'occurs'}
        
        # Split text and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = {word for word in words if len(word) > 2 and word not in common_words}
        
        return keywords
    
    def _calculate_metrics(self, total_findings: int, total_ground_truth: int, 
                          true_positives: int) -> EvaluationMetrics:
        """Calculate evaluation metrics."""
        false_positives = total_findings - true_positives
        false_negatives = total_ground_truth - true_positives
        
        # Calculate precision, recall, F1, and accuracy
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        # Accuracy is true_positives / total_ground_truth (not total_findings)
        accuracy = true_positives / total_ground_truth if total_ground_truth > 0 else 0.0
        
        return EvaluationMetrics(
            total_findings=total_findings,
            total_ground_truth=total_ground_truth,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy
        )
    
    def load_ground_truth_from_file(self, file_path: Path) -> List[GroundTruthEntry]:
        """Load ground truth entries from a JSONL file."""
        entries = []
        
        if not file_path.exists():
            return entries
        
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data = json.loads(line)
                        entry = GroundTruthEntry(**data)
                        entries.append(entry)
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"Warning: Failed to parse line {line_num} in {file_path}: {e}")
                        continue
        
        return entries
    
    def export_evaluation_result(self, result: EvaluationResult, output_file: Path):
        """Export evaluation result to a file."""
        with open(output_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
    
    def generate_summary_report(self, result: EvaluationResult) -> str:
        """Generate a human-readable summary report."""
        report = []
        report.append("=" * 60)
        report.append("REVIEW EVALUATION SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"Session ID: {result.session_id}")
        report.append(f"Review Tool: {result.review_tool}")
        report.append(f"Evaluation Time: {result.evaluation_timestamp}")
        report.append("")
        
        # Metrics summary
        report.append("METRICS SUMMARY:")
        report.append("-" * 20)
        report.append(f"Total Findings: {result.metrics.total_findings}")
        report.append(f"Total Ground Truth: {result.metrics.total_ground_truth}")
        report.append(f"True Positives: {result.metrics.true_positives}")
        report.append(f"False Positives: {result.metrics.false_positives}")
        report.append(f"False Negatives: {result.metrics.false_negatives}")
        report.append("")
        report.append(f"Precision: {result.metrics.precision:.3f}")
        report.append(f"Recall: {result.metrics.recall:.3f}")
        report.append(f"F1-Score: {result.metrics.f1_score:.3f}")
        report.append(f"Accuracy: {result.metrics.accuracy:.3f}")
        report.append("")
        
        # Match breakdown
        report.append("MATCH BREAKDOWN:")
        report.append("-" * 20)
        for strategy in MatchStrategy:
            strategy_matches = [m for m in result.matches if m.match_strategy == strategy]
            report.append(f"{strategy.value}: {len(strategy_matches)} matches")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
