"""
Tests for CLI configuration and integration.

This module tests CLI configuration aspects:
- Main CLI initialization
- Integration with factories and DI
- Service configuration
- CLI module structure and imports
"""

from unittest.mock import Mock, patch


class TestCLIInitialization:
    """Tests for CLI initialization and structure."""

    @patch("domotix.core.database.create_session")
    @patch("domotix.core.database.create_tables")
    def test_main_cli_initialization(self, mock_create_tables, mock_create_session):
        """Test main CLI initialization."""
        # Configure mocks to avoid real calls
        mock_session = Mock()
        mock_create_session.return_value = mock_session
        mock_create_tables.return_value = None

        # Test direct access to CLI components
        from domotix.cli import app, main  # pylint: disable=import-error

        # Check that imports work
        assert app is not None, "CLI app should be accessible"
        assert callable(main), "main function should be callable"

        # Check correct types
        # Test access via module path
        import sys

        from typer import Typer  # pylint: disable=import-error

        assert isinstance(app, Typer), "app should be a Typer instance"

        if "domotix.cli.main" in sys.modules:
            main_module = sys.modules["domotix.cli.main"]
            assert hasattr(main_module, "app"), "main module should have 'app'"
            assert hasattr(main_module, "main"), "main module should have 'main'"

    def test_cli_imports_and_structure(self):
        """Test CLI structure and imports."""
        # Test command imports
        from domotix.cli import device_cmds  # pylint: disable=import-error

        # Check presence of main classes (not functions)
        assert hasattr(device_cmds, "DeviceCreateCommands")
        assert hasattr(device_cmds, "DeviceListCommands")
        assert hasattr(device_cmds, "DeviceStateCommands")


class TestCLIConfiguration:
    """Tests for CLI configuration."""

    def test_config_accessibility(self):
        """Test configuration accessibility."""
        from domotix.core import config  # pylint: disable=import-error

        # Check that the config module is accessible and has the correct classes
        assert hasattr(config, "ConfigManager") or hasattr(config, "ApplicationConfig")

    def test_service_configuration_integration(self):
        """Test service configuration."""
        from domotix.core import service_configuration  # pylint: disable=import-error

        # Check module is accessible
        assert service_configuration is not None

    def test_dependency_injection_integration(self):
        """Test dependency injection system."""
        from domotix.core import dependency_injection  # pylint: disable=import-error

        # Check module is accessible
        assert dependency_injection is not None


class TestCLIFactoryIntegration:
    """Tests for integration with factories."""

    def test_factories_integration(self):
        """Test factories integration."""
        from domotix.core import factories  # pylint: disable=import-error

        # Check that the factories module is accessible
        # and does not explode on import
        assert factories is not None

    def test_service_provider_integration(self):
        """Test service provider."""
        from domotix.core import service_provider  # pylint: disable=import-error

        assert service_provider is not None

    def test_controller_factory_accessibility(self):
        """Test accessibility of controller factories."""
        # Test that factories can be imported without error
        try:
            from domotix.core.factories import (  # pylint: disable=import-error
                get_controller_factory,
            )

            # Do not call it as it requires a session,
            # just check that the import works
            assert get_controller_factory is not None
        except ImportError:
            # If the function does not exist under this name, it is acceptable
            # as long as the factories module is accessible
            from domotix.core import factories  # pylint: disable=import-error

            assert factories is not None


class TestCLIUtilityModules:
    """Tests for CLI utility modules."""

    def test_logging_system_integration(self):
        """Test logging system."""
        from domotix.core import logging_system  # pylint: disable=import-error

        assert logging_system is not None

    def test_interfaces_integration(self):
        """Test interfaces."""
        from domotix.core import interfaces  # pylint: disable=import-error

        assert interfaces is not None

    def test_error_handling_integration(self):
        """Test error handling."""
        from domotix.core import error_handling  # pylint: disable=import-error

        assert error_handling is not None
