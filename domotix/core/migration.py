"""
Migration guide to Python 3.12+ and modern best practices.

This file documents and automates the migration of the Domotix application
to the latest Python standards and modern best practices.

Main changes:
1. Migration from Python 3.13 to 3.12+ for better compatibility
2. Modern type syntax (dict instead of Dict, | instead of Union)
3. Migration of typing imports to collections.abc
4. Implementation of a modern dependency injection system
5. Structured logging system with context
6. Modern error handling with structured codes
7. Configuration with dataclasses and validation
8. Integrated monitoring and metrics

Modernized modules:
- domotix.core.dependency_injection: IoC container with scopes
- domotix.core.service_provider: Modern service provider
- domotix.core.service_configuration: Centralized service configuration
- domotix.core.interfaces: Protocols and base classes
- domotix.core.config: Configuration with dataclasses
- domotix.core.logging_system: Structured logging with context
- domotix.globals.exceptions: Modern exception hierarchy (modernized)
- domotix.core.monitoring: Metrics and health checks
- domotix.factories: Modern factory with DI
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from domotix.core.logging_system import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class MigrationRule:
    """
    Migration rule to modernize the code.

    Defines a specific transformation to apply
    to the Python files of the project.
    """

    name: str
    description: str
    pattern: str
    replacement: str
    file_extensions: list[str]
    applies_to_imports: bool = False

    def apply(self, content: str) -> tuple[str, int]:
        """
        Applies the migration rule to the content.

        Args:
            content: File content

        Returns:
            Tuple (new_content, number_of_changes)
        """
        if self.applies_to_imports:
            # Special application for imports
            return self._apply_import_rule(content)
        else:
            # Standard application with regex
            new_content, count = re.subn(
                self.pattern, self.replacement, content, flags=re.MULTILINE
            )
            return new_content, count

    def _apply_import_rule(self, content: str) -> tuple[str, int]:
        """
        Applies a migration rule specific to imports.

        Args:
            content: File content

        Returns:
            Tuple (new_content, number_of_changes)
        """
        lines = content.split("\n")
        new_lines = []
        changes = 0

        for line in lines:
            new_line = line
            if re.match(self.pattern, line.strip()):
                new_line = re.sub(self.pattern, self.replacement, line)
                if new_line != line:
                    changes += 1
            new_lines.append(new_line)

        return "\n".join(new_lines), changes


# Migration rules for Python 3.12+
MIGRATION_RULES = [
    # Migration of types to modern syntax
    MigrationRule(
        name="dict_type_modernization",
        description="Replace typing.Dict with dict",
        pattern=r"from typing import.*Dict.*",
        replacement="# Dict replaced by dict (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="list_type_modernization",
        description="Replace typing.List with list",
        pattern=r"from typing import.*List.*",
        replacement="# List replaced by list (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="tuple_type_modernization",
        description="Replace typing.Tuple with tuple",
        pattern=r"from typing import.*Tuple.*",
        replacement="# Tuple replaced by tuple (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="set_type_modernization",
        description="Replace typing.Set with set",
        pattern=r"from typing import.*Set.*",
        replacement="# Set replaced by set (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    # Migration of type annotations
    MigrationRule(
        name="dict_annotation_modernization",
        description="Replace Dict[K, V] with dict[K, V]",
        pattern=r"Dict\[([^]]+)\]",
        replacement=r"dict[\1]",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="list_annotation_modernization",
        description="Replace List[T] with list[T]",
        pattern=r"List\[([^]]+)\]",
        replacement=r"list[\1]",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="tuple_annotation_modernization",
        description="Replace Tuple[...] with tuple[...]",
        pattern=r"Tuple\[([^]]+)\]",
        replacement=r"tuple[\1]",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="set_annotation_modernization",
        description="Replace Set[T] with set[T]",
        pattern=r"Set\[([^]]+)\]",
        replacement=r"set[\1]",
        file_extensions=[".py"],
    ),
    # Migration from Union to |
    MigrationRule(
        name="union_syntax_modernization",
        description="Replace Union[A, B] with A | B",
        pattern=r"Union\[([^,]+),\s*([^]]+)\]",
        replacement=r"\1 | \2",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="optional_syntax_modernization",
        description="Replace Optional[T] with T | None",
        pattern=r"Optional\[([^]]+)\]",
        replacement=r"\1 | None",
        file_extensions=[".py"],
    ),
    # Migration of imports from collections.abc
    MigrationRule(
        name="callable_import_modernization",
        description="Replace typing.Callable with collections.abc.Callable",
        pattern=r"from typing import(.*)Callable(.*)",
        replacement=r"from collections.abc import Callable\nfrom typing import\1\2",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="iterator_import_modernization",
        description="Replace typing.Iterator with collections.abc.Iterator",
        pattern=r"from typing import(.*)Iterator(.*)",
        replacement=r"from collections.abc import Iterator\nfrom typing import\1\2",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="iterable_import_modernization",
        description="Replace typing.Iterable with collections.abc.Iterable",
        pattern=r"from typing import(.*)Iterable(.*)",
        replacement=r"from collections.abc import Iterable\nfrom typing import\1\2",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    # Migration of modern f-strings
    MigrationRule(
        name="percent_format_modernization",
        description="Replace % formatting with f-strings",
        pattern=r'"([^"]*%[sd][^"]*)" % \(([^)]+)\)',
        replacement=r'f"\1".format(\2)',
        file_extensions=[".py"],
    ),
    # Migration of docstrings to modern format
    MigrationRule(
        name="docstring_args_modernization",
        description="Modernize the format of docstrings Args:",
        pattern=r"(\s+)Args:\s*\n(\s+)(\w+) \(([^)]+)\): (.+)",
        replacement=r"\1Args:\n\2    \3: \5",
        file_extensions=[".py"],
    ),
]


class CodeMigrator:
    """
    Code migrator to apply modernization rules.

    Scans the Python files of the project and automatically applies
    migration rules to Python 3.12+.
    """

    def __init__(self, project_root: Path) -> None:
        """
        Initializes the migrator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.dry_run = True
        self.stats: dict[str, Any] = {
            "files_processed": 0,
            "files_modified": 0,
            "total_changes": 0,
            "changes_by_rule": {},
        }

    def migrate_project(self, dry_run: bool = True) -> dict[str, Any]:
        """
        Migrates the entire project to Python 3.12+.

        Args:
            dry_run: If True, shows changes without applying them

        Returns:
            Migration statistics
        """
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "total_changes": 0,
            "changes_by_rule": {},
        }

        logger.info(f"Starting project migration (dry_run={dry_run})")

        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))

        # Exclude certain directories
        excluded_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "build",
            "dist",
            ".pytest_cache",
        }
        python_files = [
            f
            for f in python_files
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]

        logger.info(f"Found {len(python_files)} Python files to process")

        for file_path in python_files:
            self._migrate_file(file_path)

        # Final report
        logger.info(f"Migration completed: {self.stats}")
        return self.stats

    def _migrate_file(self, file_path: Path) -> None:
        """
        Migrates an individual file.

        Args:
            file_path: Path to the file to migrate
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            self.stats["files_processed"] += 1
            current_content = original_content
            total_file_changes = 0

            # Applying all rules
            for rule in MIGRATION_RULES:
                if file_path.suffix in rule.file_extensions:
                    new_content, changes = rule.apply(current_content)

                    if changes > 0:
                        logger.debug(
                            f"Rule '{rule.name}' applied to {file_path}: "
                            f"{changes} changes"
                        )
                        current_content = new_content
                        total_file_changes += changes

                        # Updating statistics
                        if rule.name not in self.stats["changes_by_rule"]:
                            self.stats["changes_by_rule"][rule.name] = 0
                        self.stats["changes_by_rule"][rule.name] += changes

            # Save if changes were made
            if total_file_changes > 0:
                self.stats["files_modified"] += 1
                self.stats["total_changes"] += total_file_changes

                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(current_content)
                    logger.info(
                        f"File modified: {file_path} " f"({total_file_changes} changes)"
                    )
                else:
                    logger.info(
                        f"[DRY RUN] File to modify: {file_path} "
                        f"({total_file_changes} changes)"
                    )

        except Exception as e:
            logger.error(f"Error migrating {file_path}: {e}")


def generate_migration_report(project_root: Path) -> str:
    """
    Generates a detailed migration report.

    Args:
        project_root: Root directory of the project

    Returns:
        Migration report in Markdown format
    """
    migrator = CodeMigrator(project_root)
    stats = migrator.migrate_project(dry_run=True)

    report = f"""# Migration Report to Python 3.12+

