"""
Integration tests for the CLI interface with persistence.

This module tests integration between CLI commands and
the newly created persistence layer.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest

from domotix.cli.device_cmds import (  # type: ignore[attr-defined]
    DeviceCreateCommands,
    DeviceListCommands,
    DeviceStateCommands,
)
from domotix.models import Light, Sensor, Shutter


class TestDeviceCreateCommandsIntegration:
    """Integration tests for creation commands."""

    def test_create_light_with_persistence(self):
        """Test creating a light with persistence."""
        service_provider_path = "domotix.cli.device_cmds.scoped_service_provider"
        with patch(service_provider_path) as mock_scoped_provider:
            # Mock service provider and controller
            mock_provider = Mock()
            mock_controller = Mock()
            mock_controller.create_light.return_value = 1
            mock_controller.get_light.return_value = Light("Test Light", "Living Room")
            mock_provider.get_light_controller.return_value = mock_controller

            # Mock context manager
            mock_context = mock_scoped_provider.create_scope.return_value
            mock_context.__enter__.return_value = mock_provider
            mock_context.__exit__.return_value = None

            # Test creation
            DeviceCreateCommands.create_light("Test Light", "Living Room")

            # Verify calls
            mock_scoped_provider.create_scope.assert_called_once()
            mock_provider.get_light_controller.assert_called_once()
            mock_controller.create_light.assert_called_once_with(
                "Test Light", "Living Room"
            )
            mock_controller.get_light.assert_called_once_with(1)

    def test_create_shutter_with_persistence(self):
        """Test creating a shutter with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.create_shutter.return_value = 1
            mock_controller.get_shutter.return_value = Shutter(
                "Test Shutter", "Bedroom"
            )
            mock_factory.create_shutter_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test creation
                DeviceCreateCommands.create_shutter("Test Shutter", "Bedroom")

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_shutter_controller.assert_called_once()
                mock_controller.create_shutter.assert_called_once_with(
                    "Test Shutter", "Bedroom"
                )
                mock_controller.get_shutter.assert_called_once_with(1)

    def test_create_sensor_with_persistence(self):
        """Test creating a sensor with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.create_sensor.return_value = 1
            mock_controller.get_sensor.return_value = Sensor(
                "Test Sensor", "Living Room"
            )
            mock_factory.create_sensor_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test creation
                DeviceCreateCommands.create_sensor("Test Sensor", "Living Room")

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_sensor_controller.assert_called_once()
                mock_controller.create_sensor.assert_called_once_with(
                    "Test Sensor", "Living Room"
                )
                mock_controller.get_sensor.assert_called_once_with(1)


class TestDeviceListCommandsIntegration:
    """Integration tests for list commands."""

    def test_list_all_devices_with_persistence(self):
        """Test listing all devices with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Create test devices
            light = Light("Living Room Light", "Living Room")
            light.id = 1
            shutter = Shutter("Bedroom Shutter", "Bedroom")
            shutter.id = 2
            sensor = Sensor("Temperature Sensor", "Living Room")
            sensor.id = 3

            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_all_devices.return_value = [light, shutter, sensor]
            mock_factory.create_device_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test listing
                DeviceListCommands.list_all_devices()

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_device_controller.assert_called_once()
                mock_controller.get_all_devices.assert_called_once()

    def test_list_lights_with_persistence(self):
        """Test listing lights with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Create test lights
            light1 = Light("Living Room Light", "Living Room")
            light1.id = 1
            light1.is_on = True
            light2 = Light("Bedroom Light", "Bedroom")
            light2.id = 2
            light2.is_on = False

            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_all_lights.return_value = [light1, light2]
            mock_factory.create_light_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test listing
                DeviceListCommands.list_lights()

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_light_controller.assert_called_once()
                mock_controller.get_all_lights.assert_called_once()

    def test_show_device_with_persistence(self):
        """Test showing a device with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Create a test device
            light = Light("Test Light", "Living Room")
            light.id = 1
            light.is_on = True

            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_device.return_value = light
            mock_factory.create_device_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test showing
                DeviceListCommands.show_device(1)

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_device_controller.assert_called_once()
                mock_controller.get_device.assert_called_once_with(1)


