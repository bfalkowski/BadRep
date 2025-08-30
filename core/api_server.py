"""
ReviewLab FastAPI Server - Agentic System Foundation.

This module provides a comprehensive REST API for all ReviewLab operations,
enabling external tools and automated workflows to control the system.
"""

import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

# Import our core modules
from core.bug_injection import BugInjectionEngine
from core.github_integration import GitHubManager
from core.evaluation import EvaluationEngine
from core.github_comments import GitHubCommentExtractor, GitHubRepositoryManager
from core.models import BugTemplate, GroundTruthEntry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ReviewLab API",
    description="Agentic Code Review Evaluation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (in production, use dependency injection)
bug_engine = None
github_integration = None
evaluation_engine = None
github_extractor = None
repo_manager = None


# Import models from the models module
from core.models import (
    BugInjectionRequest, BugInjectionResponse,
    GitHubPRRequest, GitHubPRResponse,
    EvaluationRequest, EvaluationResponse,
    CommentExtractionRequest, CommentExtractionResponse,
    CleanupRequest, CleanupResponse,
    HealthResponse
)


# ============================================================================
# Dependency Injection and Initialization
# ============================================================================

def get_bug_engine() -> BugInjectionEngine:
    """Get or create bug injection engine instance."""
    global bug_engine
    if bug_engine is None:
        bug_engine = BugInjectionEngine()
    return bug_engine

def get_github_integration() -> GitHubManager:
    """Get or create GitHub integration instance."""
    global github_integration
    if github_integration is None:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")
        # Create a config object for GitHubManager
        from core.github_integration import GitHubConfig
        config = GitHubConfig(token=github_token)
        github_integration = GitHubManager(config)
    return github_integration

def get_evaluation_engine() -> EvaluationEngine:
    """Get or create evaluation engine instance."""
    global evaluation_engine
    if evaluation_engine is None:
        evaluation_engine = EvaluationEngine()
    return evaluation_engine

def get_github_extractor() -> GitHubCommentExtractor:
    """Get or create GitHub comment extractor instance."""
    global github_extractor
    if github_extractor is None:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")
        github_extractor = GitHubCommentExtractor(github_token)
    return github_extractor

def get_repo_manager() -> GitHubRepositoryManager:
    """Get or create repository manager instance."""
    global repo_manager
    if repo_manager is None:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")
        repo_manager = GitHubRepositoryManager(github_token)
    return repo_manager


# ============================================================================
# Health and Status Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health information."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        components={
            "bug_injection": "available",
            "github_integration": "available" if os.getenv('GITHUB_TOKEN') else "unconfigured",
            "evaluation_engine": "available",
            "comment_extraction": "available" if os.getenv('GITHUB_TOKEN') else "unconfigured"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return await root()

@app.get("/status")
async def status():
    """Detailed system status."""
    return {
        "system": "ReviewLab API Server",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "bug_injection": "/api/v1/inject/*",
            "github_integration": "/api/v1/github/*",
            "evaluation": "/api/v1/evaluate/*",
            "learning": "/api/v1/learning/*",
            "cleanup": "/api/v1/cleanup/*"
        }
    }


# ============================================================================
# Bug Injection Endpoints
# ============================================================================

