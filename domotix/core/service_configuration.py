"""
Configuration du conteneur d'injection de dépendance.

Ce module configure l'enregistrement de tous les services de l'application
dans le conteneur DI selon les bonnes pratiques.
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


# Marquer les classes existantes comme injectables
@Injectable(scope=Scope.SCOPED)
class InjectedDeviceRepository(DeviceRepository):
    """Repository de dispositifs avec injection de dépendance."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedLightRepository(LightRepository):
    """Repository de lampes avec injection de dépendance."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedShutterRepository(ShutterRepository):
    """Repository de volets avec injection de dépendance."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedSensorRepository(SensorRepository):
    """Repository de capteurs avec injection de dépendance."""

    pass


@Injectable(scope=Scope.SCOPED)
class InjectedDeviceController(DeviceController):
    """Contrôleur de dispositifs avec injection de dépendance."""

    def __init__(self, device_repository: DeviceRepository) -> None:
        """
        Initialise le contrôleur avec injection de dépendance.

        Args:
            device_repository: Repository injecté automatiquement
        """
        super().__init__(device_repository)


@Injectable(scope=Scope.SCOPED)
class InjectedLightController(LightController):
    """Contrôleur de lampes avec injection de dépendance."""

    def __init__(self, light_repository: DeviceRepository) -> None:
        """
        Initialise le contrôleur avec injection de dépendance.

        Args:
            light_repository: Repository injecté automatiquement
        """
        super().__init__(light_repository)


@Injectable(scope=Scope.SCOPED)
class InjectedShutterController(ShutterController):
    """Contrôleur de volets avec injection de dépendance."""

    def __init__(self, shutter_repository: DeviceRepository) -> None:
        """
        Initialise le contrôleur avec injection de dépendance.

        Args:
            shutter_repository: Repository injecté automatiquement
        """
        super().__init__(shutter_repository)


@Injectable(scope=Scope.SCOPED)
class InjectedSensorController(SensorController):
    """Contrôleur de capteurs avec injection de dépendance."""

    def __init__(self, sensor_repository: DeviceRepository) -> None:
        """
        Initialise le contrôleur avec injection de dépendance.

        Args:
            sensor_repository: Repository injecté automatiquement
        """
        super().__init__(sensor_repository)


def configure_services(container: DIContainer) -> DIContainer:
    """
    Configure tous les services dans le conteneur DI.

    Args:
        container: Conteneur à configurer

    Returns:
        DIContainer: Conteneur configuré
    """
    # Configuration de la session de base de données comme scoped
    # Une nouvelle session par scope (ex: par requête HTTP, par commande CLI)
    container.register_scoped(Session, factory=create_session)

    # Configuration des repositories comme scoped
    # Un repository par scope, partageant la même session
    container.register_scoped(DeviceRepository)
    container.register_scoped(LightRepository)
    container.register_scoped(ShutterRepository)
    container.register_scoped(SensorRepository)

    # Configuration des contrôleurs comme scoped avec les versions injectables
    # Un contrôleur par scope, avec injection automatique des repositories
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
