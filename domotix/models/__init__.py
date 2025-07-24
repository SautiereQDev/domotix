"""
Module des modèles de dispositifs domotiques.

Ce module expose toutes les classes de modèles de dispositifs disponibles
dans le système domotique. Il sert de point d'entrée unique pour importer
les modèles depuis d'autres parties de l'application.

Exposed Classes:
    Device: Classe abstraite de base pour tous les dispositifs
    Light: Modèle pour les dispositifs d'éclairage
    Shutter: Modèle pour les volets et stores
    Sensor: Modèle pour les capteurs et dispositifs de mesure

Example:
    >>> from domotix.models import Light, Shutter
    >>> lampe = Light("Lampe salon")
    >>> volet = Shutter("Volet chambre")
"""

# Imports pour les modèles
from .device import Device
from .light import Light
from .sensor import Sensor
from .shutter import Shutter

# __all__ définit les symboles publics du module
# Seuls ces noms seront importés avec 'from domotix.models import *'
__all__ = ["Device", "Light", "Shutter", "Sensor"]
