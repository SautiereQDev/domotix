from domotix.globals import CommandType, DeviceState, DeviceType


def test_device_type_enum():
    """Test que l'enum DeviceType fonctionne correctement."""
    assert DeviceType.SHUTTER.value == "SHUTTER"
    assert DeviceType.SENSOR.value == "SENSOR"
    assert DeviceType.LIGHT.value == "LIGHT"

    # Test de l'itération
    device_types = list(DeviceType)
    assert len(device_types) == 3
    assert DeviceType.LIGHT in device_types


def test_device_state_enum():
    """Test que l'enum DeviceState fonctionne correctement."""
    assert DeviceState.ON.value == "ON"
    assert DeviceState.OFF.value == "OFF"
    assert DeviceState.OPENING.value == "OPENING"
    assert DeviceState.CLOSING.value == "CLOSING"
    assert DeviceState.STOPPED.value == "STOPPED"

    # Test de l'itération
    states = list(DeviceState)
    assert len(states) == 5


def test_command_type_enum():
    """Test que l'enum CommandType fonctionne correctement."""
    assert CommandType.TURN_ON.value == "TURN_ON"
    assert CommandType.TURN_OFF.value == "TURN_OFF"
    assert CommandType.OPEN.value == "OPEN"
    assert CommandType.CLOSE.value == "CLOSE"
    assert CommandType.STOP.value == "STOP"

    # Test de l'itération
    commands = list(CommandType)
    assert len(commands) == 5


def test_enum_equality():
    """Test l'égalité des enums."""
    assert DeviceType.LIGHT == DeviceType.LIGHT
    assert DeviceType.LIGHT != DeviceType.SHUTTER


def test_enum_string_representation():
    """Test la représentation string des enums."""
    assert str(DeviceType.LIGHT) == "DeviceType.LIGHT"
    assert repr(DeviceType.LIGHT) == "<DeviceType.LIGHT: 'LIGHT'>"
