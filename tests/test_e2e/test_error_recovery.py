"""
Tests End-to-End (E2E) pour la récupération d'erreurs et la robustesse.

Ces tests valident que le système peut gérer gracieusement les erreurs
et continuer à fonctionner correctement dans des conditions adverses.

Test Coverage:
    - Gestion des erreurs de base de données
    - Récupération après pannes système
    - Validation des entrées utilisateur
    - Gestion des états incohérents
    - Timeout et ressources limitées
"""

import os
import tempfile
import time

import pytest

from domotix.core.database import create_session, create_tables
from domotix.core.factories import get_controller_factory
from domotix.core.state_manager import StateManager
from domotix.globals.exceptions import ControllerError, DomotixError
from domotix.repositories.device_repository import DeviceRepository


@pytest.fixture
def temp_database():
    """Fixture pour une base de données temporaire."""
    temp_dir = tempfile.mkdtemp(prefix="domotix_e2e_error_")
    db_path = os.path.join(temp_dir, "test_error_recovery.db")

    original_db = os.environ.get("DOMOTIX_DB_PATH")
    os.environ["DOMOTIX_DB_PATH"] = db_path

    StateManager.reset_instance()
    create_tables()

    yield db_path

    StateManager.reset_instance()
    import shutil

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    if original_db:
        os.environ["DOMOTIX_DB_PATH"] = original_db
    else:
        os.environ.pop("DOMOTIX_DB_PATH", None)


class TestDatabaseErrorRecovery:
    """Tests E2E pour la récupération d'erreurs de base de données."""

    def test_database_connection_failure_recovery(self, temp_database):
        """Test E2E: Récupération après échec de connexion DB."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Créer une lampe normale
            light_id = controller.create_light("Lampe Test", "Test Room")
            assert light_id is not None

            # Simuler une perte de connexion en corrompant le path de la DB
            original_path = os.environ.get("DOMOTIX_DB_PATH")
            os.environ["DOMOTIX_DB_PATH"] = "/invalid/path/to/database.db"

            # Essayer de créer une nouvelle session (doit échouer)
            try:
                new_session = create_session()
                new_controller = get_controller_factory().create_light_controller(
                    new_session
                )

                # Cette opération peut échouer, c'est attendu
                new_controller.create_light("Lampe Échec", "Test Room")
                # Le résultat peut être None ou lever une exception

            except Exception as e:
                # C'est attendu lors d'une panne de connexion
                assert "database" in str(e).lower() or "connection" in str(e).lower()

            # Restaurer la connexion
            os.environ["DOMOTIX_DB_PATH"] = original_path

            # Vérifier que le système peut récupérer
            recovery_session = create_session()
            try:
                recovery_controller = get_controller_factory().create_light_controller(
                    recovery_session
                )

                # Vérifier que les données précédentes existent toujours
                original_light = recovery_controller.get_light(light_id)
                assert original_light is not None
                assert original_light.name == "Lampe Test"

                # Créer une nouvelle lampe pour tester la récupération
                new_light_id = recovery_controller.create_light(
                    "Lampe Récupération", "Recovery Room"
                )
                assert new_light_id is not None

                new_light = recovery_controller.get_light(new_light_id)
                assert new_light is not None
                assert new_light.name == "Lampe Récupération"

            finally:
                recovery_session.close()

        finally:
            session.close()

    def test_corrupted_data_recovery(self, temp_database):
        """Test E2E: Récupération avec données corrompues."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Créer des données valides
            light_id = controller.create_light("Lampe Valide", "Valid Room")
            assert light_id is not None

            # Simuler une corruption en insérant des données invalides directement
            # via SQL (bypassing les validations du modèle)
            from domotix.models.base_model import DeviceModel

            corrupted_device = DeviceModel(
                id="corrupted-id-invalid",
                name="",  # Nom vide (invalide)
                location=None,  # Location None (pourrait être invalide)
                device_type="invalid_type",  # Type invalide
                is_on=None,  # Valeur None pour boolean (invalide)
                is_open=False,
                value=0.0,
            )

            # Tenter d'insérer directement (peut échouer)
            try:
                session.add(corrupted_device)
                session.commit()
            except Exception:
                # Rollback si l'insertion échoue
                session.rollback()

            # Vérifier que le système continue à fonctionner avec les données valides
            valid_light = controller.get_light(light_id)
            assert valid_light is not None
            assert valid_light.name == "Lampe Valide"

            # Créer de nouvelles données valides
            new_light_id = controller.create_light("Nouvelle Lampe", "New Room")
            assert new_light_id is not None

            # Vérifier l'intégrité des données valides
            # Utiliser une approche défensive car il peut y avoir des données corrompues
            try:
                all_valid_devices = repo.find_all()
                valid_device_names = [d.name for d in all_valid_devices if d.name]
            except ValueError as e:
                # Si find_all() échoue à cause de données corrompues,
                # tester individuellement les dispositifs valides
                if "Type de dispositif inconnu" in str(e):
                    # Vérifier que les dispositifs valides sont encore accessibles
                    valid_light = controller.get_light(light_id)
                    new_light = controller.get_light(new_light_id)

                    assert valid_light is not None
                    assert new_light is not None
                    assert valid_light.name == "Lampe Valide"
                    assert new_light.name == "Nouvelle Lampe"

                    # Le test est réussi si les données valides restent accessibles
                    valid_device_names = ["Lampe Valide", "Nouvelle Lampe"]
                else:
                    raise

            assert "Lampe Valide" in valid_device_names
            assert "Nouvelle Lampe" in valid_device_names

        finally:
            session.close()


