"""
Interfaces et protocoles pour l'architecture moderne de Domotix.

Ce module définit les interfaces et protocoles suivant les bonnes pratiques
Python modernes avec typing et runtime protocols.

Protocols:
    DeviceRepositoryProtocol: Interface pour les repositories de dispositifs
    DeviceControllerProtocol: Interface pour les contrôleurs de dispositifs
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from domotix.models.device import Device


@runtime_checkable
class DeviceRepositoryProtocol(Protocol):
    """Protocol définissant l'interface d'un repository de dispositifs."""

    def save(self, device: Device) -> Device:
        """
        Sauvegarde un dispositif.

        Args:
            device: Dispositif à sauvegarder

        Returns:
            Dispositif sauvegardé avec ID
        """
        ...

    def find_by_id(self, device_id: str) -> Device | None:
        """
        Trouve un dispositif par son ID.

        Args:
            device_id: ID du dispositif

        Returns:
            Dispositif trouvé ou None
        """
        ...

    def find_all(self) -> Sequence[Device]:
        """
        Trouve tous les dispositifs.

        Returns:
            Séquence de tous les dispositifs
        """
        ...

    def update(self, device: Device) -> bool:
        """
        Met à jour un dispositif.

        Args:
            device: Dispositif à mettre à jour

        Returns:
            True si la mise à jour a réussi
        """
        ...

    def delete(self, device_id: str) -> bool:
        """
        Supprime un dispositif.

        Args:
            device_id: ID du dispositif à supprimer

        Returns:
            True si la suppression a réussi
        """
        ...


@runtime_checkable
class DeviceControllerProtocol(Protocol):
    """Protocol définissant l'interface d'un contrôleur de dispositifs."""

    def get_device(self, device_id: str) -> Device | None:
        """
        Récupère un dispositif par son ID.

        Args:
            device_id: ID du dispositif

        Returns:
            Dispositif ou None si non trouvé
        """
        ...

    def get_all_devices(self) -> Sequence[Device]:
        """
        Récupère tous les dispositifs.

        Returns:
            Séquence de tous les dispositifs
        """
        ...

    def delete_device(self, device_id: str) -> bool:
        """
        Supprime un dispositif.

        Args:
            device_id: ID du dispositif

        Returns:
            True si la suppression a réussi
        """
        ...


class BaseRepository(ABC):
    """
    Classe de base abstraite pour tous les repositories.

    Définit les méthodes communes et les bonnes pratiques
    pour l'implémentation des repositories.
    """

    @abstractmethod
    def save(self, entity: Device) -> Device:
        """
        Sauvegarde une entité.

        Args:
            entity: Entité à sauvegarder

        Returns:
            Entité sauvegardée
        """
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Device | None:
        """
        Trouve une entité par son ID.

        Args:
            entity_id: ID de l'entité

        Returns:
            Entité trouvée ou None
        """
        pass

    @abstractmethod
    def find_all(self) -> Sequence[Device]:
        """
        Trouve toutes les entités.

        Returns:
            Séquence de toutes les entités
        """
        pass

    @abstractmethod
    def update(self, entity: Device) -> bool:
        """
        Met à jour une entité.

        Args:
            entity: Entité à mettre à jour

        Returns:
            True si la mise à jour a réussi
        """
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Supprime une entité.

        Args:
            entity_id: ID de l'entité

        Returns:
            True si la suppression a réussi
        """
        pass


class BaseController(ABC):
    """
    Classe de base abstraite pour tous les contrôleurs.

    Définit les méthodes communes et les bonnes pratiques
    pour l'implémentation des contrôleurs.
    """

    def __init__(self, repository: DeviceRepositoryProtocol) -> None:
        """
        Initialise le contrôleur avec un repository.

        Args:
            repository: Repository injecté
        """
        self._repository = repository

    @property
    def repository(self) -> DeviceRepositoryProtocol:
        """
        Accès en lecture seule au repository.

        Returns:
            Repository associé au contrôleur
        """
        return self._repository


# Type aliases pour améliorer la lisibilité
DeviceId = str
EntityCollection = Sequence[Device]
OperationResult = bool
