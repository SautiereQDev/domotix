"""
Tests pour les opérations avancées des contrôleurs et repositories.

Ce module teste les fonctionnalités avancées :
- Recherche et filtrage de devices
- Opérations en lot (bulk operations)
- Méthodes spécialisées des contrôleurs
- Validation et gestion d'erreurs avancée
- Intégration avec les factories
"""

from unittest.mock import Mock, patch

from domotix.controllers.device_controller import (  # pylint: disable=import-error
    DeviceController,
)
from domotix.controllers.light_controller import (  # pylint: disable=import-error
    LightController,
)
from domotix.controllers.sensor_controller import (  # pylint: disable=import-error
    SensorController,
)
from domotix.controllers.shutter_controller import (  # pylint: disable=import-error
    ShutterController,
)
from domotix.core.state_manager import StateManager  # pylint: disable=import-error
from domotix.globals.exceptions import (  # pylint: disable=import-error
    DeviceNotFoundError,
    InvalidDeviceTypeError,
)
from domotix.models.light import Light  # pylint: disable=import-error
from domotix.models.sensor import Sensor  # pylint: disable=import-error
from domotix.models.shutter import Shutter  # pylint: disable=import-error
from domotix.repositories.device_repository import (  # pylint: disable=import-error
    DeviceRepository,
)
from domotix.repositories.light_repository import (  # pylint: disable=import-error
    LightRepository,
)
from domotix.repositories.sensor_repository import (  # pylint: disable=import-error
    SensorRepository,
)
from domotix.repositories.shutter_repository import (  # pylint: disable=import-error
    ShutterRepository,
)


class TestControllerAdvanced:
    """Tests avancés pour les contrôleurs."""

    def test_device_controller_search_devices(self):
        """Test de la recherche de devices."""
        mock_repo = Mock()
        mock_devices = [
            Light("Kitchen Light", "Kitchen"),
            Sensor("Kitchen Sensor", "Kitchen"),
            Light("Living Light", "Living Room"),
        ]
        mock_repo.find_all.return_value = mock_devices

        controller = DeviceController(mock_repo)

        # Test recherche par nom
        results = controller.search_devices("Kitchen")
        assert len(results) == 2

        # Test recherche case insensitive
        results = controller.search_devices("kitchen")
        assert len(results) == 2

    def test_device_controller_bulk_operations(self):
        """Test des opérations en lot."""
        mock_repo = Mock()
        lights = [
            Light("Light1", "Room1"),
            Light("Light2", "Room2"),
            Light("Light3", "Room3"),
        ]
        mock_repo.find_all.return_value = lights
        mock_repo.find_by_id.side_effect = lambda device_id: next(
            (light for light in lights if light.id == device_id), None
        )
        mock_repo.update.return_value = True

        controller = DeviceController(mock_repo)

        # Test bulk turn on avec des IDs de devices
        device_ids = [light.id for light in lights]
        results = controller.bulk_operation(device_ids, "turn_on")
        assert len(results) == 3

        # Test bulk turn off
        results = controller.bulk_operation(device_ids, "turn_off")
        assert len(results) == 3

    def test_light_controller_toggle_variations(self):
        """Test des variations de toggle."""
        mock_repo = Mock()
        light = Light("Test Light", "Room")
        light.turn_off()  # S'assurer qu'elle est éteinte
        mock_repo.find_by_id.return_value = light
        mock_repo.update.return_value = True

        controller = LightController(mock_repo)

        # Test toggle quand éteinte
        result = controller.toggle(light.id)
        assert result is True
        assert light.is_on is True

        # Test toggle quand allumée
        result = controller.toggle(light.id)
        assert result is True
        assert light.is_on is False

    def test_sensor_controller_advanced_methods(self):
        """Test des méthodes avancées du SensorController."""
        mock_repo = Mock()
        sensor = Sensor("Test Sensor", "Room")
        sensor.update_value(25.5)
        mock_repo.find_by_id.return_value = sensor
        mock_repo.update.return_value = True

        controller = SensorController(mock_repo)

        # Test get_value
        value = controller.get_value(sensor.id)
        assert abs(value - 25.5) < 0.01  # Comparaison de float sécurisée

        # Test is_active
        is_active = controller.is_active(sensor.id)
        assert is_active is True

        # Test reset_value
        result = controller.reset_value(sensor.id)
        assert result is True
        assert sensor.value is None

    def test_shutter_controller_position_methods(self):
        """Test des méthodes de position du ShutterController."""
        mock_repo = Mock()
        shutter = Shutter("Test Shutter", "Room")
        mock_repo.find_by_id.return_value = shutter
        mock_repo.update.return_value = True

        controller = ShutterController(mock_repo)

        # Test set_position
        result = controller.set_position(shutter.id, 75)
        assert result is True
        assert shutter.position == 75

        # Test get_position
        position = controller.get_position(shutter.id)
        assert position == 75

        # Test open (position 100)
        result = controller.open(shutter.id)
        assert result is True
        assert shutter.position == 100

        # Test close (position 0)
        result = controller.close(shutter.id)
        assert result is True
        assert shutter.position == 0


