"""
Module for the command to turn off a device.

Classes:
    TurnOffCommand: Command to turn off a device
"""

from .command import Command


class TurnOffCommand(Command):
    """Command to turn off a device."""

    def __init__(self, device):
        """
        Initialize the command.

        Args:
            device: Device to turn off
        """
        self.device = device

    def execute(self):
        """Executes the turn off command."""
        if hasattr(self.device, "turn_off"):
            self.device.turn_off()
