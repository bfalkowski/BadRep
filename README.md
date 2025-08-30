# Bug-Seeded PR Generator + Review-Accuracy Evaluator

A self-contained repository that generates pull requests with intentionally injected bugs, maintains ground truth logs, and evaluates code review bot accuracy across multiple programming languages.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI tool
python -m cli.main --help
```

## 🎯 What This Tool Does

1. **Generate PRs with injected bugs** across Java, Python, JavaScript, and Go
2. **Maintain ground truth logs** of every injected bug for evaluation
3. **Evaluate review bot accuracy** with precision/recall/F1 metrics
4. **Support both CLI and CI workflows** for automation

## 🏗️ Project Structure

```
/
├── tooling/           # Configuration and templates
├── src/              # Baseline projects by language
├── cli/              # Command-line interface
├── core/             # Core engine and logic
├── plugins/          # Language-specific plugins
└── tests/            # Test suite
```

## 🔧 Supported Languages

- **Java** (default)
- **Python**
- **JavaScript/Node.js**
- **Go**

## 📚 Documentation

- [Specification](spec.md) - Complete feature overview
- [Requirements](REQUIREMENTS.md) - Implementation roadmap
- [Architecture](ARCHITECTURE.md) - Technical design details
- [Tasks](task.md) - Development progress tracking

## 🚧 Development Status

**Current Phase**: Phase 1 - Project Scaffolding & Core Infrastructure

This project is under active development. See [task.md](task.md) for current progress and upcoming features.

## 📄 License

MIT License - see LICENSE file for details.
