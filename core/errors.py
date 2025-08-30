"""
Error handling system for ReviewLab.

Provides custom exception classes and error handling utilities
for consistent error reporting across the application.
"""

import sys
import traceback
from typing import Any, Dict, Optional


class ReviewLabError(Exception):
    """Base exception class for ReviewLab."""

    def __init__(
        self, message: str, error_code: str = None, details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(ReviewLabError):
    """Raised when there are configuration-related issues."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class LanguageError(ReviewLabError):
    """Raised when there are language-specific issues."""

    def __init__(
        self, message: str, language: str = None, details: Optional[Dict[str, Any]] = None
    ):
        if language:
            details = details or {}
            details["language"] = language
        super().__init__(message, "LANGUAGE_ERROR", details)


class GitError(ReviewLabError):
    """Raised when there are Git operation issues."""

    def __init__(
        self, message: str, operation: str = None, details: Optional[Dict[str, Any]] = None
    ):
        if operation:
            details = details or {}
            details["operation"] = operation
        super().__init__(message, "GIT_ERROR", details)


class InjectionError(ReviewLabError):
    """Raised when there are bug injection issues."""

    def __init__(
        self,
        message: str,
        file_path: str = None,
        bug_type: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if file_path or bug_type:
            details = details or {}
            if file_path:
                details["file_path"] = file_path
            if bug_type:
                details["bug_type"] = bug_type
        super().__init__(message, "INJECTION_ERROR", details)


class EvaluationError(ReviewLabError):
    """Raised when there are evaluation issues."""

    def __init__(self, message: str, pr_id: str = None, details: Optional[Dict[str, Any]] = None):
        if pr_id:
            details = details or {}
            details["pr_id"] = pr_id
        super().__init__(message, "EVALUATION_ERROR", details)


class SecurityError(ReviewLabError):
    """Raised when there are security-related issues."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SECURITY_ERROR", details)


class ErrorHandler:
    """Handles errors and provides user-friendly error reporting."""

    @staticmethod
    def handle_error(error: Exception, context: str = "Unknown operation") -> None:
        """
        Handle an error and provide user-friendly reporting.

        Args:
            error: The exception that occurred
            context: Context about what operation was being performed
        """
        if isinstance(error, ReviewLabError):
            ErrorHandler._handle_reviewlab_error(error, context)
        else:
            ErrorHandler._handle_generic_error(error, context)

    @staticmethod
    def _handle_reviewlab_error(error: ReviewLabError, context: str):
        """Handle ReviewLab-specific errors."""
        print(f"❌ Error in {context}: {error}", file=sys.stderr)

        if error.details:
            print("\n📋 Error Details:", file=sys.stderr)
            for key, value in error.details.items():
                print(f"  {key}: {value}", file=sys.stderr)

        # Provide helpful suggestions based on error type
        ErrorHandler._provide_suggestions(error)

    @staticmethod
    def _handle_generic_error(error: Exception, context: str):
        """Handle generic Python exceptions."""
        print(f"❌ Unexpected error in {context}: {error}", file=sys.stderr)

        if hasattr(error, "__traceback__"):
            print("\n🔍 Full traceback:", file=sys.stderr)
            traceback.print_exc()

    @staticmethod
    def _provide_suggestions(error: ReviewLabError):
        """Provide helpful suggestions based on error type."""
        suggestions = {
            "CONFIG_ERROR": [
                "Check that your configuration file exists and is valid YAML",
                "Verify that all required configuration keys are present",
                "Check environment variable syntax (REVIEWLAB_*)",
            ],
            "LANGUAGE_ERROR": [
                "Ensure the specified language is supported (java, python, javascript, go)",
                "Check that language-specific tools are installed",
                "Verify the language configuration in your config file",
            ],
            "GIT_ERROR": [
                "Ensure you're in a git repository",
                "Check that you have the necessary git permissions",
                "Verify your remote configuration",
            ],
            "INJECTION_ERROR": [
                "Check that the target file exists and is readable",
                "Verify that the bug template is valid",
                "Ensure the file syntax is correct for the target language",
            ],
            "EVALUATION_ERROR": [
                "Verify that the PR ID exists",
                "Check that the findings file is valid JSON",
                "Ensure ground truth data is available",
            ],
            "SECURITY_ERROR": [
                "Check file paths for directory traversal attempts",
                "Verify that templates don't contain dangerous code",
                "Review API key usage and permissions",
            ],
        }

        error_type = error.error_code
        if error_type in suggestions:
            print(f"\n💡 Suggestions for {error_type}:", file=sys.stderr)
            for suggestion in suggestions[error_type]:
                print(f"  • {suggestion}", file=sys.stderr)

    @staticmethod
    def format_error_for_logging(error: Exception, context: str = "Unknown") -> Dict[str, Any]:
        """
        Format an error for structured logging.

        Returns:
            Dictionary with error information suitable for logging
        """
        error_info = {
            "context": context,
            "error_type": type(error).__name__,
            "message": str(error),
            "timestamp": None,  # Will be filled by logging system
        }

        if isinstance(error, ReviewLabError):
            error_info.update({"error_code": error.error_code, "details": error.details})

        return error_info


def handle_errors(func):
    """
    Decorator to automatically handle errors in functions.

    Usage:
        @handle_errors
        def my_function():
            # ... function code ...
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, f"Function {func.__name__}")
            raise

    return wrapper
