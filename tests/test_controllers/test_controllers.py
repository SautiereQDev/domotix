# pylint: skip-file
# pylint: disable=import-error,no-member
"""
Tests for controllers.

This module contains all unit tests for controllers
that manage home automation devices.
"""

from unittest.mock import MagicMock, Mock

import pytest

from domotix.controllers import (
    DeviceController,
    LightController,
    SensorController,
    ShutterController,
)
from domotix.models import Light, Sensor, Shutter
from domotix.repositories.device_repository import DeviceRepository


@pytest.fixture
def mock_repository():
    """Create a mock repository for tests."""
    mock = Mock(spec=DeviceRepository)
    # Configure mocks to return True
    mock.update.return_value = True
    mock.delete.return_value = True

    # Configure save to return an object with an id
    saved_object = Mock()
    saved_object.id = "test-id"
    mock.save.return_value = saved_object

    return mock


@pytest.fixture
def sample_light():
    """Create a test light."""
    return Light("Test light", "Living Room")


@pytest.fixture
def sample_shutter():
    """Create a test shutter."""
    return Shutter("Test shutter", "Bedroom")


@pytest.fixture
def sample_sensor():
    """Create a test sensor."""
    return Sensor("Test sensor", "Garden")


class TestLightController:
    """Tests for the LightController class."""

    def test_create_light(self, mock_repository):
        """Test for creating a light."""
        # Arrange
        controller = LightController(mock_repository)

        # Act
        result = controller.create_light("Lampe test", "Salon")

        # Assert
        assert result == "test-id"
        mock_repository.save.assert_called_once()

        # Verify that the argument passed is indeed a Light
        call_args = mock_repository.save.call_args[0][0]
        assert isinstance(call_args, Light)
        assert call_args.name == "Lampe test"
        assert call_args.location == "Salon"

    def test_get_light_existing(self, mock_repository, sample_light):
        """Test for retrieving an existing light."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_light
        controller = LightController(mock_repository)

        # Act
        result = controller.get_light("test-id")

        # Assert
        assert result == sample_light
        mock_repository.find_by_id.assert_called_once_with("test-id")

    def test_get_light_non_existing(self, mock_repository):
        """Test for retrieving a non-existing light."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        controller = LightController(mock_repository)

        # Act
        result = controller.get_light("non-existent-id")

        # Assert
        assert result is None
        mock_repository.find_by_id.assert_called_once_with("non-existent-id")

    def test_get_light_wrong_type(self, mock_repository, sample_shutter):
        """Test for retrieval with an incorrect type."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_shutter
        controller = LightController(mock_repository)

        # Act
        result = controller.get_light("test-id")

        # Assert
        assert result is None

    def test_turn_on_success(self, mock_repository, sample_light):
        """Test for successful turn on."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_light
        controller = LightController(mock_repository)

        # Act
        result = controller.turn_on("test-id")

        # Assert
        assert result is True
        assert sample_light.is_on is True
        mock_repository.update.assert_called_once_with(sample_light)

    def test_turn_on_light_not_found(self, mock_repository):
        """Test for turning on with light not found."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        controller = LightController(mock_repository)

        # Act
        result = controller.turn_on("non-existent-id")

        # Assert
        assert result is False
        mock_repository.save.assert_not_called()

    def test_turn_off_success(self, mock_repository, sample_light):
        """Test for successful turn off."""
        # Arrange
        sample_light.turn_on()  # First turn on
        mock_repository.find_by_id.return_value = sample_light
        controller = LightController(mock_repository)

        # Act
        result = controller.turn_off("test-id")

        # Assert
        assert result is True
        assert sample_light.is_on is False
        mock_repository.update.assert_called_once_with(sample_light)

    def test_toggle_success(self, mock_repository, sample_light):
        """Test for successful toggle."""
        # Arrange
        initial_state = sample_light.is_on
        mock_repository.find_by_id.return_value = sample_light
        controller = LightController(mock_repository)

        # Act
        result = controller.toggle("test-id")

        # Assert
        assert result is True
        assert sample_light.is_on != initial_state
        mock_repository.update.assert_called_once_with(sample_light)

    def test_get_all_lights(self, mock_repository):
        """Test for retrieving all lights."""
        # Arrange
        light1 = Light("Lampe 1", "Salon")
        light2 = Light("Lampe 2", "Chambre")
        shutter = Shutter("Volet", "Salon")  # Should not be included

        mock_repository.find_all.return_value = [light1, light2, shutter]
        controller = LightController(mock_repository)

        # Act
        result = controller.get_all_lights()

        # Assert
        assert len(result) == 2
        assert light1 in result
        assert light2 in result
        assert shutter not in result

    def test_delete_light(self, mock_repository):
        """Test for deleting a light."""
        # Arrange
        mock_repository.delete.return_value = True
        controller = LightController(mock_repository)

        # Act
        result = controller.delete_light("test-id")

        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with("test-id")


class TestShutterController:
    """Tests for the ShutterController class."""

    def test_create_shutter(self, mock_repository):
        """Test for creating a shutter."""
        # Arrange
        controller = ShutterController(mock_repository)

        # Act
        result = controller.create_shutter("Volet test", "Chambre")

        # Assert
        assert result == "test-id"
        mock_repository.save.assert_called_once()

        # Verify that the argument passed is indeed a Shutter
        call_args = mock_repository.save.call_args[0][0]
        assert isinstance(call_args, Shutter)
        assert call_args.name == "Volet test"
        assert call_args.location == "Chambre"

    def test_open_success(self, mock_repository, sample_shutter):
        """Test for successful opening."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_shutter
        controller = ShutterController(mock_repository)

        # Act
        result = controller.open("test-id")

        # Assert
        assert result is True
        assert sample_shutter.is_open is True
        mock_repository.update.assert_called_once_with(sample_shutter)

    def test_close_success(self, mock_repository, sample_shutter):
        """Test for successful closing."""
        # Arrange
        sample_shutter.open()  # First open
        mock_repository.find_by_id.return_value = sample_shutter
        controller = ShutterController(mock_repository)

        # Act
        result = controller.close("test-id")

        # Assert
        assert result is True
        assert sample_shutter.is_open is False
        mock_repository.update.assert_called_once_with(sample_shutter)

    def test_set_position_success(self, mock_repository, sample_shutter):
        """Test for setting position."""
        # Arrange
        # Add the set_position method to the mock
        sample_shutter.set_position = MagicMock()
        mock_repository.find_by_id.return_value = sample_shutter
        controller = ShutterController(mock_repository)

        # Act
        result = controller.set_position("test-id", 50)

        # Assert
        assert result is True
        sample_shutter.set_position.assert_called_once_with(50)
        mock_repository.update.assert_called_once_with(sample_shutter)

    def test_get_position_success(self, mock_repository, sample_shutter):
        """Test for getting position."""
        # Arrange
        sample_shutter.position = 75
        mock_repository.find_by_id.return_value = sample_shutter
        controller = ShutterController(mock_repository)

        # Act
        result = controller.get_position("test-id")

        # Assert
        assert result == 75


