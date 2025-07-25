"""
Package des repositories pour la persistance des données.

Ce package contient tous les repositories qui gèrent l'accès aux données
pour les différents types de dispositifs du système domotique.

Modules:
    device_repository: Repository générique pour tous les dispositifs
    light_repository: Repository spécialisé pour les lampes
    shutter_repository: Repository spécialisé pour les volets
    sensor_repository: Repository spécialisé pour les capteurs

Classes exportées:
    DeviceRepository: Repository générique
    LightRepository: Repository pour lampes
    ShutterRepository: Repository pour volets
    SensorRepository: Repository pour capteurs
"""

from .device_repository import DeviceRepository
from .light_repository import LightRepository
from .sensor_repository import SensorRepository
from .shutter_repository import ShutterRepository

__all__ = [
    "DeviceRepository",
    "LightRepository",
    "ShutterRepository",
    "SensorRepository",
]
