"""
Unit tests for Git operations module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.git_operations import (
    GitConfig, BranchInfo, CommitInfo, PullRequestInfo,
    GitOperations, GitHubIntegration, GitLabIntegration
)
from core.errors import GitError


class TestGitConfig:
    """Test the GitConfig class."""
    
    def test_git_config_creation(self):
        """Test creating a GitConfig instance."""
        config = GitConfig(
            remote_name="upstream",
            base_branch="develop",
            branch_prefix="feature",
            commit_prefix="feat: Add"
        )
        
        assert config.remote_name == "upstream"
        assert config.base_branch == "develop"
        assert config.branch_prefix == "feature"
        assert config.commit_prefix == "feat: Add"
    
    def test_git_config_validation(self):
        """Test GitConfig validation."""
        with pytest.raises(ValueError):
            GitConfig(branch_prefix="")
        
        with pytest.raises(ValueError):
            GitConfig(commit_prefix="")


class TestBranchInfo:
    """Test the BranchInfo class."""
    
    def test_branch_info_creation(self):
        """Test creating a BranchInfo instance."""
        branch_info = BranchInfo(
            name="feature/test",
            exists=True,
            is_current=False,
            last_commit="abc123",
            ahead_count=2,
            behind_count=1
        )
        
        assert branch_info.name == "feature/test"
        assert branch_info.exists is True
        assert branch_info.is_current is False
        assert branch_info.last_commit == "abc123"
        assert branch_info.ahead_count == 2
        assert branch_info.behind_count == 1


class TestCommitInfo:
    """Test the CommitInfo class."""
    
    def test_commit_info_creation(self):
        """Test creating a CommitInfo instance."""
        commit_info = CommitInfo(
            hash="abc123",
            author="Test User",
            date="2024-01-01",
            message="Test commit",
            files_changed=["file1.txt", "file2.txt"]
        )
        
        assert commit_info.hash == "abc123"
        assert commit_info.author == "Test User"
        assert commit_info.date == "2024-01-01"
        assert commit_info.message == "Test commit"
        assert commit_info.files_changed == ["file1.txt", "file2.txt"]


class TestPullRequestInfo:
    """Test the PullRequestInfo class."""
    
    def test_pull_request_info_creation(self):
        """Test creating a PullRequestInfo instance."""
        pr_info = PullRequestInfo(
            id="123",
            title="Test PR",
            body="Test description",
            state="open",
            url="https://github.com/test/pr/123",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            mergeable=True
        )
        
        assert pr_info.id == "123"
        assert pr_info.title == "Test PR"
        assert pr_info.body == "Test description"
        assert pr_info.state == "open"
        assert pr_info.url == "https://github.com/test/pr/123"
        assert pr_info.mergeable is True


class TestGitOperations:
    """Test the GitOperations class."""
    
    def test_git_operations_creation_invalid_path(self):
        """Test creating GitOperations with invalid path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory that's not a git repo
            non_git_dir = Path(temp_dir) / "not_git"
            non_git_dir.mkdir()
            
            with pytest.raises(GitError):
                GitOperations(non_git_dir)
    
    @patch('subprocess.run')
    def test_get_current_branch_success(self, mock_run):
        """Test successfully getting current branch."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            git_ops = GitOperations(temp_dir)
            branch = git_ops.get_current_branch()
            
            assert branch == "main"
    
    @patch('subprocess.run')
    def test_get_current_branch_failure(self, mock_run):
        """Test getting current branch when git command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: not a git repository"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            git_ops = GitOperations(temp_dir)
            
            with pytest.raises(GitError):
                git_ops.get_current_branch()
    
    @patch('subprocess.run')
    def test_get_branch_info(self, mock_run):
        """Test getting branch information."""
        # Mock git branch --list
        mock_branch_list = MagicMock()
        mock_branch_list.returncode = 0
        mock_branch_list.stdout = "feature/test\n"
        
        # Mock git log
        mock_log = MagicMock()
        mock_log.returncode = 0
        mock_log.stdout = "abc123\n"
        
        # Mock git rev-list for ahead count
        mock_ahead = MagicMock()
        mock_ahead.returncode = 0
        mock_ahead.stdout = "2\n"
        
        # Mock git rev-list for behind count
        mock_behind = MagicMock()
        mock_behind.returncode = 0
        mock_behind.stdout = "1\n"
        
        mock_run.side_effect = [mock_branch_list, mock_log, mock_ahead, mock_behind]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            git_ops = GitOperations(temp_dir)
            
            # Mock get_current_branch to return main
            with patch.object(git_ops, 'get_current_branch', return_value="main"):
                branch_info = git_ops.get_branch_info("feature/test")
                
                assert branch_info.name == "feature/test"
                assert branch_info.exists is True
                assert branch_info.is_current is False
                assert branch_info.last_commit == "abc123"
                assert branch_info.ahead_count == 2
                assert branch_info.behind_count == 1
    
    @patch('subprocess.run')
    def test_create_branch_success(self, mock_run):
        """Test successfully creating a branch."""
        # Mock git checkout -b
        mock_checkout = MagicMock()
        mock_checkout.returncode = 0
        
        # Mock git rev-parse HEAD
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0
        mock_rev_parse.stdout = "abc123\n"
        
        mock_run.side_effect = [mock_checkout, mock_rev_parse]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            git_ops = GitOperations(temp_dir)
            
            # Mock branch info methods
            with patch.object(git_ops, 'get_branch_info') as mock_branch_info:
                # Mock base branch exists
                mock_branch_info.side_effect = [
                    MagicMock(exists=True),  # base branch
                    MagicMock(exists=False)  # target branch
                ]
                
                branch_name = git_ops.create_branch("feature/test")
                assert branch_name == "feature/test"
    
    @patch('subprocess.run')
    def test_commit_changes_success(self, mock_run):
        """Test successfully committing changes."""
        # Mock git add
        mock_add = MagicMock()
        mock_add.returncode = 0
        
        # Mock git commit
        mock_commit = MagicMock()
        mock_commit.returncode = 0
        
        # Mock git rev-parse HEAD
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0
        mock_rev_parse.stdout = "abc123\n"
        
        mock_run.side_effect = [mock_add, mock_commit, mock_rev_parse]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            git_ops = GitOperations(temp_dir)
            
            commit_hash = git_ops.commit_changes("Test commit", ["file1.txt"])
            assert commit_hash == "abc123"
    
    @patch('subprocess.run')
    def test_get_status(self, mock_run):
        """Test getting git status."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "M  modified.txt\n?? new.txt\n"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            git_ops = GitOperations(temp_dir)
            
            # Mock get_current_branch
            with patch.object(git_ops, 'get_current_branch', return_value="main"):
                status = git_ops.get_status()
                
                # Check that files are parsed correctly
                assert len(status["unstaged_files"]) > 0 or len(status["staged_files"]) > 0
                assert "new.txt" in status["untracked_files"]
                assert status["clean"] is False


class TestGitHubIntegration:
    """Test the GitHubIntegration class."""
    
    def test_github_integration_creation_non_github_repo(self):
        """Test creating GitHubIntegration with non-GitHub repo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations to return non-GitHub remote
            with patch('core.git_operations.GitOperations') as mock_git_ops:
                mock_instance = MagicMock()
                mock_instance.get_remote_url.return_value = "https://gitlab.com/test/repo.git"
                mock_git_ops.return_value = mock_instance
                
                with pytest.raises(GitError):
                    GitHubIntegration(temp_dir)
    
    @patch('subprocess.run')
    def test_check_gh_cli_installed(self, mock_run):
        """Test checking if GitHub CLI is installed."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations to return GitHub remote
            with patch('core.git_operations.GitOperations') as mock_git_ops:
                mock_instance = MagicMock()
                mock_instance.get_remote_url.return_value = "https://github.com/test/repo.git"
                mock_git_ops.return_value = mock_instance
                
                github_integration = GitHubIntegration(temp_dir)
                
                # Test _check_gh_cli method
                assert github_integration._check_gh_cli() is True
    
    @patch('subprocess.run')
    def test_check_gh_cli_not_installed(self, mock_run):
        """Test checking if GitHub CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations to return GitHub remote
            with patch('core.git_operations.GitOperations') as mock_git_ops:
                mock_instance = MagicMock()
                mock_instance.get_remote_url.return_value = "https://github.com/test/repo.git"
                mock_git_ops.return_value = mock_instance
                
                github_integration = GitHubIntegration(temp_dir)
                
                # Test _check_gh_cli method
                assert github_integration._check_gh_cli() is False


class TestGitLabIntegration:
    """Test the GitLabIntegration class."""
    
    def test_gitlab_integration_creation_non_gitlab_repo(self):
        """Test creating GitLabIntegration with non-GitLab repo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations to return non-GitLab remote
            with patch('core.git_operations.GitOperations') as mock_git_ops:
                mock_instance = MagicMock()
                mock_instance.get_remote_url.return_value = "https://github.com/test/repo.git"
                mock_git_ops.return_value = mock_instance
                
                with pytest.raises(GitError):
                    GitLabIntegration(temp_dir)
    
    def test_gitlab_merge_request_not_implemented(self):
        """Test that GitLab merge request creation is not yet implemented."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations to return GitLab remote
            with patch('core.git_operations.GitOperations') as mock_git_ops:
                mock_instance = MagicMock()
                mock_instance.get_remote_url.return_value = "https://gitlab.com/test/repo.git"
                mock_git_ops.return_value = mock_instance
                
                gitlab_integration = GitLabIntegration(temp_dir)
                
                with pytest.raises(GitError, match="GitLab integration not yet implemented"):
                    gitlab_integration.create_merge_request("Test MR", "Description", "feature", "main")
