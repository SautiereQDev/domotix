"""
Module des exceptions personnalisées du système domotique Domotix.

Ce module contient toutes les exceptions personnalisées avec une architecture
moderne suivant les bonnes pratiques Python 3.12+ :
- Hiérarchie d'exceptions structurée
- Codes d'erreur standardisés
- Contexte enrichi pour le debugging
- Support du chaining d'exceptions

Exceptions:
    DomotixError: Exception de base pour toutes les erreurs du système
    DeviceError: Erreurs liées aux dispositifs
    RepositoryError: Erreurs de persistence
    ValidationError: Erreurs de validation
    ControllerError: Erreurs de logique métier
"""

from __future__ import annotations

import sys
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Iterator


class ErrorCode(str, Enum):
    """
    Codes d'erreur standardisés pour l'application.

    Utilise des codes structurés pour faciliter le debugging
    et l'intégration avec des systèmes externes.
    """

    # Erreurs génériques (1xxx)
    UNKNOWN_ERROR = "DMX-1000"
    INVALID_CONFIGURATION = "DMX-1001"
    INITIALIZATION_ERROR = "DMX-1002"

    # Erreurs de dispositifs (2xxx)
    DEVICE_NOT_FOUND = "DMX-2000"
    DEVICE_INVALID_STATE = "DMX-2001"
    DEVICE_COMMUNICATION_ERROR = "DMX-2002"
    DEVICE_TIMEOUT = "DMX-2003"
    DEVICE_ALREADY_EXISTS = "DMX-2004"
    DEVICE_INVALID_TYPE = "DMX-2005"

    # Erreurs de repository (3xxx)
    REPOSITORY_CONNECTION_ERROR = "DMX-3000"
    REPOSITORY_TRANSACTION_ERROR = "DMX-3001"
    REPOSITORY_CONSTRAINT_VIOLATION = "DMX-3002"
    REPOSITORY_DATA_CORRUPTION = "DMX-3003"

    # Erreurs de validation (4xxx)
    VALIDATION_REQUIRED_FIELD = "DMX-4000"
    VALIDATION_INVALID_FORMAT = "DMX-4001"
    VALIDATION_OUT_OF_RANGE = "DMX-4002"
    VALIDATION_INVALID_TYPE = "DMX-4003"

    # Erreurs de contrôleur (5xxx)
    CONTROLLER_OPERATION_FAILED = "DMX-5000"
    CONTROLLER_DEPENDENCY_ERROR = "DMX-5001"
    CONTROLLER_STATE_ERROR = "DMX-5002"

    # Erreurs de commande (6xxx)
    COMMAND_EXECUTION_ERROR = "DMX-6000"
    COMMAND_INVALID_PARAMETER = "DMX-6001"


@dataclass(slots=True, frozen=True)
class ErrorContext:
    """
    Contexte d'erreur pour enrichir les exceptions.

    Capture des informations utiles pour le debugging
    et la résolution de problèmes.
    """

    timestamp: datetime = field(default_factory=datetime.now)
    module: str | None = None
    function: str | None = None
    line_number: int | None = None
    user_data: dict[str, Any] = field(default_factory=dict)
    system_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_frame(cls, frame_info: traceback.FrameSummary) -> ErrorContext:
        """
        Crée un contexte à partir d'informations de stack frame.

        Args:
            frame_info: Informations du frame de la stack

        Returns:
            Contexte d'erreur initialisé
        """
        return cls(
            module=frame_info.filename,
            function=frame_info.name,
            line_number=frame_info.lineno,
        )


