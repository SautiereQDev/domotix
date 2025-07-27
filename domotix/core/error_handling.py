"""
Décorateurs et utilitaires pour la gestion d'erreurs améliorée.

Ce module fournit des décorateurs et utilitaires pour améliorer
la gestion d'erreurs dans toute l'application.
"""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from domotix.globals.exceptions import (
    DeviceError,
    ErrorCode,
    RepositoryError,
    ValidationError,
)

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def handle_repository_errors(
    operation: str = "unknown", reraise: bool = True, default_return: Any = None
) -> Callable[[F], F]:
    """
    Décorateur pour gérer les erreurs de repository.

    Args:
        operation: Nom de l'opération pour le contexte d'erreur
        reraise: Si True, relance l'exception après logging
        default_return: Valeur par défaut si pas de reraise

    Returns:
        Décorateur configuré
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                logger.error(f"Contrainte violée lors de '{operation}': {e}")
                if reraise:
                    raise RepositoryError(
                        f"Violation de contrainte lors de l'opération '{operation}'",
                        operation=operation,
                        error_code=ErrorCode.REPOSITORY_CONSTRAINT_VIOLATION,
                        cause=e,
                    )
                return default_return
            except SQLAlchemyError as e:
                logger.error(f"Erreur SQLAlchemy lors de '{operation}': {e}")
                if reraise:
                    raise RepositoryError(
                        f"Erreur de base de données lors de l'opération '{operation}'",
                        operation=operation,
                        error_code=ErrorCode.REPOSITORY_CONNECTION_ERROR,
                        cause=e,
                    )
                return default_return
            except Exception as e:
                logger.exception(f"Erreur inattendue lors de '{operation}': {e}")
                if reraise:
                    raise RepositoryError(
                        f"Erreur inattendue lors de l'opération '{operation}'",
                        operation=operation,
                        error_code=ErrorCode.REPOSITORY_CONNECTION_ERROR,
                        cause=e,
                    )
                return default_return

        return wrapper  # type: ignore[return-value]

    return decorator


def validate_device(device: Any) -> None:
    """
    Valide un dispositif avant opération.

    Args:
        device: Dispositif à valider

    Raises:
        ValidationError: Si la validation échoue
    """
    if not device:
        raise ValidationError(
            "Dispositif requis",
            field_name="device",
            field_value=device,
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )

    if not hasattr(device, "name") or not device.name or not device.name.strip():
        raise ValidationError(
            "Le nom du dispositif est requis",
            field_name="name",
            field_value=getattr(device, "name", None),
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )


def validate_device_id(device_id: str) -> None:
    """
    Valide un ID de dispositif.

    Args:
        device_id: ID à valider

    Raises:
        ValidationError: Si la validation échoue
    """
    if not device_id or not device_id.strip():
        raise ValidationError(
            "ID de dispositif requis",
            field_name="device_id",
            field_value=device_id,
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )


def handle_controller_errors(
    operation: str = "unknown", device_id: Optional[str] = None
) -> Callable[[F], F]:
    """
    Décorateur pour gérer les erreurs de contrôleur.

    Args:
        operation: Nom de l'opération
        device_id: ID du dispositif concerné (optionnel)

    Returns:
        Décorateur configuré
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError:
                # Répropagate les erreurs de validation
                raise
            except RepositoryError:
                # Répropagate les erreurs de repository
                raise
            except DeviceError:
                # Répropagage les erreurs de dispositif
                raise
            except Exception as e:
                logger.exception(f"Erreur contrôleur lors de '{operation}': {e}")
                # Enrichir avec le contexte du contrôleur
                actual_device_id = (
                    device_id
                    or kwargs.get("device_id")
                    or (args[1] if len(args) > 1 else None)
                )
                raise DeviceError(
                    f"Erreur lors de l'opération '{operation}' sur le dispositif",
                    device_id=actual_device_id,
                    error_code=ErrorCode.CONTROLLER_OPERATION_FAILED,
                    cause=e,
                )

        return wrapper  # type: ignore[return-value]

    return decorator


def safe_execute(
    func: Callable, *args, default_return: Any = None, log_errors: bool = True, **kwargs
) -> Any:
    """
    Exécute une fonction de manière sécurisée avec gestion d'erreurs.

    Args:
        func: Fonction à exécuter
        *args: Arguments positionnels
        default_return: Valeur par défaut en cas d'erreur
        log_errors: Si True, log les erreurs
        **kwargs: Arguments nommés

    Returns:
        Résultat de la fonction ou valeur par défaut
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.exception(f"Erreur lors de l'exécution de {func.__name__}: {e}")
        return default_return


class ErrorContext:
    """Gestionnaire de contexte pour capturer et enrichir les erreurs."""

    def __init__(self, operation: str, **context):
        """
        Initialise le contexte d'erreur.

        Args:
            operation: Nom de l'opération
            **context: Contexte additionnel
        """
        self.operation = operation
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, Exception):
            # Enrichir l'exception avec le contexte
            if hasattr(exc_val, "operation"):
                exc_val.operation = self.operation
            if hasattr(exc_val, "context"):
                exc_val.context.update(self.context)
        return False  # Ne supprime pas l'exception


def create_validation_error(
    message: str,
    field_name: str,
    field_value: Any = None,
    suggestions: Optional[list] = None,
) -> ValidationError:
    """
    Crée une erreur de validation avec suggestions.

    Args:
        message: Message d'erreur
        field_name: Nom du champ
        field_value: Valeur du champ
        suggestions: Suggestions pour corriger l'erreur

    Returns:
        ValidationError configurée
    """
    error = ValidationError(
        message,
        field_name=field_name,
        field_value=field_value,
        error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
    )

    if suggestions:
        error.context.user_data["suggestions"] = suggestions

    return error


def format_error_for_user(error: Exception) -> str:
    """
    Formate une erreur pour l'affichage utilisateur.

    Args:
        error: Exception à formater

    Returns:
        Message formaté pour l'utilisateur
    """
    if hasattr(error, "error_code") and hasattr(error, "context"):
        # Erreur Domotix avec contexte
        if (
            hasattr(error.context, "user_data")
            and "suggestions" in error.context.user_data
        ):
            suggestions = error.context.user_data["suggestions"]
            return f"{str(error)}\\n💡 Suggestions: {', '.join(suggestions)}"

    # Erreur standard
    return str(error)
