"""
Contrôleur pour la gestion des volets et stores.

Ce module contient le ShutterController qui coordonne les opérations
sur les volets et stores en utilisant le pattern Repository
pour la persistance des données.

Classes:
    ShutterController: Contrôleur pour les volets et stores
"""

from typing import List, Optional

from domotix.models.shutter import Shutter
from domotix.repositories.device_repository import DeviceRepository


class ShutterController:
    """
    Contrôleur pour la gestion des volets et stores.

    Ce contrôleur utilise l'injection de dépendance pour recevoir
    un repository et ne dépend pas d'un singleton pour la persistance.

    Attributes:
        _repository: Repository pour la persistance des données
    """

    def __init__(self, shutter_repository: DeviceRepository):
        """
        Initialise le contrôleur avec un repository.

        Args:
            shutter_repository: Repository pour la persistance des données de volets
        """
        self._repository = shutter_repository

    def create_shutter(self, name: str, location: Optional[str] = None) -> str:
        """
        Crée un nouveau volet.

        Args:
            name: Nom du volet
            location: Emplacement optionnel

        Returns:
            str: ID du volet créé
        """
        shutter = Shutter(name=name, location=location)
        saved_shutter = self._repository.save(shutter)
        return str(saved_shutter.id)

    def get_shutter(self, shutter_id: str) -> Optional[Shutter]:
        """
        Récupère un volet par son ID.

        Args:
            shutter_id: ID du volet

        Returns:
            Optional[Shutter]: Le volet ou None si non trouvé
        """
        device = self._repository.find_by_id(shutter_id)
        if device and isinstance(device, Shutter):
            return device
        return None

    def get_all_shutters(self) -> List[Shutter]:
        """
        Récupère tous les volets.

        Returns:
            List[Shutter]: Liste de tous les volets
        """
        devices = self._repository.find_all()
        return [device for device in devices if isinstance(device, Shutter)]

    def open(self, shutter_id: str) -> bool:
        """
        Ouvre un volet.

        Args:
            shutter_id: ID du volet

        Returns:
            bool: True si l'opération a réussi
        """
        shutter = self.get_shutter(shutter_id)
        if shutter:
            shutter.open()
            return self._repository.update(shutter)
        return False

    def close(self, shutter_id: str) -> bool:
        """
        Ferme un volet.

        Args:
            shutter_id: ID du volet

        Returns:
            bool: True si l'opération a réussi
        """
        shutter = self.get_shutter(shutter_id)
        if shutter:
            shutter.close()
            return self._repository.update(shutter)
        return False

    def stop(self, shutter_id: str) -> bool:
        """
        Arrête le mouvement d'un volet.

        Args:
            shutter_id: ID du volet

        Returns:
            bool: True si l'opération a réussi
        """
        shutter = self.get_shutter(shutter_id)
        if shutter and hasattr(shutter, "stop"):
            shutter.stop()
            return self._repository.update(shutter)
        return False

    def set_position(self, shutter_id: str, position: int) -> bool:
        """
        Définit la position d'un volet.

        Args:
            shutter_id: ID du volet
            position: Position en pourcentage (0-100)

        Returns:
            bool: True si l'opération a réussi
        """
        shutter = self.get_shutter(shutter_id)
        if shutter and hasattr(shutter, "set_position"):
            shutter.set_position(position)
            return self._repository.update(shutter)
        return False

    def get_position(self, shutter_id: str) -> Optional[int]:
        """
        Récupère la position d'un volet.

        Args:
            shutter_id: ID du volet

        Returns:
            Optional[int]: Position en pourcentage ou None si non trouvé
        """
        shutter = self.get_shutter(shutter_id)
        if shutter and hasattr(shutter, "position"):
            return shutter.position
        return None

    def delete_shutter(self, shutter_id: str) -> bool:
        """
        Supprime un volet.

        Args:
            shutter_id: ID du volet

        Returns:
            bool: True si la suppression a réussi
        """
        return self._repository.delete(shutter_id)
