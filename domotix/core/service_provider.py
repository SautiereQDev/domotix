"""
Service provider moderne avec injection de dépendance.

Ce module remplace les factories traditionnelles par un système moderne
d'injection de dépendance avec conteneur IoC utilisant Python 3.12+.

Classes:
    ServiceProvider: Provider principal pour accéder aux services
    ScopedServiceProvider: Provider avec gestion de scope
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
    Provider principal pour accéder aux services avec injection de dépendance.

    Remplace les factories traditionnelles par un système moderne de DI.
    """

    def __init__(self, di_container: DIContainer) -> None:
        """
        Initialise le service provider.

        Args:
            di_container: Conteneur d'injection de dépendance
        """
        self._container = di_container

    def get_device_controller(self) -> DeviceController:
        """
        Récupère un contrôleur de dispositifs avec DI.

        Returns:
            Contrôleur avec dépendances injectées
        """
        return self._container.resolve(DeviceController)

    def get_light_controller(self) -> LightController:
        """
        Récupère un contrôleur de lampes avec DI.

        Returns:
            Contrôleur avec dépendances injectées
        """
        return self._container.resolve(LightController)

    def get_shutter_controller(self) -> ShutterController:
        """
        Récupère un contrôleur de volets avec DI.

        Returns:
            Contrôleur avec dépendances injectées
        """
        return self._container.resolve(ShutterController)

    def get_sensor_controller(self) -> SensorController:
        """
        Récupère un contrôleur de capteurs avec DI.

        Returns:
            Contrôleur avec dépendances injectées
        """
        return self._container.resolve(SensorController)

    def get_device_repository(self) -> DeviceRepository:
        """
        Récupère un repository de dispositifs avec DI.

        Returns:
            Repository avec dépendances injectées
        """
        return self._container.resolve(DeviceRepository)

    def get_light_repository(self) -> LightRepository:
        """
        Récupère un repository de lampes avec DI.

        Returns:
            Repository avec dépendances injectées
        """
        return self._container.resolve(LightRepository)

    def get_shutter_repository(self) -> ShutterRepository:
        """
        Récupère un repository de volets avec DI.

        Returns:
            Repository avec dépendances injectées
        """
        return self._container.resolve(ShutterRepository)

    def get_sensor_repository(self) -> SensorRepository:
        """
        Récupère un repository de capteurs avec DI.

        Returns:
            Repository avec dépendances injectées
        """
        return self._container.resolve(SensorRepository)

    def resolve(self, service_type: type[T]) -> T:
        """
        Résout un service arbitraire.

        Args:
            service_type: Type du service à résoudre

        Returns:
            Instance du service
        """
        return self._container.resolve(service_type)


class ScopedServiceProvider:
    """
    Provider avec gestion automatique de scope.

    Utilise un context manager pour gérer automatiquement
    le cycle de vie des services scoped.
    """

    def __init__(self, di_container: DIContainer) -> None:
        """
        Initialise le scoped service provider.

        Args:
            di_container: Conteneur d'injection de dépendance
        """
        self._container = di_container

    @contextmanager
    def create_scope(self) -> Generator[ServiceProvider, None, None]:
        """
        Crée un nouveau scope pour l'exécution.

        Yields:
            Provider avec scope isolé
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
    Fonction de convenance pour récupérer le service provider global.

    Returns:
        Service provider configuré avec toutes les dépendances
    """
    return service_provider


def get_device_controller() -> DeviceController:
    """
    Fonction de convenance pour récupérer un contrôleur de dispositifs.

    Returns:
        Contrôleur avec dépendances injectées
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_device_controller()


def get_light_controller() -> LightController:
    """
    Fonction de convenance pour récupérer un contrôleur de lampes.

    Returns:
        Contrôleur avec dépendances injectées
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_light_controller()


def get_shutter_controller() -> ShutterController:
    """
    Fonction de convenance pour récupérer un contrôleur de volets.

    Returns:
        Contrôleur avec dépendances injectées
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_shutter_controller()


def get_sensor_controller() -> SensorController:
    """
    Fonction de convenance pour récupérer un contrôleur de capteurs.

    Returns:
        Contrôleur avec dépendances injectées
    """
    with scoped_service_provider.create_scope() as provider:
        return provider.get_sensor_controller()
