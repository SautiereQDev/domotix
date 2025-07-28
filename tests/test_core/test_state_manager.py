import threading
import time

import pytest

from domotix.core import SingletonMeta, StateManager
from domotix.models import Light, Shutter


def test_state_manager_singleton_metaclass():
    """Test that StateManager is truly a singleton with the metaclass."""
    # Reset to ensure we start from zero
    StateManager.reset_instance()

    # Create two instances
    sm1 = StateManager()
    sm2 = StateManager()

    # Check that it's the same instance
    assert sm1 is sm2
    assert id(sm1) == id(sm2)


def test_singleton_thread_safety():
    """Test that the singleton is thread-safe."""
    StateManager.reset_instance()

    instances = []

    def create_instance():
        """Function to create an instance in a thread."""
        instance = StateManager()
        instances.append(instance)
        # Small delay to increase race condition chances
        time.sleep(0.01)

    # Create multiple threads that try to create instances
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=create_instance)
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Check that all instances are identical
    assert len(instances) == 10
    first_instance = instances[0]
    for instance in instances:
        assert instance is first_instance


def test_singleton_meta_class_methods():
    """Test the class methods of the singleton metaclass."""
    StateManager.reset_instance()

    # Check that no instance exists at the beginning
    assert not SingletonMeta.has_instance(StateManager)

    # Create an instance
    sm = StateManager()

    # Check that the instance exists now
    assert StateManager.has_instance()
    current = StateManager.get_current_instance()
    assert current is sm

    # Reset and check deletion
    StateManager.reset_instance()
    assert not StateManager.has_instance()
    assert StateManager.get_current_instance() is None


def test_singleton_persistence_with_metaclass():
    """Test that the state persists between accesses to the singleton with metaclass."""
    StateManager.reset_instance()

    # First instance - add a device
    sm1 = StateManager()
    light = Light(name="Lampe test")
    device_id = sm1.register_device(light)

    # Second instance - check that the device exists
    sm2 = StateManager()
    assert sm2.device_exists(device_id)
    assert sm2.get_device_count() == 1
    retrieved_device = sm2.get_device(device_id)
    assert retrieved_device == light


def test_multiple_singletons_with_metaclass():
    """Test that the metaclass can manage multiple singleton classes."""

    # Create another singleton class for the test
    class TestSingleton(metaclass=SingletonMeta):
        def __init__(self):
            if not hasattr(self, "_initialized"):
                self.value = "test"
                self._initialized = True

    # Reset instances
    StateManager.reset_instance()
    SingletonMeta.reset_instance(TestSingleton)

    # Create instances of both classes
    sm1 = StateManager()
    sm2 = StateManager()
    ts1 = TestSingleton()
    ts2 = TestSingleton()

    # Check that each class has its own singleton
    assert sm1 is sm2
    assert ts1 is ts2
    assert sm1 is not ts1  # Different classes, different instances


def test_state_manager_enhanced_methods():
    """Test the new enhanced methods of the StateManager."""
    StateManager.reset_instance()

    state_manager = StateManager()

    # Test register_device returns the ID
    light = Light(name="Lampe test")
    device_id = state_manager.register_device(light)
    assert isinstance(device_id, str)
    assert len(device_id) > 0

    # Test device_exists
    assert state_manager.device_exists(device_id)
    assert not state_manager.device_exists("invalid-id")

    # Test get_device_count
    assert state_manager.get_device_count() == 1

    # Test unregister_device
    assert state_manager.unregister_device(device_id)
    assert not state_manager.device_exists(device_id)
    assert state_manager.get_device_count() == 0

    # Test unregister non-existing device
    assert not state_manager.unregister_device("invalid-id")


def test_state_manager_clear_all_devices():
    """Test the removal of all devices."""
    StateManager.reset_instance()

    state_manager = StateManager()

    # Add multiple devices
    state_manager.register_device(Light(name="Lampe 1"))
    state_manager.register_device(Light(name="Lampe 2"))
    state_manager.register_device(Shutter(name="Volet"))

    assert state_manager.get_device_count() == 3

    # Remove all devices
    state_manager.clear_all_devices()
    assert state_manager.get_device_count() == 0


def test_state_manager_get_devices_copy():
    """Test that get_devices returns a safe copy."""
    StateManager.reset_instance()

    state_manager = StateManager()
    light = Light(name="Lampe test")
    shutter = Shutter(name="Volet test")

    id1 = state_manager.register_device(light)
    id2 = state_manager.register_device(shutter)

    devices = state_manager.get_devices()
    assert len(devices) == 2
    assert devices[id1] == light
    assert devices[id2] == shutter

    # Check that it's a copy (modification should not affect the original)
    devices.clear()
    assert state_manager.get_device_count() == 2


def test_state_manager_string_representations():
    """Test the string representations of the StateManager."""
    StateManager.reset_instance()

    state_manager = StateManager()

    # Test with no device
    assert "0 dispositifs" in str(state_manager)
    assert "devices=[]" in repr(state_manager)

    # Add a device
    light = Light(name="Lampe test")
    device_id = state_manager.register_device(light)

    assert "1 dispositifs" in str(state_manager)
    assert device_id in repr(state_manager)


def test_singleton_meta_reusability():
    """Test that the SingletonMeta metaclass is reusable."""

    # Create two different classes using the same metaclass
    class SingletonA(metaclass=SingletonMeta):
        def __init__(self):
            if not hasattr(self, "_initialized"):
                self.name = "A"
                self._initialized = True

    class SingletonB(metaclass=SingletonMeta):
        def __init__(self):
            if not hasattr(self, "_initialized"):
                self.name = "B"
                self._initialized = True

    # Reset instances
    SingletonMeta.reset_instance(SingletonA)
    SingletonMeta.reset_instance(SingletonB)

    # Create instances
    a1 = SingletonA()
    a2 = SingletonA()
    b1 = SingletonB()
    b2 = SingletonB()

    # Check that each class has its own singleton
    assert a1 is a2
    assert b1 is b2
    assert a1.name == "A"
    assert b1.name == "B"


# Tests de compatibilité avec les anciens tests
def test_register_device():
    """Test l'enregistrement d'un dispositif (compatibilité)."""
    StateManager.reset_instance()

    state_manager = StateManager()
    light = Light(name="Lampe test")

    device_id = state_manager.register_device(light)
    assert isinstance(device_id, str)
    assert state_manager.device_exists(device_id)
    assert state_manager.get_device_count() == 1
    assert state_manager.get_device(device_id) == light


def test_get_device_non_existing():
    """Test la récupération d'un dispositif inexistant."""
    StateManager.reset_instance()

    state_manager = StateManager()

    with pytest.raises(KeyError):
        state_manager.get_device("non-existent-id")
