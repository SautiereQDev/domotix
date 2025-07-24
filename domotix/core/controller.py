"""
Module du controller principal du système domotique.

Ce module contient la classe HomeAutomationController qui sert de point
d'entrée principal pour interagir avec le système domotique. Elle utilise
le StateManager pour gérer les dispositifs.

Classes:
    HomeAutomationController: Controller principal pour le système domotique

Example:
    >>> from domotix.core import HomeAutomationController
    >>> from domotix.models import Light
    >>>
    >>> controller = HomeAutomationController()
    >>> light = Light("Lampe salon")
    >>> device_id = controller.register_device(light)
    >>> controller.turn_on(device_id)
    >>> print(controller.get_status(device_id))
    ON
"""

from typing import Dict, Optional

from ..models import Device
from .state_manager import StateManager


class HomeAutomationController:
    """
    Controller principal pour le système domotique.

    Cette classe sert de façade pour interagir avec le système domotique.
    Elle utilise le StateManager pour gérer l'état des dispositifs.

    Attributes:
        _state_manager: Instance du StateManager singleton

    Example:
        >>> controller = HomeAutomationController()
        >>> light = Light("Lampe test")
        >>> device_id = controller.register_device(light)
        >>> controller.turn_on(device_id)
        >>> assert controller.get_status(device_id) == "ON"
    """

    def __init__(self) -> None:
        """
        Initialise le controller.

        Récupère l'instance singleton du StateManager.
        """
        self._state_manager = StateManager()

    def turn_on(self, device_id: str) -> bool:
        """
        Allume un dispositif.

        Args:
            device_id: Identifiant du dispositif à allumer

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            device = self._state_manager.get_device(device_id)
            if hasattr(device, "turn_on"):
                device.turn_on()
                return True
            return False
        except KeyError:
            return False

    def turn_off(self, device_id: str) -> bool:
        """
        Éteint un dispositif.

        Args:
            device_id: Identifiant du dispositif à éteindre

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            device = self._state_manager.get_device(device_id)
            if hasattr(device, "turn_off"):
                device.turn_off()
                return True
            return False
        except KeyError:
            return False

    def get_status(self, device_id: str) -> Optional[str]:
        """
        Récupère le statut d'un dispositif.

        Args:
            device_id: Identifiant du dispositif

        Returns:
            Optional[str]: Statut du dispositif ou None si non trouvé
        """
        try:
            device = self._state_manager.get_device(device_id)
            state = device.get_state()
            # Convertir l'état en string pour l'affichage
            if hasattr(device, "is_on"):
                return "ON" if device.is_on else "OFF"
            elif hasattr(device, "position"):
                return f"Position: {device.position}%"
            else:
                return str(state)
        except KeyError:
            return None

    def register_device(self, device) -> str:
        """
        Enregistre un nouveau dispositif.

        Args:
            device: Instance de Device à enregistrer

        Returns:
            str: Identifiant unique du dispositif enregistré
        """
        return self._state_manager.register_device(device)

    def get_all_devices(self) -> Dict[str, Device]:
        """
        Récupère tous les dispositifs.

        Returns:
            Dict[str, Device]: Dictionnaire de tous les dispositifs
        """
        return self._state_manager.get_devices()

    def remove_device(self, device_id: str) -> bool:
        """
        Supprime un dispositif.

        Args:
            device_id: Identifiant du dispositif à supprimer

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        return self._state_manager.unregister_device(device_id)
