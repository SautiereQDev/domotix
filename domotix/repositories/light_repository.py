"""
Specialized repository for managing lighting devices.

This module contains the LightRepository, which inherits from DeviceRepository
and adds specialized methods for lights.

Classes:
    LightRepository: Specialized repository for lights
"""

from typing import List

from sqlalchemy.orm import Session

from domotix.models.base_model import DeviceModel
from domotix.models.light import Light

from .device_repository import DeviceRepository


class LightRepository(DeviceRepository):
    """
    Repository spécialisé pour la gestion des dispositifs d'éclairage.

    Hérite du DeviceRepository et ajoute des méthodes spécialisées
    pour les opérations sur les lampes.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository avec une session de base de données.

        Args:
            session: Session SQLAlchemy
        """
        super().__init__(session)

    def find_lights_by_location(self, location: str) -> List[Light]:
        """
        Trouve toutes les lampes dans un emplacement donné.

        Args:
            location: Emplacement à rechercher

        Returns:
            List[Light]: Liste des lampes dans cet emplacement
        """
        from domotix.globals.enums import DeviceType

        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.LIGHT.value,
                DeviceModel.location == location,
            )
            .all()
        )

        lights = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Light):
                lights.append(entity)
        return lights

    def find_on_lights(self) -> List[Light]:
        """
        Trouve toutes les lampes allumées.

        Note: Cette méthode nécessiterait une adaptation du modèle
        pour stocker l'état détaillé des lampes.

        Returns:
            List[Light]: Liste des lampes allumées
        """
        from domotix.globals.enums import DeviceType

        # Pour l'instant, on retourne toutes les lampes
        # TODO: Implémenter la logique pour filtrer les lampes allumées
        models = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.LIGHT.value)
            .all()
        )

        lights = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Light):
                lights.append(entity)
        return lights

    def find_off_lights(self) -> List[Light]:
        """
        Trouve toutes les lampes éteintes.

        Note: Cette méthode nécessiterait une adaptation du modèle
        pour stocker l'état détaillé des lampes.

        Returns:
            List[Light]: Liste des lampes éteintes
        """
        from domotix.globals.enums import DeviceType

        # Pour l'instant, on retourne toutes les lampes
        # TODO: Implémenter la logique pour filtrer les lampes éteintes
        models = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.LIGHT.value)
            .all()
        )

        lights = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Light):
                lights.append(entity)
        return lights

    def count_lights(self) -> int:
        """
        Compte le nombre total de lampes.

        Returns:
            int: Nombre de lampes
        """
        from domotix.globals.enums import DeviceType

        count: int = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.LIGHT.value)
            .count()
        )
        return count

    def search_lights_by_name(self, name_pattern: str) -> List[Light]:
        """
        Recherche des lampes par nom.

        Args:
            name_pattern: Motif de recherche dans le nom

        Returns:
            List[Light]: Liste des lampes correspondantes
        """
        from domotix.globals.enums import DeviceType

        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.LIGHT.value,
                DeviceModel.name.ilike(f"%{name_pattern}%"),
            )
            .all()
        )

        lights = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Light):
                lights.append(entity)
        return lights
