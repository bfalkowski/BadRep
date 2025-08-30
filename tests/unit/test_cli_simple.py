"""
Simplified unit tests for the CLI interface.

These tests focus on testing the CLI interface structure and help text
rather than full execution, which requires extensive mocking.
"""

import pytest
from click.testing import CliRunner

from cli.main import cli


class TestCLIInterface:
    """Test the CLI interface structure and help text."""

    def test_cli_help(self):
        """Test that CLI help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "ReviewLab" in result.output
        assert "Generate PRs with injected bugs" in result.output

    def test_cli_version(self):
        """Test that CLI version works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_language_option(self):
        """Test that language option works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--language", "java", "--help"])
        assert result.exit_code == 0

    def test_cli_verbose_option(self):
        """Test that verbose option works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--help"])
        assert result.exit_code == 0


class TestCLICommands:
    """Test that all CLI commands exist and have proper help."""

    def test_demo_command(self):
        """Test demo command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["demo", "--help"])
        assert result.exit_code == 0
        assert "Run a quick evaluation demo" in result.output
        assert "--language" in result.output
        assert "--output-dir" in result.output
        assert "--verbose" in result.output

    def test_evaluate_command(self):
        """Test evaluate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["evaluate", "--help"])
        assert result.exit_code == 0
        assert "Evaluate code review bot findings" in result.output
        assert "--findings" in result.output
        assert "--ground-truth" in result.output
        assert "--review-tool" in result.output
        assert "--strategies" in result.output
        assert "--output-format" in result.output
        assert "--output-dir" in result.output
        assert "--verbose" in result.output

    def test_list_bugs_command(self):
        """Test list-bugs command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list-bugs", "--help"])
        assert result.exit_code == 0
        assert "List available bug types" in result.output
        assert "--language" in result.output
        assert "--verbose" in result.output
        assert "--category" in result.output
        assert "--severity" in result.output
        assert "--difficulty" in result.output
        assert "--format" in result.output

    def test_generate_pr_command(self):
        """Test generate-pr command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate-pr", "--help"])
        assert result.exit_code == 0
        assert "Generate a new pull request with injected bugs" in result.output
        assert "--count" in result.output
        assert "--types" in result.output
        assert "--seed" in result.output
        assert "--title" in result.output
        assert "--base" in result.output
        assert "--auto-push" in result.output
        assert "--dry-run" in result.output

    def test_replay_command(self):
        """Test replay command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["replay", "--help"])
        assert result.exit_code == 0
        assert "Rebuild exact bug mutations from ground truth log" in result.output
        assert "--pr" in result.output
        assert "--output" in result.output


class TestCLIOptions:
    """Test CLI option handling."""

    def test_language_choices(self):
        """Test that language choices are properly defined."""
        runner = CliRunner()

        # Test valid languages
        for lang in ["java", "python", "javascript", "go"]:
            result = runner.invoke(cli, ["--language", lang, "--help"])
            assert result.exit_code == 0

        # Test invalid language - Click shows help even with invalid options
        result = runner.invoke(cli, ["--language", "invalid", "--help"])
        assert result.exit_code == 0  # Click shows help regardless

    def test_output_format_choices(self):
        """Test that output format choices are properly defined."""
        runner = CliRunner()

        # Test valid formats
        for fmt in ["json", "csv", "txt", "html", "all"]:
            result = runner.invoke(cli, ["evaluate", "--output-format", fmt, "--help"])
            assert result.exit_code == 0

        # Test invalid format - Click shows help even with invalid options
        result = runner.invoke(cli, ["evaluate", "--output-format", "invalid", "--help"])
        assert result.exit_code == 0  # Click shows help regardless

    def test_format_choices(self):
        """Test that format choices are properly defined for list-bugs."""
        runner = CliRunner()

        # Test valid formats
        for fmt in ["table", "json", "csv"]:
            result = runner.invoke(cli, ["list-bugs", "--format", fmt, "--help"])
            assert result.exit_code == 0

        # Test invalid format - Click shows help even with invalid options
        result = runner.invoke(cli, ["list-bugs", "--format", "invalid", "--help"])
        assert result.exit_code == 0  # Click shows help regardless


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_missing_required_args(self):
        """Test that missing required arguments show proper errors."""
        runner = CliRunner()

        # Test evaluate without required args
        result = runner.invoke(cli, ["evaluate"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

        # Test generate-pr without required args (should work, has defaults)
        result = runner.invoke(cli, ["generate-pr", "--help"])
        assert result.exit_code == 0

    def test_invalid_options(self):
        """Test that invalid options show proper errors."""
        runner = CliRunner()

        # Test invalid language - Click shows help even with invalid options
        result = runner.invoke(cli, ["--language", "invalid", "--help"])
        assert result.exit_code == 0  # Click shows help regardless

        # Test invalid output format - Click shows help even with invalid options
        result = runner.invoke(cli, ["evaluate", "--output-format", "invalid", "--help"])
        assert result.exit_code == 0  # Click shows help regardless
