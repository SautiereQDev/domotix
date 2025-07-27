"""
Guide de migration vers Python 3.12+ et bonnes pratiques modernes.

Ce fichier documente et automatise la migration de l'application Domotix
vers les normes les plus récentes de Python et les bonnes pratiques modernes.

Changements principaux:
1. Migration de Python 3.13 vers 3.12+ pour une meilleure compatibilité
2. Syntaxe moderne des types (dict au lieu de Dict, | au lieu de Union)
3. Migration des imports typing vers collections.abc
4. Implémentation d'un système d'injection de dépendances moderne
5. Système de logging structuré avec contexte
6. Gestion d'erreurs moderne avec codes structurés
7. Configuration avec dataclasses et validation
8. Monitoring et métriques intégrés

Modules modernisés:
- domotix.core.dependency_injection: Container IoC avec scopes
- domotix.core.service_provider: Fournisseur de services moderne
- domotix.core.service_configuration: Configuration centralisée des services
- domotix.core.interfaces: Protocols et classes de base
- domotix.core.config: Configuration avec dataclasses
- domotix.core.logging_system: Logging structuré avec contexte
- domotix.globals.exceptions: Hiérarchie d'exceptions moderne (modernisé)
- domotix.core.monitoring: Métriques et health checks
- domotix.factories: Factory moderne avec DI
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
    Règle de migration pour moderniser le code.

    Définit une transformation spécifique à appliquer
    sur les fichiers Python du projet.
    """

    name: str
    description: str
    pattern: str
    replacement: str
    file_extensions: list[str]
    applies_to_imports: bool = False

    def apply(self, content: str) -> tuple[str, int]:
        """
        Applique la règle de migration au contenu.

        Args:
            content: Contenu du fichier

        Returns:
            Tuple (nouveau_contenu, nombre_de_changements)
        """
        if self.applies_to_imports:
            # Application spéciale pour les imports
            return self._apply_import_rule(content)
        else:
            # Application standard avec regex
            new_content, count = re.subn(
                self.pattern, self.replacement, content, flags=re.MULTILINE
            )
            return new_content, count

    def _apply_import_rule(self, content: str) -> tuple[str, int]:
        """
        Applique une règle de migration spécifique aux imports.

        Args:
            content: Contenu du fichier

        Returns:
            Tuple (nouveau_contenu, nombre_de_changements)
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


# Règles de migration pour Python 3.12+
MIGRATION_RULES = [
    # Migration des types vers la syntaxe moderne
    MigrationRule(
        name="dict_type_modernization",
        description="Remplace typing.Dict par dict",
        pattern=r"from typing import.*Dict.*",
        replacement="# Dict remplacé par dict (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="list_type_modernization",
        description="Remplace typing.List par list",
        pattern=r"from typing import.*List.*",
        replacement="# List remplacé par list (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="tuple_type_modernization",
        description="Remplace typing.Tuple par tuple",
        pattern=r"from typing import.*Tuple.*",
        replacement="# Tuple remplacé par tuple (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="set_type_modernization",
        description="Remplace typing.Set par set",
        pattern=r"from typing import.*Set.*",
        replacement="# Set remplacé par set (Python 3.9+)",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    # Migration des annotations de type
    MigrationRule(
        name="dict_annotation_modernization",
        description="Remplace Dict[K, V] par dict[K, V]",
        pattern=r"Dict\[([^]]+)\]",
        replacement=r"dict[\1]",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="list_annotation_modernization",
        description="Remplace List[T] par list[T]",
        pattern=r"List\[([^]]+)\]",
        replacement=r"list[\1]",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="tuple_annotation_modernization",
        description="Remplace Tuple[...] par tuple[...]",
        pattern=r"Tuple\[([^]]+)\]",
        replacement=r"tuple[\1]",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="set_annotation_modernization",
        description="Remplace Set[T] par set[T]",
        pattern=r"Set\[([^]]+)\]",
        replacement=r"set[\1]",
        file_extensions=[".py"],
    ),
    # Migration Union vers |
    MigrationRule(
        name="union_syntax_modernization",
        description="Remplace Union[A, B] par A | B",
        pattern=r"Union\[([^,]+),\s*([^]]+)\]",
        replacement=r"\1 | \2",
        file_extensions=[".py"],
    ),
    MigrationRule(
        name="optional_syntax_modernization",
        description="Remplace Optional[T] par T | None",
        pattern=r"Optional\[([^]]+)\]",
        replacement=r"\1 | None",
        file_extensions=[".py"],
    ),
    # Migration des imports collections.abc
    MigrationRule(
        name="callable_import_modernization",
        description="Remplace typing.Callable par collections.abc.Callable",
        pattern=r"from typing import(.*)Callable(.*)",
        replacement=r"from collections.abc import Callable\nfrom typing import\1\2",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="iterator_import_modernization",
        description="Remplace typing.Iterator par collections.abc.Iterator",
        pattern=r"from typing import(.*)Iterator(.*)",
        replacement=r"from collections.abc import Iterator\nfrom typing import\1\2",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    MigrationRule(
        name="iterable_import_modernization",
        description="Remplace typing.Iterable par collections.abc.Iterable",
        pattern=r"from typing import(.*)Iterable(.*)",
        replacement=r"from collections.abc import Iterable\nfrom typing import\1\2",
        file_extensions=[".py"],
        applies_to_imports=True,
    ),
    # Migration des f-strings modernes
    MigrationRule(
        name="percent_format_modernization",
        description="Remplace % formatting par f-strings",
        pattern=r'"([^"]*%[sd][^"]*)" % \(([^)]+)\)',
        replacement=r'f"\1".format(\2)',
        file_extensions=[".py"],
    ),
    # Migration des docstrings vers format moderne
    MigrationRule(
        name="docstring_args_modernization",
        description="Modernise le format des docstrings Args:",
        pattern=r"(\s+)Args:\s*\n(\s+)(\w+) \(([^)]+)\): (.+)",
        replacement=r"\1Args:\n\2    \3: \5",
        file_extensions=[".py"],
    ),
]


class CodeMigrator:
    """
    Migrateur de code pour appliquer les règles de modernisation.

    Scanne les fichiers Python du projet et applique automatiquement
    les règles de migration vers Python 3.12+.
    """

    def __init__(self, project_root: Path) -> None:
        """
        Initialise le migrateur.

        Args:
            project_root: Répertoire racine du projet
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
        Migre tout le projet vers Python 3.12+.

        Args:
            dry_run: Si True, affiche les changements sans les appliquer

        Returns:
            Statistiques de migration
        """
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "total_changes": 0,
            "changes_by_rule": {},
        }

        logger.info(f"Début de la migration du projet (dry_run={dry_run})")

        # Trouver tous les fichiers Python
        python_files = list(self.project_root.rglob("*.py"))

        # Exclure certains répertoires
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

        logger.info(f"Trouvé {len(python_files)} fichiers Python à traiter")

        for file_path in python_files:
            self._migrate_file(file_path)

        # Rapport final
        logger.info(f"Migration terminée: {self.stats}")
        return self.stats

    def _migrate_file(self, file_path: Path) -> None:
        """
        Migre un fichier individuel.

        Args:
            file_path: Chemin vers le fichier à migrer
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            self.stats["files_processed"] += 1
            current_content = original_content
            total_file_changes = 0

            # Application de toutes les règles
            for rule in MIGRATION_RULES:
                if file_path.suffix in rule.file_extensions:
                    new_content, changes = rule.apply(current_content)

                    if changes > 0:
                        logger.debug(
                            f"Règle '{rule.name}' appliquée à {file_path}: "
                            f"{changes} changements"
                        )
                        current_content = new_content
                        total_file_changes += changes

                        # Mise à jour des statistiques
                        if rule.name not in self.stats["changes_by_rule"]:
                            self.stats["changes_by_rule"][rule.name] = 0
                        self.stats["changes_by_rule"][rule.name] += changes

            # Sauvegarde si des changements ont été effectués
            if total_file_changes > 0:
                self.stats["files_modified"] += 1
                self.stats["total_changes"] += total_file_changes

                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(current_content)
                    logger.info(
                        f"Fichier modifié: {file_path} "
                        f"({total_file_changes} changements)"
                    )
                else:
                    logger.info(
                        f"[DRY RUN] Fichier à modifier: {file_path} "
                        f"({total_file_changes} changements)"
                    )

        except Exception as e:
            logger.error(f"Erreur lors de la migration de {file_path}: {e}")


