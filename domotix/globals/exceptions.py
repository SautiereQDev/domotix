"""
Custom exceptions module for the Domotix home automation system.

This module contains all custom exceptions with a modern architecture
following Python 3.12+ best practices:
- Structured exception hierarchy
- Standardized error codes
- Enriched context for debugging
- Exception chaining support

Exceptions:
    DomotixError: Base exception for all system errors
    DeviceError: Device-related errors
    RepositoryError: Persistence errors
    ValidationError: Validation errors
    ControllerError: Business logic errors
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
    Standardized error codes for the application.

    Uses structured codes to facilitate debugging
    and integration with external systems.
    """

    # Generic errors (1xxx)
    UNKNOWN_ERROR = "DMX-1000"
    INVALID_CONFIGURATION = "DMX-1001"
    INITIALIZATION_ERROR = "DMX-1002"

    # Device errors (2xxx)
    DEVICE_NOT_FOUND = "DMX-2000"
    DEVICE_INVALID_STATE = "DMX-2001"
    DEVICE_COMMUNICATION_ERROR = "DMX-2002"
    DEVICE_TIMEOUT = "DMX-2003"
    DEVICE_ALREADY_EXISTS = "DMX-2004"
    DEVICE_INVALID_TYPE = "DMX-2005"

    # Repository errors (3xxx)
    REPOSITORY_CONNECTION_ERROR = "DMX-3000"
    REPOSITORY_TRANSACTION_ERROR = "DMX-3001"
    REPOSITORY_CONSTRAINT_VIOLATION = "DMX-3002"
    REPOSITORY_DATA_CORRUPTION = "DMX-3003"

    # Validation errors (4xxx)
    VALIDATION_REQUIRED_FIELD = "DMX-4000"
    VALIDATION_INVALID_FORMAT = "DMX-4001"
    VALIDATION_OUT_OF_RANGE = "DMX-4002"
    VALIDATION_INVALID_TYPE = "DMX-4003"

    # Controller errors (5xxx)
    CONTROLLER_OPERATION_FAILED = "DMX-5000"
    CONTROLLER_DEPENDENCY_ERROR = "DMX-5001"
    CONTROLLER_STATE_ERROR = "DMX-5002"

    # Command errors (6xxx)
    COMMAND_EXECUTION_ERROR = "DMX-6000"
    COMMAND_INVALID_PARAMETER = "DMX-6001"


@dataclass(slots=True, frozen=True)
class ErrorContext:
    """
    Error context to enrich exceptions.

    Captures useful information for debugging
    and problem resolution.
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
        Creates a context from stack frame information.

        Args:
            frame_info: Stack frame information

        Returns:
            Initialized error context
        """
        return cls(
            module=frame_info.filename,
            function=frame_info.name,
            line_number=frame_info.lineno,
        )


class DomotixError(Exception):
    """
    Base exception for all Domotix application errors.

    Provides a common structure for error handling with:
    - Standardized error code
    - Enriched context
    - Exception chaining support
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Initializes the Domotix exception.

        Args:
            message: Human-readable error message
            error_code: Standardized error code
            context: Error context
            cause: Original exception (for chaining)
        """
        super().__init__(message)
        self.error_code = error_code
        self.context = context or ErrorContext()
        self.cause = cause

        # Automatic context enrichment
        if self.context.module is None:
            self._enrich_context_from_stack()

    def _enrich_context_from_stack(self) -> None:
        """Enriches the context with stack information."""
        tb = sys.exc_info()[2]
        if tb is None:
            # No active exception context, do nothing
            return
        stack = traceback.extract_tb(tb)
        if stack:
            # Take the last frame that is not in this module
            for frame in reversed(stack):
                if not frame.filename.endswith("exceptions.py"):
                    self.context = ErrorContext.from_frame(frame)
                    break

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the exception to a dictionary.

        Returns:
            Dictionary representation of the exception
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
        """String representation with error code."""
        return f"[{self.error_code.value}] {super().__str__()}"


