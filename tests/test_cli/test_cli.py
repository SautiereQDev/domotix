# pylint: disable=import-error
from typer.testing import CliRunner

from domotix.cli import app, main


def test_cli_main_help():
    """Test que l'aide de la commande CLI fonctionne."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout or "Point d'entrée principal" in result.stdout


def test_cli_main_function():
    """Test que la fonction main peut être appelée directement."""
    # Test que la fonction main existe et peut être appelée
    # (pour le coverage du point d'entrée Poetry)
    assert callable(main)
