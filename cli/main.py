#!/usr/bin/env python3
"""
ReviewLab CLI - Bug-Seeded PR Generator + Review-Accuracy Evaluator

Main entry point for the command-line interface.
"""

import click
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import ConfigManager
from core.errors import ReviewLabError, ErrorHandler


@click.group()
@click.version_option(version="0.1.0", prog_name="reviewlab")
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--language', '-l', type=click.Choice(['java', 'python', 'javascript', 'go']), 
              help='Target programming language')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--dry-run', is_flag=True, help='Simulate operations without making changes')
@click.pass_context
def cli(ctx, config, language, verbose, dry_run):
    """
    ReviewLab - Generate PRs with injected bugs and evaluate review bot accuracy.
    
    This tool helps you create pull requests containing intentionally injected bugs
    and then evaluate how well code review bots detect them.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        if config:
            config_manager.load_config(config)
        
        # Override with CLI options
        if language:
            config_manager.set('language', language)
        if verbose:
            config_manager.set('verbose', verbose)
        if dry_run:
            config_manager.set('dry_run', dry_run)
        
        # Store in context
        ctx.obj['config'] = config_manager
        
        if verbose:
            click.echo(f"Configuration loaded: {config_manager.get('language')} language selected")
            
    except Exception as e:
        ErrorHandler.handle_error(e, "CLI initialization")
        sys.exit(1)


@cli.command()
@click.option('--count', '-n', default=5, help='Number of bugs to inject (default: 5)')
@click.option('--types', '-t', help='Comma-separated list of bug types to use')
@click.option('--seed', '-s', type=int, help='Random seed for reproducible generation')
@click.option('--title', help='Custom PR title')
@click.option('--base', default='main', help='Base branch (default: main)')
@click.pass_context
def generate_pr(ctx, count, types, seed, title, base):
    """Generate a new pull request with injected bugs."""
    config = ctx.obj['config']
    
    try:
        click.echo(f"Generating PR with {count} bugs...")
        click.echo(f"Language: {config.get('language')}")
        click.echo(f"Base branch: {base}")
        
        if types:
            click.echo(f"Bug types: {types}")
        if seed:
            click.echo(f"Seed: {seed}")
            
        # TODO: Implement actual PR generation
        click.echo("PR generation not yet implemented")
        
    except Exception as e:
        ErrorHandler.handle_error(e, "PR generation")
        sys.exit(1)


@cli.command()
@click.option('--pr', required=True, help='PR identifier')
@click.option('--findings', required=True, type=click.Path(exists=True), help='Path to bot findings JSON')
@click.option('--matcher', default='overlap', help='Matching strategy (default: overlap)')
@click.option('--tolerance', default=2, type=int, help='Line range tolerance (default: 2)')
@click.option('--report', default='both', type=click.Choice(['json', 'markdown', 'both']), 
              help='Output format (default: both)')
@click.pass_context
def evaluate(ctx, pr, findings, matcher, tolerance, report):
    """Evaluate bot findings against ground truth."""
    config = ctx.obj['config']
    
    try:
        click.echo(f"Evaluating findings for PR {pr}...")
        click.echo(f"Findings file: {findings}")
        click.echo(f"Matcher: {matcher}")
        click.echo(f"Tolerance: {tolerance}")
        click.echo(f"Report format: {report}")
        
        # TODO: Implement actual evaluation
        click.echo("Evaluation not yet implemented")
        
    except Exception as e:
        ErrorHandler.handle_error(e, "Evaluation")
        sys.exit(1)


@cli.command()
@click.option('--language', '-l', help='Target language (uses config default if not specified)')
@click.option('--verbose', is_flag=True, help='Show detailed descriptions')
@click.pass_context
def list_bugs(ctx, language, verbose):
    """List available bug types for the current language."""
    config = ctx.obj['config']
    target_language = language or config.get('language')
    
    try:
        click.echo(f"Available bug types for {target_language}:")
        
        # TODO: Implement actual bug listing
        click.echo("Bug listing not yet implemented")
        
    except Exception as e:
        ErrorHandler.handle_error(e, "Bug listing")
        sys.exit(1)


@cli.command()
@click.option('--pr', required=True, help='PR to replay')
@click.option('--output', type=click.Path(), help='Output directory for recreated changes')
@click.pass_context
def replay(ctx, pr, output):
    """Rebuild exact bug mutations from ground truth log."""
    config = ctx.obj['config']
    
    try:
        click.echo(f"Replaying PR {pr}...")
        
        if output:
            click.echo(f"Output directory: {output}")
        
        # TODO: Implement actual replay
        click.echo("Replay not yet implemented")
        
    except Exception as e:
        ErrorHandler.handle_error(e, "Replay")
        sys.exit(1)


if __name__ == '__main__':
    cli()