# Modern specialized exceptions (replace old ones)
class DeviceError(DomotixError):
    """Device-related errors."""

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
    """Persistence and data access errors."""

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
    """Data validation errors."""

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
    """Business logic errors in controllers."""

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


# Exceptions compatible with the old system (to be migrated gradually)
class DeviceNotFoundError(DeviceError):
    """Raised when a requested device is not found."""

    def __init__(self, device_id: str):
        super().__init__(
            f"Device not found: {device_id}",
            device_id=device_id,
            error_code=ErrorCode.DEVICE_NOT_FOUND,
        )


class InvalidDeviceTypeError(DeviceError):
    """Raised when an invalid device type is used."""

    def __init__(self, device_type: str):
        super().__init__(
            f"Invalid device type: {device_type}",
            error_code=ErrorCode.DEVICE_INVALID_TYPE,
        )
        self.device_type = device_type


class CommandExecutionError(DomotixError):
    """Raised when command execution fails."""

    def __init__(self, command: str, reason: str = ""):
        message = f"Command execution failed: {command}"
        if reason:
            message += f" - {reason}"

        super().__init__(message, error_code=ErrorCode.COMMAND_EXECUTION_ERROR)
        self.command = command
        self.reason = reason


# Context manager for error handling
@contextmanager
def error_handler(
    logger_name: str | None = None, reraise: bool = True, default_return: Any = None
) -> Iterator[None]:
    """
    Context manager for automatic error handling.

    Args:
        logger_name: Logger name to use
        reraise: If True, re-raises the exception after logging
        default_return: Default value to return if no re-raise

    Yields:
        None

    Example:
        with error_handler(__name__):
            risky_operation()
    """
    try:
        # Import locally to avoid circular dependencies
        from domotix.core.logging_system import get_logger

        logger = get_logger(logger_name or __name__)
    except ImportError:
        # Fallback if modern logging system is not available
        import logging

        logger = logging.getLogger(logger_name or __name__)  # type: ignore[assignment]

    try:
        yield
    except DomotixError as e:
        # Log Domotix errors with full context
        if hasattr(logger, "error") and hasattr(e, "to_dict"):
            logger.error(
                f"Domotix Error: {e}",
                error_code=e.error_code.value,
                error_context=e.to_dict(),
            )
        else:
            logger.error(f"Domotix Error: {e}")

        if reraise:
            raise
        return default_return  # type: ignore[return-value, no-any-return]
    except Exception as e:
        # Convert external exceptions to DomotixError
        domotix_error = DomotixError(
            f"Unexpected error: {e}", error_code=ErrorCode.UNKNOWN_ERROR, cause=e
        )

        if hasattr(logger, "exception"):
            logger.exception(f"Unexpected error: {e}")
        else:
            logger.error(f"Unexpected error: {e}")

        if reraise:
            raise domotix_error from e
        return default_return  # type: ignore[return-value, no-any-return]


# Utility functions for creating exceptions
def device_not_found(device_id: str, additional_info: str = "") -> DeviceError:
    """
    Creates a DeviceError exception for device not found.

    Args:
        device_id: Device ID
        additional_info: Additional information

    Returns:
        Configured exception
    """
    message = f"Device '{device_id}' not found"
    if additional_info:
        message += f": {additional_info}"

    return DeviceError(
        message=message, device_id=device_id, error_code=ErrorCode.DEVICE_NOT_FOUND
    )


def validation_failed(
    field_name: str, field_value: Any, reason: str = ""
) -> ValidationError:
    """
    Creates a ValidationError exception for validation failure.

    Args:
        field_name: Field name
        field_value: Field value
        reason: Reason for failure

    Returns:
        Configured exception
    """
    message = f"Validation failed for field '{field_name}'"
    if reason:
        message += f": {reason}"

    return ValidationError(
        message=message,
        field_name=field_name,
        field_value=field_value,
        error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
    )
