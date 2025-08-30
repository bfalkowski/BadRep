"""
Java Language Plugin for ReviewLab.

This plugin provides Java-specific bug injection capabilities,
including parsing Java source files and injecting various types of bugs.
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from core.bug_templates import BugInjection, BugTemplate

from .base import CodeLocation, CodeModification, InjectionResult, LanguagePlugin


class JavaPlugin(LanguagePlugin):
    """Java language plugin for bug injection."""

    def _initialize_language_specifics(self):
        """Initialize Java-specific attributes."""
        self.supported_extensions = {"java"}
        self.build_files = {"pom.xml", "build.gradle", "build.xml"}
        self.test_files = {"*Test.java", "*Tests.java"}
        self.maven_home = self._find_maven_home()

    def get_name(self) -> str:
        """Get the plugin name."""
        return "Java Plugin"

    def get_version(self) -> str:
        """Get the plugin version."""
        return "1.0.0"

    def get_supported_extensions(self) -> Set[str]:
        """Get supported file extensions for Java."""
        return self.supported_extensions

    def can_parse_file(self, file_path: Path) -> bool:
        """Check if this plugin can parse the given file."""
        return file_path.suffix.lower() == ".java"

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a Java source file and extract structural information."""
        if not self.can_parse_file(file_path):
            return {"error": "Not a Java file"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract basic information
            info = {
                "file_path": str(file_path),
                "lines": len(content.splitlines()),
                "classes": [],
                "methods": [],
                "imports": [],
                "package": None,
            }

            # Extract package declaration
            package_match = re.search(r"package\s+([\w.]+);", content)
            if package_match:
                info["package"] = package_match.group(1)

            # Extract imports
            import_pattern = r"import\s+([\w.*]+);"
            info["imports"] = re.findall(import_pattern, content)

            # Extract class declarations
            class_pattern = r"(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)"
            info["classes"] = re.findall(class_pattern, content)

            # Extract method declarations
            method_pattern = r"(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:abstract\s+)?(\w+)\s+(\w+)\s*\([^)]*\)\s*\{?"
            methods = re.findall(method_pattern, content)
            info["methods"] = [{"return_type": m[0], "name": m[1]} for m in methods]

            return info

        except Exception as e:
            return {"error": f"Failed to parse Java file: {e}"}

    def find_injection_targets(self, file_path: Path, template: BugTemplate) -> List[CodeLocation]:
        """Find suitable locations for injecting a specific bug template."""
        if not self.can_parse_file(file_path):
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            targets = []

            # Look for arithmetic operations based on template patterns
            if "arithmetic_error" in template.patterns or "wrong_operator" in template.patterns:
                targets.extend(self._find_arithmetic_operations(file_path, lines))

            if "off_by_one" in template.patterns:
                targets.extend(self._find_loop_boundaries(file_path, lines))

            if "zero_division" in template.patterns:
                targets.extend(self._find_division_operations(file_path, lines))

            if "overflow" in template.patterns:
                targets.extend(self._find_arithmetic_operations(file_path, lines))

            return targets

        except Exception as e:
            return []

    def _find_arithmetic_operations(self, file_path: Path, lines: List[str]) -> List[CodeLocation]:
        """Find arithmetic operations in Java code."""
        targets = []
        arithmetic_pattern = r"(\w+)\s*([+\-*/%])\s*(\w+)"

        for i, line in enumerate(lines, 1):
            if re.search(arithmetic_pattern, line):
                targets.append(
                    CodeLocation(
                        file_path=file_path,
                        line_number=i,
                        function_name=self._find_function_name(lines, i),
                    )
                )

        return targets

    def _find_loop_boundaries(self, file_path: Path, lines: List[str]) -> List[CodeLocation]:
        """Find loop boundary conditions in Java code."""
        targets = []
        loop_patterns = [
            r"for\s*\([^)]*\)\s*\{",
            r"while\s*\([^)]*\)\s*\{",
            r"do\s*\{[^}]*\}\s*while\s*\([^)]*\)",
        ]

        for i, line in enumerate(lines, 1):
            for pattern in loop_patterns:
                if re.search(pattern, line):
                    targets.append(
                        CodeLocation(
                            file_path=file_path,
                            line_number=i,
                            function_name=self._find_function_name(lines, i),
                        )
                    )
                    break

        return targets

    def _find_division_operations(self, file_path: Path, lines: List[str]) -> List[CodeLocation]:
        """Find division operations in Java code."""
        targets = []
        division_pattern = r"(\w+)\s*/\s*(\w+)"

        for i, line in enumerate(lines, 1):
            if re.search(division_pattern, line):
                targets.append(
                    CodeLocation(
                        file_path=file_path,
                        line_number=i,
                        function_name=self._find_function_name(lines, i),
                    )
                )

        return targets

    def _find_function_name(self, lines: List[str], line_number: int) -> Optional[str]:
        """Find the function name for a given line number."""
        # Look backwards to find the function declaration
        for i in range(line_number - 1, -1, -1):
            line = lines[i]
            method_match = re.search(r"(\w+)\s+(\w+)\s*\([^)]*\)\s*\{?", line)
            if method_match:
                return method_match.group(2)
        return None

    def inject_bug(self, injection: BugInjection) -> InjectionResult:
        """Inject a bug into Java source code."""
        target_file = Path(injection.location.file_path)
        if not target_file.is_absolute():
            target_file = self.project_root / target_file

        if not self.can_parse_file(target_file):
            return InjectionResult(
                success=False, modifications=[], errors=[f"File not supported: {target_file}"]
            )

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            modifications = []
            template = injection.template_id

            # Apply bug injection based on template
            if template == "java_off_by_one_loop":
                mod = self._inject_off_by_one_bug(lines, injection)
                if mod:
                    modifications.append(mod)

            elif template == "java_wrong_operator":
                mod = self._inject_wrong_operator_bug(lines, injection)
                if mod:
                    modifications.append(mod)

            elif template == "java_zero_division":
                mod = self._inject_zero_division_bug(lines, injection)
                if mod:
                    modifications.append(mod)

            elif template == "java_overflow_error":
                mod = self._inject_overflow_bug(lines, injection)
                if mod:
                    modifications.append(mod)

            else:
                return InjectionResult(
                    success=False, modifications=[], errors=[f"Unknown template: {template}"]
                )

            if modifications:
                # Apply modifications to file
                with open(target_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                return InjectionResult(success=True, modifications=modifications)
            else:
                return InjectionResult(
                    success=False, modifications=[], errors=["No modifications were made"]
                )

        except Exception as e:
            return InjectionResult(
                success=False, modifications=[], errors=[f"Failed to inject bug: {e}"]
            )

    def _inject_off_by_one_bug(
        self, lines: List[str], injection: BugInjection
    ) -> Optional[CodeModification]:
        """Inject an off-by-one bug in a loop."""
        line_num = injection.location.line_number - 1
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        original_line = line

        # Look for loop patterns and modify boundary conditions
        if "for" in line and "<=" in line:
            # Change <= to <
            modified_line = line.replace("<=", "<")
        elif "for" in line and "<" in line:
            # Change < to <=
            modified_line = line.replace("<", "<=")
        else:
            return None

        lines[line_num] = modified_line

        return CodeModification(
            location=CodeLocation(
                file_path=Path(injection.location.file_path),
                line_number=injection.location.line_number,
            ),
            original_code=original_line.rstrip(),
            modified_code=modified_line.rstrip(),
            description="Injected off-by-one bug in loop boundary",
        )

    def _inject_wrong_operator_bug(
        self, lines: List[str], injection: BugInjection
    ) -> Optional[CodeModification]:
        """Inject a wrong operator bug."""
        line_num = injection.location.line_number - 1
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        original_line = line

        # Replace arithmetic operators
        if "+" in line:
            modified_line = line.replace("+", "*")
        elif "*" in line:
            modified_line = line.replace("*", "+")
        elif "/" in line:
            modified_line = line.replace("/", "%")
        elif "%" in line:
            modified_line = line.replace("%", "/")
        else:
            return None

        lines[line_num] = modified_line

        return CodeModification(
            location=CodeLocation(
                file_path=Path(injection.location.file_path),
                line_number=injection.location.line_number,
            ),
            original_code=original_line.rstrip(),
            modified_code=modified_line.rstrip(),
            description="Injected wrong operator bug",
        )

    def _inject_zero_division_bug(
        self, lines: List[str], injection: BugInjection
    ) -> Optional[CodeModification]:
        """Inject a zero division bug by removing validation."""
        line_num = injection.location.line_number - 1
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        original_line = line

        # Look for division operations and remove any zero checks
        if "/" in line:
            # This is a simple injection - in practice, we'd need to look at surrounding context
            # For now, just modify the line to make it more likely to cause issues
            modified_line = line.replace("b != 0", "true")
            if modified_line != line:
                lines[line_num] = modified_line

                return CodeModification(
                    location=CodeLocation(
                        file_path=Path(injection.location.file_path),
                        line_number=injection.location.line_number,
                    ),
                    original_code=original_line.rstrip(),
                    modified_code=modified_line.rstrip(),
                    description="Injected zero division bug by removing validation",
                )

        return None

    def _inject_overflow_bug(
        self, lines: List[str], injection: BugInjection
    ) -> Optional[CodeModification]:
        """Inject an overflow bug by using smaller data types."""
        line_num = injection.location.line_number - 1
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        original_line = line

        # Replace long with int to cause overflow
        if "long" in line:
            modified_line = line.replace("long", "int")
            lines[line_num] = modified_line

            return CodeModification(
                location=CodeLocation(
                    file_path=Path(injection.location.file_path),
                    line_number=injection.location.line_number,
                ),
                original_code=original_line.rstrip(),
                modified_code=modified_line.rstrip(),
                description="Injected overflow bug by using smaller data type",
            )

        return None

    def validate_injection(self, injection: BugInjection) -> bool:
        """Validate that a bug injection can be performed."""
        target_file = Path(injection.location.file_path)
        if not target_file.is_absolute():
            target_file = self.project_root / target_file

        if not self.can_parse_file(target_file):
            return False

        if not target_file.exists():
            return False

        # Check if the line number is valid
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if injection.location.line_number > len(lines):
                    return False
        except Exception:
            return False

        return True

    def build_project(self) -> bool:
        """Build the Java project using Maven."""
        if not self.maven_home:
            return False

        try:
            result = subprocess.run(
                ["mvn", "clean", "compile"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_tests(self) -> Dict[str, Any]:
        """Run Java tests using Maven."""
        if not self.maven_home:
            return {"success": False, "error": "Maven not found"}

        try:
            result = subprocess.run(
                ["mvn", "test"], cwd=self.project_root, capture_output=True, text=True, timeout=120
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup_injection(self, injection: BugInjection) -> bool:
        """Clean up a bug injection by restoring original code."""
        # This would require storing the original code somewhere
        # For now, we'll return False to indicate cleanup is not implemented
        return False

    def _find_maven_home(self) -> Optional[str]:
        """Find Maven installation directory."""
        try:
            result = subprocess.run(
                ["mvn", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return "maven"  # Maven is available in PATH
        except Exception:
            pass

        # Check common Maven installation paths
        common_paths = [
            "/usr/local/maven",
            "/opt/maven",
            "/usr/share/maven",
            "/usr/local/bin/maven",
        ]

        for path in common_paths:
            if Path(path).exists():
                return path

        return None
