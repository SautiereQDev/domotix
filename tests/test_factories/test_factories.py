"""
Tests pour les factories.

Ce module contient tous les tests unitaires pour les factory classes
qui créent les contrôleurs et repositories.
"""

from unittest.mock import Mock, patch

import pytest

from domotix.controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from domotix.factories import (
    ControllerFactory,
    RepositoryFactory,
    get_device_controller,
    get_light_controller,
    get_sensor_controller,
    get_shutter_controller,
)
from domotix.repositories import (
    DeviceRepository,
    LightRepository,
    SensorRepository,
    ShutterRepository,
)


class TestRepositoryFactory:
    """Tests pour la classe RepositoryFactory."""

    @patch("domotix.factories.SessionLocal")
    def test_create_device_repository_with_default_session(self, mock_session_local):
        """Test de création d'un DeviceRepository avec session par défaut."""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        repository = RepositoryFactory.create_device_repository()

        # Assert
        assert isinstance(repository, DeviceRepository)
        assert repository.session == mock_session
        mock_session_local.assert_called_once()

    def test_create_device_repository_with_custom_session(self):
        """Test de création d'un DeviceRepository avec session personnalisée."""
        # Arrange
        custom_session = Mock()

        # Act
        repository = RepositoryFactory.create_device_repository(custom_session)

        # Assert
        assert isinstance(repository, DeviceRepository)
        assert repository.session == custom_session

    @patch("domotix.factories.SessionLocal")
    def test_create_light_repository_with_default_session(self, mock_session_local):
        """Test de création d'un LightRepository avec session par défaut."""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        repository = RepositoryFactory.create_light_repository()

        # Assert
        assert isinstance(repository, LightRepository)
        assert repository.session == mock_session
        mock_session_local.assert_called_once()

    def test_create_light_repository_with_custom_session(self):
        """Test de création d'un LightRepository avec session personnalisée."""
        # Arrange
        custom_session = Mock()

        # Act
        repository = RepositoryFactory.create_light_repository(custom_session)

        # Assert
        assert isinstance(repository, LightRepository)
        assert repository.session == custom_session

    @patch("domotix.factories.SessionLocal")
    def test_create_shutter_repository_with_default_session(self, mock_session_local):
        """Test de création d'un ShutterRepository avec session par défaut."""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        repository = RepositoryFactory.create_shutter_repository()

        # Assert
        assert isinstance(repository, ShutterRepository)
        assert repository.session == mock_session
        mock_session_local.assert_called_once()

    def test_create_shutter_repository_with_custom_session(self):
        """Test de création d'un ShutterRepository avec session personnalisée."""
        # Arrange
        custom_session = Mock()

        # Act
        repository = RepositoryFactory.create_shutter_repository(custom_session)

        # Assert
        assert isinstance(repository, ShutterRepository)
        assert repository.session == custom_session

    @patch("domotix.factories.SessionLocal")
    def test_create_sensor_repository_with_default_session(self, mock_session_local):
        """Test de création d'un SensorRepository avec session par défaut."""
        # Arrange
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        # Act
        repository = RepositoryFactory.create_sensor_repository()

        # Assert
        assert isinstance(repository, SensorRepository)
        assert repository.session == mock_session
        mock_session_local.assert_called_once()

    def test_create_sensor_repository_with_custom_session(self):
        """Test de création d'un SensorRepository avec session personnalisée."""
        # Arrange
        custom_session = Mock()

        # Act
        repository = RepositoryFactory.create_sensor_repository(custom_session)

        # Assert
        assert isinstance(repository, SensorRepository)
        assert repository.session == custom_session


