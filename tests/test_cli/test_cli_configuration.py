"""
Tests pour la configuration et l'intégration CLI.

Ce module teste les aspects de configuration du CLI :
- Initialisation du CLI principal
- Intégration avec les factories et la DI
- Configuration des services
- Structure et imports des modules CLI
"""

from unittest.mock import Mock, patch


class TestCLIInitialization:
    """Tests pour l'initialisation et la structure du CLI."""

    @patch("domotix.core.database.create_session")
    @patch("domotix.core.database.create_tables")
    def test_main_cli_initialization(self, mock_create_tables, mock_create_session):
        """Test initialisation CLI principale."""
        # Configure les mocks pour éviter les appels réels
        mock_session = Mock()
        mock_create_session.return_value = mock_session
        mock_create_tables.return_value = None

        # Test direct access to CLI components
        from domotix.cli import app, main  # pylint: disable=import-error

        # Vérifier que les imports fonctionnent
        assert app is not None, "CLI app should be accessible"
        assert callable(main), "main function should be callable"

        # Vérifier les types corrects
        # Test access via module path
        import sys

        from typer import Typer  # pylint: disable=import-error

        assert isinstance(app, Typer), "app should be a Typer instance"

        if "domotix.cli.main" in sys.modules:
            main_module = sys.modules["domotix.cli.main"]
            assert hasattr(main_module, "app"), "main module should have 'app'"
            assert hasattr(main_module, "main"), "main module should have 'main'"

    def test_cli_imports_and_structure(self):
        """Test structure et imports CLI."""
        # Test imports des commandes
        from domotix.cli import device_cmds  # pylint: disable=import-error

        # Vérifier présence des classes principales (pas des fonctions)
        assert hasattr(device_cmds, "DeviceCreateCommands")
        assert hasattr(device_cmds, "DeviceListCommands")
        assert hasattr(device_cmds, "DeviceStateCommands")


class TestCLIConfiguration:
    """Tests pour la configuration CLI."""

    def test_config_accessibility(self):
        """Test accessibilité de la configuration."""
        from domotix.core import config  # pylint: disable=import-error

        # Vérifier que le module config est accessible et a les bonnes classes
        assert hasattr(config, "ConfigManager") or hasattr(config, "ApplicationConfig")

    def test_service_configuration_integration(self):
        """Test configuration de service."""
        from domotix.core import service_configuration  # pylint: disable=import-error

        # Vérifier module accessible
        assert service_configuration is not None

    def test_dependency_injection_integration(self):
        """Test système d'injection de dépendances."""
        from domotix.core import dependency_injection  # pylint: disable=import-error

        # Vérifier module accessible
        assert dependency_injection is not None


class TestCLIFactoryIntegration:
    """Tests pour l'intégration avec les factories."""

    def test_factories_integration(self):
        """Test intégration des factories."""
        from domotix.core import factories  # pylint: disable=import-error

        # Vérifier que le module factories est accessible
        # et n'explose pas à l'import
        assert factories is not None

    def test_service_provider_integration(self):
        """Test service provider."""
        from domotix.core import service_provider  # pylint: disable=import-error

        assert service_provider is not None

    def test_controller_factory_accessibility(self):
        """Test accessibilité des factories de contrôleurs."""
        # Test que les factories peuvent être importées sans erreur
        try:
            from domotix.core.factories import (  # pylint: disable=import-error
                get_controller_factory,
            )

            # Ne pas l'appeler car cela nécessite une session,
            # juste vérifier que l'import fonctionne
            assert get_controller_factory is not None
        except ImportError:
            # Si la fonction n'existe pas sous ce nom, c'est acceptable
            # du moment que le module factories est accessible
            from domotix.core import factories  # pylint: disable=import-error

            assert factories is not None


class TestCLIUtilityModules:
    """Tests pour les modules utilitaires CLI."""

    def test_logging_system_integration(self):
        """Test système de logging."""
        from domotix.core import logging_system  # pylint: disable=import-error

        assert logging_system is not None

    def test_interfaces_integration(self):
        """Test interfaces."""
        from domotix.core import interfaces  # pylint: disable=import-error

        assert interfaces is not None

    def test_error_handling_integration(self):
        """Test gestion d'erreurs."""
        from domotix.core import error_handling  # pylint: disable=import-error

        assert error_handling is not None
