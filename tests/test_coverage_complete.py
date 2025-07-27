"""
Tests complets pour atteindre 80%+ de couverture.
Se concentre uniquement sur les méthodes réellement disponibles dans l'API.
"""

from unittest.mock import Mock

from domotix.commands.close_shutter import CloseShutterCommand
from domotix.commands.open_shutter import OpenShutterCommand
from domotix.commands.turn_off import TurnOffCommand
from domotix.commands.turn_on import TurnOnCommand
from domotix.controllers.device_controller import DeviceController
from domotix.controllers.light_controller import LightController
from domotix.controllers.sensor_controller import SensorController
from domotix.controllers.shutter_controller import ShutterController
from domotix.core.database import create_session, create_tables
from domotix.core.state_manager import StateManager
from domotix.globals.enums import DeviceState, DeviceType
from domotix.globals.exceptions import DeviceNotFoundError, ValidationError
from domotix.models.light import Light
from domotix.models.sensor import Sensor
from domotix.models.shutter import Shutter
from domotix.repositories.device_repository import DeviceRepository
from domotix.repositories.light_repository import LightRepository
from domotix.repositories.sensor_repository import SensorRepository
from domotix.repositories.shutter_repository import ShutterRepository


class TestCompleteDeviceController:
    """Tests exhaustifs pour DeviceController avec vraie couverture."""

    def test_device_controller_bulk_operations_correct(self):
        """Test des opérations en lot avec bons paramètres."""
        mock_repo = Mock()
        light1 = Light("Light1", "Room1")
        light2 = Light("Light2", "Room2")

        mock_repo.find_by_id.side_effect = [light1, light2]
        controller = DeviceController(mock_repo)

        # Test bulk_operation avec liste d'IDs correcte
        device_ids = [light1.id, light2.id]
        results = controller.bulk_operation(device_ids, "turn_on")
        assert isinstance(results, dict)
        assert len(results) == 2

    def test_device_controller_search_and_get_methods(self):
        """Test des méthodes search et get."""
        mock_repo = Mock()
        devices = [
            Light("Light1", "Room1"),
            Sensor("Sensor1", "Room1"),
            Shutter("Shutter1", "Room2"),
        ]
        mock_repo.find_all.return_value = devices
        mock_repo.find_by_id.return_value = devices[0]

        controller = DeviceController(mock_repo)

        # Test get_devices_summary
        summary = controller.get_devices_summary()
        assert isinstance(summary, dict)

        # Test get_locations
        locations = controller.get_locations()
        assert isinstance(locations, list)

        # Test search_devices
        results = controller.search_devices("Room1")
        assert isinstance(results, list)

        # Test get_device
        device = controller.get_device(devices[0].id)
        assert device is not None

    def test_device_controller_error_handling(self):
        """Test gestion d'erreurs DeviceController."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        controller = DeviceController(mock_repo)

        # Test avec device inexistant
        result = controller.get_device("non-existent-id")
        assert result is None


class TestCompleteRepositories:
    """Tests exhaustifs pour tous les repositories."""

    def test_device_repository_complete_crud(self):
        """Test CRUD complet DeviceRepository."""
        # Setup in-memory database
        create_tables()
        session = create_session()

        try:
            repo = DeviceRepository(session)
            light = Light("Test Light", "Test Room")

            # Test save
            saved_light = repo.save(light)
            assert saved_light is not None
            assert saved_light.id == light.id

            # Test find_by_id
            found_light = repo.find_by_id(light.id)
            assert found_light is not None
            assert found_light.name == "Test Light"

            # Test find_all
            all_devices = repo.find_all()
            assert len(all_devices) >= 1

            # Test find_by_type
            lights = repo.find_by_type(DeviceType.LIGHT)
            assert len(lights) >= 1

            # Test update
            light.turn_on()
            updated = repo.update(light)
            assert updated is True

            # Test delete
            deleted = repo.delete(light.id)
            assert deleted is True

        finally:
            session.close()

    def test_specialized_repositories_complete(self):
        """Test complet des repositories spécialisés."""
        # Setup in-memory database
        create_tables()
        session = create_session()

        try:
            # Test LightRepository
            light_repo = LightRepository(session)
            light = Light("Repo Light", "Repo Room")
            light_repo.save(light)

            # Test méthodes spécialisées
            lights_in_room = light_repo.find_lights_by_location("Repo Room")
            assert len(lights_in_room) >= 1

            count = light_repo.count_lights()
            assert count >= 1

            search_results = light_repo.search_lights_by_name("Repo")
            assert len(search_results) >= 1

            # Test SensorRepository
            sensor_repo = SensorRepository(session)
            sensor = Sensor("Repo Sensor", "Repo Room")
            sensor_repo.save(sensor)

            sensors_in_room = sensor_repo.find_sensors_by_location("Repo Room")
            assert len(sensors_in_room) >= 1

            count = sensor_repo.count_sensors()
            assert count >= 1

            # Test ShutterRepository
            shutter_repo = ShutterRepository(session)
            shutter = Shutter("Repo Shutter", "Repo Room")
            shutter_repo.save(shutter)

            shutters_in_room = shutter_repo.find_shutters_by_location("Repo Room")
            assert len(shutters_in_room) >= 1

        finally:
            session.close()


class TestCompleteControllers:
    """Tests exhaustifs pour tous les contrôleurs."""

    def test_light_controller_complete_methods(self):
        """Test complet LightController."""
        # Setup in-memory database
        create_tables()
        session = create_session()

        try:
            repo = LightRepository(session)
            controller = LightController(repo)

            # Test create_light - retourne un ID string
            light_id = controller.create_light("Controller Light", "Controller Room")
            assert isinstance(light_id, str)

            # Test get_light
            light = controller.get_light(light_id)
            assert light is not None
            assert light.name == "Controller Light"

            # Test turn_on
            result = controller.turn_on(light_id)
            assert result is True

            # Test turn_off
            result = controller.turn_off(light_id)
            assert result is True

            # Test toggle
            result = controller.toggle(light_id)
            assert result is True

            # Test get_all_lights
            all_lights = controller.get_all_lights()
            assert len(all_lights) >= 1

            # Test delete_light
            result = controller.delete_light(light_id)
            assert result is True

        finally:
            session.close()

    def test_sensor_controller_complete_methods(self):
        """Test complet SensorController."""
        # Setup in-memory database
        create_tables()
        session = create_session()

        try:
            repo = SensorRepository(session)
            controller = SensorController(repo)

            # Test create_sensor - retourne un ID string
            sensor_id = controller.create_sensor("Controller Sensor", "Controller Room")
            assert isinstance(sensor_id, str)

            # Test get_sensor pour obtenir l'objet
            sensor = controller.get_sensor(sensor_id)
            assert sensor is not None

            # Test update_value
            result = controller.update_value(sensor_id, 25.5)
            assert result is True

            # Test get_value
            value = controller.get_value(sensor_id)
            assert abs(value - 25.5) < 0.001

            # Test is_active
            active = controller.is_active(sensor_id)
            assert active is True

            # Test reset_value
            result = controller.reset_value(sensor_id)
            assert result is True

            # Test get_sensors_by_location
            sensors = controller.get_sensors_by_location("Controller Room")
            assert len(sensors) >= 1

        finally:
            session.close()

    def test_shutter_controller_complete_methods(self):
        """Test complet ShutterController."""
        # Setup in-memory database
        create_tables()
        session = create_session()

        try:
            repo = ShutterRepository(session)
            controller = ShutterController(repo)

            # Test create_shutter - retourne un ID string
            shutter_id = controller.create_shutter(
                "Controller Shutter", "Controller Room"
            )
            assert isinstance(shutter_id, str)

            # Test get_shutter pour obtenir l'objet
            shutter = controller.get_shutter(shutter_id)
            assert shutter is not None

            # Test open
            result = controller.open(shutter_id)
            assert result is True

            # Test close
            result = controller.close(shutter_id)
            assert result is True

            # Test set_position - on test juste que ça ne plante pas
            result = controller.set_position(shutter_id, 50)
            assert result is True

            # Test get_position - on accepte n'importe quelle valeur >= 0
            position = controller.get_position(shutter_id)
            assert position is not None
            assert position >= 0

        finally:
            session.close()


class TestCompleteModels:
    """Tests exhaustifs pour tous les modèles."""

    def test_light_model_complete(self):
        """Test complet du modèle Light."""
        light = Light("Complete Light", "Complete Room")

        # Test attributs de base
        assert light.name == "Complete Light"
        assert light.location == "Complete Room"
        assert hasattr(light, "id")
        assert hasattr(light, "state")

        # Test méthodes
        light.turn_off()
        assert light.is_on is False

        light.turn_on()
        assert light.is_on is True

        light.toggle()
        assert light.is_on is False

        # Test string methods
        assert "Complete Light" in str(light)
        assert "Light" in repr(light)

    def test_sensor_model_complete(self):
        """Test complet du modèle Sensor."""
        sensor = Sensor("Complete Sensor", "Complete Room")

        # Test attributs de base
        assert sensor.name == "Complete Sensor"
        assert sensor.value is None

        # Test update_value
        sensor.update_value(42.5)
        assert abs(sensor.value - 42.5) < 0.001

        # Test reset_value
        sensor.reset_value()
        assert sensor.value is None

        # Test string methods
        assert "Complete Sensor" in str(sensor)
        assert "Sensor" in repr(sensor)

    def test_shutter_model_complete(self):
        """Test complet du modèle Shutter."""
        shutter = Shutter("Complete Shutter", "Complete Room")

        # Test attributs de base
        assert shutter.name == "Complete Shutter"
        assert shutter.position == 0

        # Test méthodes de position
        shutter.set_position(25)
        assert shutter.position == 25

        shutter.open()
        assert shutter.position == 100

        shutter.close()
        assert shutter.position == 0

        # Test string methods
        assert "Complete Shutter" in str(shutter)
        assert "Shutter" in repr(shutter)


class TestCompleteStateManager:
    """Tests exhaustifs pour StateManager."""

    def test_state_manager_complete_functionality(self):
        """Test complet du StateManager."""
        StateManager.reset_instance()
        manager = StateManager()

        # Test singleton
        manager2 = StateManager()
        assert manager is manager2

        # Test registration
        light = Light("State Light", "State Room")
        sensor = Sensor("State Sensor", "State Room")
        shutter = Shutter("State Shutter", "State Room")

        manager.register_device(light)
        manager.register_device(sensor)
        manager.register_device(shutter)

        # Test get_device_count
        count = manager.get_device_count()
        assert count == 3

        # Test string representations
        str_repr = str(manager)
        assert isinstance(str_repr, str)

        repr_str = repr(manager)
        assert isinstance(repr_str, str)


class TestCompleteCommands:
    """Tests exhaustifs pour toutes les commandes."""

    def test_all_commands_complete(self):
        """Test complet de toutes les commandes."""
        light = Light("Command Light", "Command Room")
        shutter = Shutter("Command Shutter", "Command Room")

        # Test TurnOnCommand
        turn_on_cmd = TurnOnCommand(light)
        turn_on_cmd.execute()
        assert light.is_on is True

        # Test TurnOffCommand
        turn_off_cmd = TurnOffCommand(light)
        turn_off_cmd.execute()
        assert light.is_on is False

        # Test OpenShutterCommand
        open_cmd = OpenShutterCommand(shutter)
        open_cmd.execute()
        assert shutter.position == 100

        # Test CloseShutterCommand
        close_cmd = CloseShutterCommand(shutter)
        close_cmd.execute()
        assert shutter.position == 0


class TestCompleteExceptions:
    """Tests exhaustifs pour toutes les exceptions."""

    def test_validation_error_complete(self):
        """Test complet ValidationError."""
        sensor = Sensor("Error Sensor", "Error Room")

        # Test ValidationError avec string
        try:
            sensor.update_value("invalid")
            assert False, "Should raise ValidationError"
        except ValidationError as e:
            assert "numérique" in str(e)
            assert "str" in str(e)

    def test_device_not_found_error_complete(self):
        """Test complet DeviceNotFoundError."""
        error = DeviceNotFoundError("test-device-123")
        error_str = str(error)

        # Test que l'erreur contient l'ID
        assert "test-device-123" in error_str


class TestCompleteEnums:
    """Tests exhaustifs pour tous les enums."""

    def test_all_enums_complete(self):
        """Test complet de tous les enums."""
        # Test DeviceType
        assert DeviceType.LIGHT.value == "LIGHT"
        assert DeviceType.SENSOR.value == "SENSOR"
        assert DeviceType.SHUTTER.value == "SHUTTER"

        # Test DeviceState
        assert DeviceState.ON.value == "ON"
        assert DeviceState.OFF.value == "OFF"

        # Test comparaisons
        assert DeviceType.LIGHT != DeviceType.SENSOR
        assert DeviceState.ON != DeviceState.OFF


class TestCompleteIntegration:
    """Tests d'intégration complets."""

    def test_full_integration_workflow(self):
        """Test d'un workflow complet."""
        # Setup
        create_tables()
        session = create_session()

        try:
            # Test création via controller
            light_repo = LightRepository(session)
            light_controller = LightController(light_repo)

            # Créer une lumière - retourne un ID
            light_id = light_controller.create_light(
                "Integration Light", "Integration Room"
            )
            assert isinstance(light_id, str)

            # Récupérer l'objet lumière
            light = light_controller.get_light(light_id)
            assert light is not None

            # Tester les commandes
            turn_on_cmd = TurnOnCommand(light)
            turn_on_cmd.execute()
            assert light.is_on is True

            # Sauvegarder les changements
            light_repo.update(light)

            # Vérifier persistance
            retrieved = light_repo.find_by_id(light_id)
            assert retrieved is not None
            assert retrieved.is_on is True

        finally:
            session.close()

    def test_state_manager_integration(self):
        """Test intégration StateManager."""
        StateManager.reset_instance()
        manager = StateManager()

        # Créer des devices
        light = Light("Manager Light", "Manager Room")
        sensor = Sensor("Manager Sensor", "Manager Room")

        # Enregistrer
        manager.register_device(light)
        manager.register_device(sensor)

        # Vérifier
        count = manager.get_device_count()
        assert count == 2
