"""
Module des modèles de dispositifs domotiques.

Ce module contient la classe abstraite Device qui sert de base pour tous les
dispositifs domotiques du système. Elle définit l'interface commune que tous
les dispositifs doivent implémenter.

Classes:
    Device: Classe abstraite de base pour tous les dispositifs domotiques.

Example:
    Cette classe ne peut pas être instanciée directement:

    >>> from domotix.models import Device
    >>> device = Device("Test")  # Lève TypeError

    Elle doit être héritée par des classes concrètes comme Light ou Shutter.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from domotix.globals.enums import DeviceType


class Device(ABC):
    """Classe abstraite de base pour tous les dispositifs domotiques.

    Cette classe définit l'interface commune que tous les dispositifs
    doivent implémenter pour fonctionner avec le système domotique.

    Attributes:
        id (str): Identifiant unique du dispositif.
        name (str): Nom convivial du dispositif.
        state (dict): État actuel du dispositif.
        location (Optional[str]): Emplacement du dispositif.
    """

    def __init__(self, name: str, type: DeviceType, location: Optional[str] = None):
        """Initialise un nouveau dispositif.

        Args:
            name (str): Nom convivial du dispositif.
            type (DeviceType): Type du dispositif.
            state (dict): État initial du dispositif.
            location (Optional[str], optional): Emplacement du dispositif.
            Par défaut None.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.device_type = type
        self.state: dict[str, Any] = {}
        self.location: Optional[str] = location

    def __str__(self) -> str:
        """Représentation sous forme de chaîne du dispositif.

        Returns:
            str: Représentation textuelle du dispositif.
        """
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Représentation technique du dispositif.

        Returns:
            str: Représentation technique détaillée du dispositif.
        """
        return (
            f"{self.__class__.__name__}(id={self.id}, name={self.name}, "
            f"location={self.location})"
        )

    @abstractmethod
    def get_state(self) -> dict:
        """Renvoie l'état actuel du dispositif.

        Cette méthode doit être implémentée par toutes les classes filles.

        Returns:
            dict: État actuel du dispositif.
        """
        pass

    @abstractmethod
    def update_state(self, new_state: dict) -> bool:
        """Met à jour l'état du dispositif.

        Cette méthode doit être implémentée par toutes les classes filles.

        Args:
            new_state (dict): Nouvel état à appliquer.

        Returns:
            bool: True si la mise à jour a réussi, False sinon.
        """
        pass
