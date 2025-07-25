"""
Tests pour les repositories spécialisés.

Ce module contient tous les tests unitaires pour les repositories
spécialisés (Light, Shutter, Sensor).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domotix.core.database import Base
from domotix.globals.enums import DeviceType
from domotix.models import Light, Sensor, Shutter
from domotix.repositories import LightRepository, SensorRepository, ShutterRepository


@pytest.fixture
def test_session():
    """Crée une session de test en mémoire."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def light_repository(test_session):
    """Crée une instance de LightRepository pour les tests."""
    return LightRepository(test_session)


@pytest.fixture
def shutter_repository(test_session):
    """Crée une instance de ShutterRepository pour les tests."""
    return ShutterRepository(test_session)


@pytest.fixture
def sensor_repository(test_session):
    """Crée une instance de SensorRepository pour les tests."""
    return SensorRepository(test_session)


class TestLightRepository:
    """Tests pour la classe LightRepository."""

    def test_find_lights_by_location(self, light_repository):
        """Test de recherche de lampes par emplacement."""
        # Arrange
        light1 = Light("Lampe salon 1", "Salon")
        light2 = Light("Lampe salon 2", "Salon")
        light3 = Light("Lampe chambre", "Chambre")

        light_repository.save(light1)
        light_repository.save(light2)
        light_repository.save(light3)

        # Act
        salon_lights = light_repository.find_lights_by_location("Salon")

        # Assert
        assert len(salon_lights) == 2
        for light in salon_lights:
            assert light.location == "Salon"
            assert light.device_type == DeviceType.LIGHT

    def test_count_lights(self, light_repository):
        """Test du comptage des lampes."""
        # Arrange
        light1 = Light("Lampe 1", "Salon")
        light2 = Light("Lampe 2", "Chambre")

        light_repository.save(light1)
        light_repository.save(light2)

        # Act
        count = light_repository.count_lights()

        # Assert
        assert count == 2

    def test_search_lights_by_name(self, light_repository):
        """Test de recherche de lampes par nom."""
        # Arrange
        light1 = Light("Lampe principale salon", "Salon")
        light2 = Light("Spot cuisine", "Cuisine")
        light3 = Light("Lampe bureau", "Bureau")

        light_repository.save(light1)
        light_repository.save(light2)
        light_repository.save(light3)

        # Act
        lampe_results = light_repository.search_lights_by_name("Lampe")

        # Assert
        assert len(lampe_results) == 2
        names = [light.name for light in lampe_results]
        assert "Lampe principale salon" in names
        assert "Lampe bureau" in names

    def test_find_on_lights(self, light_repository):
        """Test de recherche des lampes allumées."""
        # Arrange
        light1 = Light("Lampe 1", "Salon")
        light2 = Light("Lampe 2", "Chambre")

        light_repository.save(light1)
        light_repository.save(light2)

        # Act
        on_lights = light_repository.find_on_lights()

        # Assert
        # Pour l'instant, cette méthode retourne toutes les lampes
        # TODO: Implémenter la logique réelle quand le modèle sera adapté
        assert len(on_lights) == 2

    def test_find_off_lights(self, light_repository):
        """Test de recherche des lampes éteintes."""
        # Arrange
        light1 = Light("Lampe 1", "Salon")
        light2 = Light("Lampe 2", "Chambre")

        light_repository.save(light1)
        light_repository.save(light2)

        # Act
        off_lights = light_repository.find_off_lights()

        # Assert
        # Pour l'instant, cette méthode retourne toutes les lampes
        # TODO: Implémenter la logique réelle quand le modèle sera adapté
        assert len(off_lights) == 2


class TestShutterRepository:
    """Tests pour la classe ShutterRepository."""

    def test_find_shutters_by_location(self, shutter_repository):
        """Test de recherche de volets par emplacement."""
        # Arrange
        shutter1 = Shutter("Volet salon 1", "Salon")
        shutter2 = Shutter("Volet salon 2", "Salon")
        shutter3 = Shutter("Volet chambre", "Chambre")

        shutter_repository.save(shutter1)
        shutter_repository.save(shutter2)
        shutter_repository.save(shutter3)

        # Act
        salon_shutters = shutter_repository.find_shutters_by_location("Salon")

        # Assert
        assert len(salon_shutters) == 2
        for shutter in salon_shutters:
            assert shutter.location == "Salon"
            assert shutter.device_type == DeviceType.SHUTTER

    def test_count_shutters(self, shutter_repository):
        """Test du comptage des volets."""
        # Arrange
        shutter1 = Shutter("Volet 1", "Salon")
        shutter2 = Shutter("Volet 2", "Chambre")

        shutter_repository.save(shutter1)
        shutter_repository.save(shutter2)

        # Act
        count = shutter_repository.count_shutters()

        # Assert
        assert count == 2

    def test_search_shutters_by_name(self, shutter_repository):
        """Test de recherche de volets par nom."""
        # Arrange
        shutter1 = Shutter("Volet principal salon", "Salon")
        shutter2 = Shutter("Store cuisine", "Cuisine")
        shutter3 = Shutter("Volet bureau", "Bureau")

        shutter_repository.save(shutter1)
        shutter_repository.save(shutter2)
        shutter_repository.save(shutter3)

        # Act
        volet_results = shutter_repository.search_shutters_by_name("Volet")

        # Assert
        assert len(volet_results) == 2
        names = [shutter.name for shutter in volet_results]
        assert "Volet principal salon" in names
        assert "Volet bureau" in names


