"""
Configuration partagée pour tous les tests.

Ce module contient les fixtures et configurations communes
utilisées par l'ensemble de la suite de tests.
"""

import tempfile
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domotix.core.database import Base
from domotix.models import Light, Sensor, Shutter


@pytest.fixture
def test_engine():
    """Crée un moteur de base de données en mémoire pour les tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Crée une session de test avec rollback automatique."""
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def temp_db():
    """Crée une base de données temporaire sur disque."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    yield db_path

    # Nettoyage
    import os

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_light():
    """Crée une lampe d'exemple pour les tests."""
    light = Light("Lampe test", "Salon")
    light.id = 1
    return light


@pytest.fixture
def sample_shutter():
    """Crée un volet d'exemple pour les tests."""
    shutter = Shutter("Volet test", "Chambre")
    shutter.id = 2
    return shutter


@pytest.fixture
def sample_sensor():
    """Crée un capteur d'exemple pour les tests."""
    sensor = Sensor("Capteur test", "Salon")
    sensor.id = 3
    return sensor


@pytest.fixture
def sample_devices(sample_light, sample_shutter, sample_sensor):
    """Retourne une liste de dispositifs d'exemple."""
    return [sample_light, sample_shutter, sample_sensor]


@pytest.fixture
def mock_session():
    """Crée une session mockée pour les tests unitaires."""
    session = Mock()
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.all.return_value = []
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_repository():
    """Crée un repository mocké pour les tests unitaires."""
    repo = Mock()
    repo.save = Mock()
    repo.find_by_id = Mock(return_value=None)
    repo.find_all = Mock(return_value=[])
    repo.delete = Mock(return_value=True)
    repo.update = Mock(return_value=True)
    return repo


@pytest.fixture
def mock_controller():
    """Crée un contrôleur mocké pour les tests unitaires."""
    controller = Mock()
    controller.create_light = Mock(return_value=1)
    controller.get_light = Mock(return_value=None)
    controller.get_all_lights = Mock(return_value=[])
    controller.turn_on = Mock(return_value=True)
    controller.turn_off = Mock(return_value=True)
    controller.toggle = Mock(return_value=True)
    controller.delete_light = Mock(return_value=True)
    return controller


@pytest.fixture(autouse=True)
def clear_singletons():
    """Nettoie les singletons entre les tests."""
    # Si des singletons sont utilisés, les réinitialiser ici
    yield
    # Nettoyage après le test


@pytest.fixture
def capture_output():
    """Capture la sortie standard pour les tests CLI."""
    import sys
    from io import StringIO

    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output

    yield captured_output

    sys.stdout = old_stdout
