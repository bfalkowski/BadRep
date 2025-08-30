"""
Bug Injection Engine for ReviewLab.

This module provides the core infrastructure for injecting bugs into baseline
projects and maintaining ground truth logs of all injected bugs.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from core.bug_templates import BugTemplate, BugInjection, BugLocation, BugTemplateManager
from core.plugins import PluginManager
from core.plugins.base import InjectionResult
from core.errors import InjectionError


@dataclass
class GroundTruthEntry:
    """Represents a ground truth entry for an injected bug."""
    id: str
    injection_id: str
    template_id: str
    project_path: str
    language: str
    file_path: str
    line_number: int
    bug_type: str
    description: str
    severity: str
    difficulty: str
    injection_timestamp: str
    original_code: str
    modified_code: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def to_jsonl(self) -> str:
        """Convert to JSONL format."""
        return json.dumps(self.to_dict())


@dataclass
class InjectionSession:
    """Represents a bug injection session."""
    session_id: str
    project_path: str
    language: str
    start_time: str
    end_time: Optional[str] = None
    total_injections: int = 0
    successful_injections: int = 0
    failed_injections: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


class GroundTruthLogger:
    """Manages ground truth logging for bug injections."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path("ground_truth")
        self.log_dir.mkdir(exist_ok=True)
        self.session_logs: Dict[str, InjectionSession] = {}
    
    def start_session(self, project_path: str, language: str) -> str:
        """Start a new injection session."""
        session_id = str(uuid.uuid4())
        session = InjectionSession(
            session_id=session_id,
            project_path=project_path,
            language=language,
            start_time=datetime.now().isoformat()
        )
        self.session_logs[session_id] = session
        return session_id
    
    def end_session(self, session_id: str):
        """End an injection session."""
        if session_id in self.session_logs:
            self.session_logs[session_id].end_time = datetime.now().isoformat()
    
    def log_injection(self, session_id: str, injection: BugInjection, 
                     result: InjectionResult, template: BugTemplate) -> GroundTruthEntry:
        """Log a bug injection to ground truth."""
        if session_id not in self.session_logs:
            raise InjectionError(f"Invalid session ID: {session_id}")
        
        session = self.session_logs[session_id]
        
        # Create ground truth entry
        entry = GroundTruthEntry(
            id=str(uuid.uuid4()),
            injection_id=injection.template_id,
            template_id=injection.template_id,
            project_path=session.project_path,
            language=session.language,
            file_path=injection.location.file_path,
            line_number=injection.location.line_number,
            bug_type=template.category.value,
            description=template.description,
            severity=template.severity.value,
            difficulty=template.difficulty.value,
            injection_timestamp=datetime.now().isoformat(),
            original_code=result.modifications[0].original_code if result.modifications else "",
            modified_code=result.modifications[0].modified_code if result.modifications else "",
            metadata={
                'template_patterns': template.patterns,
                'template_tags': template.tags,
                'injection_parameters': injection.parameters,
                'injection_metadata': injection.metadata,
                'result_metadata': result.metadata
            }
        )
        
        # Write to JSONL file
        log_file = self.log_dir / f"{session_id}.jsonl"
        with open(log_file, 'a') as f:
            f.write(entry.to_jsonl() + '\n')
        
        # Update session statistics
        session.total_injections += 1
        if result.success:
            session.successful_injections += 1
        else:
            session.failed_injections += 1
        
        return entry
    
    def get_session_logs(self, session_id: str) -> List[GroundTruthEntry]:
        """Get all ground truth entries for a session."""
        log_file = self.log_dir / f"{session_id}.jsonl"
        if not log_file.exists():
            return []
        
        entries = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    entry_data = json.loads(line)
                    entries.append(GroundTruthEntry(**entry_data))
        
        return entries
    
    def export_session_summary(self, session_id: str, output_file: Path):
        """Export a session summary to a file."""
        if session_id not in self.session_logs:
            raise InjectionError(f"Invalid session ID: {session_id}")
        
        session = self.session_logs[session_id]
        entries = self.get_session_logs(session_id)
        
        summary = {
            'session': session.to_dict(),
            'entries': [entry.to_dict() for entry in entries],
            'statistics': {
                'total_injections': session.total_injections,
                'successful_injections': session.successful_injections,
                'failed_injections': session.failed_injections,
                'success_rate': session.successful_injections / session.total_injections if session.total_injections > 0 else 0
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)


class BugInjectionEngine:
    """Main engine for coordinating bug injection across languages."""
    
    def __init__(self, project_root: Path, template_dir: Optional[Path] = None):
        self.project_root = project_root
        self.template_manager = BugTemplateManager(template_dir)
        self.plugin_manager = PluginManager(project_root)
        self.ground_truth_logger = GroundTruthLogger()
        self.current_session: Optional[str] = None
    
    def start_injection_session(self, language: str) -> str:
        """Start a new bug injection session."""
        if not self.plugin_manager.get_plugin(language):
            raise InjectionError(f"Language not supported: {language}")
        
        self.current_session = self.ground_truth_logger.start_session(
            str(self.project_root), language
        )
        return self.current_session
    
    def end_injection_session(self):
        """End the current injection session."""
        if self.current_session:
            self.ground_truth_logger.end_session(self.current_session)
            self.current_session = None
    
    def inject_bug(self, template_id: str, file_path: str, line_number: int,
                   parameters: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> InjectionResult:
        """Inject a specific bug into the code."""
        if not self.current_session:
            raise InjectionError("No active injection session")
        
        # Get the bug template
        template = self.template_manager.get_template(template_id)
        if not template:
            raise InjectionError(f"Template not found: {template_id}")
        
        # Create injection object
        location = BugLocation(
            file_path=file_path,
            line_number=line_number
        )
        
        injection = BugInjection(
            template_id=template_id,
            location=location,
            parameters=parameters or {},
            metadata=metadata or {}
        )
        
        # Validate injection
        if not self.plugin_manager.validate_injection(injection):
            raise InjectionError(f"Invalid injection: {injection}")
        
        # Perform injection
        result = self.plugin_manager.inject_bug(injection)
        
        # Log to ground truth
        self.ground_truth_logger.log_injection(
            self.current_session, injection, result, template
        )
        
        return result
    
    def inject_random_bugs(self, language: str, count: int = 5,
                          categories: Optional[List[str]] = None,
                          difficulties: Optional[List[str]] = None) -> List[InjectionResult]:
        """Inject random bugs based on criteria."""
        if not self.current_session:
            raise InjectionError("No active injection session")
        
        # Get available templates
        templates = self.template_manager.get_templates_by_language(language)
        
        # Filter by categories if specified
        if categories:
            templates = [t for t in templates if t.category.value in categories]
        
        # Filter by difficulties if specified
        if difficulties:
            templates = [t for t in templates if t.difficulty.value in difficulties]
        
        if not templates:
            raise InjectionError(f"No templates available for language: {language}")
        
        # Get source files
        plugin = self.plugin_manager.get_plugin(language)
        source_files = plugin.find_source_files()
        
        if not source_files:
            raise InjectionError(f"No source files found for language: {language}")
        
        results = []
        import random
        
        for _ in range(count):
            # Select random template and file
            template = random.choice(templates)
            source_file = random.choice(source_files)
            
            # Find injection targets
            targets = plugin.find_injection_targets(source_file, template)
            if not targets:
                continue
            
            # Select random target
            target = random.choice(targets)
            
            # Create injection
            injection = BugInjection(
                template_id=template.id,
                location=target.to_bug_location(),
                parameters={},
                metadata={'random_injection': True}
            )
            
            # Perform injection
            result = self.plugin_manager.inject_bug(injection)
            results.append(result)
            
            # Log to ground truth
            self.ground_truth_logger.log_injection(
                self.current_session, injection, result, template
            )
        
        return results
    
    def validate_project_build(self, language: str) -> bool:
        """Validate that the project still builds after injection."""
        plugin = self.plugin_manager.get_plugin(language)
        if not plugin:
            return False
        
        return plugin.build_project()
    
    def run_project_tests(self, language: str) -> Dict[str, Any]:
        """Run tests to verify bug injection worked."""
        plugin = self.plugin_manager.get_plugin(language)
        if not plugin:
            return {'success': False, 'error': 'Plugin not found'}
        
        return plugin.run_tests()
    
    def get_injection_summary(self) -> Dict[str, Any]:
        """Get a summary of the current injection session."""
        if not self.current_session:
            return {'error': 'No active session'}
        
        session = self.ground_truth_logger.session_logs[self.current_session]
        entries = self.ground_truth_logger.get_session_logs(self.current_session)
        
        return {
            'session_id': self.current_session,
            'project_path': session.project_path,
            'language': session.language,
            'start_time': session.start_time,
            'total_injections': session.total_injections,
            'successful_injections': session.successful_injections,
            'failed_injections': session.failed_injections,
            'success_rate': session.successful_injections / session.total_injections if session.total_injections > 0 else 0,
            'bug_types': list(set(entry.bug_type for entry in entries)),
            'files_modified': list(set(entry.file_path for entry in entries))
        }
    
    def export_ground_truth(self, output_file: Path):
        """Export ground truth data for the current session."""
        if not self.current_session:
            raise InjectionError("No active injection session")
        
        self.ground_truth_logger.export_session_summary(self.current_session, output_file)
    
    def cleanup_injection(self, injection_id: str) -> bool:
        """Clean up a specific bug injection."""
        # This would require storing injection metadata for cleanup
        # For now, return False to indicate cleanup is not implemented
        return False
    
    def get_available_templates(self, language: str, 
                              category: Optional[str] = None,
                              difficulty: Optional[str] = None) -> List[BugTemplate]:
        """Get available bug templates with optional filtering."""
        templates = self.template_manager.get_templates_by_language(language)
        
        if category:
            templates = [t for t in templates if t.category.value == category]
        
        if difficulty:
            templates = [t for t in templates if t.difficulty.value == difficulty]
        
        return templates
