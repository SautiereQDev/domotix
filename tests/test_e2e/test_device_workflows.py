"""
Tests End-to-End (E2E) pour les workflows de gestion des dispositifs.

Ces tests valident les workflows complets de gestion des dispositifs
en testant l'intégration entre les couches contrôleurs, repositories,
et la persistance en base de données.

Test Coverage:
    - Workflows de création de dispositifs
    - Workflows de contrôle d'état
    - Workflows de recherche et requêtes
    - Workflows de suppression et nettoyage
    - Scenarios d'intégration multi-dispositifs
"""

# pylint: disable=redefined-outer-name

import os
import tempfile
from uuid import uuid4

import pytest

from domotix.core.database import create_session, create_tables
from domotix.core.factories import get_controller_factory
from domotix.core.state_manager import StateManager
from domotix.repositories.device_repository import DeviceRepository


@pytest.fixture
def isolated_test_db():
    """Fixture pour une base de données temporaire isolée pour chaque test."""
    # Créer une base de données temporaire unique pour ce test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    # Configuration de l'environnement
    original_db = os.environ.get("DOMOTIX_DB_PATH")
    os.environ["DOMOTIX_DB_PATH"] = db_path

    # Forcer la reconfiguration et initialiser
    from domotix.core.database import reconfigure_database

    reconfigure_database()
    StateManager.reset_instance()
    create_tables()

    yield db_path

    # Nettoyage après le test
    StateManager.reset_instance()
    try:
        os.unlink(db_path)
    except OSError:
        pass

    # Restaurer l'environnement
    if original_db:
        os.environ["DOMOTIX_DB_PATH"] = original_db
    else:
        os.environ.pop("DOMOTIX_DB_PATH", None)

    # Forcer une nouvelle reconfiguration
    reconfigure_database()


@pytest.fixture
def db_session_factory(isolated_test_db):
    """Factory pour créer des sessions de base de données."""

    def _create_session():
        return create_session()

    return _create_session


class TestDeviceLifecycleWorkflows:
    """Tests E2E pour les workflows complets de cycle de vie des dispositifs."""

    def test_light_complete_lifecycle(self, db_session_factory):
        """Test E2E: Cycle de vie complet d'une lampe."""
        session = db_session_factory()

        try:
            # Phase 1: Création
            controller = get_controller_factory().create_light_controller(session)
            light_id = controller.create_light("Lampe Lifecycle", "Test Room")

            assert light_id is not None
            assert isinstance(light_id, str)

            # Phase 2: Récupération et vérification
            light = controller.get_light(light_id)
            assert light is not None
            assert light.name == "Lampe Lifecycle"
            assert light.location == "Test Room"
            assert not light.is_on  # État initial OFF

            # Phase 3: Contrôle d'état - Allumer
            success = controller.turn_on(light_id)
            assert success is True

            # Vérifier l'état après allumage
            light_updated = controller.get_light(light_id)
            assert light_updated is not None
            assert light_updated.is_on is True

            # Phase 4: Contrôle d'état - Éteindre
            success = controller.turn_off(light_id)
            assert success is True

            # Vérifier l'état après extinction
            light_final = controller.get_light(light_id)
            assert light_final is not None
            assert light_final.is_on is False

            # Phase 5: Suppression
            success = controller.delete_light(light_id)
            assert success is True

            # Vérifier que la lampe n'existe plus
            deleted_light = controller.get_light(light_id)
            assert deleted_light is None

        finally:
            session.close()

    def test_shutter_complete_lifecycle(self, db_session_factory):
        """Test E2E: Cycle de vie complet d'un volet."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_shutter_controller(session)

            # Création
            shutter_id = controller.create_shutter("Volet Lifecycle", "Test Room")
            assert shutter_id is not None

            # Vérification initiale
            shutter = controller.get_shutter(shutter_id)
            assert shutter is not None
            assert shutter.name == "Volet Lifecycle"
            assert not shutter.is_open  # État initial fermé

            # Ouverture
            success = controller.open(shutter_id)
            assert success is True

            shutter_open = controller.get_shutter(shutter_id)
            assert shutter_open is not None
            assert shutter_open.is_open is True

            # Fermeture
            success = controller.close(shutter_id)
            assert success is True

            shutter_closed = controller.get_shutter(shutter_id)
            assert shutter_closed is not None
            assert shutter_closed.is_open is False

            # Suppression
            success = controller.delete_shutter(shutter_id)
            assert success is True

            deleted_shutter = controller.get_shutter(shutter_id)
            assert deleted_shutter is None

        finally:
            session.close()

    def test_sensor_complete_lifecycle(self, db_session_factory):
        """Test E2E: Cycle de vie complet d'un capteur."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_sensor_controller(session)

            # Création
            sensor_id = controller.create_sensor("Capteur Lifecycle", "Test Room")
            assert sensor_id is not None

            # Vérification initiale
            sensor = controller.get_sensor(sensor_id)
            assert sensor is not None
            assert sensor.name == "Capteur Lifecycle"
            # Vérifier l'état initial
            assert sensor.value is None  # Valeur initiale

            # Mise à jour de la valeur
            success = controller.update_value(sensor_id, 25.5)
            assert success is True

            sensor_updated = controller.get_sensor(sensor_id)
            assert sensor_updated is not None
            assert abs(sensor_updated.value - 25.5) < 0.001

            # Suppression
            success = controller.delete_sensor(sensor_id)
            assert success is True

            deleted_sensor = controller.get_sensor(sensor_id)
            assert deleted_sensor is None

        finally:
            session.close()


