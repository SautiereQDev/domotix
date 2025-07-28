"""
Modern configuration for the Domotix application.

This module uses the latest Python features for configuration:
- dataclasses with slots for performance
- Pydantic for validation (if available)
- Environment-based configuration with sensible defaults

Classes:
    DatabaseConfig: Database configuration
    ApplicationConfig: Global application configuration
    LoggingConfig: Logging system configuration
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final

from .singleton import SingletonMeta

try:
    from pydantic import BaseModel, Field, field_validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


# Constantes pour la configuration
DEFAULT_DATABASE_PATH: Final[Path] = Path("domotix.db")
DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_DEVICE_LIMIT: Final[int] = 1000
DEFAULT_TIMEOUT: Final[float] = 30.0


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
    database_path: Path = field(default_factory=lambda: DEFAULT_DATABASE_PATH)
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
    format_string: str = DEFAULT_LOG_FORMAT
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
        db_path = os.getenv("DOMOTIX_DB_PATH", str(DEFAULT_DATABASE_PATH))
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


class ConfigManager(metaclass=SingletonMeta):
    """
    Gestionnaire singleton pour la configuration de l'application.

    Évite l'utilisation de variables globales et fournit un point
    d'accès centralisé pour la configuration.
    """

    def __init__(self) -> None:
        """Initialise le gestionnaire de configuration."""
        self._config_instance: ApplicationConfig | None = None

    def get_config(self) -> ApplicationConfig:
        """
        Récupère la configuration globale de l'application.

        Utilise un singleton paresseux pour éviter les recharges multiples.

        Returns:
            Configuration globale de l'application
        """
        if self._config_instance is None:
            self._config_instance = ApplicationConfig.from_environment()
        return self._config_instance

    def reset_config(self) -> None:
        """
        Remet à zéro la configuration globale.

        Utile pour les tests et le rechargement de configuration.
        """
        self._config_instance = None

    @classmethod
    def reset_instance(cls) -> None:
        """
        Remet à zéro l'instance singleton.

        Utile pour les tests pour créer une nouvelle instance propre.
        """
        SingletonMeta.reset_instance(cls)


def get_config() -> ApplicationConfig:
    """
    Récupère la configuration globale de l'application.

    Returns:
        Configuration globale de l'application
    """
    return ConfigManager().get_config()


def reset_config() -> None:
    """
    Remet à zéro la configuration globale.

    Utile pour les tests et le rechargement de configuration.
    """
    ConfigManager().reset_config()


# Configuration Pydantic alternative (si disponible)
if PYDANTIC_AVAILABLE:

    class PydanticDatabaseConfig(BaseModel):
        """Configuration de base de données avec validation Pydantic."""

        database_type: DatabaseType = DatabaseType.SQLITE
        database_path: Path = DEFAULT_DATABASE_PATH
        echo_sql: bool = False
        pool_size: int = Field(default=5, ge=1, le=50)
        max_overflow: int = Field(default=10, ge=0, le=100)

        @field_validator("database_path")
        @classmethod
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
