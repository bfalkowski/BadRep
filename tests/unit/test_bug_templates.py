"""
Unit tests for the bug template system.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.bug_templates import (
    BugCategory,
    BugDifficulty,
    BugInjection,
    BugLocation,
    BugSeverity,
    BugTemplate,
    BugTemplateManager,
    BugTemplateRenderer,
)


class TestBugTemplateManager:
    """Test the BugTemplateManager class."""

    def test_init_with_default_template_dir(self):
        """Test initialization with default template directory."""
        manager = BugTemplateManager()
        assert manager.template_dir == Path("tooling/bug_templates")
        assert isinstance(manager.templates, dict)
        assert isinstance(manager.taxonomy, dict)

    def test_init_with_custom_template_dir(self):
        """Test initialization with custom template directory."""
        custom_dir = Path("/custom/templates")
        manager = BugTemplateManager(custom_dir)
        assert manager.template_dir == custom_dir

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_taxonomy_success(self, mock_yaml_load, mock_open):
        """Test successful taxonomy loading."""
        mock_taxonomy = {
            "bug_categories": {"correctness": {"name": "Correctness Bugs"}},
            "language_patterns": {"java": ["null_pointer_exception"]},
        }
        mock_yaml_load.return_value = mock_taxonomy

        manager = BugTemplateManager()
        assert manager.taxonomy == mock_taxonomy

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_taxonomy_file_not_found(self, mock_yaml_load, mock_open):
        """Test taxonomy loading when file doesn't exist."""
        mock_open.side_effect = FileNotFoundError()

        # Create manager with a non-existent directory to avoid loading real templates
        manager = BugTemplateManager(Path("/non/existent/path"))
        assert manager.taxonomy == {}

    def test_get_template_count_empty(self):
        """Test template count when no templates are loaded."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        assert manager.get_template_count() == 0

    def test_list_categories_empty(self):
        """Test category listing when no taxonomy is loaded."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        assert manager.list_categories() == []

    def test_list_languages_empty(self):
        """Test language listing when no taxonomy is loaded."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        assert manager.list_languages() == []

    def test_search_templates_empty(self):
        """Test template search when no templates are loaded."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        results = manager.search_templates("test")
        assert results == []

    def test_get_templates_by_category_empty(self):
        """Test getting templates by category when none exist."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        results = manager.get_templates_by_category(BugCategory.CORRECTNESS)
        assert results == []

    def test_get_templates_by_language_empty(self):
        """Test getting templates by language when none exist."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        results = manager.get_templates_by_language("java")
        assert results == []

    def test_get_templates_by_severity_empty(self):
        """Test getting templates by severity when none exist."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        results = manager.get_templates_by_severity(BugSeverity.HIGH)
        assert results == []

    def test_get_templates_by_difficulty_empty(self):
        """Test getting templates by difficulty when none exist."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        results = manager.get_templates_by_difficulty(BugDifficulty.EASY)
        assert results == []


class TestBugTemplate:
    """Test the BugTemplate class."""

    def test_bug_template_creation(self):
        """Test creating a BugTemplate instance."""
        template = BugTemplate(
            id="test_bug",
            name="Test Bug",
            description="A test bug template",
            category=BugCategory.CORRECTNESS,
            severity=BugSeverity.HIGH,
            difficulty=BugDifficulty.EASY,
            language="java",
            patterns=["off_by_one"],
            tags=["test", "bug"],
            examples=["for (int i = 0; i <= len; i++)"],
            detection_hints=["Check loop boundaries"],
        )

        assert template.id == "test_bug"
        assert template.name == "Test Bug"
        assert template.category == BugCategory.CORRECTNESS
        assert template.severity == BugSeverity.HIGH
        assert template.difficulty == BugDifficulty.EASY
        assert template.language == "java"
        assert template.patterns == ["off_by_one"]
        assert template.tags == ["test", "bug"]
        assert template.examples == ["for (int i = 0; i <= len; i++)"]
        assert template.detection_hints == ["Check loop boundaries"]

    def test_bug_template_to_dict(self):
        """Test converting BugTemplate to dictionary."""
        template = BugTemplate(
            id="test_bug",
            name="Test Bug",
            description="A test bug template",
            category=BugCategory.CORRECTNESS,
            severity=BugSeverity.HIGH,
            difficulty=BugDifficulty.EASY,
            language="java",
        )

        template_dict = template.to_dict()
        assert template_dict["id"] == "test_bug"
        assert template_dict["category"] == "correctness"
        assert template_dict["severity"] == "high"
        assert template_dict["difficulty"] == "easy"
        assert template_dict["language"] == "java"


