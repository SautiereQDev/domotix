"""
Module de la commande pour ouvrir un volet.

Classes:
    OpenShutterCommand: Commande pour ouvrir un volet
"""

from .command import Command


class OpenShutterCommand(Command):
    """Commande pour ouvrir un volet."""

    def __init__(self, device):
        """
        Initialise la commande.

        Args:
            device: Volet à ouvrir
        """
        self.device = device

    def execute(self):
        """Exécute la commande d'ouverture du volet."""
        # Vérifier que le dispositif est un volet
        if not hasattr(self.device, "open") or not hasattr(self.device, "position"):
            raise AttributeError(f"Le dispositif {self.device.name} n'est pas un volet")

        self.device.open()
