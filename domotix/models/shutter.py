"""
Shutter model module for shutters and blinds.

This module contains the Shutter class, which represents a shutter or blind
in the home automation system. It inherits from Device and adds features
specific to shutters (open, close, position).

Classes:
    Shutter: Model for shutters and blinds

Example:
    >>> from domotix.models import Shutter
    >>> shutter = Shutter("Living Room Shutter", "Living Room")
    >>> shutter.open()
    >>> print(shutter.get_status())
    OPEN
"""

from typing import Optional

from ..globals.enums import DeviceType
from .device import Device


class Shutter(Device):
    """
    Model for shutters and blinds.

    This class represents all types of shutters and blinds
    (roller shutters, blinds, shutters, etc.) with opening and closing
    features.

    Attributes:
        is_open (bool): Shutter opening state (True=open, False=closed)
        name (str): Descriptive name inherited from Device
        id (str): Unique identifier inherited from Device

    Example:
        >>> shutter = Shutter("Bedroom Shutter", "Bedroom")
        >>> shutter.open()
        >>> assert shutter.is_open == True
        >>> shutter.close()
        >>> assert shutter.is_open == False
    """

    def __init__(self, name: str, location: Optional[str] = None) -> None:
        """
        Initializes a new shutter.

        Args:
            name: Descriptive name of the shutter (e.g., "Living Room Shutter",
            "Kitchen Blind")
            location: Location of the shutter (e.g., "Living Room", "Kitchen")
        """
        super().__init__(name, DeviceType.SHUTTER, location)
        self.position: int = 0  # Position in percentage (0=closed, 100=open)

    @property
    def is_open(self) -> bool:
        """Checks if the shutter is considered open (position > 0)."""
        return self.position > 0

    def get_state(self) -> dict:
        """
        Returns the current state of the shutter.

        Returns:
            dict: Current state of the shutter with position and status
        """
        return {
            "position": self.position,
            "is_open": self.is_open,
            "status": self.get_status(),
        }

    def update_state(self, new_state: dict) -> bool:
        """
        Updates the state of the shutter.

        Args:
            new_state: Dictionary containing the new state

        Returns:
            bool: True if the update was successful, False otherwise
        """
        try:
            if "position" in new_state:
                self.set_position(new_state["position"])
            return True
        except (ValueError, TypeError):
            return False

    def open(self) -> None:
        """
        Fully opens the shutter.

        Example:
            >>> shutter = Shutter("Test")
            >>> shutter.open()
            >>> assert shutter.position == 100
        """
        self.position = 100

    def close(self) -> None:
        """
        Fully closes the shutter.

        Example:
            >>> shutter = Shutter("Test")
            >>> shutter.close()
            >>> assert shutter.position == 0
        """
        self.position = 0

    def set_position(self, position: int) -> None:
        """
        Sets the position of the shutter.

        Args:
            position: Position in percentage (0-100)

        Raises:
            ValueError: If the position is not between 0 and 100
        """
        if not 0 <= position <= 100:
            raise ValueError("Position must be between 0 and 100")
        self.position = position

    def get_status(self) -> str:
        """
        Returns the textual status of the shutter.

        Returns:
            str: "OPEN", "CLOSED" or "PARTIAL"
        """
        if self.position == 0:
            return "CLOSED"
        elif self.position == 100:
            return "OPEN"
        else:
            return "PARTIAL"

    def toggle(self) -> None:
        """
        Toggles the state of the shutter (open <-> closed).

        If the shutter is open, it closes. If it is closed, it opens.

        Example:
            >>> shutter = Shutter("Test")
            >>> shutter.toggle()  # Closed -> Open
            >>> assert shutter.is_open == True
            >>> shutter.toggle()  # Open -> Closed
            >>> assert shutter.is_open == False
        """
        if self.is_open:
            self.close()
        else:
            self.open()
