"""
Contrôleur générique pour la gestion de tous les types de dispositifs.

Ce module contient le DeviceController qui fournit une interface unifiée
pour gérer tous les types de dispositifs (Light, Shutter, Sensor) en utilisant
le pattern Repository pour la persistance des données.

Classes:
    DeviceController: Contrôleur générique pour tous les types de dispositifs
"""

from typing import Dict, List, Optional

from domotix.models.device import Device
from domotix.models.light import Light
from domotix.models.sensor import Sensor
from domotix.models.shutter import Shutter
from domotix.repositories.device_repository import DeviceRepository


class DeviceController:
    """
    Contrôleur générique pour la gestion de tous les types de dispositifs.

    Ce contrôleur fournit une interface unifiée pour gérer tous les types
    de dispositifs dans le système domotique.

    Attributes:
        _repository: Repository pour la persistance des données
    """

    def __init__(self, device_repository: DeviceRepository):
        """
        Initialise le contrôleur avec un repository.

        Args:
            device_repository: Repository pour la persistance des données
        """
        self._repository = device_repository

    def get_device(self, device_id: str) -> Optional[Device]:
        """
        Récupère un dispositif par son ID.

        Args:
            device_id: ID du dispositif

        Returns:
            Optional[Device]: Le dispositif ou None si non trouvé
        """
        return self._repository.find_by_id(device_id)

    def get_all_devices(self) -> List[Device]:
        """
        Récupère tous les dispositifs.

        Returns:
            List[Device]: Liste de tous les dispositifs
        """
        return self._repository.find_all()

    def get_devices_by_type(self, device_type: type) -> List[Device]:
        """
        Récupère tous les dispositifs d'un type donné.

        Args:
            device_type: Type de dispositif (Light, Shutter, Sensor)

        Returns:
            List[Device]: Liste des dispositifs de ce type
        """
        all_devices = self.get_all_devices()
        return [device for device in all_devices if isinstance(device, device_type)]

    def get_devices_by_location(self, location: str) -> List[Device]:
        """
        Récupère tous les dispositifs d'un emplacement donné.

        Args:
            location: Emplacement à rechercher

        Returns:
            List[Device]: Liste des dispositifs dans cet emplacement
        """
        all_devices = self.get_all_devices()
        return [device for device in all_devices if device.location == location]

    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """
        Récupère le statut d'un dispositif.

        Args:
            device_id: ID du dispositif

        Returns:
            Optional[Dict]: Statut du dispositif ou None si non trouvé
        """
        device = self.get_device(device_id)
        if device:
            return device.get_state()
        return None

    def update_device_state(self, device_id: str, new_state: Dict) -> bool:
        """
        Met à jour l'état d'un dispositif.

        Args:
            device_id: ID du dispositif
            new_state: Nouvel état à appliquer

        Returns:
            bool: True si la mise à jour a réussi
        """
        device = self.get_device(device_id)
        if device:
            success = device.update_state(new_state)
            if success:
                return self._repository.update(device)
            return success
        return False

    def delete_device(self, device_id: str) -> bool:
        """
        Supprime un dispositif.

        Args:
            device_id: ID du dispositif

        Returns:
            bool: True si la suppression a réussi
        """
        return self._repository.delete(device_id)

    def get_devices_summary(self) -> Dict[str, int]:
        """
        Récupère un résumé du nombre de dispositifs par type.

        Returns:
            Dict[str, int]: Dictionnaire avec le nombre de dispositifs par type
        """
        all_devices = self.get_all_devices()
        summary = {
            "lights": len([d for d in all_devices if isinstance(d, Light)]),
            "shutters": len([d for d in all_devices if isinstance(d, Shutter)]),
            "sensors": len([d for d in all_devices if isinstance(d, Sensor)]),
            "total": len(all_devices),
        }
        return summary

    def get_locations(self) -> List[str]:
        """
        Récupère tous les emplacements uniques où des dispositifs sont installés.

        Returns:
            List[str]: Liste des emplacements uniques
        """
        all_devices = self.get_all_devices()
        locations = set()
        for device in all_devices:
            if device.location:
                locations.add(device.location)
        return sorted(list(locations))

    def search_devices(self, query: str) -> List[Device]:
        """
        Recherche des dispositifs par nom ou emplacement.

        Args:
            query: Terme de recherche

        Returns:
            List[Device]: Liste des dispositifs correspondants
        """
        all_devices = self.get_all_devices()
        query_lower = query.lower()

        matching_devices = []
        for device in all_devices:
            if query_lower in device.name.lower() or (
                device.location and query_lower in device.location.lower()
            ):
                matching_devices.append(device)

        return matching_devices

    def bulk_operation(
        self, device_ids: List[str], operation: str, **kwargs
    ) -> Dict[str, bool]:
        """
        Effectue une opération en lot sur plusieurs dispositifs.

        Args:
            device_ids: Liste des IDs des dispositifs
            operation: Opération à effectuer ("turn_on", "turn_off", "open",
            "close", etc.)
            **kwargs: Arguments supplémentaires pour l'opération

        Returns:
            Dict[str, bool]: Résultats de l'opération pour chaque dispositif
        """
        results = {}

        for device_id in device_ids:
            device = self.get_device(device_id)
            if device and hasattr(device, operation):
                try:
                    method = getattr(device, operation)
                    if kwargs:
                        method(**kwargs)
                    else:
                        method()
                    success = self._repository.update(device)
                    results[device_id] = success
                except Exception:
                    results[device_id] = False
            else:
                results[device_id] = False

        return results