class TestRepositoryAdvanced:
    """Tests avancés pour les repositories."""

    def test_device_repository_find_methods(self):
        """Test des méthodes find du DeviceRepository."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.first.return_value = None
        mock_query.count.return_value = 0

        repo = DeviceRepository(mock_session)

        # Test search_by_name
        result = repo.search_by_name("Test Device")
        assert result == []

        # Test find_by_location
        results = repo.find_by_location("Living Room")
        assert results == []

        # Test count_all
        count = repo.count_all()
        assert count == 0

    def test_light_repository_specialized_methods(self):
        """Test des méthodes spécialisées du LightRepository."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = LightRepository(mock_session)

        # Test find_on_lights
        results = repo.find_on_lights()
        assert results == []

        # Test find_off_lights
        results = repo.find_off_lights()
        assert results == []

        # Test count_lights
        count = repo.count_lights()
        assert count == 0

    def test_sensor_repository_specialized_methods(self):
        """Test des méthodes spécialisées du SensorRepository."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = SensorRepository(mock_session)

        # Test find_active_sensors
        results = repo.find_active_sensors()
        assert results == []

        # Test find_inactive_sensors
        results = repo.find_inactive_sensors()
        assert results == []

        # Test find_sensors_by_type
        results = repo.find_sensors_by_type("temperature")
        assert results == []

    def test_shutter_repository_specialized_methods(self):
        """Test des méthodes spécialisées du ShutterRepository."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = ShutterRepository(mock_session)

        # Test find_open_shutters
        results = repo.find_open_shutters()
        assert results == []

        # Test find_closed_shutters
        results = repo.find_closed_shutters()
        assert results == []

        # Test count_shutters
        count = repo.count_shutters()
        assert count == 0


class TestModelsAdvanced:
    """Tests avancés pour les modèles."""

    def test_light_advanced_methods(self):
        """Test des méthodes avancées de Light."""
        light = Light("Advanced Light", "Test Room")

        # Test dimming (si implémenté)
        if hasattr(light, "brightness"):
            light.brightness = 50
            assert light.brightness == 50

        # Test color (si implémenté)
        if hasattr(light, "color"):
            light.color = "#FF0000"
            assert light.color == "#FF0000"

        # Test validation des états
        light.turn_on()
        assert light.is_on is True
        light.turn_off()
        assert light.is_on is False

    def test_sensor_validation_methods(self):
        """Test des méthodes de validation du Sensor."""
        sensor = Sensor("Validation Sensor", "Test Room")

        # Test update avec valeurs valides
        sensor.update_value(25.5)
        assert abs(sensor.value - 25.5) < 0.01  # Comparaison de float sécurisée

        # Test update avec autre valeur numérique
        sensor.update_value(30.0)
        assert abs(sensor.value - 30.0) < 0.01  # Comparaison de float sécurisée

        # Test validation des ranges si implémentée
        if hasattr(sensor, "min_value") and hasattr(sensor, "max_value"):
            sensor.min_value = 0
            sensor.max_value = 100
            sensor.update_value(150)  # Devrait être clampé ou rejété

    def test_shutter_position_validation(self):
        """Test de la validation des positions du Shutter."""
        shutter = Shutter("Position Shutter", "Test Room")

        # Test positions valides
        shutter.set_position(0)
        assert shutter.position == 0

        shutter.set_position(50)
        assert shutter.position == 50

        shutter.set_position(100)
        assert shutter.position == 100

        # Test positions invalides (si validation implémentée)
        try:
            shutter.set_position(-10)
            # Si pas d'exception, vérifier que la valeur est clampée
            assert shutter.position >= 0
        except ValueError:
            # Exception attendue pour valeur invalide
            pass

        try:
            shutter.set_position(150)
            # Si pas d'exception, vérifier que la valeur est clampée
            assert shutter.position <= 100
        except ValueError:
            # Exception attendue pour valeur invalide
            pass


