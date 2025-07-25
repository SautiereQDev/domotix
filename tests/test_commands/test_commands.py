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
    """La classe de base Command ne doit pas implémenter execute."""

    # Si Command est abstraite, on crée une sous-classe pour tester
    class DummyCommand(Command):
        def execute(self):
            # Appeler l'implémentation de base (qui devrait lever une exception)
            return super().execute()

    cmd = DummyCommand()
    with pytest.raises(NotImplementedError):
        cmd.execute()


def test_turn_on_command_executes_successfully():
    """Test qu'un TurnOnCommand s'exécute avec succès."""
    StateManager.reset_instance()
    lampe = Light(name="Lampe test")
    lampe.is_on = False
    command = TurnOnCommand(device=lampe)
    command.execute()
    assert lampe.is_on is True


def test_turn_off_command_executes_successfully():
    """Test qu'un TurnOffCommand s'exécute avec succès."""
    StateManager.reset_instance()
    lampe = Light(name="Lampe test2")
    lampe.is_on = True
    command = TurnOffCommand(device=lampe)
    command.execute()
    assert lampe.is_on is False


def test_shutter_commands_execute_successfully():
    """Test que les commandes de volet s'exécutent avec succès."""
    StateManager.reset_instance()
    volet = Shutter(name="Volet test")
    volet.position = 0
    open_cmd = OpenShutterCommand(device=volet)
    close_cmd = CloseShutterCommand(device=volet)

    open_cmd.execute()
    assert volet.position == 100

    close_cmd.execute()
    assert volet.position == 0


def test_commands_raise_error_with_wrong_device_type():
    """Test que les commandes lèvent une erreur avec un mauvais type de dispositif."""
    StateManager.reset_instance()
    lampe = Light(name="Lampe erreur")
    volet = Shutter(name="Volet erreur")

    cmd_wrong1 = OpenShutterCommand(lampe)
    with pytest.raises((TypeError, AttributeError, ValueError)):
        cmd_wrong1.execute()

    cmd_wrong2 = TurnOnCommand(volet)
    with pytest.raises((TypeError, AttributeError, ValueError)):
        cmd_wrong2.execute()


def test_turn_on_command_validates_device_has_required_attributes():
    """Test que TurnOnCommand valide que le dispositif a les attributs requis."""
    StateManager.reset_instance()

    class InvalidDevice:
        def __init__(self, name):
            self.name = name
            self.id = "test-id"

    invalid_device = InvalidDevice("Device invalide")
    command = TurnOnCommand(device=invalid_device)
    with pytest.raises(AttributeError, match="n'est pas une lumière"):
        command.execute()


def test_open_shutter_command_validates_device_has_required_attributes():
    """Test que OpenShutterCommand valide que le dispositif a les attributs requis."""
    StateManager.reset_instance()

    class InvalidDevice:
        def __init__(self, name):
            self.name = name
            self.id = "test-id"

    invalid_device = InvalidDevice("Device invalide")
    command = OpenShutterCommand(device=invalid_device)

    with pytest.raises(AttributeError, match="n'est pas un volet"):
        command.execute()


def test_commands_work_with_singleton_state_manager():
    """Test que les commandes fonctionnent avec le StateManager singleton."""
    StateManager.reset_instance()
    state_manager = StateManager()

    lampe = Light(name="Lampe singleton")
    device_id = state_manager.register_device(lampe)

    # Récupérer le dispositif via le singleton
    retrieved_device = state_manager.get_device(device_id)

    command = TurnOnCommand(device=retrieved_device)
    command.execute()

    # Vérifier que l'état persiste dans le singleton
    final_device = state_manager.get_device(device_id)
    assert final_device.is_on is True
