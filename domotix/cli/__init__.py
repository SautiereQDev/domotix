"""
Module de l'interface en ligne de commande (CLI).

Ce module expose l'application Typer principale et la fonction main
pour le point d'entrée Poetry.

Exposed:
    app: Instance de l'application Typer
    main: Fonction main pour le point d'entrée
"""

# Module CLI - Interface en ligne de commande
from .main import app, main

__all__ = ["app", "main"]
