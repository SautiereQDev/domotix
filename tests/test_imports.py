"""Tests pour vérifier que tous les imports fonctionnent correctement."""

import domotix


def test_import_models():
    """Test que tous les modèles s'importent correctement."""
    from domotix.models import Device, Light, Sensor, Shutter

    assert Device is not None
    assert Light is not None
    assert Shutter is not None
    assert Sensor is not None


def test_import_commands():
    """Test que toutes les commandes s'importent correctement."""
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
    """Test que tous les éléments globaux s'importent correctement."""
    from domotix.globals import (
        CommandExecutionError,
        CommandType,
        DeviceNotFoundError,
        DeviceState,
        DeviceType,
        DomotixError,
        HttpMethod,
        InvalidDeviceTypeError,
    )

    assert DeviceType is not None
    assert HttpMethod is not None
    assert DeviceState is not None
    assert CommandType is not None
    assert DomotixError is not None
    assert DeviceNotFoundError is not None
    assert InvalidDeviceTypeError is not None
    assert CommandExecutionError is not None


def test_import_core_components():
    """Test que tous les composants core s'importent correctement."""
    from domotix.core import HomeAutomationController, StateManager

    assert HomeAutomationController is not None
    assert StateManager is not None


def test_import_cli():
    """Test que les composants CLI s'importent correctement."""
    from domotix.cli import app, main

    assert app is not None
    assert main is not None


def test_module_structure():
    """Test la structure des modules."""
    import domotix.cli
    import domotix.commands
    import domotix.core
    import domotix.globals
    import domotix.models

    # Vérifier que les modules ont les attributs attendus
    assert hasattr(domotix.models, "__all__")
    assert hasattr(domotix.commands, "__all__")
    assert hasattr(domotix.core, "__all__")
    assert hasattr(domotix.globals, "__all__")
    assert hasattr(domotix.cli, "__all__")


def test_domotix_main_import():
    """Test que l'import principal du package fonctionne."""

    # Vérifier que les éléments principaux sont disponibles
    assert hasattr(domotix, "Light")
    assert hasattr(domotix, "HomeAutomationController")
    assert hasattr(domotix, "DeviceType")
    assert hasattr(domotix, "__version__")