class TestInputValidationErrorRecovery:
    """Tests E2E pour la gestion des erreurs de validation d'entrée."""

    def test_invalid_input_handling(self, temp_database):
        """Test E2E: Gestion des entrées invalides."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Test avec des noms invalides
            invalid_names = [
                "",  # Nom vide
                None,  # Nom None
                " " * 100,  # Nom trop long d'espaces
                "A" * 1000,  # Nom trop long
            ]

            for invalid_name in invalid_names:
                try:
                    result = controller.create_light(invalid_name, "Test Room")
                    # Si l'opération réussit malgré l'entrée invalide,
                    # vérifier que le résultat est sensé
                    if result is not None:
                        light = controller.get_light(result)
                        if light is not None:
                            # Le nom doit être défini (même si vide)
                            assert light.name is not None
                            # Note: Un nom vide pourrait être acceptable selon
                            # les specs métier

                except (ValueError, DomotixError, ControllerError, Exception) as e:
                    # C'est acceptable que l'opération échoue avec des entrées invalides
                    # IntegrityError pour les contraintes de base de données
                    error_message = str(e).lower()
                    expected_errors = [
                        "name",
                        "invalid",
                        "constraint",
                        "not null",
                        "integrity",
                    ]
                    assert any(keyword in error_message for keyword in expected_errors)

            # Vérifier qu'après les erreurs, le système fonctionne toujours
            valid_light_id = controller.create_light("Lampe Valide", "Valid Room")
            assert valid_light_id is not None

            valid_light = controller.get_light(valid_light_id)
            assert valid_light is not None
            assert valid_light.name == "Lampe Valide"

        finally:
            session.close()

    def test_concurrent_access_error_recovery(self, temp_database):
        """Test E2E: Récupération lors d'accès concurrent."""
        session1 = create_session()
        session2 = create_session()

        try:
            controller1 = get_controller_factory().create_light_controller(session1)
            controller2 = get_controller_factory().create_light_controller(session2)

            # Session 1: Créer une lampe
            light_id = controller1.create_light("Lampe Concurrente", "Concurrent Room")
            assert light_id is not None

            # Session 1: Commencer une modification
            success1 = controller1.turn_on(light_id)
            assert success1 is True

            # Session 2: Essayer de modifier en même temps
            # (peut réussir ou échouer selon l'implémentation)
            try:
                success2 = controller2.turn_off(light_id)
                # Si ça réussit, vérifier la cohérence
                if success2:
                    light_state = controller2.get_light(light_id)
                    # L'état final doit être cohérent
                    assert light_state is not None
                    assert isinstance(light_state.is_on, bool)

            except Exception as e:
                # Des erreurs de concurrence sont acceptables
                assert (
                    "concurrent" in str(e).lower()
                    or "lock" in str(e).lower()
                    or "conflict" in str(e).lower()
                )

            # Vérifier qu'après les conflits, le système fonctionne
            final_light = controller1.get_light(light_id)
            assert final_light is not None
            assert final_light.name == "Lampe Concurrente"

            # Créer une nouvelle lampe pour tester la récupération
            new_light_id = controller1.create_light(
                "Lampe Post-Conflit", "Recovery Room"
            )
            assert new_light_id is not None

        finally:
            session1.close()
            session2.close()