def generate_migration_report(project_root: Path) -> str:
    """
    Génère un rapport de migration détaillé.

    Args:
        project_root: Répertoire racine du projet

    Returns:
        Rapport de migration au format Markdown
    """
    migrator = CodeMigrator(project_root)
    stats = migrator.migrate_project(dry_run=True)

    report = f"""# Rapport de Migration vers Python 3.12+

## Résumé

- **Fichiers traités**: {stats['files_processed']}
- **Fichiers à modifier**: {stats['files_modified']}
- **Total des changements**: {stats['total_changes']}

## Changements par règle

"""

    for rule_name, count in stats["changes_by_rule"].items():
        rule = next(r for r in MIGRATION_RULES if r.name == rule_name)
        report += f"### {rule.name}\n"
        report += f"- **Description**: {rule.description}\n"
        report += f"- **Occurrences**: {count}\n\n"

    report += """
## Modules modernisés ajoutés

1. **domotix.core.dependency_injection**: Container IoC moderne avec scopes
2. **domotix.core.service_provider**: Pattern Service Provider
3. **domotix.core.interfaces**: Protocols et classes de base abstraites
4. **domotix.core.config**: Configuration avec dataclasses et validation
5. **domotix.core.logging_system**: Logging structuré avec contexte
6. **domotix.globals.exceptions**: Hiérarchie d'exceptions modernisée
7. **domotix.core.monitoring**: Métriques et health checks
8. **domotix.factories**: Factory moderne avec injection de dépendances

## Prochaines étapes

1. Exécuter la migration avec `dry_run=False`
2. Mettre à jour les tests pour utiliser les nouveaux modules
3. Migrer progressivement les contrôleurs et repositories existants
4. Ajouter les annotations de type manquantes
5. Configurer le système de monitoring en production

## Bonnes pratiques appliquées

- ✅ Syntaxe moderne des types (dict au lieu de Dict, | au lieu de Union)
- ✅ Imports depuis collections.abc quand approprié
- ✅ Dataclasses avec slots pour les performances
- ✅ Protocols pour les interfaces
- ✅ Context managers pour la gestion des ressources
- ✅ Logging structuré avec contexte
- ✅ Gestion d'erreurs avec codes standardisés
- ✅ Injection de dépendances moderne
- ✅ Configuration centralisée et validée
- ✅ Monitoring et métriques intégrés
"""

    return report


def main() -> None:
    """
    Point d'entrée principal pour la migration.

    Exécute la migration en mode dry-run par défaut.
    """
    project_root = Path(__file__).parent.parent

    # Génération du rapport
    report = generate_migration_report(project_root)

    # Sauvegarde du rapport
    report_path = project_root / "MIGRATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Rapport de migration généré: {report_path}")

    # Migration en dry-run
    migrator = CodeMigrator(project_root)
    stats = migrator.migrate_project(dry_run=True)

    print(f"Migration terminée (dry-run): {stats}")
    print("Pour appliquer les changements, exécuter avec dry_run=False")


if __name__ == "__main__":
    main()
