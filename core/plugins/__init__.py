"""
Language Plugin System for ReviewLab.

This package provides the plugin infrastructure for language-specific
bug injection and analysis capabilities.
"""

from .base import LanguagePlugin, PluginManager
from .go import GoPlugin
from .java import JavaPlugin
from .javascript import JavaScriptPlugin
from .python import PythonPlugin

__all__ = [
    "LanguagePlugin",
    "PluginManager",
    "JavaPlugin",
    "PythonPlugin",
    "JavaScriptPlugin",
    "GoPlugin",
]
