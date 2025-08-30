"""
Bug Template System for ReviewLab.

This module provides the core infrastructure for defining and managing
bug injection templates across different programming languages.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from core.errors import InjectionError


class BugSeverity(Enum):
    """Bug severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BugDifficulty(Enum):
    """Bug injection difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BugCategory(Enum):
    """Bug categories."""

    CORRECTNESS = "correctness"
    API_MISUSE = "api_misuse"
    RESOURCE_HANDLING = "resource_handling"
    SECURITY_LITE = "security_lite"
    MAINTAINABILITY = "maintainability"
    TEST_ISSUES = "test_issues"


@dataclass
class BugLocation:
    """Represents the location where a bug should be injected."""

    file_path: str
    line_number: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "function_name": self.function_name,
            "class_name": self.class_name,
        }


@dataclass
class BugTemplate:
    """Base class for bug injection templates."""

    id: str
    name: str
    description: str
    category: BugCategory
    severity: BugSeverity
    difficulty: BugDifficulty
    language: str
    patterns: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    detection_hints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "severity": self.severity.value,
            "difficulty": self.difficulty.value,
            "language": self.language,
            "patterns": self.patterns,
            "tags": self.tags,
            "examples": self.examples,
            "detection_hints": self.detection_hints,
        }


@dataclass
class BugInjection:
    """Represents a specific bug injection instance."""

    template_id: str
    location: BugLocation
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "template_id": self.template_id,
            "location": self.location.to_dict(),
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


class BugTemplateEngine(ABC):
    """Abstract base class for bug template engines."""

    @abstractmethod
    def load_templates(self, template_dir: Path) -> List[BugTemplate]:
        """Load bug templates from a directory."""
        pass

    @abstractmethod
    def validate_template(self, template: BugTemplate) -> bool:
        """Validate a bug template."""
        pass

    @abstractmethod
    def get_templates_by_category(self, category: BugCategory) -> List[BugTemplate]:
        """Get templates filtered by category."""
        pass

    @abstractmethod
    def get_templates_by_language(self, language: str) -> List[BugTemplate]:
        """Get templates filtered by language."""
        pass


class BugTemplateManager:
    """Manages bug templates across different languages and categories."""

    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or Path("tooling/bug_templates")
        self.templates: Dict[str, BugTemplate] = {}
        self.taxonomy: Dict[str, Any] = {}
        self._load_taxonomy()
        self._load_templates()

    def _load_taxonomy(self):
        """Load the bug taxonomy definition."""
        taxonomy_file = self.template_dir / "bug_taxonomy.yaml"
        if taxonomy_file.exists():
            with open(taxonomy_file, "r") as f:
                self.taxonomy = yaml.safe_load(f)

    def _load_templates(self):
        """Load all bug templates from the template directory."""
        if not self.template_dir.exists():
            return

        # Load language-specific templates
        for lang_dir in self.template_dir.iterdir():
            if lang_dir.is_dir() and lang_dir.name in ["java", "python", "javascript", "go"]:
                self._load_language_templates(lang_dir)

    def _load_language_templates(self, lang_dir: Path):
        """Load templates for a specific language."""
        for template_file in lang_dir.glob("*.yaml"):
            try:
                with open(template_file, "r") as f:
                    template_data = yaml.safe_load(f)
                    if isinstance(template_data, list):
                        for item in template_data:
                            template = self._create_template_from_dict(item, lang_dir.name)
                            if template:
                                self.templates[template.id] = template
                    elif isinstance(template_data, dict):
                        template = self._create_template_from_dict(template_data, lang_dir.name)
                        if template:
                            self.templates[template.id] = template
            except Exception as e:
                print(f"Warning: Failed to load template from {template_file}: {e}")

    def _create_template_from_dict(
        self, data: Dict[str, Any], language: str
    ) -> Optional[BugTemplate]:
        """Create a BugTemplate instance from dictionary data."""
        try:
            return BugTemplate(
                id=data.get("id", ""),
                name=data.get("name", ""),
                description=data.get("description", ""),
                category=BugCategory(data.get("category", "correctness")),
                severity=BugSeverity(data.get("severity", "medium")),
                difficulty=BugDifficulty(data.get("difficulty", "medium")),
                language=language,
                patterns=data.get("patterns", []),
                tags=data.get("tags", []),
                examples=data.get("examples", []),
                detection_hints=data.get("detection_hints", []),
            )
        except (ValueError, KeyError) as e:
            print(f"Warning: Invalid template data: {e}")
            return None

    def get_template(self, template_id: str) -> Optional[BugTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def get_templates_by_category(self, category: BugCategory) -> List[BugTemplate]:
        """Get templates filtered by category."""
        return [t for t in self.templates.values() if t.category == category]

    def get_templates_by_language(self, language: str) -> List[BugTemplate]:
        """Get templates filtered by language."""
        return [t for t in self.templates.values() if t.language == language]

    def get_templates_by_severity(self, severity: BugSeverity) -> List[BugTemplate]:
        """Get templates filtered by severity."""
        return [t for t in self.templates.values() if t.severity == severity]

    def get_templates_by_difficulty(self, difficulty: BugDifficulty) -> List[BugTemplate]:
        """Get templates filtered by difficulty."""
        return [t for t in self.templates.values() if t.difficulty == difficulty]

    def search_templates(self, query: str) -> List[BugTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []

        for template in self.templates.values():
            if (
                query_lower in template.name.lower()
                or query_lower in template.description.lower()
                or any(query_lower in tag.lower() for tag in template.tags)
            ):
                results.append(template)

        return results

    def get_taxonomy(self) -> Dict[str, Any]:
        """Get the bug taxonomy definition."""
        return self.taxonomy

    def list_categories(self) -> List[str]:
        """List all available bug categories."""
        return list(self.taxonomy.get("bug_categories", {}).keys())

    def list_languages(self) -> List[str]:
        """List all supported languages."""
        return list(self.taxonomy.get("language_patterns", {}).keys())

    def get_template_count(self) -> int:
        """Get the total number of loaded templates."""
        return len(self.templates)

    def export_templates(self, output_file: Path, format: str = "json"):
        """Export all templates to a file."""
        data = {
            "templates": [t.to_dict() for t in self.templates.values()],
            "taxonomy": self.taxonomy,
            "metadata": {
                "total_templates": len(self.templates),
                "languages": self.list_languages(),
                "categories": self.list_categories(),
            },
        }

        if format.lower() == "json":
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
        elif format.lower() == "yaml":
            with open(output_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


class BugTemplateRenderer:
    """Renders bug templates into actual code modifications."""

    def __init__(self, template_manager: BugTemplateManager):
        self.template_manager = template_manager

    def render_injection(self, injection: BugInjection) -> str:
        """Render a bug injection into code modifications."""
        template = self.template_manager.get_template(injection.template_id)
        if not template:
            raise InjectionError(f"Template not found: {injection.template_id}")

        # This is a placeholder - actual rendering will be implemented
        # in language-specific renderers
        return f"// Bug injected: {template.name}\n// {template.description}"

    def validate_injection(self, injection: BugInjection) -> bool:
        """Validate that an injection can be performed."""
        template = self.template_manager.get_template(injection.template_id)
        if not template:
            return False

        # Basic validation - can be extended
        return bool(injection.location.file_path and injection.location.line_number > 0)
