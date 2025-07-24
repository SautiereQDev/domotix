"""
Module du modèle Sensor pour les capteurs et dispositifs de mesure.

Ce module contient la classe Sensor qui représente un capteur ou dispositif
de mesure dans le système domotique. Elle hérite de Device et ajoute des
fonctionnalités spécifiques à la collecte et stockage de valeurs.

Classes:
    Sensor: Modèle pour les capteurs (température, humidité, luminosité, etc.)

Example:
    >>> from domotix.models import Sensor
    >>> capteur = Sensor("Capteur température salon", "Salon")
    >>> capteur.update_value(22.5)
    >>> print(capteur.value)
    22.5
    >>> print(capteur.get_status())
    VALUE_22.5
"""

from typing import Optional, Union

from ..globals.enums import DeviceType
from .device import Device


class Sensor(Device):
    """
    Modèle pour les capteurs et dispositifs de mesure.

    Cette classe représente tous types de capteurs (température, humidité,
    luminosité, mouvement, etc.) qui collectent et stockent des valeurs
    numériques dans le système domotique.

    Attributes:
        value (Optional[Union[int, float]]): Valeur actuelle du capteur
        name (str): Nom descriptif hérité de Device
        id (str): Identifiant unique hérité de Device

    Example:
        >>> capteur = Sensor("Thermomètre extérieur", "Jardin")
        >>> capteur.update_value(-5.2)
        >>> assert capteur.value == -5.2
        >>> print(capteur.get_status())
        VALUE_-5.2
    """

    def __init__(self, name: str, location: Optional[str] = None) -> None:
        """
        Initialise un nouveau capteur.

        Args:
            name: Nom descriptif du capteur (ex: "Capteur température salon",
                 "Détecteur mouvement entrée", "Luxmètre jardin")
            location: Emplacement du capteur (ex: "Salon", "Entrée", "Jardin")
        """
        super().__init__(name, DeviceType.SENSOR, location)
        self.value: Optional[Union[int, float]] = None  # Aucune valeur initialement

    def update_value(self, value: Union[int, float]) -> None:
        """
        Met à jour la valeur du capteur.

        Args:
            value: Nouvelle valeur numérique du capteur
                  (température en °C, humidité en %, luminosité en lux, etc.)

        Raises:
            TypeError: Si la valeur n'est pas numérique (int ou float)

        Example:
            >>> capteur = Sensor("Test")
            >>> capteur.update_value(42.7)
            >>> assert capteur.value == 42.7
            >>> capteur.update_value("invalid")  # Lève TypeError
        """
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"La valeur doit être numérique, " f"reçu: {type(value).__name__}"
            )
        self.value = value

    def get_status(self) -> str:
        """
        Retourne l'état actuel du capteur.

        Returns:
            str: "VALUE_X" où X est la valeur actuelle du capteur
                "NO_VALUE" si aucune valeur n'a été définie

        Example:
            >>> capteur = Sensor("Test")
            >>> print(capteur.get_status())
            NO_VALUE
            >>> capteur.update_value(23.4)
            >>> print(capteur.get_status())
            VALUE_23.4
        """
        return f"VALUE_{self.value}" if self.value is not None else "NO_VALUE"

    def get_state(self) -> dict:
        """
        Retourne l'état actuel du capteur sous forme de dictionnaire.

        Returns:
            dict: Dictionnaire contenant l'état complet du capteur
                 avec les clés 'value' et 'has_value'

        Example:
            >>> capteur = Sensor("Test")
            >>> print(capteur.get_state())
            {'value': None, 'has_value': False}
            >>> capteur.update_value(25.3)
            >>> print(capteur.get_state())
            {'value': 25.3, 'has_value': True}
        """
        return {"value": self.value, "has_value": self.value is not None}

    def update_state(self, new_state: dict) -> bool:
        """
        Met à jour l'état du capteur à partir d'un dictionnaire.

        Args:
            new_state: Dictionnaire contenant le nouvel état
                      doit contenir la clé 'value'

        Returns:
            bool: True si la mise à jour a réussi, False sinon

        Example:
            >>> capteur = Sensor("Test")
            >>> capteur.update_state({'value': 30.5})
            True
            >>> print(capteur.value)
            30.5
            >>> capteur.update_state({'invalid': 'data'})
            False
        """
        try:
            if "value" in new_state:
                if new_state["value"] is None:
                    self.value = None
                    return True
                elif isinstance(new_state["value"], (int, float)):
                    self.value = new_state["value"]
                    return True
                else:
                    return False
            return False
        except Exception:
            return False

    def has_value(self) -> bool:
        """
        Vérifie si le capteur a une valeur définie.

        Returns:
            bool: True si une valeur a été définie, False sinon

        Example:
            >>> capteur = Sensor("Test")
            >>> print(capteur.has_value())
            False
            >>> capteur.update_value(0)
            >>> print(capteur.has_value())
            True
        """
        return self.value is not None

    def reset(self) -> None:
        """
        Remet le capteur à zéro (supprime la valeur actuelle).

        Utile pour réinitialiser un capteur défaillant ou pour
        les capteurs à événements discrets.

        Example:
            >>> capteur = Sensor("Test")
            >>> capteur.update_value(100)
            >>> capteur.reset()
            >>> assert capteur.value is None
        """
        self.value = None
