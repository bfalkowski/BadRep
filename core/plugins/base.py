"""
Base Plugin Interface for ReviewLab.

This module defines the abstract base classes and interfaces that all
language-specific plugins must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from core.bug_templates import BugInjection, BugLocation, BugTemplate


@dataclass
class CodeLocation:
    """Represents a specific location in source code."""

    file_path: Path
    line_number: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None

    def to_bug_location(self) -> BugLocation:
        """Convert to BugLocation format."""
        return BugLocation(
            file_path=str(self.file_path),
            line_number=self.line_number,
            column_start=self.column_start,
            column_end=self.column_end,
            function_name=self.function_name,
            class_name=self.class_name,
        )


@dataclass
class CodeModification:
    """Represents a modification to source code."""

    location: CodeLocation
    original_code: str
    modified_code: str
    description: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class InjectionResult:
    """Result of a bug injection operation."""

    success: bool
    modifications: List[CodeModification]
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class LanguagePlugin(ABC):
    """Abstract base class for language-specific plugins."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.supported_extensions: Set[str] = set()
        self.build_files: Set[str] = set()
        self.test_files: Set[str] = set()
        self._initialize_language_specifics()

    @abstractmethod
    def _initialize_language_specifics(self):
        """Initialize language-specific attributes and configurations."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin name."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get the plugin version."""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> Set[str]:
        """Get supported file extensions for this language."""
        pass

    @abstractmethod
    def can_parse_file(self, file_path: Path) -> bool:
        """Check if this plugin can parse the given file."""
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a source file and extract structural information."""
        pass

    @abstractmethod
    def find_injection_targets(self, file_path: Path, template: BugTemplate) -> List[CodeLocation]:
        """Find suitable locations for injecting a specific bug template."""
        pass

    @abstractmethod
    def inject_bug(self, injection: BugInjection) -> InjectionResult:
        """Inject a bug into the source code."""
        pass

    @abstractmethod
    def validate_injection(self, injection: BugInjection) -> bool:
        """Validate that a bug injection can be performed."""
        pass

    @abstractmethod
    def build_project(self) -> bool:
        """Build the project to ensure it still compiles after injection."""
        pass

    @abstractmethod
    def run_tests(self) -> Dict[str, Any]:
        """Run tests to verify the injection worked correctly."""
        pass

    @abstractmethod
    def cleanup_injection(self, injection: BugInjection) -> bool:
        """Clean up a bug injection (restore original code)."""
        pass

    def get_project_structure(self) -> Dict[str, Any]:
        """Get the project structure and metadata."""
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "project_root": str(self.project_root),
            "supported_extensions": list(self.get_supported_extensions()),
            "build_files": list(self.build_files),
            "test_files": list(self.test_files),
        }

    def find_source_files(self) -> List[Path]:
        """Find all source files in the project."""
        source_files = []
        for ext in self.supported_extensions:
            source_files.extend(self.project_root.rglob(f"*.{ext}"))
        return source_files

    def find_test_files(self) -> List[Path]:
        """Find all test files in the project."""
        test_files = []
        for test_file in self.test_files:
            test_files.extend(self.project_root.rglob(test_file))
        return test_files

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a specific file."""
        if not self.can_parse_file(file_path):
            return {"error": "File not supported by this plugin"}

        try:
            return self.parse_file(file_path)
        except Exception as e:
            return {"error": f"Failed to parse file: {e}"}


class PluginManager:
    """Manages language plugins and provides unified interface."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.plugins: Dict[str, LanguagePlugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all available language plugins."""
        try:
            from .java import JavaPlugin

            self.plugins["java"] = JavaPlugin(self.project_root)
        except ImportError:
            pass

        try:
            from .python import PythonPlugin

            self.plugins["python"] = PythonPlugin(self.project_root)
        except ImportError:
            pass

        try:
            from .javascript import JavaScriptPlugin

            self.plugins["javascript"] = JavaScriptPlugin(self.project_root)
        except ImportError:
            pass

        try:
            from .go import GoPlugin

            self.plugins["go"] = GoPlugin(self.project_root)
        except ImportError:
            pass

    def get_plugin(self, language: str) -> Optional[LanguagePlugin]:
        """Get a plugin for a specific language."""
        return self.plugins.get(language.lower())

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.plugins.keys())

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect the language of a file based on its extension."""
        for language, plugin in self.plugins.items():
            if plugin.can_parse_file(file_path):
                return language
        return None

    def get_plugin_for_file(self, file_path: Path) -> Optional[LanguagePlugin]:
        """Get the appropriate plugin for a specific file."""
        language = self.detect_language(file_path)
        if language:
            return self.plugins[language]
        return None

    def inject_bug(self, injection: BugInjection) -> InjectionResult:
        """Inject a bug using the appropriate plugin."""
        # Determine the target file
        target_file = Path(injection.location.file_path)
        if not target_file.is_absolute():
            target_file = self.project_root / target_file

        # Find the appropriate plugin
        plugin = self.get_plugin_for_file(target_file)
        if not plugin:
            return InjectionResult(
                success=False, modifications=[], errors=[f"No plugin found for file: {target_file}"]
            )

        # Perform the injection
        return plugin.inject_bug(injection)

    def validate_injection(self, injection: BugInjection) -> bool:
        """Validate a bug injection using the appropriate plugin."""
        target_file = Path(injection.location.file_path)
        if not target_file.is_absolute():
            target_file = self.project_root / target_file

        plugin = self.get_plugin_for_file(target_file)
        if not plugin:
            return False

        return plugin.validate_injection(injection)

    def get_project_info(self) -> Dict[str, Any]:
        """Get comprehensive project information from all plugins."""
        info = {
            "project_root": str(self.project_root),
            "supported_languages": self.get_supported_languages(),
            "languages": {},
        }

        for language, plugin in self.plugins.items():
            info["languages"][language] = plugin.get_project_structure()

        return info