class TestMultiDeviceWorkflows:
    """Tests E2E pour les workflows impliquant plusieurs dispositifs."""

    def test_multi_device_creation_and_management(self, db_session_factory):
        """Test E2E: Création et gestion de plusieurs dispositifs."""
        session = db_session_factory()

        try:
            # Créer les contrôleurs
            light_controller = get_controller_factory().create_light_controller(session)
            shutter_controller = get_controller_factory().create_shutter_controller(
                session
            )
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )

            # Phase 1: Création de plusieurs dispositifs
            devices_created = {}

            # Lampes
            for i in range(3):
                light_id = light_controller.create_light(
                    f"Lampe {i + 1}", f"Room {i + 1}"
                )
                assert light_id is not None
                devices_created[f"light_{i + 1}"] = light_id

            # Volets
            for i in range(2):
                shutter_id = shutter_controller.create_shutter(
                    f"Volet {i + 1}", f"Room {i + 1}"
                )
                assert shutter_id is not None
                devices_created[f"shutter_{i + 1}"] = shutter_id

            # Capteurs
            for i in range(2):
                sensor_id = sensor_controller.create_sensor(
                    f"Capteur {i + 1}", f"Room {i + 1}"
                )
                assert sensor_id is not None
                devices_created[f"sensor_{i + 1}"] = sensor_id

            # Phase 2: Vérification via repository
            repo = DeviceRepository(session)
            all_devices = repo.find_all()

            assert len(all_devices) == 7  # 3 lampes + 2 volets + 2 capteurs

            # Vérifier la répartition par localisation
            room1_devices = repo.find_by_location("Room 1")
            assert len(room1_devices) == 3  # Une lampe, un volet, un capteur

            room2_devices = repo.find_by_location("Room 2")
            assert len(room2_devices) == 3  # Une lampe, un volet, un capteur

            room3_devices = repo.find_by_location("Room 3")
            assert len(room3_devices) == 1  # Une lampe

            # Phase 3: Contrôle groupé des lampes
            for i in range(3):
                light_id = devices_created[f"light_{i + 1}"]
                success = light_controller.turn_on(light_id)
                assert success is True

            # Vérifier que toutes les lampes sont allumées
            for i in range(3):
                light_id = devices_created[f"light_{i + 1}"]
                light = light_controller.get_light(light_id)
                assert light is not None
                assert light.is_on is True

            # Phase 4: Nettoyage sélectif - supprimer les dispositifs de Room 1
            room1_device_ids = [device.id for device in room1_devices]

            for device_id in room1_device_ids:
                device = repo.find_by_id(device_id)
                if device is not None:
                    if device.device_type.value == "LIGHT":
                        result = light_controller.delete_light(device_id)
                        assert result is True, f"Failed to delete light {device_id}"
                    elif device.device_type.value == "SHUTTER":
                        result = shutter_controller.delete_shutter(device_id)
                        assert result is True, f"Failed to delete shutter {device_id}"
                    elif device.device_type.value == "SENSOR":
                        result = sensor_controller.delete_sensor(device_id)
                        assert result is True, f"Failed to delete sensor {device_id}"

            # Faire un commit pour s'assurer que les suppressions sont persistées
            session.commit()

            # Vérifier la suppression
            remaining_devices = repo.find_all()
            assert len(remaining_devices) == 4  # 7 - 3 (Room 1)

            room1_remaining = repo.find_by_location("Room 1")
            assert len(room1_remaining) == 0

        finally:
            session.close()

    def test_concurrent_device_operations(self, db_session_factory):
        """Test E2E: Opérations concurrentes sur les dispositifs."""
        # Ce test simule des opérations qui pourraient arriver en parallèle
        # dans une vraie application

        session1 = db_session_factory()
        session2 = db_session_factory()

        try:
            controller1 = get_controller_factory().create_light_controller(session1)
            controller2 = get_controller_factory().create_light_controller(session2)

            # Session 1: Créer une lampe
            light_id = controller1.create_light("Lampe Concurrente", "Shared Room")
            assert light_id is not None

            # Session 2: Essayer de récupérer la lampe (doit marcher)
            light_from_session2 = controller2.get_light(light_id)
            assert light_from_session2 is not None
            assert light_from_session2.name == "Lampe Concurrente"

            # Session 1: Allumer la lampe
            success1 = controller1.turn_on(light_id)
            assert success1 is True

            # Session 2: Vérifier l'état (doit refléter le changement)
            light_updated = controller2.get_light(light_id)
            assert light_updated is not None
            assert light_updated.is_on is True

            # Session 2: Éteindre la lampe
            success2 = controller2.turn_off(light_id)
            assert success2 is True

            # Session 1: Vérifier l'état final
            light_final = controller1.get_light(light_id)
            assert light_final is not None
            assert light_final.is_on is False

        finally:
            session1.close()
            session2.close()


