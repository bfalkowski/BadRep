"""
Report Generator for ReviewLab Evaluation.

This module generates comprehensive evaluation reports with visualizations,
analysis, and insights for code review bot evaluation results.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from core.evaluation import EvaluationResult, MatchResult, ReviewFinding, GroundTruthEntry
from core.errors import EvaluationError


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    include_detailed_matches: bool = True
    include_unmatched_items: bool = True
    include_visualizations: bool = True
    output_format: str = "json"  # json, csv, txt, html
    report_title: str = "Code Review Bot Evaluation Report"
    include_timestamps: bool = True
    include_metadata: bool = True


class ReportGenerator:
    """Generates comprehensive evaluation reports."""
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self, evaluation_result: EvaluationResult,
                                   output_file: Optional[Path] = None) -> Path:
        """Generate a comprehensive evaluation report."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.reports_dir / f"evaluation_report_{timestamp}.{self.config.output_format}"
        
        if self.config.output_format == "json":
            return self._generate_json_report(evaluation_result, output_file)
        elif self.config.output_format == "csv":
            return self._generate_csv_report(evaluation_result, output_file)
        elif self.config.output_format == "txt":
            return self._generate_text_report(evaluation_result, output_file)
        elif self.config.output_format == "html":
            return self._generate_html_report(evaluation_result, output_file)
        else:
            raise EvaluationError(f"Unsupported output format: {self.config.output_format}")
    
    def _generate_json_report(self, result: EvaluationResult, output_file: Path) -> Path:
        """Generate a JSON report."""
        report_data = {
            'report_info': {
                'title': self.config.report_title,
                'generated_at': datetime.now().isoformat(),
                'evaluation_session': result.session_id,
                'review_tool': result.review_tool
            },
            'summary': {
                'metrics': result.metrics.to_dict(),
                'total_matches': len(result.matches),
                'match_rate': len(result.matches) / result.metrics.total_ground_truth if result.metrics.total_ground_truth > 0 else 0
            },
            'detailed_analysis': self._generate_detailed_analysis(result),
            'matches': [match.to_dict() for match in result.matches] if self.config.include_detailed_matches else [],
            'unmatched_findings': [f.to_dict() for f in result.unmatched_findings] if self.config.include_unmatched_items else [],
            'unmatched_ground_truth': [gt.to_dict() for gt in result.unmatched_ground_truth] if self.config.include_unmatched_items else [],
            'metadata': result.metadata if self.config.include_metadata else {}
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_file
    
    def _generate_csv_report(self, result: EvaluationResult, output_file: Path) -> Path:
        """Generate a CSV report."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Report Title', 'Generated At', 'Session ID', 'Review Tool',
                'Total Findings', 'Total Ground Truth', 'True Positives',
                'False Positives', 'False Negatives', 'Precision', 'Recall',
                'F1-Score', 'Accuracy'
            ])
            
            # Write summary row
            writer.writerow([
                self.config.report_title,
                datetime.now().isoformat(),
                result.session_id,
                result.review_tool,
                result.metrics.total_findings,
                result.metrics.total_ground_truth,
                result.metrics.true_positives,
                result.metrics.false_positives,
                result.metrics.false_negatives,
                f"{result.metrics.precision:.4f}",
                f"{result.metrics.recall:.4f}",
                f"{result.metrics.f1_score:.4f}",
                f"{result.metrics.accuracy:.4f}"
            ])
            
            # Write matches if requested
            if self.config.include_detailed_matches and result.matches:
                writer.writerow([])  # Empty row for separation
                writer.writerow([
                    'Match ID', 'Finding ID', 'Ground Truth ID', 'Match Strategy',
                    'Confidence', 'Overlap Score', 'File Path', 'Line Number'
                ])
                
                for match in result.matches:
                    writer.writerow([
                        match.finding.id,
                        match.finding.id,
                        match.ground_truth.id,
                        match.match_strategy.value,
                        f"{match.confidence:.4f}",
                        f"{match.overlap_score:.4f}",
                        match.finding.file_path,
                        match.finding.line_number
                    ])
        
        return output_file
    
    def _generate_text_report(self, result: EvaluationResult, output_file: Path) -> Path:
        """Generate a text report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append(f"{self.config.report_title}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Evaluation Session: {result.session_id}")
        report_lines.append(f"Review Tool: {result.review_tool}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Overall Performance: {self._get_performance_rating(result.metrics.f1_score)}")
        report_lines.append(f"F1-Score: {result.metrics.f1_score:.3f}")
        report_lines.append(f"Precision: {result.metrics.precision:.3f}")
        report_lines.append(f"Recall: {result.metrics.recall:.3f}")
        report_lines.append(f"Accuracy: {result.metrics.accuracy:.3f}")
        report_lines.append("")
        
        # Detailed Metrics
        report_lines.append("DETAILED METRICS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Review Findings: {result.metrics.total_findings}")
        report_lines.append(f"Total Ground Truth Items: {result.metrics.total_ground_truth}")
        report_lines.append(f"True Positives: {result.metrics.true_positives}")
        report_lines.append(f"False Positives: {result.metrics.false_positives}")
        report_lines.append(f"False Negatives: {result.metrics.false_negatives}")
        report_lines.append("")
        
        # Match Analysis
        report_lines.append("MATCH ANALYSIS")
        report_lines.append("-" * 40)
        match_breakdown = self._get_match_breakdown(result.matches)
        for strategy, count in match_breakdown.items():
            report_lines.append(f"{strategy}: {count} matches")
        report_lines.append("")
        
        # Performance Insights
        report_lines.append("PERFORMANCE INSIGHTS")
        report_lines.append("-" * 40)
        insights = self._generate_performance_insights(result)
        for insight in insights:
            report_lines.append(f"• {insight}")
        report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 40)
        recommendations = self._generate_recommendations(result)
        for rec in recommendations:
            report_lines.append(f"• {rec}")
        report_lines.append("")
        
        # Footer
        report_lines.append("=" * 80)
        report_lines.append("Report generated by ReviewLab Evaluation Engine")
        report_lines.append("=" * 80)
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        return output_file
    
    def _generate_html_report(self, result: EvaluationResult, output_file: Path) -> Path:
        """Generate an HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.report_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #6c757d; margin-top: 10px; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ color: #007bff; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; }}
        .insight {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .recommendation {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .performance-{self._get_performance_class(result.metrics.f1_score)} {{ color: {self._get_performance_color(result.metrics.f1_score)}; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.config.report_title}</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Session ID: {result.session_id} | Review Tool: {result.review_tool}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">Performance Overview</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value performance-{self._get_performance_class(result.metrics.f1_score)}">
                        {result.metrics.f1_score:.3f}
                    </div>
                    <div class="metric-label">F1-Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{result.metrics.precision:.3f}</div>
                    <div class="metric-label">Precision</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{result.metrics.recall:.3f}</div>
                    <div class="metric-label">Recall</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{result.metrics.accuracy:.3f}</div>
                    <div class="metric-label">Accuracy</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Detailed Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Findings</td><td>{result.metrics.total_findings}</td></tr>
                <tr><td>Total Ground Truth</td><td>{result.metrics.total_ground_truth}</td></tr>
                <tr><td>True Positives</td><td>{result.metrics.true_positives}</td></tr>
                <tr><td>False Positives</td><td>{result.metrics.false_positives}</td></tr>
                <tr><td>False Negatives</td><td>{result.metrics.false_negatives}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">Performance Insights</h2>
            {self._generate_html_insights(result)}
        </div>
        
        <div class="section">
            <h2 class="section-title">Recommendations</h2>
            {self._generate_html_recommendations(result)}
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_detailed_analysis(self, result: EvaluationResult) -> Dict[str, Any]:
        """Generate detailed analysis of the evaluation results."""
        analysis = {
            'performance_rating': self._get_performance_rating(result.metrics.f1_score),
            'strengths': self._identify_strengths(result),
            'weaknesses': self._identify_weaknesses(result),
            'match_breakdown': self._get_match_breakdown(result.matches),
            'file_analysis': self._analyze_file_performance(result),
            'severity_analysis': self._analyze_severity_performance(result)
        }
        
        return analysis
    
    def _get_performance_rating(self, f1_score: float) -> str:
        """Get a human-readable performance rating."""
        if f1_score >= 0.9:
            return "Excellent"
        elif f1_score >= 0.8:
            return "Very Good"
        elif f1_score >= 0.7:
            return "Good"
        elif f1_score >= 0.6:
            return "Fair"
        elif f1_score >= 0.5:
            return "Poor"
        else:
            return "Very Poor"
    
    def _get_performance_class(self, f1_score: float) -> str:
        """Get CSS class for performance styling."""
        if f1_score >= 0.8:
            return "excellent"
        elif f1_score >= 0.6:
            return "good"
        else:
            return "poor"
    
    def _get_performance_color(self, f1_score: float) -> str:
        """Get color for performance styling."""
        if f1_score >= 0.8:
            return "#28a745"
        elif f1_score >= 0.6:
            return "#ffc107"
        else:
            return "#dc3545"
    
    def _get_match_breakdown(self, matches: List[MatchResult]) -> Dict[str, int]:
        """Get breakdown of matches by strategy."""
        breakdown = {}
        for match in matches:
            strategy = match.match_strategy.value
            breakdown[strategy] = breakdown.get(strategy, 0) + 1
        return breakdown
    
    def _identify_strengths(self, result: EvaluationResult) -> List[str]:
        """Identify strengths in the evaluation results."""
        strengths = []
        
        if result.metrics.precision > 0.8:
            strengths.append("High precision indicates low false positive rate")
        if result.metrics.recall > 0.8:
            strengths.append("High recall indicates good coverage of ground truth")
        if result.metrics.f1_score > 0.8:
            strengths.append("Balanced precision and recall performance")
        if len(result.matches) > result.metrics.total_ground_truth * 0.7:
            strengths.append("Good match rate with ground truth data")
        
        return strengths
    
    def _identify_weaknesses(self, result: EvaluationResult) -> List[str]:
        """Identify weaknesses in the evaluation results."""
        weaknesses = []
        
        if result.metrics.precision < 0.6:
            weaknesses.append("Low precision indicates high false positive rate")
        if result.metrics.recall < 0.6:
            weaknesses.append("Low recall indicates poor coverage of ground truth")
        if result.metrics.f1_score < 0.6:
            weaknesses.append("Poor overall performance balance")
        if len(result.unmatched_findings) > result.metrics.total_findings * 0.5:
            weaknesses.append("High number of unmatched findings")
        
        return weaknesses
    
    def _analyze_file_performance(self, result: EvaluationResult) -> Dict[str, Any]:
        """Analyze performance by file."""
        file_stats = {}
        
        for match in result.matches:
            file_path = match.finding.file_path
            if file_path not in file_stats:
                file_stats[file_path] = {'matches': 0, 'total_findings': 0}
            file_stats[file_path]['matches'] += 1
        
        for finding in result.unmatched_findings:
            file_path = finding.file_path
            if file_path not in file_stats:
                file_stats[file_path] = {'matches': 0, 'total_findings': 0}
            file_stats[file_path]['total_findings'] += 1
        
        return file_stats
    
    def _analyze_severity_performance(self, result: EvaluationResult) -> Dict[str, Any]:
        """Analyze performance by severity level."""
        severity_stats = {}
        
        for match in result.matches:
            severity = match.finding.severity
            if severity not in severity_stats:
                severity_stats[severity] = {'matches': 0, 'total_findings': 0}
            severity_stats[severity]['matches'] += 1
        
        for finding in result.unmatched_findings:
            severity = finding.severity
            if severity not in severity_stats:
                severity_stats[severity] = {'matches': 0, 'total_findings': 0}
            severity_stats[severity]['total_findings'] += 1
        
        return severity_stats
    
    def _generate_performance_insights(self, result: EvaluationResult) -> List[str]:
        """Generate performance insights."""
        insights = []
        
        # Basic insights
        if result.metrics.precision > result.metrics.recall:
            insights.append("Higher precision than recall suggests the tool is conservative in its findings")
        elif result.metrics.recall > result.metrics.precision:
            insights.append("Higher recall than precision suggests the tool prioritizes coverage over accuracy")
        
        # Match strategy insights
        match_breakdown = self._get_match_breakdown(result.matches)
        if 'exact_overlap' in match_breakdown and match_breakdown['exact_overlap'] > 0:
            insights.append(f"Exact overlap matching found {match_breakdown['exact_overlap']} high-confidence matches")
        
        # Performance insights
        if result.metrics.f1_score > 0.8:
            insights.append("Excellent overall performance with balanced precision and recall")
        elif result.metrics.f1_score < 0.5:
            insights.append("Significant room for improvement in detection accuracy")
        
        return insights
    
    def _generate_recommendations(self, result: EvaluationResult) -> List[str]:
        """Generate recommendations for improvement."""
        recommendations = []
        
        if result.metrics.precision < 0.7:
            recommendations.append("Focus on reducing false positives by improving detection rules")
        
        if result.metrics.recall < 0.7:
            recommendations.append("Improve coverage by expanding detection patterns and rules")
        
        if len(result.unmatched_findings) > result.metrics.total_findings * 0.3:
            recommendations.append("Investigate unmatched findings to identify missed detection patterns")
        
        if len(result.unmatched_ground_truth) > result.metrics.total_ground_truth * 0.3:
            recommendations.append("Review ground truth data to ensure comprehensive coverage")
        
        return recommendations
    
    def _generate_html_insights(self, result: EvaluationResult) -> str:
        """Generate HTML for insights section."""
        insights = self._generate_performance_insights(result)
        html = ""
        for insight in insights:
            html += f'<div class="insight">{insight}</div>'
        return html
    
    def _generate_html_recommendations(self, result: EvaluationResult) -> str:
        """Generate HTML for recommendations section."""
        recommendations = self._generate_recommendations(result)
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        return html
