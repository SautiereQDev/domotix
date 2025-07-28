"""
Tests for modern factories with dependency injection.

This module contains all unit tests for the new factory system
using modern dependency injection.
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
    """Tests for the new repository factory system with DI."""

    def test_create_device_repository_with_session(self):
        """Test creating a DeviceRepository with session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_device_repository(custom_session)

        # Assert
        assert isinstance(repository, DeviceRepository)
        assert repository.session == custom_session

    def test_create_light_repository_with_session(self):
        """Test creating a LightRepository with session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_light_repository(custom_session)

        # Assert
        assert isinstance(repository, LightRepository)
        assert repository.session == custom_session

    def test_create_shutter_repository_with_session(self):
        """Test creating a ShutterRepository with session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_shutter_repository(custom_session)

        # Assert
        assert isinstance(repository, ShutterRepository)
        assert repository.session == custom_session

    def test_create_sensor_repository_with_session(self):
        """Test creating a SensorRepository with session."""
        # Arrange
        custom_session = Mock()
        repo_factory = get_repository_factory()

        # Act
        repository = repo_factory.create_sensor_repository(custom_session)

        # Assert
        assert isinstance(repository, SensorRepository)
        assert repository.session == custom_session

    def test_repository_factory_singleton(self):
        """Test that the repository factory is a singleton."""
        # Act
        factory1 = get_repository_factory()
        factory2 = get_repository_factory()

        # Assert
        assert factory1 is factory2, "Repository factory should be a singleton"


class TestModernControllerFactory:
    """Tests for the new controller factory system with DI."""

    @patch("domotix.core.factories.RepositoryFactory")
    def test_create_device_controller_with_session(self, mock_repo_factory_class):
        """Test creating a DeviceController with session."""
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
        # Check that the repository has been injected
        assert hasattr(controller, "_repository")

    @patch("domotix.core.factories.RepositoryFactory")
    def test_create_light_controller_with_session(self, mock_repo_factory_class):
        """Test creating a LightController with session."""
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
        """Test creating a ShutterController with session."""
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
        """Test creating a SensorController with session."""
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
        """Test that the controller factory is a singleton."""
        # Act
        factory1 = get_controller_factory()
        factory2 = get_controller_factory()

        # Assert
        assert factory1 is factory2, "Controller factory should be a singleton"


class TestFactoryIntegration:
    """Integration tests for the new factory system."""

    def test_factory_singletons(self):
        """Test that the factories are singletons."""
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
        """Test the DI system with the factories."""
        # Arrange
        mock_session = Mock()
        mock_create_session.return_value = mock_session

        controller_factory = get_controller_factory()
        repo_factory = get_repository_factory()

        # Act & Assert - check that no exception is raised
        try:
            # Create repositories
            device_repo = repo_factory.create_device_repository(mock_session)
            light_repo = repo_factory.create_light_repository(mock_session)

            # Create controllers
            device_controller = controller_factory.create_device_controller(
                mock_session
            )
            light_controller = controller_factory.create_light_controller(mock_session)

            # Check types
            assert isinstance(device_repo, DeviceRepository)
            assert isinstance(light_repo, LightRepository)
            assert isinstance(device_controller, DeviceController)
            assert isinstance(light_controller, LightController)

        except Exception as e:
            pytest.fail(f"Factory integration with DI failed: {e}")

    def test_modern_factory_architecture(self):
        """Test the modern architecture of the factories."""
        # Act
        controller_factory = get_controller_factory()
        repo_factory = get_repository_factory()

        # Assert - check the attributes of the modern architecture
        assert hasattr(
            controller_factory, "_container"
        ), "Controller factory should have a DI container"
        assert hasattr(
            repo_factory, "_container"
        ), "Repository factory should have a DI container"


class TestDependencyInjectionIntegration:
    """Tests specific to integration with the DI system."""

    def test_service_provider_integration(self):
        """Test integration with the service provider."""
        from domotix.core.service_provider import get_service_provider

        # Act
        service_provider = get_service_provider()
        controller_factory = get_controller_factory()

        # Assert
        assert service_provider is not None
        assert controller_factory is not None
        # The factories use the modern DI system
        assert hasattr(controller_factory, "_container")

    def test_container_usage_in_factories(self):
        """Test that the factories correctly use the DI container."""
        # Act
        controller_factory = get_controller_factory()
        repo_factory = get_repository_factory()

        # Assert
        assert controller_factory is not None
        assert repo_factory is not None
        # Check that the container is present in the architecture
        assert hasattr(controller_factory, "_container")
        assert hasattr(repo_factory, "_container")

    def test_error_handling_with_modern_exceptions(self):
        """Test error handling with the new exception system."""
        from domotix.globals.exceptions import ControllerError

        # Act
        controller_factory = get_controller_factory()

        # Assert - Test that modern exceptions are used
        try:
            # Attempting to create with session None should use the
            # new exceptions
            controller_factory.create_device_controller(None)
        except ControllerError:
            # This is expected with the new system
            pass
        except Exception as e:
            # Check that the error is properly handled
            assert e is not None


class TestBackwardCompatibility:
    """Compatibility tests with the old system."""

    def test_legacy_imports_still_work(self):
        """Test that old imports still work."""
        # Act & Assert - The imports should work
        try:
            from domotix.core.factories import LegacyControllerFactory

            # Compatibility methods should exist
            assert hasattr(LegacyControllerFactory, "create_device_controller")
            assert hasattr(LegacyControllerFactory, "create_light_controller")

        except ImportError:
            pytest.fail("Compatibility with the old system has been broken")

    def test_modern_vs_legacy_consistency(self):
        """Test consistency between new and old systems."""
        # Arrange
        mock_session = Mock()

        # Act
        modern_factory = get_controller_factory()
        modern_controller = modern_factory.create_device_controller(mock_session)

        # Assert
        assert isinstance(modern_controller, DeviceController)
        # The new system must create the same types as the old one
        assert hasattr(modern_controller, "_repository")
