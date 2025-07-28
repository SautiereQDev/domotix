"""
Global enumerations module for the home automation system.

This module contains all enumerations used in the system
to standardize types, states, and commands.

Enums:
    DeviceType: Device types (LIGHT, SHUTTER, SENSOR)
    HttpMethod: HTTP methods (GET, POST, PUT, DELETE, PATCH)
    DeviceState: Device states (ON, OFF, OPENING, CLOSING, STOPPED)
    CommandType: Command types (TURN_ON, TURN_OFF, OPEN, CLOSE, STOP)
"""

from enum import Enum


class DeviceType(Enum):
    """Types de dispositifs supportés par le système."""

    SHUTTER = "SHUTTER"
    SENSOR = "SENSOR"
    LIGHT = "LIGHT"


class HttpMethod(Enum):
    """Méthodes HTTP supportées."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class DeviceState(Enum):
    """États possibles des dispositifs."""

    ON = "ON"
    OFF = "OFF"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    STOPPED = "STOPPED"


class CommandType(Enum):
    """Types de commandes exécutables."""

    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    STOP = "STOP"
