"""
Contrôleur pour la gestion des capteurs et dispositifs de mesure.

Ce module contient le SensorController qui coordonne les opérations
sur les capteurs en utilisant le pattern Repository
pour la persistance des données.

Classes:
    SensorController: Contrôleur pour les capteurs et dispositifs de mesure
"""

from typing import List, Optional, Union, cast

from domotix.models.sensor import Sensor
from domotix.repositories.device_repository import DeviceRepository


class SensorController:
    """
    Contrôleur pour la gestion des capteurs et dispositifs de mesure.

    Ce contrôleur utilise l'injection de dépendance pour recevoir
    un repository et ne dépend pas d'un singleton pour la persistance.

    Attributes:
        _repository: Repository pour la persistance des données
    """

    def __init__(self, sensor_repository: DeviceRepository):
        """
        Initialise le contrôleur avec un repository.

        Args:
            sensor_repository: Repository pour la persistance des données de capteurs
        """
        self._repository = sensor_repository

    def create_sensor(self, name: str, location: Optional[str] = None) -> str:
        """
        Crée un nouveau capteur.

        Args:
            name: Nom du capteur
            location: Emplacement optionnel

        Returns:
            str: ID du capteur créé
        """
        sensor = Sensor(name=name, location=location)
        saved_sensor = self._repository.save(sensor)
        return str(saved_sensor.id)

    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """
        Récupère un capteur par son ID.

        Args:
            sensor_id: ID du capteur

        Returns:
            Optional[Sensor]: Le capteur ou None si non trouvé
        """
        device = self._repository.find_by_id(sensor_id)
        if device and isinstance(device, Sensor):
            return cast(Sensor, device)
        return None

    def get_all_sensors(self) -> List[Sensor]:
        """
        Récupère tous les capteurs.

        Returns:
            List[Sensor]: Liste de tous les capteurs
        """
        devices = self._repository.find_all()
        return [device for device in devices if isinstance(device, Sensor)]

    def update_value(self, sensor_id: str, value: Union[int, float]) -> bool:
        """
        Met à jour la valeur d'un capteur.

        Args:
            sensor_id: ID du capteur
            value: Nouvelle valeur du capteur

        Returns:
            bool: True si l'opération a réussi
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            sensor.update_value(value)
            return self._repository.update(sensor)
        return False

    def get_value(self, sensor_id: str) -> Optional[Union[int, float]]:
        """
        Récupère la valeur actuelle d'un capteur.

        Args:
            sensor_id: ID du capteur

        Returns:
            Optional[Union[int, float]]: Valeur du capteur ou None si non trouvé
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            return sensor.value
        return None

    def get_reading_history(self, sensor_id: str, limit: int = 100) -> List[dict]:
        """
        Récupère l'historique des valeurs d'un capteur.

        Note: Cette méthode nécessiterait un repository spécialisé pour l'historique.
        Pour l'instant, elle retourne une liste vide.

        Args:
            sensor_id: ID du capteur
            limit: Nombre maximum de lectures à retourner

        Returns:
            List[dict]: Liste des lectures historiques
        """
        # TODO: Implémenter avec un SensorReadingRepository spécialisé
        return []

    def reset_value(self, sensor_id: str) -> bool:
        """
        Remet à zéro la valeur d'un capteur.

        Args:
            sensor_id: ID du capteur

        Returns:
            bool: True si l'opération a réussi
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            sensor = cast(Sensor, sensor)  # Type explicit pour MyPy
            sensor.reset_value()  # type: ignore[attr-defined]
            return self._repository.update(sensor)
        return False

    def is_active(self, sensor_id: str) -> bool:
        """
        Vérifie si un capteur est actif (a une valeur).

        Args:
            sensor_id: ID du capteur

        Returns:
            bool: True si le capteur est actif
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            return sensor.value is not None
        return False

    def get_sensors_by_location(self, location: str) -> List[Sensor]:
        """
        Récupère tous les capteurs d'un emplacement donné.

        Args:
            location: Emplacement à rechercher

        Returns:
            List[Sensor]: Liste des capteurs dans cet emplacement
        """
        all_sensors = self.get_all_sensors()
        return [sensor for sensor in all_sensors if sensor.location == location]

    def delete_sensor(self, sensor_id: str) -> bool:
        """
        Supprime un capteur.

        Args:
            sensor_id: ID du capteur

        Returns:
            bool: True si la suppression a réussi
        """
        return self._repository.delete(sensor_id)
