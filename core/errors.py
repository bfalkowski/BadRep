"""
Error handling module for ReviewLab.

Defines custom exception classes and error handling utilities.
"""

import sys
import traceback
from typing import Any, Dict, Optional


class ReviewLabError(Exception):
    """Base exception class for ReviewLab errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(ReviewLabError):
    """Raised when there's a configuration error."""
    pass


class ValidationError(ReviewLabError):
    """Raised when data validation fails."""
    pass


class InjectionError(ReviewLabError):
    """Raised when bug injection fails."""
    pass


class EvaluationError(ReviewLabError):
    """Raised when evaluation fails."""
    pass


class GitError(ReviewLabError):
    """Raised when Git operations fail."""
    pass


class PRWorkflowError(ReviewLabError):
    """Raised when PR workflow operations fail."""
    pass


class PluginError(ReviewLabError):
    """Raised when plugin operations fail."""
    pass


class TemplateError(ReviewLabError):
    """Raised when template operations fail."""
    pass


class ReportError(ReviewLabError):
    """Raised when report generation fails."""
    pass


class GitHubError(ReviewLabError):
    """Base exception for GitHub-related errors."""
    pass


class AuthenticationError(GitHubError):
    """Raised when GitHub authentication fails."""
    pass


class RepositoryError(GitHubError):
    """Raised when GitHub repository operations fail."""
    pass


class ErrorHandler:
    """Centralized error handling for ReviewLab."""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "Unknown operation") -> None:
        """Handle an error with proper formatting and context."""
        error_type = type(error).__name__
        
        # Print error header
        print(f"\n❌ Error in {context}")
        print(f"🔍 Type: {error_type}")
        print(f"💬 Message: {str(error)}")
        
        # Print details if available
        if hasattr(error, 'details') and error.details:
            print(f"📋 Details: {error.details}")
        
        # Print traceback in verbose mode
        if hasattr(error, 'verbose') and error.verbose:
            print(f"\n🔍 Full traceback:")
            traceback.print_exc()
        
        # Print helpful suggestions based on error type
        ErrorHandler._print_suggestions(error_type, context)
    
    @staticmethod
    def _print_suggestions(error_type: str, context: str) -> None:
        """Print helpful suggestions based on error type."""
        suggestions = {
            "ConfigurationError": [
                "Check your configuration file",
                "Verify environment variables are set",
                "Ensure all required fields are present"
            ],
            "ValidationError": [
                "Check input data format",
                "Verify required fields are provided",
                "Ensure data meets validation rules"
            ],
            "InjectionError": [
                "Check bug template syntax",
                "Verify target file exists and is writable",
                "Ensure language plugin is properly configured"
            ],
            "GitError": [
                "Check Git repository status",
                "Verify you have write permissions",
                "Ensure branch names are valid"
            ],
            "AuthenticationError": [
                "Check your GitHub token is valid",
                "Verify token has required permissions",
                "Ensure username is correct"
            ],
            "RepositoryError": [
                "Check repository exists and is accessible",
                "Verify you have write permissions",
                "Ensure branch names are valid"
            ]
        }
        
        if error_type in suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in suggestions[error_type]:
                print(f"   • {suggestion}")
    
    @staticmethod
    def handle_critical_error(error: Exception, context: str = "Critical operation") -> None:
        """Handle a critical error that requires immediate exit."""
        ErrorHandler.handle_error(error, context)
        print(f"\n💥 Critical error in {context}. Exiting.")
        sys.exit(1)
    
    @staticmethod
    def handle_warning(warning: str, context: str = "Operation") -> None:
        """Handle a warning with proper formatting."""
        print(f"\n⚠️  Warning in {context}")
        print(f"💬 {warning}")
    
    @staticmethod
    def handle_info(info: str, context: str = "Operation") -> None:
        """Handle informational messages."""
        print(f"\nℹ️  {context}: {info}")


def require_condition(condition: bool, message: str, error_type: type = ReviewLabError) -> None:
    """Require a condition to be true, otherwise raise an error."""
    if not condition:
        raise error_type(message)


def require_not_none(value: Any, message: str, error_type: type = ReviewLabError) -> None:
    """Require a value to not be None, otherwise raise an error."""
    if value is None:
        raise error_type(message)


def require_file_exists(file_path: str, error_type: type = ReviewLabError) -> None:
    """Require a file to exist, otherwise raise an error."""
    from pathlib import Path
    if not Path(file_path).exists():
        raise error_type(f"File does not exist: {file_path}")


def require_directory_exists(dir_path: str, error_type: type = ReviewLabError) -> None:
    """Require a directory to exist, otherwise raise an error."""
    from pathlib import Path
    if not Path(dir_path).exists():
        raise error_type(f"Directory does not exist: {dir_path}")


def require_valid_language(language: str, error_type: type = ValidationError) -> None:
    """Require a valid language, otherwise raise an error."""
    valid_languages = ["java", "python", "javascript", "go"]
    if language not in valid_languages:
        raise error_type(f"Invalid language: {language}. Must be one of: {valid_languages}")


def require_valid_severity(severity: str, error_type: type = ValidationError) -> None:
    """Require a valid severity level, otherwise raise an error."""
    valid_severities = ["low", "medium", "high", "critical"]
    if severity not in valid_severities:
        raise error_type(f"Invalid severity: {severity}. Must be one of: {valid_severities}")


def require_valid_difficulty(difficulty: str, error_type: type = ValidationError) -> None:
    """Require a valid difficulty level, otherwise raise an error."""
    valid_difficulties = ["easy", "medium", "hard", "expert"]
    if difficulty not in valid_difficulties:
        raise error_type(f"Invalid difficulty: {difficulty}. Must be one of: {valid_difficulties}")
