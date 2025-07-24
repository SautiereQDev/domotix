"""
Domotix - Système de domotique moderne

Ce package fournit les composants principaux pour gérer les dispositifs domotiques.
Il expose les classes les plus importantes pour une utilisation facile.

Exposed Classes:
    Device, Light, Shutter, Sensor: Modèles de dispositifs
    Command, TurnOnCommand, ...: Pattern Command
    HomeAutomationController, StateManager: Composants core
    DeviceType, HttpMethod, ...: Énumérations
    DomotixError, DeviceNotFoundError, ...: Exceptions

Example:
    >>> import domotix
    >>>
    >>> controller = domotix.HomeAutomationController()
    >>> light = domotix.Light("Ma lampe")
    >>> device_id = controller.register_device(light)
    >>> controller.turn_on(device_id)
"""

from .commands import (
    CloseShutterCommand,
    Command,
    OpenShutterCommand,
    TurnOffCommand,
    TurnOnCommand,
)
from .core import HomeAutomationController, SingletonMeta, StateManager
from .globals import (
    CommandExecutionError,
    CommandType,
    DeviceNotFoundError,
    DeviceState,
    DeviceType,
    DomotixError,
    HttpMethod,
    InvalidDeviceTypeError,
)
from .models import Device, Light, Sensor, Shutter

# Export des symboles publics
__all__ = [
    # Models
    "Device",
    "Light",
    "Shutter",
    "Sensor",
    # Commands
    "Command",
    "TurnOnCommand",
    "TurnOffCommand",
    "OpenShutterCommand",
    "CloseShutterCommand",
    # Core
    "HomeAutomationController",
    "StateManager",
    "SingletonMeta",
    # Globals
    "DeviceType",
    "HttpMethod",
    "DeviceState",
    "CommandType",
    "DomotixError",
    "DeviceNotFoundError",
    "InvalidDeviceTypeError",
    "CommandExecutionError",
]

__version__ = "0.1.0"