class TestSensorRepository:
    """Tests pour la classe SensorRepository."""

    def test_find_sensors_by_location(self, sensor_repository):
        """Test de recherche de capteurs par emplacement."""
        # Arrange
        sensor1 = Sensor("Capteur température salon", "Salon")
        sensor2 = Sensor("Capteur humidité salon", "Salon")
        sensor3 = Sensor("Capteur température chambre", "Chambre")

        sensor_repository.save(sensor1)
        sensor_repository.save(sensor2)
        sensor_repository.save(sensor3)

        # Act
        salon_sensors = sensor_repository.find_sensors_by_location("Salon")

        # Assert
        assert len(salon_sensors) == 2
        for sensor in salon_sensors:
            assert sensor.location == "Salon"
            assert sensor.device_type == DeviceType.SENSOR

    def test_count_sensors(self, sensor_repository):
        """Test du comptage des capteurs."""
        # Arrange
        sensor1 = Sensor("Capteur 1", "Salon")
        sensor2 = Sensor("Capteur 2", "Chambre")

        sensor_repository.save(sensor1)
        sensor_repository.save(sensor2)

        # Act
        count = sensor_repository.count_sensors()

        # Assert
        assert count == 2

    def test_search_sensors_by_name(self, sensor_repository):
        """Test de recherche de capteurs par nom."""
        # Arrange
        sensor1 = Sensor("Capteur température salon", "Salon")
        sensor2 = Sensor("Détecteur mouvement", "Entrée")
        sensor3 = Sensor("Capteur humidité", "Salle de bain")

        sensor_repository.save(sensor1)
        sensor_repository.save(sensor2)
        sensor_repository.save(sensor3)

        # Act
        capteur_results = sensor_repository.search_sensors_by_name("Capteur")

        # Assert
        assert len(capteur_results) == 2
        names = [sensor.name for sensor in capteur_results]
        assert "Capteur température salon" in names
        assert "Capteur humidité" in names

    def test_find_sensors_by_type(self, sensor_repository):
        """Test de recherche de capteurs par type."""
        # Arrange
        sensor1 = Sensor("Capteur température salon", "Salon")
        sensor2 = Sensor("Capteur température chambre", "Chambre")
        sensor3 = Sensor("Capteur humidité", "Salle de bain")

        sensor_repository.save(sensor1)
        sensor_repository.save(sensor2)
        sensor_repository.save(sensor3)

        # Act
        temp_sensors = sensor_repository.find_sensors_by_type("température")

        # Assert
        assert len(temp_sensors) == 2
        for sensor in temp_sensors:
            assert "température" in sensor.name.lower()

    def test_find_active_sensors(self, sensor_repository):
        """Test de recherche des capteurs actifs."""
        # Arrange
        sensor1 = Sensor("Capteur 1", "Salon")
        sensor2 = Sensor("Capteur 2", "Chambre")

        sensor_repository.save(sensor1)
        sensor_repository.save(sensor2)

        # Act
        active_sensors = sensor_repository.find_active_sensors()

        # Assert
        # Pour l'instant, cette méthode retourne tous les capteurs
        # TODO: Implémenter la logique réelle quand le modèle sera adapté
        assert len(active_sensors) == 2

    def test_find_inactive_sensors(self, sensor_repository):
        """Test de recherche des capteurs inactifs."""
        # Arrange
        sensor1 = Sensor("Capteur 1", "Salon")
        sensor2 = Sensor("Capteur 2", "Chambre")

        sensor_repository.save(sensor1)
        sensor_repository.save(sensor2)

        # Act
        inactive_sensors = sensor_repository.find_inactive_sensors()

        # Assert
        # Pour l'instant, cette méthode retourne une liste vide
        # TODO: Implémenter la logique réelle quand le modèle sera adapté
        assert len(inactive_sensors) == 0
