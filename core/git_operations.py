"""
Git Operations for ReviewLab.

This module provides Git integration capabilities for bug injection workflows,
including branching, committing, pushing, and pull request management.
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.errors import GitError, InjectionError


@dataclass
class GitConfig:
    """Configuration for Git operations."""

    remote_name: str = "origin"
    base_branch: str = "main"
    branch_prefix: str = "bug-injection"
    commit_prefix: str = "feat: Inject bug"
    pr_title_prefix: str = "Bug Injection:"
    pr_body_template: str = "Automated bug injection for testing purposes"

    def __post_init__(self):
        """Validate configuration."""
        if not self.branch_prefix or not self.commit_prefix:
            raise ValueError("Branch and commit prefixes cannot be empty")


@dataclass
class BranchInfo:
    """Information about a Git branch."""

    name: str
    exists: bool
    is_current: bool
    last_commit: Optional[str] = None
    ahead_count: int = 0
    behind_count: int = 0


@dataclass
class CommitInfo:
    """Information about a Git commit."""

    hash: str
    author: str
    date: str
    message: str
    files_changed: List[str] = field(default_factory=list)


@dataclass
class PullRequestInfo:
    """Information about a pull request."""

    id: str
    title: str
    body: str
    state: str
    url: str
    created_at: str
    updated_at: str
    mergeable: Optional[bool] = None


class GitOperations:
    """Handles Git operations for bug injection workflows."""

    def __init__(self, repo_path: Path, config: Optional[GitConfig] = None):
        self.repo_path = Path(repo_path)
        self.config = config or GitConfig()
        self._validate_git_repo()

    def _validate_git_repo(self):
        """Validate that the path is a Git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists() or not git_dir.is_dir():
            raise GitError(f"Not a Git repository: {self.repo_path}")

    def _run_git_command(
        self, command: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a Git command and return the result."""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=60,
            )
            return result
        except subprocess.TimeoutExpired:
            raise GitError(f"Git command timed out: {' '.join(command)}")
        except Exception as e:
            raise GitError(f"Failed to run Git command: {e}")

    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        result = self._run_git_command(["branch", "--show-current"])
        if result.returncode != 0:
            raise GitError(f"Failed to get current branch: {result.stderr}")
        return result.stdout.strip()

    def get_branch_info(self, branch_name: str) -> BranchInfo:
        """Get information about a specific branch."""
        # Check if branch exists
        result = self._run_git_command(["branch", "--list", branch_name])
        exists = bool(result.stdout.strip())

        # Check if it's the current branch
        current_branch = self.get_current_branch()
        is_current = branch_name == current_branch

        # Get additional info if branch exists
        last_commit = None
        ahead_count = 0
        behind_count = 0

        if exists:
            # Get last commit
            result = self._run_git_command(["log", "-1", "--format=%H", branch_name])
            if result.returncode == 0:
                last_commit = result.stdout.strip()

            # Get ahead/behind counts
            result = self._run_git_command(
                ["rev-list", "--count", f"{self.config.base_branch}..{branch_name}"]
            )
            if result.returncode == 0:
                ahead_count = int(result.stdout.strip())

            result = self._run_git_command(
                ["rev-list", "--count", f"{branch_name}..{self.config.base_branch}"]
            )
            if result.returncode == 0:
                behind_count = int(result.stdout.strip())

        return BranchInfo(
            name=branch_name,
            exists=exists,
            is_current=is_current,
            last_commit=last_commit,
            ahead_count=ahead_count,
            behind_count=behind_count,
        )

    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> str:
        """Create a new branch from the specified base branch."""
        base = base_branch or self.config.base_branch

        # Check if base branch exists
        base_info = self.get_branch_info(base)
        if not base_info.exists:
            raise GitError(f"Base branch does not exist: {base}")

        # Check if target branch already exists
        target_info = self.get_branch_info(branch_name)
        if target_info.exists:
            raise GitError(f"Branch already exists: {branch_name}")

        # Create and checkout the new branch
        result = self._run_git_command(["checkout", "-b", branch_name, base])
        if result.returncode != 0:
            raise GitError(f"Failed to create branch: {result.stderr}")

        return branch_name

    def create_injection_branch(self, injection_id: str, language: str) -> str:
        """Create a branch for bug injection."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"{self.config.branch_prefix}/{language}-{injection_id}-{timestamp}"

        return self.create_branch(branch_name)

    def stage_files(self, file_paths: List[str]) -> bool:
        """Stage specific files for commit."""
        if not file_paths:
            return True

        result = self._run_git_command(["add"] + file_paths)
        return result.returncode == 0

    def stage_all_changes(self) -> bool:
        """Stage all changes in the repository."""
        result = self._run_git_command(["add", "."])
        return result.returncode == 0

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> str:
        """Commit staged changes with the given message."""
        # Stage files if specified
        if files:
            if not self.stage_files(files):
                raise GitError("Failed to stage files for commit")

        # Commit the changes
        result = self._run_git_command(["commit", "-m", message])
        if result.returncode != 0:
            raise GitError(f"Failed to commit changes: {result.stderr}")

        # Get the commit hash
        result = self._run_git_command(["rev-parse", "HEAD"])
        if result.returncode != 0:
            raise GitError("Failed to get commit hash")

        return result.stdout.strip()

    def commit_injection(self, injection_id: str, bug_type: str, files_modified: List[str]) -> str:
        """Commit bug injection changes."""
        message = f"{self.config.commit_prefix} {bug_type} ({injection_id})"
        return self.commit_changes(message, files_modified)

    def push_branch(self, branch_name: str, force: bool = False) -> bool:
        """Push a branch to the remote repository."""
        command = ["push", self.config.remote_name, branch_name]
        if force:
            command.append("--force")

        result = self._run_git_command(command)
        return result.returncode == 0

    def get_remote_url(self) -> Optional[str]:
        """Get the remote repository URL."""
        result = self._run_git_command(["remote", "get-url", self.config.remote_name])
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    def get_commit_info(self, commit_hash: str) -> CommitInfo:
        """Get information about a specific commit."""
        result = self._run_git_command(
            ["show", "--format=%H%n%an%n%ad%n%s", "--name-only", commit_hash]
        )

        if result.returncode != 0:
            raise GitError(f"Failed to get commit info: {result.stderr}")

        lines = result.stdout.strip().split("\n")
        if len(lines) < 4:
            raise GitError("Invalid commit info format")

        # Parse commit information
        hash_line = lines[0]
        author = lines[1]
        date = lines[2]
        message = lines[3]

        # Parse files changed (everything after the first empty line)
        files_changed = []
        for line in lines[4:]:
            if line.strip():
                files_changed.append(line.strip())

        return CommitInfo(
            hash=hash_line, author=author, date=date, message=message, files_changed=files_changed
        )

    def get_recent_commits(self, count: int = 10) -> List[CommitInfo]:
        """Get recent commits from the current branch."""
        result = self._run_git_command(
            ["log", f"-{count}", "--format=%H%n%an%n%ad%n%s", "--name-only"]
        )

        if result.returncode != 0:
            raise GitError(f"Failed to get recent commits: {result.stderr}")

        commits = []
        lines = result.stdout.strip().split("\n")

        i = 0
        while i < len(lines):
            if i + 4 >= len(lines):
                break

            hash_line = lines[i]
            author = lines[i + 1]
            date = lines[i + 2]
            message = lines[i + 3]

            # Find files changed
            files_changed = []
            j = i + 4
            while j < len(lines) and lines[j].strip():
                files_changed.append(lines[j].strip())
                j += 1

            commits.append(
                CommitInfo(
                    hash=hash_line,
                    author=author,
                    date=date,
                    message=message,
                    files_changed=files_changed,
                )
            )

            i = j + 1

        return commits

    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout a specific branch."""
        result = self._run_git_command(["checkout", branch_name])
        return result.returncode == 0

    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """Delete a local branch."""
        if branch_name == self.get_current_branch():
            raise GitError("Cannot delete current branch")

        command = ["branch", "-d"]
        if force:
            command.append("-D")
        command.append(branch_name)

        result = self._run_git_command(command)
        return result.returncode == 0

    def get_status(self) -> Dict[str, Any]:
        """Get the current Git status."""
        result = self._run_git_command(["status", "--porcelain"])
        if result.returncode != 0:
            raise GitError(f"Failed to get status: {result.stderr}")

        status_lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Parse status
        staged = []
        unstaged = []
        untracked = []

        for line in status_lines:
            if not line.strip():
                continue

            status_code = line[:2]
            filename = line[3:]

            if status_code == "??":
                untracked.append(filename)
            elif status_code[0] != " ":
                staged.append(filename)
            elif status_code[1] != " ":
                unstaged.append(filename)

        return {
            "current_branch": self.get_current_branch(),
            "staged_files": staged,
            "unstaged_files": unstaged,
            "untracked_files": untracked,
            "clean": len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0,
        }

    def reset_to_commit(self, commit_hash: str, hard: bool = False) -> bool:
        """Reset the current branch to a specific commit."""
        command = ["reset"]
        if hard:
            command.append("--hard")
        command.append(commit_hash)

        result = self._run_git_command(command)
        return result.returncode == 0

    def create_stash(self, message: Optional[str] = None) -> bool:
        """Create a stash of current changes."""
        command = ["stash", "push"]
        if message:
            command.extend(["-m", message])

        result = self._run_git_command(command)
        return result.returncode == 0

    def apply_stash(self, stash_name: str = "stash@{0}") -> bool:
        """Apply a stash."""
        result = self._run_git_command(["stash", "apply", stash_name])
        return result.returncode == 0

    def get_diff(self, file_path: Optional[str] = None) -> str:
        """Get the diff of staged changes."""
        command = ["diff", "--cached"]
        if file_path:
            command.append(file_path)

        result = self._run_git_command(command)
        if result.returncode != 0:
            return ""

        return result.stdout


class GitHubIntegration:
    """Handles GitHub-specific operations for pull requests."""

    def __init__(self, repo_path: Path, token: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.token = token
        self._validate_github_repo()

    def _validate_github_repo(self):
        """Validate that this is a GitHub repository."""
        git_ops = GitOperations(self.repo_path)
        remote_url = git_ops.get_remote_url()

        if not remote_url or "github.com" not in remote_url:
            raise GitError("Not a GitHub repository")

    def create_pull_request(
        self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> PullRequestInfo:
        """Create a pull request using GitHub CLI."""
        if not self._check_gh_cli():
            raise GitError("GitHub CLI (gh) not installed")

        # Create PR using gh CLI
        command = [
            "gh",
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--head",
            head_branch,
            "--base",
            base_branch,
        ]

        try:
            result = subprocess.run(
                command, cwd=self.repo_path, capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                raise GitError(f"Failed to create PR: {result.stderr}")

            # Parse the output to get PR URL
            output = result.stdout.strip()
            pr_url_match = re.search(r"https://github\.com/[^/]+/[^/]+/pull/\d+", output)

            if not pr_url_match:
                raise GitError("Failed to parse PR URL from output")

            pr_url = pr_url_match.group(0)
            pr_id = pr_url.split("/")[-1]

            # Get PR details
            pr_info = self.get_pull_request(pr_id)
            return pr_info

        except subprocess.TimeoutExpired:
            raise GitError("GitHub CLI command timed out")
        except Exception as e:
            raise GitError(f"Failed to create pull request: {e}")

    def get_pull_request(self, pr_id: str) -> PullRequestInfo:
        """Get information about a pull request."""
        if not self._check_gh_cli():
            raise GitError("GitHub CLI (gh) not installed")

        command = [
            "gh",
            "pr",
            "view",
            pr_id,
            "--json",
            "id,title,body,state,url,createdAt,updatedAt,mergeable",
        ]

        try:
            result = subprocess.run(
                command, cwd=self.repo_path, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                raise GitError(f"Failed to get PR info: {result.stderr}")

            pr_data = json.loads(result.stdout)

            return PullRequestInfo(
                id=str(pr_data["id"]),
                title=pr_data["title"],
                body=pr_data["body"] or "",
                state=pr_data["state"],
                url=pr_data["url"],
                created_at=pr_data["createdAt"],
                updated_at=pr_data["updatedAt"],
                mergeable=pr_data.get("mergeable"),
            )

        except json.JSONDecodeError:
            raise GitError("Failed to parse PR JSON response")
        except Exception as e:
            raise GitError(f"Failed to get pull request: {e}")

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed."""
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False


class GitLabIntegration:
    """Handles GitLab-specific operations for merge requests."""

    def __init__(self, repo_path: Path, token: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.token = token
        self._validate_gitlab_repo()

    def _validate_gitlab_repo(self):
        """Validate that this is a GitLab repository."""
        git_ops = GitOperations(self.repo_path)
        remote_url = git_ops.get_remote_url()

        if not remote_url or "gitlab.com" not in remote_url:
            raise GitError("Not a GitLab repository")

    def create_merge_request(
        self, title: str, description: str, source_branch: str, target_branch: str = "main"
    ) -> Dict[str, Any]:
        """Create a merge request using GitLab API."""
        # This would require GitLab API integration
        # For now, return a placeholder
        raise GitError("GitLab integration not yet implemented")
