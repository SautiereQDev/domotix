from domotix.globals import CommandType, DeviceState, DeviceType


def test_device_type_enum():
    """Test that the DeviceType enum works correctly."""
    assert DeviceType.SHUTTER.value == "SHUTTER"
    assert DeviceType.SENSOR.value == "SENSOR"
    assert DeviceType.LIGHT.value == "LIGHT"

    # Test iteration
    device_types = list(DeviceType)
    assert len(device_types) == 3
    assert DeviceType.LIGHT in device_types


def test_device_state_enum():
    """Test that the DeviceState enum works correctly."""
    assert DeviceState.ON.value == "ON"
    assert DeviceState.OFF.value == "OFF"
    assert DeviceState.OPENING.value == "OPENING"
    assert DeviceState.CLOSING.value == "CLOSING"
    assert DeviceState.STOPPED.value == "STOPPED"

    # Test iteration
    states = list(DeviceState)
    assert len(states) == 5


def test_command_type_enum():
    """Test that the CommandType enum works correctly."""
    assert CommandType.TURN_ON.value == "TURN_ON"
    assert CommandType.TURN_OFF.value == "TURN_OFF"
    assert CommandType.OPEN.value == "OPEN"
    assert CommandType.CLOSE.value == "CLOSE"
    assert CommandType.STOP.value == "STOP"

    # Test iteration
    commands = list(CommandType)
    assert len(commands) == 5


def test_enum_equality():
    """Test enum equality."""
    assert DeviceType.LIGHT != DeviceType.SHUTTER


def test_enum_string_representation():
    """Test string representation of enums."""
    assert str(DeviceType.LIGHT) == "DeviceType.LIGHT"
    assert repr(DeviceType.LIGHT) == "<DeviceType.LIGHT: 'LIGHT'>"
