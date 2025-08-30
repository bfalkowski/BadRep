"""
Unit tests for the configuration manager.
"""

import sys
from pathlib import Path

import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config import ConfigManager
from core.errors import ConfigurationError


def test_config_manager_initialization():
    """Test that ConfigManager initializes with defaults."""
    config = ConfigManager()
    assert config is not None
    assert config.get("language") == "java"
    assert config.get("verbose") is False


def test_config_get_method():
    """Test the get method with various keys."""
    config = ConfigManager()

    # Test simple keys
    assert config.get("language") == "java"
    assert config.get("verbose") is False

    # Test nested keys
    assert config.get("git.remote") == "origin"
    assert config.get("languages.java.build_tool") == "maven"

    # Test default values
    assert config.get("nonexistent_key", "default") == "default"


def test_config_set_method():
    """Test the set method with various keys."""
    config = ConfigManager()

    # Test simple keys
    config.set("language", "python")
    assert config.get("language") == "python"

    # Test nested keys
    config.set("git.remote", "upstream")
    assert config.get("git.remote") == "upstream"

    # Test new nested keys
    config.set("new.section.value", "test")
    assert config.get("new.section.value") == "test"


def test_config_validation():
    """Test configuration validation."""
    config = ConfigManager()

    # Should not raise an exception for valid config
    assert config.validate() is True

    # Test with invalid language
    config.set("language", "unsupported_language")
    with pytest.raises(ConfigurationError):
        config.validate()


def test_config_to_dict():
    """Test that to_dict returns a copy of the configuration."""
    config = ConfigManager()
    config_dict = config.to_dict()

    assert isinstance(config_dict, dict)
    assert config_dict["language"] == "java"

    # Modifying the dict shouldn't affect the original config
    config_dict["language"] = "python"
    assert config.get("language") == "java"


def test_language_config():
    """Test getting language-specific configuration."""
    config = ConfigManager()

    java_config = config.get_language_config("java")
    assert java_config["build_tool"] == "maven"
    assert java_config["source_dir"] == "src/main/java"

    # Test default language
    default_config = config.get_language_config()
    assert default_config["build_tool"] == "maven"
