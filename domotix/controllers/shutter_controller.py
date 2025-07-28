"""
Controller for managing shutters and blinds.

This module contains the ShutterController which coordinates operations
on shutters and blinds using the Repository pattern
for data persistence.

Classes:
    ShutterController: Controller for shutters and blinds
"""

from typing import List, Optional

from domotix.models.shutter import Shutter
from domotix.repositories.device_repository import DeviceRepository


class ShutterController:
    """
    Controller for managing shutters and blinds.

    This controller uses dependency injection to receive
    a repository and does not depend on a singleton for persistence.

    Attributes:
        _repository: Repository for data persistence
    """

    def __init__(self, shutter_repository: DeviceRepository):
        """
        Initializes the controller with a repository.

        Args:
            shutter_repository: Repository for shutter data persistence
        """
        self._repository = shutter_repository

    def create_shutter(self, name: str, location: Optional[str] = None) -> str:
        """
        Creates a new shutter.

        Args:
            name: Shutter name
            location: Optional location

        Returns:
            str: ID of the created shutter
        """
        shutter = Shutter(name=name, location=location)
        saved_shutter = self._repository.save(shutter)
        return str(saved_shutter.id)

    def get_shutter(self, shutter_id: str) -> Optional[Shutter]:
        """
        Retrieves a shutter by its ID.

        Args:
            shutter_id: Shutter ID

        Returns:
            Optional[Shutter]: The shutter or None if not found
        """
        device = self._repository.find_by_id(shutter_id)
        if device and isinstance(device, Shutter):
            return device
        return None

    def get_all_shutters(self) -> List[Shutter]:
        """
        Retrieves all shutters.

        Returns:
            List[Shutter]: List of all shutters
        """
        devices = self._repository.find_all()
        return [device for device in devices if isinstance(device, Shutter)]

    def open(self, shutter_id: str) -> bool:
        """
        Opens a shutter.

        Args:
            shutter_id: Shutter ID

        Returns:
            bool: True if the operation was successful
        """
        shutter = self.get_shutter(shutter_id)
        if shutter:
            shutter.open()
            return self._repository.update(shutter)
        return False

    def close(self, shutter_id: str) -> bool:
        """
        Closes a shutter.

        Args:
            shutter_id: Shutter ID

        Returns:
            bool: True if the operation was successful
        """
        shutter = self.get_shutter(shutter_id)
        if shutter:
            shutter.close()
            return self._repository.update(shutter)
        return False

    def stop(self, shutter_id: str) -> bool:
        """
        Stops the movement of a shutter.

        Args:
            shutter_id: Shutter ID

        Returns:
            bool: True if the operation was successful
        """
        shutter = self.get_shutter(shutter_id)
        if shutter and hasattr(shutter, "stop"):
            shutter.stop()
            return self._repository.update(shutter)
        return False

    def set_position(self, shutter_id: str, position: int) -> bool:
        """
        Sets the position of a shutter.

        Args:
            shutter_id: Shutter ID
            position: Position in percentage (0-100)

        Returns:
            bool: True if the operation was successful
        """
        shutter = self.get_shutter(shutter_id)
        if shutter and hasattr(shutter, "set_position"):
            shutter.set_position(position)
            return self._repository.update(shutter)
        return False

    def get_position(self, shutter_id: str) -> Optional[int]:
        """
        Retrieves the position of a shutter.

        Args:
            shutter_id: Shutter ID

        Returns:
            Optional[int]: Position in percentage or None if not found
        """
        shutter = self.get_shutter(shutter_id)
        if shutter and hasattr(shutter, "position"):
            return shutter.position
        return None

    def delete_shutter(self, shutter_id: str) -> bool:
        """
        Deletes a shutter.

        Args:
            shutter_id: Shutter ID

        Returns:
            bool: True if the deletion was successful
        """
        return self._repository.delete(shutter_id)
