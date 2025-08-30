"""
Language Plugin System for ReviewLab.

This package provides the plugin infrastructure for language-specific
bug injection and analysis capabilities.
"""

from .base import LanguagePlugin, PluginManager
from .java import JavaPlugin
from .python import PythonPlugin
from .javascript import JavaScriptPlugin
from .go import GoPlugin

__all__ = [
    'LanguagePlugin',
    'PluginManager',
    'JavaPlugin',
    'PythonPlugin',
    'JavaScriptPlugin',
    'GoPlugin'
]
