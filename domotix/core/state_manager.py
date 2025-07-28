"""
Singleton state manager module for home automation devices.

This module defines the StateManager class, which centrally manages
all devices in the home automation system using a thread-safe singleton
pattern implemented via a metaclass.

Classes:
    StateManager: Thread-safe singleton state manager for devices

Architecture:
    StateManager uses SingletonMeta to ensure only one instance exists,
    allowing consistent shared state across all components.
    Devices are stored in a dict keyed by UUID4 strings.

Example:
    >>> from domotix.core import StateManager
    >>> from domotix.models import Light
    >>>
    >>> # Both instances refer to the same singleton
    >>> sm1 = StateManager()
    >>> sm2 = StateManager()
    >>> assert sm1 is sm2
    >>>
    >>> # Register and retrieve devices
    >>> light = Light("Living Room Light")
    >>> device_id = sm1.register_device(light)
    >>> retrieved = sm2.get_device(device_id)  # shared state
    >>> assert retrieved is light
"""

import uuid
from typing import Dict, Optional

from ..models.device import Device
from .singleton import SingletonMeta


class StateManager(metaclass=SingletonMeta):
    """
    Thread-safe singleton manager for home automation devices.

    Centralizes management of all devices in the system. Ensures a single
    StateManager instance via SingletonMeta, providing consistent shared state.

    Attributes:
        _devices: Internal dict mapping UUID4 strings to Device instances
        _initialized: Flag to prevent multiple initializations

    Example:
        >>> state_manager = StateManager()
        >>> light = Light("Living Room Light")
        >>> device_id = state_manager.register_device(light)
        >>> other_manager = StateManager()  # same instance
        >>> assert other_manager.get_device(device_id) is light
    """

    def __init__(self) -> None:
        """
        Initialize the StateManager if not already initialized.

        Uses _initialized flag to prevent multiple re-initializations even when
        StateManager() is called multiple times.
        """
        # Prevent reinitialization if already initialized (singleton pattern)
        if not hasattr(self, "_initialized"):
            # Stockage des dispositifs [UUID -> Device]
            self._devices: Dict[str, Device] = {}
            self._initialized: bool = True

    def get_device(self, device_id: str) -> Device:
        """
        Retrieve a device by its unique identifier.

        Args:
            device_id: UUID4 string identifier of the device

        Returns:
            Device: The device corresponding to the given ID

        Raises:
            KeyError: If no device matches the given ID

        Example:
            >>> state_manager = StateManager()
            >>> light = Light("Test Light")
            >>> device_id = state_manager.register_device(light)
            >>> assert state_manager.get_device(device_id) is light
        """
        return self._devices[device_id]

    def get_devices(self) -> Dict[str, Device]:
        """
        Get all registered devices.

        Returns:
            Dict[str, Device]: A copy of the internal device mapping.
                              Keys = UUID, Values = Device objects

        Note:
            Returns a copy to preserve encapsulation. Modifying the returned
            dict does not affect the internal state.

        Example:
            >>> state_manager = StateManager()
            >>> devices = state_manager.get_devices()
            >>> devices.clear()  # does not affect internal state
            >>> assert state_manager.get_device_count() >= 0
        """
        return self._devices.copy()

    def register_device(self, device: Device) -> str:
        """
        Register a new device in the system.

        Generates a unique UUID4 string for the device and stores it in the
        internal mapping. Returns the UUID for future references.

        Args:
            device: Device (or subclass) instance to register

        Returns:
            str: Generated UUID4 string for the device

        Example:
            >>> state_manager = StateManager()
            >>> light = Light("New Light")
            >>> device_id = state_manager.register_device(light)
            >>> print(len(device_id))  # 36 characters
            36
        """
        device_id = str(uuid.uuid4())  # Génération d'un UUID unique
        self._devices[device_id] = device
        return device_id

    def unregister_device(self, device_id: str) -> bool:
        """
        Unregister a device from the system.

        Args:
            device_id: UUID4 string of the device to remove

        Returns:
            bool: True if the device was successfully removed,
                  False if it did not exist

        Example:
            >>> state_manager = StateManager()
            >>> light = Light("Temp")
            >>> device_id = state_manager.register_device(light)
            >>> assert state_manager.unregister_device(device_id)
            >>> assert not state_manager.unregister_device("invalid-id")
        """
        if device_id in self._devices:
            del self._devices[device_id]
            return True
        return False

    def get_device_count(self) -> int:
        """
        Return the number of registered devices.

        Returns:
            int: Total number of devices in the system

        Example:
            >>> state_manager = StateManager()
            >>> assert state_manager.get_device_count() >= 0
        """
        return len(self._devices)

    def device_exists(self, device_id: str) -> bool:
        """
        Check if a device exists in the system.

        Args:
            device_id: UUID4 string of the device to check

        Returns:
            bool: True if the device exists, False otherwise

        Example:
            >>> state_manager = StateManager()
            >>> state_manager.device_exists("non-existent")
            >>> assert exists == False
        """
        return device_id in self._devices

    def clear_all_devices(self) -> None:
        """
        Supprime tous les dispositifs enregistrés.

        Remet le StateManager dans un état vide. Utile pour les tests
        ou la réinitialisation complète du système.
        """
        self._devices.clear()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Réinitialise l'instance singleton du StateManager.

        Méthode utilitaire pour les tests qui permet de repartir
        avec une instance fraîche du StateManager.
        """
        SingletonMeta.reset_instance(cls)

    @classmethod
    def has_instance(cls) -> bool:
        """
        Vérifie si une instance du StateManager existe.

        Returns:
            bool: True si une instance existe, False sinon
        """
        return SingletonMeta.has_instance(cls)

    @classmethod
    def get_current_instance(cls) -> Optional["StateManager"]:
        """
        Récupère l'instance actuelle sans en créer une nouvelle.

        Returns:
            StateManager ou None: L'instance si elle existe, None sinon
        """
        from typing import cast

        return cast(Optional["StateManager"], SingletonMeta.get_current_instance(cls))

    def __str__(self) -> str:
        """Représentation string lisible du StateManager."""
        return f"StateManager({self.get_device_count()} dispositifs)"

    def __repr__(self) -> str:
        """Représentation string détaillée pour debugging."""
        return f"StateManager(devices={list(self._devices.keys())})"
