"""
Module for the command to turn on a device.

Classes:
    TurnOnCommand: Command to turn on a device
"""

from .command import Command


class TurnOnCommand(Command):
    """Command to turn on a device."""

    def __init__(self, device):
        """
        Initialize the command.

        Args:
            device: Device to turn on
        """
        self.device = device

    def execute(self):
        """Executes the turn on command."""
        # Check that the device is a light
        if not hasattr(self.device, "turn_on") or not hasattr(self.device, "is_on"):
            raise AttributeError(f"Device {self.device.name} is not a light")

        if hasattr(self.device, "turn_on"):
            self.device.turn_on()
