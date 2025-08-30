"""
Unit tests for the CLI module.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cli.main import cli


def test_cli_import():
    """Test that the CLI can be imported successfully."""
    assert cli is not None
    assert hasattr(cli, 'commands')


def test_cli_has_commands():
    """Test that the CLI has the expected commands."""
    commands = cli.commands
    expected_commands = ['generate-pr', 'evaluate', 'list-bugs', 'replay']
    
    for command in expected_commands:
        assert command in commands, f"Expected command '{command}' not found"


def test_cli_help_option():
    """Test that the CLI responds to help option."""
    # This is a basic test - in a real scenario we'd use click.testing.CliRunner
    assert hasattr(cli, 'get_help_option')
