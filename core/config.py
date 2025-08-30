"""
Configuration management for ReviewLab.

Handles loading configuration from multiple sources:
1. Default values (hardcoded)
2. Configuration file (YAML)
3. Environment variables
4. CLI arguments (highest priority)
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from core.errors import ConfigurationError


class ConfigManager:
    """Manages configuration with hierarchical override system."""

    def __init__(self):
        self._config = {}
        self._load_defaults()
        self._load_environment()

    def _load_defaults(self):
        """Load default configuration values."""
        self._config = {
            "language": "java",
            "verbose": False,
            "dry_run": False,
            "bug_mix": {
                "correctness": 0.3,
                "api_misuse": 0.2,
                "resource_handling": 0.15,
                "security_lite": 0.1,
                "maintainability": 0.15,
                "test_issues": 0.1,
            },
            "injection": {
                "allow_build_breakers": False,
                "assistive_markers": False,
                "max_bugs_per_file": 3,
                "preserve_tests": True,
            },
            "git": {
                "remote": "origin",
                "base_branch": "main",
                "auto_push": True,
                "commit_message_template": "feat: {feature} with injected bugs",
            },
            "evaluation": {
                "default_matcher": "overlap",
                "line_tolerance": 2,
                "confidence_threshold": 0.7,
                "report_formats": ["json", "markdown"],
            },
            "languages": {
                "java": {
                    "build_tool": "maven",
                    "test_command": "mvn test",
                    "source_dir": "src/main/java",
                },
                "python": {"build_tool": "pip", "test_command": "pytest", "source_dir": "src"},
                "javascript": {
                    "build_tool": "npm",
                    "test_command": "npm test",
                    "source_dir": "src",
                },
                "go": {"build_tool": "go", "test_command": "go test ./...", "source_dir": "."},
            },
            "pr": {
                "title_template": "feat: Add {feature} with {bug_count} bugs",
                "body_template": "This PR introduces {feature} functionality.",
            },
        }

    def _load_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "REVIEWLAB_LANGUAGE": "language",
            "REVIEWLAB_VERBOSE": "verbose",
            "REVIEWLAB_DRY_RUN": "dry_run",
            "REVIEWLAB_GIT_REMOTE": "git.remote",
            "REVIEWLAB_GIT_BASE_BRANCH": "git.base_branch",
            "REVIEWLAB_EVALUATION_LINE_TOLERANCE": "evaluation.line_tolerance",
            "REVIEWLAB_EVALUATION_CONFIDENCE_THRESHOLD": "evaluation.confidence_threshold",
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested(config_path, self._parse_env_value(value))

    def _parse_env_value(self, value: str) -> Union[str, bool, int, float]:
        """Parse environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Integer values
        try:
            return int(value)
        except ValueError:
            pass

        # Float values
        try:
            return float(value)
        except ValueError:
            pass

        # String values (default)
        return value

    def load_config(self, config_path: Union[str, Path]):
        """Load configuration from YAML file."""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")

            with open(config_path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f)

            if file_config:
                self._merge_config(file_config)

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration file: {e}")

    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing config."""

        def merge_dicts(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value

        merge_dicts(self._config, new_config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        try:
            return self._get_nested(key)
        except KeyError:
            return default

    def _get_nested(self, key: str) -> Any:
        """Get nested configuration value using dot notation."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                raise KeyError(f"Configuration key not found: {key}")

        return value

    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)."""
        self._set_nested(key, value)

    def _set_nested(self, key: str, value: Any):
        """Set nested configuration value using dot notation."""
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value

    def get_language_config(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific language."""
        lang = language or self.get("language")
        return self.get(f"languages.{lang}", {})

    def validate(self) -> bool:
        """Validate the current configuration."""
        required_keys = ["language", "bug_mix", "injection", "git", "evaluation"]

        for key in required_keys:
            if key not in self._config:
                raise ConfigurationError(f"Missing required configuration key: {key}")

        # Validate language-specific settings
        language = self.get("language")
        if language not in self.get("languages", {}):
            raise ConfigurationError(f"Unsupported language: {language}")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Get the complete configuration as a dictionary."""
        return self._config.copy()

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(language={self.get('language')}, verbose={self.get('verbose')})"
