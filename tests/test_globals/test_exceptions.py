"""_summary_
This module contains custom exceptions for the Domotix application.
This module defines exceptions that are used throughout the application
to handle errors related to devices, commands, and other system operations.
These exceptions inherit from a base exception class to
maintain a consistent error handling strategy.
"""

from domotix.globals import (
    CommandExecutionError,
    DeviceNotFoundError,
    DomotixError,
    InvalidDeviceTypeError,
)


def test_domotix_error():
    """Test the base DomotixError exception."""
    error = DomotixError("Test message")
    assert str(error) == "[DMX-1000] Test message"
    assert isinstance(error, Exception)


def test_device_not_found_error():
    """Test the DeviceNotFoundError exception."""
    device_id = "device_123"
    error = DeviceNotFoundError(device_id)

    assert error.device_id == device_id
    assert str(error) == f"[DMX-2000] Device not found: {device_id}"
    assert isinstance(error, DomotixError)


def test_invalid_device_type_error():
    """Test the InvalidDeviceTypeError exception."""
    device_type = "INVALID_TYPE"
    error = InvalidDeviceTypeError(device_type)

    assert error.device_type == device_type
    assert str(error) == f"[DMX-2005] Invalid device type: {device_type}"
    assert isinstance(error, DomotixError)


def test_command_execution_error_without_reason():
    """Test the CommandExecutionError exception without reason."""
    command = "turn_on"
    error = CommandExecutionError(command)

    assert error.command == command
    assert error.reason == ""
    assert str(error) == f"[DMX-6000] Command execution failed: {command}"
    assert isinstance(error, DomotixError)


def test_command_execution_error_with_reason():
    """Test the CommandExecutionError exception with reason."""
    command = "turn_on"
    reason = "Device disconnected"
    error = CommandExecutionError(command, reason)

    assert error.command == command
    assert error.reason == reason
    expected = f"[DMX-6000] Command execution failed: {command} - {reason}"
    assert str(error) == expected
    assert isinstance(error, DomotixError)


def test_exception_hierarchy():
    """Test that all exceptions inherit correctly from DomotixError."""
    exceptions = [
        DeviceNotFoundError("test"),
        InvalidDeviceTypeError("test"),
        CommandExecutionError("test"),
    ]

    for exception in exceptions:
        assert isinstance(exception, DomotixError)
        assert isinstance(exception, Exception)
