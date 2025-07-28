"""
Controller for managing sensors and measurement devices.

This module contains the SensorController which coordinates operations
on sensors using the Repository pattern
for data persistence.

Classes:
    SensorController: Controller for sensors and measurement devices
"""

from typing import List, Optional, Union, cast

from domotix.models.sensor import Sensor
from domotix.repositories.device_repository import DeviceRepository


class SensorController:
    """
    Controller for managing sensors and measurement devices.

    This controller uses dependency injection to receive
    a repository and does not depend on a singleton for persistence.

    Attributes:
        _repository: Repository for data persistence
    """

    def __init__(self, sensor_repository: DeviceRepository):
        """
        Initializes the controller with a repository.

        Args:
            sensor_repository: Repository for sensor data persistence
        """
        self._repository = sensor_repository

    def create_sensor(self, name: str, location: Optional[str] = None) -> str:
        """
        Creates a new sensor.

        Args:
            name: Sensor name
            location: Optional location

        Returns:
            str: ID of the created sensor
        """
        sensor = Sensor(name=name, location=location)
        saved_sensor = self._repository.save(sensor)
        return str(saved_sensor.id)

    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """
        Retrieves a sensor by its ID.

        Args:
            sensor_id: Sensor ID

        Returns:
            Optional[Sensor]: The sensor or None if not found
        """
        device = self._repository.find_by_id(sensor_id)
        if device and isinstance(device, Sensor):
            return cast(Sensor, device)
        return None

    def get_all_sensors(self) -> List[Sensor]:
        """
        Retrieves all sensors.

        Returns:
            List[Sensor]: List of all sensors
        """
        devices = self._repository.find_all()
        return [device for device in devices if isinstance(device, Sensor)]

    def update_value(self, sensor_id: str, value: Union[int, float]) -> bool:
        """
        Updates the value of a sensor.

        Args:
            sensor_id: ID of the sensor
            value: New value for the sensor

        Returns:
            bool: True if the operation was successful
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            sensor.update_value(value)
            return self._repository.update(sensor)
        return False

    def get_value(self, sensor_id: str) -> Optional[Union[int, float]]:
        """
        Retrieves the current value of a sensor.

        Args:
            sensor_id: ID of the sensor

        Returns:
            Optional[Union[int, float]]: Value of the sensor or None if not found
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            return sensor.value
        return None

    def get_reading_history(self, sensor_id: str, limit: int = 100) -> List[dict]:
        """
        Retrieves the historical readings of a sensor.

        Note: This method would require a specialized repository for history.
        For now, it returns an empty list.

        Args:
            sensor_id: ID of the sensor
            limit: Maximum number of readings to return

        Returns:
            List[dict]: List of historical readings
        """
        # TODO: Implement with a specialized SensorReadingRepository
        return []

    def reset_value(self, sensor_id: str) -> bool:
        """
        Resets the value of a sensor.

        Args:
            sensor_id: ID of the sensor

        Returns:
            bool: True if the operation was successful
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            sensor = cast(Sensor, sensor)  # Explicit type for MyPy
            sensor.reset_value()  # type: ignore[attr-defined]
            return self._repository.update(sensor)
        return False

    def is_active(self, sensor_id: str) -> bool:
        """
        Checks if a sensor is active (has a value).

        Args:
            sensor_id: ID of the sensor

        Returns:
            bool: True if the sensor is active
        """
        sensor = self.get_sensor(sensor_id)
        if sensor is not None:
            return sensor.value is not None
        return False

    def get_sensors_by_location(self, location: str) -> List[Sensor]:
        """
        Retrieves all sensors from a given location.

        Args:
            location: Location to search for

        Returns:
            List[Sensor]: List of sensors in that location
        """
        all_sensors = self.get_all_sensors()
        return [sensor for sensor in all_sensors if sensor.location == location]

    def delete_sensor(self, sensor_id: str) -> bool:
        """
        Deletes a sensor.

        Args:
            sensor_id: ID of the sensor

        Returns:
            bool: True if the deletion was successful
        """
        return self._repository.delete(sensor_id)
