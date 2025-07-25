"""
Package des contrôleurs pour le système domotique.

Ce package contient tous les contrôleurs qui coordonnent les opérations
sur les différents types de dispositifs en utilisant le pattern Repository.

Modules:
    device_controller: Contrôleur générique pour tous les dispositifs
    light_controller: Contrôleur spécialisé pour les lampes
    shutter_controller: Contrôleur spécialisé pour les volets
    sensor_controller: Contrôleur spécialisé pour les capteurs

Classes exportées:
    DeviceController: Contrôleur générique
    LightController: Contrôleur pour lampes
    ShutterController: Contrôleur pour volets
    SensorController: Contrôleur pour capteurs
"""

from .device_controller import DeviceController
from .light_controller import LightController
from .sensor_controller import SensorController
from .shutter_controller import ShutterController

__all__ = [
    "DeviceController",
    "LightController",
    "ShutterController",
    "SensorController",
]
