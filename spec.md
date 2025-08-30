# Bug-Seeded PR Generator + Review-Accuracy Evaluator (Multi-Language)

## Overview

A self-contained repository that generates pull requests with intentionally injected bugs, maintains ground truth logs, and evaluates code review bot accuracy across multiple programming languages.

## Core Goals

1. **Generate branches and pull requests** containing intentionally injected bugs
2. **Persist machine-readable ground truth** of every injected bug (ID, type, file, lines, description)
3. **Evaluate review bot accuracy** by comparing findings to ground truth (precision/recall/F1)
4. **Multi-language support** with runnable baseline projects
5. **CLI and CI integration** for both local development and automated workflows

## Supported Languages

- **Java** (default)
- **Python**
- **JavaScript/Node.js**
- **Go**

Each language includes a small, runnable baseline project with unit tests and language-specific bug templates.

## Repository Structure

```
/
├── README.md                           # Quickstart, examples, end-to-end flow
├── tooling/
│   ├── config.yaml                     # Central configuration
│   ├── bug_templates/                  # Bug templates by language
│   │   ├── java/
│   │   ├── python/
│   │   ├── javascript/
│   │   └── go/
│   ├── ground_truth/                   # JSONL logs of injected bugs per PR
│   └── reports/                        # Evaluation outputs (metrics, confusion tables)
├── src/                                # Baseline code projects
│   ├── java/
│   ├── python/
│   ├── javascript/
│   └── go/
├── cli/                                # CLI entrypoint and commands
├── .github/workflows/ci.yml            # CI pipeline for PR generation and evaluation
└── requirements.txt                     # Python dependencies
```

## CLI Specification

### Command: `reviewlab`

**Global Options:**
- `--language <lang>`: Target language (default: java)
- `--config <path>`: Custom config file path
- `--verbose`: Enable detailed logging
- `--dry-run`: Simulate operations without making changes

**Subcommands:**

#### 1. `reviewlab generate-pr`
Creates a branch, injects bugs, commits changes, and opens a PR.

**Arguments:**
- `--count <N>`: Number of bugs to inject (default: 5)
- `--types <type1,type2>`: Specific bug types to use
- `--seed <value>`: Random seed for reproducible generation
- `--title <text>`: Custom PR title
- `--base <branch>`: Base branch (default: main)
- `--dry-run`: Simulate without pushing

**Effects:**
- Creates feature branch
- Injects specified number of bugs
- Generates ground truth JSONL log
- Commits and pushes changes
- Opens pull request (or simulates locally)
- Outputs PR metadata

#### 2. `reviewlab evaluate`
Compares bot findings to ground truth and generates accuracy metrics.

**Arguments:**
- `--pr <id>`: PR identifier
- `--findings <file>`: Path to bot findings JSON
- `--matcher <strategy>`: Matching strategy (default: overlap)
- `--tolerance <lines>`: Line range tolerance (default: 2)
- `--report <format>`: Output format (json, markdown, both)

**Output:**
- Precision, recall, F1 scores
- Detailed true positive/false positive/false negative breakdown
- Per-bug-type metrics
- Human-readable report

#### 3. `reviewlab list-bugs`
Shows available bug taxonomy for the current language.

**Arguments:**
- `--language <lang>`: Target language
- `--verbose`: Show detailed descriptions

#### 4. `reviewlab replay`
Rebuilds exact bug mutations from ground truth log.

**Arguments:**
- `--pr <id>`: PR to replay
- `--output <path>`: Output directory for recreated changes

## Bug Taxonomy

### Bug Families (Language-Adapted)

1. **Correctness**
   - Off-by-one errors
   - Wrong operator usage
   - Missing null checks
   - Logic errors

2. **API Misuse**
   - Incorrect parameters
   - Bad return value handling
   - Missing error handling

3. **Resource Handling**
   - Missing close/await calls
   - Race condition seeds
   - Memory leaks

4. **Security-Lite**
   - Unsafe string concatenation
   - Insecure randomness
   - Information disclosure

5. **Maintainability**
   - Dead code
   - Duplicate logic
   - Overly broad exception catching

6. **Test Issues**
   - Weak assertions
   - Flaky wait conditions
   - Missing test coverage

7. **Documentation Drift**
   - Contradictory comments
   - Outdated documentation
   - Missing parameter descriptions

## Bug Injection Mechanics

- **Build Preservation**: Always maintain buildability unless explicitly disabled
- **Realistic Mutations**: Inject small, realistic code changes
- **Precise Logging**: Log exact file paths and line ranges
- **Breadcrumbs**: Optional hidden markers for easier matching
- **Deterministic**: Reproducible results with same seed

## Ground Truth Log Format (JSONL)

Each bug entry includes:

