"""
Module des éléments globaux du système domotique.

Ce module expose toutes les énumérations et exceptions personnalisées
utilisées dans le système.

Exposed Enums:
    DeviceType, DeviceState, CommandType

Exposed Exceptions:
    DomotixError, DeviceNotFoundError, InvalidDeviceTypeError,
    CommandExecutionError, ErrorCode, ErrorContext, ValidationError,
    DeviceError, RepositoryError, ControllerError
"""

# Module globals - Éléments globaux du système
from .enums import CommandType, DeviceState, DeviceType
from .exceptions import (
    CommandExecutionError,
    ControllerError,
    DeviceError,
    DeviceNotFoundError,
    DomotixError,
    ErrorCode,
    ErrorContext,
    InvalidDeviceTypeError,
    RepositoryError,
    ValidationError,
)

__all__ = [
    # Enums
    "DeviceType",
    "DeviceState",
    "CommandType",
    # Exceptions
    "DomotixError",
    "DeviceNotFoundError",
    "InvalidDeviceTypeError",
    "CommandExecutionError",
    # Nouvelles exceptions du système d'error handling
    "ErrorCode",
    "ErrorContext",
    "ValidationError",
    "DeviceError",
    "RepositoryError",
    "ControllerError",
]
