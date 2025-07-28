"""
Home automation device models module.

This module exposes all available device model classes
in the home automation system. It serves as a single entry point
for importing models from other parts of the application.

Exposed Classes:
    Device: Base abstract class for all devices
    Light: Model for lighting devices
    Shutter: Model for shutters and blinds
    Sensor: Model for sensors and measurement devices

Example:
    >>> from domotix.models import Light, Shutter
    >>> light = Light("Living room lamp")
    >>> shutter = Shutter("Bedroom shutter")
"""

from .base_model import DeviceModel

# Model imports
from .device import Device
from .light import Light
from .sensor import Sensor
from .shutter import Shutter

# __all__ définit les symboles publics du module
# Seuls ces noms seront importés avec 'from domotix.models import *'
__all__ = ["Device", "Light", "Shutter", "Sensor", "DeviceModel"]
