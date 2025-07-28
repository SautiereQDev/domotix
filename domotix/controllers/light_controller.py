"""
Controller for managing lighting devices.

This module contains the LightController which coordinates operations
on lighting devices using the Repository pattern
for data persistence.

Classes:
    LightController: Controller for lights and lighting devices
"""

from typing import List, Optional

from domotix.models.light import Light
from domotix.repositories.device_repository import DeviceRepository


class LightController:
    """
    Controller for managing lighting devices.

    This controller uses dependency injection to receive
    a repository and does not depend on a singleton for persistence.

    Attributes:
        _repository: Repository for data persistence
    """

    def __init__(self, light_repository: DeviceRepository):
        """
        Initializes the controller with a repository.

        Args:
            light_repository: Repository for light data persistence
        """
        self._repository = light_repository

    def create_light(self, name: str, location: Optional[str] = None) -> str:
        """
        Creates a new light.

        Args:
            name: Light name
            location: Optional location

        Returns:
            str: ID of the created light
        """
        light = Light(name=name, location=location)
        saved_light = self._repository.save(light)
        return str(saved_light.id)

    def get_light(self, light_id: str) -> Optional[Light]:
        """
        Retrieves a light by its ID.

        Args:
            light_id: Light ID

        Returns:
            Optional[Light]: The light or None if not found
        """
        device = self._repository.find_by_id(light_id)
        if device and isinstance(device, Light):
            return device
        return None

    def get_all_lights(self) -> List[Light]:
        """
        Retrieves all lights.

        Returns:
            List[Light]: List of all lights
        """
        devices = self._repository.find_all()
        return [device for device in devices if isinstance(device, Light)]

    def turn_on(self, light_id: str) -> bool:
        """
        Turns on a light.

        Args:
            light_id: Light ID

        Returns:
            bool: True if the operation was successful
        """
        light = self.get_light(light_id)
        if light:
            light.turn_on()
            return self._repository.update(light)
        return False

    def turn_off(self, light_id: str) -> bool:
        """
        Turns off a light.

        Args:
            light_id: Light ID

        Returns:
            bool: True if the operation was successful
        """
        light = self.get_light(light_id)
        if light:
            light.turn_off()
            return self._repository.update(light)
        return False

    def toggle(self, light_id: str) -> bool:
        """
        Toggles the state of a light.

        Args:
            light_id: Light ID

        Returns:
            bool: True if the operation was successful
        """
        light = self.get_light(light_id)
        if light:
            light.toggle()
            return self._repository.update(light)
        return False

    def delete_light(self, light_id: str) -> bool:
        """
        Deletes a light.

        Args:
            light_id: Light ID

        Returns:
            bool: True if the deletion was successful
        """
        return self._repository.delete(light_id)
