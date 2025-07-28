"""Tests to verify that all imports work correctly."""


def test_import_models():
    """Test that all models import correctly."""
    from domotix.models import Device, Light, Sensor, Shutter

    assert Device is not None
    assert Light is not None
    assert Shutter is not None
    assert Sensor is not None


def test_import_commands():
    """Test that all commands import correctly."""
    from domotix.commands import (
        CloseShutterCommand,
        Command,
        OpenShutterCommand,
        TurnOffCommand,
        TurnOnCommand,
    )

    assert Command is not None
    assert TurnOnCommand is not None
    assert TurnOffCommand is not None
    assert OpenShutterCommand is not None
    assert CloseShutterCommand is not None


def test_import_globals():
    """Test that all global elements import correctly."""
    from domotix.globals import (
        CommandExecutionError,
        CommandType,
        DeviceNotFoundError,
        DeviceState,
        DeviceType,
        DomotixError,
        InvalidDeviceTypeError,
    )

    assert DeviceType is not None
    assert DeviceState is not None
    assert CommandType is not None
    assert DomotixError is not None
    assert DeviceNotFoundError is not None
    assert InvalidDeviceTypeError is not None
    assert CommandExecutionError is not None


def test_import_core_components():
    """Test that all core components import correctly."""
    from domotix.core import HomeAutomationController, StateManager

    assert HomeAutomationController is not None
    assert StateManager is not None


def test_import_cli():
    """Test that CLI components import correctly."""
    from domotix.cli import app, main

    assert app is not None
    assert main is not None


def test_module_structure():
    """Test the structure of the modules."""
    import domotix.cli
    import domotix.commands
    import domotix.core
    import domotix.globals
    import domotix.models

    # Check that the modules have the expected attributes
    assert hasattr(domotix.models, "__all__")
    assert hasattr(domotix.commands, "__all__")
    assert hasattr(domotix.core, "__all__")
    assert hasattr(domotix.globals, "__all__")
    assert hasattr(domotix.cli, "__all__")


def test_domotix_main_import():
    """Test that the main import of the package works."""
    import domotix

    # Check that the main elements are available
    assert hasattr(domotix, "Light")
    assert hasattr(domotix, "HomeAutomationController")
    assert hasattr(domotix, "DeviceType")
