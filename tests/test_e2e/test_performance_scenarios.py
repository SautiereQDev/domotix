"""
Tests End-to-End (E2E) pour les scenarios de performance du système Domotix.

Ces tests valident que le système maintient des performances acceptables
sous différentes charges et conditions d'utilisation réelles.

Test Coverage:
    - Performance de création de dispositifs en masse
    - Performance des requêtes avec grande quantité de données
    - Performance des opérations d'état fréquentes
    - Benchmarks de temps de réponse
    - Tests de scalabilité
"""

# pylint: disable=redefined-outer-name

import os
import statistics
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import pytest

from domotix.core.database import create_session, create_tables
from domotix.core.factories import get_controller_factory
from domotix.core.state_manager import StateManager
from domotix.repositories.device_repository import DeviceRepository


@pytest.fixture
def perf_test_db():
    """Fixture pour une base de données temporaire dédiée aux tests de performance."""
    temp_dir = tempfile.mkdtemp(prefix="domotix_e2e_perf_")
    db_path = os.path.join(temp_dir, "test_performance.db")

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


class PerformanceTimer:
    """Helper pour mesurer les performances."""

    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}

    def time_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Mesure le temps d'exécution d'une opération."""
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()

        duration = end_time - start_time

        if operation_name not in self.measurements:
            self.measurements[operation_name] = []
        self.measurements[operation_name].append(duration)

        return result, duration

    def get_stats(self, operation_name: str) -> Dict[str, float]:
        """Obtient les statistiques pour une opération."""
        if operation_name not in self.measurements:
            return {}

        measurements = self.measurements[operation_name]
        return {
            "count": len(measurements),
            "total": sum(measurements),
            "average": statistics.mean(measurements),
            "median": statistics.median(measurements),
            "min": min(measurements),
            "max": max(measurements),
            "stdev": statistics.stdev(measurements) if len(measurements) > 1 else 0,
        }

    def print_summary(self):
        """Affiche un résumé des performances."""
        print("\n" + "=" * 60)
        print("RÉSUMÉ DES PERFORMANCES")
        print("=" * 60)

        for operation, stats in [(op, self.get_stats(op)) for op in self.measurements]:
            if stats:
                print(f"\n{operation}:")
                print(f"  Opérations: {stats['count']}")
                print(f"  Temps total: {stats['total']:.3f}s")
                print(f"  Moyenne: {stats['average'] * 1000:.2f}ms")
                print(f"  Médiane: {stats['median'] * 1000:.2f}ms")
                print(
                    f"  Min/Max: {stats['min'] * 1000:.2f}ms / "
                    f"{stats['max'] * 1000:.2f}ms"
                )
                if stats["stdev"] > 0:
                    print(f"  Écart-type: {stats['stdev'] * 1000:.2f}ms")


@pytest.fixture
def perf_timer():
    """Fixture pour le timer de performance."""
    timer = PerformanceTimer()
    yield timer
    timer.print_summary()


class TestDeviceCreationPerformance:
    """Tests de performance pour la création de dispositifs."""

    def test_bulk_device_creation_performance(self, perf_test_db, perf_timer):
        """Test E2E: Performance de création de dispositifs en masse."""
        session = create_session()

        try:
            light_controller = get_controller_factory().create_light_controller(session)
            shutter_controller = get_controller_factory().create_shutter_controller(
                session
            )
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )

            # Test de création en masse pour chaque type
            num_devices_per_type = 50

            # Création de lampes
            light_ids = []
            for i in range(num_devices_per_type):
                light_id, duration = perf_timer.time_operation(
                    "create_light",
                    light_controller.create_light,
                    f"Lampe {i:03d}",
                    f"Room {i % 10}",
                )
                if light_id:
                    light_ids.append(light_id)

            # Création de volets
            shutter_ids = []
            for i in range(num_devices_per_type):
                shutter_id, duration = perf_timer.time_operation(
                    "create_shutter",
                    shutter_controller.create_shutter,
                    f"Volet {i:03d}",
                    f"Room {i % 10}",
                )
                if shutter_id:
                    shutter_ids.append(shutter_id)

            # Création de capteurs
            sensor_ids = []
            for i in range(num_devices_per_type):
                sensor_id, duration = perf_timer.time_operation(
                    "create_sensor",
                    sensor_controller.create_sensor,
                    f"Capteur {i:03d}",
                    f"Room {i % 10}",
                )
                if sensor_id:
                    sensor_ids.append(sensor_id)

            # Vérifications de performance
            light_stats = perf_timer.get_stats("create_light")
            shutter_stats = perf_timer.get_stats("create_shutter")
            sensor_stats = perf_timer.get_stats("create_sensor")

            # Assertions de performance (seuils raisonnables)
            assert (
                light_stats["average"] < 1.0
            ), f"Création lampe trop lente: {light_stats['average']:.3f}s"
            assert (
                shutter_stats["average"] < 1.0
            ), f"Création volet trop lente: {shutter_stats['average']:.3f}s"
            assert (
                sensor_stats["average"] < 1.0
            ), f"Création capteur trop lente: {sensor_stats['average']:.3f}s"

            # Vérification d'intégrité
            assert len(light_ids) == num_devices_per_type
            assert len(shutter_ids) == num_devices_per_type
            assert len(sensor_ids) == num_devices_per_type

            # Test de lecture après création
            repo = DeviceRepository(session)
            total_devices, _ = perf_timer.time_operation(
                "count_all_devices", repo.count_all
            )

            expected_total = num_devices_per_type * 3
            assert total_devices == expected_total

        finally:
            session.close()

    def test_sequential_vs_batch_creation(self, perf_test_db, perf_timer):
        """Test E2E: Comparaison création séquentielle vs batch."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Test séquentiel
            sequential_ids = []
            num_devices = 20

            start_time = time.time()
            for i in range(num_devices):
                light_id, _ = perf_timer.time_operation(
                    "sequential_creation",
                    controller.create_light,
                    f"Lampe Seq {i}",
                    "Sequential Room",
                )
                if light_id:
                    sequential_ids.append(light_id)
            sequential_total_time = time.time() - start_time

            # Simulation de création "batch" (création rapide successive)
            batch_ids = []
            start_time = time.time()
            for i in range(num_devices):
                light_id, _ = perf_timer.time_operation(
                    "batch_creation",
                    controller.create_light,
                    f"Lampe Batch {i}",
                    "Batch Room",
                )
                if light_id:
                    batch_ids.append(light_id)
            batch_total_time = time.time() - start_time

            # Comparaison des performances
            sequential_stats = perf_timer.get_stats("sequential_creation")
            batch_stats = perf_timer.get_stats("batch_creation")

            print("\nComparaison Séquentiel vs Batch:")
            print(
                f"Séquentiel: {sequential_total_time:.3f}s total, "
                f"{sequential_stats['average'] * 1000:.2f}ms/op"
            )
            print(
                f"Batch: {batch_total_time:.3f}s total, "
                f"{batch_stats['average'] * 1000:.2f}ms/op"
            )

            # Vérification d'intégrité
            assert len(sequential_ids) == num_devices
            assert len(batch_ids) == num_devices

            # Les deux méthodes doivent avoir des performances similaires
            # (dans ce système, il n'y a pas vraiment de batch, donc similaire)
            ratio = (
                batch_stats["average"] / sequential_stats["average"]
                if sequential_stats["average"] > 0
                else 1
            )
            assert (
                0.5 <= ratio <= 2.0
            ), f"Différence de performance trop importante: {ratio}"

        finally:
            session.close()