## Summary

- **Files processed**: {stats['files_processed']}
- **Files to modify**: {stats['files_modified']}
- **Total changes**: {stats['total_changes']}

## Changes by rule

"""

    for rule_name, count in stats["changes_by_rule"].items():
        rule = next(r for r in MIGRATION_RULES if r.name == rule_name)
        report += f"### {rule.name}\n"
        report += f"- **Description**: {rule.description}\n"
        report += f"- **Occurrences**: {count}\n\n"

    report += """
## Modernized modules added

1. **domotix.core.dependency_injection**: Modern IoC container with scopes
2. **domotix.core.service_provider**: Service Provider pattern
3. **domotix.core.interfaces**: Protocols and abstract base classes
4. **domotix.core.config**: Configuration with dataclasses and validation
5. **domotix.core.logging_system**: Structured logging with context
6. **domotix.globals.exceptions**: Modernized exception hierarchy
7. **domotix.core.monitoring**: Metrics and health checks
8. **domotix.factories**: Modern factory with dependency injection

## Next steps

1. Run the migration with `dry_run=False`
2. Update tests to use new modules
3. Gradually migrate existing controllers and repositories
4. Add missing type annotations
5. Configure the monitoring system in production

## Applied best practices

- ✅ Modern type syntax (dict instead of Dict, | instead of Union)
- ✅ Imports from collections.abc where appropriate
- ✅ Dataclasses with slots for performance
- ✅ Protocols for interfaces
- ✅ Context managers for resource management
- ✅ Structured logging with context
- ✅ Error handling with standardized codes
- ✅ Modern dependency injection
- ✅ Centralized and validated configuration
- ✅ Integrated monitoring and metrics
"""

    return report


def main() -> None:
    """
    Main entry point for migration.

    Runs the migration in dry-run mode by default.
    """
    project_root = Path(__file__).parent.parent

    # Generate the report
    report = generate_migration_report(project_root)

    # Save the report
    report_path = project_root / "MIGRATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Migration report generated: {report_path}")

    # Migration in dry-run
    migrator = CodeMigrator(project_root)
    stats = migrator.migrate_project(dry_run=True)

    print(f"Migration completed (dry-run): {stats}")
    print("To apply the changes, run with dry_run=False")


if __name__ == "__main__":
    main()