class TestDeviceSearchAndQueryWorkflows:
    """Tests E2E pour les workflows de recherche et requêtes complexes."""

    def test_complex_search_workflows(self, db_session_factory):
        """Test E2E: Workflows de recherche complexes."""
        session = db_session_factory()

        try:
            # Préparer les données de test
            light_controller = get_controller_factory().create_light_controller(session)
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )

            # Créer des dispositifs avec patterns spécifiques
            test_devices = [
                ("Lampe Principale Salon", "Salon", "light"),
                ("Lampe Secondaire Salon", "Salon", "light"),
                ("Lampe Chambre Parents", "Chambre", "light"),
                ("Capteur Température Salon", "Salon", "sensor"),
                ("Capteur Humidité Chambre", "Chambre", "sensor"),
            ]

            device_ids = {}
            for name, location, device_type in test_devices:
                if device_type == "light":
                    device_id = light_controller.create_light(name, location)
                else:  # sensor
                    device_id = sensor_controller.create_sensor(name, location)

                assert device_id is not None
                device_ids[name] = device_id

            # Tests de recherche via repository
            repo = DeviceRepository(session)

            # Test 1: Recherche par nom partiel
            salon_lights = repo.search_by_name("Salon")
            salon_device_names = [d.name for d in salon_lights]

            assert "Lampe Principale Salon" in salon_device_names
            assert "Lampe Secondaire Salon" in salon_device_names
            assert "Capteur Température Salon" in salon_device_names
            assert "Lampe Chambre Parents" not in salon_device_names

            # Test 2: Recherche par localisation
            chambre_devices = repo.find_by_location("Chambre")
            assert len(chambre_devices) == 2

            chambre_names = [d.name for d in chambre_devices]
            assert "Lampe Chambre Parents" in chambre_names
            assert "Capteur Humidité Chambre" in chambre_names

            # Test 3: Recherche par type via contrôleurs spécialisés
            # Mise à jour des valeurs des capteurs pour tester les requêtes
            temp_sensor_id = device_ids["Capteur Température Salon"]
            humidity_sensor_id = device_ids["Capteur Humidité Chambre"]

            sensor_controller.update_value(temp_sensor_id, 22.5)
            sensor_controller.update_value(humidity_sensor_id, 65.0)

            # Vérifier les valeurs via recherche
            from domotix.globals.enums import DeviceType

            all_sensors = repo.find_by_type(DeviceType.SENSOR)
            sensor_values = {s.name: s.value for s in all_sensors}

            assert abs(sensor_values["Capteur Température Salon"] - 22.5) < 0.001
            assert abs(sensor_values["Capteur Humidité Chambre"] - 65.0) < 0.001

            # Test 4: Requête combinée - tous les dispositifs du salon
            salon_devices = repo.find_by_location("Salon")
            assert len(salon_devices) == 3  # 2 lampes + 1 capteur

            salon_lights_only = [
                d for d in salon_devices if d.device_type.value == "LIGHT"
            ]
            assert len(salon_lights_only) == 2

        finally:
            session.close()


