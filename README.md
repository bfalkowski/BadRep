# ReviewLab 🐛🔍

**Agentic Bug-Seeded PR Generator + Review-Accuracy Evaluator with REST API**

[![CI - Test & Quality](https://github.com/bryanfalkowski/reviewlab/workflows/CI%20-%20Test%20%26%20Quality/badge.svg)](https://github.com/bryanfalkowski/reviewlab/actions)
[![Release](https://github.com/bryanfalkowski/reviewlab/workflows/Release/badge.svg)](https://github.com/bryanfalkowski/reviewlab/releases)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![API Status](https://img.shields.io/badge/API-Status%3A%20Live-brightgreen.svg)](http://localhost:8000/health)

ReviewLab is a **production-ready, agentic system** for testing code review bot accuracy by generating pull requests with intentionally injected bugs. Now featuring a comprehensive REST API for seamless integration with CI/CD pipelines, automated workflows, and external tools.

## 🚀 **NEW: Agentic REST API System**

### 🌐 **Primary Interface: REST API**
- **Production-Ready API Server** running on FastAPI
- **Interactive Documentation** at `/docs` and `/redoc`
- **Real-time GitHub Integration** with live PR data
- **Automated Workflows** for bug injection and evaluation
- **Multi-client Support** for team deployments

### 🔌 **API-First Architecture**
- **All operations available via HTTP endpoints**
- **JSON-based data exchange**
- **Authentication and rate limiting**
- **Comprehensive error handling**
- **Real-time status monitoring**

---

## 🚀 Features

### 🐛 **Bug Injection Engine**
- **Multi-language Support**: Java, Python, JavaScript, Go
- **Template-based System**: 30+ predefined bug patterns
- **Configurable Injection**: Severity, difficulty, and category-based selection
- **Ground Truth Logging**: Machine-readable logs of every injected bug
- **API Endpoints**: `/api/v1/inject/bugs`, `/api/v1/inject/sessions/{id}`

### 🔍 **Evaluation Engine**
- **Multiple Matching Strategies**: Exact overlap, line range, semantic similarity
- **Comprehensive Metrics**: Precision, Recall, F1-Score, Accuracy
- **Detailed Reports**: JSON, CSV, TXT, and HTML formats
- **Performance Analysis**: Benchmarking and optimization insights
- **API Endpoints**: `/api/v1/evaluate/findings`, `/api/v1/evaluate/reports/{id}`

### 🔗 **GitHub Integration**
- **Real PR Creation**: Generate actual pull requests with injected bugs
- **Repository Management**: Full CRUD operations for branches and PRs
- **Authentication**: Secure token-based GitHub access
- **Workflow Automation**: Streamlined bug injection to PR pipeline
- **API Endpoints**: `/api/v1/github/prs/{owner}/{repo}/{pr_number}/*`

### 🧠 **Learning & Adaptation System**
- **Pattern Analysis**: Learn from evaluation results
- **Adaptive Rules**: Improve detection based on feedback
- **Continuous Improvement**: Self-optimizing review strategies
- **API Endpoints**: `/api/v1/learning/analyze-session/{id}`

### 🛠️ **Developer Experience**
- **REST API**: Primary interface for all operations
- **CLI Interface**: Backup command-line tools with emojis
- **Quality Tools**: Automated formatting, linting, and type checking
- **Testing Suite**: 145+ comprehensive tests with coverage reporting
- **CI/CD Pipeline**: Automated testing, security scanning, and releases

---

## 📋 Quick Start

### **🚀 Primary Method: REST API (Recommended)**

```bash
# Clone the repository
git clone https://github.com/bryanfalkowski/reviewlab.git
cd reviewlab

# Install API dependencies
pip install -r requirements_api.txt

# Start the API server
python start_api_server.py

# Server will be running at:
# - API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### **📖 API Quick Start**

```bash
# Test the API
curl http://localhost:8000/health

# Extract GitHub comments from a PR
curl http://localhost:8000/api/v1/github/prs/bfalkowski/BadRep/1/comments

# Evaluate findings against ground truth
curl -X POST http://localhost:8000/api/v1/evaluate/findings \
  -H "Content-Type: application/json" \
  -d '{"findings_file": "github_findings.json", "ground_truth_file": "ground_truth_clean.jsonl"}'

# Run comprehensive tests
python test_api.py
```

### **🔧 Alternative Method: CLI (Backup)**

```bash
# Install CLI dependencies
pip install -e .
pip install -r requirements-dev.txt

# Use CLI commands (same as before)
reviewlab list-bugs --language java
reviewlab generate-pr --count 3 --language java
reviewlab evaluate --findings findings.json --ground-truth ground_truth.jsonl
```

---

## 🔧 Configuration

### **API Configuration**

```bash
# GitHub Integration
export GITHUB_TOKEN="your_personal_access_token"

# API Server Configuration
export REVIEWLAB_HOST="0.0.0.0"
export REVIEWLAB_PORT="8000"
export REVIEWLAB_LOG_LEVEL="INFO"
```

### **Environment Variables**

```bash
# GitHub Integration
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_USERNAME="your_github_username"

# ReviewLab Configuration
export REVIEWLAB_LANGUAGE="java"
export REVIEWLAB_VERBOSE="true"
```

### **Configuration File**

Create `config.yaml` in your project root:

```yaml
language: java
verbose: true
dry_run: false
api:
  host: "0.0.0.0"
  port: 8000
  log_level: "INFO"
github:
  default_repo: "owner/repo"
  auto_create_pr: true
  draft_mode: false
```

---

## 🌐 **API Reference**

### **Core Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API overview and status |
| `/health` | GET | Health check |
| `/status` | GET | Detailed system status |
| `/docs` | GET | Interactive API documentation |

### **Bug Injection**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/inject/bugs` | POST | Inject bugs into codebase |
| `/api/v1/inject/sessions/{id}` | GET | Get injection session details |

### **GitHub Integration**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/github/prs/{owner}/{repo}/{pr_number}/create` | POST | Create PR with injected bugs |
| `/api/v1/github/prs/{owner}/{repo}/{pr_number}` | GET | Get PR details |
| `/api/v1/github/prs/{owner}/{repo}/{pr_number}/comments` | GET | Extract PR comments |

### **Evaluation**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/evaluate/findings` | POST | Evaluate findings against ground truth |
| `/api/v1/evaluate/reports/{id}` | GET | Get evaluation report |

### **Cleanup & Management**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cleanup/repository/{owner}/{repo}` | POST | Clean up evaluation branches |
| `/api/v1/cleanup/branches/{owner}/{repo}/{branch}` | DELETE | Delete specific branch |

### **Learning System**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/learning/analyze-session/{id}` | POST | Analyze session for learning |

---

## 🔗 GitHub Integration

### **Setting Up GitHub Access**

1. **Create Personal Access Token**:
   - Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
   - Generate new token with `repo` scope
   - Copy the token

2. **Set Environment Variables**:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

3. **Use the API**:
   ```bash
   # Create bug-injected PR via API
   curl -X POST http://localhost:8000/api/v1/github/prs/owner/repo/1/create \
     -H "Content-Type: application/json" \
     -d '{"bug_count": 5, "language": "java", "title": "🐛 Bug injection test"}'
   ```

### **Repository Management via API**

```bash
# List PRs in a repository
curl http://localhost:8000/api/v1/github/prs/owner/repo

# Extract comments from a PR
curl http://localhost:8000/api/v1/github/prs/owner/repo/1/comments

# Clean up evaluation branches
curl -X POST http://localhost:8000/api/v1/cleanup/repository/owner/repo
```

---

## 📊 Evaluation & Reporting

### **Running Evaluations via API**

```bash
# Basic evaluation
curl -X POST http://localhost:8000/api/v1/evaluate/findings \
  -H "Content-Type: application/json" \
  -d '{
    "findings_file": "bot_findings.json",
    "ground_truth_file": "ground_truth.jsonl",
    "review_tool": "CodeQL",
    "strategies": ["exact_overlap", "line_range_overlap"]
  }'

# Get evaluation report
curl http://localhost:8000/api/v1/evaluate/reports/eval_20250830_150605
```

### **Report Formats**

- **JSON**: Machine-readable structured data
- **CSV**: Spreadsheet-compatible format
- **TXT**: Human-readable text report
- **HTML**: Interactive web report with charts

---

## 🧪 Testing & Development

### **Testing the API**

```bash
# Run comprehensive API tests
python test_api.py

# Test individual endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/github/prs/bfalkowski/BadRep/1/comments
```

### **Running Tests**

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

### **Code Quality**

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

---

## 🏗️ Architecture

```
ReviewLab/
├── core/                    # Core functionality
│   ├── api_server.py       # 🆕 FastAPI server (PRIMARY)
│   ├── models.py           # 🆕 API data models
│   ├── bug_injection.py    # Bug injection engine
│   ├── evaluation.py       # Evaluation engine
│   ├── git_operations.py   # Git operations
│   ├── github_integration.py # GitHub API integration
│   ├── github_comments.py  # 🆕 GitHub comment extraction
│   └── plugins/            # Language-specific plugins
├── cli/                    # Command-line interface (BACKUP)
│   └── main.py            # CLI entry point
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── reports/                # 🆕 Generated reports
├── start_api_server.py     # 🆕 API server launcher
├── test_api.py            # 🆕 API test suite
└── src/                    # Baseline projects
    ├── java/              # Java baseline
    ├── python/            # Python baseline
    ├── javascript/        # JavaScript baseline
    └── go/                # Go baseline
```

---

## 🔒 Security

ReviewLab includes comprehensive security features:

- **Input Validation**: All API inputs are validated and sanitized
- **Path Traversal Protection**: Secure file path handling
- **Template Security**: Bug injection templates are validated
- **Authentication**: Secure GitHub token handling
- **Isolation**: Bug injection runs in isolated sessions
- **API Security**: CORS, rate limiting, and input validation

See [SECURITY.md](SECURITY.md) for detailed security information.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- Code of conduct

### **Quick Contribution**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks: `make quality-check`
6. Submit a pull request

---

## 📈 CI/CD Pipeline

ReviewLab uses GitHub Actions for continuous integration:

- **Automated Testing**: Multi-Python version matrix (3.8-3.11)
- **Code Quality**: Automated linting, formatting, and type checking
- **Security Scanning**: Bandit and Safety vulnerability checks
- **Dependency Updates**: Dependabot automated dependency management
- **Automated Releases**: Tag-based release automation
- **Coverage Reporting**: Codecov integration

---

## 📚 Documentation

- **Agentic Features**: [docs/PHASE_11_AGENTIC_FEATURES.md](docs/PHASE_11_AGENTIC_FEATURES.md)
- **Development TODO**: [TODO.md](TODO.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Requirements**: [REQUIREMENTS.md](REQUIREMENTS.md)
- **Specification**: [spec.md](spec.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)

---

## 🎯 Use Cases

### **API-First Integration**
- **CI/CD Pipeline Integration**: Seamless integration with automated workflows
- **External Tool Integration**: Connect with any HTTP-capable tool
- **Team Deployments**: Multi-client support for development teams
- **Enterprise Integration**: REST API for enterprise toolchains

### **Code Review Bot Evaluation**
- Test the accuracy of automated code review tools
- Measure false positive/negative rates
- Benchmark different review strategies
- Validate security scanning effectiveness

### **Quality Assurance Training**
- Train developers to spot common bugs
- Practice code review skills
- Validate bug detection capabilities
- Benchmark team performance

### **Research & Development**
- Evaluate new static analysis techniques
- Research bug pattern detection
- Develop automated testing strategies
- Academic research and publications

---

## 🚀 Roadmap

### **Phase 11: Agentic System (COMPLETE ✅)**
- [x] **Phase 11.1**: GitHub Comment Extraction - COMPLETE
- [x] **Phase 11.2**: REST API Foundation - COMPLETE
- [ ] **Phase 11.3**: Cleanup System (Next)
- [ ] **Phase 11.5**: Learning System (Future)

### **Future Enhancements**
- [ ] **Phase 12**: Advanced Learning & AI
- [ ] **Phase 13**: Enterprise Features
- [ ] **Phase 14**: Database Evolution & Scalability
- [ ] **Phase 15**: Cloud Integration & Deployment

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Open Source Community**: For inspiration and best practices
- **GitHub**: For providing excellent APIs and Actions
- **Python Community**: For amazing tools and libraries
- **FastAPI**: For the excellent web framework
- **Contributors**: Everyone who helps improve ReviewLab

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/bryanfalkowski/reviewlab/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bryanfalkowski/reviewlab/discussions)
- **Security**: security@reviewlab.dev
- **Documentation**: [Project Wiki](https://github.com/bryanfalkowski/reviewlab/wiki)
- **API Status**: http://localhost:8000/health (when running)

---

**Made with ❤️ by the ReviewLab Team**

*ReviewLab - Now a production-ready, agentic system for code review bot evaluation! 🚀✨*

---

## 🎉 **What's New in v2.0**

### **Agentic Transformation Complete!**
- **From CLI tool** → **Production REST API**
- **From manual workflows** → **Automated, agentic processes**
- **From single-user** → **Multi-client, team-ready system**
- **From research tool** → **Enterprise-ready service**

### **Ready for Production**
- **Live GitHub integration** with real PR data
- **Comprehensive API** for all operations
- **Interactive documentation** for easy integration
- **Scalable architecture** for team deployments

**Start using the API today**: `python start_api_server.py` 🚀
