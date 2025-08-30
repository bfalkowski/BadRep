"""
Data models for ReviewLab API.

This module contains Pydantic models and data structures used throughout the API.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field


# ============================================================================
# Core Data Models
# ============================================================================

class BugTemplate(BaseModel):
    """Bug template model for injection."""
    id: str
    name: str
    description: str
    language: str
    bug_type: str
    severity: str
    difficulty: str
    patterns: List[str]
    tags: List[str]
    template_code: str
    replacement_code: str
    metadata: Optional[Dict[str, Any]] = None


class GroundTruthEntry(BaseModel):
    """Ground truth entry for evaluation."""
    id: str
    injection_id: str
    template_id: str
    project_path: str
    language: str
    file_path: str
    line_number: int
    bug_type: str
    description: str
    severity: str
    difficulty: str
    injection_timestamp: datetime
    original_code: str
    modified_code: str
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# API Request/Response Models
# ============================================================================

class BugInjectionRequest(BaseModel):
    """Request model for bug injection."""
    template_ids: List[str] = Field(..., description="List of bug template IDs to inject")
    project_path: str = Field(..., description="Path to the project for bug injection")
    language: Optional[str] = Field(None, description="Target programming language")
    max_bugs: Optional[int] = Field(10, description="Maximum number of bugs to inject")
    dry_run: Optional[bool] = Field(False, description="Simulate injection without making changes")


class BugInjectionResponse(BaseModel):
    """Response model for bug injection."""
    session_id: str
    injected_bugs: List[Dict[str, Any]]
    total_bugs: int
    project_path: str
    timestamp: datetime
    status: str


class GitHubPRRequest(BaseModel):
    """Request model for GitHub PR operations."""
    owner: str = Field(..., description="GitHub repository owner")
    repo: str = Field(..., description="GitHub repository name")
    branch_name: str = Field(..., description="Branch name for the PR")
    title: Optional[str] = Field(None, description="PR title")
    description: Optional[str] = Field(None, description="PR description")


class GitHubPRResponse(BaseModel):
    """Response model for GitHub PR operations."""
    pr_url: str
    pr_number: int
    branch_name: str
    status: str
    message: str


class EvaluationRequest(BaseModel):
    """Request model for evaluation."""
    findings_file: str = Field(..., description="Path to findings file")
    ground_truth_file: str = Field(..., description="Path to ground truth file")
    output_dir: Optional[str] = Field(None, description="Output directory for reports")
    strategies: Optional[List[str]] = Field(None, description="Matching strategies to use")


class EvaluationResponse(BaseModel):
    """Response model for evaluation."""
    session_id: str
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    total_findings: int
    true_positives: int
    false_positives: int
    false_negatives: int
    report_paths: List[str]


class CommentExtractionRequest(BaseModel):
    """Request model for GitHub comment extraction."""
    owner: str = Field(..., description="GitHub repository owner")
    repo: str = Field(..., description="GitHub repository name")
    pr_number: int = Field(..., description="Pull request number")


class CommentExtractionResponse(BaseModel):
    """Response model for GitHub comment extraction."""
    pr_number: int
    total_comments: int
    findings: List[Dict[str, Any]]
    categories: Dict[str, int]
    extraction_timestamp: datetime


class CleanupRequest(BaseModel):
    """Request model for repository cleanup."""
    retention_days: Optional[int] = Field(7, description="Days to retain branches")
    dry_run: Optional[bool] = Field(False, description="Simulate cleanup without deletion")


class CleanupResponse(BaseModel):
    """Response model for repository cleanup."""
    deleted_branches: List[str]
    total_deleted: int
    retention_days: int
    cleanup_timestamp: datetime
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]


# ============================================================================
# Utility Models
# ============================================================================

class APIError(BaseModel):
    """Standard API error response."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationInfo(BaseModel):
    """Pagination information for list endpoints."""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class ListResponse(BaseModel):
    """Generic list response with pagination."""
    items: List[Any]
    pagination: PaginationInfo
    total: int
