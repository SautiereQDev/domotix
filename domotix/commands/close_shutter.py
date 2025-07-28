"""
Module for the command to close a shutter.

Classes:
    CloseShutterCommand: Command to close a shutter
"""

from .command import Command


class CloseShutterCommand(Command):
    """Command to close a shutter."""

    def __init__(self, device):
        """
        Initialize the command.

        Args:
            device: Shutter to close
        """
        self.device = device

    def execute(self):
        """Executes the shutter closing command."""
        if hasattr(self.device, "close"):
            self.device.close()