class TestQueryPerformance:
    """Tests de performance pour les requêtes."""

    def test_large_dataset_query_performance(self, perf_test_db, perf_timer):
        """Test E2E: Performance des requêtes sur un grand dataset."""
        session = create_session()

        try:
            # Créer un grand dataset
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            num_devices = 100
            num_locations = 10

            # Création rapide du dataset
            device_ids = []
            for i in range(num_devices):
                light_id = controller.create_light(
                    f"Lampe {i:03d}", f"Room {i % num_locations}"
                )
                if light_id:
                    device_ids.append(light_id)

            assert len(device_ids) == num_devices

            # Test des différents types de requêtes

            # 1. Requête complète
            all_devices, _ = perf_timer.time_operation("query_find_all", repo.find_all)
            assert len(all_devices) == num_devices

            # 2. Requêtes par localisation
            for room_id in range(num_locations):
                location_devices, _ = perf_timer.time_operation(
                    "query_by_location", repo.find_by_location, f"Room {room_id}"
                )
                expected_count = num_devices // num_locations
                assert len(location_devices) == expected_count

            # 3. Requêtes par ID (accès direct)
            for i in range(0, min(20, len(device_ids)), 2):  # Tester 10 dispositifs
                device, _ = perf_timer.time_operation(
                    "query_by_id", repo.find_by_id, device_ids[i]
                )
                assert device is not None
                assert device.id == device_ids[i]

            # 4. Requêtes par pattern de nom
            search_results, _ = perf_timer.time_operation(
                "query_search_by_name",
                repo.search_by_name,
                "01",  # Chercher les dispositifs avec "01" dans le nom
            )
            # Doit trouver Lampe 001, 010, 011, etc.
            assert len(search_results) >= 10

            # 5. Comptage
            count, _ = perf_timer.time_operation("query_count_all", repo.count_all)
            assert count == num_devices

            # Vérifications de performance
            perf_stats = {
                "find_all": perf_timer.get_stats("query_find_all"),
                "by_location": perf_timer.get_stats("query_by_location"),
                "by_id": perf_timer.get_stats("query_by_id"),
                "search_name": perf_timer.get_stats("query_search_by_name"),
                "count": perf_timer.get_stats("query_count_all"),
            }

            # Seuils de performance (ajustables selon les besoins)
            assert (
                perf_stats["find_all"]["average"] < 2.0
            ), "Requête find_all trop lente"
            assert (
                perf_stats["by_location"]["average"] < 1.0
            ), "Requête by_location trop lente"
            assert perf_stats["by_id"]["average"] < 0.5, "Requête by_id trop lente"
            assert perf_stats["count"]["average"] < 1.0, "Requête count trop lente"

        finally:
            session.close()

    def test_concurrent_query_performance(self, perf_test_db, perf_timer):
        """Test E2E: Performance des requêtes concurrentes."""
        # Préparer les données
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Créer des dispositifs pour les tests
            device_ids = []
            for i in range(30):
                light_id = controller.create_light(
                    f"Lampe Concurrent {i}", f"Room {i % 5}"
                )
                if light_id:
                    device_ids.append(light_id)

        finally:
            session.close()

        # Test concurrent avec plusieurs threads
        def worker_thread(thread_id: int, operations_per_thread: int) -> List[float]:
            """Worker thread pour les tests concurrents."""
            thread_session = create_session()
            thread_times = []

            try:
                thread_repo = DeviceRepository(thread_session)

                for i in range(operations_per_thread):
                    # Alterner entre différents types de requêtes
                    start_time = time.time()

                    if i % 4 == 0:
                        # Requête complète
                        thread_repo.find_all()
                    elif i % 4 == 1:
                        # Requête par location
                        thread_repo.find_by_location(f"Room {i % 5}")
                    elif i % 4 == 2:
                        # Requête par ID
                        if device_ids:
                            thread_repo.find_by_id(device_ids[i % len(device_ids)])
                    else:
                        # Comptage
                        thread_repo.count_all()

                    end_time = time.time()
                    thread_times.append(end_time - start_time)

            finally:
                thread_session.close()

            return thread_times

        # Lancer les threads concurrents
        num_threads = 4
        operations_per_thread = 10

        concurrent_start = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(worker_thread, i, operations_per_thread)
                for i in range(num_threads)
            ]

            all_times = []
            for future in as_completed(futures):
                thread_times = future.result()
                all_times.extend(thread_times)

        concurrent_end = time.time()
        concurrent_total_time = concurrent_end - concurrent_start

        # Analyser les résultats
        if all_times:
            avg_time = statistics.mean(all_times)
            max_time = max(all_times)
            min_time = min(all_times)

            total_operations = num_threads * operations_per_thread
            operations_per_second = total_operations / concurrent_total_time

            print("\nPerformance Concurrente:")
            print(f"  Threads: {num_threads}")
            print(f"  Opérations totales: {total_operations}")
            print(f"  Temps total: {concurrent_total_time:.3f}s")
            print(f"  Opérations/seconde: {operations_per_second:.1f}")
            print(f"  Temps moyen par opération: {avg_time * 1000:.2f}ms")
            print(f"  Min/Max: {min_time * 1000:.2f}ms / {max_time * 1000:.2f}ms")

            # Assertions de performance
            assert avg_time < 1.0, f"Requêtes concurrentes trop lentes: {avg_time:.3f}s"
            assert (
                operations_per_second > 5
            ), f"Débit trop faible: {operations_per_second:.1f} ops/s"


