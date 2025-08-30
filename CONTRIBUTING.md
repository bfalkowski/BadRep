# Contributing to ReviewLab

Thank you for your interest in contributing to ReviewLab! 🎉

This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Basic knowledge of Python development

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/reviewlab.git
   cd reviewlab
   ```
3. **Set up the development environment** (see Development Setup below)
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Install Pre-commit Hooks

```bash
make install-hooks
```

### 4. Verify Setup

```bash
# Run tests to ensure everything works
make test

# Check code quality
make quality-check
```

## Code Style

We use several tools to maintain code quality:

### Python Code Style

- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Running Code Quality Checks

```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Run type checking
make type-check

# Run all quality checks
make quality-check
```

### Code Style Guidelines

- Follow PEP 8 (with Black formatting)
- Use type hints for all functions
- Write docstrings for all public functions
- Keep functions under 20 lines when possible
- Use meaningful variable and function names
- Add comments for complex logic

### Example

```python
from typing import List, Optional
from pathlib import Path

def process_files(file_paths: List[Path], output_dir: Optional[Path] = None) -> bool:
    """
    Process a list of files and optionally save results to output directory.
    
    Args:
        file_paths: List of file paths to process
        output_dir: Optional output directory for results
        
    Returns:
        True if processing succeeded, False otherwise
        
    Raises:
        FileNotFoundError: If any input file doesn't exist
        PermissionError: If output directory is not writable
    """
    # Implementation here
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests quickly
make test-fast

# Run specific test file
python -m pytest tests/unit/test_bug_injection.py -v

# Run tests matching pattern
python -m pytest -k "test_inject_bug" -v
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)
- Mock external dependencies
- Test both success and failure cases

### Example Test

```python
import pytest
from unittest.mock import Mock, patch
from core.bug_injection import BugInjectionEngine

class TestBugInjection:
    """Test bug injection functionality."""
    
    def test_inject_bug_success(self):
        """Test successful bug injection."""
        # Arrange
        engine = BugInjectionEngine(Path("."))
        template_id = "test_template"
        file_path = "test.py"
        line_number = 10
        
        # Act
        result = engine.inject_bug(template_id, file_path, line_number)
        
        # Assert
        assert result.success is True
        assert result.modifications is not None
        assert len(result.modifications) > 0
```

## Pull Request Process

### 1. Prepare Your Changes

- Ensure all tests pass: `make test`
- Run code quality checks: `make quality-check`
- Update documentation if needed
- Add tests for new functionality

### 2. Commit Your Changes

Use conventional commit messages:

```bash
# Format: type(scope): description
git commit -m "feat(bug-injection): add support for custom bug patterns"

# Types: feat, fix, docs, style, refactor, test, chore
# Scopes: bug-injection, evaluation, cli, core, etc.
```

### 3. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Screenshots** if UI changes were made
- **Test instructions** for reviewers
- **Related issues** if applicable

### 4. PR Review Process

- All PRs require at least one review
- Address review comments promptly
- Maintainers may request changes
- Once approved, maintainers will merge

## Bug Reports

### Before Reporting

1. Check if the issue is already reported
2. Try to reproduce the issue
3. Check if it's a configuration issue

### Bug Report Template

```markdown
**Bug Description**
Clear description of what happened

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.9.6]
- ReviewLab: [e.g., 0.1.0]

**Additional Context**
Any other information that might help
```

## Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature you'd like

**Use Case**
Why this feature would be useful

**Proposed Implementation**
How you think it could be implemented (optional)

**Alternatives Considered**
Other ways to solve the problem (optional)
```

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers
- Be patient with questions
- Respect different viewpoints

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Any conduct inappropriate in a professional setting

### Enforcement

Violations will be addressed by the project maintainers. We reserve the right to remove, edit, or reject comments, commits, code, and other contributions that are not aligned with this Code of Conduct.

## Getting Help

### Questions and Discussion

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and docs first

### Development Questions

- **Code Review**: Ask questions in PR reviews
- **Issue Comments**: Discuss implementation details in issues
- **Maintainer Contact**: Reach out to maintainers directly

## Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **Release Notes**: Credit for significant contributions
- **GitHub**: Contributor statistics and profile

## License

By contributing to ReviewLab, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to ReviewLab! 🚀

*This contributing guide is inspired by best practices from the open source community.*
