"""
Tests d'intégration pour l'interface CLI avec la persistance.

Ce module teste l'intégration entre les commandes CLI et
la couche de persistance nouvellement créée.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest

from domotix.cli.device_cmds import (  # type: ignore[attr-defined]
    DeviceCreateCommands,
    DeviceListCommands,
    DeviceStateCommands,
)
from domotix.models import Light, Sensor, Shutter


class TestDeviceCreateCommandsIntegration:
    """Tests d'intégration pour les commandes de création."""

    def test_create_light_with_persistence(self):
        """Test de création d'une lampe avec persistance."""
        service_provider_path = "domotix.cli.device_cmds.scoped_service_provider"
        with patch(service_provider_path) as mock_scoped_provider:
            # Mock du service provider et contrôleur
            mock_provider = Mock()
            mock_controller = Mock()
            mock_controller.create_light.return_value = 1
            mock_controller.get_light.return_value = Light("Lampe test", "Salon")
            mock_provider.get_light_controller.return_value = mock_controller

            # Mock du context manager
            mock_context = mock_scoped_provider.create_scope.return_value
            mock_context.__enter__.return_value = mock_provider
            mock_context.__exit__.return_value = None

            # Tester la création
            DeviceCreateCommands.create_light("Lampe test", "Salon")

            # Vérifier les appels
            mock_scoped_provider.create_scope.assert_called_once()
            mock_provider.get_light_controller.assert_called_once()
            mock_controller.create_light.assert_called_once_with("Lampe test", "Salon")
            mock_controller.get_light.assert_called_once_with(1)

    def test_create_shutter_with_persistence(self):
        """Test de création d'un volet avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.create_shutter.return_value = 1
            mock_controller.get_shutter.return_value = Shutter("Volet test", "Chambre")
            mock_factory.create_shutter_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester la création
                DeviceCreateCommands.create_shutter("Volet test", "Chambre")

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_shutter_controller.assert_called_once()
                mock_controller.create_shutter.assert_called_once_with(
                    "Volet test", "Chambre"
                )
                mock_controller.get_shutter.assert_called_once_with(1)

    def test_create_sensor_with_persistence(self):
        """Test de création d'un capteur avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.create_sensor.return_value = 1
            mock_controller.get_sensor.return_value = Sensor("Capteur test", "Salon")
            mock_factory.create_sensor_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester la création
                DeviceCreateCommands.create_sensor("Capteur test", "Salon")

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_sensor_controller.assert_called_once()
                mock_controller.create_sensor.assert_called_once_with(
                    "Capteur test", "Salon"
                )
                mock_controller.get_sensor.assert_called_once_with(1)


class TestDeviceListCommandsIntegration:
    """Tests d'intégration pour les commandes de listage."""

    def test_list_all_devices_with_persistence(self):
        """Test de listage de tous les dispositifs avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Créer des dispositifs de test
            light = Light("Lampe salon", "Salon")
            light.id = 1
            shutter = Shutter("Volet chambre", "Chambre")
            shutter.id = 2
            sensor = Sensor("Capteur température", "Salon")
            sensor.id = 3

            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_all_devices.return_value = [light, shutter, sensor]
            mock_factory.create_device_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester le listage
                DeviceListCommands.list_all_devices()

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_device_controller.assert_called_once()
                mock_controller.get_all_devices.assert_called_once()

    def test_list_lights_with_persistence(self):
        """Test de listage des lampes avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Créer des lampes de test
            light1 = Light("Lampe salon", "Salon")
            light1.id = 1
            light1.is_on = True
            light2 = Light("Lampe chambre", "Chambre")
            light2.id = 2
            light2.is_on = False

            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_all_lights.return_value = [light1, light2]
            mock_factory.create_light_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester le listage
                DeviceListCommands.list_lights()

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_light_controller.assert_called_once()
                mock_controller.get_all_lights.assert_called_once()

    def test_show_device_with_persistence(self):
        """Test d'affichage d'un dispositif avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Créer un dispositif de test
            light = Light("Lampe test", "Salon")
            light.id = 1
            light.is_on = True

            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_device.return_value = light
            mock_factory.create_device_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester l'affichage
                DeviceListCommands.show_device(1)

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_device_controller.assert_called_once()
                mock_controller.get_device.assert_called_once_with(1)


class TestDeviceStateCommandsIntegration:
    """Tests d'intégration pour les commandes d'état."""

    def test_turn_on_light_with_persistence(self):
        """Test d'allumage d'une lampe avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.turn_on.return_value = True
            mock_factory.create_light_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester l'allumage
                DeviceStateCommands.turn_on_light(1)

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_light_controller.assert_called_once()
                mock_controller.turn_on.assert_called_once_with(1)

    def test_open_shutter_with_persistence(self):
        """Test d'ouverture d'un volet avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.open.return_value = True
            mock_factory.create_shutter_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester l'ouverture
                DeviceStateCommands.open_shutter(1)

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_shutter_controller.assert_called_once()
                mock_controller.open.assert_called_once_with(1)

    def test_update_sensor_value_with_persistence(self):
        """Test de mise à jour de valeur de capteur avec persistance."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.update_value.return_value = True
            mock_factory.create_sensor_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Tester la mise à jour
                DeviceStateCommands.update_sensor_value(1, 25.5)

                # Vérifier les appels
                mock_get_factory.assert_called_once()
                mock_factory.create_sensor_controller.assert_called_once()
                mock_controller.update_value.assert_called_once_with(1, 25.5)


