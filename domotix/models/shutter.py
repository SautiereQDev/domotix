"""
Module du modèle Shutter pour les volets et stores.

Ce module contient la classe Shutter qui représente un volet ou store
dans le système domotique. Elle hérite de Device et ajoute des fonctionnalités
spécifiques aux volets (ouverture, fermeture, position).

Classes:
    Shutter: Modèle pour les volets et stores

Example:
    >>> from domotix.models import Shutter
    >>> volet = Shutter("Volet salon")
    >>> volet.open()
    >>> print(volet.get_status())
    OPEN
"""

from .device import Device


class Shutter(Device):
    """
    Modèle pour les volets et stores.

    Cette classe représente tous types de volets et stores
    (volets roulants, stores, persiennes, etc.) avec des fonctionnalités
    d'ouverture et de fermeture.

    Attributes:
        is_open (bool): État d'ouverture du volet (True=ouvert, False=fermé)
        name (str): Nom descriptif hérité de Device
        id (str): Identifiant unique hérité de Device

    Example:
        >>> volet = Shutter("Volet chambre")
        >>> volet.open()
        >>> assert volet.is_open == True
        >>> volet.close()
        >>> assert volet.is_open == False
    """

    def __init__(self, name: str) -> None:
        """
        Initialise un nouveau volet.

        Args:
            name: Nom descriptif du volet (ex: "Volet salon", "Store cuisine")
        """
        super().__init__(name)
        self.position: int = 0  # Position en pourcentage (0=fermé, 100=ouvert)

    @property
    def is_open(self) -> bool:
        """Vérifie si le volet est considéré comme ouvert (position > 0)."""
        return self.position > 0

    def get_state(self) -> dict:
        """
        Renvoie l'état actuel du volet.

        Returns:
            dict: État actuel du volet avec position et statut
        """
        return {
            "position": self.position,
            "is_open": self.is_open,
            "status": self.get_status(),
        }

    def update_state(self, new_state: dict) -> bool:
        """
        Met à jour l'état du volet.

        Args:
            new_state: Dictionnaire contenant le nouvel état

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            if "position" in new_state:
                self.set_position(new_state["position"])
            return True
        except (ValueError, TypeError):
            return False

    def open(self) -> None:
        """
        Ouvre complètement le volet.

        Example:
            >>> volet = Shutter("Test")
            >>> volet.open()
            >>> assert volet.position == 100
        """
        self.position = 100

    def close(self) -> None:
        """
        Ferme complètement le volet.

        Example:
            >>> volet = Shutter("Test")
            >>> volet.close()
            >>> assert volet.position == 0
        """
        self.position = 0

    def set_position(self, position: int) -> None:
        """
        Définit la position du volet.

        Args:
            position: Position en pourcentage (0-100)

        Raises:
            ValueError: Si la position n'est pas entre 0 et 100
        """
        if not 0 <= position <= 100:
            raise ValueError("La position doit être entre 0 et 100")
        self.position = position

    def get_status(self) -> str:
        """
        Renvoie le statut textuel du volet.

        Returns:
            str: "OPEN", "CLOSED" ou "PARTIAL"
        """
        if self.position == 0:
            return "CLOSED"
        elif self.position == 100:
            return "OPEN"
        else:
            return "PARTIAL"

    def toggle(self) -> None:
        """
        Bascule l'état du volet (ouvert <-> fermé).

        Si le volet est ouvert, le ferme. S'il est fermé, l'ouvre.

        Example:
            >>> volet = Shutter("Test")
            >>> volet.toggle()  # Fermé -> Ouvert
            >>> assert volet.is_open == True
            >>> volet.toggle()  # Ouvert -> Fermé
            >>> assert volet.is_open == False
        """
        if self.is_open:
            self.close()
        else:
            self.open()
