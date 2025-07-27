"""
Module principal de l'interface en ligne de commande (CLI).

Ce module utilise Typer pour créer une CLI pour interagir avec le
système domotique. Il sert de point d'entrée pour toutes les commandes.

Commands:
    cli: Commande principale de l'application
"""

# Core imports
import typer  # pylint: disable=import-error

# Typer application instance (needs to be declared before importing commands)
app = typer.Typer()

# Import commands to register them on the app


def main():
    """Point d'entrée pour Poetry."""
    # Initialiser la base de données
    from domotix.core.database import create_tables

    create_tables()

    # Register CLI commands by importing the module and using its app
    from domotix.cli.device_cmds_di import app as device_app

    device_app()


if __name__ == "__main__":
    main()
