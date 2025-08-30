"""
Unit tests for the error handling system.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.errors import (
    ReviewLabError, ConfigurationError, LanguageError, GitError,
    InjectionError, EvaluationError, SecurityError, ErrorHandler
)


def test_reviewlab_error_base():
    """Test the base ReviewLabError class."""
    error = ReviewLabError("Test error message")
    assert str(error) == "[UNKNOWN_ERROR] Test error message"
    assert error.error_code == "UNKNOWN_ERROR"
    assert error.details == {}


def test_reviewlab_error_with_code():
    """Test ReviewLabError with custom error code."""
    error = ReviewLabError("Test error", "CUSTOM_ERROR")
    assert str(error) == "[CUSTOM_ERROR] Test error"
    assert error.error_code == "CUSTOM_ERROR"


def test_reviewlab_error_with_details():
    """Test ReviewLabError with details."""
    details = {"file": "test.py", "line": 10}
    error = ReviewLabError("Test error", "TEST_ERROR", details)
    assert error.details == details


def test_configuration_error():
    """Test ConfigurationError class."""
    error = ConfigurationError("Config error")
    assert error.error_code == "CONFIG_ERROR"
    assert isinstance(error, ReviewLabError)


def test_language_error():
    """Test LanguageError class."""
    error = LanguageError("Language error", "python")
    assert error.error_code == "LANGUAGE_ERROR"
    assert error.details["language"] == "python"


def test_git_error():
    """Test GitError class."""
    error = GitError("Git error", "push")
    assert error.error_code == "GIT_ERROR"
    assert error.details["operation"] == "push"


def test_injection_error():
    """Test InjectionError class."""
    error = InjectionError("Injection error", "test.py", "off_by_one")
    assert error.error_code == "INJECTION_ERROR"
    assert error.details["file_path"] == "test.py"
    assert error.details["bug_type"] == "off_by_one"


def test_evaluation_error():
    """Test EvaluationError class."""
    error = EvaluationError("Evaluation error", "PR-123")
    assert error.error_code == "EVALUATION_ERROR"
    assert error.details["pr_id"] == "PR-123"


def test_security_error():
    """Test SecurityError class."""
    error = SecurityError("Security error")
    assert error.error_code == "SECURITY_ERROR"


def test_error_handler_format_error():
    """Test ErrorHandler.format_error_for_logging."""
    error = ConfigurationError("Test error", {"key": "value"})
    error_info = ErrorHandler.format_error_for_logging(error, "test_context")
    
    assert error_info["context"] == "test_context"
    assert error_info["error_type"] == "ConfigurationError"
    assert error_info["message"] == "[CONFIG_ERROR] Test error"
    assert error_info["error_code"] == "CONFIG_ERROR"
    assert error_info["details"] == {"key": "value"}


def test_error_handler_format_generic_error():
    """Test ErrorHandler.format_error_for_logging with generic error."""
    error = ValueError("Generic error")
    error_info = ErrorHandler.format_error_for_logging(error, "test_context")
    
    assert error_info["context"] == "test_context"
    assert error_info["error_type"] == "ValueError"
    assert error_info["message"] == "Generic error"
    assert "error_code" not in error_info
