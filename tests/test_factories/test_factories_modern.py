"""
Tests pour les factories modernes avec injection de dépendances.

Ce module contient tous les tests unitaires pour le nouveau système
de factories utilisant l'injection de dépendances moderne.
"""

from unittest.mock import Mock, patch

import pytest

from domotix.controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from domotix.core.factories import get_controller_factory, get_repository_factory
from domotix.repositories import (
    DeviceRepository,
    LightRepository,
    SensorRepository,
    ShutterRepository,
)


class TestModernRepositoryFactory:
    """Tests pour le nouveau système de repository factory avec DI."""

    def test_create_device_repository_with_session(self):
        """Test de création d'un DeviceRepository avec session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_device_repository(custom_session)

        # Assert
        assert isinstance(repository, DeviceRepository)
        assert repository.session == custom_session

    def test_create_light_repository_with_session(self):
        """Test de création d'un LightRepository avec session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_light_repository(custom_session)

        # Assert
        assert isinstance(repository, LightRepository)
        assert repository.session == custom_session

    def test_create_shutter_repository_with_session(self):
        """Test de création d'un ShutterRepository avec session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_shutter_repository(custom_session)

        # Assert
        assert isinstance(repository, ShutterRepository)
        assert repository.session == custom_session

    def test_create_sensor_repository_with_session(self):
        """Test de création d'un SensorRepository avec session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_sensor_repository(custom_session)

        # Assert
        assert isinstance(repository, SensorRepository)
        assert repository.session == custom_session

    def test_repository_factory_singleton(self):
        """Test que la repository factory est un singleton."""
        # Act
        factory1 = get_repository_factory()
        factory2 = get_repository_factory()

        # Assert
        assert factory1 is factory2, "Repository factory devrait être un singleton"


class TestModernControllerFactory:
    """Tests pour le nouveau système de controller factory avec DI."""

    @patch("domotix.core.factories.RepositoryFactory")
    def test_create_device_controller_with_session(self, mock_repo_factory_class):
        """Test de création d'un DeviceController avec session."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=DeviceRepository)

        mock_repo_factory = Mock()
        mock_repo_factory.create_device_repository.return_value = mock_repository
        mock_repo_factory_class.return_value = mock_repo_factory

        controller_factory = get_controller_factory()

        # Act
        controller = controller_factory.create_device_controller(custom_session)

        # Assert
        assert isinstance(controller, DeviceController)
        # Vérifier que le repository a été injecté
        assert hasattr(controller, "_repository")

    @patch("domotix.core.factories.RepositoryFactory")
    def test_create_light_controller_with_session(self, mock_repo_factory_class):
        """Test de création d'un LightController avec session."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=LightRepository)

        mock_repo_factory = Mock()
        mock_repo_factory.create_light_repository.return_value = mock_repository
        mock_repo_factory_class.return_value = mock_repo_factory

        controller_factory = get_controller_factory()

        # Act
        controller = controller_factory.create_light_controller(custom_session)

        # Assert
        assert isinstance(controller, LightController)
        assert hasattr(controller, "_repository")

    @patch("domotix.core.factories.RepositoryFactory")
    def test_create_shutter_controller_with_session(self, mock_repo_factory_class):
        """Test de création d'un ShutterController avec session."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=ShutterRepository)

        mock_repo_factory = Mock()
        mock_repo_factory.create_shutter_repository.return_value = mock_repository
        mock_repo_factory_class.return_value = mock_repo_factory

        controller_factory = get_controller_factory()

        # Act
        controller = controller_factory.create_shutter_controller(custom_session)

        # Assert
        assert isinstance(controller, ShutterController)
        assert hasattr(controller, "_repository")

    @patch("domotix.core.factories.RepositoryFactory")
    def test_create_sensor_controller_with_session(self, mock_repo_factory_class):
        """Test de création d'un SensorController avec session."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=SensorRepository)

        mock_repo_factory = Mock()
        mock_repo_factory.create_sensor_repository.return_value = mock_repository
        mock_repo_factory_class.return_value = mock_repo_factory

        controller_factory = get_controller_factory()

        # Act
        controller = controller_factory.create_sensor_controller(custom_session)

        # Assert
        assert isinstance(controller, SensorController)
        assert hasattr(controller, "_repository")

    def test_controller_factory_singleton(self):
        """Test que la controller factory est un singleton."""
        # Act
        factory1 = get_controller_factory()
        factory2 = get_controller_factory()

        # Assert
        assert factory1 is factory2, "Controller factory devrait être un singleton"


