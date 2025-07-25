"""
Module principal de l'interface en ligne de commande (CLI).

Ce module utilise Typer pour créer une CLI pour interagir avec le
système domotique. Il sert de point d'entrée pour toutes les commandes.

Commands:
    cli: Commande principale de l'application
"""

import sys

# !/usr/bin/env python3
import typer

app = typer.Typer()


def main():
    """Point d'entrée pour Poetry."""
    try:
        app()
    except SystemExit:
        # Intercepter SystemExit pour éviter de quitter le programme
        typer.echo("L'application a été arrêtée.")
        sys.exit(0)


if __name__ == "__main__":
    main()
