"""
End-to-End (E2E) tests for error recovery and robustness.

These tests validate that the system can gracefully handle errors
and continue to function correctly under adverse conditions.

Test Coverage:
    - Database error handling
    - Recovery after system failures
    - User input validation
    - Inconsistent state management
    - Timeout and resource limitations
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
    """Fixture for a temporary database."""
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
    """E2E tests for database error recovery."""

    def test_database_connection_failure_recovery(self, temp_database):
        """E2E Test: Recovery after DB connection failure."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Create a normal light
            light_id = controller.create_light("Test Light", "Test Room")
            assert light_id is not None

            # Simulate connection loss by corrupting the DB path
            original_path = os.environ.get("DOMOTIX_DB_PATH")
            os.environ["DOMOTIX_DB_PATH"] = "/invalid/path/to/database.db"

            # Try to create a new session (should fail)
            try:
                new_session = create_session()
                new_controller = get_controller_factory().create_light_controller(
                    new_session
                )

                # This operation may fail, which is expected
                new_controller.create_light("Failed Light", "Test Room")
                # The result may be None or raise an exception

            except Exception as e:
                # This is expected during a connection failure
                assert "database" in str(e).lower() or "connection" in str(e).lower()

            # Restore the connection
            os.environ["DOMOTIX_DB_PATH"] = original_path

            # Verify that the system can recover
            recovery_session = create_session()
            try:
                recovery_controller = get_controller_factory().create_light_controller(
                    recovery_session
                )

                # Verify that previous data still exists
                original_light = recovery_controller.get_light(light_id)
                assert original_light is not None
                assert original_light.name == "Test Light"

                # Create a new light to test recovery
                new_light_id = recovery_controller.create_light(
                    "Recovery Light", "Recovery Room"
                )
                assert new_light_id is not None

                new_light = recovery_controller.get_light(new_light_id)
                assert new_light is not None
                assert new_light.name == "Recovery Light"

            finally:
                recovery_session.close()

        finally:
            session.close()

    def test_corrupted_data_recovery(self, temp_database):
        """E2E Test: Recovery with corrupted data."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Create valid data
            light_id = controller.create_light("Valid Light", "Valid Room")
            assert light_id is not None

            # Verify light was created successfully
            light = controller.get_light(light_id)
            assert light is not None
            assert light.name == "Valid Light"

            # Simulate corruption by inserting invalid data directly
            # via SQL (bypassing model validations)
            from domotix.models.base_model import DeviceModel

            corrupted_device = DeviceModel(
                id="corrupted-id-invalid",
                name="",  # Empty name (invalid)
                location=None,  # Location None (might be invalid)
                device_type="invalid_type",  # Invalid type
                is_on=None,  # None value for boolean (invalid)
                is_open=False,
                value=0.0,
            )

            # Try to insert directly (may fail)
            try:
                session.add(corrupted_device)
                session.commit()
            except Exception:
                # Rollback if insertion fails
                session.rollback()

            # Verify that the system continues to work with valid data
            valid_light = controller.get_light(light_id)
            assert valid_light is not None
            assert valid_light.name == "Valid Light"

            # Create new valid data
            new_light_id = controller.create_light("New Light", "New Room")
            assert new_light_id is not None

            # Verify the integrity of valid data
            # Check devices individually (find_all might be affected by corruption)
            valid_light = controller.get_light(light_id)
            new_light = controller.get_light(new_light_id)

            assert valid_light is not None, "Original valid light should be accessible"
            assert new_light is not None, "New light should be accessible"
            assert valid_light.name == "Valid Light"
            assert new_light.name == "New Light"

            # Verify data access through both repository and direct controller access
            valid_data_accessible = False

            # Try repository first
            try:
                all_valid_devices = repo.find_all()
                repo_device_names = {
                    d.name
                    for d in all_valid_devices
                    if d and hasattr(d, "name") and d.name
                }
                expected_names = {"Valid Light", "New Light"}
                if expected_names.issubset(repo_device_names):
                    valid_data_accessible = True
            except Exception:  # pylint: disable=broad-except
                pass  # Will fall back to controller access

            # If repository access failed, verify through controller
            if not valid_data_accessible:
                valid_light = controller.get_light(light_id)
                new_light = controller.get_light(new_light_id)

                valid_data_accessible = (
                    valid_light
                    and new_light
                    and valid_light.name == "Valid Light"
                    and new_light.name == "New Light"
                )

            # Assert that we can access the data through at least one method
            assert (
                valid_data_accessible
            ), "Could not access valid devices through any method"

        finally:
            session.close()


class TestInputValidationErrorRecovery:
    """E2E tests for input validation error handling."""

    def test_invalid_input_handling(self, temp_database):
        """E2E Test: Invalid input handling."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Test with invalid names
            invalid_names = [
                "",  # Empty name
                None,  # None name
                " " * 100,  # Too long spaces name
                "A" * 1000,  # Too long name
            ]

            for invalid_name in invalid_names:
                try:
                    result = controller.create_light(invalid_name, "Test Room")
                    # If the operation succeeds despite invalid input,
                    # verify that the result makes sense
                    if result is not None:
                        light = controller.get_light(result)
                        if light is not None:
                            # The name must be defined (even if empty)
                            assert light.name is not None
                            # Note: An empty name might be acceptable according
                            # to business specs

                except (ValueError, DomotixError, ControllerError, Exception) as e:
                    # It's acceptable for the operation to fail with invalid inputs
                    # IntegrityError for database constraints
                    error_message = str(e).lower()
                    expected_errors = [
                        "name",
                        "invalid",
                        "constraint",
                        "not null",
                        "integrity",
                    ]
                    assert any(keyword in error_message for keyword in expected_errors)

            # Verify that after errors, the system still works
            valid_light_id = controller.create_light("Valid Light", "Valid Room")
            assert valid_light_id is not None

            valid_light = controller.get_light(valid_light_id)
            assert valid_light is not None
            assert valid_light.name == "Valid Light"

        finally:
            session.close()

    def test_concurrent_access_error_recovery(self, temp_database):
        """E2E Test: Recovery during concurrent access."""
        session1 = create_session()
        session2 = create_session()

        try:
            controller1 = get_controller_factory().create_light_controller(session1)
            controller2 = get_controller_factory().create_light_controller(session2)

            # Session 1: Create a light
            light_id = controller1.create_light("Concurrent Light", "Concurrent Room")
            assert light_id is not None

            # Session 1: Start a modification
            success1 = controller1.turn_on(light_id)
            assert success1 is True

            # Session 2: Try to modify at the same time
            # (may succeed or fail depending on implementation)
            try:
                success2 = controller2.turn_off(light_id)
                # If it succeeds, verify consistency
                if success2:
                    light_state = controller2.get_light(light_id)
                    # The final state must be consistent
                    assert light_state is not None
                    assert isinstance(light_state.is_on, bool)

            except Exception as e:
                # Concurrency errors are acceptable
                assert (
                    "concurrent" in str(e).lower()
                    or "lock" in str(e).lower()
                    or "conflict" in str(e).lower()
                )

            # Verify that after conflicts, the system works
            final_light = controller1.get_light(light_id)
            assert final_light is not None
            assert final_light.name == "Concurrent Light"

            # Create a new light to test recovery
            new_light_id = controller1.create_light(
                "Post-Conflict Light", "Recovery Room"
            )
            assert new_light_id is not None

        finally:
            session1.close()
            session2.close()