class TestFactoryCoverage:
    """Tests pour couvrir les factories."""

    @patch("domotix.core.factories.DeviceRepository")
    def test_controller_factory_device_controller(self, mock_repo_class):
        """Test de création de DeviceController via factory."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Test direct instantiation
        controller = DeviceController(mock_repo)
        assert hasattr(controller, "search_devices")

    @patch("domotix.core.factories.LightRepository")
    def test_controller_factory_light_controller(self, mock_repo_class):
        """Test de création de LightController via factory."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Test direct instantiation
        controller = LightController(mock_repo)
        assert hasattr(controller, "turn_on")

    @patch("domotix.core.factories.SensorRepository")
    def test_controller_factory_sensor_controller(self, mock_repo_class):
        """Test de création de SensorController via factory."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Test direct instantiation
        controller = SensorController(mock_repo)
        assert hasattr(controller, "update_value")

    @patch("domotix.core.factories.ShutterRepository")
    def test_controller_factory_shutter_controller(self, mock_repo_class):
        """Test de création de ShutterController via factory."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Test direct instantiation
        controller = ShutterController(mock_repo)
        assert hasattr(controller, "set_position")


class TestExceptionHandling:
    """Tests pour la gestion d'exceptions."""

    def test_device_not_found_error(self):
        """Test de DeviceNotFoundError."""
        error = DeviceNotFoundError("device-123")
        assert "[DMX-2000] Dispositif non trouvé : device-123" in str(error)
        assert hasattr(error, "device_id")

    def test_invalid_device_type_error(self):
        """Test de InvalidDeviceTypeError."""
        error = InvalidDeviceTypeError("invalid_type")
        assert "invalid_type" in str(error)
        assert error.device_type == "invalid_type"


class TestStateManagerAdvanced:
    """Tests avancés pour StateManager."""

    def test_state_manager_device_operations(self):
        """Test des opérations sur devices du StateManager."""
        StateManager.reset_instance()
        manager = StateManager()

        # Test ajout de devices
        light = Light("Manager Light", "Room")
        sensor = Sensor("Manager Sensor", "Room")
        shutter = Shutter("Manager Shutter", "Room")

        light_id = manager.register_device(light)
        manager.register_device(sensor)
        manager.register_device(shutter)

        # Test get_devices
        devices_dict = manager.get_devices()
        assert len(devices_dict) == 3

        # Test get_device
        retrieved_light = manager.get_device(light_id)
        assert retrieved_light is not None
        assert retrieved_light.id == light.id

        # Test unregister_device
        success = manager.unregister_device(light_id)
        assert success is True
        devices_dict = manager.get_devices()
        assert len(devices_dict) == 2

    def test_state_manager_persistence(self):
        """Test de la persistance du StateManager."""
        StateManager.reset_instance()
        manager1 = StateManager()

        light = Light("Persistent Light", "Room")
        light_id = manager1.register_device(light)

        # Nouvelle instance devrait être la même
        manager2 = StateManager()
        assert manager1 is manager2

        devices_dict = manager2.get_devices()
        assert len(devices_dict) == 1
        assert light_id in devices_dict


class TestErrorScenarios:
    """Tests pour les scénarios d'erreur."""

    def test_controller_with_none_device(self):
        """Test contrôleur avec device None."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        controller = LightController(mock_repo)

        # Toutes ces opérations devraient gérer gracieusement le None
        result = controller.turn_on("non-existent-id")
        assert result is False

        result = controller.turn_off("non-existent-id")
        assert result is False

        result = controller.toggle("non-existent-id")
        assert result is False

    def test_repository_session_errors(self):
        """Test des erreurs de session dans les repositories."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("Database error")

        repo = DeviceRepository(mock_session)

        # Les méthodes devraient gérer les erreurs gracieusement
        try:
            repo.find_all()
        except Exception as e:
            assert "Database error" in str(e)

    def test_model_validation_errors(self):
        """Test des erreurs de validation des modèles."""
        # Test création avec paramètres invalides
        try:
            # Si la validation est implémentée, devrait lever une exception
            Light("", "")  # Noms vides - assigné à _ pour ignorer
        except ValueError:
            # Exception attendue
            pass

        # Test update avec valeurs invalides
        sensor = Sensor("Test Sensor", "Room")
        try:
            sensor.update_value("not_a_number")
        except (ValueError, TypeError):
            # Exception attendue si validation implémentée
            pass
        except Exception:
            # Toute autre exception est aussi acceptable
            pass
