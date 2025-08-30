# Technical Architecture: Bug-Seeded PR Generator

## System Overview

The Bug-Seeded PR Generator is a modular, extensible system designed to inject realistic bugs into code repositories and evaluate the accuracy of code review bots. The architecture follows a plugin-based design with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer    │    │  Core Engine    │    │  Language       │
│                 │    │                 │    │  Plugins        │
│ - Command      │◄──►│ - Bug Injection │◄──►│ - Java         │
│ - Config Mgmt  │    │ - Git Ops       │    │ - Python       │
│ - User I/O     │    │ - Evaluation    │    │ - JavaScript   │
└─────────────────┘    └─────────────────┘    │ - Go           │
                                              └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Configuration  │    │   Templates     │    │   Evaluation    │
│                 │    │                 │    │                 │
│ - YAML Config  │    │ - Bug Patterns  │    │ - Metrics       │
│ - Env Vars     │    │ - Language      │    │ - Reports       │
│ - CLI Override │    │ - Severity      │    │ - Matching      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. CLI Layer (`cli/`)

**Technology**: Click or Typer (Python CLI framework)

**Responsibilities**:
- Command parsing and routing
- User input validation
- Help and documentation
- Progress indication
- Error reporting

**Key Classes**:
```python
class ReviewLabCLI:
    def __init__(self):
        self.config = ConfigManager()
        self.engine = CoreEngine()
    
    def generate_pr(self, count, types, seed, dry_run):
        # Command implementation
    
    def evaluate(self, pr_id, findings, matcher):
        # Command implementation
```

### 2. Core Engine (`core/`)

**Responsibilities**:
- Orchestrating bug injection workflow
- Managing Git operations
- Coordinating language plugins
- Handling evaluation requests

**Key Classes**:
```python
class CoreEngine:
    def __init__(self, config):
        self.config = config
        self.language_plugin = self._load_language_plugin()
        self.git_manager = GitManager()
        self.bug_injector = BugInjector()
    
    def generate_pr(self, params):
        # Main workflow orchestration
    
    def evaluate_findings(self, pr_id, findings):
        # Evaluation orchestration
```

### 3. Language Plugins (`plugins/languages/`)

**Architecture**: Plugin-based system with common interface

**Base Interface**:
```python
class LanguagePlugin(ABC):
    @abstractmethod
    def get_baseline_project(self) -> BaselineProject:
        pass
    
    @abstractmethod
    def inject_bug(self, file_path: str, bug_type: str, context: dict) -> BugInjection:
        pass
    
    @abstractmethod
    def validate_build(self, project_path: str) -> BuildResult:
        pass
    
    @abstractmethod
    def get_bug_templates(self) -> List[BugTemplate]:
        pass
```

**Plugin Implementation Example (Java)**:
```python
class JavaPlugin(LanguagePlugin):
    def __init__(self):
        self.parser = JavaASTParser()
        self.templates = self._load_templates()
    
    def inject_bug(self, file_path, bug_type, context):
        template = self.templates[bug_type]
        return self._apply_template(file_path, template, context)
```

### 4. Bug Injection Engine (`core/injection/`)

**Responsibilities**:
- Parsing source code (AST-based)
- Applying bug templates
- Preserving buildability
- Generating diffs

**Key Classes**:
```python
class BugInjector:
    def __init__(self, language_plugin):
        self.language_plugin = language_plugin
        self.parser = language_plugin.get_parser()
    
    def inject_bug(self, file_path, bug_template, context):
        ast = self.parser.parse_file(file_path)
        modified_ast = self._apply_bug_pattern(ast, bug_template, context)
        return self._generate_diff(file_path, ast, modified_ast)
```

### 5. Git Manager (`core/git/`)

**Responsibilities**:
- Branch management
- Commit creation
- Remote operations
- Conflict resolution

**Key Classes**:
```python
class GitManager:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)
        self.remote_config = self._load_remote_config()
    
    def create_branch(self, branch_name, base_branch):
        # Branch creation logic
    
    def commit_changes(self, message, files):
        # Commit logic
    
    def push_branch(self, branch_name, remote_name):
        # Push logic
```