class DomotixError(Exception):
    """
    Exception de base pour toutes les erreurs de l'application Domotix.

    Fournit une structure commune pour la gestion d'erreurs avec:
    - Code d'erreur standardisé
    - Contexte enrichi
    - Support du chaining d'exceptions
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Initialise l'exception Domotix.

        Args:
            message: Message d'erreur humainement lisible
            error_code: Code d'erreur standardisé
            context: Contexte de l'erreur
            cause: Exception originale (pour le chaining)
        """
        super().__init__(message)
        self.error_code = error_code
        self.context = context or ErrorContext()
        self.cause = cause

        # Enrichissement automatique du contexte
        if self.context.module is None:
            self._enrich_context_from_stack()

    def _enrich_context_from_stack(self) -> None:
        """Enrichit le contexte avec les informations de la stack."""
        stack = traceback.extract_tb(sys.exc_info()[2])
        if stack:
            # Prend le dernier frame qui n'est pas dans ce module
            for frame in reversed(stack):
                if not frame.filename.endswith("exceptions.py"):
                    self.context = ErrorContext.from_frame(frame)
                    break

    def to_dict(self) -> dict[str, Any]:
        """
        Convertit l'exception en dictionnaire.

        Returns:
            Représentation dictionnaire de l'exception
        """
        return {
            "error_code": self.error_code.value,
            "message": str(self),
            "timestamp": self.context.timestamp.isoformat(),
            "module": self.context.module,
            "function": self.context.function,
            "line_number": self.context.line_number,
            "user_data": self.context.user_data,
            "system_data": self.context.system_data,
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """Représentation chaîne avec code d'erreur."""
        return f"[{self.error_code.value}] {super().__str__()}"


# Exceptions spécialisées modernes (remplacent les anciennes)
class DeviceError(DomotixError):
    """Erreurs liées aux dispositifs."""

    def __init__(
        self,
        message: str,
        device_id: str | None = None,
        error_code: ErrorCode = ErrorCode.DEVICE_NOT_FOUND,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message, error_code, context, cause)
        self.device_id = device_id


class RepositoryError(DomotixError):
    """Erreurs de persistence et d'accès aux données."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        error_code: ErrorCode = ErrorCode.REPOSITORY_CONNECTION_ERROR,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message, error_code, context, cause)
        self.operation = operation


class ValidationError(DomotixError):
    """Erreurs de validation de données."""

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        field_value: Any = None,
        error_code: ErrorCode = ErrorCode.VALIDATION_REQUIRED_FIELD,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message, error_code, context, cause)
        self.field_name = field_name
        self.field_value = field_value


class ControllerError(DomotixError):
    """Erreurs de logique métier dans les contrôleurs."""

    def __init__(
        self,
        message: str,
        controller_name: str | None = None,
        error_code: ErrorCode = ErrorCode.CONTROLLER_OPERATION_FAILED,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message, error_code, context, cause)
        self.controller_name = controller_name


# Exceptions compatibles avec l'ancien système (à migrer progressivement)
class DeviceNotFoundError(DeviceError):
    """Levée quand un dispositif demandé n'est pas trouvé."""

    def __init__(self, device_id: str):
        super().__init__(
            f"Dispositif non trouvé : {device_id}",
            device_id=device_id,
            error_code=ErrorCode.DEVICE_NOT_FOUND,
        )


class InvalidDeviceTypeError(DeviceError):
    """Levée quand un type de dispositif invalide est utilisé."""

    def __init__(self, device_type: str):
        super().__init__(
            f"Type de dispositif invalide : {device_type}",
            error_code=ErrorCode.DEVICE_INVALID_TYPE,
        )
        self.device_type = device_type


class CommandExecutionError(DomotixError):
    """Levée quand l'exécution d'une commande échoue."""

    def __init__(self, command: str, reason: str = ""):
        message = f"Échec de l'exécution de la commande : {command}"
        if reason:
            message += f" - {reason}"

        super().__init__(message, error_code=ErrorCode.COMMAND_EXECUTION_ERROR)
        self.command = command
        self.reason = reason


# Gestionnaire de contexte pour la gestion d'erreurs
@contextmanager
def error_handler(
    logger_name: str | None = None, reraise: bool = True, default_return: Any = None
) -> Iterator[None]:
    """
    Gestionnaire de contexte pour la gestion automatique d'erreurs.

    Args:
        logger_name: Nom du logger à utiliser
        reraise: Si True, relance l'exception après logging
        default_return: Valeur par défaut à retourner si pas de reraise

    Yields:
        None

    Example:
        with error_handler(__name__):
            risky_operation()
    """
    try:
        # Import local pour éviter les dépendances circulaires
        from domotix.core.logging_system import get_logger

        logger = get_logger(logger_name or __name__)
    except ImportError:
        # Fallback si le système de logging moderne n'est pas disponible
        import logging

        logger = logging.getLogger(logger_name or __name__)  # type: ignore[assignment]

    try:
        yield
    except DomotixError as e:
        # Log des erreurs Domotix avec le contexte complet
        if hasattr(logger, "error") and hasattr(e, "to_dict"):
            logger.error(
                f"Erreur Domotix: {e}",
                error_code=e.error_code.value,
                error_context=e.to_dict(),
            )
        else:
            logger.error(f"Erreur Domotix: {e}")

        if reraise:
            raise
        return default_return  # type: ignore[return-value, no-any-return]
    except Exception as e:
        # Conversion des exceptions externes en DomotixError
        domotix_error = DomotixError(
            f"Erreur inattendue: {e}", error_code=ErrorCode.UNKNOWN_ERROR, cause=e
        )

        if hasattr(logger, "exception"):
            logger.exception(f"Erreur inattendue: {e}")
        else:
            logger.error(f"Erreur inattendue: {e}")

        if reraise:
            raise domotix_error from e
        return default_return  # type: ignore[return-value, no-any-return]


# Fonctions utilitaires pour la création d'exceptions
def device_not_found(device_id: str, additional_info: str = "") -> DeviceError:
    """
    Crée une exception DeviceError pour dispositif non trouvé.

    Args:
        device_id: ID du dispositif
        additional_info: Informations supplémentaires

    Returns:
        Exception configurée
    """
    message = f"Dispositif '{device_id}' non trouvé"
    if additional_info:
        message += f": {additional_info}"

    return DeviceError(
        message=message, device_id=device_id, error_code=ErrorCode.DEVICE_NOT_FOUND
    )


def validation_failed(
    field_name: str, field_value: Any, reason: str = ""
) -> ValidationError:
    """
    Crée une exception ValidationError pour échec de validation.

    Args:
        field_name: Nom du champ
        field_value: Valeur du champ
        reason: Raison de l'échec

    Returns:
        Exception configurée
    """
    message = f"Validation échouée pour le champ '{field_name}'"
    if reason:
        message += f": {reason}"

    return ValidationError(
        message=message,
        field_name=field_name,
        field_value=field_value,
        error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
    )
