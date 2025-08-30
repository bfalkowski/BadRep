# ReviewLab 🐛🔍

**Bug-Seeded PR Generator + Review-Accuracy Evaluator**

[![CI - Test & Quality](https://github.com/bryanfalkowski/reviewlab/workflows/CI%20-%20Test%20%26%20Quality/badge.svg)](https://github.com/bryanfalkowski/reviewlab/actions)
[![Release](https://github.com/bryanfalkowski/reviewlab/workflows/Release/badge.svg)](https://github.com/bryanfalkowski/reviewlab/releases)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

ReviewLab is a powerful tool for testing code review bot accuracy by generating pull requests with intentionally injected bugs. Perfect for evaluating the effectiveness of automated code review tools, security scanners, and static analysis tools.

## 🚀 Features

### 🐛 **Bug Injection Engine**
- **Multi-language Support**: Java, Python, JavaScript, Go
- **Template-based System**: 30+ predefined bug patterns
- **Configurable Injection**: Severity, difficulty, and category-based selection
- **Ground Truth Logging**: Machine-readable logs of every injected bug

### 🔍 **Evaluation Engine**
- **Multiple Matching Strategies**: Exact overlap, line range, semantic similarity
- **Comprehensive Metrics**: Precision, Recall, F1-Score, Accuracy
- **Detailed Reports**: JSON, CSV, TXT, and HTML formats
- **Performance Analysis**: Benchmarking and optimization insights

### 🔗 **GitHub Integration**
- **Real PR Creation**: Generate actual pull requests with injected bugs
- **Repository Management**: Full CRUD operations for branches and PRs
- **Authentication**: Secure token-based GitHub access
- **Workflow Automation**: Streamlined bug injection to PR pipeline

### 🛠️ **Developer Experience**
- **CLI Interface**: Intuitive command-line tools with emojis
- **Quality Tools**: Automated formatting, linting, and type checking
- **Testing Suite**: 145+ comprehensive tests with coverage reporting
- **CI/CD Pipeline**: Automated testing, security scanning, and releases

## 📋 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/bryanfalkowski/reviewlab.git
cd reviewlab

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

### Basic Usage

```bash
# List available bug types
reviewlab list-bugs --language java

# Generate a PR with injected bugs (local mode)
reviewlab generate-pr --count 3 --language java --auto-push

# Generate a PR with injected bugs (GitHub mode)
export GITHUB_TOKEN="your_token_here"
export GITHUB_USERNAME="your_username"
reviewlab generate-pr --count 3 --language java --github-repo owner/repo

# Evaluate code review bot findings
reviewlab evaluate --findings findings.json --ground-truth ground_truth.jsonl

# Run a quick demo
reviewlab demo --language java
```

## 🔧 Configuration

### Environment Variables

```bash
# GitHub Integration
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_USERNAME="your_github_username"

# ReviewLab Configuration
export REVIEWLAB_LANGUAGE="java"
export REVIEWLAB_VERBOSE="true"
```

### Configuration File

Create `config.yaml` in your project root:

```yaml
language: java
verbose: true
dry_run: false
github:
  default_repo: "owner/repo"
  auto_create_pr: true
  draft_mode: false
```

## 🐛 Bug Categories

ReviewLab supports comprehensive bug taxonomy:

| Category | Description | Examples |
|----------|-------------|----------|
| **Correctness** | Logic errors and bugs | Null pointer dereference, off-by-one errors |
| **Security** | Security vulnerabilities | SQL injection, XSS, buffer overflow |
| **Performance** | Performance issues | Memory leaks, inefficient algorithms |
| **Maintainability** | Code quality issues | Magic numbers, hardcoded values |
| **Reliability** | Error handling issues | Uncaught exceptions, resource leaks |
| **Usability** | User experience issues | Poor error messages, confusing APIs |

## 🔗 GitHub Integration

### Setting Up GitHub Access

1. **Create Personal Access Token**:
   - Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
   - Generate new token with `repo` scope
   - Copy the token

2. **Set Environment Variables**:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   export GITHUB_USERNAME="your_username"
   ```

3. **Create Bug-Injected PRs**:
   ```bash
   reviewlab generate-pr \
     --count 5 \
     --language java \
     --github-repo "owner/repo" \
     --title "🐛 Bug injection test PR" \
     --draft
   ```

### Repository Management

```bash
# List PRs in a repository
reviewlab list-prs --repo "owner/repo" --state open

# List PRs by base branch
reviewlab list-prs --repo "owner/repo" --base "main" --limit 20
```

## 📊 Evaluation & Reporting

### Running Evaluations

```bash
# Basic evaluation
reviewlab evaluate \
  --findings "bot_findings.json" \
  --ground-truth "ground_truth.jsonl" \
  --review-tool "CodeQL" \
  --strategies "exact_overlap,line_range_overlap" \
  --output-format "all"

# Verbose evaluation with custom strategies
reviewlab evaluate \
  --findings "findings.json" \
  --ground-truth "truth.jsonl" \
  --review-tool "SonarQube" \
  --strategies "exact_overlap,semantic_similarity,breadcrumb_matching" \
  --output-format "html" \
  --output-dir "reports/" \
  --verbose
```

### Report Formats

- **JSON**: Machine-readable structured data
- **CSV**: Spreadsheet-compatible format
- **TXT**: Human-readable text report
- **HTML**: Interactive web report with charts

## 🧪 Testing & Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

### Code Quality

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

### Development Workflow

```bash
# Install development dependencies
make install-dev

# Install pre-commit hooks
make install-hooks

# Clean up generated files
make clean

# Generate HTML test report
make html-report
```

## 🏗️ Architecture

```
ReviewLab/
├── core/                    # Core functionality
│   ├── bug_injection.py    # Bug injection engine
│   ├── evaluation.py       # Evaluation engine
│   ├── git_operations.py   # Git operations
│   ├── github_integration.py # GitHub API integration
│   └── plugins/            # Language-specific plugins
├── cli/                    # Command-line interface
│   └── main.py            # CLI entry point
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── src/                    # Baseline projects
    ├── java/              # Java baseline
    ├── python/            # Python baseline
    ├── javascript/        # JavaScript baseline
    └── go/                # Go baseline
```

## 🔒 Security

ReviewLab includes comprehensive security features:

- **Input Validation**: All inputs are validated and sanitized
- **Path Traversal Protection**: Secure file path handling
- **Template Security**: Bug injection templates are validated
- **Authentication**: Secure GitHub token handling
- **Isolation**: Bug injection runs in isolated sessions

See [SECURITY.md](SECURITY.md) for detailed security information.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- Code of conduct

### Quick Contribution

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks: `make quality-check`
6. Submit a pull request

## 📈 CI/CD Pipeline

ReviewLab uses GitHub Actions for continuous integration:

- **Automated Testing**: Multi-Python version matrix (3.8-3.11)
- **Code Quality**: Automated linting, formatting, and type checking
- **Security Scanning**: Bandit and Safety vulnerability checks
- **Dependency Updates**: Dependabot automated dependency management
- **Automated Releases**: Tag-based release automation
- **Coverage Reporting**: Codecov integration

## 📚 Documentation

- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Requirements**: [REQUIREMENTS.md](REQUIREMENTS.md)
- **Specification**: [spec.md](spec.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)

## 🎯 Use Cases

### Code Review Bot Evaluation
- Test the accuracy of automated code review tools
- Measure false positive/negative rates
- Benchmark different review strategies
- Validate security scanning effectiveness

### Quality Assurance Training
- Train developers to spot common bugs
- Practice code review skills
- Validate bug detection capabilities
- Benchmark team performance

### Research & Development
- Evaluate new static analysis techniques
- Research bug pattern detection
- Develop automated testing strategies
- Academic research and publications

### CI/CD Pipeline Testing
- Validate security scanning in pipelines
- Test automated review processes
- Measure pipeline effectiveness
- Continuous improvement validation

## 🚀 Roadmap

### Phase 10: Documentation & Final Polish
- [ ] Comprehensive user documentation
- [ ] API reference documentation
- [ ] Tutorial videos and examples
- [ ] Performance optimization
- [ ] Additional language support

### Future Enhancements
- [ ] Docker containerization
- [ ] Web-based interface
- [ ] Plugin marketplace
- [ ] Enterprise features
- [ ] Cloud integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open Source Community**: For inspiration and best practices
- **GitHub**: For providing excellent APIs and Actions
- **Python Community**: For amazing tools and libraries
- **Contributors**: Everyone who helps improve ReviewLab

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/bryanfalkowski/reviewlab/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bryanfalkowski/reviewlab/discussions)
- **Security**: security@reviewlab.dev
- **Documentation**: [Project Wiki](https://github.com/bryanfalkowski/reviewlab/wiki)

---

**Made with ❤️ by the ReviewLab Team**

*ReviewLab - Making code review bot evaluation simple, accurate, and fun! 🎉*
