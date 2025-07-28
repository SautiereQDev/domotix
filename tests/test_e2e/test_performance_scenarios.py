"""
End-to-End (E2E) Tests for Domotix system performance scenarios.

These tests validate that the system maintains acceptable performance
under various loads and real-world usage conditions.

Test Coverage:
    - Bulk device creation performance
    - Query performance with large data volumes
    - Frequent state operation performance
    - Response time benchmarks
    - Scalability tests
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
    """Fixture for a temporary database dedicated to performance tests."""
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
    """Helper to measure performance."""

    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}

    def time_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Measures the execution time of an operation."""
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()

        duration = end_time - start_time

        if operation_name not in self.measurements:
            self.measurements[operation_name] = []
        self.measurements[operation_name].append(duration)

        return result, duration

    def get_stats(self, operation_name: str) -> Dict[str, float]:
        """Gets the statistics for an operation."""
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
        """Displays a summary of performances."""
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)

        for operation, stats in [(op, self.get_stats(op)) for op in self.measurements]:
            if stats:
                print(f"\n{operation}:")
                print(f"  Operations: {stats['count']}")
                print(f"  Total time: {stats['total']:.3f}s")
                print(f"  Average: {stats['average'] * 1000:.2f}ms")
                print(f"  Median: {stats['median'] * 1000:.2f}ms")
                print(
                    f"  Min/Max: {stats['min'] * 1000:.2f}ms / "
                    f"{stats['max'] * 1000:.2f}ms"
                )
                if stats["stdev"] > 0:
                    print(f"  Standard deviation: {stats['stdev'] * 1000:.2f}ms")


@pytest.fixture
def perf_timer():
    """Fixture for the performance timer."""
    timer = PerformanceTimer()
    yield timer
    timer.print_summary()


