"""
Unit tests for GitHub integration module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from core.github_integration import (
    GitHubConfig,
    GitHubManager,
    GitHubWorkflow,
    create_github_config_from_cli
)
from core.errors import AuthenticationError, RepositoryError


class TestGitHubConfig:
    """Test GitHub configuration."""
    
    def test_config_with_parameters(self):
        """Test config creation with explicit parameters."""
        config = GitHubConfig(token="test_token", username="test_user")
        assert config.token == "test_token"
        assert config.username == "test_user"
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'env_token', 'GITHUB_USERNAME': 'env_user'})
    def test_config_with_environment_variables(self):
        """Test config creation with environment variables."""
        config = GitHubConfig()
        assert config.token == "env_token"
        assert config.username == "env_user"
    
    def test_config_missing_token(self):
        """Test config creation fails without token."""
        with pytest.raises(AuthenticationError, match="GitHub token not found"):
            GitHubConfig(username="test_user")
    
    def test_config_missing_username(self):
        """Test config creation fails without username."""
        with pytest.raises(AuthenticationError, match="GitHub username not found"):
            GitHubConfig(token="test_token")


class TestGitHubManager:
    """Test GitHub manager operations."""
    
    @pytest.fixture
    def mock_github(self):
        """Create a mock GitHub instance."""
        mock_github = Mock()
        mock_user = Mock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        return mock_github
    
    @pytest.fixture
    def github_manager(self, mock_github):
        """Create a GitHub manager with mocked dependencies."""
        with patch('core.github_integration.Github') as mock_github_class:
            mock_github_class.return_value = mock_github
            config = GitHubConfig(token="test_token", username="test_user")
            return GitHubManager(config)
    
    def test_manager_initialization(self, github_manager):
        """Test GitHub manager initialization."""
        assert github_manager.config.token == "test_token"
        assert github_manager.config.username == "test_user"
    
    def test_get_repository_from_path(self, github_manager, mock_github):
        """Test getting repository from owner/repo path."""
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        
        repo = github_manager.get_repository("owner/repo")
        
        mock_github.get_repo.assert_called_once_with("owner/repo")
        assert repo == mock_repo
    
    def test_get_repository_from_url(self, github_manager, mock_github):
        """Test getting repository from full GitHub URL."""
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        
        repo = github_manager.get_repository("https://github.com/owner/repo")
        
        mock_github.get_repo.assert_called_once_with("owner/repo")
        assert repo == mock_repo
    
    def test_create_branch(self, github_manager, mock_github):
        """Test branch creation."""
        mock_repo = Mock()
        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref.return_value = None
        mock_repo.get_branch.return_value = mock_branch
        
        branch = github_manager.create_branch(mock_repo, "main", "new-branch")
        
        mock_repo.create_git_ref.assert_called_once_with("refs/heads/new-branch", "abc123")
        assert branch == mock_branch
    
    def test_push_files(self, github_manager, mock_github):
        """Test pushing multiple files."""
        mock_repo = Mock()
        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.get_git_tree.return_value = Mock()
        mock_repo.create_git_tree.return_value = Mock()
        mock_repo.create_git_commit.return_value = Mock(sha="def456")
        mock_repo.get_git_ref.return_value.edit.return_value = None
        
        files = {"test.py": "print('hello')"}
        commit_sha = github_manager.push_files(mock_repo, "new-branch", files, "test commit")
        
        assert commit_sha == "def456"
    
    def test_create_pull_request(self, github_manager, mock_github):
        """Test pull request creation."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        mock_repo.create_pull.return_value = mock_pr
        
        pr = github_manager.create_pull_request(
            mock_repo, "Test PR", "Test body", "head-branch", "main", False
        )
        
        mock_repo.create_pull.assert_called_once_with(
            title="Test PR",
            body="Test body",
            head="head-branch",
            base="main",
            draft=False
        )
        assert pr == mock_pr
    
    def test_get_repository_info(self, github_manager):
        """Test getting repository information."""
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "owner/test-repo"
        mock_repo.owner.login = "owner"
        mock_repo.html_url = "https://github.com/owner/test-repo"
        mock_repo.default_branch = "main"
        mock_repo.description = "Test repository"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 42
        mock_repo.forks_count = 10
        mock_repo.open_issues_count = 5
        
        info = github_manager.get_repository_info(mock_repo)
        
        assert info["name"] == "test-repo"
        assert info["full_name"] == "owner/test-repo"
        assert info["owner"] == "owner"
        assert info["language"] == "Python"
        assert info["stars"] == "42"


class TestGitHubWorkflow:
    """Test GitHub workflow operations."""
    
    @pytest.fixture
    def mock_github_manager(self):
        """Create a mock GitHub manager."""
        return Mock()
    
    @pytest.fixture
    def github_workflow(self, mock_github_manager):
        """Create a GitHub workflow with mocked dependencies."""
        return GitHubWorkflow(mock_github_manager)
    
    def test_create_bug_injection_pr(self, github_workflow, mock_github_manager):
        """Test complete bug injection PR workflow."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        
        mock_github_manager.get_repository.return_value = mock_repo
        mock_github_manager.validate_repository_access.return_value = True
        mock_github_manager.create_branch.return_value = Mock()
        mock_github_manager.push_files.return_value = "abc123"
        mock_github_manager.create_pull_request.return_value = mock_pr
        
        files = {"test.py": "print('hello')"}
        repo, pr = github_workflow.create_bug_injection_pr(
            "owner/repo", "main", "bug-branch", files, "Test PR", "Test body", False
        )
        
        assert repo == mock_repo
        assert pr == mock_pr
        mock_github_manager.get_repository.assert_called_once_with("owner/repo")
        mock_github_manager.create_branch.assert_called_once()
        mock_github_manager.push_files.assert_called_once()
        mock_github_manager.create_pull_request.assert_called_once()
    
    def test_create_bug_injection_pr_no_access(self, github_workflow, mock_github_manager):
        """Test PR creation fails without repository access."""
        mock_repo = Mock()
        mock_github_manager.get_repository.return_value = mock_repo
        mock_github_manager.validate_repository_access.return_value = False
        
        with pytest.raises(Exception, match="Failed to create bug injection PR"):
            github_workflow.create_bug_injection_pr(
                "owner/repo", "main", "bug-branch", {}, "Test PR", "Test body", False
            )


class TestGitHubCLI:
    """Test GitHub CLI integration."""
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token', 'GITHUB_USERNAME': 'test_user'})
    def test_create_github_config_from_cli_success(self):
        """Test successful GitHub config creation from CLI."""
        config = create_github_config_from_cli()
        assert config.token == "test_token"
        assert config.username == "test_user"
    
    def test_create_github_config_from_cli_with_parameters(self):
        """Test GitHub config creation with explicit parameters."""
        config = create_github_config_from_cli("param_token", "param_user")
        assert config.token == "param_token"
        assert config.username == "param_user"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_create_github_config_from_cli_failure(self):
        """Test GitHub config creation fails without credentials."""
        with pytest.raises(SystemExit):
            create_github_config_from_cli()
