"""
Sensor model module for sensors and measurement devices.

This module contains the Sensor class, which represents a sensor or measurement device
in the home automation system. It inherits from Device and adds features
specific to value collection and storage.

Classes:
    Sensor: Model for sensors (temperature, humidity, light, etc.)

Example:
    >>> from domotix.models import Sensor
    >>> sensor = Sensor("Living Room Temperature Sensor", "Living Room")
    >>> sensor.update_value(22.5)
    >>> print(sensor.value)
    22.5
    >>> print(sensor.get_status())
    VALUE_22.5
"""

import math
from typing import Optional, Union

from ..globals.enums import DeviceType
from ..globals.exceptions import ErrorCode, ErrorContext, ValidationError
from .device import Device


class Sensor(Device):
    """
    Model for sensors and measurement devices.

    This class represents all types of sensors (temperature, humidity,
    light, motion, etc.) that collect and store numerical values
    in the home automation system.

    Attributes:
        value (Optional[Union[int, float]]): Current value of the sensor
        name (str): Descriptive name inherited from Device
        id (str): Unique identifier inherited from Device

    Example:
        >>> sensor = Sensor("Outdoor Thermometer", "Garden")
        >>> sensor.update_value(-5.2)
        >>> assert sensor.value == -5.2
        >>> print(sensor.get_status())
        VALUE_-5.2
    """

    def __init__(self, name: str, location: Optional[str] = None) -> None:
        """
        Initializes a new sensor.

        Args:
            name: Descriptive name of the sensor (e.g.,
            "Living Room Temperature Sensor", "Entrance Motion Detector",
            "Garden Light Meter")
            location: Location of the sensor (e.g., "Living Room", "Entrance", "Garden")
        """
        super().__init__(name, DeviceType.SENSOR, location)
        self.value: Optional[Union[int, float]] = None  # No initial value

    def update_value(self, value: Union[int, float]) -> None:
        """
        Updates the sensor's value.

        Args:
            value: New numerical value of the sensor
                  (temperature in °C, humidity in %, light in lux, etc.)

        Raises:
            ValidationError: If the value is not numerical or not valid

        Example:
            >>> sensor = Sensor("Test")
            >>> sensor.update_value(42.7)
            >>> assert sensor.value == 42.7
            >>> sensor.update_value("invalid")  # Raises ValidationError
        """
        if not isinstance(value, (int, float)):
            context = ErrorContext(
                module=__name__,
                function="update_value",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "value_type": type(value).__name__,
                    "value": str(value),
                    "expected_types": ["int", "float"],
                },
            )
            raise ValidationError(
                message=(
                    f"The value of the sensor '{self.name}' must be numerical, "
                    f"received: {type(value).__name__}"
                ),
                error_code=ErrorCode.VALIDATION_INVALID_TYPE,
                context=context,
            )

        # Special value validation
        if math.isnan(value):  # NaN check
            context = ErrorContext(
                module=__name__,
                function="update_value",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "value": str(value),
                    "issue": "NaN_value",
                },
            )
            raise ValidationError(
                message=f"Invalid value (NaN) for the sensor '{self.name}'",
                error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
                context=context,
            )

        # Infinity validation
        if not -float("inf") < value < float("inf"):
            context = ErrorContext(
                module=__name__,
                function="update_value",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "value": str(value),
                    "issue": "infinite_value",
                },
            )
            raise ValidationError(
                message=f"Unauthorized infinite value for the sensor '{self.name}'",
                error_code=ErrorCode.VALIDATION_OUT_OF_RANGE,
                context=context,
            )

        # Assign the value after validation
        self.value = value

    def validate_range(self, min_value: float, max_value: float) -> None:
        """
        Validates that the current value is within the specified range.

        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Raises:
            ValidationError: If the value is out of the specified range

        Example:
            >>> sensor = Sensor("Thermometer")
            >>> sensor.update_value(25.0)
            >>> sensor.validate_range(-50, 100)  # OK
            >>> sensor.validate_range(30, 40)    # Raises ValidationError
        """
        if self.value is None:
            context = ErrorContext(
                module=__name__,
                function="validate_range",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "min_value": min_value,
                    "max_value": max_value,
                },
            )
            raise ValidationError(
                message=(f"Cannot validate range for '{self.name}': " "no value set"),
                error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
                context=context,
            )

        if not min_value <= self.value <= max_value:
            context = ErrorContext(
                module=__name__,
                function="validate_range",
                user_data={
                    "device_id": self.id,
                    "device_name": self.name,
                    "current_value": self.value,
                    "min_value": min_value,
                    "max_value": max_value,
                },
            )
            raise ValidationError(
                message=(
                    f"Value {self.value} of the sensor '{self.name}' "
                    f"out of range [{min_value}, {max_value}]"
                ),
                error_code=ErrorCode.VALIDATION_OUT_OF_RANGE,
                context=context,
            )

    def is_value_valid(self) -> bool:
        """
        Checks if the current value is valid.

        Returns:
            bool: True if the value is set and valid, False otherwise

        Example:
            >>> sensor = Sensor("Test")
            >>> sensor.is_value_valid()
            False
            >>> sensor.update_value(42.0)
            >>> sensor.is_value_valid()
            True
        """
        return (
            self.value is not None
            and isinstance(self.value, (int, float))
            and not math.isnan(self.value)  # NaN check
            and -float("inf") < self.value < float("inf")  # Infinity check
        )

    def get_status(self) -> str:
        """
        Returns the current status of the sensor.

        Returns:
            str: "VALUE_X" where X is the current value of the sensor
                "NO_VALUE" if no value has been set

        Example:
            >>> sensor = Sensor("Test")
            >>> print(sensor.get_status())
            NO_VALUE
            >>> sensor.update_value(23.4)
            >>> print(sensor.get_status())
            VALUE_23.4
        """
        return f"VALUE_{self.value}" if self.value is not None else "NO_VALUE"

    def get_state(self) -> dict:
        """
        Returns the current state of the sensor as a dictionary.

        Returns:
            dict: Dictionary containing the complete state of the sensor
                 with keys 'value' and 'has_value'

        Example:
            >>> sensor = Sensor("Test")
            >>> print(sensor.get_state())
            {'value': None, 'has_value': False}
            >>> sensor.update_value(25.3)
            >>> print(sensor.get_state())
            {'value': 25.3, 'has_value': True}
        """
        return {"value": self.value, "has_value": self.value is not None}

    def update_state(self, new_state: dict) -> bool:
        """
        Updates the sensor's state from a dictionary.

        Args:
            new_state: Dictionary containing the new state
                      must contain the key 'value'

        Returns:
            bool: True if the update was successful, False otherwise

        Example:
            >>> sensor = Sensor("Test")
            >>> sensor.update_state({'value': 30.5})
            True
            >>> print(sensor.value)
            30.5
            >>> sensor.update_state({'invalid': 'data'})
            False
        """
        try:
            if "value" in new_state:
                if new_state["value"] is None:
                    self.value = None
                    return True
                elif isinstance(new_state["value"], (int, float)):
                    self.value = new_state["value"]
                    return True
                else:
                    return False
            return False
        except Exception:
            return False

    def has_value(self) -> bool:
        """
        Checks if the sensor has a defined value.

        Returns:
            bool: True if a value has been set, False otherwise

        Example:
            >>> sensor = Sensor("Test")
            >>> print(sensor.has_value())
            False
            >>> sensor.update_value(0)
            >>> print(sensor.has_value())
            True
        """
        return self.value is not None

    def reset(self) -> None:
        """
        Resets the sensor (removes the current value).

        Useful for resetting a faulty sensor or for
        sensors with discrete events.

        Example:
            >>> sensor = Sensor("Test")
            >>> sensor.update_value(100)
            >>> sensor.reset()
            >>> assert sensor.value is None
        """
        self.value = None

    def reset_value(self) -> None:
        """
        Alias for reset() - resets the sensor.

        This method is an alias for reset() for compatibility
        with the interface expected by controllers.

        Example:
            >>> sensor = Sensor("Test")
            >>> sensor.update_value(50)
            >>> sensor.reset_value()
            >>> assert sensor.value is None
        """
        self.reset()
