"""
Modern service provider with dependency injection.

This module replaces traditional factories with a modern dependency injection
system using an IoC container with Python 3.12+.

Classes:
    ServiceProvider: Main provider for accessing services
    ScopedServiceProvider: Provider with scope management
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TypeVar

from domotix.controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from domotix.core.dependency_injection import DIContainer, container
from domotix.core.service_configuration import configure_services
from domotix.repositories import (
    DeviceRepository,
    LightRepository,
    SensorRepository,
    ShutterRepository,
)

T = TypeVar("T")


class ServiceProvider:
    """
    Main provider for accessing services with dependency injection.

    Replaces traditional factories with a modern DI system.
    """

    def __init__(self, di_container: DIContainer) -> None:
        """
        Initializes the service provider.

        Args:
            di_container: Dependency injection container
        """
        self._container = di_container

    def get_device_controller(self) -> DeviceController:
        """
        Retrieves a device controller with DI.

        Returns:
            Controller with injected dependencies
        """
        return self._container.resolve(DeviceController)

    def get_light_controller(self) -> LightController:
        """
        Retrieves a light controller with DI.

        Returns:
            Controller with injected dependencies
        """
        return self._container.resolve(LightController)

    def get_shutter_controller(self) -> ShutterController:
        """
        Retrieves a shutter controller with DI.

        Returns:
            Controller with injected dependencies
        """
        return self._container.resolve(ShutterController)

    def get_sensor_controller(self) -> SensorController:
        """
        Retrieves a sensor controller with DI.

        Returns:
            Controller with injected dependencies
        """
        return self._container.resolve(SensorController)

    def get_device_repository(self) -> DeviceRepository:
        """
        Retrieves a device repository with DI.

        Returns:
            Repository with injected dependencies
        """
        return self._container.resolve(DeviceRepository)

    def get_light_repository(self) -> LightRepository:
        """
        Retrieves a light repository with DI.

        Returns:
            Repository with injected dependencies
        """
        return self._container.resolve(LightRepository)

    def get_shutter_repository(self) -> ShutterRepository:
        """
        Retrieves a shutter repository with DI.

        Returns:
            Repository with injected dependencies
        """
        return self._container.resolve(ShutterRepository)

    def get_sensor_repository(self) -> SensorRepository:
        """
        Retrieves a sensor repository with DI.

        Returns:
            Repository with injected dependencies
        """
        return self._container.resolve(SensorRepository)

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolves an arbitrary service.

        Args:
            service_type: Type of the service to resolve

        Returns:
            Instance of the service
        """
        return self._container.resolve(service_type)


class ScopedServiceProvider:
    """
    Provider with automatic scope management.

    Uses a context manager to automatically manage
    the lifecycle of scoped services.
    """

    def __init__(self, di_container: DIContainer) -> None:
        """
        Initializes the scoped service provider.

        Args:
            di_container: Dependency injection container
        """
        self._container = di_container

    @contextmanager
    def create_scope(self) -> Generator[ServiceProvider, None, None]:
        """
        Creates a new scope for execution.

        Yields:
            Provider with isolated scope
        """
        with self._container.create_scope() as scoped_container:
            yield ServiceProvider(scoped_container)


# Configuration et initialisation du conteneur global
_configured_container = configure_services(container)

# Instance globale du service provider
service_provider = ServiceProvider(_configured_container)

# Instance globale du scoped service provider
scoped_service_provider = ScopedServiceProvider(_configured_container)


# Fonctions de convenance pour compatibilité avec l'ancien système
def get_service_provider() -> ServiceProvider:
    """
    Convenience function to retrieve the global service provider.

    Returns:
        Service provider configured with all dependencies
    """
    return service_provider


def get_device_controller() -> DeviceController:
    """
    Convenience function to retrieve a device controller.

    Returns:
        Controller with injected dependencies
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_device_controller()


def get_light_controller() -> LightController:
    """
    Convenience function to retrieve a light controller.

    Returns:
        Controller with injected dependencies
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_light_controller()


def get_shutter_controller() -> ShutterController:
    """
    Convenience function to retrieve a shutter controller.

    Returns:
        Controller with injected dependencies
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_shutter_controller()


def get_sensor_controller() -> SensorController:
    """
    Convenience function to retrieve a sensor controller.

    Returns:
        Controller with injected dependencies
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_sensor_controller()
