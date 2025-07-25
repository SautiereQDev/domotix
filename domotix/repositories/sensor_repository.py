"""
Repository spécialisé pour la gestion des capteurs et dispositifs de mesure.

Ce module contient le SensorRepository qui hérite du DeviceRepository
et des méthodes spécialisées pour les capteurs.

Classes:
    SensorRepository: Repository spécialisé pour les capteurs
"""

from typing import List

from sqlalchemy.orm import Session

from domotix.models.persistence import DeviceModel
from domotix.models.sensor import Sensor

from .device_repository import DeviceRepository


class SensorRepository(DeviceRepository):
    """
    Repository spécialisé pour la gestion des capteurs et dispositifs de mesure.

    Hérite du DeviceRepository et ajoute des méthodes spécialisées
    pour les opérations sur les capteurs.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository avec une session de base de données.

        Args:
            session: Session SQLAlchemy
        """
        super().__init__(session)

    def find_sensors_by_location(self, location: str) -> List[Sensor]:
        """
        Trouve tous les capteurs dans un emplacement donné.

        Args:
            location: Emplacement à rechercher

        Returns:
            List[Sensor]: Liste des capteurs dans cet emplacement
        """
        from domotix.globals.enums import DeviceType

        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.SENSOR.value,
                DeviceModel.location == location,
            )
            .all()
        )

        sensors = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Sensor):
                sensors.append(entity)
        return sensors

    def find_active_sensors(self) -> List[Sensor]:
        """
        Trouve tous les capteurs actifs (avec des valeurs).

        Note: Cette méthode nécessiterait une adaptation du modèle
        pour stocker l'état détaillé des capteurs.

        Returns:
            List[Sensor]: Liste des capteurs actifs
        """
        from domotix.globals.enums import DeviceType

        # Pour l'instant, on retourne tous les capteurs
        # TODO: Implémenter la logique pour filtrer les capteurs actifs
        models = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.SENSOR.value)
            .all()
        )

        sensors = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Sensor):
                sensors.append(entity)
        return sensors

    def find_inactive_sensors(self) -> List[Sensor]:
        """
        Trouve tous les capteurs inactifs (sans valeurs).

        Note: Cette méthode nécessiterait une adaptation du modèle
        pour stocker l'état détaillé des capteurs.

        Returns:
            List[Sensor]: Liste des capteurs inactifs
        """

        # Pour l'instant, on retourne une liste vide
        # TODO: Implémenter la logique pour filtrer les capteurs inactifs
        return []

    def count_sensors(self) -> int:
        """
        Compte le nombre total de capteurs.

        Returns:
            int: Nombre de capteurs
        """
        from domotix.globals.enums import DeviceType

        count: int = (
            self.session.query(DeviceModel)
            .filter(DeviceModel.device_type == DeviceType.SENSOR.value)
            .count()
        )
        return count

    def search_sensors_by_name(self, name_pattern: str) -> List[Sensor]:
        """
        Recherche des capteurs par nom.

        Args:
            name_pattern: Motif de recherche dans le nom

        Returns:
            List[Sensor]: Liste des capteurs correspondants
        """
        from domotix.globals.enums import DeviceType

        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.SENSOR.value,
                DeviceModel.name.ilike(f"%{name_pattern}%"),
            )
            .all()
        )

        sensors = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Sensor):
                sensors.append(entity)
        return sensors

    def find_sensors_by_type(self, sensor_type: str) -> List[Sensor]:
        """
        Trouve tous les capteurs d'un type donné.

        Note: Cette méthode nécessiterait un champ additionnel
        pour stocker le type de capteur (température, humidité, etc.).

        Args:
            sensor_type: Type de capteur à rechercher

        Returns:
            List[Sensor]: Liste des capteurs de ce type
        """
        from domotix.globals.enums import DeviceType

        # Pour l'instant, on recherche dans le nom
        # TODO: Ajouter un champ sensor_type dans le modèle
        models = (
            self.session.query(DeviceModel)
            .filter(
                DeviceModel.device_type == DeviceType.SENSOR.value,
                DeviceModel.name.ilike(f"%{sensor_type}%"),
            )
            .all()
        )

        sensors = []
        for model in models:
            entity = self._model_to_entity(model)
            if isinstance(entity, Sensor):
                sensors.append(entity)
        return sensors