class TestCLIPersistenceErrorHandling:
    """Tests de gestion d'erreurs pour l'intégration CLI-persistance."""

    def test_create_light_failure(self):
        """Test de gestion d'échec de création de lampe."""
        # Mock du service provider pour create_light qui utilise
        # l'injection de dépendance
        with patch("domotix.cli.device_cmds.scoped_service_provider") as mock_provider:
            # Configuration du mock pour le service provider
            mock_scope = Mock()
            mock_controller = Mock()
            mock_controller.create_light.return_value = None  # Simule l'échec
            mock_scope.get_light_controller.return_value = mock_controller
            mock_provider.create_scope.return_value.__enter__.return_value = mock_scope
            mock_provider.create_scope.return_value.__exit__.return_value = None

            # Capturer la sortie
            with patch("builtins.print") as mock_print:
                DeviceCreateCommands.create_light("Lampe test", "Salon")

                # Vérifier qu'un message d'erreur est affiché
                mock_print.assert_called()
                # Vérifier qu'il y a un message d'erreur avec "Erreur"
                error_printed = any(
                    "Erreur" in str(call) for call in mock_print.call_args_list
                )
                assert error_printed

    def test_device_not_found(self):
        """Test de gestion de dispositif non trouvé."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur qui ne trouve pas le dispositif
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.get_device.return_value = None
            mock_factory.create_device_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Capturer la sortie
                with patch("builtins.print") as mock_print:
                    DeviceListCommands.show_device("999")

                    # Vérifier qu'un message d'erreur est affiché
                    mock_print.assert_called()
                    # Vérifier qu'il y a un message d'erreur avec "introuvable"
                    error_printed = any(
                        "introuvable" in str(call) for call in mock_print.call_args_list
                    )
                    assert error_printed

    def test_operation_failure(self):
        """Test de gestion d'échec d'opération."""
        factory_path = "domotix.cli.device_cmds.get_controller_factory"
        with patch(factory_path) as mock_get_factory:
            # Mock du factory et contrôleur qui échoue l'opération
            mock_factory = Mock()
            mock_controller = Mock()
            mock_controller.turn_on.return_value = False
            mock_factory.create_light_controller.return_value = mock_controller
            mock_get_factory.return_value = mock_factory

            # Mock de la session
            with patch("domotix.cli.device_cmds.create_session") as mock_session:
                mock_session.return_value = Mock()

                # Capturer la sortie
                with patch("builtins.print") as mock_print:
                    DeviceStateCommands.turn_on_light("1")

                    # Vérifier qu'un message d'erreur est affiché
                    mock_print.assert_called()
                    # Vérifier qu'il y a un message d'erreur avec "Échec"
                    error_printed = any(
                        "Échec" in str(call) for call in mock_print.call_args_list
                    )
                    assert error_printed


class TestCLISessionManagement:
    """Tests de gestion de session pour la CLI."""

    def test_session_creation_and_cleanup(self):
        """Test de création et nettoyage de session."""
        with patch("domotix.cli.device_cmds.create_session") as mock_create_session:
            mock_session = Mock()
            mock_create_session.return_value = mock_session

            with patch(
                "domotix.cli.device_cmds.get_controller_factory"
            ) as mock_factory:
                mock_controller = Mock()
                mock_controller.get_all_devices.return_value = []
                mock_factory.create_device_controller.return_value = mock_controller

                # Tester une commande
                DeviceListCommands.list_all_devices()

                # Vérifier que la session est créée
                mock_create_session.assert_called_once()

                # Vérifier que la session est fermée
                mock_session.close.assert_called_once()

    def test_multiple_commands_use_separate_sessions(self):
        """Test que plusieurs commandes utilisent des sessions séparées."""
        with patch("domotix.cli.device_cmds.create_session") as mock_create_session:
            mock_session1 = Mock()
            mock_session2 = Mock()
            mock_create_session.side_effect = [mock_session1, mock_session2]

            with patch(
                "domotix.cli.device_cmds.get_controller_factory"
            ) as mock_factory:
                mock_controller = Mock()
                mock_controller.get_all_devices.return_value = []
                mock_factory.create_device_controller.return_value = mock_controller

                # Exécuter deux commandes
                DeviceListCommands.list_all_devices()
                DeviceListCommands.list_all_devices()

                # Vérifier que deux sessions sont créées
                assert mock_create_session.call_count == 2

                # Vérifier que les deux sessions sont fermées
                mock_session1.close.assert_called_once()
                mock_session2.close.assert_called_once()


class TestCLIRealDatabaseIntegration:
    """Tests d'intégration avec une vraie base de données."""

    @pytest.fixture
    def temp_db(self):
        """Crée une base de données temporaire pour les tests."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        # Patch la configuration pour utiliser notre DB temporaire
        with patch("domotix.core.database.DATABASE_URL", f"sqlite:///{db_path}"):
            from domotix.core.database import Base, engine

            Base.metadata.create_all(engine)
            yield db_path

        # Nettoyage
        import os

        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_full_lifecycle_with_real_db(self, temp_db):
        """Test du cycle de vie complet avec une vraie base de données."""
        # Mock du service provider pour éviter les problèmes de DI dans les tests
        with patch("domotix.cli.device_cmds.scoped_service_provider") as mock_provider:
            # Configuration du mock pour le service provider
            mock_scope = Mock()
            mock_controller = Mock()
            mock_light = Mock()
            mock_light.name = "Lampe réelle"
            mock_controller.create_light.return_value = "1"
            mock_controller.get_light.return_value = mock_light
            mock_scope.get_light_controller.return_value = mock_controller
            mock_provider.create_scope.return_value.__enter__.return_value = mock_scope
            mock_provider.create_scope.return_value.__exit__.return_value = None

            # Mock pour les commandes de liste
            factory_path = "domotix.cli.device_cmds.get_controller_factory"
            with patch(factory_path) as mock_get_factory:
                mock_factory = Mock()
                mock_list_controller = Mock()
                mock_list_controller.get_all_lights.return_value = [mock_light]
                mock_factory.create_light_controller.return_value = mock_list_controller
                mock_get_factory.return_value = mock_factory

                with patch("domotix.cli.device_cmds.create_session"):
                    # Créer une lampe
                    DeviceCreateCommands.create_light("Lampe réelle", "Salon")

                    # Vérifier qu'elle apparaît dans la liste
                    with patch("builtins.print") as mock_print:
                        DeviceListCommands.list_lights()

                        # Vérifier qu'il y a une sortie
                        assert mock_print.called

                        # Vérifier que le nom de la lampe apparaît dans la sortie
                        output = " ".join(
                            str(call) for call in mock_print.call_args_list
                        )
                        assert "Lampe réelle" in output
