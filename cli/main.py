#!/usr/bin/env python3
"""
ReviewLab CLI - Bug-Seeded PR Generator + Review-Accuracy Evaluator

Main entry point for the command-line interface.
"""

import sys
from pathlib import Path

import click

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification
from core.config import ConfigManager
from core.errors import ErrorHandler, ReviewLabError


@click.group()
@click.version_option(version="0.1.0", prog_name="reviewlab")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option(
    "--language",
    "-l",
    type=click.Choice(["java", "python", "javascript", "go"]),
    help="Target programming language",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", is_flag=True, help="Simulate operations without making changes")
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
            config_manager.set("language", language)
        if verbose:
            config_manager.set("verbose", verbose)
        if dry_run:
            config_manager.set("dry_run", dry_run)

        # Store in context
        ctx.obj["config"] = config_manager

        if verbose:
            click.echo(f"Configuration loaded: {config_manager.get('language')} language selected")

    except Exception as e:
        ErrorHandler.handle_error(e, "CLI initialization")
        sys.exit(1)


@cli.command()
@click.option("--count", "-n", default=5, help="Number of bugs to inject (default: 5)")
@click.option("--types", "-t", help="Comma-separated list of bug types to use")
@click.option("--seed", "-s", type=int, help="Random seed for reproducible generation")
@click.option("--title", help="Custom PR title")
@click.option("--base", default="main", help="Base branch (default: main)")
@click.option("--auto-push", is_flag=True, help="Automatically push branch and create PR")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--github-repo", help="GitHub repository (owner/repo or full URL) for remote PR creation")
@click.option("--github-token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
@click.option("--github-username", help="GitHub username (or set GITHUB_USERNAME env var)")
@click.option("--draft", is_flag=True, help="Create PR as draft")
@click.pass_context
def generate_pr(ctx, count, types, seed, title, base, auto_push, dry_run, github_repo, github_token, github_username, draft):
    """Generate a new pull request with injected bugs."""
    config = ctx.obj["config"]

    try:
        click.echo(f"🚀 Generating PR with {count} bugs...")
        click.echo(f"🌍 Language: {config.get('language')}")
        click.echo(f"🌿 Base branch: {base}")
        click.echo(f"📤 Auto-push: {'Yes' if auto_push else 'No'}")
        click.echo(f"🧪 Dry run: {'Yes' if dry_run else 'No'}")

        if types:
            click.echo(f"🐛 Bug types: {types}")
        if seed:
            click.echo(f"🎲 Seed: {seed}")

        if dry_run:
            click.echo("🔍 DRY RUN MODE - No changes will be made")
            click.echo("This would:")
            click.echo("  1. Create a new branch")
            click.echo("  2. Inject specified bugs")
            click.echo("  3. Commit changes")
            if auto_push:
                click.echo("  4. Push branch and create PR")
            return

        # Import required components
        import random
        from datetime import datetime

        from core.bug_injection import BugInjectionEngine
        from core.git_operations import GitConfig
        from core.pr_workflow import PRWorkflowConfig, PRWorkflowManager

        # Set random seed if provided
        if seed:
            random.seed(seed)
            click.echo(f"🎲 Using random seed: {seed}")

        # Initialize workflow manager (for future use)
        git_config = GitConfig(base_branch=base, branch_prefix="bug-injection")

        # TODO: Use workflow_config for full PR workflow
        # workflow_config = PRWorkflowConfig(auto_create_pr=auto_push, auto_push=auto_push)
        # workflow_manager = PRWorkflowManager(
        #     project_root=Path("."), git_config=git_config, workflow_config=workflow_config
        # )

        # Get available templates
        injection_engine = BugInjectionEngine(Path("."))
        available_templates = injection_engine.get_available_templates(config.get("language"))

        if not available_templates:
            click.echo(f"❌ No bug templates available for {config.get('language')}")
            return

        click.echo(f"📋 Found {len(available_templates)} available bug templates")

        # Filter templates by type if specified
        selected_templates = available_templates
        if types:
            type_list = [t.strip() for t in types.split(",")]
            selected_templates = [t for t in available_templates if t.bug_type in type_list]
            click.echo(f"🎯 Filtered to {len(selected_templates)} templates of types: {type_list}")

        if len(selected_templates) < count:
            click.echo(
                f"⚠️  Warning: Only {len(selected_templates)} templates available, reducing count"
            )
            count = len(selected_templates)

        # Randomly select templates
        selected_templates = random.sample(selected_templates, count)

        # Start injection session
        click.echo("🔧 Starting bug injection session...")
        session_id = injection_engine.start_injection_session(config.get("language"))
        click.echo(f"📝 Session ID: {session_id}")

        # Inject bugs
        injected_bugs = []
        for i, template in enumerate(selected_templates, 1):
            click.echo(f"🐛 Injecting bug {i}/{count}: {template.name}")

            # Find suitable injection targets
            targets = injection_engine.find_injection_targets(template, config.get("language"))
            if not targets:
                click.echo(f"  ⚠️  No suitable targets found for {template.name}")
                continue

            # Select random target
            target = random.choice(targets)
            click.echo(f"  📍 Target: {target.file_path}:{target.line_number}")

            # Inject the bug
            injection_result = injection_engine.inject_bug(
                template.id, target.file_path, target.line_number
            )

            if injection_result.success:
                click.echo("  ✅ Successfully injected bug")
                injected_bugs.append(
                    {"template": template, "target": target, "result": injection_result}
                )
            else:
                click.echo(f"  ❌ Failed to inject bug: {injection_result.errors}")

        if not injected_bugs:
            click.echo("❌ No bugs were successfully injected")
            injection_engine.end_injection_session()
            return

        click.echo(f"🎉 Successfully injected {len(injected_bugs)} bugs!")

        # Handle GitHub integration if specified
        if github_repo:
            click.echo("🚀 GitHub integration mode - Creating remote PR...")
            
            try:
                from core.github_integration import GitHubManager, GitHubWorkflow, create_github_config_from_cli
                
                # Initialize GitHub integration
                github_config = create_github_config_from_cli(github_token, github_username)
                github_manager = GitHubManager(github_config)
                github_workflow = GitHubWorkflow(github_manager)
                
                # Prepare files for GitHub
                files_to_update = {}
                for bug in injected_bugs:
                    for mod in bug["result"].modifications:
                        file_path = mod.location.file_path
                        # Read the modified file content
                        with open(file_path, 'r') as f:
                            files_to_update[file_path] = f.read()
                
                # Create branch name
                branch_name = f"bug-injection/{config.get('language')}-{session_id[:8]}"
                
                # Prepare PR details
                pr_title = title or f"Inject {len(injected_bugs)} bugs for testing ({session_id[:8]})"
                pr_body = f"""## Bug Injection Test PR

This PR contains {len(injected_bugs)} intentionally injected bugs for testing code review bot accuracy.

**Session ID**: {session_id}
**Language**: {config.get('language')}
**Bug Count**: {len(injected_bugs)}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Injected Bugs:
"""
                
                for i, bug in enumerate(injected_bugs, 1):
                    template = bug["template"]
                    target = bug["target"]
                    pr_body += f"""
{i}. **{template.name}** ({template.category.value})
   - **File**: {target.file_path}:{target.line_number}
   - **Severity**: {template.severity.value}
   - **Difficulty**: {template.difficulty.value}
   - **Description**: {template.description}
"""
                
                pr_body += f"""

### Next Steps:
1. Review the injected bugs
2. Run your code review bot on this PR
3. Use 'reviewlab evaluate' to measure accuracy
4. Close this PR when testing is complete

---
*Generated by ReviewLab - Bug Injection Testing Tool*
"""
                
                if not dry_run:
                    # Create the PR on GitHub
                    repo, pr = github_workflow.create_bug_injection_pr(
                        repo_path=github_repo,
                        base_branch=base,
                        bug_branch=branch_name,
                        files_to_update=files_to_update,
                        pr_title=pr_title,
                        pr_body=pr_body,
                        draft=draft
                    )
                    
                    click.echo(f"🎉 GitHub PR created successfully!")
                    click.echo(f"🔗 PR URL: {pr.html_url}")
                    click.echo(f"📊 PR Number: #{pr.number}")
                    
                else:
                    click.echo("🔍 DRY RUN MODE - Would create GitHub PR:")
                    click.echo(f"   Repository: {github_repo}")
                    click.echo(f"   Branch: {branch_name}")
                    click.echo(f"   Title: {pr_title}")
                    click.echo(f"   Draft: {'Yes' if draft else 'No'}")
                
            except Exception as e:
                click.echo(f"❌ GitHub integration failed: {e}")
                click.echo("🔄 Falling back to local mode...")
                # Continue with local workflow
                github_repo = None

        # Create local workflow
        if auto_push and not github_repo:
            click.echo("🚀 Creating PR workflow...")

            # For now, we'll create a simple branch and commit
            # In a full implementation, this would use the PRWorkflowManager
            from core.git_operations import GitOperations

            git_ops = GitOperations(Path("."), git_config)

            # Create branch
            branch_name = f"bug-injection/{config.get('language')}-{session_id[:8]}"
            click.echo(f"🌿 Creating branch: {branch_name}")

            if not dry_run:
                git_ops.create_branch(branch_name, base)
                click.echo(f"✅ Branch created: {branch_name}")

            # Commit changes
            commit_message = f"feat: Inject {len(injected_bugs)} bugs for testing ({session_id})"
            click.echo(f"💾 Committing changes: {commit_message}")

            if not dry_run:
                files_modified = []
                for bug in injected_bugs:
                    for mod in bug["result"].modifications:
                        files_modified.append(mod.location.file_path)

                commit_hash = git_ops.commit_changes(commit_message, files_modified)
                click.echo(f"✅ Changes committed: {commit_hash[:8]}")

                # Push branch
                if git_ops.push_branch(branch_name):
                    click.echo(f"📤 Branch pushed: {branch_name}")
                else:
                    click.echo(f"❌ Failed to push branch: {branch_name}")

        # End session and export ground truth
        click.echo("📊 Exporting ground truth data...")
        ground_truth_file = Path("ground_truth") / f"session_{session_id}.jsonl"
        ground_truth_file.parent.mkdir(exist_ok=True)

        injection_engine.export_ground_truth(ground_truth_file)
        click.echo(f"✅ Ground truth exported to: {ground_truth_file}")

        injection_engine.end_injection_session()

        click.echo()
        click.echo("🎉 Bug injection completed successfully!")
        click.echo(f"📁 Ground truth file: {ground_truth_file}")
        if auto_push:
            click.echo(f"🌿 Branch: {branch_name}")
            click.echo("📋 Next steps:")
            click.echo("  1. Review the injected bugs")
            click.echo("  2. Run your code review bot")
            click.echo("  3. Use 'reviewlab evaluate' to measure accuracy")

    except Exception as e:
        ErrorHandler.handle_error(e, "PR generation")
        sys.exit(1)


@cli.command()
@click.option(
    "--findings", required=True, type=click.Path(exists=True), help="Path to bot findings JSON file"
)
@click.option(
    "--ground-truth",
    required=True,
    type=click.Path(exists=True),
    help="Path to ground truth JSONL file",
)
@click.option("--review-tool", default="unknown", help="Name of the review tool being evaluated")
@click.option(
    "--strategies",
    default="exact_overlap,line_range_overlap,semantic_similarity",
    help="Comma-separated list of matching strategies to use",
)
@click.option(
    "--output-format",
    default="all",
    type=click.Choice(["json", "csv", "txt", "html", "all"]),
    help="Output format for reports (default: all)",
)
@click.option(
    "--output-dir", type=click.Path(), help="Output directory for reports (default: reports/)"
)
@click.option("--verbose", is_flag=True, help="Show detailed evaluation information")
@click.pass_context
def evaluate(
    ctx, findings, ground_truth, review_tool, strategies, output_format, output_dir, verbose
):
    """Evaluate code review bot findings against ground truth data."""
    config = ctx.obj["config"]

    try:
        click.echo(f"🔍 Evaluating {review_tool} findings against ground truth...")
        click.echo(f"📁 Findings file: {findings}")
        click.echo(f"📁 Ground truth file: {ground_truth}")
        click.echo(f"🎯 Matching strategies: {strategies}")
        click.echo(f"📊 Output format: {output_format}")

        # Parse strategies
        strategy_list = [s.strip() for s in strategies.split(",")]

        # Import evaluation components
        import json

        from core.evaluation import EvaluationEngine, FindingType, MatchStrategy, ReviewFinding
        from core.report_generator import ReportConfig, ReportGenerator

        # Load review findings
        click.echo("📖 Loading review findings...")
        with open(findings, "r") as f:
            findings_data = json.load(f)

        # Convert to ReviewFinding objects
        review_findings = []
        for finding_data in findings_data:
            finding = ReviewFinding(
                id=finding_data.get("id", f"finding_{len(review_findings)}"),
                file_path=finding_data["file_path"],
                line_number=finding_data["line_number"],
                end_line=finding_data.get("end_line"),
                finding_type=FindingType(finding_data.get("finding_type", "bug")),
                severity=finding_data.get("severity", "medium"),
                confidence=finding_data.get("confidence", 0.8),
                message=finding_data.get("message", ""),
                rule_id=finding_data.get("rule_id"),
                category=finding_data.get("category"),
                metadata=finding_data.get("metadata", {}),
            )
            review_findings.append(finding)

        click.echo(f"✅ Loaded {len(review_findings)} review findings")

        # Load ground truth
        click.echo("📖 Loading ground truth data...")
        from core.bug_injection import GroundTruthEntry

        ground_truth_entries = []
        with open(ground_truth, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data = json.loads(line)
                        entry = GroundTruthEntry(**data)
                        ground_truth_entries.append(entry)
                    except Exception as e:
                        click.echo(f"⚠️  Warning: Failed to parse line {line_num}: {e}")
                        continue

        click.echo(f"✅ Loaded {len(ground_truth_entries)} ground truth entries")

        # Run evaluation
        click.echo("🚀 Running evaluation...")
        evaluation_engine = EvaluationEngine()

        # Convert strategy names to enum values
        strategy_enums = []
        for strategy_name in strategy_list:
            try:
                strategy_enums.append(MatchStrategy(strategy_name))
            except ValueError:
                click.echo(f"⚠️  Warning: Unknown strategy '{strategy_name}', skipping")

        if not strategy_enums:
            click.echo("❌ No valid strategies specified. Using defaults.")
            strategy_enums = [
                MatchStrategy.EXACT_OVERLAP,
                MatchStrategy.LINE_RANGE_OVERLAP,
                MatchStrategy.SEMANTIC_SIMILARITY,
            ]

        evaluation_result = evaluation_engine.evaluate_review(
            review_findings=review_findings,
            ground_truth_entries=ground_truth_entries,
            review_tool=review_tool,
            strategies=strategy_enums,
        )

        # Display results
        click.echo("📊 Evaluation Results:")
        click.echo(f"  🎯 Total Findings: {evaluation_result.metrics.total_findings}")
        click.echo(f"  🎯 Total Ground Truth: {evaluation_result.metrics.total_ground_truth}")
        click.echo(f"  ✅ True Positives: {evaluation_result.metrics.true_positives}")
        click.echo(f"  ❌ False Positives: {evaluation_result.metrics.false_positives}")
        click.echo(f"  ❌ False Negatives: {evaluation_result.metrics.false_negatives}")
        click.echo()
        click.echo(f"  📈 Precision: {evaluation_result.metrics.precision:.3f}")
        click.echo(f"  📈 Recall: {evaluation_result.metrics.recall:.3f}")
        click.echo(f"  📈 F1-Score: {evaluation_result.metrics.f1_score:.3f}")
        click.echo(f"  📈 Accuracy: {evaluation_result.metrics.accuracy:.3f}")
        click.echo()

        # Generate reports
        click.echo("📝 Generating reports...")
        output_directory = Path(output_dir) if output_dir else Path("reports")
        output_directory.mkdir(exist_ok=True)

        if output_format == "all":
            formats_to_generate = ["json", "csv", "txt", "html"]
        else:
            formats_to_generate = [output_format]

        generated_reports = []
        for format_type in formats_to_generate:
            config = ReportConfig(
                output_format=format_type,
                include_detailed_matches=True,
                include_unmatched_items=True,
            )

            generator = ReportGenerator(config)
            report_file = generator.generate_comprehensive_report(
                evaluation_result,
                output_directory
                / f"evaluation_report_{evaluation_result.session_id}.{format_type}",
            )
            generated_reports.append(report_file)
            click.echo(f"  ✅ Generated {format_type.upper()} report: {report_file.name}")

        # Generate summary
        click.echo("📋 Generating summary report...")
        summary = evaluation_engine.generate_summary_report(evaluation_result)
        summary_file = output_directory / f"evaluation_summary_{evaluation_result.session_id}.txt"
        with open(summary_file, "w") as f:
            f.write(summary)
        generated_reports.append(summary_file)
        click.echo(f"  ✅ Generated summary report: {summary_file.name}")

        click.echo()
        click.echo("🎉 Evaluation completed successfully!")
        click.echo(f"📁 Reports saved to: {output_directory}")
        click.echo(f"📊 Session ID: {evaluation_result.session_id}")

        if verbose:
            click.echo()
            click.echo("🔍 Detailed Match Information:")
            for i, match in enumerate(evaluation_result.matches, 1):
                click.echo(f"  {i}. {match.finding.file_path}:{match.finding.line_number}")
                click.echo(f"     Strategy: {match.match_strategy.value}")
                click.echo(f"     Confidence: {match.confidence:.3f}")
                click.echo(f"     Overlap Score: {match.overlap_score:.3f}")

    except Exception as e:
        ErrorHandler.handle_error(e, "Evaluation")
        sys.exit(1)


@cli.command()
@click.option("--language", "-l", help="Target language (uses config default if not specified)")
@click.option("--verbose", is_flag=True, help="Show detailed descriptions")
@click.option("--category", "-c", help="Filter by bug category")
@click.option("--severity", "-s", help="Filter by severity level")
@click.option("--difficulty", "-d", help="Filter by difficulty level")
@click.option(
    "--format", default="table", type=click.Choice(["table", "json", "csv"]), help="Output format"
)
@click.pass_context
def list_bugs(ctx, language, verbose, category, severity, difficulty, format):
    """List available bug types for the current language."""
    config = ctx.obj["config"]
    target_language = language or config.get("language")

    try:
        click.echo(f"📋 Available bug types for {target_language}:")

        # Import required components
        from core.bug_injection import BugInjectionEngine

        # Initialize injection engine
        injection_engine = BugInjectionEngine(Path("."))
        available_templates = injection_engine.get_available_templates(target_language)

        if not available_templates:
            click.echo(f"❌ No bug templates available for {target_language}")
            return

        # Apply filters
        filtered_templates = available_templates

        if category:
            filtered_templates = [t for t in filtered_templates if t.category.value == category]
            click.echo(f"🎯 Filtered by category: {category}")

        if severity:
            filtered_templates = [t for t in filtered_templates if t.severity.value == severity]
            click.echo(f"🎯 Filtered by severity: {severity}")

        if difficulty:
            filtered_templates = [t for t in filtered_templates if t.difficulty.value == difficulty]
            click.echo(f"🎯 Filtered by difficulty: {difficulty}")

        click.echo(f"📊 Found {len(filtered_templates)} templates")

        if format == "json":
            import json

            output_data = []
            for template in filtered_templates:
                output_data.append(
                    {
                        "id": template.id,
                        "name": template.name,
                        "category": template.category.value,
                        "severity": template.severity.value,
                        "difficulty": template.difficulty.value,
                        "description": template.description,
                        "language": template.language,
                    }
                )
            click.echo(json.dumps(output_data, indent=2))

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(
                ["ID", "Name", "Category", "Severity", "Difficulty", "Description", "Language"]
            )

            for template in filtered_templates:
                writer.writerow(
                    [
                        template.id,
                        template.name,
                        template.category.value,
                        template.severity.value,
                        template.difficulty.value,
                        template.description,
                        template.language,
                    ]
                )

            click.echo(output.getvalue())

        else:  # table format
            # Group by category
            categories = {}
            for template in filtered_templates:
                if template.category.value not in categories:
                    categories[template.category.value] = []
                categories[template.category.value].append(template)

            for cat, templates in categories.items():
                click.echo(f"\n📁 {cat.upper()} ({len(templates)} templates):")
                click.echo("-" * 50)

                for template in templates:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(template.severity, "⚪")

                    difficulty_emoji = {
                        "easy": "🟢",
                        "medium": "🟡",
                        "hard": "🟠",
                        "expert": "🔴",
                    }.get(template.difficulty, "⚪")

                    click.echo(f"  {severity_emoji} {difficulty_emoji} {template.name}")
                    click.echo(f"     ID: {template.id}")
                    click.echo(f"     Severity: {template.severity}")
                    click.echo(f"     Difficulty: {template.difficulty}")

                    if verbose:
                        click.echo(f"     Description: {template.description}")
                        click.echo(f"     Language: {template.language}")
                    click.echo()

        click.echo(f"🎯 Total: {len(filtered_templates)} bug templates available")

    except Exception as e:
        ErrorHandler.handle_error(e, "Bug listing")
        sys.exit(1)


@cli.command()
@click.option("--language", "-l", default="java", help="Target language for demo (default: java)")
@click.option(
    "--output-dir", type=click.Path(), help="Output directory for reports (default: reports/)"
)
@click.option("--verbose", is_flag=True, help="Show detailed evaluation information")
@click.pass_context
def demo(ctx, language, output_dir, verbose):
    """Run a quick evaluation demo with sample data."""
    config = ctx.obj["config"]

    try:
        click.echo(f"🎭 Running evaluation demo for {language}...")
        click.echo("This will create sample ground truth and review findings, then evaluate them.")

        # Import required components
        import json
        import tempfile

        from core.bug_injection import GroundTruthEntry
        from core.evaluation import EvaluationEngine, FindingType, MatchStrategy, ReviewFinding
        from core.report_generator import ReportConfig, ReportGenerator

        # Create sample ground truth
        click.echo("📝 Creating sample ground truth data...")
        ground_truth_entries = [
            GroundTruthEntry(
                id="gt_001",
                injection_id="injection_001",
                template_id="null_pointer",
                project_path="/demo/project",
                language=language,
                file_path=f"src/Calculator.{language}",
                line_number=25,
                bug_type="correctness",
                description="Null pointer dereference in calculator method",
                severity="high",
                difficulty="medium",
                injection_timestamp="2024-01-01T10:00:00",
                original_code="result = value.calculate();",
                modified_code="result = null.calculate();",
            ),
            GroundTruthEntry(
                id="gt_002",
                injection_id="injection_002",
                template_id="array_bounds",
                project_path="/demo/project",
                language=language,
                file_path=f"src/ArrayProcessor.{language}",
                line_number=42,
                bug_type="correctness",
                description="Array index out of bounds access",
                severity="medium",
                difficulty="easy",
                injection_timestamp="2024-01-01T10:05:00",
                original_code="return array[index];",
                modified_code="return array[array.length + 1];",
            ),
            GroundTruthEntry(
                id="gt_003",
                injection_id="injection_003",
                template_id="resource_leak",
                project_path="/demo/project",
                language=language,
                file_path=f"src/FileHandler.{language}",
                line_number=67,
                bug_type="correctness",
                description="Resource leak in file handling",
                severity="medium",
                difficulty="hard",
                injection_timestamp="2024-01-01T10:10:00",
                original_code="FileInputStream fis = new FileInputStream(file);",
                modified_code="FileInputStream fis = new FileInputStream(file); // Missing close()",
            ),
        ]

        # Create sample review findings
        click.echo("📝 Creating sample review findings...")
        review_findings = [
            ReviewFinding(
                id="finding_001",
                file_path=f"src/Calculator.{language}",
                line_number=25,
                finding_type=FindingType.BUG,
                severity="high",
                confidence=0.9,
                message="Potential null pointer dereference",
                rule_id="NP_NULL_ON_SOME_PATH",
                category="correctness",
            ),
            ReviewFinding(
                id="finding_002",
                file_path=f"src/ArrayProcessor.{language}",
                line_number=42,
                finding_type=FindingType.BUG,
                severity="medium",
                confidence=0.8,
                message="Array index out of bounds",
                rule_id="AI_ANNOTATION_ISSUES",
                category="correctness",
            ),
            ReviewFinding(
                id="finding_003",
                file_path=f"src/FileHandler.{language}",
                line_number=70,
                finding_type=FindingType.BUG,
                severity="medium",
                confidence=0.7,
                message="Resource leak detected",
                rule_id="OS_OPEN_STREAM",
                category="correctness",
            ),
            ReviewFinding(
                id="finding_004",
                file_path=f"src/Calculator.{language}",
                line_number=30,
                finding_type=FindingType.BUG,
                severity="low",
                confidence=0.6,
                message="Unused variable warning",
                rule_id="URF_UNREAD_FIELD",
                category="style",
            ),
            ReviewFinding(
                id="finding_005",
                file_path=f"src/Utils.{language}",
                line_number=15,
                finding_type=FindingType.BUG,
                severity="high",
                confidence=0.9,
                message="SQL injection vulnerability",
                rule_id="SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE",
                category="security",
            ),
        ]

        click.echo(f"✅ Created {len(ground_truth_entries)} ground truth entries")
        click.echo(f"✅ Created {len(review_findings)} review findings")

        # Run evaluation
        click.echo("🚀 Running evaluation...")
        evaluation_engine = EvaluationEngine()

        strategies = [
            MatchStrategy.EXACT_OVERLAP,
            MatchStrategy.LINE_RANGE_OVERLAP,
            MatchStrategy.SEMANTIC_SIMILARITY,
            MatchStrategy.BREADCRUMB_MATCHING,
        ]

        evaluation_result = evaluation_engine.evaluate_review(
            review_findings=review_findings,
            ground_truth_entries=ground_truth_entries,
            review_tool="Demo Review Bot",
            strategies=strategies,
        )

        # Display results
        click.echo("📊 Evaluation Results:")
        click.echo(f"  🎯 Total Findings: {evaluation_result.metrics.total_findings}")
        click.echo(f"  🎯 Total Ground Truth: {evaluation_result.metrics.total_ground_truth}")
        click.echo(f"  ✅ True Positives: {evaluation_result.metrics.true_positives}")
        click.echo(f"  ❌ False Positives: {evaluation_result.metrics.false_positives}")
        click.echo(f"  ❌ False Negatives: {evaluation_result.metrics.false_negatives}")
        click.echo()
        click.echo(f"  📈 Precision: {evaluation_result.metrics.precision:.3f}")
        click.echo(f"  📈 Recall: {evaluation_result.metrics.recall:.3f}")
        click.echo(f"  📈 F1-Score: {evaluation_result.metrics.f1_score:.3f}")
        click.echo(f"  📈 Accuracy: {evaluation_result.metrics.accuracy:.3f}")
        click.echo()

        # Generate reports
        click.echo("📝 Generating reports...")
        output_directory = Path(output_dir) if output_dir else Path("reports")
        output_directory.mkdir(exist_ok=True)

        # Generate all report formats
        formats_to_generate = ["json", "csv", "txt", "html"]
        generated_reports = []

        for format_type in formats_to_generate:
            config = ReportConfig(
                output_format=format_type,
                include_detailed_matches=True,
                include_unmatched_items=True,
            )

            generator = ReportGenerator(config)
            report_file = generator.generate_comprehensive_report(
                evaluation_result,
                output_directory / f"demo_evaluation_{evaluation_result.session_id}.{format_type}",
            )
            generated_reports.append(report_file)
            click.echo(f"  ✅ Generated {format_type.upper()} report: {report_file.name}")

        # Generate summary
        click.echo("📋 Generating summary report...")
        summary = evaluation_engine.generate_summary_report(evaluation_result)
        summary_file = output_directory / f"demo_summary_{evaluation_result.session_id}.txt"
        with open(summary_file, "w") as f:
            f.write(summary)
        generated_reports.append(summary_file)
        click.echo(f"  ✅ Generated summary report: {summary_file.name}")

        click.echo()
        click.echo("🎉 Demo completed successfully!")
        click.echo(f"📁 Reports saved to: {output_directory}")
        click.echo(f"📊 Session ID: {evaluation_result.session_id}")

        if verbose:
            click.echo()
            click.echo("🔍 Detailed Match Information:")
            for i, match in enumerate(evaluation_result.matches, 1):
                click.echo(f"  {i}. {match.finding.file_path}:{match.finding.line_number}")
                click.echo(f"     Strategy: {match.match_strategy.value}")
                click.echo(f"     Confidence: {match.confidence:.3f}")
                click.echo(f"     Overlap Score: {match.overlap_score:.3f}")

        click.echo()
        click.echo("💡 Next steps:")
        click.echo("  1. Review the generated reports")
        click.echo("  2. Try 'reviewlab generate-pr' to inject real bugs")
        click.echo("  3. Use 'reviewlab evaluate' with your own data")

    except Exception as e:
        ErrorHandler.handle_error(e, "Demo")
        sys.exit(1)


@cli.command()
@click.option("--pr", required=True, help="PR to replay")
@click.option("--output", type=click.Path(), help="Output directory for recreated changes")
@click.pass_context
def replay(ctx, pr, output):
    """Rebuild exact bug mutations from ground truth log."""
    # TODO: Use config for language-specific replay logic
    # config = ctx.obj["config"]

    try:
        click.echo(f"🔄 Replaying PR {pr}...")

        if output:
            click.echo(f"📁 Output directory: {output}")

        # TODO: Implement actual replay
        click.echo("⚠️  Replay functionality not yet implemented")
        click.echo("This would rebuild the exact bug mutations from the ground truth log.")

    except Exception as e:
        ErrorHandler.handle_error(e, "Replay")
        sys.exit(1)


@cli.command()
@click.option("--repo", required=True, help="GitHub repository (owner/repo or full URL)")
@click.option("--github-token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
@click.option("--github-username", help="GitHub username (or set GITHUB_USERNAME env var)")
@click.option("--state", default="open", type=click.Choice(["open", "closed", "all"]), help="PR state to list")
@click.option("--base", help="Filter by base branch")
@click.option("--limit", default=10, help="Maximum number of PRs to show")
@click.pass_context
def list_prs(ctx, repo, github_token, github_username, state, base, limit):
    """List pull requests in a GitHub repository."""
    try:
        click.echo(f"🔍 Listing PRs in {repo}...")
        
        from core.github_integration import GitHubManager, create_github_config_from_cli
        
        # Initialize GitHub integration
        github_config = create_github_config_from_cli(github_token, github_username)
        github_manager = GitHubManager(github_config)
        
        # Get repository and PRs
        repository = github_manager.get_repository(repo)
        prs = github_manager.list_pull_requests(repository, state=state, base_branch=base)
        
        # Limit results
        prs = prs[:limit]
        
        if not prs:
            click.echo(f"📭 No {state} pull requests found")
            if base:
                click.echo(f"   Base branch filter: {base}")
            return
        
        click.echo(f"📋 Found {len(prs)} {state} pull requests:")
        click.echo()
        
        for pr in prs:
            status_emoji = "🟢" if pr.state == "open" else "🔴"
            draft_emoji = "📝" if pr.draft else ""
            
            click.echo(f"{status_emoji} #{pr.number} {draft_emoji} {pr.title}")
            click.echo(f"   🔗 {pr.html_url}")
            click.echo(f"   🌿 {pr.head.ref} → {pr.base.ref}")
            click.echo(f"   👤 {pr.user.login}")
            click.echo(f"   📅 {pr.created_at.strftime('%Y-%m-%d %H:%M')}")
            click.echo()
        
        # Show repository info
        repo_info = github_manager.get_repository_info(repository)
        click.echo("📊 Repository Information:")
        click.echo(f"   Name: {repo_info['name']}")
        click.echo(f"   Owner: {repo_info['owner']}")
        click.echo(f"   Language: {repo_info['language']}")
        click.echo(f"   Stars: {repo_info['stars']}")
        click.echo(f"   Forks: {repo_info['forks']}")
        click.echo(f"   Open Issues: {repo_info['open_issues']}")
        
    except Exception as e:
        ErrorHandler.handle_error(e, "PR listing")
        sys.exit(1)


if __name__ == "__main__":
    cli()
