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

import math
from typing import Optional, Union

from ..globals.enums import DeviceType
from ..globals.exceptions import ErrorCode, ErrorContext, ValidationError
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
            ValidationError: Si la valeur n'est pas numérique ou n'est pas valide

        Example:
            >>> capteur = Sensor("Test")
            >>> capteur.update_value(42.7)
            >>> assert capteur.value == 42.7
            >>> capteur.update_value("invalid")  # Lève ValidationError
        """
        if not isinstance(value, (int, float)):
            context = ErrorContext(
                module=__name__,
                function="update_value",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "value_type": type(value).__name__,
                    "value": str(value),
                    "expected_types": ["int", "float"],
                },
            )
            raise ValidationError(
                message=(
                    f"La valeur du capteur '{self.name}' doit être numérique, "
                    f"reçu: {type(value).__name__}"
                ),
                error_code=ErrorCode.VALIDATION_INVALID_TYPE,
                context=context,
            )

        # Validation des valeurs spéciales
        if math.isnan(value):  # NaN check
            context = ErrorContext(
                module=__name__,
                function="update_value",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "value": str(value),
                    "issue": "NaN_value",
                },
            )
            raise ValidationError(
                message=f"Valeur invalide (NaN) pour le capteur '{self.name}'",
                error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
                context=context,
            )

        # Validation des infinis
        if not (-float("inf") < value < float("inf")):
            context = ErrorContext(
                module=__name__,
                function="update_value",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "value": str(value),
                    "issue": "infinite_value",
                },
            )
            raise ValidationError(
                message=f"Valeur infinie non autorisée pour le capteur '{self.name}'",
                error_code=ErrorCode.VALIDATION_OUT_OF_RANGE,
                context=context,
            )

        # Assignation de la valeur après validation
        self.value = value

    def validate_range(self, min_value: float, max_value: float) -> None:
        """
        Valide que la valeur actuelle est dans la plage spécifiée.

        Args:
            min_value: Valeur minimale autorisée
            max_value: Valeur maximale autorisée

        Raises:
            ValidationError: Si la valeur est hors de la plage spécifiée

        Example:
            >>> capteur = Sensor("Thermomètre")
            >>> capteur.update_value(25.0)
            >>> capteur.validate_range(-50, 100)  # OK
            >>> capteur.validate_range(30, 40)    # Lève ValidationError
        """
        if self.value is None:
            context = ErrorContext(
                module=__name__,
                function="validate_range",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "min_value": min_value,
                    "max_value": max_value,
                },
            )
            raise ValidationError(
                message=(
                    f"Impossible de valider la plage pour '{self.name}': "
                    "aucune valeur définie"
                ),
                error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
                context=context,
            )

        if not (min_value <= self.value <= max_value):
            context = ErrorContext(
                module=__name__,
                function="validate_range",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "current_value": self.value,
                    "min_value": min_value,
                    "max_value": max_value,
                },
            )
            raise ValidationError(
                message=(
                    f"Valeur {self.value} du capteur '{self.name}' "
                    f"hors de la plage [{min_value}, {max_value}]"
                ),
                error_code=ErrorCode.VALIDATION_OUT_OF_RANGE,
                context=context,
            )

    def is_value_valid(self) -> bool:
        """
        Vérifie si la valeur actuelle est valide.

        Returns:
            bool: True si la valeur est définie et valide, False sinon

        Example:
            >>> capteur = Sensor("Test")
            >>> capteur.is_value_valid()
            False
            >>> capteur.update_value(42.0)
            >>> capteur.is_value_valid()
            True
        """
        return (
            self.value is not None
            and isinstance(self.value, (int, float))
            and self.value == self.value  # NaN check
            and -float("inf") < self.value < float("inf")  # Infinity check
        )

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

    def reset_value(self) -> None:
        """
        Alias pour reset() - remet le capteur à zéro.

        Cette méthode est un alias de reset() pour la compatibilité
        avec l'interface attendue par les contrôleurs.

        Example:
            >>> capteur = Sensor("Test")
            >>> capteur.update_value(50)
            >>> capteur.reset_value()
            >>> assert capteur.value is None
        """
        self.reset()
