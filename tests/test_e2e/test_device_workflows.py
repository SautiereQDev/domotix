"""
End-to-End (E2E) Tests for device management workflows.

These tests validate the complete workflows for device management
by testing the integration between controllers, repositories,
and database persistence layers.

Test Coverage:
    - Device creation workflows
    - State control workflows
    - Search and query workflows
    - Deletion and cleanup workflows
    - Multi-device integration scenarios
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
    """Fixture for a temporary isolated database for each test."""
    # Create a unique temporary database for this test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    # Environment configuration
    original_db = os.environ.get("DOMOTIX_DB_PATH")
    os.environ["DOMOTIX_DB_PATH"] = db_path

    # Force reconfiguration and initialize
    from domotix.core.database import reconfigure_database

    reconfigure_database()
    StateManager.reset_instance()
    create_tables()

    yield db_path

    # Cleanup after the test
    StateManager.reset_instance()
    try:
        os.unlink(db_path)
    except OSError:
        pass

    # Restore environment
    if original_db:
        os.environ["DOMOTIX_DB_PATH"] = original_db
    else:
        os.environ.pop("DOMOTIX_DB_PATH", None)

    # Force a new reconfiguration
    reconfigure_database()


@pytest.fixture
def db_session_factory(isolated_test_db):
    """Factory for creating database sessions."""

    def _create_session():
        return create_session()

    return _create_session


class TestDeviceLifecycleWorkflows:
    """E2E Tests for the complete lifecycle workflows of devices."""

    def test_light_complete_lifecycle(self, db_session_factory):
        """E2E Test: Complete lifecycle of a light."""
        session = db_session_factory()

        try:
            # Phase 1: Creation
            controller = get_controller_factory().create_light_controller(session)
            light_id = controller.create_light("Lifecycle Light", "Test Room")

            assert light_id is not None
            assert isinstance(light_id, str)

            # Phase 2: Retrieval and verification
            light = controller.get_light(light_id)
            assert light is not None
            assert light.name == "Lifecycle Light"
            assert light.location == "Test Room"
            assert not light.is_on  # Initial state OFF

            # Phase 3: State control - Turn On
            success = controller.turn_on(light_id)
            assert success is True

            # Check state after turning on
            light_updated = controller.get_light(light_id)
            assert light_updated is not None
            assert light_updated.is_on is True

            # Phase 4: State control - Turn Off
            success = controller.turn_off(light_id)
            assert success is True

            # Check state after turning off
            light_final = controller.get_light(light_id)
            assert light_final is not None
            assert light_final.is_on is False

            # Phase 5: Deletion
            success = controller.delete_light(light_id)
            assert success is True

            # Verify that the light no longer exists
            deleted_light = controller.get_light(light_id)
            assert deleted_light is None

        finally:
            session.close()

    def test_shutter_complete_lifecycle(self, db_session_factory):
        """E2E Test: Complete lifecycle of a shutter."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_shutter_controller(session)

            # Creation
            shutter_id = controller.create_shutter("Lifecycle Shutter", "Test Room")
            assert shutter_id is not None

            # Initial verification
            shutter = controller.get_shutter(shutter_id)
            assert shutter is not None
            assert shutter.name == "Lifecycle Shutter"
            assert not shutter.is_open  # Initial state closed

            # Opening
            success = controller.open(shutter_id)
            assert success is True

            shutter_open = controller.get_shutter(shutter_id)
            assert shutter_open is not None
            assert shutter_open.is_open is True

            # Closing
            success = controller.close(shutter_id)
            assert success is True

            shutter_closed = controller.get_shutter(shutter_id)
            assert shutter_closed is not None
            assert shutter_closed.is_open is False

            # Deletion
            success = controller.delete_shutter(shutter_id)
            assert success is True

            deleted_shutter = controller.get_shutter(shutter_id)
            assert deleted_shutter is None

        finally:
            session.close()

    def test_sensor_complete_lifecycle(self, db_session_factory):
        """E2E Test: Complete lifecycle of a sensor."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_sensor_controller(session)

            # Creation
            sensor_id = controller.create_sensor("Lifecycle Sensor", "Test Room")
            assert sensor_id is not None

            # Initial verification
            sensor = controller.get_sensor(sensor_id)
            assert sensor is not None
            assert sensor.name == "Lifecycle Sensor"
            # Check initial state
            assert sensor.value is None  # Initial value

            # Update value
            success = controller.update_value(sensor_id, 25.5)
            assert success is True

            sensor_updated = controller.get_sensor(sensor_id)
            assert sensor_updated is not None
            assert abs(sensor_updated.value - 25.5) < 0.001

            # Deletion
            success = controller.delete_sensor(sensor_id)
            assert success is True

            deleted_sensor = controller.get_sensor(sensor_id)
            assert deleted_sensor is None

        finally:
            session.close()


class TestMultiDeviceWorkflows:
    """E2E Tests for workflows involving multiple devices."""

    def test_multi_device_creation_and_management(self, db_session_factory):
        """E2E Test: Creation and management of multiple devices."""
        session = db_session_factory()

        try:
            # Create controllers
            light_controller = get_controller_factory().create_light_controller(session)
            shutter_controller = get_controller_factory().create_shutter_controller(
                session
            )
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )

            # Phase 1: Creation of multiple devices
            devices_created = {}

            # Lights
            for i in range(3):
                light_id = light_controller.create_light(
                    f"Light {i + 1}", f"Room {i + 1}"
                )
                assert light_id is not None
                devices_created[f"light_{i + 1}"] = light_id

            # Shutters
            for i in range(2):
                shutter_id = shutter_controller.create_shutter(
                    f"Shutter {i + 1}", f"Room {i + 1}"
                )
                assert shutter_id is not None
                devices_created[f"shutter_{i + 1}"] = shutter_id

            # Sensors
            for i in range(2):
                sensor_id = sensor_controller.create_sensor(
                    f"Sensor {i + 1}", f"Room {i + 1}"
                )
                assert sensor_id is not None
                devices_created[f"sensor_{i + 1}"] = sensor_id

            # Phase 2: Verification via repository
            repo = DeviceRepository(session)
            all_devices = repo.find_all()

            assert len(all_devices) == 7  # 3 lights + 2 shutters + 2 sensors

            # Check distribution by location
            room1_devices = repo.find_by_location("Room 1")
            assert len(room1_devices) == 3  # One light, one shutter, one sensor

            room2_devices = repo.find_by_location("Room 2")
            assert len(room2_devices) == 3  # One light, one shutter, one sensor

            room3_devices = repo.find_by_location("Room 3")
            assert len(room3_devices) == 1  # One light

            # Phase 3: Group control of lights
            for i in range(3):
                light_id = devices_created[f"light_{i + 1}"]
                success = light_controller.turn_on(light_id)
                assert success is True

            # Verify that all lights are on
            for i in range(3):
                light_id = devices_created[f"light_{i + 1}"]
                light = light_controller.get_light(light_id)
                assert light is not None
                assert light.is_on is True

            # Phase 4: Selective cleanup - delete devices in Room 1
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

            # Commit to ensure deletions are persisted
            session.commit()

            # Verify deletion
            remaining_devices = repo.find_all()
            assert len(remaining_devices) == 4  # 7 - 3 (Room 1)

            room1_remaining = repo.find_by_location("Room 1")
            assert len(room1_remaining) == 0

        finally:
            session.close()

    def test_concurrent_device_operations(self, db_session_factory):
        """E2E Test: Concurrent operations on devices."""
        # This test simulates operations that could happen in parallel
        # in a real application

        session1 = db_session_factory()
        session2 = db_session_factory()

        try:
            controller1 = get_controller_factory().create_light_controller(session1)
            controller2 = get_controller_factory().create_light_controller(session2)

            # Session 1: Create a light
            light_id = controller1.create_light("Concurrent Light", "Shared Room")
            assert light_id is not None

            # Session 2: Try to retrieve the light (should work)
            light_from_session2 = controller2.get_light(light_id)
            assert light_from_session2 is not None
            assert light_from_session2.name == "Concurrent Light"

            # Session 1: Turn on the light
            success1 = controller1.turn_on(light_id)
            assert success1 is True

            # Session 2: Check the state (should reflect the change)
            light_updated = controller2.get_light(light_id)
            assert light_updated is not None
            assert light_updated.is_on is True

            # Session 2: Turn off the light
            success2 = controller2.turn_off(light_id)
            assert success2 is True

            # Session 1: Check the final state
            light_final = controller1.get_light(light_id)
            assert light_final is not None
            assert light_final.is_on is False

        finally:
            session1.close()
            session2.close()


class TestDeviceSearchAndQueryWorkflows:
    """Tests E2E for complex search and query workflows."""

    def test_complex_search_workflows(self, db_session_factory):
        """Test E2E: Complex search workflows."""
        session = db_session_factory()

        try:
            # Prepare test data
            light_controller = get_controller_factory().create_light_controller(session)
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )

            # Create devices with specific patterns
            test_devices = [
                ("Main Living Room Light", "Living Room", "light"),
                ("Secondary Living Room Light", "Living Room", "light"),
                ("Parents Bedroom Light", "Bedroom", "light"),
                ("Temperature Sensor Living Room", "Living Room", "sensor"),
                ("Humidity Sensor Bedroom", "Bedroom", "sensor"),
            ]

            device_ids = {}
            for name, location, device_type in test_devices:
                if device_type == "light":
                    device_id = light_controller.create_light(name, location)
                else:  # sensor
                    device_id = sensor_controller.create_sensor(name, location)

                assert device_id is not None
                device_ids[name] = device_id

            # Repository search tests
            repo = DeviceRepository(session)

            # Test 1: Search by partial name
            living_room_lights = repo.search_by_name("Living Room")
            living_room_device_names = [d.name for d in living_room_lights]

            assert "Main Living Room Light" in living_room_device_names
            assert "Secondary Living Room Light" in living_room_device_names
            assert "Temperature Sensor Living Room" in living_room_device_names
            assert "Parents Bedroom Light" not in living_room_device_names

            # Test 2: Search by location
            bedroom_devices = repo.find_by_location("Bedroom")
            assert len(bedroom_devices) == 2

            bedroom_names = [d.name for d in bedroom_devices]
            assert "Parents Bedroom Light" in bedroom_names
            assert "Humidity Sensor Bedroom" in bedroom_names

            # Test 3: Search by type via specialized controllers
            # Update sensor values to test queries
            temp_sensor_id = device_ids["Temperature Sensor Living Room"]
            humidity_sensor_id = device_ids["Humidity Sensor Bedroom"]

            sensor_controller.update_value(temp_sensor_id, 22.5)
            sensor_controller.update_value(humidity_sensor_id, 65.0)

            # Check values via search
            from domotix.globals.enums import DeviceType

            all_sensors = repo.find_by_type(DeviceType.SENSOR)
            sensor_values = {s.name: s.value for s in all_sensors}

            assert abs(sensor_values["Temperature Sensor Living Room"] - 22.5) < 0.001
            assert abs(sensor_values["Humidity Sensor Bedroom"] - 65.0) < 0.001

            # Test 4: Combined query - all devices in the living room
            living_room_devices = repo.find_by_location("Living Room")
            assert len(living_room_devices) == 3  # 2 lights + 1 sensor

            living_room_lights_only = [
                d for d in living_room_devices if d.device_type.value == "LIGHT"
            ]
            assert len(living_room_lights_only) == 2

        finally:
            session.close()


class TestDeviceDataIntegrityWorkflows:
    """Tests E2E for data integrity during complex workflows."""

    def test_data_consistency_across_operations(self, db_session_factory):
        """Test E2E: Data consistency during complex operations."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_light_controller(session)
            repo = DeviceRepository(session)

            # Phase 1: Creation and immediate verification
            light_id = controller.create_light("Consistency Light", "Test Consistency")

            # Verify via controller
            light_via_controller = controller.get_light(light_id)
            assert light_via_controller is not None

            # Verify via repository
            light_via_repo = repo.find_by_id(light_id)
            assert light_via_repo is not None

            # Data should be identical
            assert light_via_controller.id == light_via_repo.id
            assert light_via_controller.name == light_via_repo.name
            assert light_via_controller.location == light_via_repo.location
            assert light_via_controller.is_on == light_via_repo.is_on

            # Phase 2: Modification and consistency verification
            success = controller.turn_on(light_id)
            assert success is True

            # Verify that both access methods see the change
            light_via_controller_updated = controller.get_light(light_id)
            light_via_repo_updated = repo.find_by_id(light_id)

            assert light_via_controller_updated.is_on is True
            assert light_via_repo_updated.is_on is True

            # Phase 3: Counting and integrity of collections
            # Create multiple lights
            additional_lights = []
            for i in range(5):
                light_id_extra = controller.create_light(
                    f"Light {i}", "Test Consistency"
                )
                additional_lights.append(light_id_extra)

            # Verify counting
            total_devices = repo.count_all()
            assert total_devices == 6  # 1 initial + 5 additional

            consistency_devices = repo.find_by_location("Test Consistency")
            assert len(consistency_devices) == 6

            # Phase 4: Deletion and integrity verification
            # Delete some lights
            for light_id_to_delete in additional_lights[:3]:
                success = controller.delete_light(light_id_to_delete)
                assert success is True

            # Verify that counts are consistent
            remaining_total = repo.count_all()
            assert remaining_total == 3  # 6 - 3 deleted

            remaining_in_location = repo.find_by_location("Test Consistency")
            assert len(remaining_in_location) == 3

            # Verify that the correct lights have been deleted
            for deleted_id in additional_lights[:3]:
                deleted_light = controller.get_light(deleted_id)
                assert deleted_light is None

            # Verify that the remaining lights still exist
            for remaining_id in [light_id] + additional_lights[3:]:
                remaining_light = controller.get_light(remaining_id)
                assert remaining_light is not None

        finally:
            session.close()

    def test_error_recovery_workflows(self, db_session_factory):
        """E2E Test: Error recovery workflows."""
        session = db_session_factory()

        try:
            controller = get_controller_factory().create_light_controller(session)

            # Test 1: Attempt operation on non-existent device
            fake_id = str(uuid4())

            # These operations should fail gracefully
            result = controller.get_light(fake_id)
            assert result is None

            turn_on_result = controller.turn_on(fake_id)
            assert turn_on_result is False

            delete_result = controller.delete_light(fake_id)
            assert delete_result is False

            # Test 2: Ensure errors do not affect real data
            # Create a real light
            real_light_id = controller.create_light("Real Light", "Real Room")
            assert real_light_id is not None

            # Attempt invalid operations
            controller.turn_on(fake_id)  # Failure
            controller.get_light("invalid-id")  # Failure

            # Verify that the real light is unaffected
            real_light = controller.get_light(real_light_id)
            assert real_light is not None
            assert real_light.name == "Real Light"
            assert real_light.location == "Real Room"

            # Test 3: Valid operation after errors
            success = controller.turn_on(real_light_id)
            assert success is True

            updated_light = controller.get_light(real_light_id)
            assert updated_light is not None
            assert updated_light.is_on is True

        finally:
            session.close()