class TestBugLocation:
    """Test the BugLocation class."""

    def test_bug_location_creation(self):
        """Test creating a BugLocation instance."""
        location = BugLocation(
            file_path="src/Calculator.java",
            line_number=42,
            column_start=10,
            column_end=20,
            function_name="calculate",
            class_name="Calculator",
        )

        assert location.file_path == "src/Calculator.java"
        assert location.line_number == 42
        assert location.column_start == 10
        assert location.column_end == 20
        assert location.function_name == "calculate"
        assert location.class_name == "Calculator"

    def test_bug_location_to_dict(self):
        """Test converting BugLocation to dictionary."""
        location = BugLocation(file_path="src/Calculator.java", line_number=42)

        location_dict = location.to_dict()
        assert location_dict["file_path"] == "src/Calculator.java"
        assert location_dict["line_number"] == 42
        assert location_dict["column_start"] is None
        assert location_dict["column_end"] is None


class TestBugInjection:
    """Test the BugInjection class."""

    def test_bug_injection_creation(self):
        """Test creating a BugInjection instance."""
        location = BugLocation(file_path="src/Calculator.java", line_number=42)

        injection = BugInjection(
            template_id="java_off_by_one",
            location=location,
            parameters={"loop_type": "for"},
            metadata={"injected_by": "test"},
        )

        assert injection.template_id == "java_off_by_one"
        assert injection.location == location
        assert injection.parameters == {"loop_type": "for"}
        assert injection.metadata == {"injected_by": "test"}

    def test_bug_injection_to_dict(self):
        """Test converting BugInjection to dictionary."""
        location = BugLocation(file_path="src/Calculator.java", line_number=42)

        injection = BugInjection(template_id="java_off_by_one", location=location)

        injection_dict = injection.to_dict()
        assert injection_dict["template_id"] == "java_off_by_one"
        assert injection_dict["location"]["file_path"] == "src/Calculator.java"
        assert injection_dict["location"]["line_number"] == 42


class TestBugTemplateRenderer:
    """Test the BugTemplateRenderer class."""

    def test_renderer_creation(self):
        """Test creating a BugTemplateRenderer instance."""
        manager = BugTemplateManager()
        renderer = BugTemplateRenderer(manager)
        assert renderer.template_manager == manager

    def test_validate_injection_success(self):
        """Test successful injection validation."""
        manager = BugTemplateManager(Path("/non/existent/path"))
        renderer = BugTemplateRenderer(manager)

        location = BugLocation(file_path="src/Calculator.java", line_number=42)

        injection = BugInjection(template_id="java_off_by_one", location=location)

        # Should fail validation because template doesn't exist
        assert renderer.validate_injection(injection) is False

    def test_validate_injection_failure(self):
        """Test failed injection validation."""
        manager = BugTemplateManager()
        renderer = BugTemplateRenderer(manager)

        # Invalid location (no file path)
        location = BugLocation(file_path="", line_number=42)

        injection = BugInjection(template_id="java_off_by_one", location=location)

        assert renderer.validate_injection(injection) is False

        # Invalid location (line number <= 0)
        location = BugLocation(file_path="src/Calculator.java", line_number=0)

        injection = BugInjection(template_id="java_off_by_one", location=location)

        assert renderer.validate_injection(injection) is False


class TestBugEnums:
    """Test the bug-related enums."""

    def test_bug_category_values(self):
        """Test BugCategory enum values."""
        assert BugCategory.CORRECTNESS.value == "correctness"
        assert BugCategory.API_MISUSE.value == "api_misuse"
        assert BugCategory.RESOURCE_HANDLING.value == "resource_handling"
        assert BugCategory.SECURITY_LITE.value == "security_lite"
        assert BugCategory.MAINTAINABILITY.value == "maintainability"
        assert BugCategory.TEST_ISSUES.value == "test_issues"

    def test_bug_severity_values(self):
        """Test BugSeverity enum values."""
        assert BugSeverity.LOW.value == "low"
        assert BugSeverity.MEDIUM.value == "medium"
        assert BugSeverity.HIGH.value == "high"
        assert BugSeverity.CRITICAL.value == "critical"

    def test_bug_difficulty_values(self):
        """Test BugDifficulty enum values."""
        assert BugDifficulty.EASY.value == "easy"
        assert BugDifficulty.MEDIUM.value == "medium"
        assert BugDifficulty.HARD.value == "hard"
