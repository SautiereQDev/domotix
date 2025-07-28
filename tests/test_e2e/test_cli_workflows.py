"""
End-to-End (E2E) Tests for Domotix CLI workflows.

These tests validate the entire user journey from CLI commands
to database persistence, simulating real usage scenarios.

Test Coverage:
    - Device creation via CLI
    - Device listing and search
    - Device state control
    - Device deletion
    - Complete user workflows
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from domotix.core.database import create_session, create_tables
from domotix.repositories.device_repository import DeviceRepository


class CliTestRunner:
    """Helper to run CLI commands in test mode."""

    def __init__(self, test_db_path):
        """Initialize the CLI runner with the test database path."""
        self.test_db_path = test_db_path
        self.project_root = Path(__file__).parent.parent.parent
        self.cli_script = self.project_root / "domotix" / "cli" / "main.py"

    def run_cli_command(self, args):
        """Run domotix CLI command."""
        # Use Poetry to run with correct dependencies
        cmd = ["poetry", "run", "python", "-m", "domotix.cli.main"] + args
        env = {**os.environ, "DOMOTIX_DB_PATH": self.test_db_path}

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)


@pytest.fixture
def cli_runner(test_db_path):
    """Fixture providing a configured CLI runner."""
    return CliTestRunner(test_db_path)


@pytest.fixture
def test_db_path():
    """Fixture to create an isolated temporary database for each test."""
    # Create a unique temporary database for this test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    # Configure the environment
    original_db_path = os.environ.get("DOMOTIX_DB_PATH")
    os.environ["DOMOTIX_DB_PATH"] = db_path

    # Force reconfiguration of the database
    from domotix.core.database import reconfigure_database

    reconfigure_database()
    create_tables()

    yield db_path

    # Cleanup after the test
    try:
        os.unlink(db_path)
    except OSError:
        pass

    # Restore the environment
    if original_db_path:
        os.environ["DOMOTIX_DB_PATH"] = original_db_path
    else:
        os.environ.pop("DOMOTIX_DB_PATH", None)

    # Force a new reconfiguration
    reconfigure_database()


class TestDeviceCreationWorkflows:
    """E2E tests for device creation workflows."""

    def test_create_light_via_cli(self, cli_runner, test_db_path):
        """E2E Test: Create a light via CLI."""
        # Step 1: Create a light
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "light", "Lampe Salon", "--location", "Salon"]
        )

        # Check that the command succeeded
        assert return_code == 0, f"CLI failed: {stderr}"
        assert "Light 'Lampe Salon' created" in stdout
        assert "Salon" in stdout

        # Step 2: Verify the light is in the database
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.find_all()

            # Check there is exactly one device
            assert len(devices) == 1

            device = devices[0]
            assert device.name == "Lampe Salon"
            assert device.location == "Salon"
            assert device.device_type.value == "LIGHT"
        finally:
            session.close()

    def test_create_shutter_via_cli(self, cli_runner, test_db_path):
        """E2E Test: Create a shutter via CLI."""
        # Create a shutter
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "shutter", "Volet Chambre", "--location", "Chambre"]
        )

        assert return_code == 0, f"CLI failed: {stderr}"
        assert "Volet 'Volet Chambre' créé" in stdout

        # Verify persistence
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.find_by_location("Chambre")

            assert len(devices) == 1
            assert devices[0].name == "Volet Chambre"
            assert devices[0].device_type.value == "SHUTTER"
        finally:
            session.close()

    def test_create_sensor_via_cli(self, cli_runner, test_db_path):
        """E2E Test: Create a sensor via CLI."""
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "sensor", "Capteur Température", "--location", "Cuisine"]
        )

        assert return_code == 0, f"CLI failed: {stderr}"
        assert "Capteur 'Capteur Température' créé" in stdout

        # Verify persistence
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.search_by_name("Température")

            assert len(devices) == 1
            assert devices[0].name == "Capteur Température"
            assert devices[0].device_type.value == "SENSOR"
        finally:
            session.close()


class TestDeviceListingWorkflows:
    """E2E tests for device listing workflows."""

    def test_list_all_devices_workflow(self, cli_runner, test_db_path):
        """E2E Test: Full workflow of creation and listing."""
        # Step 1: Create multiple devices
        devices_to_create = [
            (["device-add", "light", "Lampe1", "--location", "Salon"], "Lampe1"),
            (["device-add", "shutter", "Volet1", "--location", "Chambre"], "Volet1"),
            (["device-add", "sensor", "Capteur1", "--location", "Cuisine"], "Capteur1"),
        ]

        for cmd, expected_name in devices_to_create:
            return_code, stdout, stderr = cli_runner.run_cli_command(cmd)
            assert return_code == 0, f"Failed to create {expected_name}: {stderr}"
            assert expected_name in stdout

        # Step 2: List all devices
        return_code, stdout, stderr = cli_runner.run_cli_command(["device-list"])

        assert return_code == 0, f"List command failed: {stderr}"

        # Check that all created devices appear in the list
        for _, expected_name in devices_to_create:
            assert expected_name in stdout

        # Check that locations appear
        assert "Salon" in stdout
        assert "Chambre" in stdout
        assert "Cuisine" in stdout

    def test_list_devices_by_type(self, cli_runner, test_db_path):
        """E2E Test: Listing devices by type."""
        # Create devices of different types
        cli_runner.run_cli_command(["device-add", "light", "Lampe1"])
        cli_runner.run_cli_command(["device-add", "light", "Lampe2"])
        cli_runner.run_cli_command(["device-add", "shutter", "Volet1"])

        # List only the lights
        return_code, stdout, stderr = cli_runner.run_cli_command(["lights-list"])

        assert return_code == 0, f"List lights failed: {stderr}"
        assert "Lampe1" in stdout
        assert "Lampe2" in stdout
        assert "Volet1" not in stdout  # Shutters should not appear


class TestDeviceStateWorkflows:
    """E2E tests for state control workflows."""

    def test_light_control_workflow(self, cli_runner, test_db_path):
        """E2E Test: Complete workflow for controlling a light."""
        # Step 1: Create a light
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "light", "Lampe Test"]
        )
        assert return_code == 0

        # Extract the ID of the created light (supposed to be in stdout)
        lines = stdout.strip().split("\n")
        device_id = None
        for line in lines:
            if "ID:" in line:
                device_id = line.split("ID:")[-1].strip()
                break

        assert device_id is not None, "Device ID not found in creation output"

        # Step 2: Turn on the light
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["light-on", device_id]
        )
        assert return_code == 0, f"Turn on failed: {stderr}"

        # Step 3: Check the status via CLI
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-status", device_id]
        )
        assert return_code == 0, f"Status check failed: {stderr}"
        assert "ON" in stdout.upper() or "allumé" in stdout.lower()

        # Step 4: Turn off the light
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["light-off", device_id]
        )
        assert return_code == 0, f"Turn off failed: {stderr}"

        # Step 5: Check final status
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-status", device_id]
        )
        assert return_code == 0, f"Final status check failed: {stderr}"
        assert "OFF" in stdout.upper() or "éteint" in stdout.lower()


class TestCompleteUserWorkflows:
    """E2E tests for complete and realistic user workflows."""

    def test_home_automation_scenario(self, cli_runner, test_db_path):
        """
        E2E Test: Complete home automation scenario.

        Simulates a user setting up their complete home automation system.
        """
        # Scenario: Setting up an apartment with living room, bedroom, kitchen

        # Phase 1: Living room setup
        salon_devices = [
            ["device-add", "light", "Lampe Principale", "--location", "Salon"],
            ["device-add", "light", "Lampe d'Appoint", "--location", "Salon"],
            ["device-add", "shutter", "Volet Salon", "--location", "Salon"],
        ]

        for cmd in salon_devices:
            return_code, stdout, stderr = cli_runner.run_cli_command(cmd)
            assert return_code == 0, f"Failed salon setup: {stderr}"

        # Phase 2: Bedroom setup
        chambre_devices = [
            ["device-add", "light", "Lampe Chevet", "--location", "Chambre"],
            ["device-add", "shutter", "Volet Chambre", "--location", "Chambre"],
            ["device-add", "sensor", "Capteur Température", "--location", "Chambre"],
        ]

        for cmd in chambre_devices:
            return_code, stdout, stderr = cli_runner.run_cli_command(cmd)
            assert return_code == 0, f"Failed chambre setup: {stderr}"

        # Phase 3: Verify complete installation
        return_code, stdout, stderr = cli_runner.run_cli_command(["device-list"])
        assert return_code == 0

        # Check that all devices are present
        expected_devices = [
            "Lampe Principale",
            "Lampe d'Appoint",
            "Volet Salon",
            "Lampe Chevet",
            "Volet Chambre",
            "Capteur Température",
        ]

        for device_name in expected_devices:
            assert device_name in stdout, f"Device {device_name} not found in listing"

        # Phase 4: Test group control by location
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["devices-by-location", "Salon"]
        )
        assert return_code == 0
        assert "Lampe Principale" in stdout
        assert "Lampe d'Appoint" in stdout
        assert "Volet Salon" in stdout
        assert "Lampe Chevet" not in stdout  # Should not be in the living room

        # Final persistence check in the database
        session = create_session()
        try:
            repo = DeviceRepository(session)
            all_devices = repo.find_all()

            assert len(all_devices) == 6  # 6 devices created

            salon_devices_db = repo.find_by_location("Salon")
            assert len(salon_devices_db) == 3

            chambre_devices_db = repo.find_by_location("Chambre")
            assert len(chambre_devices_db) == 3

        finally:
            session.close()

    def test_error_handling_workflow(self, cli_runner, test_db_path):
        """E2E Test: Error handling in workflows."""
        # Test 1: Create a device with an empty name (may be accepted)
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "light", ""]
        )
        # An empty name might be accepted, just testing that it doesn't crash

        # Test 2: Try to control a non-existent device
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["light-on", "inexistent-id-12345"]
        )
        # Check that an error is reported (in stdout or stderr)
        assert (
            "Échec" in stdout or "erreur" in stderr.lower() or "error" in stderr.lower()
        )

        # Test 3: Create a device with an invalid type
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "invalid-type", "Test Device"]
        )
        # Check that the invalid type is rejected
        assert "non supporté" in stdout or "not supported" in stderr or return_code != 0

        # Check that no invalid device has been created
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.find_all()
            # Only the device with an empty name might exist (if accepted)
            assert len(devices) <= 1
            if len(devices) == 1:
                # If a device was created, it should be the one with the empty name
                assert devices[0].name == ""
        finally:
            session.close()