### 6. Evaluation Engine (`core/evaluation/`)

**Responsibilities**:
- Parsing bot findings
- Matching against ground truth
- Calculating metrics
- Generating reports

**Key Classes**:
```python
class EvaluationEngine:
    def __init__(self, config):
        self.config = config
        self.matchers = self._load_matchers()
    
    def evaluate_findings(self, pr_id, findings, ground_truth):
        matches = self._find_matches(findings, ground_truth)
        metrics = self._calculate_metrics(matches)
        return self._generate_report(metrics, matches)
```

## Data Models

### 1. Bug Template Schema

```yaml
bug_template:
  id: "correctness.off_by_one"
  name: "Off-by-One Error"
  description: "Incorrect loop boundary condition"
  category: "correctness"
  severity: "medium"
  language: "java"
  
  patterns:
    - name: "loop_boundary"
      description: "Change <= to < in loop condition"
      before: "for (int i = 0; i <= array.length; i++)"
      after: "for (int i = 0; i < array.length; i++)"
      
  constraints:
    - type: "syntax_check"
      rule: "must_compile"
    - type: "test_check"
      rule: "tests_must_pass"
      
  hints:
    - "Look for loop boundary conditions"
    - "Check array indexing patterns"
```

### 2. Ground Truth Log Schema

```json
{
  "bug_id": "uuid-v4",
  "pr_id": "pr_number_or_identifier",
  "branch": "feature_branch_name",
  "file_path": "relative/path/to/file",
  "start_line": 15,
  "end_line": 17,
  "bug_type": "correctness.off_by_one",
  "severity": "medium",
  "short_description": "Off-by-one error in loop condition",
  "injected_diff_summary": "- for (int i = 0; i <= array.length; i++)",
  "seed": 12345,
  "timestamp": "2024-01-15T10:30:00Z",
  "hints": ["Look for loop boundary condition"],
  "metadata": {
    "template_version": "1.0",
    "injection_method": "ast_replacement",
    "build_status": "success",
    "test_status": "success"
  }
}
```

### 3. Bot Findings Schema

```json
{
  "file_path": "relative/path/to/file",
  "start_line": 15,
  "end_line": 17,
  "issue_type": "bug",
  "message": "Potential off-by-one error in loop",
  "severity": "medium",
  "confidence": 0.85,
  "suggestion": "Change <= to < in loop condition",
  "rule_id": "loop_boundary_check",
  "metadata": {
    "tool": "code_review_bot",
    "version": "1.2.0",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

## Configuration Management

### Configuration Hierarchy

1. **Defaults** (hardcoded in code)
2. **User Config** (`~/.reviewlab/config.yaml`)
3. **Project Config** (`./reviewlab.yaml`)
4. **Environment Variables** (`REVIEWLAB_*`)
5. **CLI Arguments** (highest priority)

### Configuration Schema

```yaml
# Global Configuration
language: java
verbose: false
dry_run: false

# Bug Injection Settings
bug_mix:
  correctness: 0.3
  api_misuse: 0.2
  resource_handling: 0.15
  security_lite: 0.1
  maintainability: 0.15
  test_issues: 0.1

injection:
  allow_build_breakers: false
  assistive_markers: false
  max_bugs_per_file: 3
  preserve_tests: true

# Git Settings
git:
  remote: origin
  base_branch: main
  auto_push: true
  commit_message_template: "feat: {feature} with injected bugs"

# Evaluation Settings
evaluation:
  default_matcher: overlap
  line_tolerance: 2
  confidence_threshold: 0.7
  report_formats: [json, markdown]

# Language-Specific Settings
languages:
  java:
    build_tool: maven
    test_command: "mvn test"
    source_dir: "src/main/java"
    
  python:
    build_tool: pip
    test_command: "pytest"
    source_dir: "src"
```

## Plugin System Architecture

### Plugin Discovery

```python
class PluginManager:
    def __init__(self):
        self.plugin_dir = "plugins"
        self.plugins = {}
        self._discover_plugins()
    
    def _discover_plugins(self):
        for plugin_dir in os.listdir(self.plugin_dir):
            if os.path.isdir(os.path.join(self.plugin_dir, plugin_dir)):
                plugin = self._load_plugin(plugin_dir)
                self.plugins[plugin_dir] = plugin
    
    def get_plugin(self, name):
        return self.plugins.get(name)