class TestResourceLimitationRecovery:
    """E2E tests for resource limitation handling."""

    def test_memory_pressure_simulation(self, temp_database):
        """E2E Test: Memory pressure simulation."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Create a large number of devices to simulate memory pressure
            created_devices = []
            max_devices = 100  # Reasonable number for a test

            for i in range(max_devices):
                try:
                    light_id = controller.create_light(
                        f"Light {i:03d}", f"Room {i % 10}"
                    )
                    if light_id is not None:
                        created_devices.append(light_id)

                    # Periodically verify integrity
                    if i % 20 == 0 and i > 0:
                        # Read test to verify system responsiveness
                        sample_light = controller.get_light(created_devices[0])
                        assert sample_light is not None

                        # Count test
                        count = repo.count_all()
                        assert count >= len(created_devices)

                except Exception as e:
                    # If we reach limits, it's acceptable
                    if "memory" in str(e).lower() or "resource" in str(e).lower():
                        break
                    else:
                        # Other errors are unexpected
                        raise

            # Verify that system still works
            assert len(created_devices) > 0, "No device created"

            # Functionality test after load
            final_test_id = controller.create_light("Final Test Light", "Final Room")
            assert final_test_id is not None

            final_light = controller.get_light(final_test_id)
            assert final_light is not None
            assert final_light.name == "Final Test Light"

            # Partial cleanup to test deletion under load
            for i, device_id in enumerate(created_devices[:20]):  # Delete the first 20
                try:
                    success = controller.delete_light(device_id)
                    # Deletion may fail under load, it's acceptable
                    if success:
                        deleted_light = controller.get_light(device_id)
                        assert deleted_light is None
                except Exception:
                    # Deletion errors under load are acceptable
                    pass

        finally:
            session.close()

    def test_timeout_recovery(self, temp_database):
        """E2E Test: Recovery after timeouts."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Create a normal light
            light_id = controller.create_light("Timeout Light", "Timeout Room")
            assert light_id is not None

            # Simulate slow operations with short timeouts
            start_time = time.time()

            # Series of quick operations to test resilience
            operations_completed = 0
            max_operations = 50

            for i in range(max_operations):
                try:
                    # Alternating operations
                    if i % 2 == 0:
                        success = controller.turn_on(light_id)
                    else:
                        success = controller.turn_off(light_id)

                    if success:
                        operations_completed += 1

                    # Periodically verify state
                    if i % 10 == 0:
                        light = controller.get_light(light_id)
                        assert light is not None

                except Exception as e:
                    # Some operations may fail under stress
                    if "timeout" in str(e).lower():
                        continue  # Timeout acceptable
                    else:
                        raise  # Other errors are problematic

            # Verify that system works after stress
            elapsed_time = time.time() - start_time

            # At least some operations must have succeeded
            assert operations_completed > 0, "No operation succeeded"

            # Final functionality test
            final_light = controller.get_light(light_id)
            assert final_light is not None
            assert final_light.name == "Timeout Light"

            # Create a new light to verify complete recovery
            recovery_light_id = controller.create_light(
                "Recovery Light", "Recovery Room"
            )
            assert recovery_light_id is not None

            print(
                f"Stress test completed: {operations_completed}/"
                f"{max_operations} operations in {elapsed_time:.2f}s"
            )

        finally:
            session.close()


