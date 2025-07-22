"""Point d'entrée principal de l'application Domotix."""

import typer

app = typer.Typer()


@app.command()
def main(name: str):
    """Dis bonjour à l'utilisateur."""
    typer.echo(f"Bonjour, {name} !")


if __name__ == "__main__":
    app()
