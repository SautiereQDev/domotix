"""
Decorators and utilities for improved error handling.

This module provides decorators and utilities to enhance
error handling throughout the application.
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
    Decorator to handle repository errors.

    Args:
        operation: Name of the operation for error context
        reraise: If True, re-raises the exception after logging
        default_return: Default value if no re-raise

    Returns:
        Configured decorator
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                logger.error("Constraint violated during '%s': %s", operation, e)
                if reraise:
                    raise RepositoryError(
                        f"Constraint violation during '{operation}' operation",
                        operation=operation,
                        error_code=ErrorCode.REPOSITORY_CONSTRAINT_VIOLATION,
                        cause=e,
                    ) from e
                return default_return
            except SQLAlchemyError as e:
                logger.error("SQLAlchemy error during '%s': %s", operation, e)
                if reraise:
                    raise RepositoryError(
                        f"Database error during '{operation}' operation",
                        operation=operation,
                        error_code=ErrorCode.REPOSITORY_CONNECTION_ERROR,
                        cause=e,
                    ) from e
                return default_return
            except Exception as e:
                logger.exception("Unexpected error during '%s': %s", operation, e)
                if reraise:
                    raise RepositoryError(
                        f"Unexpected error during '{operation}' operation",
                        operation=operation,
                        error_code=ErrorCode.REPOSITORY_CONNECTION_ERROR,
                        cause=e,
                    ) from e
                return default_return

        return wrapper  # type: ignore[return-value]

    return decorator


def validate_device(device: Any) -> None:
    """
    Validate a device before operation.

    Args:
        device: Device to validate

    Raises:
        ValidationError: If validation fails
    """
    if not device:
        raise ValidationError(
            "Device required",
            field_name="device",
            field_value=device,
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )

    if not hasattr(device, "name") or not device.name or not device.name.strip():
        raise ValidationError(
            "Device name is required",
            field_name="name",
            field_value=getattr(device, "name", None),
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )


def validate_device_id(device_id: str) -> None:
    """
    Validate a device ID.

    Args:
        device_id: ID to validate

    Raises:
        ValidationError: If validation fails
    """
    if not device_id or not device_id.strip():
        raise ValidationError(
            "Device ID required",
            field_name="device_id",
            field_value=device_id,
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )


def handle_controller_errors(
    operation: str = "unknown", device_id: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator to handle controller errors.

    Args:
        operation: Name of the operation
        device_id: ID of the concerned device (optional)

    Returns:
        Configured decorator
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError:
                # Re-raise validation errors
                raise
            except RepositoryError:
                # Re-raise repository errors
                raise
            except DeviceError:
                # Re-raise device errors
                raise
            except Exception as e:
                logger.exception("Controller error during '%s': %s", operation, e)
                # Enrich with controller context
                actual_device_id = (
                    device_id
                    or kwargs.get("device_id")
                    or (args[1] if len(args) > 1 else None)
                )
                raise DeviceError(
                    f"Error during '{operation}' operation on device",
                    device_id=actual_device_id,
                    error_code=ErrorCode.CONTROLLER_OPERATION_FAILED,
                    cause=e,
                ) from e

        return wrapper  # type: ignore[return-value]

    return decorator


def safe_execute(
    func: Callable, *args, default_return: Any = None, log_errors: bool = True, **kwargs
) -> Any:
    """
    Execute a function safely with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments
        default_return: Default value in case of error
        log_errors: If True, logs errors
        **kwargs: Named arguments

    Returns:
        Result of the function or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.exception("Error during execution of %s: %s", func.__name__, e)
        return default_return


class ErrorContext:
    """Context manager to capture and enrich errors."""

    def __init__(self, operation: str, **context):
        """
        Initialize error context.

        Args:
            operation: Name of the operation
            **context: Additional context
        """
        self.operation = operation
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, Exception):
            # Enrich the exception with context
            if hasattr(exc_val, "operation"):
                exc_val.operation = self.operation
            if hasattr(exc_val, "context"):
                exc_val.context.update(self.context)
        return False  # Does not suppress the exception


def create_validation_error(
    message: str,
    field_name: str,
    field_value: Any = None,
    suggestions: Optional[list] = None,
) -> ValidationError:
    """
    Create a validation error with suggestions.

    Args:
        message: Error message
        field_name: Field name
        field_value: Field value
        suggestions: Suggestions to correct the error

    Returns:
        Configured ValidationError
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
    Format an error for user display.

    Args:
        error: Exception to format

    Returns:
        Formatted message for the user
    """
    if hasattr(error, "error_code") and hasattr(error, "context"):
        # Domotix error with context
        if (
            hasattr(error.context, "user_data")
            and "suggestions" in error.context.user_data
        ):
            suggestions = error.context.user_data["suggestions"]
            return f"{str(error)}\\n💡 Suggestions: {', '.join(suggestions)}"

    # Standard error
    return str(error)
