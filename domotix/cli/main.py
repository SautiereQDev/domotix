"""
Module principal de l'interface en ligne de commande (CLI).

Ce module utilise Typer pour créer une CLI pour interagir avec le
système domotique. Il sert de point d'entrée pour toutes les commandes.

Commands:
    cli: Commande principale de l'application
"""

# Core imports
import sys

import typer  # pylint: disable=import-error

# Typer application instance (needs to be declared before importing commands)
app = typer.Typer()

# Import commands to register them on the app


def main():
    """Point d'entrée pour Poetry."""
    # Register CLI commands by importing the module where they are defined
    import domotix.cli.device_cmds  # noqa: F401

    try:
        app()
    except SystemExit:
        # Intercepter SystemExit pour éviter de quitter le programme
        typer.echo("L'application a été arrêtée.")
        sys.exit(0)


if __name__ == "__main__":
    main()
