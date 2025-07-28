# pylint: disable=import-error
from typer.testing import CliRunner

from domotix.cli import app, main


def test_cli_main_help():
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout or "Main entry point" in result.stdout


def test_cli_main_function():
    """Test that the main function can be called directly."""
    # Test that the main function exists and can be called
    # (for Poetry entry point coverage)
    assert callable(main)