```json
{
  "bug_id": "uuid",
  "pr_id": "pr_number",
  "branch": "feature_branch_name",
  "file_path": "src/main/java/Example.java",
  "start_line": 15,
  "end_line": 17,
  "bug_type": "correctness.off_by_one",
  "severity": "medium",
  "short_description": "Off-by-one error in loop condition",
  "injected_diff_summary": "- for (int i = 0; i <= array.length; i++)",
  "seed": 12345,
  "timestamp": "2024-01-15T10:30:00Z",
  "hints": ["Look for loop boundary condition"]
}
```

## Evaluation Input Format

Expected bot output JSON structure:

```json
{
  "file_path": "src/main/java/Example.java",
  "start_line": 15,
  "end_line": 17,
  "issue_type": "bug",
  "message": "Potential off-by-one error in loop",
  "severity": "medium",
  "suggestion": "Change <= to < in loop condition"
}
```

## Matching Strategies

1. **Default (Overlap)**: Match bugs based on file path and line range overlap
2. **Breadcrumb**: Use hidden markers for exact matching
3. **Semantic**: Fuzzy matching based on bug type and description
4. **Hybrid**: Combine multiple strategies with configurable weights

## Scoring and Reports

### Metrics
- **Global**: Overall precision, recall, F1
- **Per-Type**: Metrics broken down by bug family
- **Per-File**: File-level accuracy analysis

### Report Outputs
- `summary.json`: High-level metrics and scores
- `details.json`: Detailed breakdown with all matches
- `report.md`: Human-readable analysis with charts and insights

### Insights
- Top missed bug types
- Common false positives
- Performance by bug severity
- Recommendations for improvement

## Configuration (config.yaml)

```yaml
language: java
bug_mix:
  correctness: 0.3
  api_misuse: 0.2
  resource_handling: 0.15
  security_lite: 0.1
  maintainability: 0.15
  test_issues: 0.1

allow_build_breakers: false
assistive_markers: false
line_tolerance: 2

pr_title_template: "feat: Add {feature} with {bug_count} bugs"
pr_body_template: "This PR introduces {feature} functionality..."

git:
  remote: origin
  base_branch: main
  auto_push: true

evaluation:
  default_matcher: overlap
  confidence_threshold: 0.7
```

## Git and PR Integration

### Local Mode
- Simulate PR creation with branch + metadata
- Generate PR-like JSON output
- No actual GitHub/GitLab API calls

### Remote Mode
- Push branches to configured remote
- Create actual pull requests
- Handle webhook responses

## Reproducibility

- **Seed Persistence**: Store random seed with each generation
- **Config Snapshot**: Save complete configuration state
- **Replay Capability**: Rebuild exact PR from ground truth
- **Version Control**: Track tool version and dependencies

## Developer Experience

### Verbose Modes
- `--verbose`: Detailed operation logging
- `--debug`: Debug-level information
- `--quiet`: Minimal output

### Error Handling
- Clear, actionable error messages
- Graceful degradation for non-critical failures
- Helpful suggestions for common issues

### Performance
- Fast execution (<30 seconds for typical operations)
- Minimal external dependencies
- Efficient file processing

## CI Pipeline

### On PR Creation
- Generate bug-seeded PRs
- Create ground truth logs
- Run baseline tests to ensure buildability

### On PR Update
- Re-evaluate existing ground truth
- Update metrics and reports
- Attach evaluation results to PR

### Manual Dispatch
- Allow seeded generation via workflow dispatch
- Support custom bug counts and types
- Generate evaluation reports

## Definition of Done

✅ **Core Functionality**
- One command creates bug-seeded PR with ground truth
- One command evaluates bot output and produces metrics
- Works across all supported languages (Java, Python, JavaScript, Go)

✅ **Quality Assurance**
- Comprehensive test coverage
- Clear documentation and examples
- Performance benchmarks
- Error handling and edge cases

✅ **User Experience**
- 10-minute quickstart tutorial
- Intuitive CLI interface
- Helpful error messages
- Multiple output formats

✅ **Integration**
- CI/CD pipeline support
- Git workflow integration
- Extensible architecture
- Plugin system for custom bug types

## Non-Goals

- Multi-language bugs in single PR
- Heavy or unsafe vulnerabilities
- Complex dependency management
- Production deployment tools

## Example Usage

```bash
# Default Java repository with 5 bugs
reviewlab generate-pr --count 5

# Python repository with specific bug types
reviewlab generate-pr --count 3 --language python --types correctness,api_misuse

# Evaluate review bot for Go repository
reviewlab evaluate --pr 42 --findings bot_output.json --language go

# List available bugs for JavaScript
reviewlab list-bugs --language javascript

# Replay specific PR for debugging
reviewlab replay --pr 42 --output debug/
```

## Future Enhancements

- **Additional Languages**: Rust, C#, TypeScript
- **Custom Bug Templates**: User-defined bug patterns
- **Advanced Matching**: ML-based bug detection
- **Integration APIs**: Webhook support, REST endpoints
- **Visualization**: Interactive charts and dashboards
- **Team Features**: Multi-user collaboration, shared templates