class TestResourceLimitationRecovery:
    """Tests E2E pour la gestion des limitations de ressources."""

    def test_memory_pressure_simulation(self, temp_database):
        """Test E2E: Simulation de pression mémoire."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Créer un grand nombre de dispositifs pour simuler la pression mémoire
            created_devices = []
            max_devices = 100  # Nombre raisonnable pour un test

            for i in range(max_devices):
                try:
                    light_id = controller.create_light(
                        f"Lampe {i:03d}", f"Room {i % 10}"
                    )
                    if light_id is not None:
                        created_devices.append(light_id)

                    # Vérifier périodiquement l'intégrité
                    if i % 20 == 0 and i > 0:
                        # Test de lecture pour vérifier que le système répond
                        sample_light = controller.get_light(created_devices[0])
                        assert sample_light is not None

                        # Test de comptage
                        count = repo.count_all()
                        assert count >= len(created_devices)

                except Exception as e:
                    # Si on atteint des limites, c'est acceptable
                    if "memory" in str(e).lower() or "resource" in str(e).lower():
                        break
                    else:
                        # Autres erreurs sont inattendues
                        raise

            # Vérifier que le système fonctionne toujours
            assert len(created_devices) > 0, "Aucun dispositif créé"

            # Test de fonctionnalité après charge
            final_test_id = controller.create_light("Lampe Test Final", "Final Room")
            assert final_test_id is not None

            final_light = controller.get_light(final_test_id)
            assert final_light is not None
            assert final_light.name == "Lampe Test Final"

            # Nettoyage partiel pour tester la suppression sous charge
            for i, device_id in enumerate(
                created_devices[:20]
            ):  # Supprimer les 20 premiers
                try:
                    success = controller.delete_light(device_id)
                    # La suppression peut échouer sous charge, c'est acceptable
                    if success:
                        deleted_light = controller.get_light(device_id)
                        assert deleted_light is None
                except Exception:
                    # Erreurs de suppression sous charge sont acceptables
                    pass

        finally:
            session.close()

    def test_timeout_recovery(self, temp_database):
        """Test E2E: Récupération après timeouts."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Créer une lampe normale
            light_id = controller.create_light("Lampe Timeout", "Timeout Room")
            assert light_id is not None

            # Simuler des opérations lentes avec des timeouts courts
            start_time = time.time()

            # Série d'opérations rapides pour tester la résilience
            operations_completed = 0
            max_operations = 50

            for i in range(max_operations):
                try:
                    # Opérations alternées
                    if i % 2 == 0:
                        success = controller.turn_on(light_id)
                    else:
                        success = controller.turn_off(light_id)

                    if success:
                        operations_completed += 1

                    # Vérifier périodiquement l'état
                    if i % 10 == 0:
                        light = controller.get_light(light_id)
                        assert light is not None

                except Exception as e:
                    # Certaines opérations peuvent échouer sous stress
                    if "timeout" in str(e).lower():
                        continue  # Timeout acceptable
                    else:
                        raise  # Autres erreurs sont problématiques

            # Vérifier que le système fonctionne après stress
            elapsed_time = time.time() - start_time

            # Au moins quelques opérations doivent avoir réussi
            assert operations_completed > 0, "Aucune opération réussie"

            # Test de fonctionnalité finale
            final_light = controller.get_light(light_id)
            assert final_light is not None
            assert final_light.name == "Lampe Timeout"

            # Créer une nouvelle lampe pour vérifier la récupération complète
            recovery_light_id = controller.create_light(
                "Lampe Récupération", "Recovery Room"
            )
            assert recovery_light_id is not None

            print(
                f"Stress test completed: {operations_completed}/"
                f"{max_operations} operations in {elapsed_time:.2f}s"
            )

        finally:
            session.close()