class TestStateOperationPerformance:
    """Tests de performance pour les opérations d'état."""

    def test_frequent_state_changes_performance(self, perf_test_db, perf_timer):
        """Test E2E: Performance des changements d'état fréquents."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Créer des lampes pour les tests
            light_ids = []
            for i in range(10):
                light_id = controller.create_light(f"Lampe State {i}", "State Room")
                if light_id:
                    light_ids.append(light_id)

            assert len(light_ids) >= 5  # Au moins 5 lampes pour le test

            # Test de changements d'état rapides
            num_cycles = 20  # 20 cycles on/off par lampe

            for light_id in light_ids[:5]:  # Tester 5 lampes
                for _ in range(num_cycles):
                    # Allumer
                    success, _ = perf_timer.time_operation(
                        "turn_on_operation", controller.turn_on, light_id
                    )
                    assert success is True

                    # Vérifier l'état
                    light, _ = perf_timer.time_operation(
                        "get_light_state", controller.get_light, light_id
                    )
                    assert light is not None
                    assert light.is_on is True

                    # Éteindre
                    success, _ = perf_timer.time_operation(
                        "turn_off_operation", controller.turn_off, light_id
                    )
                    assert success is True

                    # Vérifier l'état
                    light, _ = perf_timer.time_operation(
                        "get_light_state", controller.get_light, light_id
                    )
                    assert light is not None
                    assert light.is_on is False

            # Analyser les performances
            turn_on_stats = perf_timer.get_stats("turn_on_operation")
            turn_off_stats = perf_timer.get_stats("turn_off_operation")
            get_state_stats = perf_timer.get_stats("get_light_state")

            # Seuils de performance pour les opérations d'état
            assert (
                turn_on_stats["average"] < 0.5
            ), f"Turn ON trop lent: {turn_on_stats['average']:.3f}s"
            assert (
                turn_off_stats["average"] < 0.5
            ), f"Turn OFF trop lent: {turn_off_stats['average']:.3f}s"
            assert (
                get_state_stats["average"] < 0.2
            ), f"Get state trop lent: {get_state_stats['average']:.3f}s"

            # Vérifier la consistance des temps
            on_off_ratio = (
                turn_off_stats["average"] / turn_on_stats["average"]
                if turn_on_stats["average"] > 0
                else 1
            )
            assert (
                0.5 <= on_off_ratio <= 2.0
            ), f"Incohérence performances ON/OFF: {on_off_ratio}"

        finally:
            session.close()

    def test_mixed_operation_performance(self, perf_test_db, perf_timer):
        """Test E2E: Performance d'opérations mixtes réalistes."""
        session = create_session()

        try:
            light_controller = get_controller_factory().create_light_controller(session)
            shutter_controller = get_controller_factory().create_shutter_controller(
                session
            )
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )
            repo = DeviceRepository(session)

            # Scenario réaliste: simulation d'utilisation journalière
            scenario_operations = [
                # Matin: allumer les lumières
                ("create_light", light_controller.create_light, "Lampe Salon", "Salon"),
                (
                    "create_light",
                    light_controller.create_light,
                    "Lampe Cuisine",
                    "Cuisine",
                ),
                ("turn_on", light_controller.turn_on, None),  # ID sera résolu
                ("turn_on", light_controller.turn_on, None),
                # Ouvrir les volets
                (
                    "create_shutter",
                    shutter_controller.create_shutter,
                    "Volet Salon",
                    "Salon",
                ),
                ("open", shutter_controller.open, None),
                # Capteurs de température
                (
                    "create_sensor",
                    sensor_controller.create_sensor,
                    "Temp Salon",
                    "Salon",
                ),
                ("update_sensor", sensor_controller.update_value, None, 22.5),
                # Requêtes d'état
                ("query_by_location", repo.find_by_location, "Salon"),
                (
                    "query_count",
                    repo.count_all,
                ),
                # Soirée: éteindre progressivement
                ("turn_off", light_controller.turn_off, None),
                ("close", shutter_controller.close, None),
            ]

            created_devices = {"lights": [], "shutters": [], "sensors": []}

            # Exécuter le scenario
            for operation_name, operation_func, *args in scenario_operations:
                # Résoudre les IDs dynamiquement
                resolved_args = []
                for arg in args:
                    if arg is None:
                        # Utiliser le dernier dispositif créé du type approprié
                        light_ops = ["turn_on", "turn_off"]
                        shutter_ops = ["open", "close"]

                        if "light" in operation_name or operation_name in light_ops:
                            if created_devices["lights"]:
                                resolved_args.append(created_devices["lights"][-1])
                        elif (
                            "shutter" in operation_name or operation_name in shutter_ops
                        ):
                            if created_devices["shutters"]:
                                resolved_args.append(created_devices["shutters"][-1])
                        elif (
                            "sensor" in operation_name
                            or operation_name == "update_sensor"
                        ):
                            if created_devices["sensors"]:
                                resolved_args.append(created_devices["sensors"][-1])
                    else:
                        resolved_args.append(arg)

                # Exécuter l'opération
                try:
                    if resolved_args or not args:
                        result, _ = perf_timer.time_operation(
                            operation_name, operation_func, *resolved_args
                        )

                        # Stocker les IDs créés
                        if "create_light" in operation_name and result:
                            created_devices["lights"].append(result)
                        elif "create_shutter" in operation_name and result:
                            created_devices["shutters"].append(result)
                        elif "create_sensor" in operation_name and result:
                            created_devices["sensors"].append(result)

                except Exception as e:
                    print(f"Erreur dans opération {operation_name}: {e}")
                    continue

            # Vérifier que le scenario s'est bien déroulé
            assert len(created_devices["lights"]) >= 2
            assert len(created_devices["shutters"]) >= 1
            assert len(created_devices["sensors"]) >= 1

            # Analyser les performances du scenario complet
            total_time = sum(sum(times) for times in perf_timer.measurements.values())
            total_operations = sum(
                len(times) for times in perf_timer.measurements.values()
            )

            print("\nScenario réaliste complété:")
            print(f"  Total opérations: {total_operations}")
            print(f"  Temps total: {total_time:.3f}s")
            avg_time_ms = (total_time / total_operations) * 1000
            print(f"  Temps moyen par opération: {avg_time_ms:.2f}ms")

            # Le scenario complet doit se terminer en moins de 10 secondes
            assert total_time < 10.0, f"Scenario trop lent: {total_time:.3f}s"

        finally:
            session.close()
