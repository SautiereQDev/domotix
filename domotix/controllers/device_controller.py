"""
Generic controller for managing all types of devices.

This module contains the DeviceController which provides a unified interface
for managing all types of devices (Light, Shutter, Sensor) using
the Repository pattern for data persistence.

Classes:
    DeviceController: Generic controller for all device types
"""

from typing import Dict, List, Optional

from domotix.globals.exceptions import ControllerError, ErrorCode, ErrorContext
from domotix.models.device import Device
from domotix.models.light import Light
from domotix.models.sensor import Sensor
from domotix.models.shutter import Shutter
from domotix.repositories.device_repository import DeviceRepository


class DeviceController:
    """
    Generic controller for managing all types of devices.

    This controller provides a unified interface for managing all types
    of devices in the home automation system.

    Attributes:
        _repository: Repository for data persistence
    """

    def __init__(self, device_repository: DeviceRepository):
        """
        Initializes the controller with a repository.

        Args:
            device_repository: Repository for data persistence
        """
        self._repository = device_repository

    def get_device(self, device_id: str) -> Optional[Device]:
        """
        Retrieves a device by its ID.

        Args:
            device_id: Device ID

        Returns:
            Optional[Device]: The device or None if not found

        Raises:
            ControllerError: In case of error during retrieval
        """
        if not device_id or not device_id.strip():
            context = ErrorContext(
                module=__name__,
                function="get_device",
                user_data={"device_id": device_id},
            )
            raise ControllerError(
                message="Device ID required",
                error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
                context=context,
            )

        try:
            return self._repository.find_by_id(device_id.strip())
        except Exception as e:
            context = ErrorContext(
                module=__name__,
                function="get_device",
                user_data={"device_id": device_id},
            )
            raise ControllerError(
                message=f"Error retrieving device {device_id}",
                error_code=ErrorCode.CONTROLLER_OPERATION_FAILED,
                context=context,
            ) from e

    def get_all_devices(self) -> List[Device]:
        """
        Retrieves all devices.

        Returns:
            List[Device]: List of all devices
        """
        return self._repository.find_all()

    def get_devices_by_type(self, device_type: type) -> List[Device]:
        """
        Retrieves all devices of a given type.

        Args:
            device_type: Device type (Light, Shutter, Sensor)

        Returns:
            List[Device]: List of devices of this type
        """
        all_devices = self.get_all_devices()
        return [device for device in all_devices if isinstance(device, device_type)]

    def get_devices_by_location(self, location: str) -> List[Device]:
        """
        Retrieves all devices in a given location.

        Args:
            location: Location to search

        Returns:
            List[Device]: List of devices in this location
        """
        all_devices = self.get_all_devices()
        return [device for device in all_devices if device.location == location]

    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """
        Retrieves the status of a device.

        Args:
            device_id: Device ID

        Returns:
            Optional[Dict]: Device status or None if not found
        """
        device = self.get_device(device_id)
        if device:
            return device.get_state()
        return None

    def update_device_state(self, device_id: str, new_state: Dict) -> bool:
        """
        Updates the state of a device.

        Args:
            device_id: Device ID
            new_state: New state to apply

        Returns:
            bool: True if the update was successful
        """
        device = self.get_device(device_id)
        if device:
            success = device.update_state(new_state)
            if success:
                return self._repository.update(device)
            return success
        return False

    def delete_device(self, device_id: str) -> bool:
        """
        Deletes a device.

        Args:
            device_id: Device ID

        Returns:
            bool: True if the deletion was successful
        """
        return self._repository.delete(device_id)

    def get_devices_summary(self) -> Dict[str, int]:
        """
        Retrieves a summary of the number of devices by type.

        Returns:
            Dict[str, int]: Dictionary with the number of devices by type
        """
        all_devices = self.get_all_devices()
        summary = {
            "lights": len([d for d in all_devices if isinstance(d, Light)]),
            "shutters": len([d for d in all_devices if isinstance(d, Shutter)]),
            "sensors": len([d for d in all_devices if isinstance(d, Sensor)]),
            "total": len(all_devices),
        }
        return summary

    def get_locations(self) -> List[str]:
        """
        Retrieves all unique locations where devices are installed.

        Returns:
            List[str]: List of unique locations
        """
        all_devices = self.get_all_devices()
        locations = set()
        for device in all_devices:
            if device.location:
                locations.add(device.location)
        return sorted(locations)

    def search_devices(self, query: str) -> List[Device]:
        """
        Searches for devices by name or location.

        Args:
            query: Search term

        Returns:
            List[Device]: List of matching devices
        """
        all_devices = self.get_all_devices()
        query_lower = query.lower()

        matching_devices = []
        for device in all_devices:
            if query_lower in device.name.lower() or (
                device.location and query_lower in device.location.lower()
            ):
                matching_devices.append(device)

        return matching_devices

    def bulk_operation(
        self, device_ids: List[str], operation: str, **kwargs
    ) -> Dict[str, bool]:
        """
        Performs a bulk operation on multiple devices.

        Args:
            device_ids: List of device IDs
            operation: Operation to perform ("turn_on", "turn_off", "open",
            "close", etc.)
            **kwargs: Additional arguments for the operation

        Returns:
            Dict[str, bool]: Results of the operation for each device
        """
        results = {}

        for device_id in device_ids:
            device = self.get_device(device_id)
            if device and hasattr(device, operation):
                try:
                    method = getattr(device, operation)
                    if kwargs:
                        method(**kwargs)
                    else:
                        method()
                    success = self._repository.update(device)
                    results[device_id] = success
                except Exception:
                    results[device_id] = False
            else:
                results[device_id] = False

        return results