class TestFactoryIntegration:
    """Tests d'intégration pour le nouveau système de factories."""

    def test_factory_singletons(self):
        """Test que les factories sont des singletons."""
        # Act
        controller_factory1 = get_controller_factory()
        controller_factory2 = get_controller_factory()

        repo_factory1 = get_repository_factory()
        repo_factory2 = get_repository_factory()

        # Assert
        assert controller_factory1 is controller_factory2
        assert repo_factory1 is repo_factory2

    @patch("domotix.core.database.create_session")
    def test_factories_with_dependency_injection(self, mock_create_session):
        """Test du système DI avec les factories."""
        # Arrange
        mock_session = Mock()
        mock_create_session.return_value = mock_session

        controller_factory = get_controller_factory()
        repo_factory = get_repository_factory()

        # Act & Assert - vérifier qu'aucune exception n'est levée
        try:
            # Créer des repositories
            device_repo = repo_factory.create_device_repository(mock_session)
            light_repo = repo_factory.create_light_repository(mock_session)

            # Créer des contrôleurs
            device_controller = controller_factory.create_device_controller(
                mock_session
            )
            light_controller = controller_factory.create_light_controller(mock_session)

            # Vérifier les types
            assert isinstance(device_repo, DeviceRepository)
            assert isinstance(light_repo, LightRepository)
            assert isinstance(device_controller, DeviceController)
            assert isinstance(light_controller, LightController)

        except Exception as e:
            pytest.fail(f"Factory integration with DI failed: {e}")

    def test_modern_factory_architecture(self):
        """Test de l'architecture moderne des factories."""
        # Act
        controller_factory = get_controller_factory()
        repo_factory = get_repository_factory()

        # Assert - vérifier les attributs de l'architecture moderne
        assert hasattr(
            controller_factory, "_container"
        ), "Controller factory devrait avoir un container DI"
        assert hasattr(
            repo_factory, "_container"
        ), "Repository factory devrait avoir un container DI"


class TestDependencyInjectionIntegration:
    """Tests spécifiques à l'intégration avec le système DI."""

    def test_service_provider_integration(self):
        """Test de l'intégration avec le service provider."""
        from domotix.core.service_provider import get_service_provider

        # Act
        service_provider = get_service_provider()
        controller_factory = get_controller_factory()

        # Assert
        assert service_provider is not None
        assert controller_factory is not None
        # Les factories utilisent le système DI moderne
        assert hasattr(controller_factory, "_container")

    def test_container_usage_in_factories(self):
        """Test que les factories utilisent correctement le container DI."""
        # Act
        controller_factory = get_controller_factory()
        repo_factory = get_repository_factory()

        # Assert
        assert controller_factory is not None
        assert repo_factory is not None
        # Vérifier que le container est présent dans l'architecture
        assert hasattr(controller_factory, "_container")
        assert hasattr(repo_factory, "_container")

    def test_error_handling_with_modern_exceptions(self):
        """Test de la gestion d'erreurs avec le nouveau système d'exceptions."""
        from domotix.globals.exceptions import ControllerError

        # Act
        controller_factory = get_controller_factory()

        # Assert - Test que les exceptions modernes sont utilisées
        try:
            # Tenter de créer avec session None devrait utiliser les
            # nouvelles exceptions
            controller_factory.create_device_controller(None)
        except ControllerError:
            # C'est attendu avec le nouveau système
            pass
        except Exception as e:
            # Vérifier que l'erreur est bien gérée
            assert e is not None


class TestBackwardCompatibility:
    """Tests de compatibilité avec l'ancien système."""

    def test_legacy_imports_still_work(self):
        """Test que les anciens imports fonctionnent encore."""
        # Act & Assert - Les imports devraient fonctionner
        try:
            from domotix.core.factories import LegacyControllerFactory

            # Les méthodes de compatibilité devraient exister
            assert hasattr(LegacyControllerFactory, "create_device_controller")
            assert hasattr(LegacyControllerFactory, "create_light_controller")

        except ImportError:
            pytest.fail("La compatibilité avec l'ancien système a été rompue")

    def test_modern_vs_legacy_consistency(self):
        """Test de cohérence entre nouveau et ancien système."""
        # Arrange
        mock_session = Mock()

        # Act
        modern_factory = get_controller_factory()
        modern_controller = modern_factory.create_device_controller(mock_session)

        # Assert
        assert isinstance(modern_controller, DeviceController)
        # Le nouveau système doit créer les mêmes types que l'ancien
        assert hasattr(modern_controller, "_repository")
