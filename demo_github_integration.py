#!/usr/bin/env python3
"""
GitHub Integration Demo for ReviewLab

This script demonstrates how to use ReviewLab's GitHub integration
to create real pull requests with injected bugs.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cli.main import cli
from click.testing import CliRunner


def demo_github_integration():
    """Demonstrate GitHub integration features."""
    print("🚀 ReviewLab GitHub Integration Demo")
    print("=" * 50)
    print()
    
    runner = CliRunner()
    
    # Check if GitHub credentials are available
    github_token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USERNAME")
    
    if not github_token or not github_username:
        print("⚠️  GitHub credentials not found in environment variables")
        print("   Set GITHUB_TOKEN and GITHUB_USERNAME to test GitHub integration")
        print()
        print("💡 Example setup:")
        print("   export GITHUB_TOKEN='your_github_token_here'")
        print("   export GITHUB_USERNAME='your_github_username'")
        print()
        print("🔗 Get a token from: https://github.com/settings/tokens")
        print("   Required scopes: repo, workflow")
        print()
        return False
    
    print("✅ GitHub credentials found")
    print(f"   Username: {github_username}")
    print(f"   Token: {github_token[:8]}...")
    print()
    
    # Demo 1: List PRs in a repository
    print("📋 Demo 1: Listing PRs in a repository")
    print("-" * 40)
    
    # You can change this to any repository you have access to
    test_repo = "your-username/your-test-repo"  # Change this!
    
    print(f"🔍 Listing PRs in {test_repo}...")
    print("   (Change the repository in the script to test with your own repo)")
    print()
    
    # Demo 2: Generate PR with bugs (dry-run)
    print("🐛 Demo 2: Generate PR with injected bugs (Dry Run)")
    print("-" * 40)
    
    print("🔍 Running: reviewlab generate-pr --count 2 --language java --github-repo <repo> --dry-run")
    print("   This would:")
    print("   1. Inject 2 bugs into Java code")
    print("   2. Create a new branch")
    print("   3. Push changes to GitHub")
    print("   4. Create a pull request")
    print()
    
    # Demo 3: Show help for GitHub commands
    print("📚 Demo 3: GitHub Integration Commands")
    print("-" * 40)
    
    print("Available GitHub commands:")
    print()
    
    # Show generate-pr help
    result = runner.invoke(cli, ['generate-pr', '--help'])
    if result.exit_code == 0:
        print("🚀 generate-pr -- GitHub-enabled bug injection:")
        for line in result.output.split('\n'):
            if '--github' in line:
                print(f"   {line.strip()}")
        print()
    
    # Show list-prs help
    result = runner.invoke(cli, ['list-prs', '--help'])
    if result.exit_code == 0:
        print("📋 list-prs -- List repository PRs:")
        for line in result.output.split('\n'):
            if '--repo' in line or '--github' in line:
                print(f"   {line.strip()}")
        print()
    
    print("🎯 To test with real repositories:")
    print("   1. Set up your GitHub credentials")
    print("   2. Create a test repository")
    print("   3. Run: reviewlab generate-pr --github-repo owner/repo --count 3")
    print()
    
    return True


def demo_local_workflow():
    """Demonstrate local workflow without GitHub."""
    print("🏠 Local Workflow Demo (No GitHub Required)")
    print("=" * 50)
    print()
    
    runner = CliRunner()
    
    print("🔍 Running: reviewlab generate-pr --count 2 --language java --dry-run")
    print("   This demonstrates local bug injection:")
    print()
    
    result = runner.invoke(cli, ['generate-pr', '--count', '2', '--dry-run'])
    
    if result.exit_code == 0:
        print("✅ Local demo completed successfully!")
        print("   The tool would:")
        print("   1. Inject 2 bugs into Java code")
        print("   2. Create a local branch")
        print("   3. Commit changes locally")
        print("   4. Export ground truth data")
        print()
    else:
        print("❌ Local demo failed:")
        print(result.output)
        print()


if __name__ == "__main__":
    print("🎭 ReviewLab GitHub Integration Demo")
    print("=" * 50)
    print()
    
    # Try GitHub integration first
    github_available = demo_github_integration()
    
    print()
    
    # Always show local workflow
    demo_local_workflow()
    
    print("🎉 Demo completed!")
    print()
    print("💡 Next steps:")
    if github_available:
        print("   1. Set up a test repository")
        print("   2. Run real GitHub integration")
        print("   3. Test with your code review bot")
    else:
        print("   1. Set up GitHub credentials")
        print("   2. Create a test repository")
        print("   3. Run GitHub integration demo")
    
    print("   4. Move to Phase 9 (CI/CD Pipeline)")
    print()
