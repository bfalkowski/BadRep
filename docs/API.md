# ReviewLab API Reference

This document provides comprehensive API documentation for ReviewLab's core modules and classes.

## Table of Contents

- [Core Modules](#core-modules)
- [CLI Interface](#cli-interface)
- [Plugin System](#plugin-system)
- [Error Handling](#error-handling)
- [Configuration](#configuration)

## Core Modules

### Bug Injection Engine

#### `BugInjectionEngine`

The main orchestrator for bug injection operations.

```python
from core.bug_injection import BugInjectionEngine

engine = BugInjectionEngine(
    project_path: Path,
    language: str = "java",
    config: Optional[Dict] = None
)
```

**Methods:**

- `inject_bug(template_id: str, file_path: str, line_number: int) -> InjectionResult`
- `inject_multiple_bugs(count: int, bug_types: Optional[List[str]] = None) -> List[InjectionResult]`
- `get_available_templates() -> List[BugTemplate]`
- `validate_injection(file_path: str, line_number: int) -> bool`

**Example:**
```python
engine = BugInjectionEngine(Path("./project"), "java")
result = engine.inject_bug("null_pointer", "src/Main.java", 25)
if result.success:
    print(f"✅ Bug injected: {result.modifications}")
```

#### `BugTemplate`

Represents a bug injection template.

```python
from core.bug_templates import BugTemplate

template = BugTemplate(
    id: str,
    name: str,
    description: str,
    category: BugCategory,
    severity: BugSeverity,
    difficulty: BugDifficulty,
    examples: Dict[str, str]
)
```

**Properties:**
- `id`: Unique identifier
- `name`: Human-readable name
- `description`: Detailed description
- `category`: Bug category (Correctness, Security, Performance, etc.)
- `severity`: Bug severity (Low, Medium, High, Critical)
- `difficulty`: Injection difficulty (Easy, Medium, Hard)
- `examples`: Language-specific code examples

### Evaluation Engine

#### `EvaluationEngine`

Evaluates code review bot findings against ground truth data.

```python
from core.evaluation import EvaluationEngine

evaluator = EvaluationEngine(
    strategies: List[str] = None,
    config: Optional[Dict] = None
)
```

**Methods:**

- `evaluate(findings: List[Finding], ground_truth: List[GroundTruthBug]) -> EvaluationResult`
- `add_strategy(strategy: str, implementation: Callable) -> None`
- `get_available_strategies() -> List[str]`

**Example:**
```python
evaluator = EvaluationEngine(["exact_overlap", "line_range_overlap"])
result = evaluator.evaluate(bot_findings, ground_truth_bugs)
print(f"Precision: {result.precision:.2f}")
print(f"Recall: {result.recall:.2f}")
print(f"F1-Score: {result.f1_score:.2f}")
```

#### `EvaluationResult`

Contains evaluation metrics and detailed results.

```python
@dataclass
class EvaluationResult:
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    total_findings: int
    total_bugs: int
    matched_bugs: int
    false_positives: int
    false_negatives: int
    strategy_results: Dict[str, StrategyResult]
    recommendations: List[str]
```

### Git Operations

#### `GitManager`

Handles Git repository operations.

```python
from core.git_operations import GitManager

git_manager = GitManager(
    repo_path: Path,
    config: Optional[Dict] = None
)
```

**Methods:**

- `create_branch(branch_name: str, base_branch: str = "main") -> str`
- `commit_changes(message: str, files: List[str] = None) -> str`
- `push_branch(branch_name: str, remote: str = "origin") -> bool`
- `get_status() -> GitStatus`
- `reset_to_commit(commit_hash: str) -> bool`

**Example:**
```python
git_manager = GitManager(Path("./project"))
branch = git_manager.create_branch("bug-injection-test")
git_manager.commit_changes("Add injected bugs for testing")
git_manager.push_branch(branch)
```

### GitHub Integration

#### `GitHubManager`

Low-level GitHub API operations.

```python
from core.github_integration import GitHubManager

github = GitHubManager(
    token: str,
    username: str
)
```

**Methods:**

- `get_repository(repo_path: str) -> Repository`
- `create_branch(repo: Repository, base_branch: str, new_branch: str) -> Branch`
- `push_files(repo: Repository, branch: str, files: Dict[str, str], commit_message: str) -> str`
- `create_pull_request(repo: Repository, title: str, body: str, head_branch: str, base_branch: str, draft: bool = False) -> PullRequest`
- `list_pull_requests(repo: Repository, state: str = "open", base: str = None, limit: int = 10) -> List[PullRequest]`

**Example:**
```python
github = GitHubManager(token="ghp_...", username="user")
repo = github.get_repository("owner/repo")
pr = github.create_pull_request(
    repo, "🐛 Bug injection test", "PR body", "bug-branch", "main"
)
```

#### `GitHubWorkflow`

High-level GitHub workflow operations.

```python
from core.github_integration import GitHubWorkflow

workflow = GitHubWorkflow(
    github_manager: GitHubManager,
    config: Optional[Dict] = None
)
```

**Methods:**

- `create_bug_injection_pr(repo_path: str, bugs: List[InjectionResult], title: str = None, body: str = None, draft: bool = False) -> PullRequest`

**Example:**
```python
workflow = GitHubWorkflow(github_manager)
pr = workflow.create_bug_injection_pr(
    "owner/repo", injected_bugs, "🐛 Test bugs", "PR description"
)
```

## CLI Interface

### Main Commands

#### `reviewlab generate-pr`

Generates a pull request with injected bugs.

```bash
reviewlab generate-pr [OPTIONS]

Options:
  --count, -n INTEGER        Number of bugs to inject (default: 5)
  --types TEXT               Comma-separated list of bug types
  --seed INTEGER             Random seed for reproducible generation
  --title TEXT               Custom PR title
  --base TEXT                Base branch (default: main)
  --auto-push                Automatically push branch and create PR
  --dry-run                  Show what would be done without making changes
  --github-repo TEXT         GitHub repository (owner/repo or full URL)
  --github-token TEXT        GitHub Personal Access Token
  --github-username TEXT     GitHub username
  --draft                    Create PR as draft
```

#### `reviewlab evaluate`

Evaluates code review bot findings.

```bash
reviewlab evaluate [OPTIONS]

Options:
  --findings PATH            Path to findings JSON file (required)
  --ground-truth PATH        Path to ground truth JSONL file (required)
  --review-tool TEXT         Name of the review tool being evaluated
  --strategies TEXT          Comma-separated list of matching strategies
  --output-format TEXT       Output format: json, csv, txt, html, all
  --output-dir PATH          Output directory for reports
  --verbose                  Enable verbose output
```

#### `reviewlab list-bugs`

Lists available bug templates.

```bash
reviewlab list-bugs [OPTIONS]

Options:
  --language TEXT            Filter by programming language
  --category TEXT            Filter by bug category
  --severity TEXT            Filter by bug severity
  --difficulty TEXT          Filter by bug difficulty
  --output-format TEXT       Output format: table, json, csv
```

#### `reviewlab demo`

Runs a demonstration workflow.

```bash
reviewlab demo [OPTIONS]

Options:
  --language TEXT            Programming language to use
  --count INTEGER            Number of bugs to inject
  --output-dir PATH          Output directory for results
  --verbose                  Enable verbose output
```

#### `reviewlab list-prs`

Lists pull requests in a GitHub repository.

```bash
reviewlab list-prs [OPTIONS]

Options:
  --repo TEXT                GitHub repository (owner/repo or full URL) (required)
  --github-token TEXT        GitHub Personal Access Token
  --github-username TEXT     GitHub username
  --state TEXT               PR state: open, closed, all (default: open)
  --base TEXT                Filter by base branch
  --limit INTEGER            Maximum number of PRs to show (default: 10)
```

## Plugin System

### Language Plugins

Language plugins implement the `LanguagePlugin` interface:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LanguagePlugin(ABC):
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass
    
    @abstractmethod
    def inject_bug(self, template: BugTemplate, file_path: str, line_number: int) -> InjectionResult:
        """Inject a bug using the given template."""
        pass
    
    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """Validate if the file can be processed."""
        pass
```

### Available Plugins

- **JavaPlugin**: Java source files (.java)
- **PythonPlugin**: Python source files (.py)
- **JavaScriptPlugin**: JavaScript/Node.js files (.js, .jsx, .ts, .tsx)
- **GoPlugin**: Go source files (.go)

### Creating Custom Plugins

```python
from core.plugins.base import LanguagePlugin

class CustomLanguagePlugin(LanguagePlugin):
    def get_supported_extensions(self) -> List[str]:
        return [".custom"]
    
    def inject_bug(self, template: BugTemplate, file_path: str, line_number: int) -> InjectionResult:
        # Custom implementation
        pass
    
    def validate_file(self, file_path: str) -> bool:
        # Custom validation
        pass
```

## Error Handling

### Exception Classes

```python
from core.errors import (
    ReviewLabError,           # Base exception class
    ConfigurationError,       # Configuration-related errors
    ValidationError,          # Validation errors
    GitError,                 # Git operation errors
    InjectionError,           # Bug injection errors
    EvaluationError,          # Evaluation errors
    GitHubError,              # GitHub API errors
    AuthenticationError,      # Authentication errors
    RepositoryError,          # Repository access errors
)
```

### Error Handler

```python
from core.errors import ErrorHandler

# Handle errors with context
ErrorHandler.handle_error(error, "Bug injection")
ErrorHandler.handle_warning("Warning message", "Context")
ErrorHandler.handle_info("Info message", "Context")
ErrorHandler.handle_critical_error(error, "Critical operation")
```

## Configuration

### Configuration File

Create `config.yaml` in your project root:

```yaml
# General configuration
language: java
verbose: true
dry_run: false

# GitHub integration
github:
  default_repo: "owner/repo"
  auto_create_pr: true
  draft_mode: false

# Bug injection
injection:
  default_count: 5
  preferred_categories: ["Correctness", "Security"]
  max_severity: "High"

# Evaluation
evaluation:
  default_strategies: ["exact_overlap", "line_range_overlap"]
  confidence_threshold: 0.8

# Output
output:
  default_format: "all"
  default_directory: "reports"
  include_timestamps: true
```

### Environment Variables

```bash
# GitHub Integration
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_USERNAME="your_github_username"

# ReviewLab Configuration
export REVIEWLAB_LANGUAGE="java"
export REVIEWLAB_VERBOSE="true"
export REVIEWLAB_CONFIG_PATH="./config.yaml"
```

## Data Structures

### Finding

Represents a code review bot finding.

```python
@dataclass
class Finding:
    id: str
    file_path: str
    line_number: int
    message: str
    severity: str
    category: str
    confidence: float
    tool: str
    timestamp: datetime
    metadata: Dict[str, Any]
```

### Ground Truth Bug

Represents an injected bug for evaluation.

```python
@dataclass
class GroundTruthBug:
    id: str
    template_id: str
    file_path: str
    line_number: int
    original_line: str
    modified_line: str
    category: str
    severity: str
    difficulty: str
    injection_timestamp: datetime
    metadata: Dict[str, Any]
```

### Injection Result

Result of a bug injection operation.

```python
@dataclass
class InjectionResult:
    success: bool
    template_id: str
    file_path: str
    line_number: int
    original_line: str
    modified_line: str
    modifications: List[FileModification]
    error_message: Optional[str]
    metadata: Dict[str, Any]
```

## Performance Considerations

### Optimization Tips

1. **Batch Operations**: Use `inject_multiple_bugs()` for multiple injections
2. **Caching**: Template loading is cached by default
3. **Parallel Processing**: Evaluation supports parallel strategy execution
4. **Memory Management**: Large files are processed in chunks

### Benchmarking

```python
from core.evaluation import EvaluationEngine

# Run performance benchmarks
evaluator = EvaluationEngine()
benchmark_results = evaluator.benchmark_strategies(
    test_data, 
    iterations=100
)
print(f"Average evaluation time: {benchmark_results.avg_time:.3f}s")
```

## Troubleshooting

### Common Issues

1. **GitHub Authentication**: Ensure token has `repo` scope
2. **File Permissions**: Check write permissions for target directories
3. **Template Loading**: Verify bug template files are accessible
4. **Git Operations**: Ensure Git repository is properly initialized

### Debug Mode

Enable verbose logging:

```bash
export REVIEWLAB_VERBOSE=true
reviewlab generate-pr --verbose
```

### Log Files

ReviewLab generates detailed logs in the `logs/` directory:

- `injection.log`: Bug injection operations
- `evaluation.log`: Evaluation operations
- `github.log`: GitHub API operations
- `git.log`: Git operations

---

*For more information, see the [README.md](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).*