class TestSensorController:
    """Tests for the SensorController class."""

    def test_create_sensor(self, mock_repository):
        """Test for creating a sensor."""
        # Arrange
        controller = SensorController(mock_repository)

        # Act
        result = controller.create_sensor("Capteur test", "Jardin")

        # Assert
        assert result == "test-id"
        mock_repository.save.assert_called_once()

        # Verify that the argument passed is indeed a Sensor
        call_args = mock_repository.save.call_args[0][0]
        assert isinstance(call_args, Sensor)
        assert call_args.name == "Capteur test"
        assert call_args.location == "Jardin"

    def test_update_value_success(self, mock_repository, sample_sensor):
        """Test for successful value update."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_sensor
        controller = SensorController(mock_repository)

        # Act
        result = controller.update_value("test-id", 22.5)

        # Assert
        assert result is True
        assert abs(sample_sensor.value - 22.5) < 1e-9
        mock_repository.update.assert_called_once_with(sample_sensor)

    def test_get_value_success(self, mock_repository, sample_sensor):
        """Test for getting value."""
        # Arrange
        sample_sensor.update_value(18.7)
        mock_repository.find_by_id.return_value = sample_sensor
        controller = SensorController(mock_repository)

        # Act
        result = controller.get_value("test-id")

        # Assert
        assert abs(result - 18.7) < 1e-9

    def test_is_active_with_value(self, mock_repository, sample_sensor):
        """Test for activity check with value."""
        # Arrange
        sample_sensor.update_value(20.0)
        mock_repository.find_by_id.return_value = sample_sensor
        controller = SensorController(mock_repository)

        # Act
        result = controller.is_active("test-id")

        # Assert
        assert result is True

    def test_is_active_without_value(self, mock_repository, sample_sensor):
        """Test for activity check without value."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_sensor
        controller = SensorController(mock_repository)

        # Act
        result = controller.is_active("test-id")

        # Assert
        assert result is False

    def test_reset_value_success(self, mock_repository, sample_sensor):
        """Test for resetting value."""
        # Arrange
        sample_sensor.update_value(25.0)
        mock_repository.find_by_id.return_value = sample_sensor
        controller = SensorController(mock_repository)

        # Act
        result = controller.reset_value("test-id")

        # Assert
        assert result is True
        assert sample_sensor.value is None
        mock_repository.update.assert_called_once_with(sample_sensor)

    def test_get_sensors_by_location(self, mock_repository):
        """Test for getting sensors by location."""
        # Arrange
        sensor1 = Sensor("Capteur 1", "Salon")
        sensor2 = Sensor("Capteur 2", "Salon")
        sensor3 = Sensor("Capteur 3", "Chambre")

        mock_repository.find_all.return_value = [sensor1, sensor2, sensor3]
        controller = SensorController(mock_repository)

        # Act
        result = controller.get_sensors_by_location("Salon")

        # Assert
        assert len(result) == 2
        assert sensor1 in result
        assert sensor2 in result
        assert sensor3 not in result


