"""
Unit tests for the error handling system.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.errors import (
    ConfigurationError,
    ErrorHandler,
    EvaluationError,
    GitError,
    InjectionError,
    ReviewLabError,
    ValidationError,
    GitHubError,
    AuthenticationError,
    RepositoryError,
)


def test_reviewlab_error_base():
    """Test the base ReviewLabError class."""
    error = ReviewLabError("Test error message")
    assert str(error) == "Test error message"
    assert error.details == {}


def test_reviewlab_error_with_details():
    """Test ReviewLabError with details."""
    details = {"file": "test.py", "line": 10}
    error = ReviewLabError("Test error message", details)
    assert error.details == details
    assert "file" in error.details
    assert error.details["file"] == "test.py"


def test_configuration_error():
    """Test ConfigurationError class."""
    error = ConfigurationError("Config error")
    assert isinstance(error, ReviewLabError)
    assert "Config error" in str(error)


def test_validation_error():
    """Test ValidationError class."""
    error = ValidationError("Validation error")
    assert isinstance(error, ReviewLabError)
    assert "Validation error" in str(error)


def test_git_error():
    """Test GitError class."""
    error = GitError("Git error")
    assert isinstance(error, ReviewLabError)
    assert "Git error" in str(error)


def test_injection_error():
    """Test InjectionError class."""
    error = InjectionError("Injection error")
    assert isinstance(error, ReviewLabError)
    assert "Injection error" in str(error)


def test_evaluation_error():
    """Test EvaluationError class."""
    error = EvaluationError("Evaluation error")
    assert isinstance(error, ReviewLabError)
    assert "Evaluation error" in str(error)


def test_github_error():
    """Test GitHubError class."""
    error = GitHubError("GitHub error")
    assert isinstance(error, ReviewLabError)
    assert "GitHub error" in str(error)


def test_authentication_error():
    """Test AuthenticationError class."""
    error = AuthenticationError("Auth error")
    assert isinstance(error, GitHubError)
    assert "Auth error" in str(error)


def test_repository_error():
    """Test RepositoryError class."""
    error = RepositoryError("Repo error")
    assert isinstance(error, GitHubError)
    assert "Repo error" in str(error)


def test_error_handler_handle_error():
    """Test ErrorHandler.handle_error."""
    error = ConfigurationError("Test error", {"key": "value"})
    # This should not raise an exception
    ErrorHandler.handle_error(error, "test_context")


@patch('sys.exit')
def test_error_handler_handle_critical_error(mock_exit):
    """Test ErrorHandler.handle_critical_error."""
    error = ConfigurationError("Test error", {"key": "value"})
    # This should call sys.exit(1)
    ErrorHandler.handle_critical_error(error, "test_context")
    mock_exit.assert_called_once_with(1)


def test_error_handler_handle_warning():
    """Test ErrorHandler.handle_warning."""
    # This should not raise an exception
    ErrorHandler.handle_warning("Test warning", "test_context")


def test_error_handler_handle_info():
    """Test ErrorHandler.handle_info."""
    # This should not raise an exception
    ErrorHandler.handle_info("Test info", "test_context")
