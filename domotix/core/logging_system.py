"""
Modern logging system for Domotix.

This module implements a robust logging system using:
- Structured logger with context
- Automatic file rotation
- JSON formatting for production logs
- Support for asynchronous logs (if asyncio is used)

Classes:
    ContextLogger: Logger with business context
    LoggingManager: Centralized log manager
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from domotix.core.config import get_config

# Context variable pour le contexte des logs
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})


@dataclass(slots=True)
class LogRecord:
    """
    Enregistrement de log structuré.

    Utilise dataclass avec slots pour les performances
    et permet la sérialisation JSON native.
    """

    timestamp: datetime
    level: str
    logger_name: str
    message: str
    module: str | None = None
    function: str | None = None
    line_number: int | None = None
    context: dict[str, Any] = field(default_factory=dict)
    exception: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convertit l'enregistrement en dictionnaire.

        Returns:
            Dictionnaire représentant l'enregistrement
        """
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """
        Sérialise l'enregistrement en JSON.

        Returns:
            Chaîne JSON de l'enregistrement
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=None)


class JsonFormatter(logging.Formatter):
    """
    Formateur JSON pour les logs structurés.

    Convertit les enregistrements de log Python standard
    en format JSON structuré.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formate un enregistrement de log en JSON.

        Args:
            record: Enregistrement de log Python standard

        Returns:
            Chaîne JSON formatée
        """
        # Récupération du contexte global
        context = _log_context.get({})

        # Création de l'enregistrement structuré
        log_record = LogRecord(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            context=context.copy(),
        )

        # Ajout des informations d'exception si présentes
        if record.exc_info:
            log_record.exception = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        return log_record.to_json()


class ContextLogger:
    """
    Logger avec support du contexte métier.

    Permet d'ajouter automatiquement des informations contextuelles
    à tous les logs (utilisateur, session, transaction, etc.).
    """

    def __init__(self, name: str) -> None:
        """
        Initialise le logger avec contexte.

        Args:
            name: Nom du logger
        """
        self._logger = logging.getLogger(name)
        self._name = name

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log un message de debug avec contexte."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log un message d'information avec contexte."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log un message d'avertissement avec contexte."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log un message d'erreur avec contexte."""
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log un message critique avec contexte."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log une exception avec traceback et contexte."""
        self._log_with_context(logging.ERROR, message, exc_info=True, **kwargs)

    def _log_with_context(
        self, level: int, message: str, exc_info: bool = False, **kwargs: Any
    ) -> None:
        """
        Log un message avec le contexte actuel.

        Args:
            level: Niveau de log
            message: Message à logger
            exc_info: Inclure les informations d'exception
            **kwargs: Contexte supplémentaire
        """
        if not self._logger.isEnabledFor(level):
            return

        # Fusion du contexte global et local
        current_context = _log_context.get({})
        if kwargs:
            current_context = {**current_context, **kwargs}

        # Mise à jour temporaire du contexte
        token = _log_context.set(current_context)
        try:
            self._logger.log(level, message, exc_info=exc_info)
        finally:
            _log_context.reset(token)

    @contextmanager
    def context(self, **context_data: Any) -> Iterator[None]:
        """
        Gestionnaire de contexte pour ajouter temporairement du contexte.

        Args:
            **context_data: Données de contexte à ajouter

        Yields:
            None

        Example:
            with logger.context(user_id="123", operation="device_update"):
                logger.info("Mise à jour du dispositif")
        """
        current_context = _log_context.get({})
        new_context = {**current_context, **context_data}

        token = _log_context.set(new_context)
        try:
            yield
        finally:
            _log_context.reset(token)


class LoggingManager:
    """
    Gestionnaire centralisé du système de logging.

    Configure et gère tous les aspects du logging de l'application:
    - Handlers multiples (console, fichier, rotation)
    - Formatage approprié selon l'environnement
    - Configuration des niveaux par module
    """

    _instance: LoggingManager | None = None
    _initialized: bool = False

    def __new__(cls) -> LoggingManager:
        """Singleton pattern pour le gestionnaire de logging."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialise le gestionnaire (une seule fois)."""
        if not self._initialized:
            self._setup_logging()
            LoggingManager._initialized = True

    def _setup_logging(self) -> None:
        """Configure le système de logging."""
        config = get_config()
        logging_config = config.logging

        # Configuration du logger racine
        root_logger = logging.getLogger()
        root_logger.setLevel(logging_config.level.value)

        # Suppression des handlers existants
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Handler console
        if logging_config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging_config.level.value)

            if config.debug:
                # Format détaillé en mode debug
                console_formatter = logging.Formatter(
                    logging_config.format_string, datefmt="%Y-%m-%d %H:%M:%S"
                )
            else:
                # Format JSON en production
                console_formatter = JsonFormatter()

            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # Handler fichier avec rotation
        if logging_config.log_file is not None:
            file_handler = logging.handlers.RotatingFileHandler(
                logging_config.log_file,
                maxBytes=10_000_000,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging_config.level.value)
            file_handler.setFormatter(JsonFormatter())
            root_logger.addHandler(file_handler)

        # Configuration spécifique aux modules Domotix
        self._configure_module_loggers()

    def _configure_module_loggers(self) -> None:
        """Configure les loggers spécifiques aux modules."""
        # Logger pour SQLAlchemy (plus silencieux)
        sqlalchemy_logger = logging.getLogger("sqlalchemy")
        sqlalchemy_logger.setLevel(logging.WARNING)

        # Logger pour les repositories (niveau INFO minimum)
        repo_logger = logging.getLogger("domotix.repositories")
        repo_logger.setLevel(logging.INFO)

        # Logger pour les contrôleurs (niveau DEBUG en mode debug)
        config = get_config()
        controller_level = logging.DEBUG if config.debug else logging.INFO
        controller_logger = logging.getLogger("domotix.controllers")
        controller_logger.setLevel(controller_level)

    @classmethod
    def get_logger(cls, name: str) -> ContextLogger:
        """
        Récupère un logger avec contexte pour un module.

        Args:
            name: Nom du module (généralement __name__)

        Returns:
            Logger avec support du contexte
        """
        # Assure que le gestionnaire est initialisé
        if not cls._initialized:
            cls()

        return ContextLogger(name)

    @classmethod
    def reset(cls) -> None:
        """
        Remet à zéro le gestionnaire de logging.

        Utile pour les tests et le rechargement de configuration.
        """
        cls._instance = None
        cls._initialized = False


# Fonctions utilitaires pour l'usage quotidien
def get_logger(name: str) -> ContextLogger:
    """
    Récupère un logger pour un module.

    Args:
        name: Nom du module (généralement __name__)

    Returns:
        Logger avec contexte

    Example:
        logger = get_logger(__name__)
        logger.info("Application démarrée")
    """
    return LoggingManager.get_logger(name)


@contextmanager
def log_context(**context_data: Any) -> Iterator[None]:
    """
    Gestionnaire de contexte global pour les logs.

    Args:
        **context_data: Données de contexte

    Yields:
        None

    Example:
        with log_context(request_id="abc123", user_id="456"):
            # Tous les logs auront ce contexte
            logger.info("Traitement de la requête")
    """
    current_context = _log_context.get({})
    new_context = {**current_context, **context_data}

    token = _log_context.set(new_context)
    try:
        yield
    finally:
        _log_context.reset(token)


# Initialisation automatique du système de logging
_logging_manager = LoggingManager()