class TestDeviceController:
    """Tests for the DeviceController class."""

    def test_get_devices_summary(self, mock_repository):
        """Test for getting device summary."""
        # Arrange
        light = Light("Lampe", "Salon")
        shutter = Shutter("Volet", "Chambre")
        sensor1 = Sensor("Capteur 1", "Jardin")
        sensor2 = Sensor("Capteur 2", "Salon")

        mock_repository.find_all.return_value = [light, shutter, sensor1, sensor2]
        controller = DeviceController(mock_repository)

        # Act
        result = controller.get_devices_summary()

        # Assert
        assert result["lights"] == 1
        assert result["shutters"] == 1
        assert result["sensors"] == 2
        assert result["total"] == 4

    def test_get_locations(self, mock_repository):
        """Test for getting locations."""
        # Arrange
        light = Light("Lampe", "Salon")
        shutter = Shutter("Volet", "Chambre")
        sensor = Sensor("Capteur", "Salon")  # Same location as the lamp

        mock_repository.find_all.return_value = [light, shutter, sensor]
        controller = DeviceController(mock_repository)

        # Act
        result = controller.get_locations()

        # Assert
        assert "Salon" in result
        assert "Chambre" in result
        assert len(result) == 2  # No duplicates

    def test_search_devices(self, mock_repository):
        """Test for device search."""
        # Arrange
        light = Light("Lampe salon", "Salon")
        shutter = Shutter("Volet chambre", "Chambre")
        sensor = Sensor("Capteur salon", "Salon")

        mock_repository.find_all.return_value = [light, shutter, sensor]
        controller = DeviceController(mock_repository)

        # Act
        result = controller.search_devices("salon")

        # Assert
        assert len(result) == 2  # Lampe and capteur contain "salon"
        assert light in result
        assert sensor in result
        assert shutter not in result

    def test_bulk_operation_turn_on(self, mock_repository):
        """Test for bulk operation to turn on."""
        # Arrange
        light1 = Light("Lampe 1", "Salon")
        light2 = Light("Lampe 2", "Chambre")

        def mock_find_by_id(device_id):
            if device_id == "light1-id":
                return light1
            elif device_id == "light2-id":
                return light2
            return None

        mock_repository.find_by_id.side_effect = mock_find_by_id
        controller = DeviceController(mock_repository)

        # Act
        result = controller.bulk_operation(["light1-id", "light2-id"], "turn_on")

        # Assert
        assert result["light1-id"] is True
        assert result["light2-id"] is True
        assert light1.is_on is True
        assert light2.is_on is True
        assert mock_repository.update.call_count == 2
