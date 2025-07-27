"""
Repository spécialisé pour la gestion des volets et stores.

Ce module contient le ShutterRepository qui hérite du DeviceRepository
et ajoute des méthodes spécialisées pour les volets.

Classes:
    ShutterRepository: Repository spécialisé pour les volets
"""

from typing import List

from sqlalchemy.orm import Session

from domotix.models.base_model import DeviceModel
from domotix.models.shutter import Shutter

from .device_repository import DeviceRepository


class ShutterRepository(DeviceRepository):
    """
    Repository spécialisé pour la gestion des volets et stores.

    Hérite du DeviceRepository et ajoute des méthodes spécialisées
    pour les opérations sur les volets.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository avec une session de base de données.

        Args:
            session: Session SQLAlchemy
        """
        super().__init__(session)

    def find_shutters_by_location(self, location: str) -> List[Shutter]:
        """
        Trouve tous les volets dans un emplacement donné.

        Args:
            location: Emplacement à rechercher

        Returns:
            List[Shutter]: Liste des volets dans cet emplacement
        """
        from domotix.globals.enums import DeviceType

        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.SHUTTER.value,
                DeviceModel.location == location,
            )
            .all()
        )

        shutters = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Shutter):
                shutters.append(entity)
        return shutters

    def find_open_shutters(self) -> List[Shutter]:
        """
        Trouve tous les volets ouverts.

        Note: Cette méthode nécessiterait une adaptation du modèle
        pour stocker l'état détaillé des volets.

        Returns:
            List[Shutter]: Liste des volets ouverts
        """
        from domotix.globals.enums import DeviceType

        # Pour l'instant, on retourne tous les volets
        # TODO: Implémenter la logique pour filtrer les volets ouverts
        models = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.SHUTTER.value)
            .all()
        )

        shutters = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Shutter):
                shutters.append(entity)
        return shutters

    def find_closed_shutters(self) -> List[Shutter]:
        """
        Trouve tous les volets fermés.

        Note: Cette méthode nécessiterait une adaptation du modèle
        pour stocker l'état détaillé des volets.

        Returns:
            List[Shutter]: Liste des volets fermés
        """
        from domotix.globals.enums import DeviceType

        # Pour l'instant, on retourne tous les volets
        # TODO: Implémenter la logique pour filtrer les volets fermés
        models = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.SHUTTER.value)
            .all()
        )

        shutters = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Shutter):
                shutters.append(entity)
        return shutters

    def count_shutters(self) -> int:
        """
        Compte le nombre total de volets.

        Returns:
            int: Nombre de volets
        """
        from domotix.globals.enums import DeviceType

        count: int = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.SHUTTER.value)
            .count()
        )
        return count

    def search_shutters_by_name(self, name_pattern: str) -> List[Shutter]:
        """
        Recherche des volets par nom.

        Args:
            name_pattern: Motif de recherche dans le nom

        Returns:
            List[Shutter]: Liste des volets correspondants
        """
        from domotix.globals.enums import DeviceType

        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.SHUTTER.value,
                DeviceModel.name.ilike(f"%{name_pattern}%"),
            )
            .all()
        )

        shutters = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Shutter):
                shutters.append(entity)
        return shutters