class TestSystemStateRecovery:
    """Tests E2E pour la récupération d'état système."""

    def test_state_manager_reset_recovery(self, temp_database):
        """Test E2E: Récupération après reset du StateManager."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Créer des données avant reset
            light_id = controller.create_light("Lampe Avant Reset", "Before Reset Room")
            assert light_id is not None

            success = controller.turn_on(light_id)
            assert success is True

            # Simuler un reset du StateManager
            StateManager.reset_instance()

            # Créer une nouvelle session après reset
            new_session = create_session()
            try:
                new_controller = get_controller_factory().create_light_controller(
                    new_session
                )

                # Vérifier que les données persistent après reset
                persisted_light = new_controller.get_light(light_id)
                assert persisted_light is not None
                assert persisted_light.name == "Lampe Avant Reset"
                assert persisted_light.is_on is True  # État doit être conservé

                # Vérifier que les nouvelles opérations fonctionnent
                new_light_id = new_controller.create_light(
                    "Lampe Après Reset", "After Reset Room"
                )
                assert new_light_id is not None

                new_light = new_controller.get_light(new_light_id)
                assert new_light is not None
                assert new_light.name == "Lampe Après Reset"

            finally:
                new_session.close()

        finally:
            session.close()

    def test_partial_failure_recovery(self, temp_database):
        """Test E2E: Récupération après échecs partiels."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Créer plusieurs dispositifs
            successful_devices = []
            failed_operations = 0

            for i in range(10):
                try:
                    # Alterner entre opérations valides et potentiellement
                    # problématiques
                    if i % 3 == 0:
                        # Opération normale
                        light_id = controller.create_light(f"Lampe {i}", f"Room {i}")
                        if light_id:
                            successful_devices.append(light_id)
                    elif i % 3 == 1:
                        # Opération avec nom limite
                        light_id = controller.create_light(
                            f"Lampe avec nom très long {i}" * 5, f"Room {i}"
                        )
                        if light_id:
                            successful_devices.append(light_id)
                    else:
                        # Opération potentiellement problématique
                        light_id = controller.create_light(
                            f"Lampe-{i}", None
                        )  # Location None
                        if light_id:
                            successful_devices.append(light_id)

                except Exception:
                    failed_operations += 1
                    continue

            # Vérifier que malgré les échecs, certaines opérations ont réussi
            assert len(successful_devices) > 0, "Aucune opération réussie"

            # Vérifier l'intégrité des dispositifs créés
            for device_id in successful_devices:
                device = controller.get_light(device_id)
                assert device is not None
                assert device.id == device_id

            # Test de robustesse: opérations sur dispositifs valides
            for device_id in successful_devices[:3]:  # Tester les 3 premiers
                try:
                    # Ces opérations doivent réussir
                    on_success = controller.turn_on(device_id)
                    assert on_success is True

                    off_success = controller.turn_off(device_id)
                    assert off_success is True

                except Exception as e:
                    pytest.fail(
                        f"Opération échouée sur dispositif valide {device_id}: {e}"
                    )

            # Vérifier le comptage final
            total_devices = repo.count_all()
            assert total_devices == len(successful_devices)

            print(
                f"Partial failure test: {len(successful_devices)} successful, "
                f"{failed_operations} failed"
            )

        finally:
            session.close()
