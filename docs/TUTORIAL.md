# ReviewLab Tutorial

This tutorial will walk you through using ReviewLab to test code review bot accuracy. By the end, you'll be able to generate pull requests with injected bugs and evaluate how well your code review tools detect them.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Step-by-Step Workflow](#step-by-step-workflow)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting this tutorial, ensure you have:

- **Python 3.8+** installed
- **Git** installed and configured
- **GitHub account** (for remote PR creation)
- **Basic knowledge** of command line tools

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bryanfalkowski/reviewlab.git
cd reviewlab
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
reviewlab --version
reviewlab --help
```

You should see the ReviewLab version and available commands.

## Quick Start

Let's run a quick demo to see ReviewLab in action:

```bash
# Run a demo with Java (default)
reviewlab demo --language java --count 3

# Check the results
ls reports/
```

This will:
1. Create a temporary Java project
2. Inject 3 bugs
3. Generate evaluation reports
4. Clean up temporary files

## Step-by-Step Workflow

### Step 1: Explore Available Bug Types

First, let's see what types of bugs ReviewLab can inject:

```bash
# List all available bug types
reviewlab list-bugs

# Filter by language
reviewlab list-bugs --language java

# Filter by category
reviewlab list-bugs --category Security

# Filter by severity
reviewlab list-bugs --severity High

# Get detailed output
reviewlab list-bugs --output-format json
```

**Example Output:**
```
🐛 Available Bug Templates (Java)

Category: Correctness
├── null_pointer_dereference
│   ├── Severity: High
│   ├── Difficulty: Easy
│   └── Description: Removes null check before dereferencing
├── off_by_one_error
│   ├── Severity: Medium
│   ├── Difficulty: Medium
│   └── Description: Changes loop boundary condition

Category: Security
├── sql_injection
│   ├── Severity: Critical
│   ├── Difficulty: Hard
│   └── Description: Removes input validation
```

### Step 2: Set Up Your Project

Create a directory for your test project:

```bash
mkdir my-test-project
cd my-test-project

# Initialize Git repository
git init
git remote add origin https://github.com/yourusername/your-repo.git
```

### Step 3: Add Some Code

Create a simple Java file to inject bugs into:

```bash
mkdir -p src/main/java
```

Create `src/main/java/Calculator.java`:

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
    
    public double divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return (double) a / b;
    }
}
```

### Step 4: Inject Bugs

Now let's inject some bugs into your code:

```bash
# Inject 3 bugs
reviewlab generate-pr \
  --count 3 \
  --language java \
  --title "🐛 Bug injection test PR" \
  --auto-push
```

**What happens:**
1. ReviewLab scans your project for Java files
2. Selects 3 random bug templates
3. Injects bugs at appropriate locations
4. Creates a new Git branch
5. Commits the changes
6. Pushes the branch

### Step 5: Check the Results

View the injected bugs:

```bash
# Check Git status
git status

# View the changes
git diff main

# Check ground truth log
cat ground_truth.jsonl
```

**Example ground truth entry:**
```json
{
  "id": "bug_001",
  "template_id": "null_pointer_dereference",
  "file_path": "src/main/java/Calculator.java",
  "line_number": 15,
  "original_line": "if (b == 0) {",
  "modified_line": "if (false) {",
  "category": "Correctness",
  "severity": "High",
  "difficulty": "Easy",
  "injection_timestamp": "2024-01-15T10:30:00Z"
}
```

### Step 6: Create a Pull Request

If you want to create a GitHub PR:

```bash
# Set GitHub credentials
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_USERNAME="your_username"

# Create PR on GitHub
reviewlab generate-pr \
  --count 3 \
  --language java \
  --github-repo "yourusername/your-repo" \
  --title "🐛 Bug injection test PR" \
  --draft
```

### Step 7: Run Your Code Review Bot

Now run your code review bot (e.g., SonarQube, CodeQL, etc.) on the PR. The bot should detect some of the injected bugs.

### Step 8: Evaluate Results

Collect your bot's findings and save them to a JSON file. Then evaluate:

```bash
# Evaluate bot findings against ground truth
reviewlab evaluate \
  --findings "bot_findings.json" \
  --ground-truth "ground_truth.jsonl" \
  --review-tool "SonarQube" \
  --output-format "all"
```

**Example findings format:**
```json
[
  {
    "id": "finding_001",
    "file_path": "src/main/java/Calculator.java",
    "line_number": 15,
    "message": "Condition is always false",
    "severity": "Major",
    "category": "Bug",
    "confidence": 0.95,
    "tool": "SonarQube"
  }
]
```

