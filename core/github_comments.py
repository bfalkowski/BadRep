"""
GitHub Comment Extraction and Repository Management.

This module provides functionality to:
1. Extract comments from GitHub PRs
2. Convert comments to ReviewLab findings format
3. Manage repository operations and cleanup
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from github import Github, PullRequest, IssueComment
import requests

logger = logging.getLogger(__name__)


@dataclass
class Comment:
    """Represents a GitHub comment with metadata."""
    id: int
    author: str
    body: str
    created_at: datetime
    updated_at: datetime
    comment_type: str  # 'line', 'review', 'general'
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    commit_id: Optional[str] = None
    diff_hunk: Optional[str] = None
    position: Optional[int] = None


@dataclass
class ReviewFinding:
    """ReviewLab finding format for comments."""
    id: str
    file_path: Optional[str]
    line_number: Optional[int]
    message: str
    severity: str
    category: str
    confidence: float
    tool: str
    rule_id: Optional[str] = None
    details: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BranchStatus:
    """Status information about a GitHub branch."""
    name: str
    exists: bool
    last_commit: Optional[str] = None
    protection_enabled: bool = False
    is_default: bool = False


class GitHubCommentExtractor:
    """Extract and parse GitHub PR comments."""
    
    def __init__(self, github_token: str):
        """Initialize with GitHub token."""
        self.github = Github(github_token)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    def extract_pr_comments(self, owner: str, repo: str, pr_number: int) -> List[Comment]:
        """Extract all comments from a specific PR."""
        try:
            # Get the repository and PR
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            pr = repo_obj.get_pull(pr_number)
            
            comments = []
            
            # Get general PR comments
            for comment in pr.get_issue_comments():
                comments.append(Comment(
                    id=comment.id,
                    author=comment.user.login,
                    body=comment.body,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    comment_type='general'
                ))
            
            # Get review comments (line-specific)
            for comment in pr.get_review_comments():
                comments.append(Comment(
                    id=comment.id,
                    author=comment.user.login,
                    body=comment.body,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    comment_type='line',
                    file_path=comment.path,
                    line_number=comment.line,
                    commit_id=comment.commit_id,
                    diff_hunk=comment.diff_hunk,
                    position=comment.position
                ))
            
            # Get review summaries
            for review in pr.get_reviews():
                if review.body:  # Only add if there's actual content
                    comments.append(Comment(
                        id=review.id,
                        author=review.user.login,
                        body=review.body,
                        created_at=review.submitted_at,
                        updated_at=review.submitted_at,
                        comment_type='review'
                    ))
            
            logger.info(f"Extracted {len(comments)} comments from PR #{pr_number}")
            return comments
            
        except Exception as e:
            logger.error(f"Error extracting comments from PR #{pr_number}: {e}")
            raise
    
    def parse_comment_content(self, comment: Comment) -> ReviewFinding:
        """Convert a GitHub comment to a ReviewLab finding."""
        # Analyze comment content to determine category and severity
        category, severity, confidence = self._analyze_comment(comment.body)
        
        # Generate a unique ID
        finding_id = f"gh_comment_{comment.id}_{comment.comment_type}"
        
        # Extract rule ID if present (e.g., "PYT001", "BUG-123")
        rule_id = self._extract_rule_id(comment.body)
        
        return ReviewFinding(
            id=finding_id,
            file_path=comment.file_path,
            line_number=comment.line_number,
            message=comment.body[:200] + "..." if len(comment.body) > 200 else comment.body,
            severity=severity,
            category=category,
            confidence=confidence,
            tool="GitHub Review",
            rule_id=rule_id,
            details=comment.body,
            metadata={
                "github_comment_id": comment.id,
                "author": comment.author,
                "comment_type": comment.comment_type,
                "created_at": comment.created_at.isoformat(),
                "commit_id": comment.commit_id,
                "position": comment.position
            }
        )
    
    def map_comment_to_findings(self, comments: List[Comment]) -> List[ReviewFinding]:
        """Convert multiple GitHub comments to ReviewLab findings."""
        findings = []
        for comment in comments:
            try:
                finding = self.parse_comment_content(comment)
                findings.append(finding)
            except Exception as e:
                logger.warning(f"Failed to parse comment {comment.id}: {e}")
                continue
        
        logger.info(f"Converted {len(comments)} comments to {len(findings)} findings")
        return findings
    
    def categorize_comment(self, comment: Comment) -> str:
        """Categorize a comment based on its content."""
        body_lower = comment.body.lower()
        
        # Bug-related keywords
        bug_keywords = ['bug', 'error', 'issue', 'problem', 'fix', 'broken', 'fail', 'crash']
        if any(keyword in body_lower for keyword in bug_keywords):
            return 'Bug Detection'
        
        # Code quality keywords
        quality_keywords = ['style', 'format', 'naming', 'convention', 'best practice', 'clean code']
        if any(keyword in body_lower for keyword in quality_keywords):
            return 'Code Quality'
        
        # Security keywords
        security_keywords = ['security', 'vulnerability', 'exploit', 'injection', 'xss', 'sql']
        if any(keyword in body_lower for keyword in security_keywords):
            return 'Security'
        
        # Performance keywords
        perf_keywords = ['performance', 'slow', 'optimization', 'efficiency', 'memory', 'cpu']
        if any(keyword in body_lower for keyword in perf_keywords):
            return 'Performance'
        
        # Documentation keywords
        doc_keywords = ['document', 'comment', 'readme', 'api', 'usage']
        if any(keyword in body_lower for keyword in doc_keywords):
            return 'Documentation'
        
        return 'General Feedback'
    
    def _analyze_comment(self, body: str) -> Tuple[str, str, float]:
        """Analyze comment content to determine category, severity, and confidence."""
        category = self.categorize_comment(Comment(0, "", body, datetime.now(), datetime.now(), ""))
        
        # Determine severity based on language intensity
        body_lower = body.lower()
        if any(word in body_lower for word in ['critical', 'urgent', 'blocker', 'severe']):
            severity = 'Critical'
            confidence = 0.9
        elif any(word in body_lower for word in ['important', 'major', 'significant']):
            severity = 'High'
            confidence = 0.8
        elif any(word in body_lower for word in ['minor', 'suggestion', 'consider']):
            severity = 'Low'
            confidence = 0.6
        else:
            severity = 'Medium'
            confidence = 0.7
        
        return category, severity, confidence
    
    def _extract_rule_id(self, body: str) -> Optional[str]:
        """Extract rule ID from comment body if present."""
        import re
        
        # Look for common rule ID patterns
        patterns = [
            r'[A-Z]{2,4}\d{3,4}',  # PY001, ESL123, etc.
            r'[A-Z]+-\d+',          # BUG-123, SEC-456, etc.
            r'[A-Z]+\d+',           # PYTHON123, JAVA456, etc.
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                return match.group()
        
        return None


class GitHubRepositoryManager:
    """Manage GitHub repository operations and cleanup."""
    
    def __init__(self, github_token: str):
        """Initialize with GitHub token."""
        self.github = Github(github_token)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    def delete_branch(self, owner: str, repo: str, branch_name: str) -> bool:
        """Delete a branch from the repository."""
        try:
            # Use GitHub API to delete branch
            url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
            response = self.session.delete(url)
            
            if response.status_code == 204:
                logger.info(f"Successfully deleted branch '{branch_name}' from {owner}/{repo}")
                return True
            else:
                logger.error(f"Failed to delete branch '{branch_name}': {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting branch '{branch_name}': {e}")
            return False
    
    def cleanup_evaluation_branches(self, owner: str, repo: str, retention_days: int = 7) -> List[str]:
        """Clean up evaluation branches older than retention period."""
        try:
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_branches = []
            
            for branch in repo_obj.get_branches():
                # Skip default branch
                if branch.name == repo_obj.default_branch:
                    continue
                
                # Check if branch is an evaluation branch (starts with evaluation prefix)
                if branch.name.startswith('eval-') or branch.name.startswith('bug-injection-'):
                    # Get last commit date
                    last_commit = branch.commit.commit.author.date
                    if last_commit < cutoff_date:
                        if self.delete_branch(owner, repo, branch.name):
                            deleted_branches.append(branch.name)
            
            logger.info(f"Cleaned up {len(deleted_branches)} evaluation branches")
            return deleted_branches
            
        except Exception as e:
            logger.error(f"Error during branch cleanup: {e}")
            return []
    
    def archive_results_before_cleanup(self, session_id: str) -> str:
        """Archive evaluation results before cleanup."""
        # This would compress and move results to archive directory
        # For now, return the archive path
        archive_path = f"reports/archives/session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        logger.info(f"Archiving results to {archive_path}")
        return archive_path
    
    def get_branch_status(self, owner: str, repo: str, branch_name: str) -> BranchStatus:
        """Get status information about a specific branch."""
        try:
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            
            try:
                branch = repo_obj.get_branch(branch_name)
                return BranchStatus(
                    name=branch_name,
                    exists=True,
                    last_commit=branch.commit.sha,
                    protection_enabled=branch.protected,
                    is_default=(branch_name == repo_obj.default_branch)
                )
            except:
                return BranchStatus(
                    name=branch_name,
                    exists=False
                )
                
        except Exception as e:
            logger.error(f"Error getting branch status: {e}")
            return BranchStatus(
                name=branch_name,
                exists=False
            )


def extract_and_convert_comments(owner: str, repo: str, pr_number: int, github_token: str) -> List[ReviewFinding]:
    """Convenience function to extract and convert comments in one call."""
    extractor = GitHubCommentExtractor(github_token)
    comments = extractor.extract_pr_comments(owner, repo, pr_number)
    findings = extractor.map_comment_to_findings(comments)
    return findings


if __name__ == "__main__":
    # Example usage
    import os
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Please set GITHUB_TOKEN environment variable")
        exit(1)
    
    # Test with your repository
    owner = "bfalkowski"
    repo = "BadRep"
    pr_number = 1  # Update this to your actual PR number
    
    try:
        findings = extract_and_convert_comments(owner, repo, pr_number, github_token)
        print(f"Extracted {len(findings)} findings:")
        for finding in findings:
            print(f"- {finding.category}: {finding.message[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
