"""
Module de la commande pour fermer un volet.

Classes:
    CloseShutterCommand: Commande pour fermer un volet
"""

from .command import Command


class CloseShutterCommand(Command):
    """Commande pour fermer un volet."""

    def __init__(self, device):
        """
        Initialise la commande.

        Args:
            device: Volet à fermer
            adapter: Adapter pour communiquer avec le volet
        """
        self.device = device

    def execute(self):
        """Exécute la commande de fermeture du volet."""
        if hasattr(self.device, "close"):
            self.device.close()