@app.post("/api/v1/inject/bugs", response_model=BugInjectionResponse)
async def inject_bugs(
    request: BugInjectionRequest,
    background_tasks: BackgroundTasks,
    bug_engine: BugInjectionEngine = Depends(get_bug_engine)
):
    """Inject bugs into a project."""
    try:
        logger.info(f"Injecting bugs: {request.template_ids} into {request.project_path}")
        
        # Perform bug injection
        injected_bugs = bug_engine.inject_bugs(
            template_ids=request.template_ids,
            project_path=request.project_path,
            language=request.language,
            max_bugs=request.max_bugs,
            dry_run=request.dry_run
        )
        
        # Generate session ID
        session_id = f"inject_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store results (in production, use database)
        results = {
            "session_id": session_id,
            "injected_bugs": injected_bugs,
            "total_bugs": len(injected_bugs),
            "project_path": request.project_path,
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        # Save to file for now
        output_file = f"reports/injection_sessions/{session_id}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, default=str, indent=2)
        
        return BugInjectionResponse(
            session_id=session_id,
            injected_bugs=injected_bugs,
            total_bugs=len(injected_bugs),
            project_path=request.project_path,
            timestamp=datetime.now(),
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Bug injection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/inject/sessions/{session_id}")
async def get_injection_session(session_id: str):
    """Get details of a bug injection session."""
    try:
        session_file = f"reports/injection_sessions/{session_id}.json"
        if not os.path.exists(session_file):
            raise HTTPException(status_code=404, detail="Session not found")
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        return session_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/inject/sessions/{session_id}")
async def delete_injection_session(session_id: str):
    """Delete a bug injection session."""
    try:
        session_file = f"reports/injection_sessions/{session_id}.json"
        if not os.path.exists(session_file):
            raise HTTPException(status_code=404, detail="Session not found")
        
        os.remove(session_file)
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GitHub Integration Endpoints
# ============================================================================

@app.post("/api/v1/github/prs/{owner}/{repo}/{pr_number}/create", response_model=GitHubPRResponse)
async def create_github_pr(
    owner: str,
    repo: str,
    pr_number: int,
    request: GitHubPRRequest,
    github_integration: GitHubManager = Depends(get_github_integration)
):
    """Create a GitHub pull request."""
    try:
        logger.info(f"Creating PR for {owner}/{repo} branch {request.branch_name}")
        
        # This would integrate with your existing PR creation workflow
        # For now, return a mock response
        return GitHubPRResponse(
            pr_url=f"https://github.com/{owner}/{repo}/pull/{pr_number}",
            pr_number=pr_number,
            branch_name=request.branch_name,
            status="created",
            message="PR creation endpoint - integrate with existing workflow"
        )
        
    except Exception as e:
        logger.error(f"PR creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/github/prs/{owner}/{repo}/{pr_number}")
async def get_github_pr(
    owner: str,
    repo: str,
    pr_number: int,
    github_extractor: GitHubCommentExtractor = Depends(get_github_extractor)
):
    """Get information about a GitHub PR."""
    try:
        # Get PR comments
        comments = github_extractor.extract_pr_comments(owner, repo, pr_number)
        
        return {
            "pr_number": pr_number,
            "owner": owner,
            "repo": repo,
            "total_comments": len(comments),
            "comments": [
                {
                    "id": c.id,
                    "author": c.author,
                    "body": c.body,
                    "type": c.comment_type,
                    "file_path": c.file_path,
                    "line_number": c.line_number
                }
                for c in comments
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get PR {pr_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/github/prs/{owner}/{repo}/{pr_number}/comments")
async def get_pr_comments(
    owner: str,
    repo: str,
    pr_number: int,
    github_extractor: GitHubCommentExtractor = Depends(get_github_extractor)
):
    """Extract and convert PR comments to findings."""
    try:
        logger.info(f"Extracting comments from PR #{pr_number}")
        
        # Extract comments
        comments = github_extractor.extract_pr_comments(owner, repo, pr_number)
        
        # Convert to findings
        findings = github_extractor.map_comment_to_findings(comments)
        
        # Categorize comments
        categories = {}
        for finding in findings:
            cat = finding.category
            categories[cat] = categories.get(cat, 0) + 1
        
        return CommentExtractionResponse(
            pr_number=pr_number,
            total_comments=len(comments),
            findings=[finding.__dict__ for finding in findings],
            categories=categories,
            extraction_timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Comment extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Evaluation Endpoints
# ============================================================================

@app.post("/api/v1/evaluate/findings", response_model=EvaluationResponse)
async def evaluate_findings(
    request: EvaluationRequest,
    evaluation_engine: EvaluationEngine = Depends(get_evaluation_engine)
):
    """Evaluate findings against ground truth."""
    try:
        logger.info(f"Evaluating findings: {request.findings_file}")
        
        # Load review findings
        with open(request.findings_file, "r") as f:
            findings_data = json.load(f)

        # Convert to ReviewFinding objects
        from core.evaluation import FindingType, MatchStrategy, ReviewFinding
        review_findings = []
        for finding_data in findings_data:
            finding = ReviewFinding(
                id=finding_data.get("id", f"finding_{len(review_findings)}"),
                file_path=finding_data["file_path"],
                line_number=finding_data["line_number"],
                end_line=finding_data.get("end_line"),
                finding_type=FindingType(finding_data.get("finding_type", "bug")),
                severity=finding_data.get("severity", "medium"),
                confidence=finding_data.get("confidence", 0.8),
                message=finding_data.get("message", ""),
                rule_id=finding_data.get("rule_id"),
                category=finding_data.get("category"),
                metadata=finding_data.get("metadata", {}),
            )
            review_findings.append(finding)

        # Load ground truth
        ground_truth_entries = []
        with open(request.ground_truth_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data = json.loads(line)
                        entry = GroundTruthEntry(**data)
                        ground_truth_entries.append(entry)
                    except Exception as e:
                        logger.warning(f"Failed to parse line {line_num}: {e}")
                        continue

        # Convert strategy names to enum values
        strategy_enums = []
        for strategy_name in request.strategies or ["exact_overlap", "line_range_overlap", "semantic_similarity"]:
            try:
                strategy_enums.append(MatchStrategy(strategy_name))
            except ValueError:
                logger.warning(f"Unknown strategy '{strategy_name}', skipping")

        if not strategy_enums:
            strategy_enums = [
                MatchStrategy.EXACT_OVERLAP,
                MatchStrategy.LINE_RANGE_OVERLAP,
                MatchStrategy.SEMANTIC_SIMILARITY,
            ]

        # Run evaluation
        evaluation_result = evaluation_engine.evaluate_review(
            review_findings=review_findings,
            ground_truth_entries=ground_truth_entries,
            review_tool="API",
            strategies=strategy_enums,
        )
        
        # Extract metrics from results
        metrics = evaluation_result.metrics
        
        return EvaluationResponse(
            session_id=evaluation_result.session_id,
            precision=metrics.precision,
            recall=metrics.recall,
            f1_score=metrics.f1_score,
            accuracy=metrics.accuracy,
            total_findings=metrics.total_findings,
            true_positives=metrics.true_positives,
            false_positives=metrics.false_positives,
            false_negatives=metrics.false_negatives,
            report_paths=[f"evaluation_report_{evaluation_result.session_id}.json"]
        )
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/evaluate/reports/{session_id}")
async def get_evaluation_report(session_id: str):
    """Get evaluation report for a session."""
    try:
        # Look for evaluation reports
        report_dir = f"reports/evaluation_results"
        if not os.path.exists(report_dir):
            raise HTTPException(status_code=404, detail="No evaluation reports found")
        
        # Find files matching the session ID
        matching_files = []
        for file in os.listdir(report_dir):
            if session_id in file:
                matching_files.append(file)
        
        if not matching_files:
            raise HTTPException(status_code=404, detail=f"No reports found for session {session_id}")
        
        # Return the first matching report (JSON format)
        json_report = None
        for file in matching_files:
            if file.endswith('.json'):
                json_report = file
                break
        
        if json_report:
            report_path = os.path.join(report_dir, json_report)
            with open(report_path, 'r') as f:
                return json.load(f)
        else:
            return {"message": f"Reports found: {matching_files}", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evaluation report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Cleanup Endpoints
# ============================================================================

@app.post("/api/v1/cleanup/repository/{owner}/{repo}", response_model=CleanupResponse)
async def cleanup_repository(
    owner: str,
    repo: str,
    request: CleanupRequest,
    repo_manager: GitHubRepositoryManager = Depends(get_repo_manager)
):
    """Clean up evaluation branches in a repository."""
    try:
        logger.info(f"Cleaning up repository {owner}/{repo}")
        
        # Perform cleanup
        deleted_branches = repo_manager.cleanup_evaluation_branches(
            owner=owner,
            repo=repo,
            retention_days=request.retention_days
        )
        
        return CleanupResponse(
            deleted_branches=deleted_branches,
            total_deleted=len(deleted_branches),
            retention_days=request.retention_days,
            cleanup_timestamp=datetime.now(),
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/cleanup/branches/{owner}/{repo}/{branch_name}")
async def delete_branch(
    owner: str,
    repo: str,
    branch_name: str,
    repo_manager: GitHubRepositoryManager = Depends(get_repo_manager)
):
    """Delete a specific branch."""
    try:
        logger.info(f"Deleting branch {branch_name} from {owner}/{repo}")
        
        success = repo_manager.delete_branch(owner, repo, branch_name)
        
        if success:
            return {"message": f"Branch {branch_name} deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to delete branch {branch_name}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Branch deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Learning Endpoints (Foundation)
# ============================================================================

@app.post("/api/v1/learning/analyze-session/{session_id}")
async def analyze_session_for_learning(session_id: str):
    """Analyze an evaluation session for learning patterns."""
    try:
        # This is a foundation endpoint - will be expanded in Phase 11.5
        return {
            "message": "Learning analysis endpoint - will be implemented in Phase 11.5",
            "session_id": session_id,
            "status": "foundation_ready"
        }
        
    except Exception as e:
        logger.error(f"Learning analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Application Entry Point
# ============================================================================

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("reports/injection_sessions", exist_ok=True)
    os.makedirs("reports/evaluation_results", exist_ok=True)
    
    # Start the server
    uvicorn.run(
        "core.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
