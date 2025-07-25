from domotix.globals import (
    CommandExecutionError,
    DeviceNotFoundError,
    DomotixError,
    InvalidDeviceTypeError,
)


def test_domotix_error():
    """Test l'exception de base DomotixError."""
    error = DomotixError("Message de test")
    assert str(error) == "Message de test"
    assert isinstance(error, Exception)


def test_device_not_found_error():
    """Test l'exception DeviceNotFoundError."""
    device_id = "device_123"
    error = DeviceNotFoundError(device_id)

    assert error.device_id == device_id
    assert str(error) == f"Dispositif non trouvé : {device_id}"
    assert isinstance(error, DomotixError)


def test_invalid_device_type_error():
    """Test l'exception InvalidDeviceTypeError."""
    device_type = "INVALID_TYPE"
    error = InvalidDeviceTypeError(device_type)

    assert error.device_type == device_type
    assert str(error) == f"Type de dispositif invalide : {device_type}"
    assert isinstance(error, DomotixError)


def test_command_execution_error_without_reason():
    """Test l'exception CommandExecutionError sans raison."""
    command = "turn_on"
    error = CommandExecutionError(command)

    assert error.command == command
    assert error.reason == ""
    assert str(error) == f"Échec de l'exécution de la commande : {command}"
    assert isinstance(error, DomotixError)


def test_command_execution_error_with_reason():
    """Test l'exception CommandExecutionError avec raison."""
    command = "turn_on"
    reason = "Dispositif déconnecté"
    error = CommandExecutionError(command, reason)

    assert error.command == command
    assert error.reason == reason
    assert str(error) == f"Échec de l'exécution de la commande : {command} - {reason}"
    assert isinstance(error, DomotixError)


def test_exception_hierarchy():
    """Test que toutes les exceptions héritent correctement de DomotixError."""
    exceptions = [
        DeviceNotFoundError("test"),
        InvalidDeviceTypeError("test"),
        CommandExecutionError("test"),
    ]

    for exception in exceptions:
        assert isinstance(exception, DomotixError)
        assert isinstance(exception, Exception)
