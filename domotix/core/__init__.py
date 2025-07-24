"""
Module des composants principaux du système domotique.

Ce module expose les classes principales qui orchestrent le fonctionnement
du système domotique, comme le controller et le gestionnaire d'état.

Exposed Classes:
    HomeAutomationController: Point d'entrée pour interagir avec le système
    StateManager: Gestionnaire d'état singleton pour les dispositifs
    SingletonMeta: Métaclasse pour créer des singletons thread-safe

Example:
    >>> from domotix.core import HomeAutomationController, StateManager
    >>> controller = HomeAutomationController()
    >>> state_manager = StateManager()
"""

# Module core - Composants principaux du système domotique
from .controller import HomeAutomationController
from .singleton import SingletonMeta
from .state_manager import StateManager

__all__ = ["HomeAutomationController", "StateManager", "SingletonMeta"]