class TestDeviceStateCommandsIntegration:
    """Integration tests for state commands."""

    def test_turn_on_light_with_persistence(self):
        """Test turning on a light with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.turn_on.return_value = True
            mock_factory.create_light_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test turning on
                DeviceStateCommands.turn_on_light(1)

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_light_controller.assert_called_once()
                mock_controller.turn_on.assert_called_once_with(1)

    def test_open_shutter_with_persistence(self):
        """Test opening a shutter with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.open.return_value = True
            mock_factory.create_shutter_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test opening
                DeviceStateCommands.open_shutter(1)

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_shutter_controller.assert_called_once()
                mock_controller.open.assert_called_once_with(1)

    def test_update_sensor_value_with_persistence(self):
        """Test updating sensor value with persistence."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock factory and controller
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.update_value.return_value = True
            mock_factory.create_sensor_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Test updating
                DeviceStateCommands.update_sensor_value(1, 25.5)

                # Verify calls
                mock_get_factory.assert_called_once()
                mock_factory.create_sensor_controller.assert_called_once()
                mock_controller.update_value.assert_called_once_with(1, 25.5)


class TestCLIPersistenceErrorHandling:
    """Error handling tests for CLI-persistence integration."""

    def test_create_light_failure(self):
        """Test handling light creation failure."""
        # Mock service provider for create_light using
        # dependency injection
        with patch("domotix.cli.device_cmds.scoped_service_provider") as mock_provider:
            # Configure mock for service provider
            mock_scope = Mock()
            mock_controller = Mock()
            mock_controller.create_light.return_value = None  # Simulate failure
            mock_scope.get_light_controller.return_value = mock_controller
            mock_provider.create_scope.return_value.__enter__.return_value = mock_scope
            mock_provider.create_scope.return_value.__exit__.return_value = None

            # Capture output
            with patch("builtins.print") as mock_print:
                DeviceCreateCommands.create_light("Test Light", "Living Room")

                # Verify an error message is displayed
                mock_print.assert_called()
                # Check for an error message containing "Error"
                error_printed = any(
                    "Error" in str(call) for call in mock_print.call_args_list
                )
                assert error_printed

    def test_device_not_found(self):
        """Test handling device not found."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock factory and controller that does not find the device
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_device.return_value = None
            mock_factory.create_device_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Capture output
                with patch("builtins.print") as mock_print:
                    DeviceListCommands.show_device("999")

                    # Verify an error message is displayed
                    mock_print.assert_called()
                    # Check for an error message containing "not found"
                    error_printed = any(
                        "not found" in str(call) for call in mock_print.call_args_list
                    )
                    assert error_printed

    def test_operation_failure(self):
        """Test handling operation failure."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with (
            patch(factory_path) as mock_get_factory,
            patch("builtins.print") as mock_print,
        ):
            # Mock factory and controller that fails the operation
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.turn_on.return_value = False
            mock_factory.create_light_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Create and run command
            cmd = DeviceStateCommands()
            cmd.turn_on_light("device_123")

            # Verify error message was printed
            # Check for failure message in print calls
            failure_msg = "Failed to turn on light"
            error_printed = any(
                failure_msg in str(call) for call in mock_print.call_args_list
            )
            assert error_printed


class TestCLISessionManagement:
    """Session management tests for the CLI."""

    def test_session_creation_and_cleanup(self):
        """Test session creation and cleanup."""
        with patch("domotix.cli.device_cmds.create_session") as mock_create_session:
            mock_session = Mock()
            mock_create_session.return_value = mock_session

            with patch(
                "domotix.cli.device_cmds.get_controller_factory"
            ) as mock_factory:
                mock_controller = Mock()
                mock_controller.get_all_devices.return_value = []
                mock_factory.create_device_controller.return_value = mock_controller

                # Test a command
                DeviceListCommands.list_all_devices()

                # Verify session is created
                mock_create_session.assert_called_once()

                # Verify session is closed
                mock_session.close.assert_called_once()

    def test_multiple_commands_use_separate_sessions(self):
        """Test multiple commands use separate sessions."""
        with patch("domotix.cli.device_cmds.create_session") as mock_create_session:
            mock_session1 = Mock()
            mock_session2 = Mock()
            mock_create_session.side_effect = [mock_session1, mock_session2]

            with patch(
                "domotix.cli.device_cmds.get_controller_factory"
            ) as mock_factory:
                mock_controller = Mock()
                mock_controller.get_all_devices.return_value = []
                mock_factory.create_device_controller.return_value = mock_controller

                # Execute two commands
                DeviceListCommands.list_all_devices()
                DeviceListCommands.list_all_devices()

                # Verify two sessions are created
                assert mock_create_session.call_count == 2

                # Verify both sessions are closed
                mock_session1.close.assert_called_once()
                mock_session2.close.assert_called_once()


class TestCLIRealDatabaseIntegration:
    """Integration tests with a real database."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for tests."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        # Patch configuration to use our temporary DB
        with patch("domotix.core.database.DATABASE_URL", f"sqlite:///{db_path}"):
            from domotix.core.database import Base, engine

            Base.metadata.create_all(engine)
            yield db_path

        # Cleanup
        import os

        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_full_lifecycle_with_real_db(self, temp_db):
        """Test full lifecycle with a real database."""
        # Mock service provider to avoid DI issues in tests
        with patch("domotix.cli.device_cmds.scoped_service_provider") as mock_provider:
            # Configure mock for service provider
            mock_scope = Mock()
            mock_controller = Mock()
            mock_light = Mock()
            mock_light.name = "Real Lamp"
            mock_controller.create_light.return_value = "1"
            mock_controller.get_light.return_value = mock_light
            mock_scope.get_light_controller.return_value = mock_controller
            mock_provider.create_scope.return_value.__enter__.return_value = mock_scope
            mock_provider.create_scope.return_value.__exit__.return_value = None

            # Mock for list commands
            factory_path = "domotix.cli.device_cmds.get_controller_factory"
            with patch(factory_path) as mock_get_factory:
                mock_factory = Mock()
                mock_list_controller = Mock()
                mock_list_controller.get_all_lights.return_value = [mock_light]
                mock_factory.create_light_controller.return_value = mock_list_controller
                mock_get_factory.return_value = mock_factory

                with patch("domotix.cli.device_cmds.create_session"):
                    # Create a light
                    DeviceCreateCommands.create_light("Real Lamp", "Living Room")

                    # Verify it appears in the list
                    with patch("builtins.print") as mock_print:
                        DeviceListCommands.list_lights()

                        # Verify there is output
                        assert mock_print.called

                        # Verify the lamp's name appears in the output
                        output = " ".join(
                            str(call) for call in mock_print.call_args_list
                        )
                        assert "Real Lamp" in output
