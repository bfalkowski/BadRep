"""
Unit tests for the bug injection engine.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.bug_injection import (
    BugInjectionEngine,
    GroundTruthEntry,
    GroundTruthLogger,
    InjectionSession,
)
from core.bug_templates import BugCategory, BugDifficulty, BugSeverity, BugTemplate
from core.plugins.base import CodeLocation, CodeModification, InjectionResult


class TestGroundTruthEntry:
    """Test the GroundTruthEntry class."""

    def test_ground_truth_entry_creation(self):
        """Test creating a GroundTruthEntry instance."""
        entry = GroundTruthEntry(
            id="test_id",
            injection_id="test_injection",
            template_id="test_template",
            project_path="/test/project",
            language="java",
            file_path="src/Test.java",
            line_number=42,
            bug_type="correctness",
            description="Test bug",
            severity="high",
            difficulty="easy",
            injection_timestamp="2024-01-01T00:00:00",
            original_code="original code",
            modified_code="modified code",
            metadata={"test": "data"},
        )

        assert entry.id == "test_id"
        assert entry.injection_id == "test_injection"
        assert entry.language == "java"
        assert entry.line_number == 42
        assert entry.bug_type == "correctness"
        assert entry.metadata["test"] == "data"

    def test_ground_truth_entry_to_dict(self):
        """Test converting GroundTruthEntry to dictionary."""
        entry = GroundTruthEntry(
            id="test_id",
            injection_id="test_injection",
            template_id="test_template",
            project_path="/test/project",
            language="java",
            file_path="src/Test.java",
            line_number=42,
            bug_type="correctness",
            description="Test bug",
            severity="high",
            difficulty="easy",
            injection_timestamp="2024-01-01T00:00:00",
            original_code="original code",
            modified_code="modified code",
        )

        entry_dict = entry.to_dict()
        assert entry_dict["id"] == "test_id"
        assert entry_dict["language"] == "java"
        assert entry_dict["line_number"] == 42

    def test_ground_truth_entry_to_jsonl(self):
        """Test converting GroundTruthEntry to JSONL format."""
        entry = GroundTruthEntry(
            id="test_id",
            injection_id="test_injection",
            template_id="test_template",
            project_path="/test/project",
            language="java",
            file_path="src/Test.java",
            line_number=42,
            bug_type="correctness",
            description="Test bug",
            severity="high",
            difficulty="easy",
            injection_timestamp="2024-01-01T00:00:00",
            original_code="original code",
            modified_code="modified code",
        )

        jsonl = entry.to_jsonl()
        assert isinstance(jsonl, str)
        assert "test_id" in jsonl
        assert "java" in jsonl


class TestInjectionSession:
    """Test the InjectionSession class."""

    def test_injection_session_creation(self):
        """Test creating an InjectionSession instance."""
        session = InjectionSession(
            session_id="test_session",
            project_path="/test/project",
            language="java",
            start_time="2024-01-01T00:00:00",
        )

        assert session.session_id == "test_session"
        assert session.project_path == "/test/project"
        assert session.language == "java"
        assert session.total_injections == 0
        assert session.successful_injections == 0
        assert session.failed_injections == 0

    def test_injection_session_to_dict(self):
        """Test converting InjectionSession to dictionary."""
        session = InjectionSession(
            session_id="test_session",
            project_path="/test/project",
            language="java",
            start_time="2024-01-01T00:00:00",
        )

        session_dict = session.to_dict()
        assert session_dict["session_id"] == "test_session"
        assert session_dict["language"] == "java"
        assert session_dict["total_injections"] == 0


class TestGroundTruthLogger:
    """Test the GroundTruthLogger class."""

    def test_logger_creation(self):
        """Test creating a GroundTruthLogger instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = GroundTruthLogger(Path(temp_dir))
            assert logger.log_dir == Path(temp_dir)
            assert isinstance(logger.session_logs, dict)

    def test_start_session(self):
        """Test starting a new injection session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = GroundTruthLogger(Path(temp_dir))
            session_id = logger.start_session("/test/project", "java")

            assert session_id in logger.session_logs
            session = logger.session_logs[session_id]
            assert session.project_path == "/test/project"
            assert session.language == "java"
            assert session.start_time is not None

    def test_end_session(self):
        """Test ending an injection session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = GroundTruthLogger(Path(temp_dir))
            session_id = logger.start_session("/test/project", "java")

            logger.end_session(session_id)
            session = logger.session_logs[session_id]
            assert session.end_time is not None

    def test_log_injection(self):
        """Test logging a bug injection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = GroundTruthLogger(Path(temp_dir))
            session_id = logger.start_session("/test/project", "java")

            # Mock objects
            injection = MagicMock()
            injection.template_id = "test_template"
            injection.location.file_path = "src/Test.java"
            injection.location.line_number = 42
            injection.parameters = {}
            injection.metadata = {}

            result = MagicMock()
            result.success = True
            result.modifications = [MagicMock()]
            result.modifications[0].original_code = "original"
            result.modifications[0].modified_code = "modified"
            result.metadata = {}

            template = MagicMock()
            template.category.value = "correctness"
            template.description = "Test bug"
            template.severity.value = "high"
            template.difficulty.value = "easy"
            template.patterns = []
            template.tags = []

            # Log injection
            entry = logger.log_injection(session_id, injection, result, template)

            assert entry.language == "java"
            assert entry.file_path == "src/Test.java"
            assert entry.line_number == 42

            # Check session statistics
            session = logger.session_logs[session_id]
            assert session.total_injections == 1
            assert session.successful_injections == 1
            assert session.failed_injections == 0


class TestBugInjectionEngine:
    """Test the BugInjectionEngine class."""

    def test_engine_creation(self):
        """Test creating a BugInjectionEngine instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = BugInjectionEngine(Path(temp_dir))
            assert engine.project_root == Path(temp_dir)
            assert engine.current_session is None

    @patch("core.plugins.PluginManager")
    @patch("core.bug_templates.BugTemplateManager")
    def test_start_injection_session_success(self, mock_template_manager, mock_plugin_manager):
        """Test successfully starting an injection session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock plugin manager
            mock_plugin = MagicMock()
            mock_plugin_manager.return_value.get_plugin.return_value = mock_plugin

            engine = BugInjectionEngine(Path(temp_dir))
            session_id = engine.start_injection_session("java")

            assert session_id is not None
            assert engine.current_session == session_id

    @patch("core.plugins.PluginManager")
    @patch("core.bug_templates.BugTemplateManager")
    def test_start_injection_session_unsupported_language(
        self, mock_template_manager, mock_plugin_manager
    ):
        """Test starting session with unsupported language."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock plugin manager to return None for unsupported language
            mock_plugin_manager.return_value.get_plugin.return_value = None

            engine = BugInjectionEngine(Path(temp_dir))

            with pytest.raises(Exception):  # Should raise ValidationError
                engine.start_injection_session("unsupported")

    @patch("core.plugins.PluginManager")
    @patch("core.bug_templates.BugTemplateManager")
    def test_end_injection_session(self, mock_template_manager, mock_plugin_manager):
        """Test ending an injection session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock plugin manager
            mock_plugin = MagicMock()
            mock_plugin_manager.return_value.get_plugin.return_value = mock_plugin

            engine = BugInjectionEngine(Path(temp_dir))
            session_id = engine.start_injection_session("java")

            engine.end_injection_session()
            assert engine.current_session is None

    @patch("core.plugins.PluginManager")
    @patch("core.bug_templates.BugTemplateManager")
    def test_inject_bug_no_session(self, mock_template_manager, mock_plugin_manager):
        """Test injecting bug without active session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = BugInjectionEngine(Path(temp_dir))

            with pytest.raises(Exception):  # Should raise InjectionError
                engine.inject_bug("test_template", "src/Test.java", 42)

    @patch("core.plugins.PluginManager")
    @patch("core.bug_templates.BugTemplateManager")
    def test_get_injection_summary_no_session(self, mock_template_manager, mock_plugin_manager):
        """Test getting injection summary without active session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = BugInjectionEngine(Path(temp_dir))
            summary = engine.get_injection_summary()

            assert "error" in summary
            assert summary["error"] == "No active session"

    def test_get_available_templates(self):
        """Test getting available templates with filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create engine with a non-existent template directory to avoid loading real templates
            engine = BugInjectionEngine(Path(temp_dir), Path("/non/existent/templates"))

            # Since no templates are loaded, all filtering should return empty lists
            correctness_templates = engine.get_available_templates("java", category="correctness")
            assert len(correctness_templates) == 0

            easy_templates = engine.get_available_templates("java", difficulty="easy")
            assert len(easy_templates) == 0

            filtered_templates = engine.get_available_templates(
                "java", category="correctness", difficulty="easy"
            )
            assert len(filtered_templates) == 0
