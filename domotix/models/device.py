"""
Home automation device models module.

This module contains the abstract Device class, which serves as the base for all
home automation devices in the system. It defines the common interface that all
devices must implement.

Classes:
    Device: Abstract base class for all home automation devices.

Example:
    This class cannot be instantiated directly:

    >>> from domotix.models import Device
    >>> device = Device("Test")  # Raises TypeError

    It must be inherited by concrete classes such as Light or Shutter.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from domotix.globals.enums import DeviceType


class Device(ABC):
    """Abstract base class for all home automation devices.

    This class defines the common interface that all devices
    must implement to work with the home automation system.

    Attributes:
        id (str): Unique identifier for the device.
        name (str): Friendly name for the device.
        state (dict): Current state of the device.
        location (Optional[str]): Location of the device.
    """

    def __init__(self, name: str, type: DeviceType, location: Optional[str] = None):
        """Initializes a new device.

        Args:
            name (str): Friendly name for the device.
            type (DeviceType): Type of the device.
            state (dict): Initial state of the device.
            location (Optional[str], optional): Location of the device.
            Default is None.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.device_type = type
        self.state: dict[str, Any] = {}
        self.location: Optional[str] = location

    def __str__(self) -> str:
        """String representation of the device.

        Returns:
            str: Textual representation of the device.
        """
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Technical representation of the device.

        Returns:
            str: Detailed technical representation of the device.
        """
        return (
            f"{self.__class__.__name__}(id={self.id}, name={self.name}, "
            f"location={self.location})"
        )

    @abstractmethod
    def get_state(self) -> dict:
        """Returns the current state of the device.

        This method must be implemented by all subclasses.

        Returns:
            dict: Current state of the device.
        """
        pass

    @abstractmethod
    def update_state(self, new_state: dict) -> bool:
        """Updates the state of the device.

        This method must be implemented by all subclasses.

        Args:
            new_state (dict): New state to apply.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        pass
