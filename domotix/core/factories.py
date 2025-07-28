"""
Modern factory for creating Domotix objects.

This module implements a modern factory system using:
- Automatic dependency injection
- Modern object creation patterns
- Generic type support
- Centralized configuration

Classes:
    ControllerFactory: Factory for controllers
    RepositoryFactory: Factory for repositories
    ServiceFactory: Factory for services
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
    Modern factory for creating controllers.

    Uses dependency injection and centralized configuration
    to create the appropriate controllers.
    """

    def __init__(self, container: DIContainer) -> None:
        """
        Initializes the factory with a DI container.

        Args:
            container: Dependency injection container
        """
        self._container = container
        self._repo_factory = RepositoryFactory(container)

    def create_device_controller(self, session: Session) -> DeviceController:
        """
        Creates a device controller with its dependencies.

        Args:
            session: SQLAlchemy session

        Returns:
            Configured device controller

        Raises:
            ControllerError: If creation fails
        """
        try:
            repository = self._repo_factory.create_device_repository(session)

            # Manual injection because existing controllers
            # are not yet modernized
            return DeviceController(repository)

        except Exception as e:
            logger.error(f"Failed to create device controller: {e}")
            raise ControllerError(
                f"Unable to create device controller: {e}",
                controller_name="DeviceController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e

    def create_light_controller(self, session: Session) -> LightController:
        """
        Creates a light controller with its dependencies.

        Args:
            session: SQLAlchemy session

        Returns:
            Configured light controller

        Raises:
            ControllerError: If creation fails
        """
        try:
            repository = self._repo_factory.create_light_repository(session)
            return LightController(repository)

        except Exception as e:
            logger.error(f"Failed to create light controller: {e}")
            raise ControllerError(
                f"Unable to create light controller: {e}",
                controller_name="LightController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e

    def create_sensor_controller(self, session: Session) -> SensorController:
        """
        Creates a sensor controller with its dependencies.

        Args:
            session: SQLAlchemy session

        Returns:
            Configured sensor controller

        Raises:
            ControllerError: If creation fails
        """
        try:
            repository = self._repo_factory.create_sensor_repository(session)
            return SensorController(repository)

        except Exception as e:
            logger.error(f"Failed to create sensor controller: {e}")
            raise ControllerError(
                f"Unable to create sensor controller: {e}",
                controller_name="SensorController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e

    def create_shutter_controller(self, session: Session) -> ShutterController:
        """
        Creates a shutter controller with its dependencies.

        Args:
            session: SQLAlchemy session

        Returns:
            Configured shutter controller

        Raises:
            ControllerError: If creation fails
        """
        try:
            repository = self._repo_factory.create_shutter_repository(session)
            return ShutterController(repository)

        except Exception as e:
            logger.error(f"Failed to create shutter controller: {e}")
            raise ControllerError(
                f"Unable to create shutter controller: {e}",
                controller_name="ShutterController",
                error_code=ErrorCode.CONTROLLER_DEPENDENCY_ERROR,
                cause=e,
            ) from e


class RepositoryFactory:
    """
    Modern factory for creating repositories.

    Manages the creation and configuration of repositories
    with their appropriate dependencies.
    """

    def __init__(self, container: DIContainer) -> None:
        """
        Initializes the factory with a DI container.

        Args:
            container: Dependency injection container
        """
        self._container = container

    def create_device_repository(self, session: Session) -> DeviceRepository:
        """
        Creates a device repository.

        Args:
            session: SQLAlchemy session

        Returns:
            Device repository
        """
        return DeviceRepository(session)

    def create_light_repository(self, session: Session) -> LightRepository:
        """
        Creates a light repository.

        Args:
            session: SQLAlchemy session

        Returns:
            Light repository
        """
        return LightRepository(session)

    def create_sensor_repository(self, session: Session) -> SensorRepository:
        """
        Creates a sensor repository.

        Args:
            session: SQLAlchemy session

        Returns:
            Sensor repository
        """
        return SensorRepository(session)

    def create_shutter_repository(self, session: Session) -> ShutterRepository:
        """
        Creates a shutter repository.

        Args:
            session: SQLAlchemy session

        Returns:
            Shutter repository
        """
        return ShutterRepository(session)


@Injectable(scope=Scope.SINGLETON)
class ServiceFactory:
    """
    Factory for the application's business services.

    Uses dependency injection to create services
    with all their dependencies configured.
    """

    def __init__(self, container: DIContainer) -> None:
        """
        Initializes the service factory.

        Args:
            container: Dependency injection container
        """
        self._container = container

    def create_controller_factory(self) -> ControllerFactory:
        """
        Creates a controller factory.

        Returns:
            Configured controller factory
        """
        return ControllerFactory(self._container)

    def create_repository_factory(self) -> RepositoryFactory:
        """
        Creates a repository factory.

        Returns:
            Configured repository factory
        """
        return RepositoryFactory(self._container)


class FactoryManager:
    """
    Singleton manager for the application's factories.

    Avoids the use of global variables and provides a central access point
    for all factories.
    """

    _instance: FactoryManager | None = None
    _container: DIContainer | None = None
    _controller_factory: ControllerFactory | None = None
    _repository_factory: RepositoryFactory | None = None

    def __new__(cls) -> FactoryManager:
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_container(self) -> DIContainer:
        """
        Retrieves the global DI container.

        Returns:
            Dependency injection container
        """
        if self._container is None:
            self._container = DIContainer()
            # Service configuration will be added here
        return self._container

    def get_controller_factory(self) -> ControllerFactory:
        """
        Retrieves the global controller factory.

        Returns:
            Controller factory
        """
        if self._controller_factory is None:
            self._controller_factory = ControllerFactory(self.get_container())
        return self._controller_factory

    def get_repository_factory(self) -> RepositoryFactory:
        """
        Retrieves the global repository factory.

        Returns:
            Repository factory
        """
        if self._repository_factory is None:
            self._repository_factory = RepositoryFactory(self.get_container())
        return self._repository_factory

    def reset_factories(self) -> None:
        """
        Resets all factories.

        Useful for testing and reloading configuration.
        """
        self._container = None
        self._controller_factory = None
        self._repository_factory = None

    @classmethod
    def reset_instance(cls) -> None:
        """
        Resets the singleton instance.

        Useful for tests to create a new clean instance.
        """
        cls._instance = None


# Convenience functions for the public API
def get_container() -> DIContainer:
    """
    Retrieves the global DI container.

    Returns:
        Dependency injection container
    """
    return FactoryManager().get_container()


def get_controller_factory() -> ControllerFactory:
    """
    Retrieves the global controller factory.

    Returns:
        Controller factory
    """
    return FactoryManager().get_controller_factory()


def get_repository_factory() -> RepositoryFactory:
    """
    Retrieves the global repository factory.

    Returns:
        Repository factory
    """
    return FactoryManager().get_repository_factory()


def reset_factories() -> None:
    """
    Resets all global factories.

    Useful for testing and reloading configuration.
    """
    FactoryManager().reset_factories()


# Compatibility with the old system (to be gradually removed)
class LegacyControllerFactory:
    """Compatibility factory for the old system."""

    @staticmethod
    def create_device_controller(session: Session) -> DeviceController:
        """Creates a device controller (compatibility)."""
        return get_controller_factory().create_device_controller(session)

    @staticmethod
    def create_light_controller(session: Session) -> LightController:
        """Creates a light controller (compatibility)."""
        return get_controller_factory().create_light_controller(session)

    @staticmethod
    def create_sensor_controller(session: Session) -> SensorController:
        """Creates a sensor controller (compatibility)."""
        return get_controller_factory().create_sensor_controller(session)

    @staticmethod
    def create_shutter_controller(session: Session) -> ShutterController:
        """Creates a shutter controller (compatibility)."""
        return get_controller_factory().create_shutter_controller(session)
