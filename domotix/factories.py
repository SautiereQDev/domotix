"""
Factory moderne pour la création d'objets Domotix.

Ce module implémente un système de factory moderne utilisant:
- Injection de dépendances automatique
- Patterns modernes de création d'objets
- Support des types génériques
- Configuration centralisée

Classes:
    ControllerFactory: Factory pour les contrôleurs
    RepositoryFactory: Factory pour les repositories
    ServiceFactory: Factory pour les services
"""

from __future__ import annotations

from typing import TypeVar

from sqlalchemy.orm import Session

from domotix.controllers.device_controller import DeviceController
from domotix.controllers.light_controller import LightController
from domotix.controllers.sensor_controller import SensorController
from domotix.controllers.shutter_controller import ShutterController
from domotix.core.dependency_injection import DIContainer, Injectable, Scope
from domotix.core.interfaces import BaseController, DeviceRepositoryProtocol
from domotix.core.logging_system import get_logger
from domotix.globals.exceptions import ControllerError, ErrorCode
from domotix.repositories.device_repository import DeviceRepository
from domotix.repositories.light_repository import LightRepository
from domotix.repositories.sensor_repository import SensorRepository
from domotix.repositories.shutter_repository import ShutterRepository

T = TypeVar("T", bound=BaseController)
R = TypeVar("R", bound=DeviceRepositoryProtocol)

logger = get_logger(__name__)


