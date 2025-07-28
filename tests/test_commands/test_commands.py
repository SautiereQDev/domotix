import pytest

from domotix.commands import (
    CloseShutterCommand,
    Command,
    OpenShutterCommand,
    TurnOffCommand,
    TurnOnCommand,
)
from domotix.core import StateManager
from domotix.models import Light, Shutter


def test_command_base_execute_not_implemented():
    """The base Command class must not implement execute."""

    # If Command is abstract, create a subclass to test
    class DummyCommand(Command):
        def execute(self):
            # Call the base implementation (should raise an exception)
            return super().execute()

    cmd = DummyCommand()
    with pytest.raises(NotImplementedError):
        cmd.execute()


def test_turn_on_command_executes_successfully():
    """Test that a TurnOnCommand executes successfully."""
    StateManager.reset_instance()
    lamp = Light(name="Test lamp")
    lamp.is_on = False
    command = TurnOnCommand(device=lamp)
    command.execute()
    assert lamp.is_on is True


def test_turn_off_command_executes_successfully():
    """Test that a TurnOffCommand executes successfully."""
    StateManager.reset_instance()
    lamp = Light(name="Test lamp 2")
    lamp.is_on = True
    command = TurnOffCommand(device=lamp)
    command.execute()
    assert lamp.is_on is False


def test_shutter_commands_execute_successfully():
    """Test that shutter commands execute successfully."""
    StateManager.reset_instance()
    shutter = Shutter(name="Test shutter")
    shutter.position = 0
    open_cmd = OpenShutterCommand(device=shutter)
    close_cmd = CloseShutterCommand(device=shutter)

    open_cmd.execute()
    assert shutter.position == 100

    close_cmd.execute()
    assert shutter.position == 0


def test_commands_raise_error_with_wrong_device_type():
    """Test that commands raise an error with the wrong device type."""
    StateManager.reset_instance()
    lamp = Light(name="Error lamp")
    shutter = Shutter(name="Error shutter")

    cmd_wrong1 = OpenShutterCommand(lamp)
    with pytest.raises((TypeError, AttributeError, ValueError)):
        cmd_wrong1.execute()

    cmd_wrong2 = TurnOnCommand(shutter)
    with pytest.raises((TypeError, AttributeError, ValueError)):
        cmd_wrong2.execute()


def test_turn_on_command_validates_device_has_required_attributes():
    """Test that TurnOnCommand validates the device has the required attributes."""
    StateManager.reset_instance()

    class InvalidDevice:
        def __init__(self, name):
            self.name = name
            self.id = "test-id"

    invalid_device = InvalidDevice("Invalid device")
    command = TurnOnCommand(device=invalid_device)
    with pytest.raises(AttributeError, match="is not a light"):
        command.execute()


def test_open_shutter_command_validates_device_has_required_attributes():
    """Test that OpenShutterCommand validates the device has the required attributes."""
    StateManager.reset_instance()

    class InvalidDevice:
        def __init__(self, name):
            self.name = name
            self.id = "test-id"

    invalid_device = InvalidDevice("Invalid device")
    command = OpenShutterCommand(device=invalid_device)

    with pytest.raises(AttributeError, match="is not a shutter"):
        command.execute()


def test_commands_work_with_singleton_state_manager():
    """Test that commands work with the StateManager singleton."""
    StateManager.reset_instance()
    state_manager = StateManager()

    lamp = Light(name="Singleton lamp")
    device_id = state_manager.register_device(lamp)

    # Retrieve the device via the singleton
    retrieved_device = state_manager.get_device(device_id)

    command = TurnOnCommand(device=retrieved_device)
    command.execute()

    # Check that the state persists in the singleton
    final_device = state_manager.get_device(device_id)
    assert final_device.is_on is True
