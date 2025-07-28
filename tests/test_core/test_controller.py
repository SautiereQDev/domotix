from domotix.core import HomeAutomationController, StateManager
from domotix.models import Light, Sensor


def test_controller_init():
    """Test that the controller initializes correctly."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()
    assert hasattr(controller, "_state_manager")


def test_controller_register_and_turn_on():
    """Test registering a device and turning it on."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()
    light = Light(name="Test lamp")

    # Register the device - use the return value
    device_id = controller.register_device(light)

    # Check initial state
    assert not light.is_on

    # Turn on the device
    result = controller.turn_on(device_id)
    assert result is True
    assert light.is_on


def test_controller_turn_off():
    """Test turning off a device."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()
    light = Light(name="Test lamp")
    light.turn_on()  # Turn on first

    device_id = controller.register_device(light)

    # Turn off the device
    result = controller.turn_off(device_id)
    assert result is True
    assert not light.is_on


def test_controller_turn_on_invalid_device():
    """Test turning on a device that does not have a turn_on method."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()
    sensor = Sensor(name="Test sensor")

    device_id = controller.register_device(sensor)

    # Try to turn on a sensor (which does not have turn_on)
    result = controller.turn_on(device_id)
    assert result is False


def test_controller_turn_off_invalid_device():
    """Test turning off a device that does not have a turn_off method."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()
    sensor = Sensor(name="Test sensor")

    device_id = controller.register_device(sensor)

    # Try to turn off a sensor (which does not have turn_off)
    result = controller.turn_off(device_id)
    assert result is False


def test_controller_get_status():
    """Test getting the status of a device."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()
    light = Light(name="Test lamp")

    device_id = controller.register_device(light)

    # Check initial status
    status = controller.get_status(device_id)
    assert status == "OFF"

    # Turn on and check new status
    controller.turn_on(device_id)  # Use the controller to turn on
    status = controller.get_status(device_id)
    assert status == "ON"


def test_controller_get_status_nonexistent_device():
    """Test getting the status of a nonexistent device."""
    StateManager.reset_instance()  # Reset for each test
    controller = HomeAutomationController()

    # Now get_status returns None instead of raising KeyError
    result = controller.get_status("non-existent-id")
    assert result is None