class ControllerFactory:
    """
    Factory moderne pour la création de contrôleurs.

    Utilise l'injection de dépendances et la configuration
    centralisée pour créer les contrôleurs appropriés.
    """

    def __init__(self, container: DIContainer) -> None:
        """
        Initialise la factory avec un container DI.

        Args:
            container: Container d'injection de dépendances
        """
        self._container = container

    def create_device_controller(self, session: Session) -> DeviceController:
        """
        Crée un contrôleur de dispositifs avec ses dépendances.

        Args:
            session: Session SQLAlchemy

        Returns:
            Contrôleur de dispositifs configuré

        Raises:
            ControllerError: Si la création échoue
        """
        try:
            repo_factory = RepositoryFactory(self._container)
            repository = repo_factory.create_device_repository(session)

            # Injection manuelle car les contrôleurs existants
            # ne sont pas encore modernisés
            return DeviceController(repository)

        except Exception as e:
            logger.error(f"Échec de création du contrôleur de dispositifs: {e}")
            raise ControllerError(
                f"Impossible de créer le contrôleur de dispositifs: {e}",
                controller_name="DeviceController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e

    def create_light_controller(self, session: Session) -> LightController:
        """
        Crée un contrôleur de lumières avec ses dépendances.

        Args:
            session: Session SQLAlchemy

        Returns:
            Contrôleur de lumières configuré

        Raises:
            ControllerError: Si la création échoue
        """
        try:
            repo_factory = RepositoryFactory(self._container)
            repository = repo_factory.create_light_repository(session)
            return LightController(repository)

        except Exception as e:
            logger.error(f"Échec de création du contrôleur de lumières: {e}")
            raise ControllerError(
                f"Impossible de créer le contrôleur de lumières: {e}",
                controller_name="LightController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e

    def create_sensor_controller(self, session: Session) -> SensorController:
        """
        Crée un contrôleur de capteurs avec ses dépendances.

        Args:
            session: Session SQLAlchemy

        Returns:
            Contrôleur de capteurs configuré

        Raises:
            ControllerError: Si la création échoue
        """
        try:
            repo_factory = RepositoryFactory(self._container)
            repository = repo_factory.create_sensor_repository(session)
            return SensorController(repository)

        except Exception as e:
            logger.error(f"Échec de création du contrôleur de capteurs: {e}")
            raise ControllerError(
                f"Impossible de créer le contrôleur de capteurs: {e}",
                controller_name="SensorController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e

    def create_shutter_controller(self, session: Session) -> ShutterController:
        """
        Crée un contrôleur de volets avec ses dépendances.

        Args:
            session: Session SQLAlchemy

        Returns:
            Contrôleur de volets configuré

        Raises:
            ControllerError: Si la création échoue
        """
        try:
            repo_factory = RepositoryFactory(self._container)
            repository = repo_factory.create_shutter_repository(session)
            return ShutterController(repository)

        except Exception as e:
            logger.error(f"Échec de création du contrôleur de volets: {e}")
            raise ControllerError(
                f"Impossible de créer le contrôleur de volets: {e}",
                controller_name="ShutterController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e


class RepositoryFactory:
    """
    Factory moderne pour la création de repositories.

    Gère la création et la configuration des repositories
    avec leurs dépendances appropriées.
    """

    def __init__(self, container: DIContainer) -> None:
        """
        Initialise la factory avec un container DI.

        Args:
            container: Container d'injection de dépendances
        """
        self._container = container

    def create_device_repository(self, session: Session) -> DeviceRepository:
        """
        Crée un repository de dispositifs.

        Args:
            session: Session SQLAlchemy

        Returns:
            Repository de dispositifs
        """
        return DeviceRepository(session)

    def create_light_repository(self, session: Session) -> LightRepository:
        """
        Crée un repository de lumières.

        Args:
            session: Session SQLAlchemy

        Returns:
            Repository de lumières
        """
        return LightRepository(session)

    def create_sensor_repository(self, session: Session) -> SensorRepository:
        """
        Crée un repository de capteurs.

        Args:
            session: Session SQLAlchemy

        Returns:
            Repository de capteurs
        """
        return SensorRepository(session)

    def create_shutter_repository(self, session: Session) -> ShutterRepository:
        """
        Crée un repository de volets.

        Args:
            session: Session SQLAlchemy

        Returns:
            Repository de volets
        """
        return ShutterRepository(session)


@Injectable(scope=Scope.SINGLETON)
class ServiceFactory:
    """
    Factory pour les services métier de l'application.

    Utilise l'injection de dépendances pour créer des services
    avec toutes leurs dépendances configurées.
    """

    def __init__(self, container: DIContainer) -> None:
        """
        Initialise la factory de services.

        Args:
            container: Container d'injection de dépendances
        """
        self._container = container

    def create_controller_factory(self) -> ControllerFactory:
        """
        Crée une factory de contrôleurs.

        Returns:
            Factory de contrôleurs configurée
        """
        return ControllerFactory(self._container)

    def create_repository_factory(self) -> RepositoryFactory:
        """
        Crée une factory de repositories.

        Returns:
            Factory de repositories configurée
        """
        return RepositoryFactory(self._container)


# Factory globale utilisée par l'application
_global_container: DIContainer | None = None
_controller_factory: ControllerFactory | None = None
_repository_factory: RepositoryFactory | None = None


def get_container() -> DIContainer:
    """
    Récupère le container DI global.

    Returns:
        Container d'injection de dépendances
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
        # Configuration des services sera ajoutée ici
    return _global_container


def get_controller_factory() -> ControllerFactory:
    """
    Récupère la factory de contrôleurs globale.

    Returns:
        Factory de contrôleurs
    """
    global _controller_factory
    if _controller_factory is None:
        _controller_factory = ControllerFactory(get_container())
    return _controller_factory


def get_repository_factory() -> RepositoryFactory:
    """
    Récupère la factory de repositories globale.

    Returns:
        Factory de repositories
    """
    global _repository_factory
    if _repository_factory is None:
        _repository_factory = RepositoryFactory(get_container())
    return _repository_factory


def reset_factories() -> None:
    """
    Remet à zéro toutes les factories globales.

    Utile pour les tests et le rechargement de configuration.
    """
    global _global_container, _controller_factory, _repository_factory
    _global_container = None
    _controller_factory = None
    _repository_factory = None


# Compatibilité avec l'ancien système (à supprimer progressivement)
class LegacyControllerFactory:
    """Factory de compatibilité pour l'ancien système."""

    @staticmethod
    def create_device_controller(session: Session) -> DeviceController:
        """Crée un contrôleur de dispositifs (compatibilité)."""
        return get_controller_factory().create_device_controller(session)

    @staticmethod
    def create_light_controller(session: Session) -> LightController:
        """Crée un contrôleur de lumières (compatibilité)."""
        return get_controller_factory().create_light_controller(session)

    @staticmethod
    def create_sensor_controller(session: Session) -> SensorController:
        """Crée un contrôleur de capteurs (compatibilité)."""
        return get_controller_factory().create_sensor_controller(session)

    @staticmethod
    def create_shutter_controller(session: Session) -> ShutterController:
        """Crée un contrôleur de volets (compatibilité)."""
        return get_controller_factory().create_shutter_controller(session)
