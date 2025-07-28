"""
Repository for device management.

This module contains the base repository for all devices
that handles CRUD operations with the database.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from domotix.globals.enums import DeviceType
from domotix.models import Device, Light, Sensor, Shutter
from domotix.models.base_model import DeviceModel


class DeviceRepository:
    """Repository pour la gestion des dispositifs en base de données."""

    def __init__(self, session: Session):
        """
        Initialise le repository avec une session SQLAlchemy.

        Args:
            session: Session SQLAlchemy pour les opérations de base de données
        """
        self.session = session

    def _model_to_entity(self, model: DeviceModel) -> Device:
        """
        Convertit un modèle SQLAlchemy en entité métier.

        Args:
            model: Modèle SQLAlchemy

        Returns:
            Device: Entité métier correspondante
        """
        device: Device
        if model.device_type == DeviceType.LIGHT.value:
            device = Light(model.name, model.location)  # type: ignore
            device.is_on = model.is_on or False  # type: ignore
        elif model.device_type == DeviceType.SHUTTER.value:
            device = Shutter(model.name, model.location)  # type: ignore
            # Pour les volets, is_open est calculé à partir de la position
            # Nous devons reconstituer la position à partir de is_open
            if model.is_open:  # type: ignore
                device.position = 100  # Ouvert
            else:
                device.position = 0  # Fermé
        elif model.device_type == DeviceType.SENSOR.value:
            device = Sensor(model.name, model.location)  # type: ignore
            device.value = model.value  # type: ignore
        else:
            # Ne devrait pas arriver, mais au cas où...
            raise ValueError(f"Type de dispositif inconnu: {model.device_type}")

        # Remplacer l'ID généré par celui de la base
        device.id = str(model.id)  # type: ignore
        return device

    def _entity_to_model(self, device: Device) -> DeviceModel:
        """
        Convertit une entité métier en modèle SQLAlchemy.

        Args:
            device: Entité métier

        Returns:
            DeviceModel: Modèle SQLAlchemy correspondant
        """
        model = DeviceModel(
            name=device.name,
            device_type=device.device_type.value,
            location=device.location,
        )

        # Copier l'ID si il existe
        if hasattr(device, "id") and device.id is not None:
            model.id = device.id  # type: ignore

        # Copier les attributs spécifiques
        if isinstance(device, Light):
            model.is_on = device.is_on  # type: ignore
        elif isinstance(device, Shutter):
            model.is_open = device.is_open  # type: ignore
        elif isinstance(device, Sensor):
            model.value = device.value  # type: ignore

        return model

    def save(self, device: Device) -> Device:
        """
        Sauvegarde un dispositif en base de données.

        Args:
            device: Dispositif à sauvegarder

        Returns:
            Device: Dispositif sauvegardé avec son ID
        """
        try:
            model = self._entity_to_model(device)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)

            # Mettre à jour l'ID du dispositif
            device.id = model.id  # type: ignore
            return device

        except Exception as e:
            self.session.rollback()
            raise e

    def find_by_id(self, device_id: str) -> Optional[Device]:
        """
        Trouve un dispositif par son ID.

        Args:
            device_id: ID du dispositif

        Returns:
            Device: Dispositif trouvé ou None
        """
        model = (
            self.session.query(DeviceModel).filter(DeviceModel.id == device_id).first()
        )
        return self._model_to_entity(model) if model else None

    def find_all(self) -> List[Device]:
        """
        Retrieves all devices.

        Returns:
            List[Device]: List of all devices (empty list if none found)
        """
        try:
            models = self.session.query(DeviceModel).all()
            return [self._model_to_entity(model) for model in models] if models else []
        except Exception:
            return []

    def update(self, device: Device) -> bool:
        """
        Met à jour un dispositif.

        Args:
            device: Dispositif à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            model = (
                self.session.query(DeviceModel)
                .filter(DeviceModel.id == device.id)
                .first()
            )
            if not model:
                return False

            # Mettre à jour les champs
            model.name = device.name  # type: ignore
            model.location = device.location  # type: ignore

            # Mettre à jour les champs spécifiques
            if isinstance(device, Light):
                model.is_on = device.is_on  # type: ignore
            elif isinstance(device, Shutter):
                model.is_open = device.is_open  # type: ignore
            elif isinstance(device, Sensor):
                model.value = device.value  # type: ignore

            self.session.commit()
            return True

        except Exception:
            self.session.rollback()
            return False

    def delete(self, device_id: str) -> bool:
        """
        Supprime un dispositif.

        Args:
            device_id: ID du dispositif à supprimer

        Returns:
            bool: True si la suppression a réussi
        """
        try:
            model = (
                self.session.query(DeviceModel)
                .filter(DeviceModel.id == device_id)
                .first()
            )
            if model:
                self.session.delete(model)
                self.session.commit()
                return True
            return False

        except Exception:
            self.session.rollback()
            return False

    def find_by_location(self, location: str) -> List[Device]:
        """
        Finds all devices in a given location.

        Args:
            location: Location to search for

        Returns:
            List[Device]: List of devices in that location (empty list if none found)
        """
        try:
            models = (
                self.session.query(DeviceModel)
                .filter(DeviceModel.location == location)
                .all()
            )
            return [self._model_to_entity(model) for model in models] if models else []
        except Exception:
            return []

    def find_by_type(self, device_type: DeviceType) -> List[Device]:
        """
        Finds all devices of a given type.

        Args:
            device_type: Type of device to search for

        Returns:
            List[Device]: List of devices of that type (empty list if none found)
        """
        try:
            models = (
                self.session.query(DeviceModel)
                .filter(DeviceModel.device_type == device_type.value)
                .all()
            )
            return [self._model_to_entity(model) for model in models] if models else []
        except Exception:
            return []

    def count_all(self) -> int:
        """
        Compte le nombre total de dispositifs.

        Returns:
            int: Nombre total de dispositifs
        """
        count: int = self.session.query(DeviceModel).count()
        return count

    def search_by_name(self, name_pattern: str) -> List[Device]:
        """
        Searches for devices by name (partial match).

        Args:
            name_pattern: Search pattern for the name

        Returns:
            List[Device]: List of matching devices (empty list if none found)
        """
        try:
            models = (
                self.session.query(DeviceModel)
                .filter(DeviceModel.name.contains(name_pattern))
                .all()
            )
            return [self._model_to_entity(model) for model in models] if models else []
        except Exception:
            return []