class TestDeviceDataIntegrityWorkflows:
    """Tests E2E pour l'intégrité des données lors des workflows complexes."""

    def test_data_consistency_across_operations(self, db_session_factory):
        """Test E2E: Consistance des données lors d'opérations complexes."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Phase 1: Création et vérification immédiate
            light_id = controller.create_light("Lampe Consistance", "Test Consistency")

            # Vérifier via contrôleur
            light_via_controller = controller.get_light(light_id)
            assert light_via_controller is not None

            # Vérifier via repository
            light_via_repo = repo.find_by_id(light_id)
            assert light_via_repo is not None

            # Les données doivent être identiques
            assert light_via_controller.id == light_via_repo.id
            assert light_via_controller.name == light_via_repo.name
            assert light_via_controller.location == light_via_repo.location
            assert light_via_controller.is_on == light_via_repo.is_on

            # Phase 2: Modification et vérification de consistance
            success = controller.turn_on(light_id)
            assert success is True

            # Vérifier que les deux méthodes d'accès voient le changement
            light_via_controller_updated = controller.get_light(light_id)
            light_via_repo_updated = repo.find_by_id(light_id)

            assert light_via_controller_updated.is_on is True
            assert light_via_repo_updated.is_on is True

            # Phase 3: Comptage et intégrité des collections
            # Créer plusieurs lampes
            additional_lights = []
            for i in range(5):
                light_id_extra = controller.create_light(
                    f"Lampe {i}", "Test Consistency"
                )
                additional_lights.append(light_id_extra)

            # Vérifier le comptage
            total_devices = repo.count_all()
            assert total_devices == 6  # 1 initiale + 5 additionnelles

            consistency_devices = repo.find_by_location("Test Consistency")
            assert len(consistency_devices) == 6

            # Phase 4: Suppression et vérification d'intégrité
            # Supprimer quelques lampes
            for light_id_to_delete in additional_lights[:3]:
                success = controller.delete_light(light_id_to_delete)
                assert success is True

            # Vérifier que les comptages sont cohérents
            remaining_total = repo.count_all()
            assert remaining_total == 3  # 6 - 3 supprimées

            remaining_in_location = repo.find_by_location("Test Consistency")
            assert len(remaining_in_location) == 3

            # Vérifier que les bonnes lampes ont été supprimées
            for deleted_id in additional_lights[:3]:
                deleted_light = controller.get_light(deleted_id)
                assert deleted_light is None

            # Vérifier que les lampes restantes existent toujours
            for remaining_id in [light_id] + additional_lights[3:]:
                remaining_light = controller.get_light(remaining_id)
                assert remaining_light is not None

        finally:
            session.close()

    def test_error_recovery_workflows(self, db_session_factory):
        """Test E2E: Workflows de récupération d'erreur."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Test 1: Tentative d'opération sur dispositif inexistant
            fake_id = str(uuid4())

            # Ces opérations doivent échouer gracieusement
            result = controller.get_light(fake_id)
            assert result is None

            turn_on_result = controller.turn_on(fake_id)
            assert turn_on_result is False

            delete_result = controller.delete_light(fake_id)
            assert delete_result is False

            # Test 2: Vérifier que les erreurs n'affectent pas les vraies données
            # Créer une vraie lampe
            real_light_id = controller.create_light("Lampe Réelle", "Real Room")
            assert real_light_id is not None

            # Tenter des opérations invalides
            controller.turn_on(fake_id)  # Échec
            controller.get_light("invalid-id")  # Échec

            # Vérifier que la vraie lampe n'est pas affectée
            real_light = controller.get_light(real_light_id)
            assert real_light is not None
            assert real_light.name == "Lampe Réelle"
            assert real_light.location == "Real Room"

            # Test 3: Opération valide après erreurs
            success = controller.turn_on(real_light_id)
            assert success is True

            updated_light = controller.get_light(real_light_id)
            assert updated_light is not None
            assert updated_light.is_on is True

        finally:
            session.close()
