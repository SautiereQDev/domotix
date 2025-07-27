"""
Configuration moderne pour l'application Domotix.

Ce module utilise les dernières fonctionnalités Python pour la configuration:
- dataclasses avec slots pour les performances
- Pydantic pour la validation (si disponible)
- Configuration par environnement avec des valeurs par défaut sensées

Classes:
    DatabaseConfig: Configuration de la base de données
    ApplicationConfig: Configuration globale de l'application
    LoggingConfig: Configuration du système de logs
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final

try:
    from pydantic import BaseModel, Field, validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class LogLevel(str, Enum):
    """Niveaux de log disponibles."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseType(str, Enum):
    """Types de base de données supportés."""

    SQLITE = "sqlite"
    MEMORY = "memory"


@dataclass(slots=True, frozen=True)
class DatabaseConfig:
    """
    Configuration de la base de données avec valeurs par défaut.

    Utilise dataclass avec slots pour de meilleures performances
    et frozen=True pour l'immutabilité.
    """

    database_type: DatabaseType = DatabaseType.SQLITE
    database_path: Path = field(default_factory=lambda: Path("domotix.db"))
    echo_sql: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def connection_string(self) -> str:
        """
        Génère la chaîne de connexion SQLAlchemy.

        Returns:
            Chaîne de connexion formatée
        """
        if self.database_type == DatabaseType.MEMORY:
            return "sqlite:///:memory:"
        return f"sqlite:///{self.database_path}"

    def __post_init__(self) -> None:
        """Validation post-initialisation."""
        if self.database_type == DatabaseType.SQLITE:
            # Assure que le répertoire parent existe
            self.database_path.parent.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True, frozen=True)
class LoggingConfig:
    """Configuration du système de logs."""

    level: LogLevel = LogLevel.INFO
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Path | None = None
    console_output: bool = True

    def __post_init__(self) -> None:
        """Validation et création du fichier de log si nécessaire."""
        if self.log_file is not None:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True, frozen=True)
class ApplicationConfig:
    """
    Configuration globale de l'application Domotix.

    Centralise toute la configuration avec des valeurs par défaut
    intelligentes et la possibilité de surcharge par variables d'environnement.
    """

    app_name: str = "Domotix"
    version: str = "1.0.0"
    debug: bool = False
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Configuration des dispositifs
    max_devices: int = 100
    device_timeout: float = 30.0
    state_persistence_interval: float = 5.0

    @classmethod
    def from_environment(cls) -> ApplicationConfig:
        """
        Crée une configuration à partir des variables d'environnement.

        Variables d'environnement supportées:
        - DOMOTIX_DEBUG: Active le mode debug
        - DOMOTIX_DB_PATH: Chemin vers la base de données
        - DOMOTIX_LOG_LEVEL: Niveau de log
        - DOMOTIX_LOG_FILE: Fichier de log

        Returns:
            Configuration initialisée depuis l'environnement
        """
        debug = os.getenv("DOMOTIX_DEBUG", "false").lower() == "true"

        # Configuration de la base de données
        db_path = os.getenv("DOMOTIX_DB_PATH", "domotix.db")
        db_echo = os.getenv("DOMOTIX_DB_ECHO", "false").lower() == "true"

        database_config = DatabaseConfig(database_path=Path(db_path), echo_sql=db_echo)

        # Configuration des logs
        log_level_str = os.getenv("DOMOTIX_LOG_LEVEL", "INFO").upper()
        log_level = (
            LogLevel(log_level_str)
            if log_level_str in LogLevel.__members__
            else LogLevel.INFO
        )

        log_file_path = os.getenv("DOMOTIX_LOG_FILE")
        log_file = Path(log_file_path) if log_file_path else None

        logging_config = LoggingConfig(level=log_level, log_file=log_file)

        return cls(debug=debug, database=database_config, logging=logging_config)


# Configuration globale singleton
_config_instance: ApplicationConfig | None = None


def get_config() -> ApplicationConfig:
    """
    Récupère la configuration globale de l'application.

    Utilise un singleton paresseux pour éviter les recharges multiples.

    Returns:
        Configuration globale de l'application
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ApplicationConfig.from_environment()
    return _config_instance


def reset_config() -> None:
    """
    Remet à zéro la configuration globale.

    Utile pour les tests et le rechargement de configuration.
    """
    global _config_instance
    _config_instance = None


# Configuration Pydantic alternative (si disponible)
if PYDANTIC_AVAILABLE:

    class PydanticDatabaseConfig(BaseModel):
        """Configuration de base de données avec validation Pydantic."""

        database_type: DatabaseType = DatabaseType.SQLITE
        database_path: Path = Path("domotix.db")
        echo_sql: bool = False
        pool_size: int = Field(default=5, ge=1, le=50)
        max_overflow: int = Field(default=10, ge=0, le=100)

        @validator("database_path")
        def validate_database_path(cls, v: Path) -> Path:
            """Valide et crée le répertoire parent si nécessaire."""
            if v.suffix != ".db":
                raise ValueError(
                    "Le fichier de base de données doit avoir l'extension .db"
                )
            v.parent.mkdir(parents=True, exist_ok=True)
            return v

        @property
        def connection_string(self) -> str:
            """Génère la chaîne de connexion."""
            if self.database_type == DatabaseType.MEMORY:
                return "sqlite:///:memory:"
            return f"sqlite:///{self.database_path}"

        class Config:
            """Configuration Pydantic."""

            use_enum_values = True
            arbitrary_types_allowed = True


# Constantes pour la configuration
DEFAULT_DATABASE_PATH: Final[Path] = Path("domotix.db")
DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_DEVICE_LIMIT: Final[int] = 1000
DEFAULT_TIMEOUT: Final[float] = 30.0
