#!/usr/bin/env python3
"""
Direct test of a simple E2E workflow to verify that everything works.
"""

import os
import sys
import tempfile
import traceback

# Add project path to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

try:
    from domotix.core.database import create_session, create_tables
    from domotix.core.factories import get_controller_factory
    from domotix.core.state_manager import StateManager
    from domotix.repositories.device_repository import DeviceRepository

    def test_simple_e2e_workflow():
        """Simple E2E test to verify basic functionality."""
        print("🚀 Starting simple E2E test...")

        # Test environment setup
        temp_dir = tempfile.mkdtemp(prefix="domotix_simple_e2e_")
        db_path = os.path.join(temp_dir, "test_simple.db")

        original_db = os.environ.get("DOMOTIX_DB_PATH")
        os.environ["DOMOTIX_DB_PATH"] = db_path

        try:
            # Initialize the system
            StateManager.reset_instance()
            create_tables()
            print("✅ Database initialized")

            # Device creation test
            session = create_session()
            try:
                controller = get_controller_factory().create_light_controller(session)
                print("✅ Controller created")

                # Create a light
                light_id = controller.create_light("E2E Test Light", "Test Room")
                assert light_id is not None, "Light creation failed"
                print(f"✅ Light created with ID: {light_id}")

                # Verify the light
                light = controller.get_light(light_id)
                assert light is not None, "Light retrieval failed"
                assert light.name == "E2E Test Light", "Incorrect light name"
                assert light.location == "Test Room", "Incorrect location"
                print("✅ Light verified")

                # State test
                success = controller.turn_on(light_id)
                assert success is True, "Turn on failed"
                print("✅ Light turned on")

                # Verify state
                light_on = controller.get_light(light_id)
                assert light_on.is_on is True, "Incorrect light on state"
                print("✅ Light on state verified")

                # Test repository
                repo = DeviceRepository(session)

                # Count before creation for reference
                initial_count = repo.count_all()
                print(f"Initial devices count: {initial_count}")

                # Verify our light exists
                our_light = repo.find_by_id(light_id)
                assert our_light is not None, "Our light does not exist in the database"
                assert our_light.name == "E2E Test Light", "Incorrect name in database"
                print("✅ Repository functional")

                # Deletion test
                success = controller.delete_light(light_id)
                assert success is True, "Deletion failed"

                deleted_light = controller.get_light(light_id)
                assert deleted_light is None, "Light not deleted"
                print("✅ Light deleted")

                print("🎉 Simple E2E test passed!")
                return True

            finally:
                session.close()

        finally:
            # Cleanup
            StateManager.reset_instance()
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            if original_db:
                os.environ["DOMOTIX_DB_PATH"] = original_db
            else:
                os.environ.pop("DOMOTIX_DB_PATH", None)

    if __name__ == "__main__":
        try:
            success = test_simple_e2e_workflow()
            if success:
                print("\n✅ All basic E2E tests are functional!")
                sys.exit(0)
            else:
                print("\n❌ Basic E2E tests failed")
                sys.exit(1)
        except Exception as e:
            print(f"\n💥 Error during E2E test: {e}")
            print("\nComplete stacktrace:")
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure the project is correctly configured")
    sys.exit(1)
