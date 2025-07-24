from domotix.core import HomeAutomationController, StateManager
from domotix.models import Light, Sensor


def test_controller_init():
    """Test que le controller s'initialise correctement."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()
    assert hasattr(controller, "_state_manager")


def test_controller_register_and_turn_on():
    """Test l'enregistrement d'un dispositif et son allumage."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()
    light = Light(name="Lampe test")

    # Enregistrer le dispositif - utiliser la valeur de retour
    device_id = controller.register_device(light)

    # Vérifier l'état initial
    assert not light.is_on

    # Allumer le dispositif
    result = controller.turn_on(device_id)
    assert result is True
    assert light.is_on


def test_controller_turn_off():
    """Test l'extinction d'un dispositif."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()
    light = Light(name="Lampe test")
    light.turn_on()  # Allumer d'abord

    device_id = controller.register_device(light)

    # Éteindre le dispositif
    result = controller.turn_off(device_id)
    assert result is True
    assert not light.is_on


def test_controller_turn_on_invalid_device():
    """Test l'allumage d'un dispositif qui n'a pas de méthode turn_on."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()
    sensor = Sensor(name="Capteur test")

    device_id = controller.register_device(sensor)

    # Tenter d'allumer un capteur (qui n'a pas de turn_on)
    result = controller.turn_on(device_id)
    assert result is False


def test_controller_turn_off_invalid_device():
    """Test l'extinction d'un dispositif qui n'a pas de méthode turn_off."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()
    sensor = Sensor(name="Capteur test")

    device_id = controller.register_device(sensor)

    # Tenter d'éteindre un capteur (qui n'a pas de turn_off)
    result = controller.turn_off(device_id)
    assert result is False


def test_controller_get_status():
    """Test la récupération du statut d'un dispositif."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()
    light = Light(name="Lampe test")

    device_id = controller.register_device(light)

    # Vérifier le statut initial
    status = controller.get_status(device_id)
    assert status == "OFF"

    # Allumer et vérifier le nouveau statut
    controller.turn_on(device_id)  # Utiliser le controller pour allumer
    status = controller.get_status(device_id)
    assert status == "ON"


def test_controller_get_status_nonexistent_device():
    """Test la récupération du statut d'un dispositif inexistant."""
    StateManager.reset_instance()  # Reset pour chaque test
    controller = HomeAutomationController()

    # Maintenant get_status retourne None au lieu de lever KeyError
    result = controller.get_status("non-existent-id")
    assert result is None
