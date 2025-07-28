"""
Main module for the command-line interface (CLI).

This module uses Typer to create a CLI for interacting with the
home automation system. It serves as the entry point for all commands.

Commands:
    cli: Main application command
"""

# Core imports
import typer  # pylint: disable=import-error

# Typer application instance (needs to be declared before importing commands)
app = typer.Typer()

# Import commands to register them on the app


def main():
    """Entry point for Poetry."""
    # Initialize the database
    from domotix.core.database import create_tables

    create_tables()

    # Register CLI commands by importing the module and using its app
    from domotix.cli.device_cmds_di import app as device_app

    device_app()


if __name__ == "__main__":
    main()
