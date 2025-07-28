"""
Integration tests for persistence.

This module contains integration tests that test
the entire persistence chain (repositories + controllers).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domotix.core.database import Base
from domotix.core.factories import (
    FactoryManager,
    get_controller_factory,
    get_repository_factory,
)
from domotix.models import Light, Sensor, Shutter


@pytest.fixture
def test_session():
    """Create an in-memory test session."""
    # Reset factories to avoid interference between tests
    FactoryManager.reset_instance()

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    test_session_cls = sessionmaker(bind=engine)
    session = test_session_cls()
    yield session
    session.close()


@pytest.fixture
def light_controller(test_session):
    """Create a light controller with a test session."""
    return get_controller_factory().create_light_controller(test_session)


@pytest.fixture
def shutter_controller(test_session):
    """Create a shutter controller with a test session."""
    return get_controller_factory().create_shutter_controller(test_session)


@pytest.fixture
def sensor_controller(test_session):
    """Create a sensor controller with a test session."""
    return get_controller_factory().create_sensor_controller(test_session)


@pytest.fixture
def device_controller(test_session):
    """Create a general controller with a test session."""
    return get_controller_factory().create_device_controller(test_session)


class TestLightControllerIntegration:
    """Integration tests for LightController."""

    def test_complete_light_lifecycle(self, light_controller):
        """Test the complete lifecycle of a lamp."""
        # Create a lamp
        light_id = light_controller.create_light("Lampe salon", "Salon")
        assert light_id is not None

        # Retrieve the lamp
        light = light_controller.get_light(light_id)
        assert light is not None
        assert light.name == "Lampe salon"
        assert light.location == "Salon"
        assert light.is_on is False

        # Turn on the lamp
        success = light_controller.turn_on(light_id)
        assert success is True

        # Check the state
        light = light_controller.get_light(light_id)
        assert light.is_on is True

        # Turn off the lamp
        success = light_controller.turn_off(light_id)
        assert success is True

        # Check the state
        light = light_controller.get_light(light_id)
        assert light.is_on is False

        # Toggle the state
        success = light_controller.toggle(light_id)
        assert success is True

        # Check the state
        light = light_controller.get_light(light_id)
        assert light.is_on is True

        # Delete the lamp
        success = light_controller.delete_light(light_id)
        assert success is True

        # Check that the lamp no longer exists
        light = light_controller.get_light(light_id)
        assert light is None

    def test_multiple_lights_management(self, light_controller):
        """Test management of multiple lamps."""
        # Create several lamps
        light1_id = light_controller.create_light("Lampe salon", "Salon")
        light2_id = light_controller.create_light("Lampe chambre", "Chambre")
        light3_id = light_controller.create_light("Spot cuisine", "Cuisine")

        # Check that they all exist
        all_lights = light_controller.get_all_lights()
        assert len(all_lights) == 3

        # Turn on some lamps
        light_controller.turn_on(light1_id)
        light_controller.turn_on(light3_id)

        # Check the states
        light1 = light_controller.get_light(light1_id)
        light2 = light_controller.get_light(light2_id)
        light3 = light_controller.get_light(light3_id)

        assert light1.is_on is True
        assert light2.is_on is False
        assert light3.is_on is True


class TestShutterControllerIntegration:
    """Tests d'intégration pour le ShutterController."""

    def test_complete_shutter_lifecycle(self, shutter_controller):
        """Test du cycle de vie complet d'un volet."""
        # Créer un volet
        shutter_id = shutter_controller.create_shutter("Volet salon", "Salon")
        assert shutter_id is not None

        # Récupérer le volet
        shutter = shutter_controller.get_shutter(shutter_id)
        assert shutter is not None
        assert shutter.name == "Volet salon"
        assert shutter.location == "Salon"
        assert shutter.is_open is False

        # Ouvrir le volet
        success = shutter_controller.open(shutter_id)
        assert success is True

        # Vérifier l'état
        shutter = shutter_controller.get_shutter(shutter_id)
        assert shutter.is_open is True

        # Fermer le volet
        success = shutter_controller.close(shutter_id)
        assert success is True

        # Vérifier l'état
        shutter = shutter_controller.get_shutter(shutter_id)
        assert shutter.is_open is False

        # Supprimer le volet
        success = shutter_controller.delete_shutter(shutter_id)
        assert success is True

        # Vérifier que le volet n'existe plus
        shutter = shutter_controller.get_shutter(shutter_id)
        assert shutter is None


