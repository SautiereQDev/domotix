"""
Light model module for lighting devices.

This module contains the Light class, which represents a lighting device
in the home automation system. It inherits from Device and adds features
specific to lighting.

Classes:
    Light: Model for lighting devices (lamps, spots, etc.)

Example:
    >>> from domotix.models import Light
    >>> lamp = Light("Living Room Lamp", "Living Room")
    >>> print(lamp.is_on)
    False
    >>> lamp.turn_on()
    >>> print(lamp.get_status())
    ON
"""

from typing import Literal, Optional

from ..globals.enums import DeviceType
from .device import Device


class Light(Device):
    """
    Modèle pour les dispositifs d'éclairage.

    Cette classe représente tous types de dispositifs d'éclairage
    (lampes, spots, néons, etc.) avec des fonctionnalités de base
    d'allumage et d'extinction.

    Attributes:
        is_on (bool): État d'allumage de la lampe (True=allumée, False=éteinte)
        name (str): Nom descriptif hérité de Device
        id (str): Identifiant unique hérité de Device

    Example:
        >>> lampe = Light("Lampe chambre", "Chambre")
        >>> lampe.turn_on()
        >>> assert lampe.is_on == True
        >>> lampe.turn_off()
        >>> assert lampe.is_on == False
    """

    def __init__(self, name: str, location: Optional[str] = None) -> None:
        """
        Initialise une nouvelle lampe.

        Args:
            name: Nom descriptif de la lampe (ex: "Lampe salon", "Spot cuisine")
            location: Emplacement de la lampe (ex: "Salon", "Cuisine")
        """
        super().__init__(name, DeviceType.LIGHT, location)
        self.is_on: bool = False  # État initial: éteinte

    def get_state(self) -> dict:
        """
        Renvoie l'état actuel de la lampe.

        Implémentation de la méthode abstraite héritée de Device.

        Returns:
            dict: État actuel de la lampe avec les clés:
                 - 'is_on': booléen indiquant si la lampe est allumée
                 - 'status': statut textuel de la lampe

        Example:
            >>> lampe = Light("Test")
            >>> state = lampe.get_state()
            >>> print(state['is_on'])
            False
            >>> lampe.turn_on()
            >>> state = lampe.get_state()
            >>> print(state['status'])
            ON
        """
        return {"is_on": self.is_on, "status": self.get_status()}

    def update_state(self, new_state: dict) -> bool:
        """
        Met à jour l'état de la lampe.

        Implémentation de la méthode abstraite héritée de Device.

        Args:
            new_state: Dictionnaire contenant le nouvel état.
                      Doit contenir la clé 'is_on' avec une valeur booléenne.

        Returns:
            bool: True si la mise à jour a réussi, False sinon.

        Example:
            >>> lampe = Light("Test")
            >>> success = lampe.update_state({'is_on': True})
            >>> print(success)
            True
            >>> print(lampe.is_on)
            True
        """
        try:
            if "is_on" not in new_state:
                return False

            new_is_on = new_state["is_on"]

            if isinstance(new_is_on, bool):
                self.is_on = new_is_on
                return True

            return False

        except Exception:
            return False

    def turn_on(self) -> None:
        """
        Allume la lampe.

        Change l'état interne à True. Cette méthode est idempotente :
        appeler turn_on() sur une lampe déjà allumée n'a pas d'effet.

        Example:
            >>> lampe = Light("Test")
            >>> lampe.turn_on()
            >>> assert lampe.is_on == True
        """
        self.is_on = True

    def turn_off(self) -> None:
        """
        Éteint la lampe.

        Change l'état interne à False. Cette méthode est idempotente :
        appeler turn_off() sur une lampe déjà éteinte n'a pas d'effet.

        Example:
            >>> lampe = Light("Test")
            >>> lampe.turn_on()
            >>> lampe.turn_off()
            >>> assert lampe.is_on == False
        """
        self.is_on = False

    def get_status(self) -> Literal["ON", "OFF"]:
        """
        Retourne l'état actuel de la lampe.

        Returns:
            "ON" si la lampe est allumée, "OFF" si elle est éteinte

        Example:
            >>> lampe = Light("Test")
            >>> print(lampe.get_status())
            OFF
            >>> lampe.turn_on()
            >>> print(lampe.get_status())
            ON
        """
        return "ON" if self.is_on else "OFF"

    def toggle(self) -> None:
        """
        Bascule l'état de la lampe (allumée <-> éteinte).

        Si la lampe est allumée, l'éteint. Si elle est éteinte, l'allume.

        Example:
            >>> lampe = Light("Test")
            >>> lampe.toggle()  # Éteinte -> Allumée
            >>> assert lampe.is_on == True
            >>> lampe.toggle()  # Allumée -> Éteinte
            >>> assert lampe.is_on == False
        """
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()
