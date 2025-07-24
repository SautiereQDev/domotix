import threading
import time

import pytest

from domotix.core import SingletonMeta, StateManager
from domotix.models import Light, Shutter


def test_state_manager_singleton_metaclass():
    """Test que StateManager est bien un singleton avec la métaclasse."""
    # Réinitialiser pour s'assurer qu'on part de zéro
    StateManager.reset_instance()

    # Créer deux instances
    sm1 = StateManager()
    sm2 = StateManager()

    # Vérifier que c'est la même instance
    assert sm1 is sm2
    assert id(sm1) == id(sm2)


def test_singleton_thread_safety():
    """Test que le singleton est thread-safe."""
    StateManager.reset_instance()

    instances = []

    def create_instance():
        """Fonction pour créer une instance dans un thread."""
        instance = StateManager()
        instances.append(instance)
        # Petit délai pour augmenter les chances de conditions de course
        time.sleep(0.01)

    # Créer plusieurs threads qui tentent de créer des instances
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=create_instance)
        threads.append(thread)

    # Démarrer tous les threads
    for thread in threads:
        thread.start()

    # Attendre que tous les threads se terminent
    for thread in threads:
        thread.join()

    # Vérifier que toutes les instances sont identiques
    assert len(instances) == 10
    first_instance = instances[0]
    for instance in instances:
        assert instance is first_instance


def test_singleton_meta_class_methods():
    """Test les méthodes de classe de la métaclasse singleton."""
    StateManager.reset_instance()

    # Vérifier qu'aucune instance n'existe au début
    assert not SingletonMeta.has_instance(StateManager)

    # Créer une instance
    sm = StateManager()

    # Vérifier que l'instance existe maintenant
    assert StateManager.has_instance()
    current = StateManager.get_current_instance()
    assert current is sm

    # Réinitialiser et vérifier la suppression
    StateManager.reset_instance()
    assert not StateManager.has_instance()
    assert StateManager.get_current_instance() is None


def test_singleton_persistence_with_metaclass():
    """Test que l'état persiste entre les accès au singleton avec métaclasse."""
    StateManager.reset_instance()

    # Première instance - ajouter un dispositif
    sm1 = StateManager()
    light = Light(name="Lampe test")
    device_id = sm1.register_device(light)

    # Deuxième instance - vérifier que le dispositif existe
    sm2 = StateManager()
    assert sm2.device_exists(device_id)
    assert sm2.get_device_count() == 1
    retrieved_device = sm2.get_device(device_id)
    assert retrieved_device == light


def test_multiple_singletons_with_metaclass():
    """Test que la métaclasse peut gérer plusieurs classes singleton."""

    # Créer une autre classe singleton pour le test
    class TestSingleton(metaclass=SingletonMeta):
        def __init__(self):
            if not hasattr(self, "_initialized"):
                self.value = "test"
                self._initialized = True

    # Réinitialiser les instances
    StateManager.reset_instance()
    SingletonMeta.reset_instance(TestSingleton)

    # Créer des instances des deux classes
    sm1 = StateManager()
    sm2 = StateManager()
    ts1 = TestSingleton()
    ts2 = TestSingleton()

    # Vérifier que chaque classe a son propre singleton
    assert sm1 is sm2
    assert ts1 is ts2
    assert sm1 is not ts1  # Différentes classes, différentes instances


def test_state_manager_enhanced_methods():
    """Test les nouvelles méthodes améliorées du StateManager."""
    StateManager.reset_instance()

    state_manager = StateManager()

    # Test register_device retourne l'ID
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

    # Test unregister device inexistant
    assert not state_manager.unregister_device("invalid-id")


def test_state_manager_clear_all_devices():
    """Test la suppression de tous les dispositifs."""
    StateManager.reset_instance()

    state_manager = StateManager()

    # Ajouter plusieurs dispositifs
    state_manager.register_device(Light(name="Lampe 1"))
    state_manager.register_device(Light(name="Lampe 2"))
    state_manager.register_device(Shutter(name="Volet"))

    assert state_manager.get_device_count() == 3

    # Supprimer tous les dispositifs
    state_manager.clear_all_devices()
    assert state_manager.get_device_count() == 0


def test_state_manager_get_devices_copy():
    """Test que get_devices retourne une copie sécurisée."""
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

    # Vérifier que c'est une copie (modification ne doit pas affecter l'original)
    devices.clear()
    assert state_manager.get_device_count() == 2


def test_state_manager_string_representations():
    """Test les représentations string du StateManager."""
    StateManager.reset_instance()

    state_manager = StateManager()

    # Test avec aucun dispositif
    assert "0 dispositifs" in str(state_manager)
    assert "devices=[]" in repr(state_manager)

    # Ajouter un dispositif
    light = Light(name="Lampe test")
    device_id = state_manager.register_device(light)

    assert "1 dispositifs" in str(state_manager)
    assert device_id in repr(state_manager)


def test_singleton_meta_reusability():
    """Test que la métaclasse SingletonMeta est réutilisable."""

    # Créer deux classes différentes utilisant la même métaclasse
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

    # Réinitialiser les instances
    SingletonMeta.reset_instance(SingletonA)
    SingletonMeta.reset_instance(SingletonB)

    # Créer des instances
    a1 = SingletonA()
    a2 = SingletonA()
    b1 = SingletonB()
    b2 = SingletonB()

    # Vérifier que chaque classe a son propre singleton
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