class TestSensorControllerIntegration:
    """Tests d'intégration pour le SensorController."""

    def test_complete_sensor_lifecycle(self, sensor_controller):
        """Test du cycle de vie complet d'un capteur."""
        # Créer un capteur
        sensor_id = sensor_controller.create_sensor("Capteur température", "Salon")
        assert sensor_id is not None

        # Récupérer le capteur
        sensor = sensor_controller.get_sensor(sensor_id)
        assert sensor is not None
        assert sensor.name == "Capteur température"
        assert sensor.location == "Salon"
        assert sensor.value is None

        # Vérifier qu'il n'est pas actif
        assert sensor_controller.is_active(sensor_id) is False

        # Mettre à jour la valeur
        success = sensor_controller.update_value(sensor_id, 22.5)
        assert success is True

        # Vérifier l'état
        sensor = sensor_controller.get_sensor(sensor_id)
        assert sensor.value == 22.5

        # Vérifier qu'il est maintenant actif
        assert sensor_controller.is_active(sensor_id) is True

        # Récupérer la valeur
        value = sensor_controller.get_value(sensor_id)
        assert value == 22.5

        # Remettre à zéro
        success = sensor_controller.reset_value(sensor_id)
        assert success is True

        # Vérifier l'état
        sensor = sensor_controller.get_sensor(sensor_id)
        assert sensor.value is None
        assert sensor_controller.is_active(sensor_id) is False

        # Supprimer le capteur
        success = sensor_controller.delete_sensor(sensor_id)
        assert success is True

        # Vérifier que le capteur n'existe plus
        sensor = sensor_controller.get_sensor(sensor_id)
        assert sensor is None


class TestDeviceControllerIntegration:
    """Tests d'intégration pour le DeviceController."""

    def test_mixed_devices_management(self, device_controller, test_session):
        """Test de gestion d'un mélange de dispositifs."""
        # Créer différents types de dispositifs
        light_repo = get_repository_factory().create_light_repository(test_session)
        shutter_repo = get_repository_factory().create_shutter_repository(test_session)
        sensor_repo = get_repository_factory().create_sensor_repository(test_session)

        # Créer des dispositifs directement via les repositories
        light = Light("Lampe salon", "Salon")
        shutter = Shutter("Volet chambre", "Chambre")
        sensor = Sensor("Capteur température", "Salon")

        light_repo.save(light)
        shutter_repo.save(shutter)
        sensor_repo.save(sensor)

        # Tester les fonctionnalités du contrôleur général
        all_devices = device_controller.get_all_devices()
        assert len(all_devices) == 3

        # Tester le résumé
        summary = device_controller.get_devices_summary()
        assert summary["lights"] == 1
        assert summary["shutters"] == 1
        assert summary["sensors"] == 1
        assert summary["total"] == 3

        # Tester les emplacements
        locations = device_controller.get_locations()
        assert "Salon" in locations
        assert "Chambre" in locations
        assert len(locations) == 2

        # Tester la recherche
        salon_devices = device_controller.get_devices_by_location("Salon")
        assert len(salon_devices) == 2  # Lampe + capteur

        # Tester la recherche par nom
        search_results = device_controller.search_devices("salon")
        assert len(search_results) == 2  # Lampe salon + capteur dans le salon

        # Tester une opération en lot (allumer la lampe)
        results = device_controller.bulk_operation([light.id], "turn_on")
        assert results[light.id] is True

        # Vérifier que la lampe est allumée
        updated_light = device_controller.get_device(light.id)
        assert updated_light.is_on is True

    def test_device_state_management(self, device_controller, test_session):
        """Test de gestion d'état des dispositifs."""
        # Créer un dispositif
        light_repo = get_repository_factory().create_light_repository(test_session)
        light = Light("Lampe test", "Test")
        light_repo.save(light)

        # Récupérer l'état initial
        status = device_controller.get_device_status(light.id)
        assert status is not None
        assert status["is_on"] is False

        # Mettre à jour l'état
        new_state = {"is_on": True}
        success = device_controller.update_device_state(light.id, new_state)
        assert success is True

        # Vérifier le nouvel état
        status = device_controller.get_device_status(light.id)
        assert status["is_on"] is True


class TestCrossControllerIntegration:
    """Tests d'intégration entre différents contrôleurs."""

    def test_persistence_across_controllers(self, test_session):
        """Test de persistence entre différents contrôleurs."""
        # Créer des contrôleurs avec la même session
        light_controller = get_controller_factory().create_light_controller(
            test_session
        )
        device_controller = get_controller_factory().create_device_controller(
            test_session
        )

        # Créer une lampe via le contrôleur spécialisé
        light_id = light_controller.create_light("Lampe partagée", "Salon")

        # Vérifier qu'elle est visible via le contrôleur général
        device = device_controller.get_device(light_id)
        assert device is not None
        assert device.name == "Lampe partagée"
        assert isinstance(device, Light)

        # Modifier l'état via le contrôleur général
        success = device_controller.update_device_state(light_id, {"is_on": True})
        assert success is True

        # Vérifier l'état via le contrôleur spécialisé
        light = light_controller.get_light(light_id)
        assert light.is_on is True

    def test_repository_consistency(self, test_session):
        """Test de cohérence entre repositories."""
        # Créer des repositories avec la même session
        device_repo = get_repository_factory().create_device_repository(test_session)
        light_repo = get_repository_factory().create_light_repository(test_session)

        # Créer une lampe via le repository spécialisé
        light = Light("Lampe cohérence", "Test")
        light_repo.save(light)

        # Vérifier qu'elle est visible via le repository général
        device = device_repo.find_by_id(light.id)
        assert device is not None
        assert device.name == "Lampe cohérence"

        # Vérifier le comptage
        all_devices = device_repo.find_all()
        lights_count = light_repo.count_lights()

        assert len(all_devices) == 1
        assert lights_count == 1
