"""
Module for the command to open a shutter.

Classes:
    OpenShutterCommand: Command to open a shutter
"""

from .command import Command


class OpenShutterCommand(Command):
    """Command to open a shutter."""

    def __init__(self, device):
        """
        Initialize the command.

        Args:
            device: Shutter to open
        """
        self.device = device

    def execute(self):
        """Executes the shutter opening command."""
        # Check that the device is a shutter
        if not hasattr(self.device, "open") or not hasattr(self.device, "position"):
            raise AttributeError(f"Device {self.device.name} is not a shutter")

        self.device.open()
