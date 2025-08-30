"""
Unit tests for PR workflow manager.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.pr_workflow import (
    PRWorkflowConfig, WorkflowResult, PRWorkflowManager
)
from core.git_operations import GitConfig, GitOperations
from core.bug_injection import BugInjectionEngine
from core.errors import GitError, InjectionError


class TestPRWorkflowConfig:
    """Test the PRWorkflowConfig class."""
    
    def test_pr_workflow_config_creation(self):
        """Test creating a PRWorkflowConfig instance."""
        config = PRWorkflowConfig(
            auto_create_pr=False,
            auto_push=False,
            pr_title_template="Custom: {bug_type}",
            labels=["custom-label"],
            reviewers=["user1", "user2"]
        )
        
        assert config.auto_create_pr is False
        assert config.auto_push is False
        assert config.pr_title_template == "Custom: {bug_type}"
        assert "custom-label" in config.labels
        assert "user1" in config.reviewers
        assert "user2" in config.reviewers


class TestWorkflowResult:
    """Test the WorkflowResult class."""
    
    def test_workflow_result_creation(self):
        """Test creating a WorkflowResult instance."""
        result = WorkflowResult(
            success=True,
            session_id="test-session",
            branch_name="feature/test",
            commit_hash="abc123",
            pr_info={"id": "123"},
            metadata={"test": "data"}
        )
        
        assert result.success is True
        assert result.session_id == "test-session"
        assert result.branch_name == "feature/test"
        assert result.commit_hash == "abc123"
        assert result.pr_info["id"] == "123"
        assert result.metadata["test"] == "data"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0


class TestPRWorkflowManager:
    """Test the PRWorkflowManager class."""
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_workflow_manager_creation(self, mock_injection_engine, mock_git_ops):
        """Test creating a PRWorkflowManager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            assert workflow_manager.project_root == Path(temp_dir)
            assert workflow_manager.git_ops == mock_git_instance
            assert workflow_manager.injection_engine == mock_injection_instance
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    @patch('core.pr_workflow.GitHubIntegration')
    def test_workflow_manager_with_github(self, mock_github, mock_injection_engine, mock_git_ops):
        """Test creating PRWorkflowManager with GitHub integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_engine.return_value = mock_injection_instance
            
            # Mock GitHubIntegration
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            assert workflow_manager.github_integration == mock_github_instance
            assert workflow_manager.gitlab_integration is None
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    @patch('core.pr_workflow.GitLabIntegration')
    def test_workflow_manager_with_gitlab(self, mock_gitlab, mock_injection_engine, mock_git_ops):
        """Test creating PRWorkflowManager with GitLab integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_engine.return_value = mock_injection_instance
            
            # Mock GitLabIntegration
            mock_gitlab_instance = MagicMock()
            mock_gitlab.return_value = mock_gitlab_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            assert workflow_manager.gitlab_integration == mock_gitlab_instance
            assert workflow_manager.github_integration is None
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_execute_workflow_success(self, mock_injection_engine, mock_git_ops):
        """Test successfully executing a workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_instance.create_injection_branch.return_value = "bug-injection/java-test-123"
            mock_git_instance.commit_injection.return_value = "abc123"
            mock_git_instance.push_branch.return_value = True
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_instance.start_injection_session.return_value = "test-session"
            mock_injection_instance.end_injection_session.return_value = None
            mock_injection_instance.export_ground_truth.return_value = None
            
            # Mock injection result
            mock_injection_result = MagicMock()
            mock_injection_result.success = True
            mock_modification = MagicMock()
            mock_modification.location.file_path = "src/Test.java"
            mock_injection_result.modifications = [mock_modification]
            mock_injection_instance.inject_bug.return_value = mock_injection_result
            
            # Mock template
            mock_template = MagicMock()
            mock_template.name = "Test Bug"
            mock_injection_instance.template_manager.get_template.return_value = mock_template
            
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            # Mock GitHub integration
            workflow_manager.github_integration = MagicMock()
            workflow_manager.github_integration.create_pull_request.return_value = {"id": "123"}
            
            result = workflow_manager.execute_workflow(
                "java", "test_template", "src/Test.java", 42
            )
            
            assert result.success is True
            assert result.session_id == "test-session"
            assert result.branch_name == "bug-injection/java-test-123"
            assert result.commit_hash == "abc123"
            assert result.pr_info["id"] == "123"
            assert "injection_id" in result.metadata
            assert result.metadata["language"] == "java"
            assert result.metadata["bug_type"] == "Test Bug"
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_execute_workflow_injection_failure(self, mock_injection_engine, mock_git_ops):
        """Test workflow execution when bug injection fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_instance.create_injection_branch.return_value = "bug-injection/java-test-123"
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_instance.start_injection_session.return_value = "test-session"
            mock_injection_instance.end_injection_session.return_value = None
            
            # Mock injection result failure
            mock_injection_result = MagicMock()
            mock_injection_result.success = False
            mock_injection_result.errors = ["Template not found"]
            mock_injection_instance.inject_bug.return_value = mock_injection_result
            
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            result = workflow_manager.execute_workflow(
                "java", "test_template", "src/Test.java", 42
            )
            
            assert result.success is False
            assert "Template not found" in result.errors[0]
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_execute_batch_workflow_success(self, mock_injection_engine, mock_git_ops):
        """Test successfully executing a batch workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_instance.create_injection_branch.return_value = "bug-injection/java-batch-123"
            mock_git_instance.commit_injection.return_value = "abc123"
            mock_git_instance.push_branch.return_value = True
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_instance.start_injection_session.return_value = "test-session"
            mock_injection_instance.end_injection_session.return_value = None
            mock_injection_instance.export_ground_truth.return_value = None
            
            # Mock injection results
            mock_injection_result = MagicMock()
            mock_injection_result.success = True
            mock_modification = MagicMock()
            mock_modification.location.file_path = "src/Test.java"
            mock_injection_result.modifications = [mock_modification]
            mock_injection_instance.inject_bug.return_value = mock_injection_result
            
            # Mock template
            mock_template = MagicMock()
            mock_template.name = "Test Bug"
            mock_injection_instance.template_manager.get_template.return_value = mock_template
            
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            # Mock GitHub integration
            workflow_manager.github_integration = MagicMock()
            workflow_manager.github_integration.create_pull_request.return_value = {"id": "123"}
            
            # Execute batch workflow
            injections = [
                {
                    'template_id': 'test_template_1',
                    'file_path': 'src/Test1.java',
                    'line_number': 42
                },
                {
                    'template_id': 'test_template_2',
                    'file_path': 'src/Test2.java',
                    'line_number': 84
                }
            ]
            
            results = workflow_manager.execute_batch_workflow("java", injections)
            
            assert len(results) == 2
            assert all(result.success for result in results)
            assert all(result.branch_name == "bug-injection/java-batch-123" for result in results)
            assert all(result.commit_hash == "abc123" for result in results)
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_get_workflow_status(self, mock_injection_engine, mock_git_ops):
        """Test getting workflow status."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_instance.get_current_branch.return_value = "main"
            mock_git_instance.get_status.return_value = {
                "current_branch": "main",
                "staged_files": [],
                "unstaged_files": [],
                "untracked_files": [],
                "clean": True
            }
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            status = workflow_manager.get_workflow_status()
            
            assert status['project_root'] == str(temp_dir)
            assert status['git_config']['base_branch'] == "main"
            assert status['workflow_config']['auto_create_pr'] is True
            assert status['integrations']['github'] is False
            assert status['integrations']['gitlab'] is False
            assert status['current_branch'] == "main"
            assert status['git_status']['clean'] is True
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_cleanup_workflow_success(self, mock_injection_engine, mock_git_ops):
        """Test successfully cleaning up workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_instance.checkout_branch.return_value = True
            mock_git_instance.delete_branch.return_value = True
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            result = workflow_manager.cleanup_workflow("bug-injection/test-branch")
            
            assert result is True
            mock_git_instance.checkout_branch.assert_called_once_with("main")
            mock_git_instance.delete_branch.assert_called_once_with("bug-injection/test-branch", False)
    
    @patch('core.pr_workflow.GitOperations')
    @patch('core.pr_workflow.BugInjectionEngine')
    def test_cleanup_workflow_failure(self, mock_injection_engine, mock_git_ops):
        """Test workflow cleanup failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            # Mock GitOperations
            mock_git_instance = MagicMock()
            mock_git_instance.checkout_branch.return_value = False  # Checkout fails
            mock_git_ops.return_value = mock_git_instance
            
            # Mock BugInjectionEngine
            mock_injection_instance = MagicMock()
            mock_injection_engine.return_value = mock_injection_instance
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            result = workflow_manager.cleanup_workflow("bug-injection/test-branch")
            
            assert result is False
            mock_git_instance.checkout_branch.assert_called_once_with("main")
            mock_git_instance.delete_branch.assert_not_called()
    
    def test_format_batch_changes(self):
        """Test formatting batch changes for PR description."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            workflow_manager = PRWorkflowManager(temp_dir)
            
            # Test with empty results
            empty_results = []
            formatted = workflow_manager._format_batch_changes(empty_results)
            assert formatted == "No changes made."
            
            # Test with results
            mock_results = [
                MagicMock(
                    success=True,
                    metadata={'files_modified': ['file1.java'], 'template_id': 'template1'}
                ),
                MagicMock(
                    success=True,
                    metadata={'files_modified': ['file1.java', 'file2.java'], 'template_id': 'template2'}
                ),
                MagicMock(
                    success=False,
                    metadata={}
                )
            ]
            
            formatted = workflow_manager._format_batch_changes(mock_results)
            
            assert "file1.java" in formatted
            assert "file2.java" in formatted
            assert "template1" in formatted
            assert "template2" in formatted
