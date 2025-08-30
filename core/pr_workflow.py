"""
Pull Request Workflow Manager for ReviewLab.

This module coordinates bug injection, Git operations, and pull request
creation to automate the process of creating PRs with injected bugs.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from core.bug_injection import BugInjectionEngine, InjectionSession
from core.git_operations import GitOperations, GitHubIntegration, GitLabIntegration, GitConfig
from core.errors import GitError, InjectionError


@dataclass
class PRWorkflowConfig:
    """Configuration for PR workflow."""
    auto_create_pr: bool = True
    auto_push: bool = True
    pr_title_template: str = "🐛 Bug Injection: {bug_type} in {language} code"
    pr_body_template: str = """
## Automated Bug Injection

This pull request contains intentionally injected bugs for testing purposes.

**Language**: {language}
**Bug Type**: {bug_type}
**Injection ID**: {injection_id}
**Session ID**: {session_id}

### Changes Made

{changes_summary}

### Ground Truth

All injected bugs are logged with full metadata in the ground truth system.
This PR is intended for code review evaluation and testing.

**⚠️ Do not merge this PR - it contains intentional bugs!**
"""
    labels: List[str] = field(default_factory=lambda: ["bug-injection", "testing", "do-not-merge"])
    reviewers: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    """Result of a PR workflow execution."""
    success: bool
    session_id: str
    branch_name: str
    commit_hash: str
    pr_info: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PRWorkflowManager:
    """Manages the complete PR workflow for bug injection."""
    
    def __init__(self, project_root: Path, 
                 git_config: Optional[GitConfig] = None,
                 workflow_config: Optional[PRWorkflowConfig] = None):
        self.project_root = Path(project_root)
        self.git_config = git_config or GitConfig()
        self.workflow_config = workflow_config or PRWorkflowConfig()
        
        # Initialize components
        self.git_ops = GitOperations(project_root, self.git_config)
        self.injection_engine = BugInjectionEngine(project_root)
        
        # Initialize platform-specific integrations
        self.github_integration = None
        self.gitlab_integration = None
        
        try:
            self.github_integration = GitHubIntegration(project_root)
        except GitError:
            pass  # Not a GitHub repo
        
        try:
            self.gitlab_integration = GitLabIntegration(project_root)
        except GitError:
            pass  # Not a GitLab repo
    
    def execute_workflow(self, language: str, bug_template_id: str, 
                        file_path: str, line_number: int,
                        parameters: Optional[Dict[str, Any]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Execute the complete PR workflow for a single bug injection."""
        try:
            # Step 1: Start injection session
            session_id = self.injection_engine.start_injection_session(language)
            
            # Step 2: Create injection branch
            injection_id = str(uuid.uuid4())[:8]
            branch_name = self.git_ops.create_injection_branch(injection_id, language)
            
            # Step 3: Inject the bug
            injection_result = self.injection_engine.inject_bug(
                bug_template_id, file_path, line_number, parameters, metadata
            )
            
            if not injection_result.success:
                raise InjectionError(f"Bug injection failed: {injection_result.errors}")
            
            # Step 4: Get template info for PR details
            template = self.injection_engine.template_manager.get_template(bug_template_id)
            if not template:
                raise InjectionError(f"Template not found: {bug_template_id}")
            
            # Step 5: Commit the changes
            files_modified = [mod.location.file_path for mod in injection_result.modifications]
            commit_hash = self.git_ops.commit_injection(injection_id, template.name, files_modified)
            
            # Step 6: Push the branch
            if self.workflow_config.auto_push:
                if not self.git_ops.push_branch(branch_name):
                    raise GitError(f"Failed to push branch: {branch_name}")
            
            # Step 7: Create pull request
            pr_info = None
            if self.workflow_config.auto_create_pr:
                pr_info = self._create_pull_request(
                    injection_id, language, template, branch_name, files_modified
                )
            
            # Step 8: End injection session
            self.injection_engine.end_injection_session()
            
            # Step 9: Export ground truth
            ground_truth_file = Path("ground_truth") / f"workflow_{injection_id}.json"
            self.injection_engine.export_ground_truth(ground_truth_file)
            
            return WorkflowResult(
                success=True,
                session_id=session_id,
                branch_name=branch_name,
                commit_hash=commit_hash,
                pr_info=pr_info,
                metadata={
                    'injection_id': injection_id,
                    'language': language,
                    'bug_type': template.name,
                    'template_id': bug_template_id,
                    'files_modified': files_modified,
                    'ground_truth_file': str(ground_truth_file)
                }
            )
            
        except Exception as e:
            # Clean up on failure
            try:
                if 'session_id' in locals():
                    self.injection_engine.end_injection_session()
            except:
                pass
            
            return WorkflowResult(
                success=False,
                session_id=session_id if 'session_id' in locals() else "unknown",
                branch_name=branch_name if 'branch_name' in locals() else "unknown",
                commit_hash=commit_hash if 'commit_hash' in locals() else "unknown",
                errors=[str(e)]
            )
    
    def execute_batch_workflow(self, language: str, 
                              injections: List[Dict[str, Any]]) -> List[WorkflowResult]:
        """Execute PR workflow for multiple bug injections."""
        results = []
        
        try:
            # Start injection session
            session_id = self.injection_engine.start_injection_session(language)
            
            # Create injection branch
            batch_id = str(uuid.uuid4())[:8]
            branch_name = self.git_ops.create_injection_branch(batch_id, language)
            
            # Process each injection
            for i, injection_data in enumerate(injections):
                try:
                    # Inject bug
                    injection_result = self.injection_engine.inject_bug(
                        injection_data['template_id'],
                        injection_data['file_path'],
                        injection_data['line_number'],
                        injection_data.get('parameters'),
                        injection_data.get('metadata')
                    )
                    
                    if not injection_result.success:
                        results.append(WorkflowResult(
                            success=False,
                            session_id=session_id,
                            branch_name=branch_name,
                            commit_hash="unknown",
                            errors=[f"Injection {i+1} failed: {injection_result.errors}"]
                        ))
                        continue
                    
                    # Get template info
                    template = self.injection_engine.template_manager.get_template(
                        injection_data['template_id']
                    )
                    
                    # Commit changes
                    files_modified = [mod.location.file_path for mod in injection_result.modifications]
                    commit_hash = self.git_ops.commit_injection(
                        f"{batch_id}-{i+1}", template.name if template else "Unknown", files_modified
                    )
                    
                    results.append(WorkflowResult(
                        success=True,
                        session_id=session_id,
                        branch_name=branch_name,
                        commit_hash=commit_hash,
                        metadata={
                            'injection_index': i + 1,
                            'template_id': injection_data['template_id'],
                            'files_modified': files_modified
                        }
                    ))
                    
                except Exception as e:
                    results.append(WorkflowResult(
                        success=False,
                        session_id=session_id,
                        branch_name=branch_name,
                        commit_hash="unknown",
                        errors=[f"Injection {i+1} failed: {str(e)}"]
                    ))
            
            # Push branch if auto-push is enabled
            if self.workflow_config.auto_push:
                if not self.git_ops.push_branch(branch_name):
                    raise GitError(f"Failed to push branch: {branch_name}")
            
            # Create pull request if auto-create is enabled
            if self.workflow_config.auto_create_pr and results:
                # Create summary PR for batch
                pr_info = self._create_batch_pull_request(
                    batch_id, language, branch_name, results
                )
                
                # Update results with PR info
                for result in results:
                    result.pr_info = pr_info
            
            # End injection session
            self.injection_engine.end_injection_session()
            
            # Export ground truth
            ground_truth_file = Path("ground_truth") / f"batch_workflow_{batch_id}.json"
            self.injection_engine.export_ground_truth(ground_truth_file)
            
        except Exception as e:
            # Clean up on failure
            try:
                if 'session_id' in locals():
                    self.injection_engine.end_injection_session()
            except:
                pass
            
            # Add error result for the entire batch
            results.append(WorkflowResult(
                success=False,
                session_id=session_id if 'session_id' in locals() else "unknown",
                branch_name=branch_name if 'branch_name' in locals() else "unknown",
                commit_hash="unknown",
                errors=[f"Batch workflow failed: {str(e)}"]
            ))
        
        return results
    
    def _create_pull_request(self, injection_id: str, language: str, template: Any,
                           branch_name: str, files_modified: List[str]) -> Any:
        """Create a pull request for a single bug injection."""
        # Prepare PR details
        title = self.workflow_config.pr_title_template.format(
            bug_type=template.name,
            language=language
        )
        
        changes_summary = "\n".join([f"- `{file}`" for file in files_modified])
        
        body = self.workflow_config.pr_body_template.format(
            language=language,
            bug_type=template.name,
            injection_id=injection_id,
            session_id=self.injection_engine.current_session,
            changes_summary=changes_summary
        )
        
        # Create PR based on platform
        if self.github_integration:
            return self.github_integration.create_pull_request(
                title=title,
                body=body,
                head_branch=branch_name,
                base_branch=self.git_config.base_branch
            )
        elif self.gitlab_integration:
            return self.gitlab_integration.create_merge_request(
                title=title,
                description=body,
                source_branch=branch_name,
                target_branch=self.git_config.base_branch
            )
        else:
            raise GitError("No supported Git platform integration found")
    
    def _create_batch_pull_request(self, batch_id: str, language: str, 
                                 branch_name: str, results: List[WorkflowResult]) -> Any:
        """Create a pull request for a batch of bug injections."""
        successful_injections = [r for r in results if r.success]
        
        title = f"🐛 Batch Bug Injection: {len(successful_injections)} bugs in {language} code"
        
        body = f"""
## Batch Bug Injection

This pull request contains {len(successful_injections)} intentionally injected bugs for testing purposes.

**Language**: {language}
**Batch ID**: {batch_id}
**Total Injections**: {len(results)}
**Successful Injections**: {len(successful_injections)}
**Failed Injections**: {len(results) - len(successful_injections)}

### Changes Made

{self._format_batch_changes(results)}

### Ground Truth

All injected bugs are logged with full metadata in the ground truth system.
This PR is intended for code review evaluation and testing.

**⚠️ Do not merge this PR - it contains intentional bugs!**
"""
        
        # Create PR based on platform
        if self.github_integration:
            return self.github_integration.create_pull_request(
                title=title,
                body=body,
                head_branch=branch_name,
                base_branch=self.git_config.base_branch
            )
        elif self.gitlab_integration:
            return self.gitlab_integration.create_merge_request(
                title=title,
                description=body,
                source_branch=branch_name,
                target_branch=self.git_config.base_branch
            )
        else:
            raise GitError("No supported Git platform integration found")
    
    def _format_batch_changes(self, results: List[WorkflowResult]) -> str:
        """Format the changes summary for batch PR."""
        if not results:
            return "No changes made."
        
        changes_by_file = {}
        for result in results:
            if result.success and 'files_modified' in result.metadata:
                for file_path in result.metadata['files_modified']:
                    if file_path not in changes_by_file:
                        changes_by_file[file_path] = []
                    changes_by_file[file_path].append(result.metadata.get('template_id', 'Unknown'))
        
        if not changes_by_file:
            return "No changes made."
        
        lines = []
        for file_path, template_ids in changes_by_file.items():
            lines.append(f"- `{file_path}`")
            for template_id in template_ids:
                lines.append(f"  - {template_id}")
        
        return "\n".join(lines)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow manager."""
        return {
            'project_root': str(self.project_root),
            'git_config': {
                'remote_name': self.git_config.remote_name,
                'base_branch': self.git_config.base_branch,
                'branch_prefix': self.git_config.branch_prefix
            },
            'workflow_config': {
                'auto_create_pr': self.workflow_config.auto_create_pr,
                'auto_push': self.workflow_config.auto_push
            },
            'integrations': {
                'github': self.github_integration is not None,
                'gitlab': self.gitlab_integration is not None
            },
            'current_branch': self.git_ops.get_current_branch(),
            'git_status': self.git_ops.get_status()
        }
    
    def cleanup_workflow(self, branch_name: str, force: bool = False) -> bool:
        """Clean up workflow artifacts (branch, etc.)."""
        try:
            # Switch back to base branch
            if not self.git_ops.checkout_branch(self.git_config.base_branch):
                return False
            
            # Delete the workflow branch
            if not self.git_ops.delete_branch(branch_name, force):
                return False
            
            return True
        except Exception:
            return False
