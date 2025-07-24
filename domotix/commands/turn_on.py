"""
Module de la commande pour allumer un dispositif.

Classes:
    TurnOnCommand: Commande pour allumer un dispositif
"""

from .command import Command


class TurnOnCommand(Command):
    """Commande pour allumer un dispositif."""

    def __init__(self, device):
        """
        Initialise la commande.

        Args:
            device: Dispositif à allumer
        """
        self.device = device

    def execute(self):
        """Exécute la commande d'allumage."""
        # Vérifier que le dispositif est une lumière
        if not hasattr(self.device, "turn_on") or not hasattr(self.device, "is_on"):
            raise AttributeError(
                f"Le dispositif {self.device.name} n'est pas une lumière"
            )

        if hasattr(self.device, "turn_on"):
            self.device.turn_on()
