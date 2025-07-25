"""
Contrôleur pour la gestion des dispositifs d'éclairage.

Ce module contient le LightController qui coordonne les opérations
sur les dispositifs d'éclairage en utilisant le pattern Repository
pour la persistance des données.

Classes:
    LightController: Contrôleur pour les lampes et dispositifs d'éclairage
"""

from typing import List, Optional

from domotix.models.light import Light
from domotix.repositories.device_repository import DeviceRepository


class LightController:
    """
    Contrôleur pour la gestion des dispositifs d'éclairage.

    Ce contrôleur utilise l'injection de dépendance pour recevoir
    un repository et ne dépend pas d'un singleton pour la persistance.

    Attributes:
        _repository: Repository pour la persistance des données
    """

    def __init__(self, light_repository: DeviceRepository):
        """
        Initialise le contrôleur avec un repository.

        Args:
            light_repository: Repository pour la persistance des données de lampes
        """
        self._repository = light_repository

    def create_light(self, name: str, location: Optional[str] = None) -> str:
        """
        Crée une nouvelle lampe.

        Args:
            name: Nom de la lampe
            location: Emplacement optionnel

        Returns:
            str: ID de la lampe créée
        """
        light = Light(name=name, location=location)
        saved_light = self._repository.save(light)
        return str(saved_light.id)

    def get_light(self, light_id: str) -> Optional[Light]:
        """
        Récupère une lampe par son ID.

        Args:
            light_id: ID de la lampe

        Returns:
            Optional[Light]: La lampe ou None si non trouvée
        """
        device = self._repository.find_by_id(light_id)
        if device and isinstance(device, Light):
            return device
        return None

    def get_all_lights(self) -> List[Light]:
        """
        Récupère toutes les lampes.

        Returns:
            List[Light]: Liste de toutes les lampes
        """
        devices = self._repository.find_all()
        return [device for device in devices if isinstance(device, Light)]

    def turn_on(self, light_id: str) -> bool:
        """
        Allume une lampe.

        Args:
            light_id: ID de la lampe

        Returns:
            bool: True si l'opération a réussi
        """
        light = self.get_light(light_id)
        if light:
            light.turn_on()
            return self._repository.update(light)
        return False

    def turn_off(self, light_id: str) -> bool:
        """
        Éteint une lampe.

        Args:
            light_id: ID de la lampe

        Returns:
            bool: True si l'opération a réussi
        """
        light = self.get_light(light_id)
        if light:
            light.turn_off()
            return self._repository.update(light)
        return False

    def toggle(self, light_id: str) -> bool:
        """
        Bascule l'état d'une lampe.

        Args:
            light_id: ID de la lampe

        Returns:
            bool: True si l'opération a réussi
        """
        light = self.get_light(light_id)
        if light:
            light.toggle()
            return self._repository.update(light)
        return False

    def delete_light(self, light_id: str) -> bool:
        """
        Supprime une lampe.

        Args:
            light_id: ID de la lampe

        Returns:
            bool: True si la suppression a réussi
        """
        return self._repository.delete(light_id)