### Step 9: Analyze the Report

ReviewLab generates comprehensive reports:

```bash
# View HTML report
open reports/evaluation_report.html

# Check CSV for data analysis
cat reports/evaluation_report.csv

# View text summary
cat reports/evaluation_report.txt
```

**Example metrics:**
```
📊 Evaluation Results for SonarQube

Overall Metrics:
├── Precision: 0.75 (3/4 findings were correct)
├── Recall: 0.60 (3/5 bugs were detected)
├── F1-Score: 0.67
└── Accuracy: 0.75

Strategy Results:
├── Exact Overlap: 3 matches
├── Line Range Overlap: 0 matches
└── Semantic Similarity: 0 matches

Recommendations:
├── Consider adjusting detection sensitivity
├── Review false positive patterns
└── Optimize for high-severity bugs
```

## Advanced Usage

### Custom Bug Selection

```bash
# Inject specific bug types
reviewlab generate-pr \
  --count 5 \
  --types "null_pointer_dereference,sql_injection,buffer_overflow" \
  --language java

# Use specific seed for reproducible results
reviewlab generate-pr \
  --count 3 \
  --seed 42 \
  --language java
```

### Multiple Language Support

```bash
# Test with Python
reviewlab generate-pr --language python --count 3

# Test with JavaScript
reviewlab generate-pr --language javascript --count 3

# Test with Go
reviewlab generate-pr --language go --count 3
```

### Advanced Evaluation

```bash
# Use specific matching strategies
reviewlab evaluate \
  --findings "findings.json" \
  --ground-truth "truth.jsonl" \
  --strategies "exact_overlap,semantic_similarity" \
  --output-format "html" \
  --output-dir "custom_reports"

# Enable verbose output
reviewlab evaluate \
  --findings "findings.json" \
  --ground-truth "truth.jsonl" \
  --verbose
```

### Batch Processing

```bash
# Generate multiple PRs with different configurations
for lang in java python javascript go; do
  reviewlab generate-pr \
    --language $lang \
    --count 5 \
    --title "🐛 $lang bug injection test" \
    --auto-push
done
```

### Integration with CI/CD

Create a GitHub Actions workflow:

```yaml
name: Bug Injection Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install ReviewLab
      run: |
        pip install -e .
    
    - name: Run bug injection test
      run: |
        reviewlab demo --language java --count 5
        reviewlab evaluate \
          --findings "ci_findings.json" \
          --ground-truth "ground_truth.jsonl" \
          --output-format "json"
```

## Troubleshooting

### Common Issues

#### 1. "No supported files found"

**Problem**: ReviewLab can't find files to inject bugs into.

**Solution**: Ensure your project has files with supported extensions:
- Java: `.java`
- Python: `.py`
- JavaScript: `.js`, `.jsx`, `.ts`, `.tsx`
- Go: `.go`

#### 2. "GitHub authentication failed"

**Problem**: Can't create GitHub PRs.

**Solution**: Check your token:
```bash
# Verify token has repo scope
export GITHUB_TOKEN="your_token"
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

#### 3. "Template not found"

**Problem**: Bug template doesn't exist.

**Solution**: Check available templates:
```bash
reviewlab list-bugs --language java
```

#### 4. "Evaluation failed"

**Problem**: Can't evaluate bot findings.

**Solution**: Verify file formats:
```bash
# Check ground truth format
head -1 ground_truth.jsonl | jq .

# Check findings format
head -1 findings.json | jq .
```

### Debug Mode

Enable verbose logging:

```bash
export REVIEWLAB_VERBOSE=true
reviewlab generate-pr --verbose
```

### Getting Help

```bash
# Command help
reviewlab --help
reviewlab generate-pr --help
reviewlab evaluate --help

# List available options
reviewlab list-bugs --help
```

## Next Steps

Now that you've completed the tutorial:

1. **Experiment** with different bug types and languages
2. **Integrate** ReviewLab into your development workflow
3. **Customize** bug templates for your specific needs
4. **Contribute** improvements to the project
5. **Share** your experiences with the community

## Additional Resources

- [API Reference](API.md) - Detailed API documentation
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Security Policy](../SECURITY.md) - Security information
- [GitHub Issues](https://github.com/bryanfalkowski/reviewlab/issues) - Report bugs or request features

---

**Happy bug hunting! 🐛🔍**

*ReviewLab makes code review bot evaluation simple, accurate, and fun!*
