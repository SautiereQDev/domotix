"""
Dependency injection container configuration.

This module configures the registration of all application services
in the DI container according to best practices.
"""

from sqlalchemy.orm import Session

from domotix.controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from domotix.core.database import create_session
from domotix.core.dependency_injection import DIContainer, Injectable, Scope
from domotix.repositories import (
    DeviceRepository,
    LightRepository,
    SensorRepository,
    ShutterRepository,
)


# Mark existing classes as injectable
@Injectable(scope=Scope.SCOPED)
class InjectedDeviceRepository(DeviceRepository):
    """Device repository with dependency injection."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedLightRepository(LightRepository):
    """Light repository with dependency injection."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedShutterRepository(ShutterRepository):
    """Shutter repository with dependency injection."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedSensorRepository(SensorRepository):
    """Sensor repository with dependency injection."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedDeviceController(DeviceController):
    """Device controller with dependency injection."""

    def __init__(self, device_repository: DeviceRepository) -> None:
        """
        Initialize the controller with dependency injection.

        Args:
            device_repository: Repository automatically injected
        """
        super().__init__(device_repository)


@Injectable(scope=Scope.SCOPED)
class InjectedLightController(LightController):
    """Light controller with dependency injection."""

    def __init__(self, light_repository: DeviceRepository) -> None:
        """
        Initialize the controller with dependency injection.

        Args:
            light_repository: Repository automatically injected
        """
        super().__init__(light_repository)


@Injectable(scope=Scope.SCOPED)
class InjectedShutterController(ShutterController):
    """Shutter controller with dependency injection."""

    def __init__(self, shutter_repository: DeviceRepository) -> None:
        """
        Initialize the controller with dependency injection.

        Args:
            shutter_repository: Repository automatically injected
        """
        super().__init__(shutter_repository)


@Injectable(scope=Scope.SCOPED)
class InjectedSensorController(SensorController):
    """Sensor controller with dependency injection."""

    def __init__(self, sensor_repository: DeviceRepository) -> None:
        """
        Initialize the controller with dependency injection.

        Args:
            sensor_repository: Repository automatically injected
        """
        super().__init__(sensor_repository)


def configure_services(container: DIContainer) -> DIContainer:
    """
    Configure all services in the DI container.

    Args:
        container: Container to configure

    Returns:
        DIContainer: Configured container
    """
    # Configure the database session as scoped
    # A new session per scope (e.g., per HTTP request, per CLI command)
    container.register_scoped(Session, factory=create_session)

    # Configure repositories as scoped
    # One repository per scope, sharing the same session
    container.register_scoped(DeviceRepository)
    container.register_scoped(LightRepository)
    container.register_scoped(ShutterRepository)
    container.register_scoped(SensorRepository)

    # Configure controllers as scoped with injectable versions
    # One controller per scope, with automatic repository injection
    container.register_scoped(
        DeviceController, implementation_type=InjectedDeviceController
    )
    container.register_scoped(
        LightController, implementation_type=InjectedLightController
    )
    container.register_scoped(
        ShutterController, implementation_type=InjectedShutterController
    )
    container.register_scoped(
        SensorController, implementation_type=InjectedSensorController
    )

    return container
