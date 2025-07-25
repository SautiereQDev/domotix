"""
Factory pour la création des contrôleurs et repositories.

Ce module contient les factory methods pour créer facilement
les contrôleurs et repositories avec leurs dépendances configurées.

Classes:
    ControllerFactory: Factory pour créer les contrôleurs
    RepositoryFactory: Factory pour créer les repositories
"""

from typing import Optional

from sqlalchemy.orm import Session

from domotix.controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from domotix.core.database import SessionLocal
from domotix.repositories import (
    DeviceRepository,
    LightRepository,
    SensorRepository,
    ShutterRepository,
)


class RepositoryFactory:
    """
    Factory pour créer les repositories avec leurs dépendances.
    """

    @staticmethod
    def create_device_repository(session: Optional[Session] = None) -> DeviceRepository:
        """
        Crée un repository générique pour les dispositifs.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            DeviceRepository: Instance du repository
        """
        if session is None:
            session = SessionLocal()
        return DeviceRepository(session)

    @staticmethod
    def create_light_repository(session: Optional[Session] = None) -> LightRepository:
        """
        Crée un repository spécialisé pour les lampes.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            LightRepository: Instance du repository
        """
        if session is None:
            session = SessionLocal()
        return LightRepository(session)

    @staticmethod
    def create_shutter_repository(
        session: Optional[Session] = None,
    ) -> ShutterRepository:
        """
        Crée un repository spécialisé pour les volets.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            ShutterRepository: Instance du repository
        """
        if session is None:
            session = SessionLocal()
        return ShutterRepository(session)

    @staticmethod
    def create_sensor_repository(session: Optional[Session] = None) -> SensorRepository:
        """
        Crée un repository spécialisé pour les capteurs.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            SensorRepository: Instance du repository
        """
        if session is None:
            session = SessionLocal()
        return SensorRepository(session)


class ControllerFactory:
    """
    Factory pour créer les contrôleurs avec leurs dépendances.
    """

    @staticmethod
    def create_device_controller(session: Optional[Session] = None) -> DeviceController:
        """
        Crée un contrôleur générique pour les dispositifs.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            DeviceController: Instance du contrôleur
        """
        repository = RepositoryFactory.create_device_repository(session)
        return DeviceController(repository)

    @staticmethod
    def create_light_controller(session: Optional[Session] = None) -> LightController:
        """
        Crée un contrôleur spécialisé pour les lampes.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            LightController: Instance du contrôleur
        """
        repository = RepositoryFactory.create_light_repository(session)
        return LightController(repository)

    @staticmethod
    def create_shutter_controller(
        session: Optional[Session] = None,
    ) -> ShutterController:
        """
        Crée un contrôleur spécialisé pour les volets.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            ShutterController: Instance du contrôleur
        """
        repository = RepositoryFactory.create_shutter_repository(session)
        return ShutterController(repository)

    @staticmethod
    def create_sensor_controller(session: Optional[Session] = None) -> SensorController:
        """
        Crée un contrôleur spécialisé pour les capteurs.

        Args:
            session: Session de base de données (optionnel)

        Returns:
            SensorController: Instance du contrôleur
        """
        repository = RepositoryFactory.create_sensor_repository(session)
        return SensorController(repository)


# Instances partagées pour un usage simple
def get_device_controller() -> DeviceController:
    """Retourne une instance du contrôleur générique."""
    return ControllerFactory.create_device_controller()


def get_light_controller() -> LightController:
    """Retourne une instance du contrôleur de lampes."""
    return ControllerFactory.create_light_controller()


def get_shutter_controller() -> ShutterController:
    """Retourne une instance du contrôleur de volets."""
    return ControllerFactory.create_shutter_controller()


def get_sensor_controller() -> SensorController:
    """Retourne une instance du contrôleur de capteurs."""
    return ControllerFactory.create_sensor_controller()
