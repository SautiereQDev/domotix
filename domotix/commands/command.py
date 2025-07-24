"""
Module de la commande de base pour le pattern Command.

Ce module contient la classe abstraite Command qui sert de base
pour toutes les commandes du système.

Classes:
    Command: Classe abstraite de base pour toutes les commandes
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Classe abstraite de base pour toutes les commandes.

    Cette classe définit l'interface commune que toutes les commandes
    doivent implémenter pour utiliser le pattern Command.

    Abstract Methods:
        execute(): Exécute la commande
    """

    @abstractmethod
    def execute(self):
        """
        Exécute la commande.

        Cette méthode doit être implémentée par toutes les classes filles.
        """
        raise NotImplementedError(
            "La méthode execute doit être implémentée " "par les sous-classes"
        )
