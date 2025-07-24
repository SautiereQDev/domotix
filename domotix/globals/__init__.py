"""
Module des éléments globaux du système domotique.

Ce module expose toutes les énumérations et exceptions personnalisées
utilisées dans le système.

Exposed Enums:
    DeviceType, HttpMethod, DeviceState, CommandType

Exposed Exceptions:
    DomotixError, DeviceNotFoundError, InvalidDeviceTypeError,
    CommandExecutionError
"""

# Module globals - Éléments globaux du système
from .enums import CommandType, DeviceState, DeviceType
from .exceptions import (
    CommandExecutionError,
    DeviceNotFoundError,
    DomotixError,
    InvalidDeviceTypeError,
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
]
