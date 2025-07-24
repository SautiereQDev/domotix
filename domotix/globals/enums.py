"""
Module des énumérations globales du système domotique.

Ce module contient toutes les énumérations utilisées dans le système
pour standardiser les types, états et commandes.

Enums:
    DeviceType: Types de dispositifs (LIGHT, SHUTTER, SENSOR)
    HttpMethod: Méthodes HTTP (GET, POST, PUT, DELETE, PATCH)
    DeviceState: États des dispositifs (ON, OFF, OPENING, CLOSING, STOPPED)
    CommandType: Types de commandes (TURN_ON, TURN_OFF, OPEN, CLOSE, STOP)
"""

from enum import Enum


class DeviceType(Enum):
    """Types de dispositifs supportés par le système."""

    SHUTTER = "SHUTTER"
    SENSOR = "SENSOR"
    LIGHT = "LIGHT"


class HttpMethod(Enum):
    """Méthodes HTTP standard."""

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
