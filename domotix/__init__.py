"""
Domotix - Modern Home Automation System

This package provides the main components for managing home automation devices.
It exposes the most important classes for easy use.

Exposed Classes:
    Device, Light, Shutter, Sensor: Device models
    Command, TurnOnCommand, ...: Command Pattern
    HomeAutomationController, StateManager: Core components
    DeviceType, ...: Enumerations
    DomotixError, DeviceNotFoundError, ...: Exceptions

Example:
    >>> import domotix
    >>>
    >>> controller = domotix.HomeAutomationController()
    >>> light = domotix.Light("My Light", "Living Room")
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
from .controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from .core import HomeAutomationController, SingletonMeta, StateManager
from .globals import (
    CommandExecutionError,
    CommandType,
    DeviceNotFoundError,
    DeviceState,
    DeviceType,
    DomotixError,
    InvalidDeviceTypeError,
)
from .models import Device, Light, Sensor, Shutter

# Export of public symbols
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
    # Controllers
    "DeviceController",
    "LightController",
    "ShutterController",
    "SensorController",
    # Core
    "HomeAutomationController",
    "StateManager",
    "SingletonMeta",
    # Globals
    "DeviceType",
    "DeviceState",
    "CommandType",
    "DomotixError",
    "DeviceNotFoundError",
    "InvalidDeviceTypeError",
    "CommandExecutionError",
]

__version__ = "0.1.0"