```

### Plugin Interface

```python
class BugTemplatePlugin(ABC):
    @abstractmethod
    def get_templates(self) -> List[BugTemplate]:
        pass
    
    @abstractmethod
    def validate_template(self, template: BugTemplate) -> bool:
        pass
    
    @abstractmethod
    def apply_template(self, file_path: str, template: BugTemplate) -> BugInjection:
        pass

class LanguagePlugin(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_build_tool(self) -> str:
        pass
    
    @abstractmethod
    def validate_build(self, project_path: str) -> BuildResult:
        pass
```

## Error Handling Strategy

### Error Categories

1. **Configuration Errors**: Invalid config, missing files
2. **Language Errors**: Unsupported language, build failures
3. **Git Errors**: Branch conflicts, push failures
4. **Injection Errors**: Template failures, syntax errors
5. **Evaluation Errors**: Invalid input, matching failures

### Error Handling Patterns

```python
class ReviewLabError(Exception):
    def __init__(self, message, error_code, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ErrorHandler:
    def handle_error(self, error, context):
        if isinstance(error, ConfigurationError):
            return self._handle_config_error(error, context)
        elif isinstance(error, LanguageError):
            return self._handle_language_error(error, context)
        # ... other error types
    
    def _handle_config_error(self, error, context):
        # Provide helpful suggestions for config issues
        pass
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Load plugins and templates only when needed
2. **Caching**: Cache parsed ASTs and compiled templates
3. **Parallel Processing**: Inject multiple bugs concurrently
4. **Incremental Updates**: Only re-parse changed files

### Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation):
        self.metrics[operation] = time.time()
    
    def end_timer(self, operation):
        if operation in self.metrics:
            duration = time.time() - self.metrics[operation]
            self.metrics[operation] = duration
            return duration
```

## Security Considerations

### Input Validation

1. **File Path Sanitization**: Prevent directory traversal
2. **Template Validation**: Ensure templates don't contain malicious code
3. **API Key Security**: Secure storage and usage of API keys
4. **Sandboxing**: Isolate bug injection operations

### Security Implementation

```python
class SecurityManager:
    def validate_file_path(self, file_path):
        # Prevent directory traversal
        normalized = os.path.normpath(file_path)
        if normalized.startswith('..'):
            raise SecurityError("Invalid file path")
        return normalized
    
    def validate_template(self, template):
        # Check for potentially dangerous patterns
        dangerous_patterns = ['exec(', 'eval(', 'import os']
        for pattern in dangerous_patterns:
            if pattern in template.code:
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
```

## Testing Strategy

### Test Types

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Complete workflow testing
4. **Performance Tests**: Load and stress testing

### Test Structure

```
tests/
├── unit/
│   ├── test_cli.py
│   ├── test_core_engine.py
│   ├── test_bug_injector.py
│   └── test_evaluation.py
├── integration/
│   ├── test_java_workflow.py
│   ├── test_python_workflow.py
│   └── test_git_integration.py
├── fixtures/
│   ├── sample_projects/
│   ├── bug_templates/
│   └── test_findings/
└── conftest.py
```

## Deployment and Distribution

### Distribution Methods

1. **PyPI Package**: Standard Python package distribution
2. **Docker Image**: Containerized deployment
3. **GitHub Releases**: Binary distributions
4. **Local Installation**: Development setup

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=reviewlab --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Monitoring and Observability

### Logging Strategy

```python
import logging
import structlog

class LoggerFactory:
    @staticmethod
    def create_logger(name, level=logging.INFO):
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger(name)
```

### Metrics Collection

```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name, value, tags=None):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            'value': value,
            'timestamp': time.time(),
            'tags': tags or {}
        })
    
    def get_metrics(self, name, time_window=None):
        # Return metrics with optional time filtering
        pass
```

This architecture provides a solid foundation for building a robust, extensible bug-seeded PR generator that can support multiple languages and integrate seamlessly with existing development workflows.
