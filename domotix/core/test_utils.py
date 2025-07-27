"""
Utilitaires pour les tests avec injection de dépendance.

Ce module fournit des outils pour faciliter les tests avec le système
d'injection de dépendance moderne.

Classes:
    TestScope: Context manager pour les tests avec DI
    MockServiceProvider: Provider de test avec mocks
"""

import functools
from typing import Callable, Dict, Type, TypeVar
from unittest.mock import Mock

from domotix.core.dependency_injection import DIContainer
from domotix.core.service_provider import ServiceProvider

T = TypeVar("T")


class TestServiceProvider(ServiceProvider):
    """
    Service provider spécialisé pour les tests.

    Permet d'injecter des mocks facilement pour isoler les tests.
    """

    def __init__(self, di_container: DIContainer):
        """
        Initialise le test service provider.

        Args:
            di_container: Conteneur DI pour les tests
        """
        super().__init__(di_container)
        self._mocks: Dict[Type, Mock] = {}

    def mock_service(self, service_type: Type[T], mock_instance: Mock) -> None:
        """
        Enregistre un mock pour un type de service.

        Args:
            service_type: Type de service à mocker
            mock_instance: Instance mock à utiliser
        """
        self._mocks[service_type] = mock_instance
        self._container.register_instance(service_type, mock_instance)

    def get_mock(self, service_type: Type[T]) -> Mock:
        """
        Récupère le mock pour un type de service.

        Args:
            service_type: Type de service

        Returns:
            Mock: Instance mock
        """
        return self._mocks.get(service_type, Mock())


def with_test_scope(func: Callable) -> Callable:
    """
    Décorateur pour exécuter un test avec un scope DI isolé.

    Args:
        func: Fonction de test à décorer

    Returns:
        Callable: Fonction décorée avec gestion de scope
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Créer un conteneur de test isolé
        test_container = DIContainer()

        # Configurer les services de base pour les tests
        from domotix.core.service_configuration import configure_services

        configure_services(test_container)

        # Créer un provider de test
        test_provider = TestServiceProvider(test_container)

        # Exécuter le test avec le provider
        with test_container.create_scope():
            return func(*args, test_provider=test_provider, **kwargs)

    return wrapper


def with_mocked_dependencies(**mock_mappings) -> Callable:
    """
    Décorateur pour exécuter un test avec des dépendances mockées.

    Args:
        **mock_mappings: Mapping des types vers les mocks

    Returns:
        Callable: Décorateur configuré
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Créer un conteneur de test
            test_container = DIContainer()

            # Enregistrer les mocks
            for service_type, mock_instance in mock_mappings.items():
                test_container.register_instance(service_type, mock_instance)

            # Créer un provider de test
            test_provider = TestServiceProvider(test_container)

            # Exécuter le test avec le provider
            with test_container.create_scope():
                return func(*args, test_provider=test_provider, **kwargs)

        return wrapper

    return decorator


class TestDIContainer:
    """
    Conteneur DI spécialisé pour les tests avec utilitaires de mocking.
    """

    def __init__(self):
        """Initialise le conteneur de test."""
        self.container = DIContainer()
        self.mocks: Dict[Type, Mock] = {}

    def register_mock(
        self, service_type: Type[T], mock_instance: Mock | None = None
    ) -> Mock:
        """
        Enregistre un mock pour un service.

        Args:
            service_type: Type de service à mocker
            mock_instance: Mock spécifique (optionnel)

        Returns:
            Mock: Instance mock enregistrée
        """
        if mock_instance is None:
            mock_instance = Mock(spec=service_type)

        self.mocks[service_type] = mock_instance
        self.container.register_instance(service_type, mock_instance)
        return mock_instance

    def get_mock(self, service_type: Type[T]) -> Mock:
        """
        Récupère le mock pour un type.

        Args:
            service_type: Type de service

        Returns:
            Mock: Instance mock
        """
        return self.mocks.get(service_type)  # type: ignore[return-value]

    def resolve(self, service_type: Type[T]) -> T:
        """
        Résout un service (délègue au conteneur).

        Args:
            service_type: Type de service

        Returns:
            T: Instance du service
        """
        return self.container.resolve(service_type)  # type: ignore[return-value,no-any-return]  # noqa: E501

    def create_scope(self):
        """
        Crée un scope de test.

        Returns:
            ScopedContainer: Scope de test
        """
        return self.container.create_scope()


# Factory pour créer des conteneurs de test
def create_test_container() -> TestDIContainer:
    """
    Crée un conteneur DI configuré pour les tests.

    Returns:
        TestDIContainer: Conteneur de test configuré
    """
    test_container = TestDIContainer()

    # Configuration de base pour les tests
    from domotix.core.service_configuration import configure_services

    configure_services(test_container.container)

    return test_container