class TestControllerFactory:
    """Tests pour la classe ControllerFactory."""

    @patch("domotix.factories.RepositoryFactory.create_device_repository")
    def test_create_device_controller_with_default_session(self, mock_create_repo):
        """Test de création d'un DeviceController avec session par défaut."""
        # Arrange
        mock_repository = Mock(spec=DeviceRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_device_controller()

        # Assert
        assert isinstance(controller, DeviceController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(None)

    @patch("domotix.factories.RepositoryFactory.create_device_repository")
    def test_create_device_controller_with_custom_session(self, mock_create_repo):
        """Test de création d'un DeviceController avec session personnalisée."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=DeviceRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_device_controller(custom_session)

        # Assert
        assert isinstance(controller, DeviceController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(custom_session)

    @patch("domotix.factories.RepositoryFactory.create_light_repository")
    def test_create_light_controller_with_default_session(self, mock_create_repo):
        """Test de création d'un LightController avec session par défaut."""
        # Arrange
        mock_repository = Mock(spec=LightRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_light_controller()

        # Assert
        assert isinstance(controller, LightController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(None)

    @patch("domotix.factories.RepositoryFactory.create_light_repository")
    def test_create_light_controller_with_custom_session(self, mock_create_repo):
        """Test de création d'un LightController avec session personnalisée."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=LightRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_light_controller(custom_session)

        # Assert
        assert isinstance(controller, LightController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(custom_session)

    @patch("domotix.factories.RepositoryFactory.create_shutter_repository")
    def test_create_shutter_controller_with_default_session(self, mock_create_repo):
        """Test de création d'un ShutterController avec session par défaut."""
        # Arrange
        mock_repository = Mock(spec=ShutterRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_shutter_controller()

        # Assert
        assert isinstance(controller, ShutterController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(None)

    @patch("domotix.factories.RepositoryFactory.create_shutter_repository")
    def test_create_shutter_controller_with_custom_session(self, mock_create_repo):
        """Test de création d'un ShutterController avec session personnalisée."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=ShutterRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_shutter_controller(custom_session)

        # Assert
        assert isinstance(controller, ShutterController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(custom_session)

    @patch("domotix.factories.RepositoryFactory.create_sensor_repository")
    def test_create_sensor_controller_with_default_session(self, mock_create_repo):
        """Test de création d'un SensorController avec session par défaut."""
        # Arrange
        mock_repository = Mock(spec=SensorRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_sensor_controller()

        # Assert
        assert isinstance(controller, SensorController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(None)

    @patch("domotix.factories.RepositoryFactory.create_sensor_repository")
    def test_create_sensor_controller_with_custom_session(self, mock_create_repo):
        """Test de création d'un SensorController avec session personnalisée."""
        # Arrange
        custom_session = Mock()
        mock_repository = Mock(spec=SensorRepository)
        mock_create_repo.return_value = mock_repository

        # Act
        controller = ControllerFactory.create_sensor_controller(custom_session)

        # Assert
        assert isinstance(controller, SensorController)
        assert controller._repository == mock_repository
        mock_create_repo.assert_called_once_with(custom_session)


class TestConvenienceFunctions:
    """Tests pour les fonctions de commodité."""

    @patch("domotix.factories.ControllerFactory.create_device_controller")
    def test_get_device_controller(self, mock_create_controller):
        """Test de la fonction get_device_controller."""
        # Arrange
        mock_controller = Mock(spec=DeviceController)
        mock_create_controller.return_value = mock_controller

        # Act
        result = get_device_controller()

        # Assert
        assert result == mock_controller
        mock_create_controller.assert_called_once()

    @patch("domotix.factories.ControllerFactory.create_light_controller")
    def test_get_light_controller(self, mock_create_controller):
        """Test de la fonction get_light_controller."""
        # Arrange
        mock_controller = Mock(spec=LightController)
        mock_create_controller.return_value = mock_controller

        # Act
        result = get_light_controller()

        # Assert
        assert result == mock_controller
        mock_create_controller.assert_called_once()

    @patch("domotix.factories.ControllerFactory.create_shutter_controller")
    def test_get_shutter_controller(self, mock_create_controller):
        """Test de la fonction get_shutter_controller."""
        # Arrange
        mock_controller = Mock(spec=ShutterController)
        mock_create_controller.return_value = mock_controller

        # Act
        result = get_shutter_controller()

        # Assert
        assert result == mock_controller
        mock_create_controller.assert_called_once()

    @patch("domotix.factories.ControllerFactory.create_sensor_controller")
    def test_get_sensor_controller(self, mock_create_controller):
        """Test de la fonction get_sensor_controller."""
        # Arrange
        mock_controller = Mock(spec=SensorController)
        mock_create_controller.return_value = mock_controller

        # Act
        result = get_sensor_controller()

        # Assert
        assert result == mock_controller
        mock_create_controller.assert_called_once()


class TestFactoryIntegration:
    """Tests d'intégration pour les factories."""

    def test_controller_factory_creates_working_controllers(self):
        """Test que les factories créent des contrôleurs fonctionnels."""
        # Note: Ce test nécessiterait une vraie base de données
        # Pour l'instant, on vérifie juste que les objets sont créés

        # Act & Assert - vérifier qu'aucune exception n'est levée
        try:
            device_controller = ControllerFactory.create_device_controller()
            light_controller = ControllerFactory.create_light_controller()
            shutter_controller = ControllerFactory.create_shutter_controller()
            sensor_controller = ControllerFactory.create_sensor_controller()

            # Vérifier les types
            assert isinstance(device_controller, DeviceController)
            assert isinstance(light_controller, LightController)
            assert isinstance(shutter_controller, ShutterController)
            assert isinstance(sensor_controller, SensorController)

        except Exception as e:
            pytest.fail(f"Factory integration failed: {e}")

    def test_repository_factory_creates_working_repositories(self):
        """Test que les factories créent des repositories fonctionnels."""
        # Note: Ce test nécessiterait une vraie base de données
        # Pour l'instant, on vérifie juste que les objets sont créés

        # Act & Assert - vérifier qu'aucune exception n'est levée
        try:
            device_repo = RepositoryFactory.create_device_repository()
            light_repo = RepositoryFactory.create_light_repository()
            shutter_repo = RepositoryFactory.create_shutter_repository()
            sensor_repo = RepositoryFactory.create_sensor_repository()

            # Vérifier les types
            assert isinstance(device_repo, DeviceRepository)
            assert isinstance(light_repo, LightRepository)
            assert isinstance(shutter_repo, ShutterRepository)
            assert isinstance(sensor_repo, SensorRepository)

        except Exception as e:
            pytest.fail(f"Repository factory integration failed: {e}")