class TestDeviceCreationPerformance:
    """Performance tests for device creation."""

    def test_bulk_device_creation_performance(self, perf_test_db, perf_timer):
        """E2E Test: Bulk device creation performance."""
        session = create_session()

        try:
            light_controller = get_controller_factory().create_light_controller(session)
            shutter_controller = get_controller_factory().create_shutter_controller(
                session
            )
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )

            # Bulk creation test for each type
            num_devices_per_type = 50

            # Creating lights
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

            # Creating shutters
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

            # Creating sensors
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

            # Performance checks
            light_stats = perf_timer.get_stats("create_light")
            shutter_stats = perf_timer.get_stats("create_shutter")
            sensor_stats = perf_timer.get_stats("create_sensor")

            # Performance assertions (reasonable thresholds)
            assert (
                light_stats["average"] < 1.0
            ), f"Light creation too slow: {light_stats['average']:.3f}s"
            assert (
                shutter_stats["average"] < 1.0
            ), f"Shutter creation too slow: {shutter_stats['average']:.3f}s"
            assert (
                sensor_stats["average"] < 1.0
            ), f"Sensor creation too slow: {sensor_stats['average']:.3f}s"

            # Integrity check
            assert len(light_ids) == num_devices_per_type
            assert len(shutter_ids) == num_devices_per_type
            assert len(sensor_ids) == num_devices_per_type

            # Read test after creation
            repo = DeviceRepository(session)
            total_devices, _ = perf_timer.time_operation(
                "count_all_devices", repo.count_all
            )

            expected_total = num_devices_per_type * 3
            assert total_devices == expected_total

        finally:
            session.close()

    def test_sequential_vs_batch_creation(self, perf_test_db, perf_timer):
        """E2E Test: Sequential vs batch creation comparison."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Sequential test
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

            # Simulate "batch" creation (rapid successive creation)
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

            # Performance comparison
            sequential_stats = perf_timer.get_stats("sequential_creation")
            batch_stats = perf_timer.get_stats("batch_creation")

            print("\nSequential vs Batch Comparison:")
            print(
                f"Sequential: {sequential_total_time:.3f}s total, "
                f"{sequential_stats['average'] * 1000:.2f}ms/op"
            )
            print(
                f"Batch: {batch_total_time:.3f}s total, "
                f"{batch_stats['average'] * 1000:.2f}ms/op"
            )

            # Integrity check
            assert len(sequential_ids) == num_devices
            assert len(batch_ids) == num_devices

            # Both methods should have similar performance
            # (in this system, there is not really a batch, so similar)
            ratio = (
                batch_stats["average"] / sequential_stats["average"]
                if sequential_stats["average"] > 0
                else 1
            )
            assert 0.5 <= ratio <= 2.0, f"Performance difference too high: {ratio}"

        finally:
            session.close()


class TestQueryPerformance:
    """Performance tests for queries."""

    def test_large_dataset_query_performance(self, perf_test_db, perf_timer):
        """E2E Test: Query performance on a large dataset."""
        session = create_session()

        try:
            # Create a large dataset
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            num_devices = 100
            num_locations = 10

            # Rapid dataset creation
            device_ids = []
            for i in range(num_devices):
                light_id = controller.create_light(
                    f"Lampe {i:03d}", f"Room {i % num_locations}"
                )
                if light_id:
                    device_ids.append(light_id)

            assert len(device_ids) == num_devices

            # Test different types of queries

            # 1. Full query
            all_devices, _ = perf_timer.time_operation("query_find_all", repo.find_all)
            assert len(all_devices) == num_devices

            # 2. Location-based queries
            for room_id in range(num_locations):
                location_devices, _ = perf_timer.time_operation(
                    "query_by_location", repo.find_by_location, f"Room {room_id}"
                )
                expected_count = num_devices // num_locations
                assert len(location_devices) == expected_count

            # 3. ID-based queries (direct access)
            for i in range(0, min(20, len(device_ids)), 2):  # Test 10 devices
                device, _ = perf_timer.time_operation(
                    "query_by_id", repo.find_by_id, device_ids[i]
                )
                assert device is not None
                assert device.id == device_ids[i]

            # 4. Name pattern queries
            search_results, _ = perf_timer.time_operation(
                "query_search_by_name",
                repo.search_by_name,
                "01",  # Search for devices with "01" in the name
            )
            # Should find Lampe 001, 010, 011, etc.
            assert len(search_results) >= 10

            # 5. Counting
            count, _ = perf_timer.time_operation("query_count_all", repo.count_all)
            assert count == num_devices

            # Performance checks
            perf_stats = {
                "find_all": perf_timer.get_stats("query_find_all"),
                "by_location": perf_timer.get_stats("query_by_location"),
                "by_id": perf_timer.get_stats("query_by_id"),
                "search_name": perf_timer.get_stats("query_search_by_name"),
                "count": perf_timer.get_stats("query_count_all"),
            }

            # Performance thresholds (adjustable as needed)
            assert perf_stats["find_all"]["average"] < 2.0, "find_all query too slow"
            assert (
                perf_stats["by_location"]["average"] < 1.0
            ), "by_location query too slow"
            assert perf_stats["by_id"]["average"] < 0.5, "by_id query too slow"
            assert perf_stats["count"]["average"] < 1.0, "count query too slow"

        finally:
            session.close()

    def test_concurrent_query_performance(self, perf_test_db, perf_timer):
        """E2E Test: Performance of concurrent queries."""
        # Prepare data
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Create devices for testing
            device_ids = []
            for i in range(30):
                light_id = controller.create_light(
                    f"Lampe Concurrent {i}", f"Room {i % 5}"
                )
                if light_id:
                    device_ids.append(light_id)

        finally:
            session.close()

        # Concurrent test with multiple threads
        def worker_thread(thread_id: int, operations_per_thread: int) -> List[float]:
            """Worker thread for concurrent tests."""
            thread_session = create_session()
            thread_times = []

            try:
                thread_repo = DeviceRepository(thread_session)

                for i in range(operations_per_thread):
                    # Alternate between different types of queries
                    start_time = time.time()

                    if i % 4 == 0:
                        # Full query
                        thread_repo.find_all()
                    elif i % 4 == 1:
                        # Location-based query
                        thread_repo.find_by_location(f"Room {i % 5}")
                    elif i % 4 == 2:
                        # ID-based query
                        if device_ids:
                            thread_repo.find_by_id(device_ids[i % len(device_ids)])
                    else:
                        # Counting
                        thread_repo.count_all()

                    end_time = time.time()
                    thread_times.append(end_time - start_time)

            finally:
                thread_session.close()

            return thread_times

        # Launch concurrent threads
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

        # Analyze results
        if all_times:
            avg_time = statistics.mean(all_times)
            max_time = max(all_times)
            min_time = min(all_times)

            total_operations = num_threads * operations_per_thread
            operations_per_second = total_operations / concurrent_total_time

            print("\nConcurrent Performance:")
            print(f"  Threads: {num_threads}")
            print(f"  Total operations: {total_operations}")
            print(f"  Total time: {concurrent_total_time:.3f}s")
            print(f"  Operations/second: {operations_per_second:.1f}")
            print(f"  Average time per operation: {avg_time * 1000:.2f}ms")
            print(f"  Min/Max: {min_time * 1000:.2f}ms / {max_time * 1000:.2f}ms")

            # Performance assertions
            assert avg_time < 1.0, f"Concurrent queries too slow: {avg_time:.3f}s"
            assert (
                operations_per_second > 5
            ), f"Throughput too low: {operations_per_second:.1f} ops/s"


class TestStateOperationPerformance:
    """Performance tests for state operations."""

    def test_frequent_state_changes_performance(self, perf_test_db, perf_timer):
        """E2E Test: Performance of frequent state changes."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Create lights for testing
            light_ids = []
            for i in range(10):
                light_id = controller.create_light(f"Lampe State {i}", "State Room")
                if light_id:
                    light_ids.append(light_id)

            assert len(light_ids) >= 5  # At least 5 lights for the test

            # Rapid state change test
            num_cycles = 20  # 20 on/off cycles per lamp

            for light_id in light_ids[:5]:  # Test 5 lamps
                for _ in range(num_cycles):
                    # Turn on
                    success, _ = perf_timer.time_operation(
                        "turn_on_operation", controller.turn_on, light_id
                    )
                    assert success is True

                    # Check state
                    light, _ = perf_timer.time_operation(
                        "get_light_state", controller.get_light, light_id
                    )
                    assert light is not None
                    assert light.is_on is True

                    # Turn off
                    success, _ = perf_timer.time_operation(
                        "turn_off_operation", controller.turn_off, light_id
                    )
                    assert success is True

                    # Check state
                    light, _ = perf_timer.time_operation(
                        "get_light_state", controller.get_light, light_id
                    )
                    assert light is not None
                    assert light.is_on is False

            # Analyze performances
            turn_on_stats = perf_timer.get_stats("turn_on_operation")
            turn_off_stats = perf_timer.get_stats("turn_off_operation")
            get_state_stats = perf_timer.get_stats("get_light_state")

            # Performance thresholds for state operations
            assert (
                turn_on_stats["average"] < 0.5
            ), f"Turn ON too slow: {turn_on_stats['average']:.3f}s"
            assert (
                turn_off_stats["average"] < 0.5
            ), f"Turn OFF too slow: {turn_off_stats['average']:.3f}s"
            assert (
                get_state_stats["average"] < 0.2
            ), f"Get state too slow: {get_state_stats['average']:.3f}s"

            # Consistency check
            on_off_ratio = (
                turn_off_stats["average"] / turn_on_stats["average"]
                if turn_on_stats["average"] > 0
                else 1
            )
            assert (
                0.5 <= on_off_ratio <= 2.0
            ), f"ON/OFF performance inconsistency: {on_off_ratio}"

        finally:
            session.close()

    def test_mixed_operation_performance(self, perf_test_db, perf_timer):
        """E2E Test: Performance of realistic mixed operations."""
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

            # Realistic scenario: simulating daily usage
            scenario_operations = [
                # Morning: turn on lights
                ("create_light", light_controller.create_light, "Lampe Salon", "Salon"),
                (
                    "create_light",
                    light_controller.create_light,
                    "Lampe Cuisine",
                    "Cuisine",
                ),
                ("turn_on", light_controller.turn_on, None),  # ID will be resolved
                ("turn_on", light_controller.turn_on, None),
                # Open shutters
                (
                    "create_shutter",
                    shutter_controller.create_shutter,
                    "Volet Salon",
                    "Salon",
                ),
                ("open", shutter_controller.open, None),
                # Temperature sensors
                (
                    "create_sensor",
                    sensor_controller.create_sensor,
                    "Temp Salon",
                    "Salon",
                ),
                ("update_sensor", sensor_controller.update_value, None, 22.5),
                # State queries
                ("query_by_location", repo.find_by_location, "Salon"),
                (
                    "query_count",
                    repo.count_all,
                ),
                # Evening: gradually turn off
                ("turn_off", light_controller.turn_off, None),
                ("close", shutter_controller.close, None),
            ]

            created_devices = {"lights": [], "shutters": [], "sensors": []}

            # Execute scenario
            for operation_name, operation_func, *args in scenario_operations:
                # Dynamically resolve IDs
                resolved_args = []
                for arg in args:
                    if arg is None:
                        # Use the last created device ID of the appropriate type
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

                # Execute operation
                try:
                    if resolved_args or not args:
                        result, _ = perf_timer.time_operation(
                            operation_name, operation_func, *resolved_args
                        )

                        # Store created IDs
                        if "create_light" in operation_name and result:
                            created_devices["lights"].append(result)
                        elif "create_shutter" in operation_name and result:
                            created_devices["shutters"].append(result)
                        elif "create_sensor" in operation_name and result:
                            created_devices["sensors"].append(result)

                except Exception as e:
                    print(f"Error in operation {operation_name}: {e}")
                    continue

            # Check that the scenario executed correctly
            assert len(created_devices["lights"]) >= 2
            assert len(created_devices["shutters"]) >= 1
            assert len(created_devices["sensors"]) >= 1

            # Analyze performances of the complete scenario
            total_time = sum(sum(times) for times in perf_timer.measurements.values())
            total_operations = sum(
                len(times) for times in perf_timer.measurements.values()
            )

            print("\nRealistic scenario completed:")
            print(f"  Total operations: {total_operations}")
            print(f"  Total time: {total_time:.3f}s")
            avg_time_ms = (total_time / total_operations) * 1000
            print(f"  Average time per operation: {avg_time_ms:.2f}ms")

            # The complete scenario should finish in less than 10 seconds
            assert total_time < 10.0, f"Scenario too slow: {total_time:.3f}s"

        finally:
            session.close()
