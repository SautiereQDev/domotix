"""
Module de la commande pour éteindre un dispositif.

Classes:
    TurnOffCommand: Commande pour éteindre un dispositif
"""

from .command import Command


class TurnOffCommand(Command):
    """Commande pour éteindre un dispositif."""

    def __init__(self, device):
        """
        Initialise la commande.

        Args:
            device: Dispositif à éteindre
        """
        self.device = device

    def execute(self):
        """Exécute la commande d'extinction."""
        if hasattr(self.device, "turn_off"):
            self.device.turn_off()
