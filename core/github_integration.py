"""
GitHub Integration Module for ReviewLab.

Handles GitHub API operations including authentication, repository management,
and pull request creation for bug-injected code.
"""

import base64
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import click
from github import Github, GithubException
from github.Repository import Repository
from github.Branch import Branch
from github.PullRequest import PullRequest

from core.errors import RepositoryError, AuthenticationError


class GitHubConfig:
    """Configuration for GitHub integration."""

    def __init__(self, token: Optional[str] = None, username: Optional[str] = None):
        """Initialize GitHub configuration."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.username = username or os.getenv("GITHUB_USERNAME")
        
        if not self.token:
            raise AuthenticationError(
                "GitHub token not found. Set GITHUB_TOKEN environment variable "
                "or provide via --github-token option."
            )
        
        if not self.username:
            raise AuthenticationError(
                "GitHub username not found. Set GITHUB_USERNAME environment variable "
                "or provide via --github-username option."
            )


class GitHubManager:
    """Manages GitHub operations for ReviewLab."""

    def __init__(self, config: GitHubConfig):
        """Initialize GitHub manager."""
        self.config = config
        self.github = Github(config.token)
        self.user = self.github.get_user()
        
        # Verify authentication
        try:
            self.user.login
        except GithubException as e:
            raise AuthenticationError(f"Failed to authenticate with GitHub: {e}")

    def get_repository(self, repo_path: str) -> Repository:
        """Get a repository by path (owner/repo or full URL)."""
        try:
            if repo_path.startswith("https://github.com/"):
                # Extract owner/repo from URL
                parts = repo_path.rstrip("/").split("/")
                if len(parts) >= 5:
                    repo_path = f"{parts[-2]}/{parts[-1]}"
            
            return self.github.get_repo(repo_path)
        except GithubException as e:
            raise RepositoryError(f"Failed to get repository {repo_path}: {e}")

    def create_branch(self, repo: Repository, base_branch: str, new_branch: str) -> Branch:
        """Create a new branch from base branch."""
        try:
            # Get the base branch reference
            base_ref = repo.get_branch(base_branch)
            
            # Create new branch
            repo.create_git_ref(f"refs/heads/{new_branch}", base_ref.commit.sha)
            
            click.echo(f"✅ Created branch: {new_branch}")
            return repo.get_branch(new_branch)
            
        except GithubException as e:
            raise RepositoryError(f"Failed to create branch {new_branch}: {e}")

    def push_files(
        self,
        repo: Repository,
        branch: str,
        files: Dict[str, str],
        commit_message: str,
        base_tree: Optional[Any] = None
    ) -> str:
        """Push files to a GitHub branch using Git Data API."""
        try:
            # Get the branch reference
            branch_ref = repo.get_git_ref(f"heads/{branch}")
            
            # Create tree entries for all files
            tree_elements = []
            for file_path, content in files.items():
                click.echo(f"Creating blob for {file_path}...")
                
                # Create a blob for the file content first
                blob = repo.create_git_blob(content, "utf-8")
                click.echo(f"Created blob: {blob.sha}")
                
                # Reference the blob SHA in the tree (not the content)
                tree_elements.append({
                    "path": file_path,
                    "mode": "100644",  # Regular file
                    "type": "blob",
                    "sha": blob.sha  # Use blob SHA instead of content
                })
            
            click.echo(f"Creating Git tree with {len(tree_elements)} files...")
            
            # Create the new tree using direct HTTP requests to GitHub API
            try:
                click.echo(f"Attempting to create tree with {len(tree_elements)} elements via direct HTTP...")
                
                # Get the GitHub token from the repository object
                import requests
                import json
                
                # Extract token from PyGithub repository object
                token = repo._requester._Requester__auth.token
                owner, repo_name = repo.full_name.split('/')
                
                # Prepare the tree creation payload
                tree_data = {
                    "tree": tree_elements
                }
                if base_tree:
                    tree_data["base_tree"] = base_tree.sha
                
                # Make direct HTTP request to GitHub API
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
                
                url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees"
                
                click.echo(f"Making HTTP request to: {url}")
                response = requests.post(url, headers=headers, json=tree_data)
                
                if response.status_code == 201:
                    tree_response = response.json()
                    new_tree_sha = tree_response["sha"]
                    click.echo(f"Created Git tree via direct HTTP: {new_tree_sha}")
                    
                    # Create a mock tree object for compatibility
                    class MockTree:
                        def __init__(self, sha):
                            self.sha = sha
                    
                    new_tree = MockTree(new_tree_sha)
                else:
                    click.echo(f"HTTP request failed: {response.status_code}")
                    click.echo(f"Response: {response.text}")
                    raise RepositoryError(f"GitHub API returned status {response.status_code}: {response.text}")
                
            except Exception as e:
                click.echo(f"Direct HTTP tree creation failed: {e}")
                click.echo(f"Tree elements: {tree_elements}")
                raise RepositoryError(f"Failed to create Git tree via direct HTTP: {e}")
            
            # Create the commit using direct HTTP requests to GitHub API
            try:
                click.echo(f"Creating Git commit via direct HTTP...")
                
                # Prepare the commit creation payload
                commit_data = {
                    "message": commit_message,
                    "tree": new_tree.sha,
                    "parents": [branch_ref.commit.sha]
                }
                
                # Make direct HTTP request to GitHub API
                url = f"https://api.github.com/repos/{owner}/{repo_name}/git/commits"
                
                click.echo(f"Making HTTP request to: {url}")
                response = requests.post(url, headers=headers, json=commit_data)
                
                if response.status_code == 201:
                    commit_response = response.json()
                    commit_sha = commit_response["sha"]
                    click.echo(f"Created Git commit via direct HTTP: {commit_sha}")
                    
                    # Create a mock commit object for compatibility
                    class MockCommit:
                        def __init__(self, sha):
                            self.sha = sha
                    
                    commit = MockCommit(commit_sha)
                else:
                    click.echo(f"HTTP commit creation failed: {response.status_code}")
                    click.echo(f"Response: {response.text}")
                    raise RepositoryError(f"GitHub API returned status {response.status_code}: {response.text}")
                
            except Exception as e:
                click.echo(f"Direct HTTP commit creation failed: {e}")
                raise RepositoryError(f"Failed to create Git commit via direct HTTP: {e}")
            
            click.echo(f"Created Git commit: {commit.sha}")
            
            # Update the branch reference
            click.echo(f"Updating branch reference for {branch}...")
            repo.get_git_ref(f"heads/{branch}").edit(commit.sha)
            click.echo(f"Updated branch reference")
            
            # Add a small delay to ensure the branch is updated
            import time
            time.sleep(1)
            
            click.echo(f"Pushed {len(files)} files to branch {branch}")
            return commit.sha
            
        except Exception as e:
            raise RepositoryError(f"Failed to push files: {e}")

    def create_pull_request(
        self,
        repo: Repository,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        draft: bool = False
    ) -> PullRequest:
        """Create a pull request."""
        try:
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch,
                draft=draft
            )
            
            click.echo(f"✅ Created pull request: #{pr.number}")
            click.echo(f"🔗 URL: {pr.html_url}")
            
            return pr
            
        except GithubException as e:
            raise RepositoryError(f"Failed to create pull request: {e}")

    def get_pull_request(self, repo: Repository, pr_number: int) -> PullRequest:
        """Get a pull request by number."""
        try:
            return repo.get_pull(pr_number)
        except GithubException as e:
            raise RepositoryError(f"Failed to get pull request #{pr_number}: {e}")

    def list_pull_requests(
        self, 
        repo: Repository, 
        state: str = "open",
        base_branch: Optional[str] = None
    ) -> List[PullRequest]:
        """List pull requests in a repository."""
        try:
            prs = repo.get_pulls(state=state)
            if base_branch:
                prs = [pr for pr in prs if pr.base.ref == base_branch]
            return list(prs)
        except GithubException as e:
            raise RepositoryError(f"Failed to list pull requests: {e}")

    def close_pull_request(self, pr: PullRequest, merge: bool = False) -> None:
        """Close or merge a pull request."""
        try:
            if merge:
                pr.merge()
                click.echo(f"✅ Merged pull request #{pr.number}")
            else:
                pr.edit(state="closed")
                click.echo(f"✅ Closed pull request #{pr.number}")
        except GithubException as e:
            raise RepositoryError(f"Failed to close/merge pull request #{pr.number}: {e}")

    def get_repository_info(self, repo: Repository) -> Dict[str, str]:
        """Get basic repository information."""
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "owner": repo.owner.login,
            "url": repo.html_url,
            "default_branch": repo.default_branch,
            "description": repo.description or "No description",
            "language": repo.language or "Unknown",
            "stars": str(repo.stargazers_count),
            "forks": str(repo.forks_count),
            "open_issues": str(repo.open_issues_count)
        }

    def validate_repository_access(self, repo: Repository) -> bool:
        """Validate that we have write access to the repository."""
        try:
            # Try to get the repository permissions
            permissions = repo.permissions
            return permissions.push
        except GithubException:
            return False


class GitHubWorkflow:
    """High-level workflow for GitHub operations."""

    def __init__(self, github_manager: GitHubManager):
        """Initialize GitHub workflow."""
        self.github = github_manager

    def create_bug_injection_pr(
        self,
        repo_path: str,
        base_branch: str,
        bug_branch: str,
        files_to_update: Dict[str, str],
        pr_title: str,
        pr_body: str,
        draft: bool = False
    ) -> Tuple[Repository, PullRequest]:
        """Create a complete bug injection PR workflow."""
        try:
            # Get the repository
            repo = self.github.get_repository(repo_path)
            
            # Validate access
            if not self.github.validate_repository_access(repo):
                raise RepositoryError(
                    f"No write access to repository {repo_path}. "
                    "Make sure your token has push permissions."
                )
            
            click.echo(f"🔍 Working with repository: {repo.full_name}")
            
            # Create the bug injection branch
            self.github.create_branch(repo, base_branch, bug_branch)
            
            # Push the bug-injected files
            commit_sha = self.github.push_files(
                repo, bug_branch, files_to_update, pr_body
            )
            
            # Create the pull request
            pr = self.github.create_pull_request(
                repo, pr_title, pr_body, bug_branch, base_branch, draft
            )
            
            return repo, pr
            
        except Exception as e:
            raise RepositoryError(f"Failed to create bug injection PR: {e}")

    def cleanup_branch(self, repo: Repository, branch: str) -> None:
        """Clean up a branch after PR is closed/merged."""
        try:
            repo.get_git_ref(f"heads/{branch}").delete()
            click.echo(f"🗑️  Deleted branch: {branch}")
        except GithubException as e:
            click.echo(f"⚠️  Warning: Failed to delete branch {branch}: {e}")


def create_github_config_from_cli(
    token: Optional[str] = None,
    username: Optional[str] = None
) -> GitHubConfig:
    """Create GitHub config from CLI options or environment variables."""
    try:
        return GitHubConfig(token=token, username=username)
    except AuthenticationError as e:
        click.echo(f"❌ {e}")
        click.echo("\n💡 To set up GitHub integration:")
        click.echo("   1. Create a GitHub Personal Access Token")
        click.echo("   2. Set GITHUB_TOKEN environment variable")
        click.echo("   3. Set GITHUB_USERNAME environment variable")
        click.echo("   4. Or use --github-token and --github-username options")
        sys.exit(1)
