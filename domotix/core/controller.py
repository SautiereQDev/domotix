"""
Main controller module for the home automation system.

This module contains the HomeAutomationController class, which serves as the main
entry point for interacting with the home automation system. It uses
StateManager to manage devices.

Classes:
    HomeAutomationController: Main controller for the home automation system

Example:
    >>> from domotix.core import HomeAutomationController
    >>> from domotix.models import Light
    >>>
    >>> controller = HomeAutomationController()
    >>> light = Light("Living Room Lamp", "Living Room")
    >>> device_id = controller.register_device(light)
    >>> controller.turn_on(device_id)
    >>> print(controller.get_status(device_id))
    ON
"""

from typing import Dict, Optional

from ..models.device import Device
from .state_manager import StateManager


class HomeAutomationController:
    """
    Main controller for the home automation system.

    This class acts as a facade to interact with the home automation system.
    It uses the StateManager to manage the state of devices.

    Attributes:
        _state_manager: Instance of the StateManager singleton

    Example:
        >>> controller = HomeAutomationController()
        >>> light = Light("Test Lamp", "Test")
        >>> device_id = controller.register_device(light)
        >>> controller.turn_on(device_id)
        >>> assert controller.get_status(device_id) == "ON"
    """

    def __init__(self) -> None:
        """
        Initializes the controller.

        Retrieves the singleton instance of the StateManager.
        """
        self._state_manager = StateManager()

    def turn_on(self, device_id: str) -> bool:
        """
        Turns on a device.

        Args:
            device_id: Identifier of the device to turn on

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            device = self._state_manager.get_device(device_id)
            if hasattr(device, "turn_on"):
                device.turn_on()
                return True
            return False
        except KeyError:
            return False

    def turn_off(self, device_id: str) -> bool:
        """
        Turns off a device.

        Args:
            device_id: Identifier of the device to turn off

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            device = self._state_manager.get_device(device_id)
            if hasattr(device, "turn_off"):
                device.turn_off()
                return True
            return False
        except KeyError:
            return False

    def get_status(self, device_id: str) -> Optional[str]:
        """
        Retrieves the status of a device.

        Args:
            device_id: Identifier of the device

        Returns:
            Optional[str]: Status of the device or None if not found
        """
        try:
            device = self._state_manager.get_device(device_id)
            state = device.get_state()
            # Convert the state to string for display
            if hasattr(device, "is_on"):
                return "ON" if device.is_on else "OFF"
            elif hasattr(device, "position"):
                return f"Position: {device.position}%"
            else:
                return str(state)
        except KeyError:
            return None

    def register_device(self, device) -> str:
        """
        Registers a new device.

        Args:
            device: Instance of Device to register

        Returns:
            str: Unique identifier of the registered device
        """
        return self._state_manager.register_device(device)

    def get_all_devices(self) -> Dict[str, Device]:
        """
        Retrieves all devices.

        Returns:
            Dict[str, Device]: Dictionary of all devices
        """
        return self._state_manager.get_devices()

    def remove_device(self, device_id: str) -> bool:
        """
        Removes a device.

        Args:
            device_id: Identifier of the device to remove

        Returns:
            bool: True if the removal was successful, False otherwise
        """
        return self._state_manager.unregister_device(device_id)