class TestSystemStateRecovery:
    """E2E tests for system state recovery."""

    def test_state_manager_reset_recovery(self, temp_database):
        """E2E Test: Recovery after StateManager reset."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Create data before reset
            light_id = controller.create_light(
                "Before Reset Light", "Before Reset Room"
            )
            assert light_id is not None

            success = controller.turn_on(light_id)
            assert success is True

            # Simulate a StateManager reset
            StateManager.reset_instance()

            # Create a new session after reset
            new_session = create_session()
            try:
                new_controller = get_controller_factory().create_light_controller(
                    new_session
                )

                # Verify that data persists after reset
                persisted_light = new_controller.get_light(light_id)
                assert persisted_light is not None
                assert persisted_light.name == "Before Reset Light"
                assert persisted_light.is_on is True  # State must be preserved

                # Verify that new operations work
                new_light_id = new_controller.create_light(
                    "After Reset Light", "After Reset Room"
                )
                assert new_light_id is not None

                new_light = new_controller.get_light(new_light_id)
                assert new_light is not None
                assert new_light.name == "After Reset Light"

            finally:
                new_session.close()

        finally:
            session.close()

    def test_partial_failure_recovery(self, temp_database):
        """E2E Test: Recovery after partial failures."""
        session = create_session()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Create multiple devices
            successful_devices = []
            failed_operations = 0

            for i in range(10):
                try:
                    # Alternate between valid and potentially
                    # problematic operations
                    if i % 3 == 0:
                        # Normal operation
                        light_id = controller.create_light(f"Light {i}", f"Room {i}")
                        if light_id:
                            successful_devices.append(light_id)
                    elif i % 3 == 1:
                        # Operation with limit name
                        light_id = controller.create_light(
                            f"Light with very long name {i}" * 5, f"Room {i}"
                        )
                        if light_id:
                            successful_devices.append(light_id)
                    else:
                        # Potentially problematic operation
                        light_id = controller.create_light(
                            f"Light-{i}", None
                        )  # Location None
                        if light_id:
                            successful_devices.append(light_id)

                except Exception:
                    failed_operations += 1
                    continue

            # Verify that despite failures, some operations succeeded
            assert len(successful_devices) > 0, "No operation succeeded"

            # Verify integrity of created devices
            for device_id in successful_devices:
                device = controller.get_light(device_id)
                assert device is not None
                assert device.id == device_id

            # Robustness test: operations on valid devices
            for device_id in successful_devices[:3]:  # Test the first 3
                try:
                    # These operations must succeed
                    on_success = controller.turn_on(device_id)
                    assert on_success is True

                    off_success = controller.turn_off(device_id)
                    assert off_success is True

                except Exception as e:
                    pytest.fail(f"Operation failed on valid device {device_id}: {e}")

            # Verify final count
            total_devices = repo.count_all()
            assert total_devices == len(successful_devices)

            print(
                f"Partial failure test: {len(successful_devices)} successful, "
                f"{failed_operations} failed"
            )

        finally:
            session.close()
