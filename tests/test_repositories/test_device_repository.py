"""
Tests pour le DeviceRepository.

Ce module contient tous les tests unitaires pour le repository générique
des dispositifs domotiques.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domotix.core.database import Base
from domotix.globals.enums import DeviceType
from domotix.models import Light, Sensor, Shutter
from domotix.repositories.device_repository import DeviceRepository


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
def device_repository(test_session):
    """Crée une instance de DeviceRepository pour les tests."""
    return DeviceRepository(test_session)


@pytest.fixture
def sample_light():
    """Crée une lampe de test."""
    return Light("Lampe test", "Salon")


@pytest.fixture
def sample_shutter():
    """Crée un volet de test."""
    return Shutter("Volet test", "Chambre")


@pytest.fixture
def sample_sensor():
    """Crée un capteur de test."""
    return Sensor("Capteur test", "Jardin")


class TestDeviceRepository:
    """Tests pour la classe DeviceRepository."""

    def test_save_device(self, device_repository, sample_light):
        """Test de sauvegarde d'un dispositif."""
        # Act
        result = device_repository.save(sample_light)

        # Assert
        assert result is not None
        assert result.id == sample_light.id
        assert result.name == sample_light.name
        assert result.device_type == DeviceType.LIGHT

    def test_find_by_id_existing(self, device_repository, sample_light):
        """Test de recherche d'un dispositif existant par ID."""
        # Arrange
        device_repository.save(sample_light)

        # Act
        result = device_repository.find_by_id(sample_light.id)

        # Assert
        assert result is not None
        assert result.id == sample_light.id
        assert result.name == sample_light.name

    def test_find_by_id_non_existing(self, device_repository):
        """Test de recherche d'un dispositif inexistant."""
        # Act
        result = device_repository.find_by_id("non-existent-id")

        # Assert
        assert result is None

    def test_find_all_empty(self, device_repository):
        """Test de récupération de tous les dispositifs (liste vide)."""
        # Act
        result = device_repository.find_all()

        # Assert
        assert result == []

    def test_find_all_with_devices(
        self, device_repository, sample_light, sample_shutter
    ):
        """Test de récupération de tous les dispositifs."""
        # Arrange
        device_repository.save(sample_light)
        device_repository.save(sample_shutter)

        # Act
        result = device_repository.find_all()

        # Assert
        assert len(result) == 2
        device_ids = [device.id for device in result]
        assert sample_light.id in device_ids
        assert sample_shutter.id in device_ids

    def test_update_device(self, device_repository, sample_light):
        """Test de mise à jour d'un dispositif."""
        # Arrange
        device_repository.save(sample_light)
        sample_light.name = "Nouveau nom"
        sample_light.turn_on()

        # Act
        result = device_repository.update(sample_light)

        # Assert
        assert result is True
        updated_device = device_repository.find_by_id(sample_light.id)
        assert updated_device.name == "Nouveau nom"

    def test_update_non_existing_device(self, device_repository, sample_light):
        """Test de mise à jour d'un dispositif inexistant."""
        # Act
        result = device_repository.update(sample_light)

        # Assert
        assert result is False

    def test_delete_existing_device(self, device_repository, sample_light):
        """Test de suppression d'un dispositif existant."""
        # Arrange
        device_repository.save(sample_light)

        # Act
        result = device_repository.delete(sample_light.id)

        # Assert
        assert result is True
        deleted_device = device_repository.find_by_id(sample_light.id)
        assert deleted_device is None

    def test_delete_non_existing_device(self, device_repository):
        """Test de suppression d'un dispositif inexistant."""
        # Act
        result = device_repository.delete("non-existent-id")

        # Assert
        assert result is False

    def test_save_multiple_device_types(
        self, device_repository, sample_light, sample_shutter, sample_sensor
    ):
        """Test de sauvegarde de différents types de dispositifs."""
        # Act
        light_result = device_repository.save(sample_light)
        shutter_result = device_repository.save(sample_shutter)
        sensor_result = device_repository.save(sample_sensor)

        # Assert
        assert light_result.device_type == DeviceType.LIGHT
        assert shutter_result.device_type == DeviceType.SHUTTER
        assert sensor_result.device_type == DeviceType.SENSOR

        all_devices = device_repository.find_all()
        assert len(all_devices) == 3

    def test_rollback_on_update_error(
        self, device_repository, sample_light, monkeypatch
    ):
        """Test du rollback en cas d'erreur lors de la mise à jour."""
        # Arrange
        device_repository.save(sample_light)

        # Simuler une erreur lors du commit
        def mock_commit():
            raise Exception("Database error")

        monkeypatch.setattr(device_repository.session, "commit", mock_commit)

        # Act
        result = device_repository.update(sample_light)

        # Assert
        assert result is False

    def test_rollback_on_delete_error(
        self, device_repository, sample_light, monkeypatch
    ):
        """Test du rollback en cas d'erreur lors de la suppression."""
        # Arrange
        device_repository.save(sample_light)

        # Simuler une erreur lors du commit
        def mock_commit():
            raise Exception("Database error")

        monkeypatch.setattr(device_repository.session, "commit", mock_commit)

        # Act
        result = device_repository.delete(sample_light.id)

        # Assert
        assert result is False
